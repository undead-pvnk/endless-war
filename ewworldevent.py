import asyncio
import time

import ewcfg
import ewutils

class EwEventDef:
	event_type = ""
	
	str_event_start = ""
	str_event_end = ""

	def __init__(
		self,
		event_type = "",
		str_event_start = "",
		str_event_end = "",
	):
		self.event_type = event_type
		self.str_event_start = str_event_start
		self.str_event_end = str_event_end
		

class EwWorldEvent:
	id_event = -1
	id_server = ""
	event_type = ""
	time_activate = -1
	time_expir = -1

	event_props = None

	def __init__(
		self,
		id_event = None
	):
		if(id_event != None):
			self.id_event = id_event

			self.event_props = {}

			try:
				# Retrieve object
				result = ewutils.execute_sql_query("SELECT {}, {}, {}, {} FROM world_events WHERE id_event = %s".format(
					ewcfg.col_id_server,
					ewcfg.col_event_type,
					ewcfg.col_time_activate,
					ewcfg.col_time_expir,
				), (
					self.id_event,
				))

				if len(result) > 0:
					result = result[0]

					# Record found: apply the data to this object.
					self.id_server = result[0]
					self.event_type = result[1]
					self.time_activate = result[2]
					self.time_expir = result[3]

					# Retrieve additional properties
					props = ewutils.execute_sql_query("SELECT {}, {} FROM world_events_prop WHERE id_event = %s".format(
						ewcfg.col_name,
						ewcfg.col_value
					), (
						self.id_event,
					))

					for row in props:
						# this try catch is only necessary as long as extraneous props exist in the table
						try:
							self.event_props[row[0]] = row[1]
						except:
							ewutils.logMsg("extraneous event_prop row detected.")

				else:
					# Item not found.
					self.id_event = -1
			except:
				ewutils.logMsg("Error while retrieving world event {}".format(id_event))


	""" Save event data object to the database. """
	def persist(self):
		try:
			# Save the object.
			ewutils.execute_sql_query("REPLACE INTO world_events({}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s)".format(
				ewcfg.col_id_event,
				ewcfg.col_id_server,
				ewcfg.col_event_type,
				ewcfg.col_time_activate,
				ewcfg.col_time_expir,
			), (
				self.id_event,
				self.id_server,
				self.event_type,
				self.time_activate,
				self.time_expir,
			))

			# Remove all existing property rows.
			ewutils.execute_sql_query("DELETE FROM world_events_prop WHERE {} = %s".format(
				ewcfg.col_id_event
			), (
				self.id_event,
			))

			# Write out all current property rows.
			for name in self.event_props:
				ewutils.execute_sql_query("INSERT INTO world_events_prop({}, {}, {}) VALUES(%s, %s, %s)".format(
					ewcfg.col_id_event,
					ewcfg.col_name,
					ewcfg.col_value
				), (
					self.id_event,
					name,
					self.event_props[name]
				))
		except:
			ewutils.logMsg("Error while persisting world event {}".format(self.id_event))


def get_world_events(id_server = None, active_only = True):
	world_events = {}
	if id_server == None:
		return world_events

	time_now = int(time.time())
	query = "SELECT {col_id_event}, {col_event_type} FROM world_events WHERE id_server = %s"

	if active_only:
		query_suffix = " AND {col_time_activate} <= {time_now} AND ({col_time_expir} >= {time_now} OR {col_time_expir} < 0)"
		query += query_suffix

	data = ewutils.execute_sql_query(query.format(
		col_id_event = ewcfg.col_id_event,
		col_event_type = ewcfg.col_event_type,
		col_time_activate = ewcfg.col_time_activate,
		col_time_expir = ewcfg.col_time_expir,
		time_now = time_now,
	),(
		id_server,
	))

	for row in data:
		world_events[row[0]] = row[1]

	return world_events

def create_world_event(
	id_server = None,
	event_type = None,
	time_activate = -1,
	time_expir = -1,
	event_props = {}
):
	if id_server == None or event_type == None:
		return -1
	try:
		# Get database handles if they weren't passed.
		conn_info = ewutils.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		# Create the item in the database.

		cursor.execute("INSERT INTO world_events({}, {}, {}, {}) VALUES(%s, %s, %s, %s)".format(
			ewcfg.col_event_type,
			ewcfg.col_id_server,
			ewcfg.col_time_activate,
			ewcfg.col_time_expir,
		), (
			event_type,
			id_server,
			time_activate,
			time_expir
		))

		event_id = cursor.lastrowid
		conn.commit()

		if event_id > 0:
			# If additional properties are specified in the item definition or in this create call, create and persist them.
			event_inst = EwWorldEvent(id_event = event_id)

			event_inst.event_props.update(event_props)

			event_inst.persist()

			conn.commit()
	finally:
		# Clean up the database handles.
		cursor.close()
		ewutils.databaseClose(conn_info)


	return event_id

def delete_world_event(id_event):
	try:
		ewutils.execute_sql_query("DELETE FROM world_events WHERE {id_event} = %".format(
			id_event = ewcfg.col_id_event,
		),(
			id_event,
		))
	except:
		ewutils.logMsg("Error while deleting world event {}".format(id_event))
