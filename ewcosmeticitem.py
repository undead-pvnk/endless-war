import math
import random

import ewcfg
import ewitem
import ewutils
import asyncio

from ew import EwUser
from ewitem import EwItem

"""
	Cosmetic item model object
"""
class EwCosmeticItem:
	item_type = "cosmetic"

	# The proper name of the cosmetic item
	id_cosmetic = ""

	# The string name of the cosmetic item
	str_name = ""

	# The text displayed when you !inspect it
	str_desc = ""

	# The text displayed when you !adorn it
	str_onadorn = ""

	# The text displayed when you take it off
	str_unadorn = ""

	# The text displayed when it breaks! Oh no!
	str_onbreak = ""

	# How rare the item is, can be "Plebeian", "Patrician", or "Princeps"
	rarity = ""

	# The stats the item increases/decreases
	stats = {}

	# Some items have special abilities that act like less powerful Mutations
	ability = ""

	# While !adorn'd, this item takes damage-- If this reaches 0, it breaks
	durability = 0

	# How much space this item takes up on your person-- You can only wear so many items at a time, the amount is determined by your level
	size = 0

	# What fashion style the cosmetic belongs to: Goth, jock, prep, nerd
	style = ""

	# How fresh a cosmetic is, in other words how fleek, in other words how godDAMN it is, in other words how good it looks
	freshness = 0

	# The ingredients necessary to make this item via it's acquisition method
	ingredients = ""

	# Cost in SlimeCoin to buy this item.
	price = 0

	# Names of the vendors selling this item.
	vendors = []

	#Whether a cosmetic is a hat or not
	is_hat = False

	def __init__(
		self,
		id_cosmetic = "",
		str_name = "",
		str_desc = "",
		str_onadorn = "",
		str_unadorn = "",
		str_onbreak = "",
		rarity = "",
		stats = {},
		ability = "",
		durability = 0,
		size = 0,
		style = "",
		freshness = 0,
		ingredients = "",
		acquisition = "",
		price = 0,
		vendors = [],
		is_hat = False,

	):
		self.item_type = ewcfg.it_cosmetic

		self.id_cosmetic = id_cosmetic
		self.str_name = str_name
		self.str_desc = str_desc
		self.str_onadorn = str_onadorn
		self.str_unadorn = str_unadorn
		self.str_onbreak = str_onbreak
		self.rarity = rarity
		self.stats = stats
		self.ability = ability
		self.durability = durability
		self.size = size
		self.style = style
		self.freshness = freshness
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.price = price
		self.vendors = vendors
		self.is_hat = is_hat

async def adorn(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Check to see if you even have the item you want to repair
	item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

	try:
		item_id_int = int(item_id)
	except:
		item_id_int = None

	if item_id is not None and len(item_id) > 0:
		response = "You don't have one."

		cosmetic_items = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.message.server.id,
			item_type_filter = ewcfg.it_cosmetic
		)

		item_sought = None
		item_from_slimeoid = None
		already_adorned = False
		space_adorned = 0

		# Check all cosmetics found
		for item in cosmetic_items:
			i = EwItem(item.get('id_item'))

			# Search for desired cosmetic
			if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):


				if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
					item_from_slimeoid = i
					continue
				if i.item_props.get("adorned") == 'true':
					already_adorned = True
					item_sought = i
					break
				elif i.item_props.get("context") == 'costume':
					if not ewutils.check_fursuit_active(i.id_server):
						response = "You can't adorn your costume right now."
					else:
						item_sought = i
						break
				else:
					item_sought = i
					break

			# Get space used adorned cosmetics
			if i.item_props['adorned'] == 'true':
				space_adorned += int(i.item_props['size'])

		if item_sought == None:
			item_sought = item_from_slimeoid

		# If the cosmetic you want to adorn is found
		if item_sought != None:

			# Unadorn the cosmetic
			if already_adorned:
				item_sought.item_props['adorned'] = 'false'

				unadorn_response = str(item_sought.item_props['str_unadorn'])

				response = unadorn_response.format(item_sought.item_props['cosmetic_name'])

				user_data.attack -= int(item_sought.item_props[ewcfg.stat_attack])
				user_data.defense -= int(item_sought.item_props[ewcfg.stat_defense])
				user_data.speed -= int(item_sought.item_props[ewcfg.stat_speed])

				item_sought.persist()
				user_data.freshness = ewutils.get_total_freshness(id_user = cmd.message.author.id, id_server = cmd.message.server.id)
				user_data.persist()

			# Attempt to adorn the cosmetic
			else:
				# Calculate how much space you'll have after adorning...
				if int(item_sought.item_props['size']) > 0:
					space_adorned += int(item_sought.item_props['size'])

				# If you don't have enough space, abort
				if space_adorned >= ewutils.max_adornspace_bylevel(user_data.slimelevel):
					response = "You can't adorn anymore cosmetics."

				else:
					item_sought.item_props['adorned'] = 'true'

					user_data.attack += int(item_sought.item_props[ewcfg.stat_attack])
					user_data.defense += int(item_sought.item_props[ewcfg.stat_defense])
					user_data.speed += int(item_sought.item_props[ewcfg.stat_speed])

					if item_sought.item_props.get('slimeoid') == 'true':
						item_sought.item_props['slimeoid'] = 'false'
						response = "You take your {} from your slimeoid and successfully adorn it.".format(item_sought.item_props.get('cosmetic_name'))
					else:
						onadorn_response = item_sought.item_props['str_onadorn']
						response = onadorn_response.format(item_sought.item_props['cosmetic_name'])

					item_sought.persist()
					user_data.freshness = ewutils.get_total_freshness(id_user = cmd.message.author.id, id_server = cmd.message.server.id)
					user_data.persist()

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Adorn which cosmetic? Check your **!inventory**.'))


async def dye(cmd):
	first_id = ewutils.flattenTokenListToString(cmd.tokens[1:2])
	second_id = ewutils.flattenTokenListToString(cmd.tokens[2:])

	try:
		first_id_int = int(first_id)
		second_id_int = int(second_id)
	except:
		first_id_int = None
		second_id_int = None

	if first_id != None and len(first_id) > 0 and second_id != None and len(second_id) > 0:
		response = "You don't have one."

		items = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.message.server.id,
		)

		cosmetic = None
		dye = None
		for item in items:
			if item.get('id_item') in [first_id_int, second_id_int] or first_id in ewutils.flattenTokenListToString(item.get('name')) or second_id in ewutils.flattenTokenListToString(item.get('name')):
				if item.get('item_type') == ewcfg.it_cosmetic and cosmetic is None:
					cosmetic = item

				if item.get('item_type') == ewcfg.it_item and item.get('name') in ewcfg.dye_map and dye is None:
					dye = item	

				if cosmetic != None and dye != None:
					break

		if cosmetic != None:
			if dye != None:
				user_data = EwUser(member = cmd.message.author)

				cosmetic_item = EwItem(id_item=cosmetic.get("id_item"))
				dye_item = EwItem(id_item=dye.get("id_item"))

				hue = ewcfg.hue_map.get(dye_item.item_props.get('id_item'))

				response = "You dye your {} in {} paint!".format(cosmetic_item.item_props.get('cosmetic_name'), hue.str_name)
				cosmetic_item.item_props['hue'] = hue.id_hue

				cosmetic_item.persist()
				ewitem.item_delete(id_item=dye.get('id_item'))
			else:
				response = 'Use which dye? Check your **!inventory**.'
		else:
			response = 'Dye which cosmetic? Check your **!inventory**.'
		
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'You need to specify which cosmetic you want to paint and which dye you want to use! Check your **!inventory**.'))

async def smoke(cmd):
	usermodel = EwUser(member=cmd.message.author)
	#item_sought = ewitem.find_item(item_search="cigarette", id_user=cmd.message.author.id, id_server=usermodel.id_server)
	item_sought = None
	space_adorned = 0
	item_stash = ewitem.inventory(id_user=cmd.message.author.id, id_server=usermodel.id_server)
	for item_piece in item_stash:
		item = EwItem(id_item=item_piece.get('id_item'))
		if item.item_props['adorned'] == 'true':
			space_adorned += int(item.item_props['size'])

		if item_piece.get('item_type') == ewcfg.it_cosmetic and (item.item_props.get('id_cosmetic') == "cigarette" or item.item_props.get('id_cosmetic') == "cigar") and "lit" not in item.item_props.get('cosmetic_desc'):
			item_sought = item_piece


	if item_sought:
		item = EwItem(id_item=item_sought.get('id_item'))
		if item_sought.get('item_type') == ewcfg.it_cosmetic and item.item_props.get('id_cosmetic') == "cigarette":
			if int(item_sought.item_props['size']) > 0:
				space_adorned += int(item_sought.item_props['size'])

			if space_adorned <= ewutils.max_adornspace_bylevel(usermodel.slimelevel):
				response = "You light a cig and bring it to your mouth. So relaxing. So *cool*. All those naysayers and PSAs in Health class can go fuck themselves."
				item.item_props['cosmetic_desc'] = "A single lit cigarette sticking out of your mouth. You huff these things down in seconds but you’re never seen without one. Everyone thinks you’re really, really cool."
				item.item_props['adorned'] = "true"
				item.persist()

				usermodel.attack += int(item_sought.item_props[ewcfg.stat_attack])
				usermodel.defense += int(item_sought.item_props[ewcfg.stat_defense])
				usermodel.speed += int(item_sought.item_props[ewcfg.stat_speed])
				usermodel.freshness = ewutils.get_total_freshness(id_user = cmd.message.author.id, id_server = cmd.message.server.id)

				usermodel.persist()


				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				await asyncio.sleep(60)
				item = EwItem(id_item=item_sought.get('id_item'))

				response = "The cigarette fizzled out."

				item.item_props['cosmetic_desc'] = "It's a cigarette butt. What kind of hoarder holds on to these?"
				item.item_props['adorned'] = "false"
				item.item_props['id_cosmetic'] = "cigarettebutt"
				item.item_props['cosmetic_name'] = "cigarette butt"
				item.persist()

				usermodel.attack -= int(item_sought.item_props[ewcfg.stat_attack])
				usermodel.defense -= int(item_sought.item_props[ewcfg.stat_defense])
				usermodel.speed -= int(item_sought.item_props[ewcfg.stat_speed])
				usermodel.freshness = ewutils.get_total_freshness(id_user = cmd.message.author.id, id_server = cmd.message.server.id)

				usermodel.persist()

			else:
				response = "Sadly, you cannot smoke the cigarette. To smoke it, you'd have to have it inbetween your lips for approximately a minute, which technically counts as adorning something. " \
						   "And, seeing as you are out of adornable cosmetic space, you cannot do that. Sorry. Weird how this message doesn't show up when you suck all that dick though, huh?"

		elif item_sought.get('item_type') == ewcfg.it_cosmetic and item.item_props.get('id_cosmetic') == "cigar":
			if int(item_sought.item_props['size']) > 0:
				space_adorned += int(item_sought.item_props['size'])

			if space_adorned <= ewutils.max_adornspace_bylevel(usermodel.slimelevel):
				response = "You light up your stogie and bring it to your mouth. So relaxing. So *cool*. All those naysayers and PSAs in Health class can go fuck themselves."
				item.item_props['cosmetic_desc'] = "A single lit cigar sticking out of your mouth. These thing take their time to kick in, but it's all worth it to look like a supreme gentleman."
				item.item_props['adorned'] = "true"

				item.persist()

				usermodel.attack += int(item_sought.item_props[ewcfg.stat_attack])
				usermodel.defense += int(item_sought.item_props[ewcfg.stat_defense])
				usermodel.speed += int(item_sought.item_props[ewcfg.stat_speed])
				usermodel.freshness = ewutils.get_total_freshness(id_user = cmd.message.author,
																  id_server = cmd.message.server)

				usermodel.persist()

				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				await asyncio.sleep(300)
				item = EwItem(id_item=item_sought.get('id_item'))

				response = "The cigar fizzled out."

				item.item_props['cosmetic_desc'] = "It's a cigar stump. It's seen better days."
				item.item_props['adorned'] = "false"
				item.item_props['id_cosmetic'] = "cigarstump"
				item.item_props['cosmetic_name'] = "cigar stump"
				item.persist()

				usermodel.attack -= int(item_sought.item_props[ewcfg.stat_attack])
				usermodel.defense -= int(item_sought.item_props[ewcfg.stat_defense])
				usermodel.speed -= int(item_sought.item_props[ewcfg.stat_speed])
				usermodel.freshness = ewutils.get_total_freshness(id_user = cmd.message.author.id, id_server = cmd.message.server.id)

				usermodel.persist()

			else:
				response = "Sadly, you cannot smoke the cigar. To smoke it, you'd have to have it inbetween your lips for approximately a minute, which technically counts as adorning something. " \
						   "And, seeing as you are out of adornable cosmetic space, you cannot do that. Sorry. Weird how this message doesn't show up when you suck all that dick though, huh?"
		else:
			response = "You can't smoke that."
	else:
		response = "There aren't any usable cigarettes or cigars in your inventory."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


def dedorn_all_costumes():
	costumes = ewutils.execute_sql_query("SELECT id_item FROM items_prop WHERE name = 'context' AND value = 'costume' AND id_item IN (SELECT id_item FROM items_prop WHERE (name = 'adorned' OR name = 'slimeoid') AND value = 'true')")
	costume_count = 0

	for costume_id in costumes:
		costume_item = EwItem(id_item=costume_id)

		usermodel = EwUser(id_user = costume_item.id_owner, id_server = costume_item.id_server)
		
		costume_item.item_props['adorned'] = 'false'

		if costume_item.item_props['slimeoid'] == 'false':
			usermodel.attack -= int(costume_item.item_props[ewcfg.stat_attack])
			usermodel.defense -= int(costume_item.item_props[ewcfg.stat_defense])
			usermodel.speed -= int(costume_item.item_props[ewcfg.stat_speed])
			usermodel.freshness = ewutils.get_total_freshness(id_user = costume_item.id_owner, id_server = costume_item.id_server)

			usermodel.persist()

		costume_item.item_props['slimeoid'] = 'false'
		costume_item.persist()
		
		costume_count += 1
		
	ewutils.logMsg("Dedorned {} costumes after full moon ended.".format(costume_count))

async def sew(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Player must be at the Bodega
	if cmd.message.channel.name == ewcfg.channel_bodega:
		item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

		try:
			item_id_int = int(item_id)
		except:
			item_id_int = None

		# Check to see if you even have the item you want to repair
		if item_id != None and len(item_id) > 0:
			response = "You don't have one."

			cosmetic_items = ewitem.inventory(
				id_user = cmd.message.author.id,
				id_server = cmd.message.server.id,
				item_type_filter = ewcfg.it_cosmetic
			)

			item_sought = None
			item_from_slimeoid = None

			for item in cosmetic_items:
				if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
					i = EwItem(item.get('id_item'))

					if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
						item_from_slimeoid = i
						continue
					else:
						item_sought = i
						break

			if item_sought == None:
				item_sought = item_from_slimeoid

			# If the cosmetic you want to have repaired is found
			if item_sought != None:
				# Can't repair scalps because we don't know what the original durability limit was
				if item_sought.item_props['id_cosmetic'] == 'scalp':
					response = "What the hell is this? I'm not gonna repair some dude's fucking scalp, are you retarded?"

				# Can't repair items without durability limits, since they couldn't have been damaged in the first place
				elif item_sought.item_props['durability'] is None:
					response = "I'm sorry, but I can't repair that piece of clothing!"

				else:
					cosmetic_name = item_sought.item_props['cosmetic_name']

					original_durability = int(ewcfg.cosmetic_map.get(item_sought.item_props['id_cosmetic']))
					current_durability = int(item_sought.item_props['durability'])

					# If the cosmetic is actually damaged at all
					if current_durability < original_durability:
						difference = abs(current_durability - original_durability)

						cost_ofrepair = difference * 4 # NO ONE SAID IT WOULD BE EASY

						if cost_ofrepair > user_data.slimes:
							response = "Get out of here! Scram, weirdo! It costs {} to repair that cosmetic, which you don't have! Die! Die! Fucking Die!".format(cost_ofrepair)
						else:
							response = "It costs {} to repair this. Are you sure you wanna?".format(cost_ofrepair)
							response += "\n**!accept** or **!refuse** the deal."

							await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

							# Wait for an answer
							accepted = False

							try:
								message = await cmd.client.wait_for_message(timeout = 20, author = cmd.message.author, check = ewutils.check_accept_or_refuse)

								if message != None:
									if message.content.lower() == "!accept":
										accepted = True
									if message.content.lower() == "!refuse":
										accepted = False
							except:
								accepted = False

							# Cancel deal if the hat is no longer in user's inventory
							if item_sought.id_owner != user_data.id_user:
								accepted = False

							# Cancel deal if the user has left Krak Bay
							if user_data.poi != ewcfg.poi_id_krakbay:
								accepted = False

							if accepted == True:
								user_data.slimes -= cost_ofrepair
								user_data.persist()

								item_sought.item_props['durability'] = original_durability
								item_sought.persist()

								response = '"Pleasure doing business with you, laddy!"'

							else:
								response = '"Ok, sure, whatever. No, I dont care. No, yeah. sure."'
					else:
						response = "What're you talking about? This looks fine to me!"
		else:
			response = "Sew which cosmetic? Check your **!inventory**."
	else:
		response = "Heh, yeah right. What kind of self-respecting juvenile delinquent knows how to sew? Sewing totally lame, everyone knows that! Even people who sew know that! Looks like you’re gonna have to find some nerd to do it for you."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def retrofit(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Player must be at the Bodega
	if cmd.message.channel.name == ewcfg.channel_bodega:
		item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

		try:
			item_id_int = int(item_id)
		except:
			item_id_int = None

		# Check to see if you even have the item you want to retrofit
		if item_id != None and len(item_id) > 0:
			response = "You don't have one."

			cosmetic_items = ewitem.inventory(
				id_user = cmd.message.author.id,
				id_server = cmd.message.server.id,
				item_type_filter = ewcfg.it_cosmetic
			)

			item_sought = None
			item_from_slimeoid = None

			for item in cosmetic_items:
				if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
					i = EwItem(item.get('id_item'))

					if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
						item_from_slimeoid = i
						continue
					else:
						item_sought = i
						break

			if item_sought == None:
				item_sought = item_from_slimeoid

			# If the cosmetic you want to have repaired is found
			if item_sought != None:
				# Can't retrofit scalps because we just can't, okay?
				if item_sought.item_props['id_cosmetic'] == 'scalp':
					response = "What the hell is this? I'm not gonna retrofit some dude's fucking scalp, are you retarded?"

				else:
					desired_item = ewcfg.cosmetic_map.get(item_sought.item_props['id_cosmetic'])

					desired_item_stats = {
						ewcfg.stat_attack: desired_item.stats[ewcfg.stat_attack],
						ewcfg.stat_defense: desired_item.stats[ewcfg.stat_defense],
						ewcfg.stat_speed: desired_item.stats[ewcfg.stat_speed],
					}

					current_item_stats = {
						ewcfg.stat_attack: item_sought.item_props[ewcfg.stat_attack],
						ewcfg.stat_defense: item_sought.item_props[ewcfg.stat_defense],
						ewcfg.stat_speed: item_sought.item_props[ewcfg.stat_speed],
					}

					# If the cosmetic is actually damaged at all
					if current_item_stats != desired_item_stats:
						cost_ofretrofit = desired_item.price if desired_item.price else 50000

						if cost_ofretrofit > user_data.slimes:
							response = "Get out of here! Scram, weirdo! It costs {} to retrofit that cosmetic, which you don't have! Die! Die! Fucking Die!".format(cost_ofretrofit)
						else:
							response = "It costs {} to repair this. Are you sure you wanna?".format(cost_ofretrofit)
							response += "\n**!accept** or **!refuse** the deal."

							await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

							# Wait for an answer
							accepted = False

							try:
								message = await cmd.client.wait_for_message(timeout = 20, author = cmd.message.author, check = ewutils.check_accept_or_refuse)

								if message != None:
									if message.content.lower() == "!accept":
										accepted = True
									if message.content.lower() == "!refuse":
										accepted = False
							except:
								accepted = False

							# Cancel deal if the hat is no longer in user's inventory
							if item_sought.id_owner != user_data.id_user:
								accepted = False

							# Cancel deal if the user has left Krak Bay
							if user_data.poi != ewcfg.poi_id_krakbay:
								accepted = False

							if accepted == True:
								user_data.slimes -= cost_ofretrofit
								user_data.persist()

								item_sought.item_props[ewcfg.stat_attack] = desired_item.stats[ewcfg.stat_attack]
								item_sought.item_props[ewcfg.stat_defense] = desired_item.stats[ewcfg.stat_defense]
								item_sought.item_props[ewcfg.stat_speed] = desired_item.stats[ewcfg.stat_speed]
								item_sought.persist()

								response = '"Pleasure doing business with you, laddy!"'

							else:
								response = '"Ok, sure, whatever. No, I dont care. No, yeah. sure."'
					else:
						response = "What're you talking about? This looks fine to me!"
		else:
			response = "Sew which cosmetic? Check your **!inventory**."
	else:
		response = "Heh, yeah right. What kind of self-respecting juvenile delinquent knows how to sew? Sewing totally lame, everyone knows that! Even people who sew know that! Looks like you’re gonna have to find some nerd to do it for you."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def sip(cmd):
	user_data = EwUser(member = cmd.message.author)
	cosmetic_abilites = ewutils.get_cosmetic_abilities(id_user = cmd.message.author.id, id_server = cmd.message.server.id)

	if ewcfg.cosmeticAbility_id_drinkable in cosmetic_abilites:
		hunger_restored = 5
		user_data.hunger -= hunger_restored
		if user_data.hunger < 0:
			user_data.hunger = 0
		response = "You take a sip from your FUCK ENERGY™ novelty baseball helmet! TASTY!"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))