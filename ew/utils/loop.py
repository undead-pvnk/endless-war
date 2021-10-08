import asyncio
import math
import random
import time

import discord

from . import combat as cmbt_utils
from . import core as ewutils
from . import frontend as fe_utils
from . import hunting as hunt_utils
from . import item as itm_utils
from . import market as market_utils
from . import apt as apt_utils
from . import cosmeticitem as cosmetic_utils
from . import move as move_utils
from . import leaderboard as leaderboard_utils
from . import weather as weather_utils
from . import rolemgr as ewrolemgr
from . import stats as ewstats
from .combat import EwEnemy
from .combat import EwUser
from .district import EwDistrict
from .frontend import EwResponseContainer
from ..backend import core as bknd_core
from ..backend import hunting as bknd_hunt
from ..backend import item as bknd_item
from ..backend import worldevent as bknd_event
from ..backend import fish as bknd_fish
from ..backend import ads as bknd_ads
from ..backend.market import EwMarket
from ..backend.player import EwPlayer
from ..backend.status import EwEnemyStatusEffect
from ..backend.status import EwStatusEffect
from ..backend.worldevent import EwWorldEvent
from ..static import cfg as ewcfg
from ..static import items as static_items
from ..static import poi as poi_static
from ..static import status as se_static
from ..static import weapons as static_weapons


async def event_tick_loop(id_server):
    # initialise void connections
    void_connections = bknd_event.get_void_connection_pois(id_server)
    void_poi = poi_static.id_to_poi.get(ewcfg.poi_id_thevoid)
    for connection_poi in void_connections:
        # add the existing connections as neighbors for the void
        void_poi.neighbors[connection_poi] = ewcfg.travel_time_district
    for _ in range(3 - len(void_connections)):
        # create any missing connections
        bknd_event.create_void_connection(id_server)
    ewutils.logMsg("initialised void connections, current links are: {}".format(tuple(void_poi.neighbors.keys())))

    interval = ewcfg.event_tick_length
    while not ewutils.TERMINATE:
        await asyncio.sleep(interval)
        await event_tick(id_server)


async def event_tick(id_server):
    time_now = int(time.time())
    resp_cont = EwResponseContainer(id_server=id_server)
    try:
        data = bknd_core.execute_sql_query(
            "SELECT {id_event} FROM world_events WHERE {time_expir} <= %s AND {time_expir} > 0 AND id_server = %s".format(
                id_event=ewcfg.col_id_event,
                time_expir=ewcfg.col_time_expir,
            ), (
                time_now,
                id_server,
            ))

        for row in data:
            try:
                event_data = EwWorldEvent(id_event=row[0])
                event_def = poi_static.event_type_to_def.get(event_data.event_type)

                response = event_def.str_event_end if event_def else ""
                if event_data.event_type == ewcfg.event_type_minecollapse:
                    user_data = EwUser(id_user=event_data.event_props.get('id_user'), id_server=id_server)
                    mutations = user_data.get_mutations()
                    if user_data.poi == event_data.event_props.get('poi'):

                        player_data = EwPlayer(id_user=user_data.id_user)
                        response = "*{}*: You have lost an arm and a leg in a mining accident. Tis but a scratch.".format(
                            player_data.display_name)

                        if random.randrange(4) == 0:
                            response = "*{}*: Big John arrives just in time to save you from your mining accident!\nhttps://cdn.discordapp.com/attachments/431275470902788107/743629505876197416/mine2.jpg".format(
                                player_data.display_name)
                        else:

                            if ewcfg.mutation_id_lightminer in mutations:
                                response = "*{}*: You instinctively jump out of the way of the collapsing shaft, not a scratch on you. Whew, really gets your blood pumping.".format(
                                    player_data.display_name)
                            else:
                                user_data.change_slimes(n=-(user_data.slimes * 0.5))
                                user_data.persist()


                # check if any void connections have expired, if so pop it and create a new one
                elif event_data.event_type == ewcfg.event_type_voidconnection:
                    void_poi = poi_static.id_to_poi.get(ewcfg.poi_id_thevoid)
                    void_poi.neighbors.pop(event_data.event_props.get('poi'), "")
                    bknd_event.create_void_connection(id_server)

                if len(response) > 0:
                    poi = event_data.event_props.get('poi')
                    channel = event_data.event_props.get('channel')
                    if channel != None:

                        # in shambaquarium the event happens in the user's DMs
                        if event_data.event_type == ewcfg.event_type_shambaquarium:
                            client = ewutils.get_client()
                            channel = client.get_guild(id_server).get_member(int(channel))

                        resp_cont.add_channel_response(channel, response)
                    elif poi != None:
                        poi_def = poi_static.id_to_poi.get(poi)
                        if poi_def != None:
                            resp_cont.add_channel_response(poi_def.channel, response)

                    else:
                        for ch in ewcfg.hideout_channels:
                            resp_cont.add_channel_response(ch, response)

                bknd_event.delete_world_event(event_data.id_event)
            except:
                ewutils.logMsg("Error in event tick for server {}".format(id_server))

        await resp_cont.post()

    except:
        ewutils.logMsg("Error in event tick for server {}".format(id_server))


""" Decay slime totals for all users, with the exception of Kingpins"""


async def decaySlimes(id_server = None):
    if id_server != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT id_user, life_state FROM users WHERE id_server = %s AND {slimes} > 1 AND NOT ({life_state} = {life_state_kingpin} OR {life_state} = {life_state_ghost})".format(
                slimes=ewcfg.col_slimes,
                life_state=ewcfg.col_life_state,
                life_state_kingpin=ewcfg.life_state_kingpin,
                life_state_ghost=ewcfg.life_state_corpse
            ), (
                id_server,
            ))

            users = cursor.fetchall()
            total_decayed = 0

            for user in users:
                user_data = EwUser(id_user=user[0], id_server=id_server)
                slimes_to_decay = user_data.slimes - (user_data.slimes * (.5 ** (ewcfg.update_market / ewcfg.slime_half_life)))

                # round up or down, randomly weighted
                remainder = slimes_to_decay - int(slimes_to_decay)
                if random.random() < remainder:
                    slimes_to_decay += 1
                slimes_to_decay = int(slimes_to_decay)

                if slimes_to_decay >= 1:
                    user_data.change_slimes(n=-slimes_to_decay, source=ewcfg.source_decay)
                    user_data.persist()
                    total_decayed += slimes_to_decay

            cursor.execute("SELECT district FROM districts WHERE id_server = %s AND {slimes} > 1".format(
                slimes=ewcfg.col_district_slimes
            ), (
                id_server,
            ))

            districts = cursor.fetchall()

            for district in districts:
                district_data = EwDistrict(district=district[0], id_server=id_server)
                slimes_to_decay = district_data.slimes - (district_data.slimes * (.5 ** (ewcfg.update_market / ewcfg.slime_half_life)))

                # round up or down, randomly weighted
                remainder = slimes_to_decay - int(slimes_to_decay)
                if random.random() < remainder:
                    slimes_to_decay += 1
                slimes_to_decay = int(slimes_to_decay)

                if slimes_to_decay >= 1:
                    district_data.change_slimes(n=-slimes_to_decay, source=ewcfg.source_decay)
                    district_data.persist()
                    total_decayed += slimes_to_decay

            cursor.execute("UPDATE markets SET {decayed} = ({decayed} + %s) WHERE {server} = %s".format(
                decayed=ewcfg.col_decayed_slimes,
                server=ewcfg.col_id_server
            ), (
                total_decayed,
                id_server
            ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


"""
	Kills users who have left the server while the bot was offline
"""


def kill_quitters(id_server = None):
    if id_server != None:
        try:
            client = ewutils.get_client()
            server = client.get_guild(id_server)
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND ( life_state > 0 OR slimes < 0 )".format(
            ), (
                id_server,
            ))

            users = cursor.fetchall()

            for user in users:
                member = server.get_member(user[0])

                # Make sure to kill players who may have left while the bot was offline.
                if member is None:
                    try:
                        user_data = EwUser(id_user=user[0], id_server=id_server)

                        user_data.trauma = ewcfg.trauma_id_suicide
                        user_data.die(cause=ewcfg.cause_leftserver)
                        user_data.persist()

                        ewutils.logMsg('Player with id {} killed for leaving the server.'.format(user[0]))
                    except:
                        ewutils.logMsg('Failed to kill member who left the server.')

        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


""" Flag all users in the Outskirts for PvP """


async def flag_outskirts(id_server = None):
    if id_server != None:
        try:
            client = ewutils.get_client()
            server = client.get_guild(id_server)
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND poi IN %s".format(
            ), (
                id_server,
                tuple(poi_static.outskirts)

            ))

            users = cursor.fetchall()

            for user in users:
                user_data = EwUser(id_user=user[0], id_server=id_server)
                # Flag the user for PvP
                enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
                user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
                user_data.persist()
                await ewrolemgr.updateRoles(client=client, member=server.get_member(user_data.id_user))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


"""
	Flag all users in vulnerable territory, defined as capturable territory (streets) and outskirts.
"""


async def flag_vulnerable_districts(id_server = None):
    if id_server != None:
        try:
            client = ewutils.get_client()
            server = client.get_guild(id_server)
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND poi IN %s".format(
            ), (
                id_server,
                tuple(poi_static.vulnerable_districts)

            ))

            users = cursor.fetchall()

            for user in users:
                user_data = EwUser(id_user=user[0], id_server=id_server)
                member = server.get_member(user_data.id_user)

                # Flag the user for PvP
                enlisted = True if user_data.life_state == ewcfg.life_state_enlisted else False
                user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_vulnerable_districts, enlisted)
                user_data.persist()

                await ewrolemgr.updateRoles(client=client, member=member, remove_or_apply_flag='apply')

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


"""
	Coroutine that continually calls bleedSlimes; is called once per server, and not just once globally
"""


async def bleed_tick_loop(id_server):
    interval = ewcfg.bleed_tick_length
    # causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
    while not ewutils.TERMINATE:
        await bleedSlimes(id_server=id_server)
        await enemyBleedSlimes(id_server=id_server)
        # ewutils.ewutils.logMsg("Capture tick happened on server %s." % id_server + " Timestamp: %d" % int(time.time()))

        await asyncio.sleep(interval)


""" Bleed slime for all users """


async def bleedSlimes(id_server = None):
    if id_server != None:
        try:
            client = ewutils.get_client()
            server = client.get_guild(id_server)
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND {bleed_storage} > 1".format(
                bleed_storage=ewcfg.col_bleed_storage
            ), (
                id_server,
            ))

            users = cursor.fetchall()
            total_bled = 0
            deathreport = ""
            resp_cont = EwResponseContainer(id_server=id_server)
            for user in users:
                user_data = EwUser(id_user=user[0], id_server=id_server)

                mutations = user_data.get_mutations()
                member = server.get_member(user_data.id_user)
                if ewcfg.mutation_id_bleedingheart not in mutations or user_data.time_lasthit < int(time.time()) - ewcfg.time_bhbleed:
                    slimes_to_bleed = user_data.bleed_storage * (
                            1 - .5 ** (ewcfg.bleed_tick_length / ewcfg.bleed_half_life))
                    slimes_to_bleed = max(slimes_to_bleed, ewcfg.bleed_tick_length * 1000)
                    slimes_dropped = user_data.totaldamage + user_data.slimes

                    # trauma = se_static.trauma_map.get(user_data.trauma)
                    # bleed_mod = 1
                    # if trauma != None and trauma.trauma_class == ewcfg.trauma_class_bleeding:
                    #	bleed_mod += 0.5 * user_data.degradation / 100

                    # round up or down, randomly weighted
                    remainder = slimes_to_bleed - int(slimes_to_bleed)
                    if random.random() < remainder:
                        slimes_to_bleed += 1
                    slimes_to_bleed = int(slimes_to_bleed)

                    slimes_to_bleed = min(slimes_to_bleed, user_data.bleed_storage)

                    if slimes_to_bleed >= 1:

                        real_bleed = round(slimes_to_bleed)  # * bleed_mod)

                        user_data.bleed_storage -= slimes_to_bleed
                        user_data.change_slimes(n=- real_bleed, source=ewcfg.source_bleeding)

                        district_data = EwDistrict(id_server=id_server, district=user_data.poi)
                        district_data.change_slimes(n=real_bleed, source=ewcfg.source_bleeding)
                        district_data.persist()

                        if user_data.slimes < 0:
                            user_data.trauma = ewcfg.trauma_id_environment
                            die_resp = user_data.die(cause=ewcfg.cause_bleeding)
                            # user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
                            player_data = EwPlayer(id_server=user_data.id_server, id_user=user_data.id_user)
                            resp_cont.add_response_container(die_resp)
                        user_data.persist()

                        total_bled += real_bleed

                    await ewrolemgr.updateRoles(client=client, member=member)

            await resp_cont.post()

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


""" Bleed slime for all enemies """


async def enemyBleedSlimes(id_server = None):
    if id_server != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT id_enemy FROM enemies WHERE id_server = %s AND {bleed_storage} > 1".format(
                bleed_storage=ewcfg.col_enemy_bleed_storage
            ), (
                id_server,
            ))

            enemies = cursor.fetchall()
            total_bled = 0
            resp_cont = EwResponseContainer(id_server=id_server)
            for enemy in enemies:
                enemy_data = EwEnemy(id_enemy=enemy[0], id_server=id_server)
                slimes_to_bleed = enemy_data.bleed_storage * (1 - .5 ** (ewcfg.bleed_tick_length / ewcfg.bleed_half_life))
                slimes_to_bleed = max(slimes_to_bleed, ewcfg.bleed_tick_length * 1000)
                slimes_to_bleed = min(slimes_to_bleed, enemy_data.bleed_storage)

                district_data = EwDistrict(id_server=id_server, district=enemy_data.poi)

                # round up or down, randomly weighted
                remainder = slimes_to_bleed - int(slimes_to_bleed)
                if random.random() < remainder:
                    slimes_to_bleed += 1
                slimes_to_bleed = int(slimes_to_bleed)

                if slimes_to_bleed >= 1:
                    enemy_data.bleed_storage -= slimes_to_bleed
                    enemy_data.change_slimes(n=- slimes_to_bleed, source=ewcfg.source_bleeding)
                    enemy_data.persist()
                    district_data.change_slimes(n=slimes_to_bleed, source=ewcfg.source_bleeding)
                    district_data.persist()
                    total_bled += slimes_to_bleed

                    if enemy_data.slimes <= 0:
                        bknd_hunt.delete_enemy(enemy_data)

            await resp_cont.post()
            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


""" Increase hunger for every player in the server. """


def pushupServerHunger(id_server = None):
    if id_server != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Save data
            cursor.execute("UPDATE users SET {hunger} = {hunger} + {tick} WHERE life_state > 0 AND id_server = %s AND hunger < {limit}".format(
                hunger=ewcfg.col_hunger,
                tick=ewcfg.hunger_pertick,
                # this function returns the bigger of two values; there is no simple way to do this in sql and we can't calculate it within this python script
                limit="0.5 * (({val1} + {val2}) + ABS({val1} - {val2}))".format(
                    val1=ewcfg.min_stamina,
                    val2="POWER(" + ewcfg.col_slimelevel + ", 2)"
                )
            ), (
                id_server,
            ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


""" Reduce inebriation for every player in the server. """


async def pushdownServerInebriation(id_server = None):
    if id_server != None:
        try:
            bknd_core.execute_sql_query("UPDATE users SET {inebriation} = {inebriation} - {tick} WHERE id_server = %s AND {inebriation} > {limit}".format(
                inebriation=ewcfg.col_inebriation,
                tick=ewcfg.inebriation_pertick,
                limit=0
            ), (
                id_server,
            ))
        except:
            ewutils.logMsg("Failed to pushdown server inebriation.")     

"""
	Coroutine that continually calls burnSlimes; is called once per server, and not just once globally
"""


async def burn_tick_loop(id_server):
    interval = ewcfg.burn_tick_length
    while not ewutils.TERMINATE:
        await burnSlimes(id_server=id_server)
        await enemyBurnSlimes(id_server=id_server)
        await asyncio.sleep(interval)


""" Burn slime for all users """


async def burnSlimes(id_server = None):
    if id_server != None:
        time_now = int(time.time())
        client = ewutils.get_client()
        server = client.get_guild(id_server)
        status_origin = 'user'

        results = {}

        # Get users with harmful status effects
        data = bknd_core.execute_sql_query("SELECT {id_user}, {value}, {source}, {id_status} from status_effects WHERE {id_status} IN %s and {id_server} = %s".format(
            id_user=ewcfg.col_id_user,
            value=ewcfg.col_value,
            id_status=ewcfg.col_id_status,
            id_server=ewcfg.col_id_server,
            source=ewcfg.col_source
        ), (
            tuple(ewcfg.harmful_status_effects),
            id_server
        ))

        resp_cont = EwResponseContainer(id_server=id_server)
        for result in data:
            user_data = EwUser(id_user=result[0], id_server=id_server)
            member = server.get_member(user_data.id_user)

            slimes_dropped = user_data.totaldamage + user_data.slimes
            used_status_id = result[3]

            # Deal 10% of total slime to burn every second
            slimes_to_burn = math.ceil(int(float(result[1])) * ewcfg.burn_tick_length / ewcfg.time_expire_burn)

            # Check if a status effect originated from an enemy or a user.
            killer_data = EwUser(id_server=id_server, id_user=result[2])
            if killer_data == None:
                killer_data = EwEnemy(id_server=id_server, id_enemy=result[2])
                if killer_data != None:
                    status_origin = 'enemy'
                else:
                    # For now, skip over any status that did not originate from a user or an enemy. This might be changed in the future.
                    continue

            if status_origin == 'user':
                # Damage stats
                ewstats.change_stat(user=killer_data, metric=ewcfg.stat_lifetime_damagedealt, n=slimes_to_burn)

            # Player died
            if user_data.slimes - slimes_to_burn < 0:
                weapon = static_weapons.weapon_map.get(ewcfg.weapon_id_molotov)

                player_data = EwPlayer(id_server=user_data.id_server, id_user=user_data.id_user)
                killer = EwPlayer(id_server=id_server, id_user=killer_data.id_user)
                poi = poi_static.id_to_poi.get(user_data.poi)

                # Kill stats
                if status_origin == 'user':
                    ewstats.increment_stat(user=killer_data, metric=ewcfg.stat_kills)
                    ewstats.track_maximum(user=killer_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))

                    if killer_data.slimelevel > user_data.slimelevel:
                        ewstats.increment_stat(user=killer_data, metric=ewcfg.stat_lifetime_ganks)
                    elif killer_data.slimelevel < user_data.slimelevel:
                        ewstats.increment_stat(user=killer_data, metric=ewcfg.stat_lifetime_takedowns)

                    # Collect bounty
                    coinbounty = int(user_data.bounty / ewcfg.slimecoin_exchangerate)  # 100 slime per coin

                    if user_data.slimes >= 0:
                        killer_data.change_slimecoin(n=coinbounty, coinsource=ewcfg.coinsource_bounty)

                # Kill player
                if status_origin == 'user':
                    user_data.id_killer = killer_data.id_user
                elif status_origin == 'enemy':
                    user_data.id_killer = killer_data.id_enemy

                user_data.trauma = ewcfg.trauma_id_environment
                die_resp = user_data.die(cause=ewcfg.cause_burning)
                # user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)

                resp_cont.add_response_container(die_resp)

                if used_status_id == ewcfg.status_burning_id:
                    deathreport = "{} has burned to death.".format(player_data.display_name)
                elif used_status_id == ewcfg.status_acid_id:
                    deathreport = "{} has been melted to death by acid.".format(player_data.display_name)
                elif used_status_id == ewcfg.status_spored_id:
                    deathreport = "{} has been overrun by spores.".format(player_data.display_name)
                else:
                    deathreport = ""
                resp_cont.add_channel_response(poi.channel, deathreport)

                user_data.trauma = weapon.id_weapon

                user_data.persist()
                await ewrolemgr.updateRoles(client=client, member=member)
            else:
                user_data.change_slimes(n=-slimes_to_burn, source=ewcfg.source_damage)
                user_data.persist()

        await resp_cont.post()


async def enemyBurnSlimes(id_server):
    if id_server != None:
        time_now = int(time.time())
        client = ewutils.get_client()
        server = client.get_guild(id_server)
        status_origin = 'user'

        results = {}

        # Get enemies with harmful status effects
        data = bknd_core.execute_sql_query("SELECT {id_enemy}, {value}, {source}, {id_status} from enemy_status_effects WHERE {id_status} IN %s and {id_server} = %s".format(
            id_enemy=ewcfg.col_id_enemy,
            value=ewcfg.col_value,
            id_status=ewcfg.col_id_status,
            id_server=ewcfg.col_id_server,
            source=ewcfg.col_source
        ), (
            ewcfg.harmful_status_effects,
            id_server
        ))

        resp_cont = EwResponseContainer(id_server=id_server)
        for result in data:
            enemy_data = EwEnemy(id_enemy=result[0], id_server=id_server)

            slimes_dropped = enemy_data.totaldamage + enemy_data.slimes
            used_status_id = result[3]

            # Deal 10% of total slime to burn every second
            slimes_to_burn = math.ceil(int(float(result[1])) * ewcfg.burn_tick_length / ewcfg.time_expire_burn)

            # Check if a status effect originated from an enemy or a user.
            killer_data = EwUser(id_server=id_server, id_user=result[2])
            if killer_data == None:
                killer_data = EwEnemy(id_server=id_server, id_enemy=result[2])
                if killer_data != None:
                    status_origin = 'enemy'
                else:
                    # For now, skip over any status that did not originate from a user or an enemy. This might be changed in the future.
                    continue

            if status_origin == 'user':
                ewstats.change_stat(user=killer_data, metric=ewcfg.stat_lifetime_damagedealt, n=slimes_to_burn)

            if enemy_data.slimes - slimes_to_burn <= 0:
                bknd_hunt.delete_enemy(enemy_data)

                if used_status_id == ewcfg.status_burning_id:
                    response = "{} has burned to death.".format(enemy_data.display_name)
                elif used_status_id == ewcfg.status_acid_id:
                    response = "{} has been melted to death by acid.".format(enemy_data.display_name)
                elif used_status_id == ewcfg.status_spored_id:
                    response = "{} has been overrun by spores.".format(enemy_data.display_name)
                else:
                    response = ""
                resp_cont.add_channel_response(poi_static.id_to_poi.get(enemy_data.poi).channel, response)

                district_data = EwDistrict(id_server=id_server, district=enemy_data.poi)
                resp_cont.add_response_container(cmbt_utils.drop_enemy_loot(enemy_data, district_data))
            else:
                enemy_data.change_slimes(n=-slimes_to_burn, source=ewcfg.source_damage)
                enemy_data.persist()

        await resp_cont.post()


async def remove_status_loop(id_server):
    interval = ewcfg.removestatus_tick_length
    while not ewutils.TERMINATE:
        removeExpiredStatuses(id_server=id_server)
        enemyRemoveExpiredStatuses(id_server=id_server)
        await asyncio.sleep(interval)


""" Remove expired status effects for all users """


def removeExpiredStatuses(id_server = None):
    if id_server != None:
        time_now = int(time.time())

        # client = ewutils.get_client()
        # server = client.get_server(id_server)

        statuses = bknd_core.execute_sql_query("SELECT {id_status},{id_user} FROM status_effects WHERE id_server = %s AND {time_expire} < %s".format(
            id_status=ewcfg.col_id_status,
            id_user=ewcfg.col_id_user,
            time_expire=ewcfg.col_time_expir
        ), (
            id_server,
            time_now
        ))

        for row in statuses:
            status = row[0]
            id_user = row[1]
            user_data = EwUser(id_user=id_user, id_server=id_server)
            status_def = se_static.status_effects_def_map.get(status)
            status_effect = EwStatusEffect(id_status=status, user_data=user_data)

            if status_def.time_expire > 0:
                if status_effect.time_expire < time_now:
                    user_data.clear_status(id_status=status)

            # Status that expire under special conditions
            else:
                if status == ewcfg.status_stunned_id:
                    if int(status_effect.value) < time_now:
                        user_data.clear_status(id_status=status)


def enemyRemoveExpiredStatuses(id_server = None):
    if id_server != None:
        time_now = int(time.time())

        statuses = bknd_core.execute_sql_query("SELECT {id_status}, {id_enemy} FROM enemy_status_effects WHERE id_server = %s AND {time_expire} < %s".format(
            id_status=ewcfg.col_id_status,
            id_enemy=ewcfg.col_id_enemy,
            time_expire=ewcfg.col_time_expir
        ), (
            id_server,
            time_now
        ))

        for row in statuses:
            status = row[0]
            id_enemy = row[1]
            enemy_data = EwEnemy(id_enemy=id_enemy, id_server=id_server)
            status_def = se_static.status_effects_def_map.get(status)
            status_effect = EwEnemyStatusEffect(id_status=status, enemy_data=enemy_data)

            if status_def.time_expire > 0:
                if status_effect.time_expire < time_now:
                    enemy_data.clear_status(id_status=status)

            # Status that expire under special conditions
            else:
                if status == ewcfg.status_stunned_id:
                    if int(status_effect.value) < time_now:
                        enemy_data.clear_status(id_status=status)


async def decrease_food_multiplier():
    while not ewutils.TERMINATE:
        for user in ewutils.food_multiplier.copy():
            # If the food multi is empty, then just remove the user from the list
            if ewutils.food_multiplier[user] == 0:
                ewutils.food_multiplier.pop(user)
            # Reduce it down
            if ewutils.food_multiplier.get(user):
                ewutils.food_multiplier[user] = max(0, ewutils.food_multiplier.get(user) - 1)
            
        await asyncio.sleep(5)


async def spawn_enemies(id_server = None):
    market_data = EwMarket(id_server=id_server)
    resp_list = []
    # One in 3 chance of spawning a regular enemy in the outskirts
    if random.randrange(3) == 0:
        weathertype = ewcfg.enemy_weathertype_normal
        # If it's raining, an enemy has  2/3 chance to spawn as a bicarbonate enemy, which doesn't take rain damage
        if market_data.weather == ewcfg.weather_bicarbonaterain:
            if random.randrange(3) < 2:
                weathertype = ewcfg.enemy_weathertype_rainresist

        resp_list.append(hunt_utils.spawn_enemy(id_server=id_server, pre_chosen_weather=weathertype))
    # One in two chance of spawning a slimeoid trainer in either the Battle Arena or Subway
    # Why did I make this into incredibly hacky code? Because.
    if random.randrange(2) == 0:
            if random.randrange(2) == 0:
                resp_list.append(hunt_utils.spawn_enemy(id_server=id_server, pre_chosen_type=ewcfg.enemy_type_slimeoidtrainer))
            else:
                resp_list.append(hunt_utils.spawn_enemy(id_server=id_server, pre_chosen_type=ewcfg.enemy_type_ug_slimeoidtrainer))
    
    for cont in resp_list:
        await cont.post()


# TODO remove after double halloween
# market_data = EwMarket(id_server=id_server)
# underworld_district = EwDistrict(district=ewcfg.poi_id_underworld, id_server=id_server)
# enemies_count = len(underworld_district.get_enemies_in_district())

# if enemies_count == 0 and int(time.time()) > (market_data.horseman_timeofdeath + ewcfg.horseman_death_cooldown):
#	dh_resp_cont = ewhunting.spawn_enemy(id_server=id_server, pre_chosen_type=ewcfg.enemy_type_doubleheadlessdoublehorseman, pre_chosen_poi=ewcfg.poi_id_underworld, manual_spawn=True)

#	await dh_resp_cont.post()

async def spawn_enemies_tick_loop(id_server):
    interval = ewcfg.enemy_spawn_tick_length
    # Causes the possibility of an enemy spawning every 10 seconds
    while not ewutils.TERMINATE:
        await asyncio.sleep(interval)
        await spawn_enemies(id_server=id_server)


async def enemy_action_tick_loop(id_server):
    interval = ewcfg.enemy_attack_tick_length
    # Causes hostile enemies to attack every tick.
    while not ewutils.TERMINATE:
        await asyncio.sleep(interval)
        # resp_cont = EwResponseContainer(id_server=id_server)
        if ewcfg.gvs_active:
            await cmbt_utils.enemy_perform_action_gvs(id_server)

        else:
            await cmbt_utils.enemy_perform_action(id_server)


async def gvs_gamestate_tick_loop(id_server):
    interval = ewcfg.gvs_gamestate_tick_length
    # Causes various events to occur during a Garden or Graveyard ops in Gankers Vs. Shamblers
    while not ewutils.TERMINATE:
        await asyncio.sleep(interval)
        await hunt_utils.gvs_update_gamestate(id_server)


async def spawn_prank_items_tick_loop(id_server):
    # DEBUG
    # interval = 10

    # If there are more active people, items spawn more frequently, and less frequently if there are less active people.
    interval = 180
    new_interval = 0
    while not ewutils.TERMINATE:
        if new_interval > 0:
            interval = new_interval

        # print("newinterval:{}".format(new_interval))

        await asyncio.sleep(interval)
        new_interval = await spawn_prank_items(id_server=id_server)


async def spawn_prank_items(id_server):
    new_interval = 0
    base_interval = 60

    try:
        active_users_count = 0

        if id_server != None:
            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT id_user FROM users WHERE id_server = %s AND {poi} in %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin}) AND {time_last_action} > %s".format(
                        life_state=ewcfg.col_life_state,
                        poi=ewcfg.col_poi,
                        life_state_corpse=ewcfg.life_state_corpse,
                        life_state_kingpin=ewcfg.life_state_kingpin,
                        time_last_action=ewcfg.col_time_last_action,
                    ), (
                        id_server,
                        poi_static.capturable_districts,
                        (int(time.time()) - ewcfg.time_kickout),
                    ))

                users = cursor.fetchall()

                active_users_count = len(users)

                conn.commit()
            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

        # Avoid division by 0
        if active_users_count == 0:
            active_users_count = 1
        else:
            # print(active_users_count)
            pass

        new_interval = (math.ceil(base_interval / active_users_count) * 5)  # 5 active users = 1 minute timer, 10 = 30 second timer, and so on.

        district_id = random.choice(poi_static.capturable_districts)

        # Debug
        # district_id = 'wreckington'

        district_channel_name = poi_static.id_to_poi.get(district_id).channel

        client = ewutils.get_client()

        server = client.get_guild(id_server)

        district_channel = fe_utils.get_channel(server=server, channel_name=district_channel_name)

        pie_or_prank = random.randrange(3)

        if pie_or_prank == 0:
            swilldermuk_food_item = random.choice(static_items.swilldermuk_food)

            item_props = itm_utils.gen_item_props(swilldermuk_food_item)

            swilldermuk_food_item_id = bknd_item.item_create(
                item_type=swilldermuk_food_item.item_type,
                id_user=district_id,
                id_server=id_server,
                item_props=item_props
            )

            # print('{} with id {} spawned in {}!'.format(swilldermuk_food_item.str_name, swilldermuk_food_item_id, district_id))

            response = "That smell... it's unmistakeable!! Someone's left a fresh {} on the ground!".format(swilldermuk_food_item.str_name)
            await fe_utils.send_message(client, district_channel, response)
        else:
            rarity_roll = random.randrange(10)

            if rarity_roll > 3:
                prank_item = random.choice(static_items.prank_items_heinous)
            elif rarity_roll > 0:
                prank_item = random.choice(static_items.prank_items_scandalous)
            else:
                prank_item = random.choice(static_items.prank_items_forbidden)

            # Debug
            # prank_item = static_items.prank_items_heinous[1] # Chinese Finger Trap

            item_props = itm_utils.gen_item_props(prank_item)

            prank_item_id = bknd_item.item_create(
                item_type=prank_item.item_type,
                id_user=district_id,
                id_server=id_server,
                item_props=item_props
            )

            # print('{} with id {} spawned in {}!'.format(prank_item.str_name, prank_item_id, district_id))

            response = "An ominous wind blows through the streets. You think you hear someone drop a {} on the ground nearby...".format(prank_item.str_name)
            await fe_utils.send_message(client, district_channel, response)

    except:
        ewutils.logMsg("An error occured in spawn prank items tick for server {}".format(id_server))

    return new_interval


async def generate_credence_tick_loop(id_server):
    # DEBUG
    # interval = 10

    while not ewutils.TERMINATE:
        interval = (random.randrange(121) + 120)  # anywhere from 2-4 minutes
        await asyncio.sleep(interval)
        await generate_credence(id_server)


async def generate_credence(id_server):
    # print("CREDENCE GENERATED")

    if id_server != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND {poi} in %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin}) AND {time_last_action} > %s".format(
                life_state=ewcfg.col_life_state,
                poi=ewcfg.col_poi,
                life_state_corpse=ewcfg.life_state_corpse,
                life_state_kingpin=ewcfg.life_state_kingpin,
                time_last_action=ewcfg.col_time_last_action,
            ), (
                id_server,
                poi_static.capturable_districts,
                (int(time.time()) - ewcfg.time_afk_swilldermuk),
            ))

            users = cursor.fetchall()

            for user in users:
                user_data = EwUser(id_user=user[0], id_server=id_server)
                added_credence = 0
                lowered_credence_used = 0

                if user_data.credence >= 1000:
                    added_credence = 1 + random.randrange(5)
                elif user_data.credence >= 500:
                    added_credence = 10 + random.randrange(41)
                elif user_data.credence >= 100:
                    added_credence = 25 + random.randrange(76)
                else:
                    added_credence = 50 + random.randrange(151)

                if user_data.credence_used > 0:
                    lowered_credence_used = int(user_data.credence_used / 10)

                    if lowered_credence_used == 1:
                        lowered_credence_used = 0

                    user_data.credence_used = lowered_credence_used

                added_credence = max(0, added_credence - lowered_credence_used)
                user_data.credence += added_credence

                user_data.persist()

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


# Pay out salaries. SlimeCoin can be taken away or given depending on if the user has positive or negative credits.
async def pay_salary(id_server = None):
    ewutils.logMsg('Paying salary...')

    try:
        conn_info = bknd_core.databaseConnect()
        conn = conn_info.get('conn')
        cursor = conn.cursor()
        client = ewutils.get_client()
        if id_server != None:
            # get all players with apartments. If a player is evicted, thir rent is 0, so this will not affect any bystanders.
            cursor.execute("SELECT id_user FROM users WHERE salary_credits != 0 AND id_server = {}".format(id_server))

            security_officers = cursor.fetchall()

            for officer in security_officers:
                officer_id_user = int(officer[0])

                user_data = EwUser(id_user=officer_id_user, id_server=id_server)
                credits = user_data.salary_credits

                # Prevent the user from obtaining negative slimecoin
                if credits < 0 and user_data.slimecoin < (-1 * credits):
                    user_data.change_slimecoin(n=-user_data.slimecoin, coinsource=ewcfg.coinsource_salary)
                else:
                    user_data.change_slimecoin(n=user_data.salary_credits, coinsource=ewcfg.coinsource_salary)

                user_data.persist()
    finally:
        cursor.close()
        bknd_core.databaseClose(conn_info)


"""
	Updates/Increments the capture_points values of all districts every time it's called
"""


async def capture_tick(id_server):
    # the variables might apparently be accessed before assignment if i didn't declare them here
    cursor = None
    conn_info = None

    resp_cont_capture_tick = EwResponseContainer(client=ewutils.get_client(), id_server=id_server)

    all_districts = poi_static.capturable_districts

    if len(all_districts) > 0:  # if all_districts isn't empty
        server = ewcfg.server_list[id_server]
        time_old = time.time()

        for district in all_districts:
            district_name = district
            dist = EwDistrict(id_server=id_server, district=district_name)

            if dist.time_unlock > 0 and not dist.all_neighbors_friendly():
                responses = dist.change_capture_lock(progress=-ewcfg.capture_tick_length)
                resp_cont_capture_tick.add_response_container(responses)
                dist.persist()

            if dist.time_unlock > 0:
                continue

            # no more automatic capping
            continue

            controlling_faction = dist.controlling_faction

            gangsters_in_district = dist.get_players_in_district(min_slimes=ewcfg.min_slime_to_cap, life_states=[ewcfg.life_state_enlisted], ignore_offline=True)

            slimeoids = ewutils.get_slimeoids_in_poi(poi=district_name, id_server=id_server, sltype=ewcfg.sltype_nega)

            nega_present = len(slimeoids) > 0
            #			if nega_present:
            #				continue

            # the faction that's actively capturing the district this tick
            # if no players are present, it's None, if only players of one faction (ignoring juvies and ghosts) are,
            # it's the faction's name, i.e. 'rowdys' or 'killers', and if both are present, it's 'both'
            faction_capture = None

            # how much progress will be made. is higher the more people of one faction are in a district, and is 0 if both teams are present
            capture_speed = 0

            # number of players actively capturing
            num_capturers = 0

            dc_stat_increase_list = []

            # checks if any players are in the district and if there are only players of the same faction, i.e. progress can happen
            for player in gangsters_in_district:
                player_id = player
                user_data = EwUser(id_user=player_id, id_server=id_server)
                player_faction = user_data.faction

                mutations = user_data.get_mutations()

                try:
                    player_online = server.get_member(player_id).status != discord.Status.offline
                except:
                    player_online = False

                # ewutils.logMsg("Online status checked. Time elapsed: %f" % (time.time() - time_old) + " Server: %s" % id_server + " Player: %s" % player_id + " Status: %s" % ("online" if player_online else "offline"))

                if player_online:
                    if faction_capture not in [None, player_faction]:  # if someone of the opposite faction is in the district
                        faction_capture = 'both'  # standstill, gang violence has to happen
                        capture_speed = 0
                        num_capturers = 0
                        dc_stat_increase_list.clear()

                    else:  # if the district isn't already controlled by the player's faction and the capture isn't halted by an enemy
                        faction_capture = player_faction
                        player_capture_speed = 1
                        if ewcfg.mutation_id_lonewolf in mutations and len(gangsters_in_district) == 1:
                            player_capture_speed *= 2
                        if ewcfg.mutation_id_patriot in mutations:
                            player_capture_speed *= 2

                        capture_speed += player_capture_speed
                        num_capturers += 1
                        dc_stat_increase_list.append(player_id)

            if faction_capture not in ['both', None]:  # if only members of one faction is present
                if district_name in poi_static.capturable_districts:
                    friendly_neighbors = dist.get_number_of_friendly_neighbors()
                    if dist.all_neighbors_friendly():
                        capture_speed = 0
                    elif dist.controlling_faction == faction_capture:
                        capture_speed *= 1 + 0.1 * friendly_neighbors
                    else:
                        capture_speed /= 1 + 0.1 * friendly_neighbors

                    capture_progress = dist.capture_points

                    if faction_capture != dist.capturing_faction:
                        capture_progress *= -1

                    capture_speed *= ewcfg.baseline_capture_speed

                    if dist.capture_points < dist.max_capture_points:
                        for stat_recipient in dc_stat_increase_list:
                            ewstats.change_stat(
                                id_server=id_server,
                                id_user=stat_recipient,
                                metric=ewcfg.stat_capture_points_contributed,
                                n=ewcfg.capture_tick_length * capture_speed
                            )

                    if faction_capture == dist.capturing_faction:  # if the faction is already in the process of capturing, continue
                        responses = dist.change_capture_points(ewcfg.capture_tick_length * capture_speed, faction_capture, num_capturers)
                        resp_cont_capture_tick.add_response_container(responses)

                    elif dist.capture_points == 0 and dist.controlling_faction == "":  # if it's neutral, start the capture
                        responses = dist.change_capture_points(ewcfg.capture_tick_length * capture_speed, faction_capture, num_capturers)
                        resp_cont_capture_tick.add_response_container(responses)

                        dist.capturing_faction = faction_capture

                    # lower the enemy faction's progress to revert it to neutral (or potentially get it onto your side without becoming neutral first)
                    else:  # if the (de-)capturing faction is not in control
                        responses = dist.change_capture_points(-(ewcfg.capture_tick_length * capture_speed * ewcfg.decapture_speed_multiplier), faction_capture)
                        resp_cont_capture_tick.add_response_container(responses)

                    dist.persist()


# await resp_cont_capture_tick.post()


"""
	Coroutine that continually calls capture_tick; is called once per server, and not just once globally
"""


async def capture_tick_loop(id_server):
    interval = ewcfg.capture_tick_length
    # causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
    while not ewutils.TERMINATE:
        await capture_tick(id_server=id_server)
        # ewutils.logMsg("Capture tick happened on server %s." % id_server + " Timestamp: %d" % int(time.time()))

        await asyncio.sleep(interval)


"""
	Gives both kingpins the appropriate amount of slime for how many districts they own and lowers the capture_points property of each district by a certain amount, turning them neutral after a while
"""


# Used in the market loop, trying to get EwUser out of district utils so this can go here
async def give_kingpins_slime_and_decay_capture_points(id_server):
    resp_cont_decay_loop = EwResponseContainer(client=ewutils.get_client(), id_server=id_server)

    for kingpin_role in [ewcfg.role_rowdyfucker, ewcfg.role_copkiller]:
        kingpin = fe_utils.find_kingpin(id_server=id_server, kingpin_role=kingpin_role)
        if kingpin is not None:
            kingpin = EwUser(id_server=id_server, id_user=kingpin.id_user)
            total_slimegain = 0
            for id_district in poi_static.capturable_districts:

                district = EwDistrict(id_server=id_server, district=id_district)

                # if the kingpin is controlling this district give the kingpin slime based on the district's property class
                if district.controlling_faction == (ewcfg.faction_killers if kingpin.faction == ewcfg.faction_killers else ewcfg.faction_rowdys):
                    poi = poi_static.id_to_poi.get(id_district)

                    slimegain = ewcfg.district_control_slime_yields[poi.property_class]

                    # increase slimeyields by 10 percent per friendly neighbor
                    friendly_mod = 1 + 0.1 * district.get_number_of_friendly_neighbors()
                    total_slimegain += slimegain * friendly_mod

            kingpin.change_slimes(n=total_slimegain)
            kingpin.persist()

            ewutils.logMsg(kingpin_role + " just received %d" % total_slimegain + " slime for their captured districts.")

    # Decay capture points.
    for id_district in poi_static.capturable_districts:
        district = EwDistrict(id_server=id_server, district=id_district)

        district.decay_capture_points()
        # resp_cont_decay_loop.add_response_container(responses)
        district.persist()
# await resp_cont_decay_loop.post()

""" Good ol' Clock Tick Loop. Handles everything that has to occur on an in-game hour. (15 minutes)"""

async def clock_tick_loop(id_server = None, force_active = False):
    try:
        if id_server:
            while not ewutils.TERMINATE:
                time_now = int(time.time())
                # Load the market from the database
                market_data = EwMarket(id_server)
                client = ewcfg.get_client()
                server = ewcfg.server_list[id_server]

                # Check when the last recorded tick was in the database, just to make sure we don't double up when the bot restarts.
                if market_data.time_lasttick + ewcfg.update_market <= time_now or force_active:

                    # Advance the time and potentially change weather.
                    market_data.clock += 1

                    if market_data.clock >= 24 or market_data.clock < 0:
                        market_data.clock = 0
                        market_data.day += 1

                    market_data.time_lasttick = time_now

                    ewutils.logMsg('The time is now {}.'.format(market_data.clock))

                    ewutils.logMsg("Updating stocks...")
                    await market_utils.update_stocks(id_server)
                    market_data.persist()

                    ewutils.logMsg("Handling weather cycle...")
                    await weather_utils.weather_cycle(id_server)

                    if not ewutils.check_fursuit_active(market_data):
                        await cosmetic_utils.dedorn_all_costumes()

                    await apt_utils.setOffAlarms(id_server)

                    # Decay slime totals
                    ewutils.logMsg("Decaying slimes...")
                    await decaySlimes(id_server)

                    # Increase hunger for all players below the max.
                    # ewutils.pushupServerHunger(id_server = server.id)

                    # Decrease inebriation for all players above min (0).
                    ewutils.logMsg("Handling inebriation...")
                    await pushdownServerInebriation(id_server)

                    ewutils.logMsg("Killing offers...")
                    # Remove fish offers which have timed out
                    bknd_fish.kill_dead_offers(id_server)

                    ewutils.logMsg("Deleting old ads...")
                    # kill advertisements that have timed out
                    bknd_ads.delete_expired_ads(id_server)

                    ewutils.logMsg("Handling capture points...")
                    await give_kingpins_slime_and_decay_capture_points(id_server)
                    ewutils.logMsg("Sending gangbase messages...")
                    await move_utils.send_gangbase_messages(id_server, market_data.clock)
                    ewutils.logMsg("Kicking AFK players...")
                    await move_utils.kick(id_server)

                    ewutils.logMsg("Finished clock tick.")  

                    sex_channel = fe_utils.get_channel(server=server, channel_name=ewcfg.channel_stockexchange)

                    if market_data.clock == 6 or force_active:
                        response = ' The SlimeCorp Stock Exchange is now open for business.'
                        await fe_utils.send_message(client, sex_channel, response)
                        ewutils.logMsg("Started bazaar refresh...")
                        await market_utils.refresh_bazaar(id_server)
                        ewutils.logMsg("...finished bazaar refresh.")
                        
                        await leaderboard_utils.post_leaderboards(client=client, server=server)
                        
                        if market_data.clock % 8 == 0 or force_active:
                            ewutils.logMsg("Started rent calc...")
                            await apt_utils.rent_time(id_server)
                            await pay_salary(id_server)
                            ewutils.logMsg("...finished rent calc.")

                    elif market_data.clock == 20:
                        response = ' The SlimeCorp Stock Exchange has closed for the night.'
                        await fe_utils.send_message(client, sex_channel, response)
                  
                await asyncio.sleep(60)
    except:
        ewutils.logMsg('An error occurred in the scheduled slime market update task. Fix that.')
