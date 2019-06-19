import math
import time

import ewcfg
import ewitem
import ewutils
import ewrolemgr
from ew import EwUser
from ewmarket import EwMarket, EwCompany, EwStock

""" Food model object """
class EwFood:
	# The main name of this food.
	id_food = ""

	# A list of alternative names.
	alias = []

	# Hunger reduced by eating this food.
	recover_hunger = 0

	# Cost in SlimeCoin to eat this food.
	price = 0

	# A nice string name describing this food.
	str_name = ""

	# Names of the vendors selling this food in the food court.
	vendors = []

	# Flavor text displayed when you eat this food.
	str_eat = ""

	# Alcoholic effect
	inebriation = 0

	# Flavor text displayed when you inspect this food.
	str_desc = ""

	# Expiration time (can be left blank for standard expiration time)
	time_expir = 0

	# The ingredients necessary to make this item via milling.
	ingredients = ""

	def __init__(
		self,
		id_food = "",
		alias = [],
		recover_hunger = 0,
		price = 0,
		str_name = "",
		vendors = [],
		str_eat = "",
		inebriation = 0,
		str_desc = "",
		time_expir = 0,
		ingredients = ""
	):
		self.id_food = id_food
		self.alias = alias
		self.recover_hunger = recover_hunger
		self.price = price
		self.str_name = str_name
		self.vendors = vendors
		self.str_eat = str_eat
		self.inebriation = inebriation
		self.str_desc = str_desc
		self.time_expir = time_expir if time_expir > 0 else ewcfg.std_food_expir
		self.ingredients = ingredients


""" show all available food items """
async def menu(cmd):
	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	if poi == None or len(poi.vendors) == 0:
		# Only allowed in the food court.
		response = ewcfg.str_food_channelreq.format(action = "see the menu")
	else:
		response = "{} Menu:\n\n".format(poi.str_name)

		for vendor in poi.vendors:
			food_items = []
			for food_item_name in ewcfg.food_vendor_inv[vendor]:
				food_item = ewcfg.food_map.get(food_item_name)
				# increase profits for the stock market
				stock_data = None
				if vendor in ewcfg.vendor_stock_map:
					stock = ewcfg.vendor_stock_map.get(vendor)
					stock_data = EwStock(id_server = user_data.id_server, stock = stock)

				value = food_item.price

				if stock_data is not None:
					value *= (stock_data.exchange_rate / ewcfg.default_stock_exchange_rate) ** 0.2

				value = int(value)

				if food_item != None:
					food_items.append('{name} ({price})'.format(name=food_item_name, price=value))
				else:
					food_items.append(food_item_name)

			response += "**{}**: *{}*\n".format(vendor, ewutils.formatNiceList(names = food_items))

	# Send the response to the player.1
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

""" players order food, for themselves or somebody else """
async def order(cmd):
	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)
	time_now = int(time.time())

	if (poi == None) or (len(poi.vendors) == 0):
		# Only allowed in the food court.
		response = ewcfg.str_food_channelreq.format(action = "order")
	else:
		value = None
		togo = False
		current_vendor = None
		if cmd.tokens_count > 1:
			for token in cmd.tokens[1:]:
				if token.startswith('<@') == False and token.lower() not in "togo":  # togo can be spelled together or separate
					value = token
					break
			for token in cmd.tokens[1:]:
				if token.lower() in "togo":  # lets people get away with just typing only to or only go (or only t etc.) but whatever
					togo = True
					break

		food = ewcfg.food_map.get(value.lower() if value != None else value)
		if food != None and ewcfg.vendor_vendingmachine in food.vendors:
			togo = True

		member = None
		if not togo:  # cant order togo for someone else, you can just give it to them in person
			if cmd.mentions_count == 1:
				member = cmd.mentions[0]
				if member.id == cmd.message.author.id:
					member = None

		member_data = EwUser(member = member)

		if food is not None:
			# gets a vendor that the item is available and the player currently located in
			try:
				current_vendor = (set(food.vendors).intersection(set(poi.vendors))).pop()
			except:
				current_vendor = None

		if food == None or current_vendor is None or len(current_vendor) < 1:
			response = "Check the {} for a list of items you can {}.".format(ewcfg.cmd_menu, ewcfg.cmd_order)
		elif member is not None and member_data.poi != user_data.poi:
			response = "The delivery service has become unavailable due to unforeseen circumstances."
		else:
			market_data = EwMarket(id_server = cmd.message.server.id)

			target_data = None
			if member != None:
				target_data = EwUser(member = member)

			value = food.price if not togo else food.price * ewcfg.togo_price_increase
			
			stock_data = None
			company_data = None
			# factor in the current stocks
			for vendor in food.vendors:
				if vendor in ewcfg.vendor_stock_map:
					stock = ewcfg.vendor_stock_map.get(vendor)
					company_data = EwCompany(id_server = user_data.id_server, stock = stock)
					stock_data = EwStock(id_server = user_data.id_server, stock = stock)
					

			if stock_data is not None:
				value *= (stock_data.exchange_rate / ewcfg.default_stock_exchange_rate) ** 0.2

			value = int(value)

			# Kingpins eat free.
			if user_data.life_state == ewcfg.life_state_kingpin or user_data.life_state == ewcfg.life_state_grandfoe:
				value = 0

			if value > user_data.slimecoin:
				# Not enough money.
				response = "A {food} is {cost:,} SlimeCoin (and you only have {coins:,}).".format(
					food = food.str_name,
					cost = value,
					coins = user_data.slimecoin
				)
			else:
				user_data.change_slimecoin(n = -value, coinsource = ewcfg.coinsource_spending)

				if company_data is not None:
					company_data.recent_profits += value
					company_data.persist()


				if not togo:

					if target_data != None:
						target_data.hunger -= food.recover_hunger
						if target_data.hunger < 0:
							target_data.hunger = 0
						target_data.inebriation += food.inebriation
						if target_data.inebriation > ewcfg.inebriation_max:
							target_data.inebriation = ewcfg.inebriation_max
						if food.id_food == "coleslaw":
							target_data.ghostbust = True
							#Bust target if they're a ghost
							if target_data.life_state == ewcfg.life_state_corpse:
								target_data.die(cause = ewcfg.cause_busted)

					else:
						user_data.hunger -= food.recover_hunger
						if user_data.hunger < 0:
							user_data.hunger = 0
						user_data.inebriation += food.inebriation
						if user_data.inebriation > ewcfg.inebriation_max:
							user_data.inebriation = ewcfg.inebriation_max
						if food.id_food == "coleslaw":
							user_data.ghostbust = True
							#Bust player if they're a ghost
							if user_data.life_state == ewcfg.life_state_corpse:
								user_data.die(cause = ewcfg.cause_busted)

				else:  # if it's togo
					food_items = ewitem.inventory(
						id_user = cmd.message.author.id,
						id_server = cmd.message.server.id,
						item_type_filter = ewcfg.it_food
					)

					if len(food_items) >= user_data.get_food_capacity():
						# user_data never got persisted so the player won't lose money unnecessarily
						response = "You can't carry any more food than that."
						return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

					item_props = {
						# not all attributes are necessary to store in the database since the price and vendors list is only needed for buying it
						'id_food': food.id_food,
						'food_name': food.str_name,
						'food_desc': food.str_desc,
						'recover_hunger': food.recover_hunger,
						'inebriation': food.inebriation,
						'str_eat': food.str_eat,
						'time_expir': time.time() + (food.time_expir if food.time_expir is not None else ewcfg.std_food_expir)
					}

					ewitem.item_create(
						item_type = ewcfg.it_food,
						id_user = cmd.message.author.id,
						id_server = cmd.message.server.id,
						item_props = item_props
					)

				response = "You slam an encrypted thumbdrive into the cash register down at {vendor} and transfer {cost:,} SlimeCoin for a {food}{togo}{sharetext}{flavor}".format(
					cost = value,
					vendor = current_vendor,
					food = food.str_name,
					togo = " to go" if togo else "",
					sharetext = (". " if member == None else " and give it to {}.\n\n{}".format(member.display_name, ewutils.formatMessage(member, ""))),
					flavor = food.str_eat if not togo else ""
				)
				if member == None and user_data.hunger <= 0 and not togo:
					response += "\n\nYou're stuffed!"

				user_data.persist()
				market_data.persist()

				if target_data != None:
					target_data.persist()
					await ewrolemgr.updateRoles(client = cmd.client, member = member)

				await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
