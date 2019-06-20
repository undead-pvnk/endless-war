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
	id_enemy = 0
	id_server = ""

	slimes = 0
	ai = ""
	name = ""
	level = 0
	poi = ""
	type = ""
	bleed_storage = 0
	time_lastenter = 0

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
					"SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM enemies{}".format(
						ewcfg.col_id_enemy,
						ewcfg.col_id_server,
						ewcfg.col_enemy_slimes,
						ewcfg.col_enemy_ai,
						ewcfg.col_enemy_type,
						ewcfg.col_enemy_name,
						ewcfg.col_enemy_level,
						ewcfg.col_enemy_poi,
						ewcfg.col_enemy_bleed_storage,
						ewcfg.col_enemy_time_lastenter,
						query_suffix
					))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.id_enemy = result[0]
					self.id_server = result[1]
					self.slimes = result[2]
					self.ai = result[3]
					self.type = result[4]
					self.name = result[5]
					self.level = result[6]
					self.poi = result[7]
					self.bleed_storage = result[8]
					self.time_lastenter = result[9]

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
				"REPLACE INTO enemies({}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
					ewcfg.col_id_enemy,
					ewcfg.col_id_server,
					ewcfg.col_enemy_slimes,
					ewcfg.col_enemy_ai,
					ewcfg.col_enemy_type,
					ewcfg.col_enemy_name,
					ewcfg.col_enemy_level,
					ewcfg.col_enemy_poi,
					ewcfg.col_enemy_bleed_storage,
					ewcfg.col_enemy_time_lastenter,
				), (
					self.id_enemy,
					self.id_server,
					self.slimes,
					self.ai,
					self.type,
					self.name,
					self.level,
					self.poi,
					self.bleed_storage,
					self.time_lastenter,
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
		enemy.slimes = 10000
		enemy.ai = ""
		enemy.poi = user_data.poi
		enemy.level = "10"
		enemy.type = enemytype
		enemy.name = "the lost juvie"
		enemy.bleed_storage = 0
		enemy.time_lastenter = 0

		enemy.persist()

		response = "**DEBUG**: You have summoned **{}**, a level {} enemy. Type =  {}.".format(enemy.name, enemy.level, enemy.type)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def hurtmesoftly(cmd):
	user_data = EwUser(member = cmd.message.author)
	resp_cont = ewutils.EwResponseContainer(id_server = user_data.id_server)

	enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {poi} = %s".format(
		id_enemy=ewcfg.col_id_enemy_id,
		poi=ewcfg.col_enemy_poi,
	), (
		user_data.poi,
	))

	for row in enemydata:
		enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
		resp_cont = enemy.kill()

	await resp_cont.post()

async def hunt(cmd):
	user_data = EwUser(member=cmd.message.author)
	response = None

	# converts ['THE', 'Lost', 'juvie'] into 'the lost juvie'
	huntedenemy = " ".join(cmd.tokens[1:]).lower()


	if not len(cmd.tokens) > 1:
		response = "Hunt *what*, exactly?"
	else:
		search = find_enemy(huntedenemy, user_data)

		if search != None:
			response = "You hunt {}. Nice work!".format(search.name)
			delete_enemy(search)

		elif cmd.mentions_count > 0:
			response = "You can't hunt other players, dummy. Try using !kill instead."
		else:
			print(huntedenemy)
			response = "You didn't manage to hunt anything by that name"


	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

def find_enemy(enemy_search = None, user_data = None):
	enemy_sought = None
	if enemy_search:
		enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {poi} = %s".format(
			id_enemy=ewcfg.col_id_enemy,
			poi=ewcfg.col_enemy_poi,
		), (
			user_data.poi,
		))

		# find the first (i.e. the oldest) item that matches the search
		for row in enemydata:
			enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
			if enemy.name == enemy_search:
				enemy_sought = enemy
				break

	return enemy_sought

def delete_enemy(enemy):
	ewutils.execute_sql_query("DELETE FROM enemies WHERE {id_enemy} = %s".format(
		id_enemy = ewcfg.col_id_enemy
	),(
		enemy.id_enemy,
	))