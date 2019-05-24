import time
import random

import ewcfg
import ewitem
import ewutils

from ew import EwUser
from ewitem import EwItem

class EwFarm:
	id_server = ""
	id_user = ""
	name = ""
	time_lastsow = 0

	def __init__(
		self,
		id_server = None,
		id_user = None,
		farm = None
	):
		if id_server is not None and id_user is not None and farm is not None:
			self.id_server = id_server
			self.id_user = id_user
			self.name = farm

			data = ewutils.execute_sql_query(
				"SELECT {time_lastsow} FROM farms WHERE id_server = %s AND id_user = %s AND {col_farm} = %s".format(
					time_lastsow = ewcfg.col_time_lastsow,
					col_farm = ewcfg.col_farm
				), (
					id_server,
					id_user,
					farm
				)
			)

			if len(data) > 0:  # if data is not empty, i.e. it found an entry
				# data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
				self.time_lastsow = data[0][0]
			else:  # create new entry
				ewutils.execute_sql_query(
					"REPLACE INTO farms (id_server, id_user, {col_farm}) VALUES (%s, %s, %s)".format(
						col_farm = ewcfg.col_farm
					), (
						id_server,
						id_user,
						farm
					)
				)

	def persist(self):
		ewutils.execute_sql_query(
			"REPLACE INTO farms(id_server, id_user, {col_farm}, {col_time_lastsow}) VALUES(%s, %s, %s, %s)".format(
				col_farm = ewcfg.col_farm,
				col_time_lastsow = ewcfg.col_time_lastsow
			), (
				self.id_server,
				self.id_user,
				self.name,
				self.time_lastsow
			)
		)

"""
	milled items
"""
class EwMilledItem:
	# The name of the cosmetic item
	name = ""

	# The text displayed when you look at it
	description = ""

	# The item(s) necessary to create this item
	ingredients = ""

	def __init__(
		self,
		name = "",
		desc = "",
		context_name = "",
		context_desc = "",
		ingredients = ""
	):
		self.name = name
		self.desc = desc
		self.context_name = context_name
		self.context_desc = context_desc
		self.ingredients = ingredients

"""
	Reap planted crops.
"""
async def reap(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Checking availability of reap action
	if user_data.life_state != ewcfg.life_state_juvenile:
		response = "Only Juveniles of pure heart and with nothing better to do can farm."
	elif user_data.poi not in [ewcfg.poi_id_jr_farms, ewcfg.poi_id_og_farms, ewcfg.poi_id_ab_farms]:
		response = "Do you remember planting anything here in this barren wasteland? No, you don’t. Idiot."
	else:
		if user_data.poi == ewcfg.poi_id_jr_farms:
			farm_id = ewcfg.poi_id_jr_farms
		elif user_data.poi == ewcfg.poi_id_og_farms:
			farm_id = ewcfg.poi_id_og_farms
		else:  # if it's the farm in arsonbrook
			farm_id = ewcfg.poi_id_ab_farms

		farm = EwFarm(
			id_server = cmd.message.server.id,
			id_user = cmd.message.author.id,
			farm = farm_id
		)

		if farm.time_lastsow == 0:
			response = "You missed a step, you haven’t planted anything here yet."
		else:
			cur_time_min = time.time() / 60
			time_grown = cur_time_min - farm.time_lastsow

			if time_grown < ewcfg.crops_time_to_grow:
				response = "Patience is a virtue and you are morally bankrupt. Just wait, asshole."
			else: # Reaping
				if time_grown > ewcfg.crops_time_to_grow * 16:  # about 2 days
					response = "You eagerly cultivate your crop, but what’s this? It’s dead and wilted! It seems as though you’ve let it lay fallow for far too long. Pay better attention to your farm next time. You gain no slime."
				else:
					# Determine if a slime poudrin is found.
					poudrin = False
					poudrinamount = 0

					poudrin_rarity = ewcfg.poudrin_rarity / 500  # 1 in 3 chance
					poudrin_mined = random.randint(1, poudrin_rarity)

					if poudrin_mined == 1:
						poudrin = True
						poudrinamount = 1 if random.randint(1, 3) != 1 else 2  # 33% chance of extra drop

					# Create and give slime poudrins
					for pcreate in range(poudrinamount):
						ewitem.item_create(
							id_user = cmd.message.author.id,
							id_server = cmd.message.server.id,
							item_type = ewcfg.it_slimepoudrin,
						)

					#  Determine what crop is grown.
					vegetable = ewcfg.food_map.get(random.choice(ewcfg.vegetable_list))

					for vcreate in range(4):
						ewitem.item_create(
							id_user = cmd.message.author.id,
							id_server = cmd.message.server.id,
							item_type = ewcfg.it_food,
							item_props = {
								'id_food': vegetable.id_food,
								'food_name': vegetable.str_name,
								'food_desc': vegetable.str_desc,
								'recover_hunger': vegetable.recover_hunger,
								'str_eat': vegetable.str_eat,
								'time_expir': time.time() + (vegetable.time_expir if vegetable.time_expir is not None else ewcfg.std_food_expir)
							}
						)

					slime_gain = ewcfg.reap_gain
					user_data.change_slimes(n = slime_gain, source = ewcfg.source_farming)
					user_data.hunger += ewcfg.hunger_perfarm
					user_data.persist()

					response = "You reap what you’ve sown. Your investment has yielded {} slime, ".format(ewcfg.reap_gain)

					if poudrin == True:
						if poudrinamount == 1:
							response += "a slime poudrin, "
						elif poudrinamount == 2:
							response += "two slime poudrins, "

					response += "and a bushel of {}!".format(vegetable.str_name)

				farm.time_lastsow = 0  # 0 means no seeds are currently planted
				farm.persist()
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


"""
	Sow seeds that may eventually be !reaped.
"""
async def sow(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Checking availability of sow action
	if user_data.life_state != ewcfg.life_state_juvenile:
		response = "Only Juveniles of pure heart and with nothing better to do can farm."

	elif user_data.poi not in [ewcfg.poi_id_jr_farms, ewcfg.poi_id_og_farms, ewcfg.poi_id_ab_farms]:
		response = "The cracked, filthy concrete streets around you would be a pretty terrible place for a farm. Try again on more arable land."

	else:
		if user_data.poi == ewcfg.poi_id_jr_farms:
			farm_id = ewcfg.poi_id_jr_farms
		elif user_data.poi == ewcfg.poi_id_og_farms:
			farm_id = ewcfg.poi_id_og_farms
		else:  # if it's the farm in arsonbrook
			farm_id = ewcfg.poi_id_ab_farms

		farm = EwFarm(
			id_server = cmd.message.server.id,
			id_user = cmd.message.author.id,
			farm = farm_id
		)

		if farm.time_lastsow > 0:
			response = "You’ve already sown something here. Try planting in another farming location. If you’ve planted in all three farming locations, you’re shit out of luck. Just wait, asshole."
		else:
			poudrins = ewitem.inventory(
				id_user = cmd.message.author.id,
				id_server = cmd.message.server.id,
				item_type_filter = ewcfg.it_slimepoudrin
			)

			if len(poudrins) < 1:
				response = "You don't have anything to plant! Try collecting a poudrin."
			else:
				# Sowing
				response = "You sow a poudrin into the fertile soil beneath you. It will grow in about a day."

				farm.time_lastsow = int(time.time() / 60)  # Grow time is stored in minutes.
				ewitem.item_delete(id_item = poudrins[0].get('id_item'))  # Remove Poudrins

				farm.persist()

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def mill(cmd):
	user_data = EwUser(member = cmd.message.author)
	ingredient_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	ingredient_sought = ewitem.find_item(item_search = ingredient_search, id_user = cmd.message.author.id, id_server = cmd.message.server.id if cmd.message.server is not None else None)

	if user_data.poi not in [ewcfg.poi_id_jr_farms, ewcfg.poi_id_og_farms, ewcfg.poi_id_ab_farms]:
		response = "You can only !mill in farms."

	elif ingredient_sought not in ewcfg.vegetable_list:
		response = "You can only !mill vegetables."

		if ingredient_sought:
			vegetable = EwItem(id_item = ingredient_sought.get("id_item"))
			matched_item = ""

			for result in ewcfg.milled_item_list:
				if EwMilledItem.ingredients != vegetable:
					pass
				else:
					matched_item = result

			item = matched_item

			ewitem.item_create(
				item_type = ewcfg.it_milleditem,
				id_user = cmd.message.author.id,
				id_server = cmd.message.server.id,
				item_props = {
					'milled_name': item.name,
					'milled_desc': item.desc,
					'context_name': item.context_name,
					'context_desc': item.context_desc,
					'ingredients': vegetable,
				}
			)
			response = "You milled a {item_name}!".format(item_name = item.name)
			user_data.persist()

		else:
			response = "You don't have one."

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


