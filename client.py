#!/usr/bin/python3
#
# endless-war
# mperron (2018)
#
# a chat bot for the RFCK discord server

import asyncio
import json
import logging
import os
import random
import re
import shlex
import subprocess
import sys
import time
import traceback

import discord

from ew.cmd import cmd_map, dm_cmd_map, apt_dm_cmd_map
import ew.cmd.cmds as ewcmd
try:
    from ew.cmd import debug as ewdebug
except:
    from ew.cmd import debug_dummy as ewdebug
import ew.cmd.dungeons as ewdungeons
import ew.cmd.item as ewitem

import ew.utils.apt as apt_utils
import ew.utils.cmd as cmd_utils
import ew.utils.cosmeticitem as cosmetic_utils
import ew.utils.dungeons as dungeon_utils
import ew.utils.frontend as fe_utils
import ew.utils.item as itm_utils
import ew.utils.leaderboard as bknd_leaderboard
import ew.utils.loop as loop_utils
import ew.utils.market as market_utils
import ew.utils.move as move_utils
import ew.utils.rolemgr as ewrolemgr
import ew.utils.slimeoid as slimeoid_utils
import ew.utils.sports as sports_utils
import ew.utils.transport as transport_utils
import ew.utils.weather as bknd_weather
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict

import ew.backend.ads as bknd_ads
import ew.backend.core as bknd_core
import ew.backend.farm as bknd_farm
import ew.backend.fish as bknd_fish
import ew.backend.item as bknd_item
import ew.backend.player as bknd_player
import ew.backend.server as bknd_server
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.market import EwStock
from ew.backend.player import EwPlayer
from ew.backend.status import EwStatusEffect

import ew.utils.core as ewutils

import ew.static.cosmetics as cosmetics
import ew.static.food as static_food
import ew.static.items as static_items
import ew.static.poi as poi_static
import ew.static.vendors as vendors
import ew.static.weather as weather_static

import ew.static.cfg as ewcfg


ewutils.logMsg('Starting up...')
init_complete = False

# output discord logs to console
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s]:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.all()

client = discord.Client(intents=intents)

# A map containing user IDs and the last time in UTC seconds since we sent them
# the help doc via DM. This is to prevent spamming.
last_helped_times = {}

# Map of server ID to a map of active users on that server.
active_users_map = {}

# Map of server ID to slime twitter channels
channels_slimetwitter = {}

# Map of all command words in the game to their implementing function.
#cmd_map = cmds.cmd_map

# Map of commands always allowed in dms
#dm_cmd_map = cmds.dm_cmd_map

# Map of commands only allowed in dms while in an apartment
#apt_dm_cmd_map = cmds.apt_dm_cmd_map

debug = False
db_prefix = '--db='
while sys.argv:
    arg_lower = sys.argv[0].lower()
    if arg_lower == '--debug':
        debug = True
    elif arg_lower == '--debugallon': #set all debug option true at startup
        debug = True
        for option in ewutils.DEBUG_OPTIONS:
            ewutils.DEBUG_OPTIONS[option] = True
    elif arg_lower.startswith(db_prefix):
        ewcfg.database = arg_lower[len(db_prefix):]

    sys.argv = sys.argv[1:]

# When debug is enabled, additional commands are turned on.
if debug == True:
    ewutils.DEBUG = True
    ewutils.logMsg('Debug mode enabled.')

ewutils.logMsg('Using database: {}'.format(ewcfg.database))


@client.event
async def on_member_remove(member):
    # Kill players who leave the server.
    try:
        user_data = EwUser(member=member)

        # don't kill players who haven't cleared the tutorial yet
        if user_data.poi in poi_static.tutorial_pois:
            return

        user_data.trauma = ewcfg.trauma_id_suicide
        user_data.die(cause=ewcfg.cause_leftserver)
        user_data.persist()

        ewutils.logMsg('Player killed for leaving the server.')
    except:
        ewutils.logMsg('Failed to kill member who left the server.')


@client.event
async def on_member_update(before, after):
    # update last offline time if they went from offline to online
    try:
        if before.status == discord.Status.offline and after.status != discord.Status.offline:
            user_data = EwUser(member=after)
            user_data.time_lastoffline = int(time.time())
            user_data.persist()
    except:
        ewutils.logMsg('Failed to update member\'s last offline time.')


@client.event
async def on_ready():

    try:
        await client.change_presence(activity=discord.Game(name="EW " + ewcfg.version))
    except:
        ewutils.logMsg("Failed to change_presence!")

    global init_complete
    if init_complete:
        return
    init_complete = True
    ewcfg.set_client(client)
    ewutils.logMsg('Logged in as {} ({}).'.format(client.user.name, client.user.id))

    ewutils.logMsg("Loaded NLACakaNM world map. ({}x{})".format(move_utils.map_width, move_utils.map_height))
    move_utils.map_draw()

    # Flatten role names to all lowercase, no spaces.
    fake_observer = EwUser()
    fake_observer.life_state = ewcfg.life_state_observer
    for poi in poi_static.poi_list:
        if poi.role != None:
            poi.role = ewutils.mapRoleName(poi.role)
        if poi.major_role != None:
            poi.major_role = ewutils.mapRoleName(poi.major_role)
        if poi.minor_role != None:
            poi.minor_role = ewutils.mapRoleName(poi.minor_role)

        neighbors = []
        neighbor_ids = []
        # if poi.coord != None:
        if len(poi.neighbors.keys()) > 0:
            neighbors = move_utils.path_to(poi_start=poi.id_poi, user_data=fake_observer)
        # elif poi.id_poi == ewcfg.poi_id_thesewers:
        #	neighbors = poi_static.poi_list

        if neighbors != None:

            for neighbor in neighbors:
                neighbor_ids.append(neighbor.id_poi)

        poi_static.poi_neighbors[poi.id_poi] = set(neighbor_ids)
        ewutils.logMsg("Found neighbors for poi {}: {}".format(poi.id_poi, poi_static.poi_neighbors[poi.id_poi]))

    for id_poi in poi_static.landmark_pois:
        ewutils.logMsg("beginning landmark precomputation for " + id_poi)
        move_utils.landmarks[id_poi] = move_utils.score_map_from(
            poi_start=id_poi,
            user_data=fake_observer,
            landmark_mode=True
        )

    cosmetic_utils.update_hues()

    ewutils.logMsg("finished landmark precomputation")


    # Look for a Twitch client_id on disk.
    # FIXME debug - temporarily disable Twitch integration
    if False:
        twitch_client_id = ewutils.getTwitchClientId()

    # If no twitch client ID is available, twitch integration will be disabled.
    # FIXME debug - temporarily disable Twitch integration.
    if True:
        twitch_client_id = None
        ewutils.logMsg('Twitch integration disabled.')
    elif twitch_client_id == None or len(twitch_client_id) == 0:
        ewutils.logMsg('No twitch_client_id file found. Twitch integration disabled.')
    else:
        ewutils.logMsg("Enabled Twitch integration.")

    # Channels in the connected discord servers to announce to.
    channels_announcement = []

    # Channels in the connected discord servers to send stock market updates to. Map of server ID to channel.
    channels_stockmarket = {}

    for server in client.guilds:
        # Update server data in the database
        bknd_server.server_update(server=server)

        # store the list of channels in an ewutils field
        ewcfg.update_server_list(server=server)

        # find roles and add them tom the database
        ewrolemgr.setupRoles(client=client, id_server=server.id)

        # Refresh the permissions of all users
        # await ewrolemgr.refresh_user_perms(client = client, id_server = server.id, startup = True)

        # Grep around for channels
        ewutils.logMsg("connected to server: {}".format(server.name))
        for channel in server.channels:
            if (channel.type == discord.ChannelType.text):
                if (channel.name == ewcfg.channel_twitch_announcement):
                    channels_announcement.append(channel)
                    ewutils.logMsg("• found channel for announcements: {}".format(channel.name))

                elif (channel.name == ewcfg.channel_stockexchange):
                    channels_stockmarket[server.id] = channel
                    ewutils.logMsg("• found channel for stock exchange: {}".format(channel.name))

                elif (channel.name == ewcfg.channel_slimetwitter):
                    channels_slimetwitter[server.id] = channel
                    ewutils.logMsg("• found channel for slime twitter: {}".format(channel.name))
        ewdebug.initialize_gamestate(id_server=server.id)
        # create all the districts in the database
        for poi_object in poi_static.poi_list:
            poi = poi_object.id_poi
            # call the constructor to create an entry if it doesnt exist yet
            dist = EwDistrict(id_server=server.id, district=poi)
            # change the ownership to the faction that's already in control to initialize topic names
            try:
                # initialize gang bases
                if poi == ewcfg.poi_id_rowdyroughhouse:
                    dist.controlling_faction = ewcfg.faction_rowdys
                elif poi == ewcfg.poi_id_copkilltown:
                    dist.controlling_faction = ewcfg.faction_killers

                resp_cont = dist.change_ownership(new_owner=dist.controlling_faction, actor="init", client=client)
                dist.persist()
                await resp_cont.post()

            except:
                ewutils.logMsg('Could not change ownership for {} to "{}".'.format(poi, dist.controlling_faction))

        # kill people who left the server while the bot was offline
        # ewutils.kill_quitters(server.id) #FIXME function get_member doesn't find users reliably

        asyncio.ensure_future(loop_utils.capture_tick_loop(id_server=server.id))
        asyncio.ensure_future(loop_utils.bleed_tick_loop(id_server=server.id))
        asyncio.ensure_future(loop_utils.enemy_action_tick_loop(id_server=server.id))
        asyncio.ensure_future(loop_utils.burn_tick_loop(id_server=server.id))
        asyncio.ensure_future(loop_utils.remove_status_loop(id_server=server.id))
        asyncio.ensure_future(loop_utils.event_tick_loop(id_server=server.id))

        # SWILLDERMUK
        # asyncio.ensure_future(ewutils.spawn_prank_items_tick_loop(id_server = server.id))
        # asyncio.ensure_future(ewutils.generate_credence_tick_loop(id_server = server.id))

        if ewcfg.gvs_active:
            asyncio.ensure_future(loop_utils.gvs_gamestate_tick_loop(id_server=server.id))
        else:
            # Enemies do not spawn randomly during Gankers Vs. Shamblers
            asyncio.ensure_future(loop_utils.spawn_enemies_tick_loop(id_server=server.id))

        if not debug:
            await transport_utils.init_transports(id_server=server.id)
            asyncio.ensure_future(bknd_weather.weather_tick_loop(id_server=server.id))
        asyncio.ensure_future(slimeoid_utils.slimeoid_tick_loop(id_server=server.id))
        asyncio.ensure_future(bknd_farm.farm_tick_loop(id_server=server.id))
        asyncio.ensure_future(sports_utils.slimeball_tick_loop(id_server=server.id))

        print('\nNUMBER OF CHANNELS IN SERVER: {}\n'.format(len(server.channels)))

    try:
        ewutils.logMsg('Creating message queue directory.')
        os.mkdir(ewcfg.dir_msgqueue)
    except FileExistsError:
        ewutils.logMsg('Message queue directory already exists.')

    ewutils.logMsg('Ready.')

    """
        Set up for infinite loop to perform periodic tasks.
    """
    time_now = int(time.time())
    time_last_pvp = time_now

    time_last_twitch = time_now
    time_twitch_downed = 0

    # Every three hours we log a message saying the periodic task hook is still active. On startup, we want this to happen within about 60 seconds, and then on the normal 3 hour interval.
    time_last_logged = time_now - ewcfg.update_hookstillactive + 60

    stream_live = None

    ewutils.logMsg('Beginning periodic hook loop.')
    while not ewutils.TERMINATE:
        time_now = int(time.time())

        # Periodic message to log that this stuff is still running.
        if (time_now - time_last_logged) >= ewcfg.update_hookstillactive:
            time_last_logged = time_now

            ewutils.logMsg("Periodic hook still active.")

        # Check to see if a stream is live via the Twitch API.
        # FIXME disabled
        if False:
            # if twitch_client_id != None and (time_now - time_last_twitch) >= ewcfg.update_twitch:
            time_last_twitch = time_now

            try:
                # Twitch API call to see if there are any active streams.
                json_string = ""
                p = subprocess.Popen(
                    "curl -H 'Client-ID: {}' -X GET 'https://api.twitch.tv/helix/streams?user_login = rowdyfrickerscopkillers' 2>/dev/null".format(twitch_client_id),
                    shell=True,
                    stdout=subprocess.PIPE
                )

                for line in p.stdout.readlines():
                    json_string += line.decode('utf-8')

                json_parsed = json.loads(json_string)

                # When a stream is up, data is an array of stream information objects.
                data = json_parsed.get('data')
                if data != None:
                    data_count = len(data)
                    stream_was_live = stream_live
                    stream_live = True if data_count > 0 else False

                    if stream_was_live == True and stream_live == False:
                        time_twitch_downed = time_now

                    if stream_was_live == False and stream_live == True and (time_now - time_twitch_downed) > 600:
                        ewutils.logMsg("The stream is now live.")

                        # The stream has transitioned from offline to online. Make an announcement!
                        for channel in channels_announcement:
                            await fe_utils.send_message(
                                client,
                                channel,
                                "ATTENTION CITIZENS. THE **ROWDY FUCKER** AND THE **COP KILLER** ARE **STREAMING**. BEWARE OF INCREASED KILLER AND ROWDY ACTIVITY.\n\n@everyone\n{}".format(
                                    "https://www.twitch.tv/rowdyfrickerscopkillers"
                                )
                            )
            except:
                ewutils.logMsg('Twitch handler hit an exception (continuing): {}'.format(json_string))
                traceback.print_exc(file=sys.stdout)

        # Adjust the exchange rate of slime for the market.
        try:
            for server in client.guilds:

                # Load market data from the database.
                market_data = EwMarket(id_server=server.id)

                if market_data.time_lasttick + ewcfg.update_market <= time_now:

                    market_response = ""
                    exchange_data = EwDistrict(district=ewcfg.poi_id_stockexchange, id_server=server.id)

                    for stock in ewcfg.stocks:
                        s = EwStock(server.id, stock)
                        # we don't update stocks when they were just added
                        # or when shamblers have degraded it
                        if s.timestamp != 0 and not exchange_data.is_degraded():
                            s.timestamp = time_now
                            market_response = market_utils.market_tick(s, server.id)
                            await fe_utils.send_message(client, channels_stockmarket.get(server.id), market_response)

                    market_data = EwMarket(id_server=server.id)
                    market_data.time_lasttick = time_now

                    # Advance the time and potentially change weather.
                    market_data.clock += 1

                    if market_data.clock >= 24 or market_data.clock < 0:
                        market_data.clock = 0
                        market_data.day += 1

                    if market_data.clock == 6:
                        # Update the list of available bazaar items by clearing the current list and adding the new items
                        market_data.bazaar_wares.clear()

                        bazaar_foods = []
                        bazaar_cosmetics = []
                        bazaar_general_items = []
                        bazaar_furniture = []

                        for item in vendors.vendor_inv.get(ewcfg.vendor_bazaar):
                            if item in static_items.item_names:
                                bazaar_general_items.append(item)

                            elif item in static_food.food_names:
                                bazaar_foods.append(item)

                            elif item in cosmetics.cosmetic_names:
                                bazaar_cosmetics.append(item)

                            elif item in static_items.furniture_names:
                                bazaar_furniture.append(item)

                        market_data.bazaar_wares['slimecorp1'] = ewcfg.weapon_id_umbrella
                        market_data.bazaar_wares['slimecorp2'] = ewcfg.cosmetic_id_raincoat

                        market_data.bazaar_wares['generalitem'] = random.choice(bazaar_general_items)

                        market_data.bazaar_wares['food1'] = random.choice(bazaar_foods)
                        # Don't add repeated foods
                        bw_food2 = None
                        while bw_food2 is None or bw_food2 in market_data.bazaar_wares.values():
                            bw_food2 = random.choice(bazaar_foods)

                        market_data.bazaar_wares['food2'] = bw_food2

                        market_data.bazaar_wares['cosmetic1'] = random.choice(bazaar_cosmetics)
                        # Don't add repeated cosmetics
                        bw_cosmetic2 = None
                        while bw_cosmetic2 is None or bw_cosmetic2 in market_data.bazaar_wares.values():
                            bw_cosmetic2 = random.choice(bazaar_cosmetics)

                        market_data.bazaar_wares['cosmetic2'] = bw_cosmetic2

                        bw_cosmetic3 = None
                        while bw_cosmetic3 is None or bw_cosmetic3 in market_data.bazaar_wares.values():
                            bw_cosmetic3 = random.choice(bazaar_cosmetics)

                        market_data.bazaar_wares['cosmetic3'] = bw_cosmetic3

                        market_data.bazaar_wares['furniture1'] = random.choice(bazaar_furniture)

                        bw_furniture2 = None
                        while bw_furniture2 is None or bw_furniture2 in market_data.bazaar_wares.values():
                            bw_furniture2 = random.choice(bazaar_furniture)

                        market_data.bazaar_wares['furniture2'] = bw_furniture2

                        bw_furniture3 = None
                        while bw_furniture3 is None or bw_furniture3 in market_data.bazaar_wares.values():
                            bw_furniture3 = random.choice(bazaar_furniture)

                        market_data.bazaar_wares['furniture3'] = bw_furniture3

                        if random.random() < 0.05:  # 1 / 20
                            market_data.bazaar_wares['minigun'] = ewcfg.weapon_id_minigun

                        if random.random() < 0.05:  # 1 / 20
                            market_data.bazaar_wares['bustedrifle'] = ewcfg.item_id_bustedrifle

                    market_data.persist()

                    ewutils.logMsg('The time is now {}.'.format(market_data.clock))

                    if not ewutils.check_fursuit_active(market_data):
                        cosmetic_utils.dedorn_all_costumes()

                    if market_data.clock == 6 and market_data.day % 8 == 0:
                        await apt_utils.rent_time(id_server=server.id)
                        await loop_utils.pay_salary(id_server=server.id)

                    market_data = EwMarket(id_server=server.id)

                    market_data.persist()
                    if market_data.clock == 6:
                        response = ' The SlimeCorp Stock Exchange is now open for business.'
                        await fe_utils.send_message(client, channels_stockmarket.get(server.id), response)
                    elif market_data.clock == 20:
                        response = ' The SlimeCorp Stock Exchange has closed for the night.'
                        await fe_utils.send_message(client, channels_stockmarket.get(server.id), response)

                    market_data = EwMarket(id_server=server.id)

                    if random.randrange(3) == 0:
                        pattern_count = len(weather_static.weather_list)

                        if pattern_count > 1:
                            weather_old = market_data.weather

                            # if random.random() < 0.4:
                            # 	market_data.weather = ewcfg.weather_bicarbonaterain

                            # Randomly select a new weather pattern. Try again if we get the same one we currently have.
                            while market_data.weather == weather_old:
                                pick = random.randrange(len(weather_static.weather_list))
                                market_data.weather = weather_static.weather_list[pick].name

                        # Log message for statistics tracking.
                        ewutils.logMsg("The weather changed. It's now {}.".format(market_data.weather))

                    # Persist new data.
                    market_data.persist()

                    await apt_utils.setOffAlarms(id_server=server.id)

                    # Decay slime totals
                    loop_utils.decaySlimes(id_server=server.id)

                    # Increase hunger for all players below the max.
                    # ewutils.pushupServerHunger(id_server = server.id)

                    # Decrease inebriation for all players above min (0).
                    loop_utils.pushdownServerInebriation(id_server=server.id)

                    # Remove fish offers which have timed out
                    bknd_fish.kill_dead_offers(id_server=server.id)

                    # kill advertisements that have timed out
                    bknd_ads.delete_expired_ads(id_server=server.id)

                    await loop_utils.give_kingpins_slime_and_decay_capture_points(id_server=server.id)
                    await move_utils.send_gangbase_messages(server.id, market_data.clock)
                    await move_utils.kick(server.id)

                    # Post leaderboards at 6am NLACakaNM time.
                    if market_data.clock == 6:
                        await bknd_leaderboard.post_leaderboards(client=client, server=server)

        except:
            ewutils.logMsg('An error occurred in the scheduled slime market update task:')
            traceback.print_exc(file=sys.stdout)

        # Parse files dumped into the msgqueue directory and send messages as needed.
        try:
            for msg_file in os.listdir(ewcfg.dir_msgqueue):
                fname = "{}/{}".format(ewcfg.dir_msgqueue, msg_file)

                msg = fe_utils.readMessage(fname)
                os.remove(fname)

                msg_channel_names = []
                msg_channel_names_reverb = []

                if msg.channel != None:
                    msg_channel_names.append(msg.channel)

                if msg.poi != None:
                    poi = poi_static.id_to_poi.get(msg.poi)
                    if poi != None:
                        if poi.channel != None and len(poi.channel) > 0:
                            msg_channel_names.append(poi.channel)

                        if msg.reverb == True:
                            pois_adjacent = move_utils.path_to(poi_start=msg.poi)

                            for poi_adjacent in pois_adjacent:
                                if poi_adjacent.channel != None and len(poi_adjacent.channel) > 0:
                                    msg_channel_names_reverb.append(poi_adjacent.channel)

                if len(msg_channel_names) == 0:
                    ewutils.logMsg('in file {} message for channel {} (reverb {})\n{}'.format(msg_file, msg.channel, msg.reverb, msg.message))
                else:
                    # Send messages to every connected server.
                    for server in client.guilds:
                        for channel in server.channels:
                            if channel.name in msg_channel_names:
                                await fe_utils.send_message(client, channel, "**{}**".format(msg.message))
                            elif channel.name in msg_channel_names_reverb:
                                await fe_utils.send_message(client, channel, "**Something is happening nearby...\n\n{}**".format(msg.message))
        except:
            ewutils.logMsg('An error occurred while trying to process the message queue:')
            traceback.print_exc(file=sys.stdout)

        # Wait a while before running periodic tasks.
        await asyncio.sleep(15)


@client.event
async def on_member_join(member):
    ewutils.logMsg("New member \"{}\" joined. Configuring default roles / permissions now.".format(member.display_name))
    await ewrolemgr.updateRoles(client=client, member=member)
    bknd_player.player_update(
        member=member,
        server=member.guild
    )
    user_data = EwUser(member=member)

    if user_data.poi in poi_static.tutorial_pois:
        await dungeon_utils.begin_tutorial(member)


@client.event
async def on_message_delete(message):
    if message != None and message.guild != None and message.author.id != client.user.id and message.content.startswith(ewcfg.cmd_prefix):
        user_data = EwUser(member=message.author)
        mutations = user_data.get_mutations()

        if ewcfg.mutation_id_amnesia not in mutations:
            ewutils.logMsg("deleted message from {}: {}".format(message.author.display_name, message.content))
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, '**I SAW THAT.**'))


@client.event
async def on_message(message):
    time_now = int(time.time())
    ewcfg.set_client(client)

    """ do not interact with our own messages """
    if message.author.id == client.user.id or message.author.bot == True:
        return

    if message.guild != None:
        # Note that the user posted a message.
        active_map = active_users_map.get(message.guild.id)
        if active_map == None:
            active_map = {}
            active_users_map[message.guild.id] = active_map
        active_map[message.author.id] = True

        # Update player information.
        bknd_player.player_update(
            member=message.author,
            server=message.guild
        )

    content_tolower = message.content.lower()
    content_tolower_list = content_tolower.split(" ")

    re_awoo = re.compile('.*![a]+[w]+o[o]+.*')
    re_moan = re.compile('.*![b]+[r]+[a]+[i]+[n]+[z]+.*')

    # update the player's time_last_action which is used for kicking AFK players out of subzones
    if message.guild != None:

        try:
            bknd_core.execute_sql_query("UPDATE users SET {time_last_action} = %s WHERE id_user = %s AND id_server = %s".format(
                time_last_action=ewcfg.col_time_last_action
            ), (
                int(time.time()),
                message.author.id,
                message.guild.id
            ))
        except:
            ewutils.logMsg('server {}: failed to update time_last_action for {}'.format(message.guild.id, message.author.id))

        user_data = EwUser(member=message.author)
        statuses = user_data.getStatusEffects()

        if ewcfg.status_strangled_id in statuses:
            strangle_effect = EwStatusEffect(id_status=ewcfg.status_strangled_id, user_data=user_data)
            source = EwPlayer(id_user=strangle_effect.source, id_server=message.guild.id)
            response = "You manage to break {}'s garrote wire!".format(source.display_name)
            user_data.clear_status(ewcfg.status_strangled_id)
            return await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        if ewutils.active_restrictions.get(user_data.id_user) == 3:
            user_data.trauma = ewcfg.trauma_id_environment
            die_resp = user_data.die(cause=ewcfg.cause_praying)
            user_data.persist()
            await ewrolemgr.updateRoles(client=client, member=message.author)
            await die_resp.post()

            response = "ENDLESS WAR completely and utterly obliterates {} with a bone-hurting beam.".format(message.author.display_name).replace("@", "\{at\}")
            return await fe_utils.send_message(client, message.channel, response)
        if str(message.channel) in ["nurses-office", "suggestion-box", "detention-center", "community-service", "playground", "graffiti-wall", "post-slime-drip", "outside-the-lunchroom", "outside-the-lunchrooom"]:
            if ewcfg.status_hogtied_id in statuses:
                response = random.choice(["MMMPH!", "MBBBBB", "HMMHM", "MMMMMHMMF!"])
                await fe_utils.send_message(client, message.channel, response)
                await message.delete()
                return

    if message.content.startswith(ewcfg.cmd_prefix) or message.guild == None or (any(swear in content_tolower for swear in ewcfg.curse_words.keys())) or message.channel in ["nurses-office", "suggestion-box", "detention-center", "community-service", "playground", "graffiti-wall", "post-slime-drip", "outside-the-lunchroom", "outside-the-lunchrooom"]:
        """
            Wake up if we need to respond to messages. Could be:
                message starts with !
                direct message (server == None)
                user is new/has no roles (len(roles) < 4)
                user is a security officer and has cussed
        """

        # Ignore users with weird characters in their name

        try:
            message.author.display_name[:3].encode('utf-8').decode('ascii')
        except UnicodeError:
            return await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, "We don't take kindly to moon runes around here."))

        # tokenize the message. the command should be the first word.
        try:
            tokens = shlex.split(message.content)  # it's split with shlex now because shlex regards text within quotes as a single token
        except:
            tokens = message.content.split(' ')  # if splitting via shlex doesnt work (odd number of quotes), use the old splitting method so it doesnt give an exception

        tokens_count = len(tokens)
        cmd = tokens[0].lower() if tokens_count >= 1 else ""

        mentions = message.mentions
        mentions_count = len(mentions)

        playermodel = EwPlayer(id_user=message.author.id)

        if message.guild == None:
            guild_used = ewcfg.server_list[playermodel.id_server]
            admin_permissions = False
        else:
            guild_used = message.guild
            admin_permissions = message.author.guild_permissions.administrator

        # Create command object
        cmd_obj = cmd_utils.EwCmd(
            tokens=tokens,
            message=message,
            client=client,
            mentions=mentions,
            guild=guild_used,
            admin=admin_permissions
        )

        # remove mentions to us #moved below cmd_obj because of EwIds #TODO: remove this and move debug commands somewhere else
        mentions = list(filter(lambda user: user.id != client.user.id, message.mentions))
        mentions_count = len(mentions)

        """
            Punish the user for swearing.
            The swear_jar attribute has been repurposed for SlimeCorp security officers
        """
        if (any(swear in content_tolower for swear in ewcfg.curse_words.keys())):
            # print(content_tolower_list)
            swear_multiplier = 0
            usermodel = EwUser(id_user=message.author.id, id_server=playermodel.id_server)

            if usermodel != None:
                market_data = EwMarket(id_server=usermodel.id_server)

                if usermodel.faction == ewcfg.faction_slimecorp and usermodel.life_state == ewcfg.life_state_enlisted:

                    # gather all the swear words the user typed.
                    for swear in ewcfg.curse_words.keys():

                        swear_count = content_tolower.count(swear)

                        # Niche scenarios. If certain words are used, don't count their components as swears.
                        if swear == "shit" and "shit" not in content_tolower:
                            # print('swear detection turned off for {}.'.format(swear))
                            continue

                        # This one's funny, keep this one on. Bit of a gamer...
                        # elif swear == "fag" and "fag" not in content_tolower:
                        # print('swear detection turned off for {}.'.format(swear))
                        # continue

                        elif swear == "fuck" and (content_tolower.count('<rowdyfucker431275088076079105>') > 0 or content_tolower.count('<fucker431424220837183489>') > 0):
                            # print('swear detection turned off for {}.'.format(swear))
                            continue
                        elif swear == "mick" and (content_tolower.count('gimmick') > 0):
                            # print('swear detection turned off for {}.'.format(swear))
                            continue

                        for i in range(swear_count):
                            swear_multiplier += ewcfg.curse_words[swear]

                        # usermodel.swear_jar += 1

                    # print('multiplier: {}'.format(swear_multiplier))

                    # don't fine the user or send out the message if there weren't enough curse words
                    if swear_multiplier > 10:
                        # fine the user for swearing, based on how much they've sworn right now, as well as in the past
                        swear_jar_fee = swear_multiplier * 10000

                        usermodel.salary_credits -= swear_jar_fee

                        response = '*{}*: Your SlimeCorp headset chatters in your ear...\n"Reminder: Foul language is strictly prohibited. {} salary credits have been docked from your profile."'.format(message.author.display_name, swear_jar_fee)
                        await fe_utils.send_message(client, message.channel, response)

                    market_data.persist()
                    usermodel.persist()

            # if the message wasn't a command, we can stop here
            if not message.content.startswith(ewcfg.cmd_prefix):
                return

        """
            Handle direct messages.
        """
        if message.guild == None:
            playermodel = EwPlayer(id_user=message.author.id)
            usermodel = EwUser(id_user=message.author.id, id_server=playermodel.id_server)
            poi = poi_static.id_to_poi.get(usermodel.poi)
            cmd_obj.guild = ewcfg.server_list[playermodel.id_server]
            cmd_obj.message.author = cmd_obj.guild.get_member(playermodel.id_user)

            # Handle DM compatible commands
            if cmd in dm_cmd_map:
                cmd_fnc = dm_cmd_map.get(cmd)
                if cmd_fnc:
                    return await cmd_fnc(cmd_obj)
            elif poi.is_apartment and cmd in apt_dm_cmd_map:
                cmd_fnc = apt_dm_cmd_map.get(cmd)
                if cmd_fnc:
                    return await cmd_fnc(cmd_obj)
            else:
                # Only send the help response once every thirty seconds. There's no need to spam it.
                # Also, don't send out response if the user doesn't actually type a command.
                if message.content.startswith(ewcfg.cmd_prefix):
                    time_last = last_helped_times.get(message.author.id, 0)
                    if (time_now - time_last) > 30:
                        last_helped_times[message.author.id] = time_now
                        direct_help_response = "ENDLESS WAR doesn't allow you to do that command in DMs.\nIf you're confused about what you're doing, you might want to get some **!help** over at the server."
                        await fe_utils.send_message(client, message.channel, direct_help_response)
                else:
                    return

            # Nothing else to do in a DM.
            return

        # assign the appropriate roles to a user with less than @everyone, faction, both location roles
        # if len(message.author.roles) < 4:
        # await ewrolemgr.updateRoles(client = client, member = message.author)

        user_data = EwUser(member=message.author)
        if user_data.arrested:
            return

        mutations = user_data.get_mutations()
        # Scold/ignore offline players.
        if message.author.status == discord.Status.offline:

            if ewcfg.mutation_id_chameleonskin not in mutations or cmd not in ewcfg.offline_cmds:
                response = "You cannot participate in the ENDLESS WAR while offline."

                return await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        if user_data.time_lastoffline > time_now - ewcfg.time_offline:

            if ewcfg.mutation_id_chameleonskin not in mutations or cmd not in ewcfg.offline_cmds:
                response = "You are too paralyzed by ENDLESS WAR's judgemental stare to act."

                return await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        statuses = user_data.getStatusEffects()
        # Ignore stunned players
        if ewcfg.status_stunned_id in statuses:
            return

        # Check the main command map for the requested command.
        #global cmd_map
        cmd_fn = cmd_map.get(cmd)

        if user_data.poi in ewdebug.act_pois.keys():
            if content_tolower in ewdebug.act_pois.get(user_data.poi).keys():
                return await ewdebug.act(cmd_obj, user_data.poi, content_tolower)

        if user_data.poi in poi_static.tutorial_pois:
            return await ewdungeons.tutorial_cmd(cmd_obj)

        elif cmd_fn != None:
            # Execute found command
            return await cmd_fn(cmd_obj)

        # FIXME debug
        # Test item creation
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createtestitem'):
            item_id = bknd_item.item_create(
                item_type='medal',
                id_user=message.author.id,
                id_server=message.guild.id,
                item_props={
                    'medal_name': 'Test Award',
                    'medal_desc': '**{medal_name}**: *Awarded to Krak by Krak for testing shit.*'
                }
            )

            ewutils.logMsg('Created item: {}'.format(item_id))
            item = EwItem(id_item=item_id)
            item.item_props['test'] = 'meow'
            item.persist()

            item = EwItem(id_item=item_id)

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, ewitem.item_look(item)))

        # Creates a poudrin
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createpoudrin'):
            for item in static_items.item_list:
                if item.context == "poudrin":
                    poudrin_count = 1
                    if cmd_obj.tokens_count > 1:
                        try:
                            poudrin_count = int(cmd_obj.tokens[1])
                        except:
                            poudrin_count = 1
                    for i in range(poudrin_count):
                        bknd_item.item_create(
                            item_type=ewcfg.it_item,
                            id_user=message.author.id,
                            id_server=message.guild.id,
                            item_props={
                                'id_item': item.id_item,
                                'context': item.context,
                                'item_name': item.str_name,
                                'item_desc': item.str_desc,
                            }
                        )
                        ewutils.logMsg('Created item: {}'.format(item.id_item))
            else:
                pass

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, "Poudrin(s) created."))

        # Shows damage
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'damage'):
            user_data = EwUser(member=message.author, data_level=1)
            slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 60)
            # disabled until held items update
            # attack_stat_multiplier = 1 + (user_data.attack / 50) # 2% more damage per stat point
            attack_stat_multiplier = 1
            weapon_skill_multiplier = 1 + ((user_data.weaponskill * 5) / 100)  # 5% more damage per skill point
            slimes_damage = int(10 * slimes_spent * attack_stat_multiplier * weapon_skill_multiplier)  # ten times slime spent, multiplied by both multipliers
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, "{}".format(slimes_damage)))

        # Gives the user some slime
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'getslime'):
            user_data = EwUser(member=message.author)
            user_initial_level = user_data.slimelevel

            response = "You get 1,000,000 slime!"

            levelup_response = user_data.change_slimes(n=1000000)

            was_levelup = True if user_initial_level < user_data.slimelevel else False

            if was_levelup:
                response += " {}".format(levelup_response)

            user_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'getcoin'):
            user_data = EwUser(member=message.author)
            user_data.change_slimecoin(n=1000000000000, coinsource=ewcfg.coinsource_spending)

            response = "You get 1,000,000,000,000 slimecoin!"

            user_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        # Deletes all items in your inventory.
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'clearinv'):
            user_data = EwUser(member=message.author)
            bknd_item.item_destroyall(id_server=message.guild.id, id_user=message.author.id)
            response = "You destroy every single item in your inventory."
            user_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createapple'):
            item_id = bknd_item.item_create(
                id_user=message.author.id,
                id_server=message.guild.id,
                item_type=ewcfg.it_food,
                item_props={
                    'id_food': "direapples",
                    'food_name': "Dire Apples",
                    'food_desc': "This sure is a illegal Dire Apple!",
                    'recover_hunger': 500,
                    'str_eat': "You chomp into this illegal Dire Apple.",
                    'time_expir': int(time.time() + ewcfg.farm_food_expir)
                }
            )

            ewutils.logMsg('Created item: {}'.format(item_id))
            item = EwItem(id_item=item_id)
            item.item_props['test'] = 'meow'
            item.persist()

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, "Apple created."))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'weathertick'):

            await apt_utils.setOffAlarms(id_server=message.guild.id)

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createhat'):
            patrician_rarity = 20
            patrician_smelted = random.randint(1, patrician_rarity)
            patrician = False

            if patrician_smelted == 1:
                patrician = True

            items = []

            for cosmetic in cosmetics.cosmetic_items_list:
                if patrician and cosmetic.rarity == ewcfg.rarity_patrician:
                    items.append(cosmetic)
                elif not patrician and cosmetic.rarity == ewcfg.rarity_plebeian:
                    items.append(cosmetic)

            item = items[random.randint(0, len(items) - 1)]

            item_props = itm_utils.gen_item_props(item)

            item_id = bknd_item.item_create(
                item_type=item.item_type,
                id_user=message.author.id,
                id_server=message.guild.id,
                item_props=item_props
            )

            ewutils.logMsg('Created item: {}'.format(item_id))
            item = EwItem(id_item=item_id)
            item.item_props['test'] = 'meow'
            item.persist()

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, "Hat created."))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createfood'):
            item = static_food.food_list[random.randint(0, len(static_food.food_list) - 1)]

            item_id = bknd_item.item_create(
                item_type=ewcfg.it_food,
                id_user=message.author.id,
                id_server=message.guild.id,
                item_props={
                    'id_food': item.id_food,
                    'food_name': item.str_name,
                    'food_desc': item.str_desc,
                    'recover_hunger': item.recover_hunger,
                    'str_eat': item.str_eat,
                    'time_expir': item.time_expir
                }
            )

            ewutils.logMsg('Created item: {}'.format(item_id))
            item = EwItem(id_item=item_id)
            item.item_props['test'] = 'meow'
            item.persist()

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, "Food created."))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createdye'):
            item = static_items.dye_list[random.randint(0, len(static_items.dye_list) - 1)]

            item_props = itm_utils.gen_item_props(item)

            bknd_item.item_create(
                item_type=item.item_type,
                id_user=message.author.id,
                id_server=message.guild.id,
                item_props=item_props
            )

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, "{} created.".format(item.str_name)))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createoldhat'):
            patrician_rarity = 20
            patrician_smelted = random.randint(1, patrician_rarity)
            patrician = False

            if patrician_smelted == 1:
                patrician = True

            cosmetics_list = []

            for result in cosmetics.cosmetic_items_list:
                if result.acquisition == ewcfg.acquisition_smelting:
                    cosmetics_list.append(result)
                else:
                    pass

            items = []

            for cosmetic in cosmetics_list:
                if patrician and cosmetic.rarity == ewcfg.rarity_patrician:
                    items.append(cosmetic)
                elif not patrician and cosmetic.rarity == ewcfg.rarity_plebeian:
                    items.append(cosmetic)

            item = items[random.randint(0, len(items) - 1)]

            bknd_item.item_create(
                item_type=ewcfg.it_cosmetic,
                id_user=message.author.id,
                id_server=message.guild.id,
                item_props={
                    'id_cosmetic': item.id_cosmetic,
                    'cosmetic_name': item.str_name,
                    'cosmetic_desc': item.str_desc,
                    'rarity': item.rarity,
                    'adorned': 'false'
                }
            )

            response = "Success! You've smelted a {}!".format(item.str_name)

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createoldscalp'):
            bknd_item.item_create(
                item_type=ewcfg.it_cosmetic,
                id_user=message.author.id,
                id_server=message.guild.id,
                item_props={
                    'id_cosmetic': 'scalp',
                    'cosmetic_name': "My scalp",
                    'cosmetic_desc': "A scalp.",
                    'adorned': 'false'
                }
            )
            response = "Success! You've smelted a scalp!"

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'createoldsoul'):
            bknd_item.item_create(
                id_user=message.author.id,
                id_server=message.guild.id,
                item_type=ewcfg.it_cosmetic,
                item_props={
                    'id_cosmetic': "soul",
                    'cosmetic_name': "My soul",
                    'cosmetic_desc': "The immortal soul of me. It dances with a vivacious energy inside its jar.\n If you listen to it closely you can hear it whispering numbers: me.",
                    'rarity': ewcfg.rarity_patrician,
                    'adorned': 'false',
                    'user_id': "usermodel.id_user",
                }
            )

            response = "Success! You've smelted a soul!"

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))


        # FIXME debug
        # Test item deletion
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'delete'):
            items = bknd_item.inventory(
                id_user=message.author.id,
                id_server=message.guild.id
            )

            for item in items:
                bknd_item.item_delete(
                    id_item=item.get('id_item')
                )

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, 'ok'))

        # AWOOOOO
        elif re_awoo.match(cmd):
            return await ewcmd.cmdcmds.cmd_howl(cmd_obj)
        elif re_moan.match(cmd):
            return await ewcmd.cmdcmds.cmd_moan(cmd_obj)

        # Debug command to override the role of a user
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'setrole'):

            response = ""

            if mentions_count == 0:
                response = 'Set who\'s role?'
            else:
                roles_map = ewutils.getRoleMap(message.guild.roles)
                role_target = tokens[1]
                role = roles_map.get(role_target)

                if role != None:
                    for user in mentions:
                        try:
                            await user.edit(roles=role)
                        except:
                            ewutils.logMsg('Failed to replace_roles for user {} with {}.'.format(user.display_name, role.name))

                    response = 'Done.'
                else:
                    response = 'Unrecognized role.'

            await fe_utils.send_message(client, cmd.message.channel, fe_utils.formatMessage(message.author, response))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'getrowdy'):
            response = "You get rowdy. Fuck. YES!"
            user_data = EwUser(member=message.author)
            user_data.life_state = ewcfg.life_state_enlisted
            user_data.faction = ewcfg.faction_rowdys
            user_data.time_lastenlist = time_now + ewcfg.cd_enlist
            user_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'getkiller'):
            response = "You uh... 'get' killer. Sure."
            user_data = EwUser(member=message.author)
            user_data.life_state = ewcfg.life_state_enlisted
            user_data.faction = ewcfg.faction_killers
            user_data.time_lastenlist = time_now + ewcfg.cd_enlist
            user_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'getshambler'):
            response = "You get shambler. Jesus fucking Christ, why not, sure."
            user_data = EwUser(member=message.author)
            user_data.life_state = ewcfg.life_state_shambler
            user_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        # Toggles rain on and off
        elif debug == True and cmd == (ewcfg.cmd_prefix + 'toggledownfall'):
            market_data = EwMarket(id_server=message.guild.id)

            if market_data.weather == ewcfg.weather_bicarbonaterain:
                newweather = ewcfg.weather_sunny

                market_data.weather = newweather
                response = "Bicarbonate rain turned OFF. Weather was set to {}.".format(newweather)
            else:
                market_data.weather = ewcfg.weather_bicarbonaterain
                response = "Bicarbonate rain turned ON."

            market_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'dayforward'):
            market_data = EwMarket(id_server=message.guild.id)

            market_data.day += 1
            market_data.persist()

            response = "Time has progressed 1 day forward manually."

            if ewutils.check_fursuit_active(market_data):
                response += "\nIt's a full moon!"

            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'hourforward'):
            market_data = EwMarket(id_server=message.guild.id)
            market_data.clock += 1
            response = "Time has progressed 1 hour forward manually."

            if market_data.clock >= 24 or market_data.clock < 0:
                market_data.clock = 0
                market_data.day += 1
                response += "\nMidnight has come. 1 day progressed forward."

            if ewutils.check_fursuit_active(market_data):
                response += "\nIt's a full moon!"

            market_data.persist()
            await fe_utils.send_message(client, message.channel, fe_utils.formatMessage(message.author, response))

        elif debug == True and cmd == (ewcfg.cmd_prefix + 'postleaderboard'):
            try:
                for server in client.guilds:
                    await bknd_leaderboard.post_leaderboards(client=client, server=server)
            except:
                pass


        # didn't match any of the command words.
        else:
            """ couldn't process the command. bail out!! """
            """ bot rule 0: be cute """
            randint = random.randint(1, 3)
            msg_mistake = "ENDLESS WAR is growing frustrated."
            if randint == 2:
                msg_mistake = "ENDLESS WAR denies you his favor."
            elif randint == 3:
                msg_mistake = "ENDLESS WAR pays you no mind."

            msg = await fe_utils.send_message(client, cmd_obj.message.channel, msg_mistake, 2)
            await asyncio.sleep(2)
            try:
                await msg.delete()
                pass
            except:
                pass

    elif content_tolower.find(ewcfg.cmd_howl) >= 0 or content_tolower.find(ewcfg.cmd_howl_alt1) >= 0 or re_awoo.match(content_tolower):
        """ Howl if !howl is in the message at all. """
        return await ewcmd.cmdcmds.cmd_howl(cmd_utils.EwCmd(
            message=message,
            client=client,
            guild=message.guild
        ))
    elif content_tolower.find(ewcfg.cmd_moan) >= 0 or re_moan.match(content_tolower):
        return await ewcmd.cmdcmds.cmd_moan(cmd_utils.EwCmd(
            message=message,
            client=client,
            guild=message.guild
        ))


@client.event
async def on_raw_reaction_add(payload):
    # We only respond to reactions in the slime twitter channel
    if (payload.guild_id is not None  # not a dm
            and channels_slimetwitter[payload.guild_id] is not None  # server has a slime twitter channel
            and payload.channel_id == channels_slimetwitter[payload.guild_id].id):  # reaction was in that channel

        message = await channels_slimetwitter[payload.guild_id].fetch_message(payload.message_id)

        if len(message.embeds) > 0:

            embed = message.embeds[0]
            userid = "<@!{}>".format(payload.user_id)

            # Ignore reaction if it's not from the slime tweet author
            if embed.description.startswith(userid):

                if (str(payload.emoji) == ewcfg.emote_delete_tweet):
                    await message.delete()


# find our REST API token
token = ewutils.getToken()

if token == None or len(token) == 0:
    ewutils.logMsg('Please place your API token in a file called "token", in the same directory as this script.')
    sys.exit(0)

# connect to discord and run indefinitely
try:
    client.run(token)
finally:
    ewutils.TERMINATE = True
    ewutils.logMsg("main thread terminated.")
