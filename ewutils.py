import sys
import traceback

import MySQLdb
import datetime
import time
import re
import random
import asyncio

import ewstats
import ewitem

import discord

import ewcfg
from ew import EwUser
from ewdistrict import EwDistrict
from ewplayer import EwPlayer

db_pool = {}
db_pool_id = 0

# Map of user IDs to their course ID.
moves_active = {}

class Message:
	# Send the message to this exact channel by name.
	channel = None

	# Send the message to the channel associated with this point of interest.
	id_poi = None

	# Should this message echo to adjacent points of interest?
	reverb = None
	message = ""

	def __init__(
		self,
		channel = None,
		reverb = False,
		message = "",
		id_poi = None
	):
		self.channel = channel
		self.reverb = reverb
		self.message = message
		self.id_poi = id_poi

"""
	Class for storing, passing, editing and posting channel responses and topics
"""
class EwResponseContainer:
	client = None
	id_server = ""
	channel_responses = {}
	channel_topics = {}

	def __init__(self, client = None, id_server = None):
		self.client = client
		self.id_server = id_server
		self.channel_responses = {}
		self.channel_topics = {}

	def add_channel_response(self, channel, response):
		if channel in self.channel_responses:
			self.channel_responses[channel] += "\n" + response
		else:
			self.channel_responses[channel] = response

	def add_channel_topic(self, channel, topic):
		self.channel_topics[channel] = topic

	def add_response_container(self, resp_cont):
		for ch in resp_cont.channel_responses:
			self.add_channel_response(ch, resp_cont.channel_responses[ch])

		for ch in resp_cont.channel_topics:
			self.add_channel_topic(ch, resp_cont.channel_topics[ch])

	async def post(self):
		self.client = get_client()
		messages = []

		if self.client == None:
			logMsg("Couldn't find client")
			return messages
			
		server = self.client.get_server(self.id_server)
		if server == None:
			logMsg("Couldn't find server with id {}".format(self.id_server))
			return messages

		for ch in self.channel_responses:
			channel = get_channel(server = server, channel_name = ch)
			try:
				message = await send_message(self.client, channel, self.channel_responses[ch])
				messages.append(message)
			except:
				logMsg('Failed to send message to channel {}: {}'.format(ch, self.channel_responses[ch]))
				

		for ch in self.channel_topics:
			channel = get_channel(server = server, channel_name = ch)
			try:
				await self.client.edit_channel(channel = channel, topic = self.channel_topics[ch])
			except:
				logMsg('Failed to set channel topic for {} to {}'.format(ch, self.channel_topics[ch]))

		return messages


def readMessage(fname):
	msg = Message()

	try:
		f = open(fname, "r")
		f_lines = f.readlines()

		count = 0
		for line in f_lines:
			line = line.rstrip()
			count += 1
			if len(line) == 0:
				break

			args = line.split('=')
			if len(args) == 2:
				field = args[0].strip().lower()
				value = args[1].strip()

				if field == "channel":
					msg.channel = value.lower()
				elif field == "poi":
					msg.poi = value.lower()
				elif field == "reverb":
					msg.reverb = True if (value.lower() == "true") else False
			else:
				count -= 1
				break

		for line in f_lines[count:]:
			msg.message += (line.rstrip() + "\n")
	except:
		logMsg('failed to parse message.')
		traceback.print_exc(file = sys.stdout)
	finally:
		f.close()

	return msg

""" Write the string to stdout with a timestamp. """
def logMsg(string):
	print("[{}] {}".format(datetime.datetime.now(), string))

	return string

""" read a file named fname and return its contents as a string """
def getValueFromFileContents(fname):
	token = ""

	try:
		f_token = open(fname, "r")
		f_token_lines = f_token.readlines()

		for line in f_token_lines:
			line = line.rstrip()
			if len(line) > 0:
				token = line
	except IOError:
		token = ""
		print("Could not read {} file.".format(fname))
	finally:
		f_token.close()

	return token

""" get the Discord API token from the config file on disk """
def getToken():
	return getValueFromFileContents("token")

""" get the Twitch client ID from the config file on disk """
def getTwitchClientId():
	return getValueFromFileContents("twitch_client_id")

""" print a list of strings with nice comma-and grammar """
def formatNiceList(names = [], conjunction = "and"):
	l = len(names)

	if l == 0:
		return ''

	if l == 1:
		return names[0]
	
	return ', '.join(names[0:-1]) + '{comma} {conj} '.format(comma = (',' if l > 2 else ''), conj = conjunction) + names[-1]

""" turn a list of Users into a list of their respective names """
def userListToNameString(list_user):
	names = []

	for user in list_user:
		names.append(user.display_name)

	return formatNiceList(names)

""" turn a list of Roles into a map of name = >Role """
def getRoleMap(roles):
	roles_map = {}

	for role in roles:
		roles_map[mapRoleName(role.name)] = role

	return roles_map

""" turn a list of Roles into a map of id = >Role """
def getRoleIdMap(roles):
	roles_map = {}

	for role in roles:
		roles_map[mapRoleName(role.id)] = role

	return roles_map

""" canonical lowercase no space name for a role """
def mapRoleName(roleName):
	return roleName.replace(" ", "").lower()

""" connect to the database """
def databaseConnect():
	conn_info = None

	conn_id_todelete = []

	global db_pool
	global db_pool_id

	# Iterate through open connections and find the currently active one.
	for pool_id in db_pool:
		conn_info_iter = db_pool.get(pool_id)

		if conn_info_iter['closed'] == True:
			if conn_info_iter['count'] <= 0:
				conn_id_todelete.append(pool_id)
		else:
			conn_info = conn_info_iter

	# Close and remove dead connections.
	if len(conn_id_todelete) > 0:
		for pool_id in conn_id_todelete:
			conn_info_iter = db_pool[pool_id]
			conn_info_iter['conn'].close()

			del db_pool[pool_id]

	# Create a new connection.
	if conn_info == None:
		db_pool_id += 1
		conn_info = {
			'conn': MySQLdb.connect(host = "localhost", user = "rfck-bot", passwd = "rfck", db = "rfck", charset = "utf8"),
			'created': int(time.time()),
			'count': 1,
			'closed': False
		}
		db_pool[db_pool_id] = conn_info
	else:
		conn_info['count'] += 1

	return conn_info

""" close (maybe) the active database connection """
def databaseClose(conn_info):
	conn_info['count'] -= 1

	# Expire old database connections.
	if (conn_info['created'] + 60) < int(time.time()):
		conn_info['closed'] = True

""" format responses with the username: """
def formatMessage(user_target, message):
	return "*{}*: {}".format(user_target.display_name, message).replace("@", "\{at\}")

""" Decay slime totals for all users """
def decaySlimes(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND {slimes} > 1".format(
				slimes = ewcfg.col_slimes
			), (
				id_server,
			))

			users = cursor.fetchall()
			total_decayed = 0

			for user in users:
				user_data = EwUser(id_user = user[0], id_server = id_server)
				slimes_to_decay = user_data.slimes - (user_data.slimes * (.5 ** (ewcfg.update_market / ewcfg.slime_half_life)))

				#round up or down, randomly weighted
				remainder = slimes_to_decay - int(slimes_to_decay)
				if random.random() < remainder: 
					slimes_to_decay += 1 
				slimes_to_decay = int(slimes_to_decay)

				if slimes_to_decay >= 1:
					user_data.change_slimes(n = -slimes_to_decay, source = ewcfg.source_decay)
					user_data.persist()
					total_decayed += slimes_to_decay

			cursor.execute("SELECT district FROM districts WHERE id_server = %s AND {slimes} > 1".format(
				slimes = ewcfg.col_district_slimes
			), (
				id_server,
			))

			districts = cursor.fetchall()

			for district in districts:
				district_data = EwDistrict(district = district[0], id_server = id_server)
				slimes_to_decay = district_data.slimes - (district_data.slimes * (.5 ** (ewcfg.update_market / ewcfg.slime_half_life)))

				#round up or down, randomly weighted
				remainder = slimes_to_decay - int(slimes_to_decay)
				if random.random() < remainder: 
					slimes_to_decay += 1 
				slimes_to_decay = int(slimes_to_decay)

				if slimes_to_decay >= 1:
					district_data.change_slimes(n = -slimes_to_decay, source = ewcfg.source_decay)
					district_data.persist()
					total_decayed += slimes_to_decay

			cursor.execute("UPDATE markets SET {decayed} = ({decayed} + %s) WHERE {server} = %s".format(
				decayed = ewcfg.col_decayed_slimes,
				server = ewcfg.col_id_server
			), (
				total_decayed,
				id_server
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)	
"""
	Coroutine that continually calls bleedSlimes; is called once per server, and not just once globally
"""
async def bleed_tick_loop(id_server):
	interval = ewcfg.bleed_tick_length
	# causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
	while True:
		await bleedSlimes(id_server = id_server)
		# ewutils.logMsg("Capture tick happened on server %s." % id_server + " Timestamp: %d" % int(time.time()))

		await asyncio.sleep(interval)

""" Bleed slime for all users """
async def bleedSlimes(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT id_user FROM users WHERE id_server = %s AND {bleed_storage} > 1".format(
				bleed_storage = ewcfg.col_bleed_storage
			), (
				id_server,
			))

			users = cursor.fetchall()
			total_bled = 0
			deathreport = ""
			resp_cont = EwResponseContainer(id_server = id_server)
			for user in users:
				user_data = EwUser(id_user = user[0], id_server = id_server)
				slimes_to_bleed = user_data.bleed_storage * (1 - .5 ** (ewcfg.bleed_tick_length / ewcfg.bleed_half_life))
				slimes_to_bleed = max(slimes_to_bleed, ewcfg.bleed_tick_length * 1000)
				slimes_to_bleed = min(slimes_to_bleed, user_data.bleed_storage)
				slimes_dropped = user_data.totaldamage + user_data.slimes

				district_data = EwDistrict(id_server = id_server, district = user_data.poi)

				#round up or down, randomly weighted
				remainder = slimes_to_bleed - int(slimes_to_bleed)
				if random.random() < remainder: 
					slimes_to_bleed += 1 
				slimes_to_bleed = int(slimes_to_bleed)

				if slimes_to_bleed >= 1:
					user_data.bleed_storage -= slimes_to_bleed
					user_data.change_slimes(n = - slimes_to_bleed, source = ewcfg.source_bleeding)
					if user_data.slimes < 0:
						user_data.die(cause = ewcfg.cause_bleeding)
						user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
						player_data = EwPlayer(id_server = user_data.id_server, id_user = user_data.id_user)
						deathreport = "{skull} *{uname}*: You have succumbed to your wounds. {skull}".format(skull = ewcfg.emote_slimeskull, uname = player_data.display_name)
						resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)
					user_data.persist()

					district_data.change_slimes(n = slimes_to_bleed, source = ewcfg.source_bleeding)
					district_data.persist()
					total_bled += slimes_to_bleed

			await resp_cont.post()



			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)		

""" Increase hunger for every player in the server. """
def pushupServerHunger(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save data
			cursor.execute("UPDATE users SET {hunger} = {hunger} + {tick} WHERE life_state > 0 AND id_server = %s AND hunger < {limit}".format(
				hunger = ewcfg.col_hunger,
				tick = ewcfg.hunger_pertick,
				# this function returns the bigger of two values; there is no simple way to do this in sql and we can't calculate it within this python script
				limit = "0.5 * (({val1} + {val2}) + ABS({val1} - {val2}))".format(
					val1 = ewcfg.min_stamina,
					val2 = "POWER(" + ewcfg.col_slimelevel + ", 2)"
				)
			), (
				id_server,
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

""" Reduce inebriation for every player in the server. """
def pushdownServerInebriation(id_server = None):
	if id_server != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save data
			cursor.execute("UPDATE users SET {inebriation} = {inebriation} - {tick} WHERE id_server = %s AND {inebriation} > {limit}".format(
				inebriation = ewcfg.col_inebriation,
				tick = ewcfg.inebriation_pertick,
				limit = 0
			), (
				id_server,
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

""" Parse a list of tokens and return an integer value. If allow_all, return -1 if the word 'all' is present. """
def getIntToken(tokens = [], allow_all = False, negate = False):
	value = None

	for token in tokens[1:]:
		try:
			value = int(token.replace(",", ""))
			if value < 0 and not negate:
				value = None
			elif value > 0 and negate:
				value = None
			elif negate:
				value = -value
			break
		except:
			if allow_all and ("{}".format(token)).lower() == 'all':
				return -1
			else:
				value = None

	return value

""" Get the map of weapon skills for the specified player. """
def weaponskills_get(id_server = None, id_user = None, member = None):
	weaponskills = {}

	if member != None:
		id_server = member.server.id
		id_user = member.id

	if id_server != None and id_user != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("SELECT {weapon}, {weaponskill} FROM weaponskills WHERE {id_server} = %s AND {id_user} = %s".format(
				weapon = ewcfg.col_weapon,
				weaponskill = ewcfg.col_weaponskill,
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user
			), (
				id_server,
				id_user
			))

			data = cursor.fetchall()
			if data != None:
				for row in data:
					weaponskills[row[0]] = {
						'skill': row[1]
					}
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

	return weaponskills

""" Set an individual weapon skill value for a player. """
def weaponskills_set(id_server = None, id_user = None, member = None, weapon = None, weaponskill = 0):
	if member != None:
		id_server = member.server.id
		id_user = member.id

	if id_server != None and id_user != None and weapon != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			cursor.execute("REPLACE INTO weaponskills({id_server}, {id_user}, {weapon}, {weaponskill}) VALUES(%s, %s, %s, %s)".format(
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user,
				weapon = ewcfg.col_weapon,
				weaponskill = ewcfg.col_weaponskill
			), (
				id_server,
				id_user,
				weapon,
				weaponskill
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)

""" Clear all weapon skills for a player (probably called on death). """
def weaponskills_clear(id_server = None, id_user = None, member = None):
	if member != None:
		id_server = member.server.id
		id_user = member.id

	if id_server != None and id_user != None:
		try:
			conn_info = databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Clear any records that might exist.
			cursor.execute("UPDATE weaponskills SET {weaponskill} = %s WHERE {weaponskill} > %s AND {id_server} = %s AND {id_user} = %s".format(
				weaponskill = ewcfg.col_weaponskill,
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user
			), (
				ewcfg.weaponskill_max_onrevive,
				ewcfg.weaponskill_max_onrevive,
				id_server,
				id_user
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			databaseClose(conn_info)


re_flattener = re.compile("[ '\"!@#$%^&*().,/?{}\[\];:]")

"""
	Turn an array of tokens into a single word (no spaces or punctuation) with all lowercase letters.
"""
def flattenTokenListToString(tokens):
	global re_flattener
	target_name = ""

	if type(tokens) == list:
		for token in tokens:
			if token.startswith('<@') == False:
				target_name += re_flattener.sub("", token.lower())
	elif tokens.startswith('<@') == False:
		target_name = re_flattener.sub("", tokens.lower())

	return target_name


"""
	Execute a given sql_query. (the purpose of this function is to minimize repeated code and keep functions readable)
"""
def execute_sql_query(sql_query = None, sql_replacements = None):
	data = None

	try:
		conn_info = databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()
		cursor.execute(sql_query, sql_replacements)
		if sql_query.lower().startswith("select"):
			data = cursor.fetchall()
		conn.commit()
	finally:
		# Clean up the database handles.
		cursor.close()
		databaseClose(conn_info)

	return data


"""
	Send a message to multiple chat channels at once. "channels" can be either a list of discord channel objects or strings
"""
async def post_in_channels(id_server, message, channels = None):
	client = get_client()
	server = client.get_server(id = id_server)

	if channels is None and server is not None:
		channels = server.channels

	for channel in channels:
		if type(channel) is str:  # if the channels are passed as strings instead of discord channel objects
			channel = get_channel(server, channel)
		if channel is not None and channel.type == discord.ChannelType.text:
			await send_message(client, channel, message)
	return

"""
	Find a chat channel by name in a server.
"""
def get_channel(server = None, channel_name = ""):
	channel = None

	for chan in server.channels:
		if chan.name == channel_name:
			channel = chan

	return channel

"""
	Return the role name of a user's faction. Takes user data object or life_state and faction tag
"""
def get_faction(user_data = None, life_state = 0, faction = ""):
	life_state = life_state
	faction = faction
	if user_data != None:
		life_state = user_data.life_state
		faction = user_data.faction

	faction_role = ewcfg.role_corpse

	if life_state == ewcfg.life_state_juvenile:
		faction_role = ewcfg.role_juvenile

	elif life_state == ewcfg.life_state_enlisted:
		if faction == ewcfg.faction_killers:
			faction_role = ewcfg.role_copkillers

		elif faction == ewcfg.faction_rowdys:
			faction_role = ewcfg.role_rowdyfuckers

		else:
			faction_role = ewcfg.role_juvenile

	elif life_state == ewcfg.life_state_kingpin:
		faction_role = ewcfg.role_kingpin

	elif life_state == ewcfg.life_state_grandfoe:
		faction_role = ewcfg.role_grandfoe

	return faction_role

def get_faction_symbol(faction = "", faction_raw = ""):
	result = None

	if faction == ewcfg.role_kingpin:
		if faction_raw == ewcfg.faction_rowdys:
			result = ewcfg.emote_rowdyfucker
		elif faction_raw == ewcfg.faction_killers:
			result = ewcfg.emote_copkiller

	if result == None:
		if faction == ewcfg.role_corpse:
			result = ewcfg.emote_ghost
		elif faction == ewcfg.role_juvenile:
			result = ewcfg.emote_slime3
		elif faction == ewcfg.role_copkillers:
			result = ewcfg.emote_ck
		elif faction == ewcfg.role_rowdyfuckers:
			result = ewcfg.emote_rf
		else:
			result = ewcfg.emote_blank

	return result


"""
	Calculate the slime amount needed to reach a certain level
"""
def slime_bylevel(slimelevel):
	return int(slimelevel ** 4)


"""
	Calculate what level the player should be at, given their slime amount
"""
def level_byslime(slime):
	return int(abs(slime) ** 0.25)


"""
	Calculate the maximum hunger level at the player's slimelevel
"""
def hunger_max_bylevel(slimelevel):
	# note that when you change this formula, you'll also have to adjust its sql equivalent in pushupServerHunger
	return max(ewcfg.min_stamina, slimelevel ** 2)


"""
	Calculate how much more stamina activities should cost
"""
def hunger_cost_mod(slimelevel):
	return hunger_max_bylevel(slimelevel) / 200


"""
	Returns an EwUser object of the selected kingpin
"""
def find_kingpin(id_server, kingpin_role):
	data = execute_sql_query("SELECT id_user FROM users WHERE id_server = %s AND {life_state} = %s AND {faction} = %s".format(
		life_state = ewcfg.col_life_state,
		faction = ewcfg.col_faction
	), (
		id_server,
		ewcfg.life_state_kingpin,
		ewcfg.faction_rowdys if kingpin_role == ewcfg.role_rowdyfucker else ewcfg.faction_killers
	))

	kingpin = None

	if len(data) > 0:
		id_kingpin = data[0][0]
		kingpin = EwUser(id_server = id_server, id_user = id_kingpin)

	return kingpin


"""
	Posts a message both in CK and RR.
"""
async def post_in_hideouts(id_server, message):
	await post_in_channels(
		id_server = id_server,
		message = message,
		channels = [ewcfg.channel_copkilltown, ewcfg.channel_rowdyroughhouse]
	)

"""
	gets the discord client the bot is running on
"""
def get_client():
	return ewcfg.get_client()


"""
	Proxy to discord.py Client.send_message with exception handling.
"""
async def send_message(client, channel, text):
	try:
		return await client.send_message(channel, text)
	except:
		logMsg('Failed to send message to channel: {}\n{}'.format(channel, text))

"""
	Proxy to discord.py Client.edit_message with exception handling.
"""
async def edit_message(client, message, text):
	try:
		return await client.edit_message(message, text)
	except:
		logMsg('Failed to edit message. Updated text would have been:\n{}'.format(text))

"""
	Returns a list of slimeoid ids in the district
"""
def get_slimeoids_in_poi(id_server = None, poi = None, sltype = None):
	slimeoids = []
	if id_server is None:
		return slimeoids

	query = "SELECT {id_slimeoid} FROM slimeoids WHERE {id_server} = %s".format(
		id_slimeoid = ewcfg.col_id_slimeoid,
		id_server = ewcfg.col_id_server
	)

	if sltype is not None:
		query += " AND {} = '{}'".format(ewcfg.col_type, sltype)

	if poi is not None:
		query += " AND {} = '{}'".format(ewcfg.col_poi, poi)

	data = execute_sql_query(query,(
		id_server,
	))

	for row in data:
		slimeoids.append(row[0])

	return slimeoids
