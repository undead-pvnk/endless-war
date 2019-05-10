import time
import math
import asyncio

import ewcfg
import ewutils
import ewrolemgr
from ew import EwUser
from ewplayer import EwPlayer
from ewutils import EwResponseContainer


class EwStatusEffectDef:
	id_status = ""
	# Time until expiration, negative values have non time based expire conditions
	time_expire = -1
    
	str_acquire = ""
	str_describe = ""
	str_describe_self = ""
	# Values have to be in the same position as types 
	# ie: if there's a 20% aim bonus and 30% damage bonus you would put 
	# types = ["aim", "dmg"]
	# values = [0.2, 0.3]
	types = []
	values = []
	# Target for statuses used in damage calculation
	target = ""

	def __init__(
        self,
        id_status = "",
        time_expire = -1,
        str_acquire = "",
        str_describe = "",
        str_describe_self = "",
		types = [],
		values = [],
		target = ""
    ):
		self.id_status = id_status
		self.time_expire = time_expire
		self.str_acquire = str_acquire
		self.str_describe = str_describe
		self.str_describe_self = str_describe_self
		self.types = types
		self.values = values
		self.target = target

class EwStatusEffect:
	id_server = ""
	id_user = ""
	id_status = ""
	time_expire = -1

	def __init__(
		self,
		status = None,
        user_data = None,
		value = 0
	):
		if status != None and user_data != None:
			self.id_server = user_data.id_server
			self.id_user = user_data.id_user
			self.id_status = status.id_status
			self.time_expire = status.time_expire
			self.value = value
			time_now = int(time.time())

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute("SELECT {time_expire}, value FROM status_effects WHERE {id_status} = %s and {id_server} = %s and {id_user} = %s".format(
                    time_expire = ewcfg.col_time_expir,
                    id_status = ewcfg.col_id_status,
                    id_server = ewcfg.col_id_server,
                    id_user = ewcfg.col_id_user
				), (
					self.id_status,
                    self.id_server,
                    self.id_user
				))
				result = cursor.fetchone()

				if result != None:
					self.time_expire = result[0]

				else:
					# Save the object.
					cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s)".format(
						ewcfg.col_id_server,
						ewcfg.col_id_user,
						ewcfg.col_id_status,
						ewcfg.col_time_expir,
						ewcfg.col_value
					), (
						self.id_server,
						self.id_user,
						self.id_status,
						(self.time_expire + time_now) if self.time_expire > 0 else self.time_expire,
						self.value
					))

					self.time_expire = (self.time_expire + time_now) if self.time_expire > 0 else self.time_expire

					conn.commit()

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save item data object to the database. """
	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s)".format(
				ewcfg.col_id_server,
				ewcfg.col_id_user,
				ewcfg.col_id_status,
				ewcfg.col_time_expir,
				ewcfg.col_value
			), (
				self.id_server,
				self.id_user,
                self.id_status,
				self.time_expire,
				self.value
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

def applyStatus(user_data = None, id_status = None, value = 0):
	response = ""
	if user_data != None and id_status != None:
		status = None

		status = ewcfg.status_effects_map.get(id_status)

		if status != None:
			statuses = user_data.getStatusEffects()

			status_effect = EwStatusEffect(status=status, user_data=user_data, value = value)

			if statuses != None:
				if id_status in statuses.keys():
					status_effect.value = value

					if status.time_expire > 0 and id_status != ewcfg.status_ghostbust_id:
						status_effect.time_expire += status.time_expire
						response = status.str_acquire

					status_effect.persist() 
				else:
					response = status.str_acquire
			else:
				response = status.str_acquire

	return response


"""
	Coroutine that continually calls burnEffect; is called once per server, and not just once globally
"""
async def burn_tick_loop(id_server):
	interval = 1#ewcfg.burn_tick_length
	# causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
	while True:
		await burnSlimes(id_server = id_server)
		# ewutils.logMsg("Capture tick happened on server %s." % id_server + " Timestamp: %d" % int(time.time()))

		await asyncio.sleep(interval)

""" Burn slime for all users """
async def burnSlimes(id_server = None):
	if id_server != None:
		time_now = int(time.time())
		client = ewutils.get_client()
		server = client.get_server(id_server)

		results = {}

		data = ewutils.execute_sql_query("SELECT {id_user}, {time_expire}, {value} from status_effects WHERE {id_status} = %s and {id_server} = %s".format(
			id_user = ewcfg.col_id_user,
			time_expire = ewcfg.col_time_expir,
			value = ewcfg.col_value,
			id_status = ewcfg.col_id_status,
			id_server = ewcfg.col_id_server
		), (
			ewcfg.status_burning_id,
			id_server
		))


		deathreport = ""
		resp_cont = EwResponseContainer(id_server = id_server)
		for result in data:
			user_data = EwUser(id_user = result[0], id_server = id_server)
			if result[1] >= time_now:
				slimes_dropped = user_data.totaldamage + user_data.slimes

				slime_to_burn = math.ceil(int(result[2]) * 0.1)

				user_data.change_slimes(n = -slime_to_burn, source=ewcfg.source_damage)

				if user_data.slimes < 0:
					member = server.get_member(user_data.id_user)

					user_data.die(cause = ewcfg.cause_burning)
					user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
					player_data = EwPlayer(id_server = user_data.id_server, id_user = user_data.id_user)
					deathreport = "{skull} *{uname}*: You have succumbed to your burns. {skull}".format(skull = ewcfg.emote_slimeskull, uname = player_data.display_name)
					resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)

					user_data.trauma = 'molotov'
					await ewrolemgr.updateRoles(client = client, member = member)
				user_data.persist()

			else:
				user_data.clear_status(id_status = ewcfg.status_burning_id)

		await resp_cont.post()	