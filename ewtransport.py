import asyncio
import time

import ewutils
import ewcfg

class EwTransport:
	id_server = ""
	poi = ""

	transport_type = ""
	current_line = ""
	current_stop = ""

	def __init__(self, id_server = None, poi = None):
		if id_server is not None and poi is not None:
			self.id_server = id_server
			self.poi = poi
			try:
				data = ewutils.execute_sql_query("SELECT {transport_type}, {current_line}, {current_stop} FROM transports WHERE {id_server} = %s AND {poi} = %s".format(
						transport_type = ewcfg.col_transport_type,
						current_line = ewcfg.col_current_line,
						current_stop = ewcfg.col_current_stop,
						id_server = ewcfg.col_id_server,
						poi = ewcfg.col_poi
					),(
						self.id_server,
						self.poi
					))
				if len(data) > 0:
					self.transport_type = data[0][0]
					self.current_line = data[0][1]
					self.current_stop = data[0][2]
				else:
					poi_data = ewutils.id_to_poi.get(self.poi)
					if poi_data is not None:
						self.transport_type = poi_data.transport_type
						self.current_line = poi_data.default_line
						self.current_stop = poi_data.default_stop

						self.persist()
			except:
				ewutils.logMsg("Failed to retrieve transport {} from database.".format(self.poi))
							
	def persist(self):

		try:
			ewutils.execute_sql_query("REPLACE INTO transports ({id_server}, {poi}, {transport_type}, {current_line}, {current_stop}) VALUES (%s, %s, %s, %s, %s)".format(	
					id_server = ewcfg.col_id_server,
					poi = ewcfg.col_poi,
					transport_type = ewcfg.col_transport_type,
					current_line = ewcfg.col_current_line,
					current_stop = ewcfg.col_current_stop
				),(
					self.id_server,
					self.poi,
					self.transport_type,
					self.current_line,
					self.current_stop
				))
		except:
			ewutils.logMsg("Failed to write transport {} to database.".format(self.poi))

	async def move_loop(self):
		while True:
			try:
				transport_line = ewcfg.id_to_transport_line(self.current_line)

				if self.current_stop == transport_line.last_stop:
					self.current_line = transport_line.next_line
				else:
					schedule = transport_line.schedule.get(self.current_stop)
					await asyncio.sleep(schedule[0])
					self.current_stop = schedule[1]

				self.persist()

			except:
				ewutils.logMsg("An error occured while moving transport {}.".format(self.poi))
				break

class EwTransportLine:

	# name of the transport line
	id_line = ""

	# which stop the line starts at
	first_stop = ""

	# which stop the line ends at
	last_stop = ""

	# which line transports switch to after the last stop
	next_line = ""

	# how long to stay at each stop, and which stop follows
	schedule = {}

	def __init__(self,
		id_line = "",
		first_stop = "",
		last_stop = "",
		next_line = "",
		schedule = {}
		):
		self.id_line = id_line
		self.first_stop = first_stop
		self.last_stop = last_stop
		self.next_line = next_line
		self.schedule = schedule


		
