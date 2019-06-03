import random
import asyncio
import time

import ewcfg
import ewutils
import ewitem
import ewrolemgr
import ewstats
import ewmap
import ewslimeoid
from ew import EwUser
from ewmarket import EwMarket
from ewitem import EwItem
from ewslimeoid import EwSlimeoid

""" class to send general data about an interaction to a command """
class EwCmd:
	cmd = ""
	tokens = []
	tokens_count = 0
	message = None
	client = None
	mentions = []
	mentions_count = 0

	def __init__(
		self,
		tokens = [],
		message = None,
		client = None,
		mentions = []
	):
		self.tokens = tokens
		self.message = message
		self.client = client
		self.mentions = mentions
		self.mentions_count = len(mentions)

		if len(tokens) >= 1:
			self.tokens_count = len(tokens)
			self.cmd = tokens[0]

""" Send an initial message you intend to edit later while processing the command. Returns handle to the message. """
async def start(cmd = None, message = '...', channel = None, client = None):
	if cmd != None:
		channel = cmd.message.channel
		client = cmd.client

	if client != None and channel != None:
		return await ewutils.send_message(client, channel, message)

	return None

""" pure flavor command, howls """
async def cmd_howl(cmd):
	user_data = EwUser(member = cmd.message.author)
	slimeoid = EwSlimeoid(member = cmd.message.author)
	response = ewcfg.howls[random.randrange(len(ewcfg.howls))]

	if (slimeoid.life_state == ewcfg.slimeoid_state_active) and (user_data.life_state != ewcfg.life_state_corpse):
		response += "\n{} howls along with you! {}".format(str(slimeoid.name), ewcfg.howls[random.randrange(len(ewcfg.howls))])

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

""" returns true if it's night time and the casino is open, else false. """
def is_casino_open(t):
	if t < 18 and t >= 6:
		return False

	return True

def gen_score_text(
	id_user = None,
	id_server = None,
	display_name = None
):
	response = ""

	user_data = EwUser(
		id_user = id_user,
		id_server = id_server
	)
	poudrins = ewitem.inventory(
		id_user = id_user,
		id_server = id_server,
		item_type_filter = ewcfg.it_slimepoudrin
	)
	poudrins_count = len(poudrins)

	if user_data.life_state == ewcfg.life_state_grandfoe:
		# Can't see a raid boss's slime score.
		response = "{}'s power is beyond your understanding.".format(display_name)
	else:
		# return somebody's score
		response = "{} currently has {:,} slime{}.".format(display_name, user_data.slimes, (" and {} slime poudrin{}".format(poudrins_count, ("" if poudrins_count == 1 else "s")) if poudrins_count > 0 else ""))

	return response

""" show player's slime score """
async def score(cmd):
	response = ""
	user_data = None
	member = None

	if cmd.mentions_count == 0:
		user_data = EwUser(member = cmd.message.author)
		poudrins = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.message.server.id,
			item_type_filter = ewcfg.it_slimepoudrin
		)
		poudrins_count = len(poudrins)

		# return my score
		response = "You currently have {:,} slime{}.".format(user_data.slimes, (" and {} slime poudrin{}".format(poudrins_count, ("" if poudrins_count == 1 else "s")) if poudrins_count > 0 else ""))

	else:
		member = cmd.mentions[0]
		response = gen_score_text(
			id_user = member.id,
			id_server = member.server.id,
			display_name = member.display_name
		)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
	if member != None:
		await ewrolemgr.updateRoles(client = cmd.client, member = member)

def gen_data_text(
	id_user = None,
	id_server = None,
	display_name = None
):
	response = ""
	user_data = EwUser(
		id_user = id_user,
		id_server = id_server
	)
	slimeoid = EwSlimeoid(id_user = id_user, id_server = id_server)

	cosmetics = ewitem.inventory(
		id_user = user_data.id_user,
		id_server = user_data.id_server,
		item_type_filter = ewcfg.it_cosmetic
	)
	adorned_cosmetics = []
	for cosmetic in cosmetics:
		cos = EwItem(id_item = cosmetic.get('id_item'))
		if cos.item_props['adorned'] == 'true':
			adorned_cosmetics.append(cosmetic.get('name'))

	if user_data.life_state == ewcfg.life_state_grandfoe:
		poi = ewcfg.id_to_poi.get(user_data.poi)
		if poi != None:
			response = "{} is {} {}.".format(display_name, poi.str_in, poi.str_name)
		else:
			response = "You can't discern anything useful about {}.".format(display_name)
	else:

		# return somebody's score
		if user_data.life_state == ewcfg.life_state_corpse:
			response = "{} is a level {} deadboi.".format(display_name, user_data.slimelevel)
		else:
			response = "{} is a level {} slimeboi.".format(display_name, user_data.slimelevel)

		coinbounty = int(user_data.bounty / ewcfg.slimecoin_exchangerate)

		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

		if weapon != None:
			response += " {} {}{}.".format(ewcfg.str_weapon_married if user_data.weaponmarried == True else ewcfg.str_weapon_wielding, ("" if len(weapon_item.item_props.get("weapon_name")) == 0 else "{}, ".format(weapon_item.item_props.get("weapon_name"))), weapon.str_weapon)
			if user_data.weaponskill >= 5:
				response += " {}".format(weapon.str_weaponmaster.format(rank = (user_data.weaponskill - 4)))

		trauma = ewcfg.weapon_map.get(user_data.trauma)
		if trauma != None:
			response += " {}".format(trauma.str_trauma)

		user_kills = ewstats.get_stat(user = user_data, metric = ewcfg.stat_kills)
		if user_kills > 0:
			response += " They have {:,} confirmed kills.".format(user_kills)

		if coinbounty != 0:
			response += " SlimeCorp offers a bounty of {:,} SlimeCoin for their death.".format(coinbounty)

		if len(adorned_cosmetics) > 0:
			response += " They have a {} adorned.".format(ewutils.formatNiceList(adorned_cosmetics, 'and'))

		if (slimeoid.life_state == ewcfg.slimeoid_state_active) and (user_data.life_state != ewcfg.life_state_corpse):
			response += " They are accompanied by {}, a {}-foot-tall Slimeoid.".format(slimeoid.name, str(slimeoid.level))

	return response

""" show player information and description """
async def data(cmd):
	response = ""
	user_data = None
	member = None

	if cmd.mentions_count == 0:
		user_data = EwUser(member = cmd.message.author)
		slimeoid = EwSlimeoid(member = cmd.message.author)

		cosmetics = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.message.server.id,
			item_type_filter = ewcfg.it_cosmetic
		)
		adorned_cosmetics = []
		for cosmetic in cosmetics:
			cos = EwItem(id_item = cosmetic.get('id_item'))
			if cos.item_props['adorned'] == 'true':
				adorned_cosmetics.append(cosmetic.get('name'))

		poi = ewcfg.id_to_poi.get(user_data.poi)
		if poi != None:
			response = "You find yourself {} {}. ".format(poi.str_in, poi.str_name)

		# return my data
		if user_data.life_state == ewcfg.life_state_corpse:
			response += "You are a level {} deadboi.".format(user_data.slimelevel)
		else:
			response += "You are a level {} slimeboi.".format(user_data.slimelevel)

		coinbounty = int(user_data.bounty / ewcfg.slimecoin_exchangerate)

		weapon_item = EwItem(id_item = user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

		if weapon != None:
			response += " {} {}{}.".format(ewcfg.str_weapon_married_self if user_data.weaponmarried == True else ewcfg.str_weapon_wielding_self, ("" if len(weapon_item.item_props.get("weapon_name")) == 0 else "{}, ".format(weapon_item.item_props.get("weapon_name"))), weapon.str_weapon)
			if user_data.weaponskill >= 5:
				response += " {}".format(weapon.str_weaponmaster_self.format(rank = (user_data.weaponskill - 4)))

		trauma = ewcfg.weapon_map.get(user_data.trauma)
		if trauma != None:
			response += " {}".format(trauma.str_trauma_self)

		user_kills = ewstats.get_stat(user = user_data, metric = ewcfg.stat_kills)
		if user_kills > 0:
			response += " You have {:,} confirmed kills.".format(user_kills)

		if coinbounty != 0:
			response += " SlimeCorp offers a bounty of {:,} SlimeCoin for your death.".format(coinbounty)

		if len(adorned_cosmetics) > 0:
			response += " You have a {} adorned.".format(ewutils.formatNiceList(adorned_cosmetics, 'and'))

		if user_data.hunger > 0:
			response += " You are {}% hungry.".format(
				round(user_data.hunger * 100.0 / ewutils.hunger_max_bylevel(user_data.slimelevel), 1)
			)

		if user_data.ghostbust:
			response += " The coleslaw in your stomach enables you to bust ghosts."

		if user_data.busted and user_data.life_state == ewcfg.life_state_corpse:
			response += " You are busted and therefore cannot leave the sewers without reviving."

		if (slimeoid.life_state == ewcfg.slimeoid_state_active) and (user_data.life_state != ewcfg.life_state_corpse):
			response += " You are accompanied by {}, a {}-foot-tall Slimeoid.".format(slimeoid.name, str(slimeoid.level))

		response += "\n\nhttps://ew.krakissi.net/stats/player.html?pl={}".format(user_data.id_user)

	else:
		member = cmd.mentions[0]
		response = gen_data_text(
			id_user = member.id,
			id_server = member.server.id,
			display_name = member.display_name
		)

		response += "\n\nhttps://ew.krakissi.net/stats/player.html?pl={}".format(member.id)


	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
	if member != None:
		await ewrolemgr.updateRoles(client = cmd.client, member = member)

def weather_txt(id_server):
	response = ""
	market_data = EwMarket(id_server = id_server)
	time_current = market_data.clock
	displaytime = str(time_current)
	ampm = ''

	if time_current <= 12:
		ampm = 'AM'
	if time_current > 12:
		displaytime = str(time_current - 12)
		ampm = 'PM'

	if time_current == 0:
		displaytime = 'midnight'
		ampm = ''
	if time_current == 12:
		displaytime = 'high noon'
		ampm = ''

	flair = ''
	weather_data = ewcfg.weather_map.get(market_data.weather)
	if weather_data != None:
		if time_current >= 6 and time_current <= 7:
			flair = weather_data.str_sunrise
		if time_current >= 8 and time_current <= 17:
			flair = weather_data.str_day
		if time_current >= 18 and time_current <= 19:
			flair = weather_data.str_sunset
		if time_current >= 20 or time_current <= 5:
			flair = weather_data.str_night

	response += "It is currently {}{} in NLACakaNM.{}".format(displaytime, ampm, (' ' + flair))
	return response

""" time and weather information """
async def weather(cmd):
	response = weather_txt(cmd.message.server.id)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


"""
	Harvest is not and has never been a command.
"""
async def harvest(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, '**HARVEST IS NOT A COMMAND YOU FUCKING IDIOT**'))

"""
	Salute the NLACakaNM flag.
"""
async def salute(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'https://ew.krakissi.net/img/nlacakanm_flag.gif'))

"""
	Burn the NLACakaNM flag.
"""
async def unsalute(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'https://ew.krakissi.net/img/nlacakanm_flag_burning.gif'))
"""
	Burn the NLACakaNM flag.
"""
async def hurl(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'https://ew.krakissi.net/img/tfaaap-hurl.gif'))


"""
	Rowdys THRASH
"""
async def thrash(cmd):
	user_data = EwUser(member = cmd.message.author)

	if (user_data.life_state == ewcfg.life_state_enlisted or user_data.life_state == ewcfg.life_state_kingpin) and user_data.faction == ewcfg.faction_rowdys:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_rf + ewcfg.emote_slime3 + ewcfg.emote_slime1 + ewcfg.emote_slime3 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_slime1 + ewcfg.emote_slime1 + ewcfg.emote_slime3 + ewcfg.emote_slime1 + ewcfg.emote_rf + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_slime3 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + '\n' + ewcfg.emote_rowdyfucker + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_slime3 + ewcfg.emote_slime1 + ewcfg.emote_slime3 + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_slime3 + ewcfg.emote_slime1 + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rowdyfucker + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_slime3 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_slime3 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_rf + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_slime1 + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf + ewcfg.emote_rf))

"""
	Killers DAB
"""
async def dab(cmd):
	user_data = EwUser(member = cmd.message.author)

	if (user_data.life_state == ewcfg.life_state_enlisted or user_data.life_state == ewcfg.life_state_kingpin) and user_data.faction == ewcfg.faction_killers:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, '\n'  + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_slime1 + ewcfg.emote_slime3 + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime1 + ewcfg.emote_ck + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime1 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + '\n' + ewcfg.emote_copkiller  + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime1 + ewcfg.emote_slime1 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_copkiller + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime1 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_ck + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_ck + ewcfg.emote_slime3 + ewcfg.emote_slime1 + ewcfg.emote_slime1 + ewcfg.emote_slime3 + ewcfg.emote_ck + ewcfg.emote_slime1 + ewcfg.emote_ck + ewcfg.emote_ck + ewcfg.emote_slime1 + ewcfg.emote_ck))

"""
	advertise patch notes
"""
async def patchnotes(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Look for the latest patchnotes on the news page: https://ew.krakissi.net/news/'))

"""
	advertise help services
"""
async def help(cmd):
	response = ""
	topic = None
	user_data = EwUser(member = cmd.message.author)

	# help only checks for districts while in game channels
	if ewmap.channel_name_is_poi(cmd.message.channel.name) == False:
		response = 'Check out the guide for help: https://ew.krakissi.net/guide/' + ' \n' + 'You can also visit N.L.A.C.U. (!goto uni) or Neo Milwaukee State (!goto nms) to get more in-depth descriptions about how various game mechanics work.'
	else:
		# checks if user is in a college
		if user_data.poi == ewcfg.poi_id_neomilwaukeestate or user_data.poi == ewcfg.poi_id_nlacu:
			if not len(cmd.tokens) > 1:
				# list off help topics to player at college
				response = 'What would you like to learn about? Topics include: \n' \
						   '**mining**, **food**, **capturing**, **dojo**, **bleeding**, **scavenging**,\n' \
						   '**farming**, **slimeoids**, **transportation**, **scouting**, and **offline**.'
			else:
				topic = ewutils.flattenTokenListToString(cmd.tokens[1:])
				if topic in ewcfg.help_responses:
					response = ewcfg.help_responses[topic]
				else:
					response = 'ENDLESS WAR questions your belief in the existence of such a topic.'
		else:
			# user not in college, check what help message would apply to the subzone they are in

			# poi variable assignment used for checking if player is in a vendor subzone or not
			poi = ewcfg.id_to_poi.get(user_data.poi)

			if user_data.poi in [ewcfg.poi_id_mine, ewcfg.poi_id_cv_mines, ewcfg.poi_id_tt_mines]:
				# mine help
				response = ewcfg.help_responses['mining']
			elif (len(poi.vendors) >= 1):
				response = ewcfg.help_responses['food']
				# food help
			elif user_data.poi in ewcfg.poi_id_dojo:
				# dojo help
				response = ewcfg.help_responses['dojo']
			elif user_data.poi in [ewcfg.poi_id_jr_farms, ewcfg.poi_id_og_farms, ewcfg.poi_id_ab_farms]:
				# farming help
				response = ewcfg.help_responses['farming']
			elif user_data.poi in ewcfg.poi_id_slimeoidlab:
				# slimeoid help (somewhat redundant, but may help by pointing player towards !instructions)
				response = ewcfg.help_responses['slimeoids']
			elif user_data.poi in ewcfg.transport_stops:
				# transportation help
				response =  ewcfg.help_responses['transportation']
			else:
				# catch-all response for when user isn't in a sub-zone with a help response
				response = 'Check out the guide for help: https://ew.krakissi.net/guide/' + ' \n' + 'You can also visit N.L.A.C.U. (!goto uni) or Neo Milwaukee State (!goto nms) to get more in-depth descriptions about how various game mechanics work.'

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


"""
	Link to the world map.
"""
async def map(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Online world map: https://ew.krakissi.net/map/'))

"""
	Link to the RFCK wiki.
"""
async def wiki(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Rowdy Fuckers Cop Killers Wiki: https://rfck.miraheze.org/wiki/Main_Page'))

"""
	Link to the fan art booru.
"""
async def booru(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Rowdy Fuckers Cop Killers Booru: http://rfck.booru.org/'))

"""
	Link to the leaderboards on ew.krakissi.net.
"""
async def leaderboard(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Live leaderboards: https://ew.krakissi.net/stats/'))

""" Accept a russian roulette challenge """
async def accept(cmd):
	user = EwUser(member = cmd.message.author)
	if(user.rr_challenger != ""):
		challenger = EwUser(id_user = user.rr_challenger, id_server = user.id_server)
		if(user.rr_challenger != user.id_user and challenger.rr_challenger != user.id_user):
			challenger.rr_challenger = user.id_user
			challenger.persist()
			if cmd.message.channel.name == ewcfg.channel_arena and ewslimeoid.active_slimeoidbattles.get(cmd.message.author.id):
				response = "You accept the challenge! Both of your Slimeoids ready themselves for combat!"
			elif cmd.message.channel.name == ewcfg.channel_casino:
				response = "You accept the challenge! Both of you head out back behind the casino and load a bullet into the gun."
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" Refuse a russian roulette challenge """
async def refuse(cmd):
	user = EwUser(member = cmd.message.author)

	if(user.rr_challenger != ""):
		challenger = EwUser(id_user = user.rr_challenger, id_server = user.id_server)

		user.rr_challenger = ""
		user.persist()

		if(user.rr_challenger != user.id_user and challenger.rr_challenger != user.id_user):
			response = "You refuse the challenge, but not before leaving a large puddle of urine beneath you."
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		else:
			challenger.rr_challenger = ""
			challenger.persist()

async def slimeoidbattle(cmd):

	if cmd.message.channel.name != ewcfg.channel_arena:
		#Only at the casino
		response = "You can only have Slimeoid Battles at the Battle Arena."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.mentions_count != 1:
		#Must mention only one player
		response = "Mention the player you want to challenge."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	author = cmd.message.author
	member = cmd.mentions[0]

	if author.id == member.id:
		response = "You can't challenge yourself, dumbass."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

	challenger = EwUser(member = author)
	challenger_slimeoid = EwSlimeoid(member = author)
	challengee = EwUser(member = member)
	challengee_slimeoid = EwSlimeoid(member = member)

	challenger.rr_challenger = ""
	challengee.rr_challenger = ""

	#Players have been challenged
	if challenger.rr_challenger != "":
		response = "You are already in the middle of a challenge."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

	if challengee.rr_challenger != "":
		response = "{} is already in the middle of a challenge.".format(member.display_name).replace("@", "\{at\}")
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

	if challenger.poi != challengee.poi:
		#Challangee must be in the casino
		response = "Both players must be in the Battle Arena."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

	if challenger_slimeoid.life_state != ewcfg.slimeoid_state_active:
		response = "You do not have a Slimeoid ready to battle with!"

	if challengee_slimeoid.life_state != ewcfg.slimeoid_state_active:
		response = "{} does not have a Slimeoid ready to battle with!".format(member.display_name)

	time_now = int(time.time())

	if (time_now - challenger_slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
			response = "Your Slimeoid is still recovering from its last defeat!"
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

	if (time_now - challengee_slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
			response = "{}'s Slimeoid is still recovering from its last defeat!".format(member.display_name)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

	#Players have to be enlisted
	if challenger.life_state == ewcfg.life_state_corpse or challengee.life_state == ewcfg.life_state_corpse:
		if challenger.life_state == ewcfg.life_state_corpse:
			response = "Your Slimeoid won't battle for you while you're dead.".format(author.display_name).replace("@", "\{at\}")
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

		elif challengee.life_state == ewcfg.life_state_corpse:
			response = "{}'s Slimeoid won't battle for them while they're dead.".format(member.display_name).replace("@", "\{at\}")
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))

	#Assign a challenger so players can't be challenged
	challenger.rr_challenger = challenger.id_user
	challengee.rr_challenger = challenger.id_user

	challenger.persist()
	challengee.persist()

	response = "You have been challenged by {} to a Slimeoid Battle. Do you !accept or !refuse?".format(author.display_name).replace("@", "\{at\}")
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(member, response))

	#Wait for an answer
	accepted = 0
	try:
		msg = await cmd.client.wait_for_message(timeout = 30, author = member, check = check)

		if msg != None:
			if msg.content == "!accept":
				accepted = 1
	except:
		accepted = 0

	# Clear challenger field.
	challenger = EwUser(member = author)
	challengee = EwUser(member = member)

	challenger.rr_challenger = ""
	challengee.rr_challenger = ""

	challenger.persist()
	challengee.persist()

	#Start game
	if accepted == 1:
		s1name = str(challengee_slimeoid.name)
		s1weapon = ewcfg.offense_map.get(challengee_slimeoid.weapon)
		s1armor = ewcfg.defense_map.get(challengee_slimeoid.armor)
		s1special = ewcfg.special_map.get(challengee_slimeoid.special)
		s1legs = ewcfg.mobility_map.get(challengee_slimeoid.legs)
		s1brain = ewcfg.brain_map.get(challengee_slimeoid.ai)
		s1moxie = challengee_slimeoid.atk + 1
		s1grit = challengee_slimeoid.defense + 1
		s1chutzpah = challengee_slimeoid.intel + 1

		s2name = str(challenger_slimeoid.name)
		s2weapon = ewcfg.offense_map.get(challenger_slimeoid.weapon)
		s2armor = ewcfg.defense_map.get(challenger_slimeoid.armor)
		s2special = ewcfg.special_map.get(challenger_slimeoid.special)
		s2legs = ewcfg.mobility_map.get(challenger_slimeoid.legs)
		s2brain = ewcfg.brain_map.get(challenger_slimeoid.ai)
		s2moxie = challenger_slimeoid.atk + 1
		s2grit = challenger_slimeoid.defense + 1
		s2chutzpah = challenger_slimeoid.intel + 1

		challenger_resistance = ""
		challengee_resistance = ""
		challenger_weakness = ""
		challengee_weakness = ""

		#challengee resistance/weakness
		if challengee_slimeoid.armor == 'scales':
			if challenger_slimeoid.weapon == 'electricity':
				s2moxie -= 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_resistance = " {}'s scales conduct the electricity away from its vitals!".format(challengee_slimeoid.name)
			if challenger_slimeoid.special == 'TK':
				s2chutzpah += 2
				challengee_weakness = " {}'s scales refract and amplify the disrupting brainwaves inside its skull!".format(challengee_slimeoid.name)
		if challengee_slimeoid.armor == 'boneplates':
			if challenger_slimeoid.weapon == 'blades':
				s2moxie -= 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_resistance = " {}'s bone plates block the worst of the damage!".format(challengee_slimeoid.name)
			if challenger_slimeoid.special == 'spines':
				s2chutzpah += 2
				challengee_weakness = " {}'s bone plates only drive the quills deeper into its body as it moves!".format(challengee_slimeoid.name)
		if challengee_slimeoid.armor == 'formless':
			if challenger_slimeoid.weapon == 'bludgeon':
				s2moxie -= 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_resistance = " {}'s squishy body easily absorbs the blows!".format(challengee_slimeoid.name)
			if challenger_slimeoid.special == 'webs':
				s2chutzpah += 2
				challengee_weakness = " {}'s squishy body easily adheres to and becomes entangled by the webs!".format(challengee_slimeoid.name)
		if challengee_slimeoid.armor == 'regeneration':
			if challenger_slimeoid.weapon == 'spikes':
				s2moxie -= 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_resistance = " {} quickly begins regenerating the small puncture wounds inflicted by the spikes!".format(challengee_slimeoid.name)
			if challenger_slimeoid.special == 'spit':
				s2chutzpah += 2
				challengee_weakness = " {}'s regeneration is impeded by the corrosive chemicals!".format(challengee_slimeoid.name)
		if challengee_slimeoid.armor == 'stench':
			if challenger_slimeoid.weapon == 'teeth':
				s2moxie -= 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_resistance = " {}'s noxious fumes make its opponent hesitant to put its mouth anywhere near it!".format(challengee_slimeoid.name)
			if challenger_slimeoid.special == 'throw':
				s2chutzpah += 2
				challengee_weakness = " {}'s foul odor gives away its position, making it easy to target with thrown projectiles!".format(challengee_slimeoid.name)
		if challengee_slimeoid.armor == 'oil':
			if challenger_slimeoid.weapon == 'grip':
				s2moxie -= 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_resistance = " {}'s slippery coating makes it extremely difficult to grab on to!".format(challengee_slimeoid.name)
			if challenger_slimeoid.special == 'fire':
				s2chutzpah += 2
				challengee_weakness = " {}'s oily coating is flammable, igniting as it contacts the flame!".format(challengee_slimeoid.name)
		if challengee_slimeoid.armor == 'quantumfield':
			if challenger_slimeoid.weapon == 'slam':
				s2moxie -= 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_resistance = " {}'s quantum superposition makes it difficult to hit head-on!".format(challengee_slimeoid.name)
			if challenger_slimeoid.special == 'laser':
				s2chutzpah += 2
				challengee_weakness = " {}'s quantum particles are excited by the high-frequency radiation, destabilizing its structure!".format(challengee_slimeoid.name)

		#challenger resistance/weakness
		if challenger_slimeoid.armor == 'scales':
			if challengee_slimeoid.weapon == 'electricity':
				s1moxie -= 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_resistance = " {}'s scales conduct the electricity away from its vitals!".format(challenger_slimeoid.name)
			if challengee_slimeoid.special == 'TK':
				s1chutzpah += 2
				challenger_weakness = " {}'s scales refract and amplify the disrupting brainwaves inside its skull!".format(challenger_slimeoid.name)
		if challenger_slimeoid.armor == 'boneplates':
			if challengee_slimeoid.weapon == 'blades':
				s1moxie -= 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_resistance = " {}'s bone plates block the worst of the damage!".format(challenger_slimeoid.name)
			if challengee_slimeoid.special == 'spines':
				s1chutzpah += 2
				challenger_weakness = " {}'s bone plates only drive the quills deeper into its body as it moves!".format(challenger_slimeoid.name)
		if challenger_slimeoid.armor == 'formless':
			if challengee_slimeoid.weapon == 'bludgeon':
				s1moxie -= 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_resistance = " {}'s squishy body easily absorbs the blows!".format(challenger_slimeoid.name)
			if challengee_slimeoid.special == 'webs':
				s1chutzpah += 2
				challenger_weakness = " {}'s squishy body easily adheres to and becomes entangled by the webs!".format(challenger_slimeoid.name)
		if challenger_slimeoid.armor == 'regeneration':
			if challengee_slimeoid.weapon == 'spikes':
				s1moxie -= 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_resistance = " {} quickly begins regenerating the small puncture wounds inflicted by the spikes!".format(challenger_slimeoid.name)
			if challengee_slimeoid.special == 'spit':
				s1chutzpah += 2
				challenger_weakness = " {}'s regeneration is impeded by the corrosive chemicals!".format(challenger_slimeoid.name)
		if challenger_slimeoid.armor == 'stench':
			if challengee_slimeoid.weapon == 'teeth':
				s1moxie -= 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_resistance = " {}'s noxious fumes make its opponent hesitant to put its mouth anywhere near it!".format(challenger_slimeoid.name)
			if challengee_slimeoid.special == 'throw':
				s1chutzpah += 2
				challenger_weakness = " {}'s foul odor gives away its position, making it easy to target with thrown projectiles!".format(challenger_slimeoid.name)
		if challenger_slimeoid.armor == 'oil':
			if challengee_slimeoid.weapon == 'grip':
				s1moxie -= 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_resistance = " {}'s slippery coating makes it extremely difficult to grab on to!".format(challenger_slimeoid.name)
			if challengee_slimeoid.special == 'fire':
				s1chutzpah += 2
				challenger_weakness = " {}'s oily coating is flammable, igniting as it contacts the flame!".format(challenger_slimeoid.name)
		if challenger_slimeoid.armor == 'quantumfield':
			if challengee_slimeoid.weapon == 'slam':
				s1moxie -= 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_resistance = " {}'s quantum superposition makes it difficult to hit head-on!".format(challenger_slimeoid.name)
			if challengee_slimeoid.special == 'laser':
				s1chutzpah += 2
				challenger_weakness = " {}'s quantum particles are excited by the high-frequency radiation, destabilizing its structure!".format(challenger_slimeoid.name)

		challenger_splitcomplementary = ""
		challenger_analogous = ""
		challengee_splitcomplementary = ""
		challengee_analogous = ""

	#challengee hue supereffectiveness/notveryeffectiveness
		if challengee_slimeoid.hue == None:
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
		if challengee_slimeoid.hue == 'red':
			if challenger_slimeoid.hue == 'pink':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'orange':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'pink':
			if challenger_slimeoid.hue == 'magenta':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'red':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'cyan':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'magenta':
			if challenger_slimeoid.hue == 'purple':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'pink':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'purple':
			if challenger_slimeoid.hue == 'blue':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'violet':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'green':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'yellow':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'blue':
			if challenger_slimeoid.hue == 'cobalt':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'purple':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'orange':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'cobalt':
			if challenger_slimeoid.hue == 'cyan':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'yellow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'red':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'cyan':
			if challenger_slimeoid.hue == 'teal':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'orange':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'teal':
			if challenger_slimeoid.hue == 'green':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'red':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'magenta':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'green':
			if challenger_slimeoid.hue == 'lime':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'pink':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'purple':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'lime':
			if challenger_slimeoid.hue == 'yellow':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'green':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'magenta':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'yellow':
			if challenger_slimeoid.hue == 'orange':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
		if challengee_slimeoid.hue == 'orange':
			if challenger_slimeoid.hue == 'red':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'yellow':
				s2grit += 2
				if s2grit <= 1:
					s2grit = 1
				challengee_analogous = "It's not very effective against {}...".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'cyan':
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s2moxie += 2
				if s2moxie <= 1:
					s2moxie = 1
				s2chutzpah += 2
				if s2chutzpah <= 1:
					s2chutzpah = 1
				challengee_splitcomplementary = "It's Super Effective against {}!".format(challengee_slimeoid.name)

		#chalenger hue supereffectiveness/notveryeffectiveness
		if challenger_slimeoid.hue == None:
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
		if challenger_slimeoid.hue == 'red':
			if challenger_slimeoid.hue == 'pink':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'orange':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'pink':
			if challenger_slimeoid.hue == 'magenta':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'red':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'cyan':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'magenta':
			if challenger_slimeoid.hue == 'purple':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'pink':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'purple':
			if challenger_slimeoid.hue == 'blue':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'violet':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'green':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'yellow':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'blue':
			if challenger_slimeoid.hue == 'cobalt':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'purple':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'orange':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'cobalt':
			if challenger_slimeoid.hue == 'cyan':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'yellow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'red':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'cyan':
			if challenger_slimeoid.hue == 'teal':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'orange':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'teal':
			if challenger_slimeoid.hue == 'green':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'red':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'magenta':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'green':
			if challenger_slimeoid.hue == 'lime':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'teal':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'pink':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'purple':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'lime':
			if challenger_slimeoid.hue == 'yellow':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'green':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'magenta':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'yellow':
			if challenger_slimeoid.hue == 'orange':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'lime':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'cobalt':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
		if challenger_slimeoid.hue == 'orange':
			if challenger_slimeoid.hue == 'red':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'yellow':
				s1grit += 2
				if s1grit <= 1:
					s1grit = 1
				challenger_analogous = "It's not very effective against {}...".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'blue':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'cyan':
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)
			if challenger_slimeoid.hue == 'rainbow':
				s1moxie += 2
				if s1moxie <= 1:
					s1moxie = 1
				s1chutzpah += 2
				if s1chutzpah <= 1:
					s1chutzpah = 1
				challenger_splitcomplementary = "It's Super Effective against {}!".format(challenger_slimeoid.name)

		s1_active = False
		in_range = False

		if challengee_slimeoid.defense > challenger_slimeoid.defense:
			s1_active = True
		elif challengee_slimeoid.defense == challenger_slimeoid.defense:
			coinflip = random.randrange(1,3)
			if coinflip == 1:
				s1_active = True

		player = author

		response = "**{} sends {} out into the Battle Arena!**".format(author.display_name, s2name)
		await ewutils.send_message(cmd.client, cmd.message.channel, response)
		await asyncio.sleep(1)
		response = "**{} sends {} out into the Battle Arena!**".format(member.display_name, s1name)
		await ewutils.send_message(cmd.client, cmd.message.channel, response)
		await asyncio.sleep(1)
		response = "\nThe crowd erupts into cheers! The battle between {} and {} has begun! :crossed_swords:".format(s1name, s2name)
#		response += "\n{} {} {} {} {} {}".format(str(s1moxie),str(s1grit),str(s1chutzpah),str(challengee_slimeoid.weapon),str(challengee_slimeoid.armor),str(challengee_slimeoid.special))
#		response += "\n{} {} {} {} {} {}".format(str(s2moxie),str(s2grit),str(s2chutzpah),str(challenger_slimeoid.weapon),str(challenger_slimeoid.armor),str(challenger_slimeoid.special))
#		response += "\n{}, {}".format(str(challengee_resistance),str(challengee_weakness))
#		response += "\n{}, {}".format(str(challenger_resistance),str(challenger_weakness))
		await ewutils.send_message(cmd.client, cmd.message.channel, response)
		await asyncio.sleep(3)

		s1hpmax = 50 + (challengee_slimeoid.level * 20)
		s2hpmax = 50 + (challenger_slimeoid.level * 20)
		s1hp = s1hpmax
		s2hp = s2hpmax

		turncounter = 100
		while s1hp > 0 and s2hp > 0 and turncounter > 0:
			# Limit the number of turns in battle.
			turncounter -= 1

			response = ""
			battlecry = random.randrange(1,4)
			thrownobject = ewcfg.thrownobjects_list[random.randrange(len(ewcfg.thrownobjects_list))]
			if s1_active:
				player = member
				if in_range == False:

					#determine strat based on ai
					if challengee_slimeoid.ai in ['a', 'g']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'attack'
						else:
							strat = 'move'
					elif challengee_slimeoid.ai in ['b', 'd', 'f']:
						ranged_strat = random.randrange(1,3)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'
					elif challengee_slimeoid.ai in ['c', 'e']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'

					#potentially add brain-based flavor text
					if strat == 'attack' and battlecry == 1:
						if (s1hpmax/s1hp) > 3:
							response = s1brain.str_battlecry_weak.format(
								slimeoid_name=s1name
							)
						else:
							response = s1brain.str_battlecry.format(
								slimeoid_name=s1name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					elif strat == 'move' and battlecry == 1:
						if (s1hpmax/s1hp) > 3:
							response = s1brain.str_movecry_weak.format(
								slimeoid_name=s1name
							)
						else:
							response = s1brain.str_movecry.format(
								slimeoid_name=s1name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					#perform action
					if strat == 'move':
						if (s1hpmax/s1hp) > 3:
							in_range = True
							response = s1legs.str_advance_weak.format(
								active=s1name,
								inactive=s2name,
							)
						else:
							in_range = True
							response = s1legs.str_advance.format(
								active=s1name,
								inactive=s2name,
							)
#						response += " *s1close*"

					else:
						hp = s2hp
						damage = (s1chutzpah * 10)
						s2hp -= damage
						response = "**"
						if s2hp <= 0:
							response += s1special.str_special_attack_coup.format(
								active=s1name,
								inactive=s2name,
								object=thrownobject
							)
							challenger_weakness = ""
							challenger_splitcomplementary = ""
						elif (s1hpmax/s1hp) > 3:
							response += s1special.str_special_attack_weak.format(
								active=s1name,
								inactive=s2name,
								object=thrownobject
							)
						else:
							response += s1special.str_special_attack.format(
								active=s1name,
								inactive=s2name,
								object=thrownobject
							)
						response += "**"
						response += " :boom:"
#						response += " strat:{}".format(str(ranged_strat))

						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

						if challenger_weakness != "" or s2hp > 0:
							response = ""
							if challenger_weakness != "":
								response = challenger_weakness

						if challenger_splitcomplementary != "" or s2hp > 0:
							response = ""
							if challenger_splitcomplementary != "":
								response += challenger_splitcomplementary

							if s2hp > 0:
								if hp/damage > 10:
									response += " {} barely notices the damage.".format(challenger_slimeoid.name)
								elif hp/damage > 6:
									response += " {} is hurt, but shrugs it off.".format(challenger_slimeoid.name)
								elif hp/damage > 4:
									response += " {} felt that one!".format(challenger_slimeoid.name)
								elif hp/damage >= 3:
									response += " {} really felt that one!".format(challenger_slimeoid.name)
								elif hp/damage < 3:
									response += " {} reels from the force of the attack!!".format(challenger_slimeoid.name)
#						response += " *s1shoot{}*".format(str(damage))
#						response += " *({}/{} s2hp)*".format(s2hp, s2hpmax)

				else:
					#determine strat based on ai
					if challengee_slimeoid.ai in ['a', 'b', 'c']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'
					elif challengee_slimeoid.ai in ['d']:
						ranged_strat = random.randrange(1,3)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'
					elif challengee_slimeoid.ai in ['e', 'f', 'g']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'attack'
						else:
							strat = 'move'

					#potentially add brain-based flavor text
					if strat == 'attack' and battlecry == 1:
						if (s1hpmax/s1hp) > 3:
							response = s1brain.str_battlecry_weak.format(
								slimeoid_name=s1name
							)
						else:
							response = s1brain.str_battlecry.format(
								slimeoid_name=s1name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					elif strat == 'move' and battlecry == 1:
						if (s1hpmax/s1hp) > 3:
							response = s1brain.str_movecry_weak.format(
								slimeoid_name=s1name
							)
						else:
							response = s1brain.str_movecry.format(
								slimeoid_name=s1name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					#perform action
					if strat == 'attack':
						hp = s2hp
						damage = int((s1moxie / s2grit) * 15)
						s2hp -= damage
						response = "**"
						if s2hp <= 0:
							response += s1weapon.str_attack_coup.format(
								active=s1name,
								inactive=s2name,
							)
							challenger_resistance = ""
							challenger_analogous = ""
						elif (s1hpmax/s1hp) > 3:
							response += s1weapon.str_attack_weak.format(
								active=s1name,
								inactive=s2name,
							)
						else:
							response += s1weapon.str_attack.format(
								active=s1name,
								inactive=s2name,
							)
						response += "**"
						response += " :boom:"
#						response += " strat:{}".format(str(ranged_strat))

						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

						if challenger_resistance != "" or s2hp > 0:
							response = ""
							if challenger_resistance != "":
								response += challenger_resistance

						if challenger_analogous != "" or s2hp > 0:
							response = ""
							if challenger_analogous != "":
								response += challenger_analogous

							if s2hp > 0:
								if hp/damage > 10:
									response += " {} barely notices the damage.".format(challenger_slimeoid.name)
								elif hp/damage > 6:
									response += " {} is hurt, but shrugs it off.".format(challenger_slimeoid.name)
								elif hp/damage > 4:
									response += " {} felt that one!".format(challenger_slimeoid.name)
								elif hp/damage >= 3:
									response += " {} really felt that one!".format(challenger_slimeoid.name)
								elif hp/damage < 3:
									response += " {} reels from the force of the attack!!".format(challenger_slimeoid.name)
#						response += " *s1hit{}*".format(str(damage))
#						response += " *({}/{}s2hp)*".format(s2hp, s2hpmax)

					else:
						if (s1hpmax/s1hp) > 3:
							in_range = False
							response = s1legs.str_retreat_weak.format(
								active=s1name,
								inactive=s2name,
							)
						else:
							in_range = False
							response = s1legs.str_retreat.format(
								active=s1name,
								inactive=s2name,
							)
#						response += " *s1flee*"

				s1_active = False

			else:
				player = author
				if in_range == False:

					#determine strat based on ai
					if challenger_slimeoid.ai in ['a', 'g']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'attack'
						else:
							strat = 'move'
					elif challenger_slimeoid.ai in ['b', 'd', 'f']:
						ranged_strat = random.randrange(1,3)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'
					elif challenger_slimeoid.ai in ['c', 'e']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'

					#potentially add brain-based flavor text
					if strat == 'attack' and battlecry == 1:
						if (s2hpmax/s2hp) > 3:
							response = s2brain.str_battlecry_weak.format(
								slimeoid_name=s2name
							)
						else:
							response = s2brain.str_battlecry.format(
								slimeoid_name=s2name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					elif strat == 'move' and battlecry == 1:
						if (s2hpmax/s2hp) > 3:
							response = s2brain.str_movecry_weak.format(
								slimeoid_name=s2name
							)
						else:
							response = s2brain.str_movecry.format(
								slimeoid_name=s2name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					#perform action
					if strat == 'move':
						if (s2hpmax/s2hp) > 3:
							in_range = True
							response = s2legs.str_advance_weak.format(
								active=s2name,
								inactive=s1name,
							)
						else:
							in_range = True
							response = s2legs.str_advance.format(
								active=s2name,
								inactive=s1name,
							)
#						response += " *s2close*"

					else:
						hp = s1hp
						damage = (s2chutzpah * 10)
						s1hp -= damage
						response = "**"
						if s1hp <= 0:
							response += s2special.str_special_attack_coup.format(
								active=s2name,
								inactive=s1name,
								object=thrownobject
							)
							challengee_weakness = ""
							challengee_splitcomplementary = ""
						elif (s2hpmax/s2hp) > 3:
							response += s2special.str_special_attack_weak.format(
								active=s2name,
								inactive=s1name,
								object=thrownobject
							)
						else:
							response += s2special.str_special_attack.format(
								active=s2name,
								inactive=s1name,
								object=thrownobject
							)
						response += "**"
						response += " :boom:"
#						response += " strat:{}".format(str(ranged_strat))

						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

						if challengee_weakness != "" or s1hp > 0:
							response = ""
							if challengee_weakness != "":
								response += challengee_weakness

						if challengee_splitcomplementary != "" or s1hp > 0:
							response = ""
							if challengee_splitcomplementary != "":
								response += challengee_splitcomplementary

							if s1hp > 0:
								if hp/damage > 10:
									response += " {} barely notices the damage.".format(challengee_slimeoid.name)
								elif hp/damage > 6:
									response += " {} is hurt, but shrugs it off.".format(challengee_slimeoid.name)
								elif hp/damage > 4:
									response += " {} felt that one!".format(challengee_slimeoid.name)
								elif hp/damage >= 3:
									response += " {} really felt that one!".format(challengee_slimeoid.name)
								elif hp/damage < 3:
									response += " {} reels from the force of the attack!!".format(challengee_slimeoid.name)
#						response += " *s2shoot{}*".format(str(damage))
#						response += " *({}/{} s1hp)*".format(s1hp, s1hpmax)
				else:

					#determine strat based on ai
					if challenger_slimeoid.ai in ['a', 'b', 'c']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'
					elif challenger_slimeoid.ai in ['d']:
						ranged_strat = random.randrange(1,3)
						if ranged_strat < 2:
							strat = 'move'
						else:
							strat = 'attack'
					elif challenger_slimeoid.ai in ['e', 'f', 'g']:
						ranged_strat = random.randrange(1,5)
						if ranged_strat < 2:
							strat = 'attack'
						else:
							strat = 'move'

					#potentially add brain-based flavor text
					if strat == 'attack' and battlecry == 1:
						if (s2hpmax/s2hp) > 3:
							response = s2brain.str_battlecry_weak.format(
								slimeoid_name=s2name
							)
						else:
							response = s2brain.str_battlecry.format(
								slimeoid_name=s2name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					elif strat == 'move' and battlecry == 1:
						if (s2hpmax/s2hp) > 3:
							response = s2brain.str_movecry_weak.format(
								slimeoid_name=s2name
							)
						else:
							response = s2brain.str_movecry.format(
								slimeoid_name=s2name
							)
						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

					#perform action
					if strat == 'attack':
						hp = s1hp
						damage = int((s2moxie / s1grit) * 15)
						s1hp -= damage
						response = "**"
						if s1hp <= 0:
							response += s2weapon.str_attack_coup.format(
								active=s2name,
								inactive=s1name,
							)
							challengee_resistance = ""
							challengee_analogous = ""
						elif (s2hpmax/s2hp) > 3:
							response += s2weapon.str_attack_weak.format(
								active=s2name,
								inactive=s1name,
							)
						else:
							response += s2weapon.str_attack.format(
								active=s2name,
								inactive=s1name,
							)
						response += "**"
						response += " :boom:"
#						response += " strat:{}".format(str(ranged_strat))

						await ewutils.send_message(cmd.client, cmd.message.channel, response)
						await asyncio.sleep(1)

						if challengee_resistance != "" or s2hp > 0:
							response = ""
							if challengee_resistance != "":
								response = challengee_resistance

						if challengee_analogous != "" or s2hp > 0:
							response = ""
							if challengee_analogous != "":
								response = challengee_analogous

							if s1hp > 0:
								if hp/damage > 10:
									response += " {} barely notices the damage.".format(challengee_slimeoid.name)
								elif hp/damage > 6:
									response += " {} is hurt, but shrugs it off.".format(challengee_slimeoid.name)
								elif hp/damage > 4:
									response += " {} felt that one!".format(challengee_slimeoid.name)
								elif hp/damage >= 3:
									response += " {} really felt that one!".format(challengee_slimeoid.name)
								elif hp/damage < 3:
									response += " {} reels from the force of the attack!!".format(challengee_slimeoid.name)

#						response += " *s2hit{}*".format(str(damage))
#						response += " *({}/{} s1hp)*".format(s1hp, s1hpmax)

					else:
						if (s2hpmax/s2hp) > 3:
							in_range = False
							response = s2legs.str_retreat_weak.format(
								active=s2name,
								inactive=s1name,
							)
						else:
							in_range = False
							response = s2legs.str_retreat.format(
								active=s2name,
								inactive=s1name,
							)
#						response += " *s2flee*"

				s1_active = True

			# Send the response to the player.
			if s1hp > 0 and s2hp > 0:
				await ewutils.send_message(cmd.client, cmd.message.channel, response)
				await asyncio.sleep(2)

		if s1hp <= 0:
			response = "\n" + s1legs.str_defeat.format(
				slimeoid_name=s1name
			)
			response += " {}".format(ewcfg.emote_slimeskull)
			response += "\n" + s2brain.str_victory.format(
				slimeoid_name=s2name
			)

			challenger_slimeoid = EwSlimeoid(member = author)
			challengee_slimeoid = EwSlimeoid(member = member)

			# Losing slimeoid loses clout and has a time_defeated cooldown.
			challengee_slimeoid.clout = calculate_clout_loss(challengee_slimeoid.clout)
			challengee_slimeoid.time_defeated = int(time.time())
			challengee_slimeoid.persist()

			challenger_slimeoid.clout = calculate_clout_gain(challenger_slimeoid.clout)
			challenger_slimeoid.persist()

			await ewutils.send_message(cmd.client, cmd.message.channel, response)
			await asyncio.sleep(2)
			response = "\n**{} has won the Slimeoid battle!! The crowd erupts into cheers for {} and {}!!** :tada:".format(challenger_slimeoid.name, challenger_slimeoid.name, author.display_name)
			await ewutils.send_message(cmd.client, cmd.message.channel, response)
			await asyncio.sleep(2)
		else:
			response = "\n" + s2legs.str_defeat.format(
				slimeoid_name=s2name
			)
			response += " {}".format(ewcfg.emote_slimeskull)
			response += "\n" + s1brain.str_victory.format(
				slimeoid_name=s1name
			)

			challenger_slimeoid = EwSlimeoid(member = author)
			challengee_slimeoid = EwSlimeoid(member = member)

			# store defeated slimeoid's defeat time in the database
			challenger_slimeoid.clout = calculate_clout_loss(challenger_slimeoid.clout)
			challenger_slimeoid.time_defeated = int(time.time())
			challenger_slimeoid.persist()

			challengee_slimeoid.clout = calculate_clout_gain(challengee_slimeoid.clout)
			challengee_slimeoid.persist()

			await ewutils.send_message(cmd.client, cmd.message.channel, response)
			await asyncio.sleep(2)
			response = "\n**{} has won the Slimeoid battle!! The crowd erupts into cheers for {} and {}!!** :tada:".format(challengee_slimeoid.name, challengee_slimeoid.name, member.display_name)
			await ewutils.send_message(cmd.client, cmd.message.channel, response)
			await asyncio.sleep(2)

	else:
		response = "{} was too cowardly to accept your challenge.".format(member.display_name).replace("@", "\{at\}")

		# Send the response to the player.
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(author, response))
