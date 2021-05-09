import random


from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.backend import core as bknd_core

from ew.utils.combat import EwUser
from ew.backend.market import EwMarket
from ew.backend.player import EwPlayer

from ew.utils.frontend import EwResponseContainer
from ew.backend.slimeoid import EwSlimeoidBase

""" Slimeoid data model for database persistence """
class EwSlimeoid(EwSlimeoidBase):

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
		resp_cont = EwResponseContainer(id_server = self.id_server)
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
		resp_cont = EwResponseContainer(id_server = self.id_server)
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

		



