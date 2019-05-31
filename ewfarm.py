import time
import random

import ewcfg
import ewitem
import ewutils

from ew import EwUser
from ewmarket import EwMarket
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
					vegetable = ewcfg.vegetable_list[random.randint(0, len(ewcfg.vegetable_list) - 1)]

					#  Create and give a bushel of whatever crop was grown.
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
								'time_expir': time.time() + ewcfg.farm_food_expir
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
	market_data = EwMarket(id_server = user_data.id_server)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search = item_search, id_user = cmd.message.author.id, id_server = cmd.message.server.id if cmd.message.server is not None else None)

	# Checking availability of milling
	if user_data.life_state != ewcfg.life_state_juvenile:
		response = "Only Juveniles of pure heart and with nothing better to do can mill their vegetables."
	elif user_data.poi not in [ewcfg.poi_id_jr_farms, ewcfg.poi_id_og_farms, ewcfg.poi_id_ab_farms]:
		response = "Alas, there doesn’t seem to be an official SlimeCorp milling station anywhere around here. Probably because you’re in the middle of the fucking city. Try looking where you reaped your vegetable in the first place, dumbass."

	elif user_data.slimes < ewcfg.slimes_permill:
		response = "It costs {} to !mill, and you only have {}.".format(ewcfg.slimes_permill, user_data.slimes)

	elif item_sought:
		items = []

		for result in ewcfg.mill_results:
			if result.ingredients != item_search:
				pass
			else:
				items.append(result)

		if len(items) > 0:
			item = random.choice(items)

			if hasattr(item, 'id_item'):
				ewitem.item_create(
					item_type = ewcfg.it_item,
					id_user = cmd.message.author.id,
					id_server = cmd.message.server.id,
					item_props = {
						'id_item': item.id_item,
						'context': item.context,
						'subcontext': item.subcontext,
						'item_name': item.str_name,
						'item_desc': item.str_desc,
						'ingredients': item.ingredients,
					}
				),

			elif hasattr(item, 'id_food'):
				ewitem.item_create(
					item_type = ewcfg.it_food,
					id_user = cmd.message.author.id,
					id_server = cmd.message.server.id,
					item_props = {
						'id_food': item.id_food,
						'food_name': item.str_name,
						'food_desc': item.str_desc,
						'recover_hunger': item.recover_hunger,
						'inebriation': item.inebriation,
						'str_eat': item.str_eat,
						'time_expir': time.time() + ewcfg.farm_food_expir
					}
				),

			elif hasattr(item, 'id_cosmetic'):
				ewitem.item_create(
					item_type = ewcfg.it_cosmetic,
					id_user = cmd.message.author.id,
					id_server = cmd.message.server.id,
					item_props = {
						'id_cosmetic': item.id_cosmetic,
						'cosmetic_name': item.str_name,
						'cosmetic_desc': item.str_desc,
						'rarity': item.rarity,
						'adorned': 'false'
					}
				),

			response = "You walk up to the official SlimeCorp Milling Station and shove your irradiated produce into the hand-crank. You prick your finger, dripping {} slimes into a small compartment on the device’s side which supposedly fuels it. You begin slowly churning them into a glorious, pastry goo. As the goo tosses and turns inside the machine, it solidifies, and after a few moments a {} pops out!".format(ewcfg.slimes_permill, item.str_name)

			market_data.donated_slimes -= ewcfg.slimes_permill
			market_data.persist()

			ewitem.item_delete(id_item = item_sought.get('id_item'))
			user_data.change_slimes(n = ewcfg.slimes_permill, source = ewcfg.source_spending)
			user_data.persist()
		else:
			response = "You can only mill fresh vegetables! SlimeCorp obviously wants you to support local farmers."

	else:
		if item_search:  # if they didn't forget to specify an item and it just wasn't found
			response = "You don't have one."
		else:
			response = "Mill which item? (check **!inventory**)"

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


