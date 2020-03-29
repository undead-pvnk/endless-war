#import math
#import time
#import random
#import asyncio

import ewutils
#import ewcfg

from ew import EwUser
from ewplayer import EwPlayer

"""
	Prank items for Swilldermuk
"""
class EwPrankItem:
	item_type = "item"
	id_item = " "
	
	
	alias = []
	
	context = "prankitem"
	str_name = ""
	str_desc = ""
	
	prank_type = "" # Type of prank item. Can be an instant use, trap, or response item
	prank_desc = "" # A line of text that appears when the prank item gets used
	rarity = "" # Rarity of prank item. Used in determining how often it should spawn
	gambit = 0 # Gambit multiplier
	response_command = "" # All response items need a different command to break out of them
	trap_chance = 0 # All trap items only have a certain chance to activate
	trap_stored_credence = 0 # Trap items store half your current credence up front for later
	trap_user_id = "" # Trap items store your user id when you lay them down for later
	side_effect = "" # Some prank items have side-effects. Example: The 'bungis beam' will change a player's name to '[player name] (Bungis)'
	
	ingredients = ""
	acquisition = ""
	vendors = []

	def __init__(
		self,
		id_item=" ",
		alias = [],
		str_name = "",
		str_desc = "",
		prank_type = "",
		prank_desc = "",
		rarity = "",
		gambit = 0,
		response_command = "",
		trap_chance = 0,
		trap_stored_credence = 0,
		trap_user_id = "",
		side_effect = "",
		ingredients = "",
		acquisition = "",
		vendors = [],
	):
		self.item_type = "item"
		self.id_item = id_item
		self.alias = alias
		self.context = "prankitem"
		self.str_name = str_name
		self.str_desc = str_desc
		self.prank_type = prank_type
		self.prank_desc = prank_desc
		self.rarity = rarity
		self.gambit = gambit
		self.response_command = response_command
		self.trap_chance = trap_chance
		self.trap_stored_credence = trap_stored_credence
		self.trap_user_id = trap_user_id
		self.side_effect = side_effect
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.vendors = vendors
		
def calculate_gambit_exchange(pranker_data, pranked_data, item, response_item_multiplier = 1):
	pranker_credence = pranker_data.credence
	pranked_credence = pranked_data.credence
	
	print(pranker_credence)
	print(pranked_credence)
	
	item_props = item.item_props
	gambit_multiplier = int(item_props.get('gambit'))
	
	total_gambit_value = ((pranked_credence + pranker_credence) * gambit_multiplier * response_item_multiplier)
	
	pranker_data.credence = 0
	pranked_data.credence = 0
	
	pranker_data.credence_used += total_gambit_value
	pranked_data.credence_used += total_gambit_value
	
	pranker_data.gambit += total_gambit_value
	pranked_data.gambit -= total_gambit_value
	
	pranker_data.persist()
	pranked_data.persist()
	
async def prank_item_effect_instantuse(cmd, item):
	should_delete_item = False
	mentions_user = False
	use_mention_displayname = False
	if cmd.mentions_count == 1:
		mentions_user = True
		
	if mentions_user:
		member = cmd.mentions[0]
		
		pranker_data = EwUser(member=cmd.message.author)
		pranked_data = EwUser(member=member)
		
		prank_item_data = item
		
		calculate_gambit_exchange(pranker_data, pranked_data, prank_item_data)
		
		response = prank_item_data.item_props.get('prank_desc')
		
		response = response.format(cmd.message.author.display_name)
		should_delete_item = False
		use_mention_displayname = True
	else:
		response = "You gotta find someone to prank someone with that item, first!\n**(Hint: !use item @player)**"
		should_delete_item = False
	
	return should_delete_item, response, use_mention_displayname


async def prank_item_effect_response(cmd, item):
	return True, "", False

async def prank_item_effect_trap(cmd, item):
	return True, "", False