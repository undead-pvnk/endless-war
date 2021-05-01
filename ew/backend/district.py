import math
import time

import discord

from . import core as bknd_core
from ..static import cfg as ewcfg
from ..static import poi as poi_static
from .. import utils as ewutils

"""
	district data model for database persistence
"""
class EwDistrict:
	id_server = -1

	# The district's identifying string
	name = ""

	# The faction currently controlling this district
	controlling_faction = ""

	# The faction currently capturing this district
	capturing_faction = ""

	# The amount of progress made on the capture
	capture_points = 0

	# The property class of the district
	property_class = ""

	# The amount of CP it takes for the district to be captured
	max_capture_points = 0

	# The amount of slime in the district
	slimes = 0

	# Time until the district unlocks for capture again
	time_unlock = 0


	#Amount of influence in a district

	cap_side = ""

	# determines if the zone is functional
	degradation = 0
	
	# a timestamp for when a shambler can next plant a tombstone
	horde_cooldown = 0
	
	# the amount of gaiaslime the garden gankers have at their disposal
	gaiaslime = 0

	def __init__(self, id_server = None, district = None):
		if id_server is not None and district is not None:
			self.id_server = id_server
			self.name = district

			# find the district's property class
			for poi in poi_static.poi_list:
				if poi.id_poi == self.name:
					self.property_class = poi.property_class.lower()

			if len(self.property_class) > 0:
				self.max_capture_points = ewcfg.limit_influence[self.property_class]
			else:
				self.max_capture_points = 0


			data = bknd_core.execute_sql_query("SELECT {controlling_faction}, {capturing_faction}, {capture_points},{slimes}, {time_unlock}, {cap_side}, {degradation}, {horde_cooldown}, {gaiaslime} FROM districts WHERE id_server = %s AND {district} = %s".format(

				controlling_faction = ewcfg.col_controlling_faction,
				capturing_faction = ewcfg.col_capturing_faction,
				capture_points = ewcfg.col_capture_points,
				district = ewcfg.col_district,
				slimes = ewcfg.col_district_slimes,
				time_unlock = ewcfg.col_time_unlock,
				cap_side = ewcfg.col_cap_side,
				degradation = ewcfg.col_degradation,
				horde_cooldown = ewcfg.col_horde_cooldown,
				gaiaslime = ewcfg.col_gaiaslime,
			), (
				id_server,
				district
			))

			if len(data) > 0:  # if data is not empty, i.e. it found an entry
				# data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
				self.controlling_faction = data[0][0]
				self.capturing_faction = data[0][1]
				self.capture_points = data[0][2]
				self.slimes = data[0][3]
				self.time_unlock = data[0][4]
				self.cap_side = data[0][5]
				self.degradation = data[0][6]
				self.horde_cooldown = data[0][7]
				self.gaiaslime = data[0][8]

				# ewutils.logMsg("EwDistrict object '" + self.name + "' created.  Controlling faction: " + self.controlling_faction + "; Capture progress: %d" % self.capture_points)
			else:  # create new entry
				bknd_core.execute_sql_query("REPLACE INTO districts ({id_server}, {district}) VALUES (%s, %s)".format(
					id_server = ewcfg.col_id_server,
					district = ewcfg.col_district
				), (
					id_server,
					district
				))

	def persist(self):
		bknd_core.execute_sql_query("REPLACE INTO districts(id_server, {district}, {controlling_faction}, {capturing_faction}, {capture_points}, {slimes}, {time_unlock}, {cap_side}, {degradation}, {horde_cooldown}, {gaiaslime}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
			district = ewcfg.col_district,
			controlling_faction = ewcfg.col_controlling_faction,
			capturing_faction = ewcfg.col_capturing_faction,
			capture_points = ewcfg.col_capture_points,
			slimes = ewcfg.col_district_slimes,
			time_unlock = ewcfg.col_time_unlock,
			cap_side = ewcfg.col_cap_side,
			degradation = ewcfg.col_degradation,
			horde_cooldown = ewcfg.col_horde_cooldown,
			gaiaslime = ewcfg.col_gaiaslime,
		), (
			self.id_server,
			self.name,
			self.controlling_faction,
			self.capturing_faction,
			self.capture_points,
			self.slimes,
			self.time_unlock,
			self.cap_side,
			self.degradation,
			self.horde_cooldown,
			self.gaiaslime
		))
	
	def get_number_of_friendly_neighbors(self):
		if self.controlling_faction == "":
			return 0
		neighbors = poi_static.poi_neighbors[self.name]
		friendly_neighbors = 0

		for neighbor_id in neighbors:
			neighbor_data = EwDistrict(id_server = self.id_server, district = neighbor_id)
			if neighbor_data.controlling_faction == self.controlling_faction:
				friendly_neighbors += 1
		return friendly_neighbors

	def all_neighbors_friendly(self):
		rival_gang_poi = "none"
		if self.controlling_faction == "":
			return False
		elif self.controlling_faction == ewcfg.faction_killers:
			rival_gang_poi = ewcfg.poi_id_rowdyroughhouse
		elif self.controlling_faction == ewcfg.faction_rowdys:
			rival_gang_poi = ewcfg.poi_id_copkilltown


		neighbors = poi_static.poi_neighbors[self.name]
		for neighbor_id in neighbors:
			neighbor_poi = poi_static.id_to_poi.get(neighbor_id)
			neighbor_data = EwDistrict(id_server = self.id_server, district = neighbor_id)
			if neighbor_data.controlling_faction != self.controlling_faction and not neighbor_poi.is_subzone and not neighbor_poi.is_outskirts or neighbor_poi.id_poi == rival_gang_poi:
				return False
			elif neighbor_poi.id_poi == ewcfg.poi_id_juviesrow:
				return False
		return True

	def all_streets_taken(self):
		street_name_list = ewutils.get_street_list(self.name)
		
		if self.name == ewcfg.poi_id_rowdyroughhouse:
			return ewcfg.faction_rowdys
		elif self.name == ewcfg.poi_id_copkilltown:
			return ewcfg.faction_killers

		faction_list = []
		for name in street_name_list:
			district_data = EwDistrict(id_server=self.id_server, district=name)
			faction_list.append(district_data.controlling_faction)
	
		if len(faction_list) > 0 and all(faction == faction_list[0] for faction in faction_list):
			return faction_list[0]
		else:
			return ""

	def get_players_in_district(self,
			min_level = 0,
			max_level = math.inf,
			life_states = [],
			factions = [],
			min_slimes = -math.inf,
			max_slimes = math.inf,
			ignore_offline = False,
			pvp_only = False
		):
		client = ewutils.get_client()
		server = client.get_guild(self.id_server)
		if server == None:
			ewutils.logMsg("error: couldn't find server with id {}".format(self.id_server))
			return []
		time_now = int(time.time())

		players = bknd_core.execute_sql_query("SELECT {id_user}, {slimes}, {slimelevel}, {faction}, {life_state} FROM users WHERE id_server = %s AND {poi} = %s".format(
			id_user = ewcfg.col_id_user,
			slimes = ewcfg.col_slimes,
			slimelevel = ewcfg.col_slimelevel,
			faction = ewcfg.col_faction,
			life_state = ewcfg.col_life_state,
			poi = ewcfg.col_poi
		),(
			self.id_server,
			self.name
		))

		filtered_players = []
		for player in players:
			id_user = player[0]
			slimes = player[1]
			slimelevel = player[2]
			faction = player[3]
			life_state = player[4]
			
			member = server.get_member(id_user)

			if member != None:
				if max_level >= slimelevel >= min_level \
				and max_slimes >= slimes >= min_slimes \
				and (len(life_states) == 0 or life_state in life_states) \
				and (len(factions) == 0 or faction in factions) \
				and not (ignore_offline and member.status == discord.Status.offline):# \
				#and not (pvp_only and life_state == ewcfg.life_state_juvenile and slimelevel <= ewcfg.max_safe_level):
					filtered_players.append(id_user)

		return filtered_players

	def get_enemies_in_district(self,
			min_level = 0,
			max_level = math.inf,
			min_slimes = -math.inf,
			max_slimes = math.inf,
			scout_used = False,
			classes = None,
		):

		client = ewutils.get_client()
		server = client.get_guild(self.id_server)
		if server == None:
			ewutils.logMsg("error: couldn't find server with id {}".format(self.id_server))
			return []

		enemies = bknd_core.execute_sql_query("SELECT {id_enemy}, {slimes}, {level}, {enemytype}, {enemyclass} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1".format(
			id_enemy = ewcfg.col_id_enemy,
			slimes = ewcfg.col_enemy_slimes,
			level = ewcfg.col_enemy_level,
			enemytype = ewcfg.col_enemy_type,
			enemyclass = ewcfg.col_enemy_class,
			poi = ewcfg.col_enemy_poi,
			life_state = ewcfg.col_enemy_life_state
		),(
			self.id_server,
			self.name
		))

		filtered_enemies = []
		for enemy_data_column in enemies:

			fetched_id_enemy = enemy_data_column[0] # data from id_enemy column in enemies table
			fetched_slimes = enemy_data_column[1] # data from slimes column in enemies table
			fetched_level = enemy_data_column[2] # data from level column in enemies table
			fetched_type = enemy_data_column[3] # data from enemytype column in enemies table
			fetched_class = enemy_data_column[4] # data from enemyclass column in enemies table

			# Append the enemy to the list if it meets the requirements
			if max_level >= fetched_level >= min_level \
			and max_slimes >= fetched_slimes >= min_slimes:
				if classes != None:
					if fetched_class in classes:
						filtered_enemies.append(fetched_id_enemy)
				else:
					filtered_enemies.append(fetched_id_enemy)
				
			# Don't show sandbags on !scout
			if scout_used and fetched_type == ewcfg.enemy_type_sandbag:
				filtered_enemies.remove(fetched_id_enemy)

		return filtered_enemies

	def decay_capture_points(self):
		resp_cont_decay = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = self.id_server)
		if self.capture_points > 0:
				#and self.time_unlock == 0:

			neighbors = poi_static.poi_neighbors[self.name]
			all_neighbors_friendly = self.all_neighbors_friendly()

			decay = -math.ceil(ewcfg.limit_influence_a / (ewcfg.ticks_per_day * ewcfg.decay_modifier))
			#decay = -math.ceil(ewcfg.max_capture_points_a / (ewcfg.ticks_per_day * ewcfg.decay_modifier))

			slimeoids = ewutils.get_slimeoids_in_poi(poi = self.name, id_server = self.id_server, sltype = ewcfg.sltype_nega)
			
			nega_present = len(slimeoids) > 0

			poi = poi_static.id_to_poi.get(self.name)

			if nega_present:
				decay *= 1.5
			if self.capture_points + (decay * 3) > (ewcfg.limit_influence[poi.property_class]):
				decay *= 3

			if self.controlling_faction == "" or (not self.all_neighbors_friendly() and self.capture_points > ewcfg.limit_influence[poi.property_class]) or nega_present:  # don't decay if the district is completely surrounded by districts controlled by the same faction
				# reduces the capture progress at a rate with which it arrives at 0 after 1 in-game day
				#if (self.capture_points + int(decay) < ewcfg.min_influence[self.property_class] and self.capture_points >= ewcfg.min_influence[self.property_class]) and not nega_present and self.controlling_faction != "":
				#	responses = self.change_capture_points(self.capture_points - ewcfg.min_influence[self.property_class], ewcfg.actor_decay)
				#else:
				responses = self.change_capture_points(int(decay), ewcfg.actor_decay)
				resp_cont_decay.add_response_container(responses)

		#if self.capture_points < 0:
		#	self.capture_points = 0

		if self.capture_points <= 0:
			if self.controlling_faction != "":  # if it was owned by a faction

				message = "The {faction} have lost control over {district} because of sheer negligence.".format(
					faction = self.controlling_faction,
					district = poi_static.id_to_poi[self.name].str_name
				)
				channels = [poi_static.id_to_poi[self.name].channel] + ewcfg.hideout_channels
				for ch in channels:
					resp_cont_decay.add_channel_response(channel = ch, response = message)
			responses = self.change_ownership("", ewcfg.actor_decay)
			resp_cont_decay.add_response_container(responses)
			self.capturing_faction = ""
		return resp_cont_decay

	def change_capture_lock(self, progress):
		resp_cont = ewutils.EwResponseContainer(id_server = self.id_server)

		progress_before = self.time_unlock

		self.time_unlock += progress

		if self.time_unlock < 0:
			self.time_unlock == 0

		progress_after = self.time_unlock

		if (progress_after // ewcfg.capture_lock_milestone) != (progress_before // ewcfg.capture_lock_milestone):
			time_mins = ewutils.formatNiceTime(seconds = progress_after, round_to_minutes = True)
			if progress < 0:
				if progress_before >= 15 * 60 >= progress_after:
					message = "{district} will unlock for capture in {time}.".format(
						district = poi_static.id_to_poi[self.name].str_name,
						time = time_mins
					)
					channels = ewcfg.hideout_channels

					for ch in channels:
						resp_cont.add_channel_response(channel = ch, response = message)
				
				elif progress_before >= 5 * 60 >= progress_after:
					message = "{district} will unlock for capture in {time}.".format(
						district = poi_static.id_to_poi[self.name].str_name,
						time = time_mins
					)
					channels = ewcfg.hideout_channels

					for ch in channels:
						resp_cont.add_channel_response(channel = ch, response = message)
				
				message = "{district} will unlock for capture in {time}.".format(
					district = poi_static.id_to_poi[self.name].str_name,
					time = time_mins
				)

				channels = [poi_static.id_to_poi[self.name].channel]

				for ch in channels:
					resp_cont.add_channel_response(channel = ch, response = message)

		if self.time_unlock == 0 and progress < 0:
			chip_cont = self.change_capture_points(progress = -1, actor = ewcfg.actor_decay)
			resp_cont.add_response_container(chip_cont)

		return resp_cont

	def change_capture_points(self, progress, actor, num_lock = 0):  # actor can either be a faction or "decay"
		district_poi = poi_static.id_to_poi.get(self.name)
		invasion_response = ""
		max_capture = ewcfg.limit_influence[district_poi.property_class]
		progress_percent_before = int(self.capture_points / max_capture * 100)

		if actor == 'slimecorp':
			progress /= 3

		self.capture_points += progress

		resp_cont_change_cp = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = self.id_server)

		# ensures that the value doesn't exceed the bounds
		if self.capture_points < 0:
			self.capture_points = 0


		if self.cap_side == "" and actor != ewcfg.actor_decay:
			self.cap_side = actor


		if self.capture_points <= 0:
			self.cap_side = ""
			self.controlling_faction = ""


		elif self.capture_points > self.max_capture_points:
			self.capture_points = self.max_capture_points
		#where we're going we don't need roads

		progress_percent_after = int(self.capture_points / max_capture * 100)

		#if num_lock > 0 \
		#and self.capture_points == max_capture \
		#and progress > 0 \
		#and self.property_class in ewcfg.capture_locks \
		#and self.time_unlock == 0:
		#	base_time_unlock = ewcfg.capture_locks.get(self.property_class)
		#	responses = self.change_capture_lock(base_time_unlock + (num_lock - 1) * ewcfg.capture_lock_per_gangster)
		#	resp_cont_change_cp.add_response_container(responses)

		if actor != ewcfg.actor_decay:
			self.capturing_faction = actor


		if self.controlling_faction == "" and progress > 0 and self.cap_side == actor and self.capture_points + progress > (ewcfg.min_influence[district_poi.property_class]):
			self.controlling_faction = actor
			invasion_response = "{} just captured {}.".format(self.capturing_faction.capitalize(), district_poi.str_name)


		# display a message if it's reached a certain amount
		if (progress_percent_after // ewcfg.capture_milestone) != (progress_percent_before // ewcfg.capture_milestone):  # if a progress milestone was reached
			if progress > 0:  # if it was a positive change
				if ewcfg.capture_milestone <= progress_percent_after < ewcfg.capture_milestone * 2:  # if its the first milestone
					message = "{faction} have started capturing {district}. Current progress: {progress}%".format(
						faction = self.capturing_faction.capitalize(),
						district = district_poi.str_name,
						progress = progress_percent_after
					)
					channels = [district_poi.channel]

					for ch in channels:
						resp_cont_change_cp.add_channel_response(channel = ch, response = message)
				else:
					# alert both factions of significant capture progress
					if progress_percent_after >= 30 > progress_percent_before:  # if the milestone of 30% was just reached
						message = "{faction} are capturing {district}.".format(
							faction = self.capturing_faction.capitalize(),
							district = district_poi.str_name,
							progress = progress_percent_after
						)
						if self.controlling_faction == ewcfg.faction_rowdys:
							channels = [ewcfg.channel_rowdyroughhouse]
						elif self.controlling_faction == ewcfg.faction_killers:
							channels = [ewcfg.channel_copkilltown]
						else:
							channels = ewcfg.hideout_channels

						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)

					if self.controlling_faction != actor:  # if it's not already owned by that faction
						message = "{faction} continue to capture {district}. Current progress: {progress}%".format(
							faction = self.capturing_faction.capitalize(),
							district = poi_static.id_to_poi[self.name].str_name,
							progress = progress_percent_after
						)
						channels = [district_poi.channel]
						
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)
					else:
						message = "{faction} are renewing their grasp on {district}. Current control level: {progress}%".format(
							faction = self.capturing_faction.capitalize(),
							district = district_poi.str_name,
							progress = progress_percent_after
						)
						channels = [district_poi.channel]
						
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)
			else:  # if it was a negative change
				if self.controlling_faction != "":  # if the district is owned by a faction
					if progress_percent_after < 50 <= progress_percent_before:
						message = "{faction}' control of {district} is slipping.".format(
							faction = self.controlling_faction.capitalize(),
							district = district_poi.str_name,
							progress = progress_percent_after
						)
						channels = ewcfg.hideout_channels
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)

					elif progress_percent_after < 75 <= progress_percent_before and actor != ewcfg.actor_decay:
						message = "{faction} are de-capturing {district}.".format(
							faction = actor.capitalize(),
							district = district_poi.str_name,
							progress = progress_percent_after
						)
						channels = ewcfg.hideout_channels
						
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = message)

					message = "{faction}' control of {district} has decreased. Remaining control level: {progress}%".format(
						faction = self.controlling_faction.capitalize(),
						district = district_poi.str_name,
						progress = progress_percent_after
					)
					channels = [district_poi.channel]
					
					for ch in channels:
						resp_cont_change_cp.add_channel_response(channel = ch, response = message)
				else:  # if it's an uncontrolled district
					message = "{faction}' capture progress of {district} has decreased. Remaining progress: {progress}%".format(
						faction = self.capturing_faction.capitalize(),
						district = district_poi.str_name,
						progress = progress_percent_after
					)
					channels = [district_poi.channel]

					if invasion_response != "":
						for ch in channels:
							resp_cont_change_cp.add_channel_response(channel = ch, response = invasion_response)

		if progress < 0 and self.capture_points == 0:
			self.capturing_faction = ""

		# if capture_points is at its maximum value (or above), assign the district to the capturing faction
		#if self.capture_points > max_capture:
		#	responses = self.change_ownership(self.capturing_faction, actor)
		#	resp_cont_change_cp.add_response_container(responses)

		# if the district has decayed or been de-captured and it wasn't neutral anyway, make it neutral
		#elif self.capture_points == 0 and self.controlling_faction != "":
		#	responses = self.change_ownership("", actor)
		#	resp_cont_change_cp.add_response_container(responses)
		#return
		return resp_cont_change_cp

	"""
		Change who controls the district. Can be used to update the channel topic by passing the already controlling faction as an arg.
	"""
	def change_ownership(self, new_owner, actor, client = None):  # actor can either be a faction, "decay", or "init"
		resp_cont_owner = ewutils.EwResponseContainer(client = ewutils.get_client(), id_server = self.id_server)

		factions = ["", ewcfg.faction_killers, ewcfg.faction_rowdys]

		if new_owner in factions:
			server = ewcfg.server_list[self.id_server]
			channel_str = poi_static.id_to_poi[self.name].channel
			channel = ewutils.get_channel(server = server, channel_name = channel_str)

			if channel is not None and channel.topic:  # tests if the topic is neither None nor empty
				initialized = False

				# initialize channel topic control statuses
				for faction in factions:
					if ewcfg.control_topics[faction] in channel.topic:
						initialized = True

				if not initialized:
					new_topic = channel.topic + " " + ewcfg.control_topics[new_owner]

				# replace the the string of the previously controlling faction with that of the new one.
				else:
					new_topic = channel.topic.replace(ewcfg.control_topics[self.controlling_faction], ewcfg.control_topics[new_owner])

				if client is None:
					client = ewutils.get_client()


				if client is not None:
					resp_cont_owner.add_channel_topic(channel = channel_str, topic = new_topic)

			if self.controlling_faction != new_owner:  # if the controlling faction actually changed
				if new_owner != "":  # if it was captured by a faction instead of being de-captured or decayed
					countdown_message = ""
					if self.time_unlock > 0:
						countdown_message = "It will unlock for capture again in {}.".format(ewutils.formatNiceTime(seconds = self.time_unlock, round_to_minutes = True))
					message = "{faction} just captured {district}. {countdown}".format(
						faction = self.capturing_faction.capitalize(),
						district = poi_static.id_to_poi[self.name].str_name,
						countdown = countdown_message
					)
					channels = [poi_static.id_to_poi[self.name].channel] + ewcfg.hideout_channels
					
					for ch in channels:
						resp_cont_owner.add_channel_response(channel = ch, response = message)
				else:  # successful de-capture or full decay
					if actor != ewcfg.actor_decay:
						message = "{faction} just wrested control over {district} from the {other_faction}.".format(
							faction = actor.capitalize(),
							district = poi_static.id_to_poi[self.name].str_name,
							other_faction = self.controlling_faction  # the faction that just lost control
						)
						channels = [poi_static.id_to_poi[self.name].channel] + ewcfg.hideout_channels
						
						for ch in channels:
							resp_cont_owner.add_channel_response(channel = ch, response = message)

				self.controlling_faction = new_owner

		return resp_cont_owner

	""" add or remove slime """
	def change_slimes(self, n = 0, source = None):
		change = int(n)
		self.slimes += change

	""" wether the district is still functional """
	def is_degraded(self):
		checked_poi = poi_static.id_to_poi.get(self.name)
		if checked_poi is None:
			return True
		
		poi = None
		
		# In the Gankers Vs. Shamblers event, importance is placed on districts
		# As a result, if a district is degraded, then all of its subzones/streets are also now degraded
		if checked_poi.is_district:
			poi = checked_poi
		elif checked_poi.is_street:
			poi = poi_static.id_to_poi.get(checked_poi.father_district)
		elif checked_poi.is_subzone:
			# Subzones are a more complicated affair to check for degradation.
			# Look to see if its mother district is a district or a street, then check for degradation of the appropriate district.
			for mother_poi_id in checked_poi.mother_districts:
				mother_poi = poi_static.id_to_poi.get(mother_poi_id)
				
				if mother_poi.is_district:
					# First mother POI found is a district. Break here and check for its degradation.
					poi = mother_poi
					break
				elif mother_poi.is_street:
					# First mother POI found is a street. Break here and check for its father district's degradation.
					poi = poi_static.id_to_poi.get(mother_poi.father_district)
					break
		else:
			poi = checked_poi

		# print('poi checked was {}. looking for {} degradation.'.format(self.name, poi.id_poi))
		poi_district_data = EwDistrict(district = poi.id_poi, id_server = self.id_server)
		return poi_district_data.degradation >= poi.max_degradation
