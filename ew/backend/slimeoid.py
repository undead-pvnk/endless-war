import random

from ..static import cfg as ewcfg
from ..static import poi as poi_static
from .. import utils as ewutils
from . import core as bknd_core

from ..user import EwUser
from .market import EwMarket
from .player import EwPlayer

""" Slimeoid data model for database persistence """
class EwSlimeoid:
	id_slimeoid = 0
	id_user = ""
	id_server = -1

	life_state = 0
	body = ""
	head = ""
	legs = ""
	armor = ""
	weapon = ""
	special = ""
	ai = ""
	sltype = "Lab"
	name = ""
	atk = 0
	defense = 0
	intel = 0
	level = 0
	time_defeated = 0
	clout = 0
	hue = ""
	coating = ""
	poi = ""

	#slimeoid = EwSlimeoid(member = cmd.message.author, )
	#slimeoid = EwSlimeoid(id_slimeoid = 12)

	""" Load the slimeoid data for this user from the database. """
	def __init__(self, member = None, id_slimeoid = None, life_state = None, id_user = None, id_server = None, sltype = "Lab", slimeoid_name = None):
		query_suffix = ""
		user_data = None
		if member != None:
			id_user = str(member.id)
			id_server = member.guild.id
		elif id_user != None:
			id_user = str(id_user)

		#	user_data = EwUser(member = member)

		#if user_data != None:
		#	if user_data.active_slimeoid > -1:
		#		id_slimeoid = user_data.active_slimeoid

		if id_slimeoid != None:
			query_suffix = " WHERE id_slimeoid = '{}'".format(id_slimeoid)
		else:

			if id_user != None and id_server != None:
				query_suffix = " WHERE id_user = '{}' AND id_server = '{}'".format(id_user, id_server)
				if life_state != None:
					query_suffix += " AND life_state = '{}'".format(life_state)
				if sltype != None:
					query_suffix += " AND type = '{}'".format(sltype)
				if slimeoid_name != None:
					query_suffix += " AND name = '{}'".format(slimeoid_name)


		if query_suffix != "":
			try:
				conn_info = bknd_core.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute("SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM slimeoids{}".format(
					ewcfg.col_id_slimeoid,
					ewcfg.col_id_user,
					ewcfg.col_id_server,
					ewcfg.col_life_state,
					ewcfg.col_body,
					ewcfg.col_head,
					ewcfg.col_legs,
					ewcfg.col_armor,
					ewcfg.col_weapon,
					ewcfg.col_special,
					ewcfg.col_ai,
					ewcfg.col_type,
					ewcfg.col_name,
					ewcfg.col_atk,
					ewcfg.col_defense,
					ewcfg.col_intel,
					ewcfg.col_level,
					ewcfg.col_time_defeated,
					ewcfg.col_clout,
					ewcfg.col_hue,
					ewcfg.col_coating,
					ewcfg.col_poi,
					query_suffix
				))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.id_slimeoid = result[0]
					self.id_user = result[1]
					self.id_server = result[2]
					self.life_state = result[3]
					self.body = result[4]
					self.head = result[5]
					self.legs = result[6]
					self.armor = result[7]
					self.weapon = result[8]
					self.special = result[9]
					self.ai= result[10]
					self.sltype = result[11]
					self.name = result[12]
					self.atk = result[13]
					self.defense = result[14]
					self.intel = result[15]
					self.level = result[16]
					self.time_defeated = result[17]
					self.clout = result[18]
					self.hue = result[19]
					self.coating = result[20]
					self.poi = result[21]

			finally:
				# Clean up the database handles.
				cursor.close()
				bknd_core.databaseClose(conn_info)


	""" Save slimeoid data object to the database. """
	def persist(self):
		try:
			conn_info = bknd_core.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save the object.
			cursor.execute("REPLACE INTO slimeoids({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_slimeoid,
				ewcfg.col_id_user,
				ewcfg.col_id_server,
				ewcfg.col_life_state,
				ewcfg.col_body,
				ewcfg.col_head,
				ewcfg.col_legs,
				ewcfg.col_armor,
				ewcfg.col_weapon,
				ewcfg.col_special,
				ewcfg.col_ai,
				ewcfg.col_type,
				ewcfg.col_name,
				ewcfg.col_atk,
				ewcfg.col_defense,
				ewcfg.col_intel,
				ewcfg.col_level,
				ewcfg.col_time_defeated,
				ewcfg.col_clout,
				ewcfg.col_hue,
				ewcfg.col_coating,
				ewcfg.col_poi
			), (
				self.id_slimeoid,
				self.id_user,
				self.id_server,
				self.life_state,
				self.body,
				self.head,
				self.legs,
				self.armor,
				self.weapon,
				self.special,
				self.ai,
				self.sltype,
				self.name,
				self.atk,
				self.defense,
				self.intel,
				self.level,
				self.time_defeated,
				self.clout,
				self.hue,
				self.coating,
				self.poi
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			bknd_core.databaseClose(conn_info)

	def die(self):
		self.life_state = ewcfg.slimeoid_state_dead
		self.id_user = ""


	def delete(self):
		bknd_core.execute_sql_query("DELETE FROM slimeoids WHERE {id_slimeoid} = %s".format(
			id_slimeoid = ewcfg.col_id_slimeoid
		),(
			self.id_slimeoid,
		))
	
	def haunt(self):
		resp_cont = ewutils.EwResponseContainer(id_server = self.id_server)
		if (self.sltype != ewcfg.sltype_nega) or ewutils.active_slimeoidbattles.get(self.id_slimeoid):
			return resp_cont
		market_data = EwMarket(id_server = self.id_server)
		ch_name = poi_static.id_to_poi.get(self.poi).channel

		data = bknd_core.execute_sql_query("SELECT {id_user} FROM users WHERE {poi} = %s AND {id_server} = %s".format(
			id_user = ewcfg.col_id_user,
			poi = ewcfg.col_poi,
			id_server = ewcfg.col_id_server
		),(
			self.poi,
			self.id_server
		))

		for row in data:
			haunted_data = EwUser(id_user = row[0], id_server = self.id_server)
			haunted_player = EwPlayer(id_user = row[0])

			if haunted_data.life_state in [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted]:
				haunted_slimes = 2 * int(haunted_data.slimes / ewcfg.slimes_hauntratio)

				haunt_cap = 10 ** (self.level-1)
				haunted_slimes = min(haunt_cap, haunted_slimes) # cap on for how much you can haunt

				haunted_data.change_slimes(n = -haunted_slimes, source = ewcfg.source_haunted)
				market_data.negaslime -= haunted_slimes

				# Persist changes to the database.
				haunted_data.persist()
		response = "{} lets out a blood curdling screech. Everyone in the district loses slime.".format(self.name)
		resp_cont.add_channel_response(ch_name, response)
		market_data.persist()

		return resp_cont

	def move(self):
		resp_cont = ewutils.EwResponseContainer(id_server = self.id_server)
		if ewutils.active_slimeoidbattles.get(self.id_slimeoid):
			return resp_cont
		try:
			destinations = poi_static.poi_neighbors.get(self.poi).intersection(set(poi_static.capturable_districts))
			if len(destinations) > 0:
				self.poi = random.choice(list(destinations))
				poi_def = poi_static.id_to_poi.get(self.poi)
				ch_name = poi_def.channel
		
				response = "The air grows colder and color seems to drain from the streets and buildings around you. {} has arrived.".format(self.name)
				resp_cont.add_channel_response(ch_name, response)
				response = "There are reports of a sinister presence in {}.".format(poi_def.str_name)
				resp_cont.add_channel_response(ewcfg.channel_rowdyroughhouse, response)
				resp_cont.add_channel_response(ewcfg.channel_copkilltown, response)
		finally:
			return resp_cont

	def eat(self, food_item):
		if food_item.item_props.get('context') != ewcfg.context_slimeoidfood:
			return False
		
		if food_item.item_props.get('decrease') == ewcfg.slimeoid_stat_moxie:
			if self.atk < 1:
				return False
			
			self.atk -= 1
		elif food_item.item_props.get('decrease') == ewcfg.slimeoid_stat_grit:
			if self.defense < 1:
				return False
			
			self.defense -= 1
		elif food_item.item_props.get('decrease') == ewcfg.slimeoid_stat_chutzpah:
			if self.intel < 1:
				return False
			
			self.intel -= 1
		if food_item.item_props.get('increase') == ewcfg.slimeoid_stat_moxie:
			self.atk += 1
		elif food_item.item_props.get('increase') == ewcfg.slimeoid_stat_grit:
			self.defense += 1
		elif food_item.item_props.get('increase') == ewcfg.slimeoid_stat_chutzpah:
			self.intel += 1

		return True

		



