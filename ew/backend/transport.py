import asyncio

from ..utils import core as ewutils
from ..static import cfg as ewcfg
from ..static import poi as poi_static
from . import core as bknd_core

from .district import EwDistrict

from ..utils.frontend import EwResponseContainer

"""
	Database Object for public transportation vehicles, such as ferries or subway trains
"""
class EwTransport:
	# server id
	id_server = -1

	# id of the EwPoi object for this transport
	poi = ""

	# string describing the kind of vehicle it is
	transport_type = ""

	# which line the vehicle follows. see EwTransportLine object
	current_line = ""

	# connection to the world map
	current_stop = ""

	""" Retrieve object from database, or initialize it, if it doesn't exist yet """
	def __init__(self, id_server = None, poi = None):
		if id_server is not None and poi is not None:
			self.id_server = id_server
			self.poi = poi
			try:
				data = bknd_core.execute_sql_query("SELECT {transport_type}, {current_line}, {current_stop} FROM transports WHERE {id_server} = %s AND {poi} = %s".format(
						transport_type = ewcfg.col_transport_type,
						current_line = ewcfg.col_current_line,
						current_stop = ewcfg.col_current_stop,
						id_server = ewcfg.col_id_server,
						poi = ewcfg.col_poi
					),(
						self.id_server,
						self.poi
					))
				# Retrieve data if the object was found
				if len(data) > 0:
					self.transport_type = data[0][0]
					self.current_line = data[0][1]
					self.current_stop = data[0][2]
				# initialize it per the Poi default otherwise
				else:
					poi_data = poi_static.id_to_poi.get(self.poi)
					if poi_data is not None:
						self.transport_type = poi_data.transport_type
						self.current_line = poi_data.default_line
						self.current_stop = poi_data.default_stop

						self.persist()
			except:
				ewutils.logMsg("Failed to retrieve transport {} from database.".format(self.poi))

	""" Write object to database """
	def persist(self):

		try:
			bknd_core.execute_sql_query("REPLACE INTO transports ({id_server}, {poi}, {transport_type}, {current_line}, {current_stop}) VALUES (%s, %s, %s, %s, %s)".format(
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

	""" Makes the object move across the world map. Called once at client startup for every object """
	async def move_loop(self):
		response = ""
		poi_data = poi_static.id_to_poi.get(self.poi)
		last_messages = []
		# Loop till bot stops
		while not ewutils.TERMINATE:

			district_data = EwDistrict(district = self.poi, id_server = self.id_server)

			# Don't move trains if they're degraded
			if district_data.is_degraded():
				return

			# Grab EwTransportLine object for current line
			transport_line = poi_static.id_to_transport_line[self.current_line]
			client = ewutils.get_client()
			resp_cont = EwResponseContainer(client = client, id_server = self.id_server)

			# If the train is at its last stop, switch to the opposite direction
			if self.current_stop == transport_line.last_stop:
				# wait for other train to clear the line
				if self.transport_type == ewcfg.transport_type_subway:
					# find the other train
					twin_poi = self.poi
					if self.poi[-1] == '1':
						twin_poi = twin_poi[:-1] + '2'
					else:
						twin_poi = twin_poi[:-1] + '1'
					twin_train = EwTransport(id_server=self.id_server, poi=twin_poi)

					delay_track = 0
					# check every second
					while(twin_train.current_line == transport_line.next_line):
						twin_train = EwTransport(id_server=self.id_server, poi=twin_poi)
						if twin_train.current_stop == poi_static.id_to_transport_line[twin_train.current_line].last_stop:
							break
						delay_track += 1
						await asyncio.sleep(1)
					if delay_track != 0 and ewutils.DEBUG:
						ewutils.logMsg(self.poi + " waited " + str(delay_track) + " seconds for " + twin_poi)

				self.current_line = transport_line.next_line
				self.persist()
			# If the train is mid-route
			else:
				schedule = transport_line.schedule[self.current_stop]
				# Wait for scheduled time
				await asyncio.sleep(schedule[0])
				# Delete last arrival message
				for message in last_messages:
					try:
						await message.delete()
						pass
					except:
						ewutils.logMsg("Failed to delete message while moving transport {}.".format(transport_line.str_name))
				# Switch to the next stop
				self.current_stop = schedule[1]
				self.persist()

				# Grab EwPoi of station
				stop_data = poi_static.id_to_poi.get(self.current_stop)

				# announce new stop inside the transport
				# if stop_data.is_subzone:
				# 	stop_mother = poi_static.id_to_poi.get(stop_data.mother_district)
				# 	response = "We have reached {}.".format(stop_mother.str_name)
				# else:
				response = "We have reached {}.".format(stop_data.str_name)

				# Initialize next_line in this scope
				next_line = transport_line

				# Allow for some stops to be blocked
				if stop_data.is_transport_stop:
					response += " You may exit now."

				# If it's at the end, announce new route
				if stop_data.id_poi == transport_line.last_stop:
					next_line = poi_static.id_to_transport_line[transport_line.next_line]
					response += " This {} will proceed on {}.".format(self.transport_type, next_line.str_name.replace("The", "the"))
				else:
					# Otherwise announce next stop, if usable
					next_stop = poi_static.id_to_poi.get(transport_line.schedule.get(stop_data.id_poi)[1])
					if next_stop.is_transport_stop:
						# if next_stop.is_subzone:
						# 	stop_mother = poi_static.id_to_poi.get(next_stop.mother_district)
						# 	response += " The next stop is {}.".format(stop_mother.str_name)
						# else:
						response += " The next stop is {}.".format(next_stop.str_name)
				resp_cont.add_channel_response(poi_data.channel, response)

				# announce transport has arrived at the stop
				if stop_data.is_transport_stop:
					response = "{} has arrived. You may board now.".format(next_line.str_name)
					resp_cont.add_channel_response(stop_data.channel, response)
				elif self.transport_type == ewcfg.transport_type_ferry:
					response = "{} sails by.".format(next_line.str_name)
					resp_cont.add_channel_response(stop_data.channel, response)
				elif self.transport_type == ewcfg.transport_type_blimp:
					response = "{} flies overhead.".format(next_line.str_name)
					resp_cont.add_channel_response(stop_data.channel, response)


				last_messages = await resp_cont.post()



