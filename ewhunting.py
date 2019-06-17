import random
import asyncio
import time

import ewcfg
import ewutils
import ewitem
import ewrolemgr
import ewstats
import ewmap

from ew import EwUser
from ewmarket import EwMarket
from ewdistrict import EwDistrict
from ewplayer import EwPlayer


""" Enemy data model for database persistence """


class EwEnemy:
	id_enemyid = 0
	id_server = ""

	ai = ""
	name = ""
	level = 0
	poi = ""
	enemytype = ""

	# slimeoid = EwSlimeoid(member = cmd.message.author, )
	# slimeoid = EwSlimeoid(id_slimeoid = 12)

	""" Load the enemy data from the database. """

	def __init__(self, member=None, id_enemy=None, life_state=None, id_server=None):
		query_suffix = ""

		if id_enemy != None:
			query_suffix = " WHERE id_enemy = '{}'".format(id_enemy)
		else:
			if member != None:
				id_server = member.server.id

			if id_server != None:
				query_suffix = " WHERE id_server = '{}'".format(id_server)
				if enemytype != None:
					query_suffix += " AND enemytype = '{}'".format(enemytype)

		if query_suffix != "":
			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute(
					"SELECT {}, {}, {}, {}, {}, {}, {} FROM enemies{}".format(
						ewcfg.col_id_enemyid,
						ewcfg.col_id_server,
						ewcfg.col_enemyai,
						ewcfg.col_enemytype,
						ewcfg.col_enemyname,
						ewcfg.col_enemylevel,
						ewcfg.col_enemypoi,
						query_suffix
					))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.id_enemyid = result[0]
					self.id_server = result[1]
					self.ai = result[2]
					self.enemytype = result[3]
					self.name = result[4]
					self.level = result[5]
					self.poi = result[6]

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save enemy data object to the database. """

	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save the object.
			cursor.execute(
				"REPLACE INTO enemies({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
					ewcfg.col_id_enemyid,
					ewcfg.col_id_server,
					ewcfg.col_enemyai,
					ewcfg.col_enemytype,
					ewcfg.col_enemyname,
					ewcfg.col_enemylevel,
					ewcfg.col_enemypoi,
				), (
					self.id_enemyid,
					self.id_server,
					self.ai,
					self.enemytype,
					self.name,
					self.level,
					self.poi,
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

	def kill(self):
		resp_cont = ewutils.EwResponseContainer(id_server=self.id_server)
		market_data = EwMarket(id_server=self.id_server)
		ch_name = ewcfg.id_to_poi.get(self.poi).channel

		data = ewutils.execute_sql_query("SELECT {id_user} FROM users WHERE {poi} = %s AND {id_server} = %s".format(
			id_user=ewcfg.col_id_user,
			poi=ewcfg.col_poi,
			id_server=ewcfg.col_id_server
		), (
			self.poi,
			self.id_server
		))

		for row in data:
			hurt_data = EwUser(id_user=row[0], id_server=self.id_server)
			hurt_player = EwPlayer(id_user=row[0])

			if hurt_data.life_state in [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted]:
				hurt_slimes = 1000

				hurt_data.change_slimes(n=-hurt_slimes, source=ewcfg.source_enemydamage)

				# Persist changes to the database.
				hurt_data.persist()
		response = "{} attacks {}, they lose {} slime!".format(self.name, hurt_player.display_name, hurt_slimes)
		resp_cont.add_channel_response(ch_name, response)
		market_data.persist()

		return resp_cont

async def summon_enemy(cmd):
	response = ""
	user_data = EwUser(member = cmd.message.author)

	if user_data.poi not in ewcfg.capturable_districts:
		response = "**DEBUG**: MUST SUMMON IN CAPTURABLE DISTRICT."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	enemytype = None
	if len(cmd.tokens) > 1:
		enemytype = ewutils.flattenTokenListToString(cmd.tokens[1:])
	if enemytype != None:
		enemy = EwEnemy()

		enemy.id_server = user_data.id_server
		enemy.ai = ""
		enemy.poi = user_data.poi
		enemy.level = "5"
		enemy.enemytype = enemytype
		enemy.name = "THE LOST JUVIE"

		enemy.persist()

		response = "**DEBUG**: You have summoned **{}**, a level {} enemy. Type =  {}.".format(enemy.name, enemy.level, enemy.enemytype)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def hurtmesoftly(cmd):
	user_data = EwUser(member = cmd.message.author)
	resp_cont = ewutils.EwResponseContainer(id_server = user_data.id_server)

	enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {poi} = %s".format(
		id_enemy=ewcfg.col_id_enemyid,
		poi=ewcfg.col_enemypoi,
	), (
		user_data.poi,
	))

	for row in enemydata:
		enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
		resp_cont = enemy.kill()

	await resp_cont.post()