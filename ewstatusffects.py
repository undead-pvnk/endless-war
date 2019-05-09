import time
import math

import ewcfg
import ewutils
from ew import EwUser

class EwStatusEffectDef:
	id_status = ""
	time_expire = -1
    
	str_acquire = ""
	str_describe = ""
	str_describe_self = ""
	type = ""
	value = ""

	def __init__(
        self,
        id_status = "",
        time_expire = -1,
        str_acquire = "",
        str_describe = "",
        str_describe_self = "",
		type = "",
		value = ""
    ):
		self.id_status = id_status
		self.time_expire = time_expire
		self.str_acquire = str_acquire
		self.str_describe = str_describe
		self.str_describe_self = str_describe_self
		self.type = type
		self.value = value

class EwStatusEffect:
	id_server = ""
	id_user = ""
	id_status = ""
	time_expire = -1

	def __init__(
		self,
		status = None,
        id_server = None,
        id_user = None
	):
		if status != None and id_server != None and id_user != None:
			self.id_server = id_server
			self.id_user = id_user
			self.id_status = status.id_status
			self.time_expire = status.time_expire

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute("SELECT {time_expire} FROM status_effects WHERE {id_status} = %s and {id_server} = %s and {id_user} = %s".format(
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
					cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}) VALUES(%s, %s, %s, %s)".format(
						ewcfg.col_id_server,
						ewcfg.col_id_user,
						ewcfg.col_id_status,
						ewcfg.col_time_expir
					), (
						self.id_server,
						self.id_user,
						self.id_status,
						(self.time_expire + int(time.time())) if self.time_expire > 0 else self.time_expire
					))

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
			cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}) VALUES(%s, %s, %s, %s)".format(
				ewcfg.col_id_server,
				ewcfg.col_id_user,
				ewcfg.col_id_status,
				ewcfg.col_time_expir
			), (
				self.id_server,
				self.id_user,
                self.id_status,
				self.time_expire
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)