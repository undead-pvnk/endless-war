import asyncio
import math
import time

import discord

import ewcfg
import ewstats
import ewutils

class EwMutationFlavor:

	# The mutation's name
	id_mutation = ""

	# String used to describe the mutation when you !data yourself
	str_describe_self = ""

	# String used to describe the mutation when you !data another player
	str_describe_other = ""

	# String used when you acquire the mutation
	str_acquire = ""

	def __init__(self,
		id_mutation = "",
		str_describe_self = "",
		str_describe_other = "",
		str_acquire = ""):

		self.id_mutation = id_mutation
		self.str_describe_self = str_describe_self
		self.str_describe_other = str_describe_other
		self.str_acquire = str_acquire


class EwMutation:
	id_server = ""
	id_user = ""
	id_mutation = ""

	time_lastuse = 0

	""" Create a new EwMutation and optionally retrieve it from the database. """
	def __init__(self, id_user = None, id_server = None, id_mutation = None):
		# Retrieve the object from the database if the user is provided.
		if(id_user != None) and (id_server != None) and (id_mutation != None):
			self.id_server = id_server
			self.id_user = id_user
			self.id_mutation = id_mutation

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute("SELECT {time_lastuse} FROM mutations WHERE id_user = %s AND id_server = %s AND {id_mutation} = %s".format(
					time_lastuse = ewcfg.col_time_lastuse,
					id_mutation = ewcfg.col_id_mutation
				), (
					id_user,
					id_server,
					id_mutation
				))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.time_lastuse = result[0]
				else:
					# Create a new database entry if the object is missing.
					cursor.execute("REPLACE INTO mutations(id_user, id_server, {id_mutation}, {time_lastuse}) VALUES(%s, %s, %s, %s)".format(
						id_mutation = ewcfg.col_id_mutation,
						time_lastuse = ewcfg.col_time_lastuse
					), (
						id_user,
						id_server,
						id_mutation,
						self.time_lastuse
					))
					
					conn.commit()

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save this mutation object to the database. """
	def persist(self):
	
		try:
			# Get database handles if they weren't passed.
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();


			# Save the object.
			# Todo Preserve Farming Data 	farmActive, plantType, time_lastsow
			cursor.execute("REPLACE INTO mutations(id_user, id_server, {id_mutation}, {time_lastuse}) VALUES(%s, %s, %s, %s)".format(
					id_mutation = ewcfg.col_id_mutation,
					time_lastuse = ewcfg.col_time_lastuse
				), (
					self.id_user,
					self.id_server,
					self.id_mutation,
					self.time_lastuse
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)
