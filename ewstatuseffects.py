import time
import math
import asyncio

import ewcfg
import ewutils
import ewrolemgr

#from ew import EwUser
from ewplayer import EwPlayer

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


