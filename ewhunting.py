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

    life_state = 0
    ai = ""
    name = ""
    level = 0
    time_defeated = 0
    poi = ""
    type = ""

    # slimeoid = EwSlimeoid(member = cmd.message.author, )
    # slimeoid = EwSlimeoid(id_slimeoid = 12)

    """ Load the enemy data from the database. """

    def __init__(self, member=None, id_enemy=None, life_state=None, id_server=None):
        query_suffix = ""

        if id_enemy != None:
            query_suffix = " WHERE id_enemy = '{}'".format(id_enemy)
        else:
            if member != None:
                id_user = member.id
                id_server = member.server.id

            if id_user != None and id_server != None:
                query_suffix = " WHERE id_user = '{}' AND id_server = '{}'".format(id_user, id_server)
                if life_state != None:
                    query_suffix += " AND life_state = '{}'".format(life_state)
                if sltype != None:
                    query_suffix += " AND type = '{}'".format(sltype)

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
                        ewcfg.col_enetype,
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
                    self.enemyai = result[2]
                    self.enemytype = result[3]
                    self.enemyname = result[4]
                    self.enemylevel = result[5]
                    self.enemypoi = result[6]

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
                    ewcfg.col_enetype,
                    ewcfg.col_enemyname,
                    ewcfg.col_enemylevel,
                    ewcfg.col_enemypoi,
                ), (
                    self.id_enemyid,
                    self.id_server,
                    self.enemyai,
                    self.enemytype,
                    self.enemyname,
                    self.enemylevel,
                    self.enemypoi,
                ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            ewutils.databaseClose(conn_info)

    def kill(self):
        resp_cont = ewutils.EwResponseContainer(id_server=self.id_server)
        if (self.sltype != ewcfg.sltype_nega) or active_slimeoidbattles.get(self.id_slimeoid):
            return resp_cont
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


                hurt_data.change_slimes(n=-hurt_slimes, source=ewcfg.source_haunted)

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
		response = "You can't conduct the ritual here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	enemytype = None
	if cmd.tokens_count > 1:
		enemytype = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True, negate = True)
	if value != None:
		enemy = EwEnemy()


			level = len(str(value))
			user_data.change_slimes(n = int(value/10))
			market_data.negaslime += value
			slimeoid.sltype = ewcfg.sltype_nega
			slimeoid.life_state = ewcfg.slimeoid_state_active
			slimeoid.level = level
			slimeoid.id_user = user_data.id_user
			slimeoid.id_server = user_data.id_server
			slimeoid.poi = user_data.poi
			slimeoid.name = generate_negaslimeoid_name()
			slimeoid.body = random.choice(ewcfg.body_names)
			slimeoid.head = random.choice(ewcfg.head_names)
			slimeoid.legs = random.choice(ewcfg.mobility_names)
			slimeoid.armor = random.choice(ewcfg.defense_names)
			slimeoid.weapon = random.choice(ewcfg.offense_names)
			slimeoid.special = random.choice(ewcfg.special_names)
			slimeoid.ai = random.choice(ewcfg.brain_names)
			for i in range(level):
				rand = random.randrange(3)
				if rand == 0:
					slimeoid.atk += 1
				elif rand == 1:
					slimeoid.defense += 1
				else:
					slimeoid.intel += 1



			user_data.persist()
			slimeoid.persist()
			market_data.persist()

			response = "You have summoned **{}**, an enemy.".format(enemy.name)
			desc = ewslimeoid.slimeoid_describe(slimeoid)
			response += desc

	else:
		response = "Specify how much negative slime you will sacrifice."
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))