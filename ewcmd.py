import random
import asyncio
import time

import ewcfg
import ewutils
import ewitem
import ewrolemgr
import ewstats
import ewstatuseffects
import ewmap
import ewslimeoid
import ewfaction
import ewapt

from ew import EwUser
from ewmarket import EwMarket
from ewitem import EwItem
from ewslimeoid import EwSlimeoid
from ewhunting import find_enemy
from ewstatuseffects import EwStatusEffect
from ewstatuseffects import EwEnemyStatusEffect
from ewdistrict import EwDistrict

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

	user_data = EwUser(
		id_user = id_user,
		id_server = id_server
	)

	items = ewitem.inventory(
		id_user = id_user,
		id_server = id_server,
		item_type_filter = ewcfg.it_item
	)

	poudrin_amount = ewitem.find_poudrin(id_user = id_user, id_server = id_server)

	if user_data.life_state == ewcfg.life_state_grandfoe:
		# Can't see a raid boss's slime score.
		response = "{}'s power is beyond your understanding.".format(display_name)
	else:
		# return somebody's score
		response = "{} currently has {:,} slime{}.".format(display_name, user_data.slimes, (" and {} slime poudrin{}".format(poudrin_amount, ("" if poudrin_amount == 1 else "s")) if poudrin_amount > 0 else ""))

	return response

""" show player's slime score """
async def score(cmd):
	user_data = None
	member = None

	if cmd.mentions_count == 0:
		user_data = EwUser(member = cmd.message.author)

		poudrin_amount = ewitem.find_poudrin(id_user = cmd.message.author.id, id_server = cmd.message.server.id)

		# return my score
		response = "You currently have {:,} slime{}.".format(user_data.slimes, (" and {} slime poudrin{}".format(poudrin_amount, ("" if poudrin_amount == 1 else "s")) if poudrin_amount > 0 else ""))

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
		id_user=None,
		id_server=None,
		display_name=None,
		channel_name=None
):
	user_data = EwUser(
		id_user=id_user,
		id_server=id_server
	)
	slimeoid = EwSlimeoid(id_user=id_user, id_server=id_server)

	cosmetics = ewitem.inventory(
		id_user=user_data.id_user,
		id_server=user_data.id_server,
		item_type_filter=ewcfg.it_cosmetic
	)
	adorned_cosmetics = []
	for cosmetic in cosmetics:
		cos = EwItem(id_item=cosmetic.get('id_item'))
		if cos.item_props['adorned'] == 'true':
			hue = ewcfg.hue_map.get(cos.item_props.get('hue'))
			adorned_cosmetics.append((hue.str_name + " " if hue != None else "") + cosmetic.get('name'))

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
		elif user_data.life_state == ewcfg.life_state_shambler:
			response = "{} is a level {} shambler.".format(display_name, user_data.slimelevel)
		else:
			response = "{} is a level {} slimeboi.".format(display_name, user_data.slimelevel)
			if user_data.degradation < 20:
				pass
			elif user_data.degradation < 40:
				response += " Their bodily integrity is starting to slip."
			elif user_data.degradation < 60:
				response += " Their face seems to be melting and they periodically have to put it back in place."
			elif user_data.degradation < 80:
				response += " They are walking a bit funny, because their legs are getting mushy."
			elif user_data.degradation < 100:
				response += " Their limbs keep falling off. It's really annoying."
			else:
				response += " They almost look like a shambler already."

		coinbounty = int(user_data.bounty / ewcfg.slimecoin_exchangerate)

		weapon_item = EwItem(id_item=user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

		if weapon != None:
			response += " {} {}{}.".format(
				ewcfg.str_weapon_married if user_data.weaponmarried == True else ewcfg.str_weapon_wielding, (
					"" if len(weapon_item.item_props.get("weapon_name")) == 0 else "{}, ".format(
						weapon_item.item_props.get("weapon_name"))), weapon.str_weapon)
			if user_data.weaponskill >= 5:
				response += " {}".format(weapon.str_weaponmaster.format(rank=(user_data.weaponskill - 4)))

		trauma = ewcfg.trauma_map.get(user_data.trauma)

		if trauma != None:
			response += " {}".format(trauma.str_trauma)

		response_block = ""

		user_kills = ewstats.get_stat(user=user_data, metric=ewcfg.stat_kills)

		enemy_kills = ewstats.get_stat(user=user_data, metric=ewcfg.stat_pve_kills)

		if user_kills > 0 and enemy_kills > 0:
			response_block += "They have {:,} confirmed kills, and {:,} confirmed hunts. ".format(user_kills,
																								  enemy_kills)
		elif user_kills > 0:
			response_block += "They have {:,} confirmed kills. ".format(user_kills)
		elif enemy_kills > 0:
			response_block += "They have {:,} confirmed hunts. ".format(enemy_kills)

		if coinbounty != 0:
			response_block += "SlimeCorp offers a bounty of {:,} SlimeCoin for their death. ".format(coinbounty)

		if len(adorned_cosmetics) > 0:
			response_block += "They have a {} adorned. ".format(ewutils.formatNiceList(adorned_cosmetics, 'and'))

		statuses = user_data.getStatusEffects()

		for status in statuses:
			status_effect = EwStatusEffect(id_status=status, user_data=user_data)
			if status_effect.time_expire > time.time() or status_effect.time_expire == -1:
				status_flavor = ewcfg.status_effects_def_map.get(status)

				severity = ""
				try:
					value_int = int(status_effect.value)
					if value_int < 3:
						severity = "lightly injured."
					elif value_int < 7:
						severity = "battered and bruised."
					elif value_int < 11:
						severity = "severely damaged."
					else:
						severity = "completely fucked up, holy shit!"
				except:
					pass

				format_status = {'severity': severity}

				if status_flavor is not None:
					response_block += status_flavor.str_describe.format_map(format_status) + " "

		if (slimeoid.life_state == ewcfg.slimeoid_state_active) and (user_data.life_state != ewcfg.life_state_corpse):
			response_block += "They are accompanied by {}, a {}-foot-tall Slimeoid. ".format(slimeoid.name, str(slimeoid.level))
			
		if user_data.swear_jar >= 500:
			response_block += "They're going to The Underworld for the things they've said."
		elif user_data.swear_jar >= 100:
			response_block += "They swear like a sailor!"
		elif user_data.swear_jar >= 50:
			response_block += "They have quite a profane vocabulary."
		elif user_data.swear_jar >= 10:
			response_block += "They've said some naughty things in the past."
		elif user_data.swear_jar >= 5:
			response_block += "They've cussed a handfull of times here and there."
		elif user_data.swear_jar > 0:
			response_block += "They've sworn only a few times."
		else:
			response_block += "Their mouth is clean as a whistle."
			
		if len(response_block) > 0:
			response += "\n" + response_block

	return response


""" show player information and description """


async def data(cmd):
	member = None
	response = ""

	if len(cmd.tokens) > 1 and cmd.mentions_count == 0:
		user_data = EwUser(member=cmd.message.author)

		soughtenemy = " ".join(cmd.tokens[1:]).lower()
		enemy = find_enemy(soughtenemy, user_data)
		if enemy != None:
			if enemy.attacktype != ewcfg.enemy_attacktype_unarmed:
				response = "{} is a level {} enemy. They have {:,} slime, and attack with their {}. ".format(
					enemy.display_name, enemy.level, enemy.slimes, enemy.attacktype)
			else:
				response = "{} is a level {} enemy. They have {:,} slime. ".format(enemy.display_name, enemy.level,
																				enemy.slimes)
		
			statuses = enemy.getStatusEffects()

			for status in statuses:
				status_effect = EwEnemyStatusEffect(id_status=status, enemy_data=enemy)
				if status_effect.time_expire > time.time() or status_effect.time_expire == -1:
					status_flavor = ewcfg.status_effects_def_map.get(status)

					severity = ""
					try:
						value_int = int(status_effect.value)
						if value_int < 3:
							severity = "lightly injured."
						elif value_int < 7:
							severity = "battered and bruised."
						elif value_int < 11:
							severity = "severely damaged."
						else:
							severity = "completely fucked up, holy shit!"
					except:
						pass

					format_status = {'severity': severity}

					if status_flavor is not None:
						response += status_flavor.str_describe.format_map(format_status) + " "
		else:
			response = "ENDLESS WAR didn't understand that name."



	elif cmd.mentions_count == 0:

		user_data = EwUser(member=cmd.message.author)
		slimeoid = EwSlimeoid(member=cmd.message.author)

		cosmetics = ewitem.inventory(
			id_user=cmd.message.author.id,
			id_server=cmd.message.server.id,
			item_type_filter=ewcfg.it_cosmetic
		)
		adorned_cosmetics = []
		for cosmetic in cosmetics:
			cos = EwItem(id_item=cosmetic.get('id_item'))
			if cos.item_props['adorned'] == 'true':
				hue = ewcfg.hue_map.get(cos.item_props.get('hue'))
				adorned_cosmetics.append((hue.str_name + " " if hue != None else "") + cosmetic.get('name'))

		poi = ewcfg.id_to_poi.get(user_data.poi)
		if poi != None:
			response = "You find yourself {} {}. ".format(poi.str_in, poi.str_name)

		# return my data
		if user_data.life_state == ewcfg.life_state_corpse:
			response += "You are a level {} deadboi.".format(user_data.slimelevel)
		elif user_data.life_state == ewcfg.life_state_shambler:
			response += "You are a level {} shambler.".format(user_data.slimelevel)
		else:
			response += "You are a level {} slimeboi.".format(user_data.slimelevel)
			if user_data.degradation < 20:
				pass
			elif user_data.degradation < 40:
				response += " Your bodily integrity is starting to slip."
			elif user_data.degradation < 60:
				response += " Your face seems to be melting and you periodically have to put it back in place."
			elif user_data.degradation < 80:
				response += " You are walking a bit funny, because your legs are getting mushy."
			elif user_data.degradation < 100:
				response += " Your limbs keep falling off. It's really annoying."
			else:
				response += " You almost look like a shambler already."

		if user_data.has_soul == 0:
			response += " You have no soul."

		coinbounty = int(user_data.bounty / ewcfg.slimecoin_exchangerate)

		weapon_item = EwItem(id_item=user_data.weapon)
		weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))

		if weapon != None:
			response += " {} {}{}.".format(
				ewcfg.str_weapon_married_self if user_data.weaponmarried == True else ewcfg.str_weapon_wielding_self, (
					"" if len(weapon_item.item_props.get("weapon_name")) == 0 else "{}, ".format(
						weapon_item.item_props.get("weapon_name"))), weapon.str_weapon)
			if user_data.weaponskill >= 5:
				response += " {}".format(weapon.str_weaponmaster_self.format(rank=(user_data.weaponskill - 4)))

		trauma = ewcfg.trauma_map.get(user_data.trauma)

		if trauma != None:
			response += " {}".format(trauma.str_trauma_self)

		response_block = ""

		user_kills = ewstats.get_stat(user=user_data, metric=ewcfg.stat_kills)
		enemy_kills = ewstats.get_stat(user=user_data, metric=ewcfg.stat_pve_kills)

		if user_kills > 0 and enemy_kills > 0:
			response_block += "You have {:,} confirmed kills, and {:,} confirmed hunts. ".format(user_kills,
																								 enemy_kills)
		elif user_kills > 0:
			response_block += "You have {:,} confirmed kills. ".format(user_kills)
		elif enemy_kills > 0:
			response_block += "You have {:,} confirmed hunts. ".format(enemy_kills)

		if coinbounty != 0:
			response_block += "SlimeCorp offers a bounty of {:,} SlimeCoin for your death. ".format(coinbounty)

		if len(adorned_cosmetics) > 0:
			response_block += "You have a {} adorned. ".format(ewutils.formatNiceList(adorned_cosmetics, 'and'))

		if user_data.hunger > 0:
			response_block += "You are {}% hungry. ".format(
				round(user_data.hunger * 100.0 / user_data.get_hunger_max(), 1)
			)

		if user_data.busted and user_data.life_state == ewcfg.life_state_corpse:
			response_block += "You are busted and therefore cannot leave the sewers until your next !haunt. "

		statuses = user_data.getStatusEffects()

		for status in statuses:
			status_effect = EwStatusEffect(id_status=status, user_data=user_data)
			if status_effect.time_expire > time.time() or status_effect.time_expire == -1:
				status_flavor = ewcfg.status_effects_def_map.get(status)

				severity = ""
				try:
					value_int = int(status_effect.value)
					if value_int < 3:
						severity = "lightly injured."
					elif value_int < 7:
						severity = "battered and bruised."
					elif value_int < 11:
						severity = "severely damaged."
					else:
						severity = "completely fucked up, holy shit!"
				except:
					pass

				format_status = {'severity': severity}

				if status_flavor is not None:
					response_block += status_flavor.str_describe_self.format_map(format_status) + " "

		if (slimeoid.life_state == ewcfg.slimeoid_state_active) and (user_data.life_state != ewcfg.life_state_corpse):
			response_block += "You are accompanied by {}, a {}-foot-tall Slimeoid. ".format(slimeoid.name, str(slimeoid.level))
		
		if user_data.swear_jar >= 500:
			response_block += "You're going to The Underworld for the things you've said."
		elif user_data.swear_jar >= 100:
			response_block += "You swear like a sailor!"
		elif user_data.swear_jar >= 50:
			response_block += "You have quite a profane vocabulary."
		elif user_data.swear_jar >= 10:
			response_block += "You've said some naughty things in the past."
		elif user_data.swear_jar >= 5:
			response_block += "You've cussed a handfull of times here and there."
		elif user_data.swear_jar > 0:
			response_block += "You've sworn only a few times."
		else:
			response_block += "Your mouth is clean as a whistle."
			

		if len(response_block) > 0:
			response += "\n" + response_block

		response += "\n\nhttps://ew.krakissi.net/stats/player.html?pl={}".format(user_data.id_user)
	else:
		member = cmd.mentions[0]
		response = gen_data_text(
			id_user=member.id,
			id_server=member.server.id,
			display_name=member.display_name,
			channel_name=cmd.message.channel.name
		)

		response += "\n\nhttps://ew.krakissi.net/stats/player.html?pl={}".format(member.id)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
	if member != None:
		await ewrolemgr.updateRoles(client=cmd.client, member=member)


""" Finally, separates mutations from !data """


async def mutations(cmd):
	response = ""
	if cmd.mentions_count == 0:
		user_data = EwUser(member=cmd.message.author)
		mutations = user_data.get_mutations()
		for mutation in mutations:
			mutation_flavor = ewcfg.mutations_map[mutation]
			response += "{} ".format(mutation_flavor.str_describe_self)
		if len(mutations) == 0:
			response = "You are miraculously unmodified from your normal genetic code!"

	else:
		member = cmd.mentions[0]
		user_data = EwUser(
			id_user=member.id,
			id_server=member.server.id
		)
		mutations = user_data.get_mutations()
		for mutation in mutations:
			mutation_flavor = ewcfg.mutations_map[mutation]
			response += "{} ".format(mutation_flavor.str_describe_other)
		if len(mutations) == 0:
			response = "They are miraculously unmodified from their normal genetic code!"

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

""" Check how hungry you are. """
async def hunger(cmd):
	user_data = EwUser(member=cmd.message.author)
	response = ""

	if user_data.hunger > 0:
		response = "You are {}% hungry. ".format(
			round(user_data.hunger * 100.0 / user_data.get_hunger_max(), 1)
		)
	else:
		response = "You aren't hungry at all."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def endlesswar(cmd):
	total = ewutils.execute_sql_query("SELECT SUM(slimes) FROM users WHERE slimes > 0 AND id_server = '{}'".format(cmd.message.server.id))
	totalslimes = total[0][0]

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "ENDLESS WAR has amassed {:,} slime.".format(totalslimes)))

async def swearjar(cmd):
	market_data = EwMarket(id_server=cmd.message.server.id)
	total_swears = market_data.global_swear_jar
	
	response = "The swear jar has reached: **{}**".format(total_swears)
	
	if total_swears < 1000:
		pass
	elif total_swears < 10000:
		response += "\nThings are starting to get nasty."
	elif total_swears < 100000:
		response += "\nSwears? In *my* free Text-Based MMORPG playable entirely within my browser? It's more likely than you think."
	elif total_swears < 1000000:
		response += "\nGod help us all..."
	else:
		response = "\nThe city is rife with mischief and vulgarity, though that's hardly a surprise when it's inhabited by lowlifes and sinners across the board."
	
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


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

async def lol(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'You laugh out loud!'))

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
	Juvies DANCE
"""
async def dance(cmd):
	user_data = EwUser(member = cmd.message.author)
	member = cmd.message.author
	
	if user_data.life_state == ewcfg.life_state_juvenile:
		dance_response = random.choice(ewcfg.dance_responses).format(member.display_name)
		dance_response = "{} {} {}".format(ewcfg.emote_slime3, dance_response, ewcfg.emote_slime3)
		await ewutils.send_message(cmd.client, cmd.message.channel, dance_response)

"""
	Ghosts BOO
"""
async def boo(cmd):
	user_data = EwUser(member = cmd.message.author)
	
	if user_data.life_state == ewcfg.life_state_corpse or user_data.life_state == ewcfg.life_state_grandfoe:
		resp_cont = ewutils.EwResponseContainer(id_server = user_data.id_server)
		
		response = ewutils.formatMessage(cmd.message.author, '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_staydead + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + '\n' + ewcfg.emote_ghost + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_ghost + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead)
		resp_cont.add_channel_response(cmd.message.channel.name, response)
		
		# if user_data.life_state == ewcfg.life_state_corpse or user_data.life_state == ewcfg.life_state_grandfoe:
		await resp_cont.post()
	#await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_blank + ewcfg.emote_blank + '\n' + ewcfg.emote_ghost + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_srs + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_ghost + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_blank + ewcfg.emote_blank + '\n' + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_negaslime + ewcfg.emote_srs + ewcfg.emote_negaslime + ewcfg.emote_staydead + ewcfg.emote_staydead + ewcfg.emote_blank + ewcfg.emote_blank + ewcfg.emote_blank))

"""
	Terezi Gang FLIP COINS
"""
async def coinflip(cmd):
	
	user_data = EwUser(member=cmd.message.author)
	response = ""
	
	if ewutils.check_user_has_role(cmd.message.server, cmd.message.author, ewcfg.role_donor_proper):
		
		if user_data.slimecoin <= 1:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "YOU DON'T H4V3 4NY SL1M3CO1N TO FL1P >:["))
		else:
			user_data.change_slimecoin(n = -1, coinsource = ewcfg.coinsource_spending)
			user_data.persist()
		
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "YOU FL1P ON3 SL1M3CO1N R1GHT 1N TH3 41R!\nhttps://cdn.discordapp.com/attachments/431240644464214017/652341405129375794/Terezi_Hussnasty_coinflip.gif"))
		await asyncio.sleep(2)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "..."))
		await asyncio.sleep(3)
		
		flipnum = random.randrange(2)

		if flipnum == 0:
			response = "H34DS!\nhttps://www.homestuck.com/images/storyfiles/hs2/02045_3.gif"
		else:
			response = "T41LS!\nhttps://66.media.tumblr.com/tumblr_m6gdpg4qOg1r6ajb6.gif"
		
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def spook(cmd):
	#user_data = EwUser(member=cmd.message.author)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, '\n' "***SPOOKED YA!***" + '\n' + "https://www.youtube.com/watch?v=T-dtcIXZo4s"))

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

	# checks if user is in a college or if they have a game guide
	gameguide = ewitem.find_item(item_search="gameguide", id_user=cmd.message.author.id, id_server=cmd.message.server.id if cmd.message.server is not None else None, item_type_filter = ewcfg.it_item)

	if cmd.message.channel.name == ewcfg.channel_neomilwaukeestate or cmd.message.channel.name == ewcfg.channel_nlacu or gameguide:
		if not len(cmd.tokens) > 1:
			topic_counter = 0
			topic_total = 0
			# list off help topics to player at college
			response = "(Use !help [topic] to learn about a topic. Example: '!help gangs')\n\nWhat would you like to learn about? Topics include: \n"
			
			# display the list of topics in order
			topics = ewcfg.help_responses_ordered_keys
			for topic in topics:
				topic_counter += 1
				topic_total += 1
				response += "**{}**".format(topic)
				if topic_total != len(topics):
					response += ", "
				
				if topic_counter == 5:
					topic_counter = 0
					response += "\n"
				
		else:
			topic = ewutils.flattenTokenListToString(cmd.tokens[1:])
			if topic in ewcfg.help_responses:
				response = ewcfg.help_responses[topic]
				if topic == 'mymutations':
					mutations = user_data.get_mutations()
					for mutation in mutations:
						response += "\n**{}**: {}".format(mutation, ewcfg.mutation_descriptions[mutation])
			else:
				response = 'ENDLESS WAR questions your belief in the existence of such a topic. Try referring to the topics list again by using just !help.'
	else:
		# user not in college, check what help message would apply to the subzone they are in

		# poi variable assignment used for checking if player is in a vendor subzone or not
		poi = ewmap.fetch_poi_if_coordless(cmd.message.channel.name)

		dojo_topics = ["dojo", "sparring", "combat", "sap", ewcfg.weapon_id_revolver, ewcfg.weapon_id_dualpistols, ewcfg.weapon_id_shotgun, ewcfg.weapon_id_rifle, ewcfg.weapon_id_smg, ewcfg.weapon_id_minigun, ewcfg.weapon_id_bat, ewcfg.weapon_id_brassknuckles, ewcfg.weapon_id_katana, ewcfg.weapon_id_broadsword, ewcfg.weapon_id_nunchucks, ewcfg.weapon_id_scythe, ewcfg.weapon_id_yoyo, ewcfg.weapon_id_bass, ewcfg.weapon_id_umbrella, ewcfg.weapon_id_knives, ewcfg.weapon_id_molotov, ewcfg.weapon_id_grenades, ewcfg.weapon_id_garrote]

		if poi is None:
			# catch-all response for when user isn't in a sub-zone with a help response
			response = ewcfg.generic_help_response

		elif cmd.message.channel.name in [ewcfg.channel_mines, ewcfg.channel_cv_mines, ewcfg.channel_tt_mines]:
			# mine help
			response = ewcfg.help_responses['mining']
		elif (len(poi.vendors) >= 1) and not cmd.message.channel.name in [ewcfg.channel_dojo, ewcfg.channel_greencakecafe, ewcfg.channel_glocksburycomics]:
			# food help
			response = ewcfg.help_responses['food']
		elif cmd.message.channel.name in [ewcfg.channel_greencakecafe, ewcfg.channel_glocksburycomics]:
			# zines help
			response = ewcfg.help_responses['zines']
		elif cmd.message.channel.name in ewcfg.channel_dojo and not len(cmd.tokens) > 1:
			# dojo help
			response = "For general dojo information, do **'!help dojo'**. For information about the sparring and weapon rank systems, do **'!help sparring.'**. For general information about combat, do **'!help combat'**. For information about the sap system, do **'!help sap'**. For information about a specific weapon, do **'!help [weapon]'**."
		elif cmd.message.channel.name in ewcfg.channel_dojo and len(cmd.tokens) > 1:
			topic = ewutils.flattenTokenListToString(cmd.tokens[1:])
			if topic in dojo_topics and topic in ewcfg.help_responses:
				response = ewcfg.help_responses[topic]
			else:
				response = 'ENDLESS WAR questions your belief in the existence of such information regarding the dojo. Try referring to the topics list again by using just !help.'
		elif cmd.message.channel.name in [ewcfg.channel_jr_farms, ewcfg.channel_og_farms, ewcfg.channel_ab_farms]:
			# farming help
			response = ewcfg.help_responses['farming']
		elif cmd.message.channel.name in ewcfg.channel_slimeoidlab and not len(cmd.tokens) > 1:
			# labs help
			response = "For information on slimeoids, do **'!help slimeoids'**. To learn about your current mutations, do **'!help mymutations'**"
		elif cmd.message.channel.name in ewcfg.channel_slimeoidlab and len(cmd.tokens) > 1:
			topic = ewutils.flattenTokenListToString(cmd.tokens[1:])
			if topic == 'slimeoids':
				response = ewcfg.help_responses['slimeoids']
			elif topic == 'mymutations':
				response = ewcfg.help_responses['mymutations']
				mutations = user_data.get_mutations()
				for mutation in mutations:
					response += "\n**{}**: {}".format(mutation, ewcfg.mutation_descriptions[mutation])
			else:
				response = 'ENDLESS WAR questions your belief in the existence of such information regarding the laboratory. Try referring to the topics list again by using just !help.'
		elif cmd.message.channel.name in ewcfg.transport_stops_ch:
			# transportation help
			response = ewcfg.help_responses['transportation']
		elif cmd.message.channel.name in ewcfg.channel_stockexchange:
			# stock exchange help
			response = ewcfg.help_responses['stocks']
		elif cmd.message.channel.name in ewcfg.channel_casino:
			# casino help
			response = ewcfg.help_responses['casino']
		elif cmd.message.channel.name in ewcfg.channel_sewers:
			# death help
			response = ewcfg.help_responses['death']

		elif cmd.message.channel.name in ewcfg.channel_realestateagency:
			#real estate help
			response = ewcfg.help_responses['realestate']
		elif cmd.message.channel.name in [
			ewcfg.channel_tt_pier,
			ewcfg.channel_afb_pier,
			ewcfg.channel_jr_pier,
			ewcfg.channel_cl_pier,
			ewcfg.channel_se_pier,
			ewcfg.channel_jp_pier,
			ewcfg.channel_ferry
		]:
			# fishing help
			response = ewcfg.help_responses['fishing']
		elif user_data.poi in ewcfg.outskirts_districts:
			# hunting help
			response = ewcfg.help_responses['hunting']
		else:
			# catch-all response for when user isn't in a sub-zone with a help response
			response = ewcfg.generic_help_response
				
	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


"""
	Link to the world map.
"""
async def map(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Online world map: https://ew.krakissi.net/map/'))

"""
	Link to the subway map
"""
async def transportmap(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Map of the subway: https://cdn.discordapp.com/attachments/431238867459375145/570392908780404746/t_system_final_stop_telling_me_its_wrong_magicks.png\nPlease note that the white line is currently non-operational, and that there also exists a **blimp** that goes between Dreadford and Assault Flats Beach, as well as a **ferry** that goes between Wreckington and Vagrant's Corner."))


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
	if(ewutils.active_target_map.get(user.id_user) != None and ewutils.active_target_map.get(user.id_user) != ""):
		challenger = EwUser(id_user = ewutils.active_target_map[user.id_user], id_server = user.id_server)
		if(ewutils.active_target_map.get(user.id_user) != user.id_user and ewutils.active_target_map.get(challenger.id_user) != user.id_user):
			ewutils.active_target_map[challenger.id_user] = user.id_user
			slimeoid_data = EwSlimeoid(member = cmd.message.author)
			response = ""
			if cmd.message.channel.name == ewcfg.channel_arena and ewslimeoid.active_slimeoidbattles.get(slimeoid_data.id_slimeoid):
				response = "You accept the challenge! Both of your Slimeoids ready themselves for combat!"
			elif cmd.message.channel.name == ewcfg.channel_casino and ewutils.active_restrictions[challenger.id_user] == 1:
				response = "You accept the challenge! Both of you head out back behind the casino and load a bullet into the gun."

			if len(response) > 0:
				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" Refuse a russian roulette challenge """
async def refuse(cmd):
	user = EwUser(member = cmd.message.author)

	if(ewutils.active_target_map.get(user.id_user) != None and ewutils.active_target_map.get(user.id_user) != ""):
		challenger = EwUser(id_user = ewutils.active_target_map[user.id_user], id_server = user.id_server)

		ewutils.active_target_map[user.id_user] = ""
		ewutils.active_restrictions[user.id_user] = 0

		if(ewutils.active_target_map.get(user.id_user) != user.id_user and ewutils.active_target_map.get(challenger.id_user) != user.id_user):
			response = "You refuse the challenge, but not before leaving a large puddle of urine beneath you."
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		else:
			ewutils.active_target_map[challenger.id_user] = ""
			ewutils.active_restrictions[challenger.id_user] = 0

"""
	Ban a player from participating in the game
"""
async def arrest(cmd):

	author = cmd.message.author
	
	if not author.server_permissions.administrator:
		return
	
	if cmd.mentions_count == 1:
		member = cmd.mentions[0]
		user_data = EwUser(member = member)
		user_data.arrested = True
		user_data.poi = ewcfg.poi_id_juviesrow
		user_data.change_slimes(n = - user_data.slimes)
		user_data.persist()

		response = "{} is thrown into one of the Juvenile Detention Center's high security solitary confinement cells.".format(member.display_name)
		await ewrolemgr.updateRoles(client = cmd.client, member = member)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""
	Allow a player to participate in the game again
"""
async def release(cmd):

	author = cmd.message.author
	
	if not author.server_permissions.administrator:
		return
	
	if cmd.mentions_count == 1:
		member = cmd.mentions[0]
		user_data = EwUser(member = member)
		user_data.arrested = False
		user_data.persist()

		response = "{} is released. But beware, the cops will be keeping an eye on you.".format(member.display_name)
		await ewrolemgr.updateRoles(client = cmd.client, member = member)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""
	Grants executive status
"""
async def promote(cmd):

	author = cmd.message.author
	
	if not author.server_permissions.administrator:
		return
	
	if cmd.mentions_count == 1:
		member = cmd.mentions[0]
		user_data = EwUser(member = member)
		user_data.life_state = ewcfg.life_state_executive
		user_data.persist()

		await ewrolemgr.updateRoles(client = cmd.client, member = member)

""" !piss """
async def piss(cmd):
	user_data = EwUser(member = cmd.message.author)
	mutations = user_data.get_mutations()

	if ewcfg.mutation_id_enlargedbladder in mutations:
		if cmd.mentions_count == 0:
			response = "You unzip your dick and just start pissing all over the goddamn fucking floor. God, you’ve waited so long for this moment, and it’s just as perfect as you could have possibly imagined. You love pissing so much."
			if random.randint(1,100) < 2:
				slimeoid = EwSlimeoid(member = cmd.message.author)
				if slimeoid.life_state == ewcfg.slimeoid_state_active:
					hue = ewcfg.hue_map.get("yellow")
					response = "CONGRATULATIONS. You suddenly lose control of your HUGE COCK and saturate your {} with your PISS. {}".format(slimeoid.name, hue.str_saturate)
					slimeoid.hue = (ewcfg.hue_map.get("yellow")).id_hue
					slimeoid.persist()
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		if cmd.mentions_count == 1:
			target_member = cmd.mentions[0]
			target_user_data = EwUser(member = target_member)
			
			if user_data.id_user == target_user_data.id_user:
				response = "Your love for piss knows no bounds. You aim your urine stream sky high, causing it to land right back into your own mouth. Mmmm, tasty~!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			
			if user_data.poi == target_user_data.poi:

				if target_user_data.life_state == ewcfg.life_state_corpse:
					response = "You piss right through them! Their ghostly form ripples as the stream of urine pours endlessly unto them."
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				
				if user_data.sap < ewcfg.sap_spend_piss:
					response = "You don't have enough liquid sap to !piss..."
				else:
					sap_damage_target = min(ewcfg.sap_crush_piss, target_user_data.hardened_sap)
					target_user_data.hardened_sap -= sap_damage_target
					target_user_data.persist()
					
					user_data.sap -= ewcfg.sap_spend_piss
					user_data.limit_fix()
					user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, (int(time.time()) + ewcfg.time_pvp_attack))
					user_data.persist()
					
					await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
					
					response = "You spend {} liquid sap to !piss HARD and FAST right onto {}!! They lose {} hardened sap!".format(ewcfg.sap_spend_piss, target_member.display_name, sap_damage_target)
			else:
				response = "You can't !piss on someone who isn't there! Moron!"

		elif cmd.mentions_count > 1:
			response = "Whoa, one water-sports fetishist at a time, pal!"
			
	else:
		response = "You lack the moral fiber necessary for urination."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""find out how many days are left until the 31st"""
async def fursuit(cmd):
	user_data = EwUser(member=cmd.message.author)
	mutations = user_data.get_mutations()
	market_data = EwMarket(id_server=cmd.message.server.id)

	if ewcfg.mutation_id_organicfursuit in mutations:
		days_until = -market_data.day % 31
		
		if days_until == 0:
			response = "Hair is beginning to grow on the surface of your skin rapidly. Your canine instincts will take over soon!"
		else:
			response = "With a basic hairy palm reading, you determine that you'll be particularly powerful in {} day{}.".format(days_until, "s" if days_until is not 1 else "")

		if ewutils.check_fursuit_active(user_data.id_server):
			response = "The full moon shines above! Now's your chance to strike!"
			
	else:
		response = "You're about as hairless as an egg, my friend."

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def pray(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	if cmd.message.channel.name != ewcfg.channel_endlesswar:
		response = "You must be in the presence of your lord if you wish to pray to him."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.chname_to_poi.get(cmd.message.channel.name)
	district_data = EwDistrict(district = poi.id_poi, id_server = cmd.message.server.id)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	if user_data.life_state == ewcfg.life_state_kingpin:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"https://i.imgur.com/WgnoDSA.gif"
		))
		await asyncio.sleep(9)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"https://i.imgur.com/M5GWGGc.gif"
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"https://i.imgur.com/fkLZ3XX.gif"
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"https://i.imgur.com/lUajXCs.gif"
		))
		await asyncio.sleep(9)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"https://i.imgur.com/FIuGl0C.png"
		))
		await asyncio.sleep(6)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"BUT SERIOUSLY, FOLKS... https://i.imgur.com/sAa0uwB.png"
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"IT'S SLIMERNALIA! https://i.imgur.com/lbLNJNC.gif"
		))
		await asyncio.sleep(6)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"***WHRRRRRRRRRRRR*** https://i.imgur.com/pvCfBQ2.gif"
		))
		await asyncio.sleep(6)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"***WHRRRRRRRRRRRR*** https://i.imgur.com/e2PY1VJ.gif"
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"DELICIOUS KINGPIN SLIME... https://i.imgur.com/2Cp1u43.png"
		))
		await asyncio.sleep(3)
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"JUST ENOUGH FOR A WEEK OR TWO OF CLEAR SKIES... https://i.imgur.com/L7T3V5b.gif"
		))
		await asyncio.sleep(9)
		await ewutils.send_message(cmd.client, cmd.message.channel,
			"@everyone Yo, Slimernalia! https://imgur.com/16mzAJT"
		)
		response = "NOW GO FORTH AND SPLATTER SLIME."
		market_data = EwMarket(id_server = cmd.message.server.id)
		market_data.weather = ewcfg.weather_sunny
		market_data.persist()

	else:
		# Generates a random integer from 1 to 100. If it is below the prob of poudrin, the player gets a poudrin.
		# If the random integer is above prob of poudrin but below probofpoud+probofdeath, then the player dies. Else,
		# the player is blessed with a response from EW.
		probabilityofpoudrin = 10
		probabilityofdeath = 10
		diceroll = random.randint(1, 100)

		# Redeem the player for their sins.
		market_data = EwMarket(id_server=cmd.message.server.id)
		market_data.global_swear_jar = max(0, market_data.global_swear_jar - 3)
		market_data.persist()
		user_data.swear_jar = max(0, user_data.swear_jar - 3)
		user_data.persist()

		if diceroll < probabilityofpoudrin: # Player gets a poudrin.
			item = random.choice(ewcfg.mine_results)

			item_props = ewitem.gen_item_props(item)

			ewitem.item_create(
				item_type = item.item_type,
				id_user = cmd.message.author.id,
				id_server = cmd.message.server.id,
				item_props = item_props
			)

			response = "ENDLESS WAR takes pity on you, and with a minor tremor he materializes a {} in your pocket.".format(item.str_name)

		elif diceroll < (probabilityofpoudrin + probabilityofdeath): # Player gets a face full of bone-hurting beam.
			response = "ENDLESS WAR doesn’t respond. You squint, looking directly into his eye, and think you begin to see particle effects begin to accumulate..."
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			await asyncio.sleep(3)

			user_data = EwUser(member = cmd.message.author)
			user_data.trauma = ewcfg.trauma_id_environment
			die_resp = user_data.die(cause = ewcfg.cause_praying)
			user_data.persist()
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
			await die_resp.post()

			response = "ENDLESS WAR completely and utterly obliterates you with a bone-hurting beam."

		else:
			responses_list = ewcfg.pray_responses_list

			if user_data.slimes > 1000000:
				responses_list = responses_list + ["ENDLESS WAR is impressed by your vast amounts of slime."]
			else:
				responses_list = responses_list + ["ENDLESS WAR can’t help but laugh at how little slime you have."]

			response = random.choice(responses_list)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

"""recycle your trash at the SlimeCorp Recycling plant"""
async def recycle(cmd):
	user_data = EwUser(member=cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = ""

	if cmd.message.channel.name != ewcfg.channel_recyclingplant:
		response = "You can only {} your trash at the SlimeCorp Recycling Plant in Smogsburg.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.chname_to_poi.get(cmd.message.channel.name)
	district_data = EwDistrict(district = poi.id_poi, id_server = cmd.message.server.id)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

	item_sought = ewitem.find_item(item_search = item_search, id_user = cmd.message.author.id, id_server = cmd.message.server.id if cmd.message.server is not None else None)
	
	if item_sought:
		item = EwItem(id_item = item_sought.get("id_item"))

		if not item.soulbound:
			if item.item_type == ewcfg.it_weapon and user_data.weapon >= 0 and item.id_item == user_data.weapon:
				if user_data.weaponmarried:
					weapon = ewcfg.weapon_map.get(item.item_props.get("weapon_type"))
					response = "Woah, wow, hold on there! Domestic violence is one thing, but how could you just throw your faithful {} into a glorified incinerator? Look, we all have bad days, but that's no way to treat a weapon. At least get a proper divorce first, you animal.".format(weapon.str_weapon)
					return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				else:
					user_data.weapon = -1
					user_data.persist()
			
			ewitem.item_delete(id_item = item.id_item)

			pay = int(random.random() * 10 ** random.randrange(2,6))
			response = "You put your {} into the designated opening. **CRUSH! Splat!** *hiss...* and it's gone. \"Thanks for keeping the city clean.\" a robotic voice informs you.".format(item_sought.get("name"))
			if pay == 0:
				item_reward = random.choice(ewcfg.mine_results)

				item_props = ewitem.gen_item_props(item_reward)

				ewitem.item_create(
					item_type = item_reward.item_type,
					id_user = cmd.message.author.id,
					id_server = cmd.message.server.id,
					item_props = item_props
				)

				ewstats.change_stat(user = user_data, metric = ewcfg.stat_lifetime_poudrins, n = 1)

				response += "\n\nYou receive a {}!".format(item_reward.str_name)
			else:
				user_data.change_slimecoin(n=pay, coinsource = ewcfg.coinsource_recycle)
				user_data.persist()

				response += "\n\nYou receive {:,} SlimeCoin.".format(pay)

		else:
			response = "You can't {} soulbound items.".format(cmd.tokens[0])
	else:
		if item_search:
			response = "You don't have one"
		else:
			response = "{} which item? (check **!inventory**)".format(cmd.tokens[0])

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def store_item(cmd):
	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	if poi.community_chest != None:
		return await ewfaction.store(cmd)
	elif poi.is_apartment:
		response = "Try that in a DM to ENDLESS WAR."
	else:
		response = "There is no storage here, public or private."
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def remove_item(cmd):
	user_data = EwUser(member = cmd.message.author)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	if poi.community_chest != None:
		return await ewfaction.take(cmd)
	elif poi.is_apartment:
		response = "Try that in a DM to ENDLESS WAR."
	else:
		response = "There is no storage here, public or private."
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def view_sap(cmd):
	user_data = EwUser(member = cmd.message.author)
	
	if cmd.mentions_count > 1:
		response = "One at a time."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	elif cmd.mentions_count == 1:
		member = cmd.mentions[0]
		target_data = EwUser(member = member)
		response = "{} has {} hardened sap and {} liquid sap.".format(member.display_name, target_data.hardened_sap, target_data.sap)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		response = "You have {} hardened sap and {} liquid sap.".format(user_data.hardened_sap, user_data.sap)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def push(cmd):
	time_now = int(time.time())
	user_data = EwUser(member=cmd.message.author)
	districtmodel = EwDistrict(id_server=cmd.message.server.id, district=ewcfg.poi_id_slimesendcliffs)

	if cmd.mentions_count == 0:
		response = "You try to push a nearby building. Nope, still not strong enough to move it."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif cmd.mentions_count >= 2:
		response = "You can't push more than one person at a time."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	target = cmd.mentions[0]
	targetmodel = EwUser(member=target)
	target_mutations = targetmodel.get_mutations()
	user_mutations = user_data.get_mutations()

	server = cmd.message.server

	if targetmodel.poi != user_data.poi:
		response = "You can't {} them because they aren't here.".format(cmd.tokens[0])
		
	elif cmd.message.channel.name != ewcfg.channel_slimesendcliffs:
		response = random.choice(ewcfg.bully_responses)

		formatMap = {}
		formatMap["target_name"] = target.display_name

		slimeoid_model = EwSlimeoid(id_server=cmd.message.server.id, id_user=targetmodel.id_user)
		if slimeoid_model.name != "":
			slimeoid_model = slimeoid_model.name
		else:
			slimeoid_model = ""

		cosmetics = ewitem.inventory(id_user=targetmodel.id_user, id_server=targetmodel.id_server, item_type_filter=ewcfg.it_cosmetic)
		selected_cos = None
		for cosmetic in cosmetics:
			cosmetic_item = EwItem(id_item=cosmetic.get('id_item'))
			if cosmetic_item.item_props.get('adorned') == "true":
				selected_cos = cosmetic
				break

		if selected_cos == None:
			selected_cos = "PANTS"
		else:
			selected_cos = id_item = selected_cos.get('name')

		formatMap["cosmetic"] = selected_cos.upper()

		if "{slimeoid}" in response:
			if slimeoid_model != "":
				formatMap["slimeoid"] = slimeoid_model
			elif slimeoid_model == "":
				response = "You push {target_name} into a puddle of sludge, laughing at how hopelessly dirty they are."
			
		response = response.format_map(formatMap)

	elif user_data.life_state == ewcfg.life_state_corpse:
		response = "You attempt to push {} off the cliff, but your hand passes through them. If you're going to push someone, make sure you're corporeal.".format(target.display_name)

	elif targetmodel.life_state == ewcfg.life_state_corpse:
		response = "You try to give ol' {} a shove, but they're a bit too dead to be taking up physical space.".format(target.display_name)

	elif time_now > targetmodel.time_expirpvp:
		# Target is not flagged for PvP.
		response = "{} is not mired in the ENDLESS WAR right now.".format(target.display_name)

	elif (ewcfg.mutation_id_bigbones in target_mutations or ewcfg.mutation_id_fatchance in target_mutations) and ewcfg.mutation_id_lightasafeather not in target_mutations:
		response = "You try to push {}, but they're way too heavy. It's always fat people, constantly trying to prevent your murderous schemes.".format(target.display_name)

	elif targetmodel.life_state == ewcfg.life_state_kingpin:
		response = "You sneak behind the kingpin and prepare to push. The crime you're about to commit is so heinous that you start snickering to yourself, and {} catches you in the act. Shit, mission failed.".format(target.display_name)

	elif ewcfg.mutation_id_lightasafeather in user_mutations:
		response = "You strain to push {} off the cliff, but your light frame gives you no lifting power.".format(target.display_name)

	else:
		response = "You push {} off the cliff and watch them scream in agony as they fall. Sea monsters frenzy on their body before they even land, gnawing them to jagged ribbons and gushing slime back to the clifftop.".format(target.display_name)

		if ewcfg.mutation_id_lightasafeather in target_mutations:
			response = "You pick {} up with your thumb and index finger, and gently toss them off the cliff. Wow. That was easy.".format(target.display_name)

		slimetotal = targetmodel.slimes * 0.75
		districtmodel.change_slimes(n=slimetotal)
		districtmodel.persist()

		cliff_inventory = ewitem.inventory(id_server=cmd.message.server.id, id_user=targetmodel.id_user)
		for item in cliff_inventory:
			item_object = ewitem.EwItem(id_item=item.get('id_item'))
			if item.get('soulbound') == True:
				pass

			elif item_object.item_type == ewcfg.it_weapon:
				if item.get('id_item') == targetmodel.weapon:
					ewitem.give_item(id_item=item_object.id_item, id_user=ewcfg.poi_id_slimesea, id_server=cmd.message.server.id)

				else:
					item_off(id_item=item.get('id_item'), is_pushed_off=True, item_name=item.get('name'), id_server=cmd.message.server.id)


			elif item_object.item_props.get('adorned') == 'true':
				ewitem.give_item(id_item=item_object.id_item, id_user=ewcfg.poi_id_slimesea, id_server=cmd.message.server.id)

			else:
				item_off(id_item=item.get('id_item'), is_pushed_off=True, item_name=item.get('name'), id_server=cmd.message.server.id)



		targetmodel.trauma = ewcfg.trauma_id_environment
		die_resp = targetmodel.die(cause = ewcfg.cause_cliff)
		targetmodel.persist()

		# Flag the user for PvP
		user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, (int(time.time()) + ewcfg.time_pvp_kill))
		user_data.persist()

		await ewrolemgr.updateRoles(client = cmd.client, member = target)
		await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

		await die_resp.post()

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def jump(cmd):
	user_data = EwUser(member=cmd.message.author)

	if cmd.message.channel.name != ewcfg.channel_slimesendcliffs:
		response = "You jump. Nope. Still not good at parkour."
	elif user_data.life_state == ewcfg.life_state_corpse:
		response = "You're already dead. You'd just ghost hover above the cliff."
	elif user_data.life_state == ewcfg.life_state_kingpin:
		response = "You try to end things right here. Sadly, the gangster sycophants that kiss the ground you walk on grab your ankles in desperation and prevent you from suicide. Oh, the price of fame."
	else:
		response = "Hmm. The cliff looks safe enough. You imagine, with the proper diving posture, you'll be able to land in the slime unharmed. You steel yourself for the fall, run along the cliff, and swan dive off its steep edge. Of course, you forgot that the Slime Sea is highly corrosive, there are several krakens there, and you can't swim. Welp, time to die."

		cliff_inventory = ewitem.inventory(id_server=cmd.message.server.id, id_user=user_data.id_user)
		for item in cliff_inventory:
			item_object = ewitem.EwItem(id_item=item.get('id_item'))
			if item.get('soulbound') == True:
				pass

			elif item_object.item_type == ewcfg.it_weapon:
				if item.get('id_item') == user_data.weapon:
					ewitem.give_item(id_item=item_object.id_item, id_user=ewcfg.poi_id_slimesea, id_server=cmd.message.server.id)

				else:
					item_off(id_item=item.get('id_item'), is_pushed_off=True, item_name=item.get('name'), id_server=cmd.message.server.id)


			elif item_object.item_props.get('adorned') == 'true':
				ewitem.give_item(id_item=item_object.id_item, id_user=ewcfg.poi_id_slimesea, id_server=cmd.message.server.id)

			else:
				item_off(id_item=item.get('id_item'), is_pushed_off=True, item_name=item.get('name'), id_server=cmd.message.server.id)

		targetmodel.trauma = ewcfg.trauma_id_environment
		die_resp = user_data.die(cause = ewcfg.cause_cliff)
		user_data.persist()
		await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
		if die_resp != ewutils.EwResponseContainer(id_server = cmd.message.server.id):
			await die_resp.post()
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def toss_off_cliff(cmd):
	user_data = EwUser(member=cmd.message.author)
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=user_data.id_server)

	if cmd.message.channel.name != ewcfg.channel_slimesendcliffs:
		if item_sought:
			if item_sought.get('name')=="brick" and cmd.mentions_count > 0:
				item = EwItem(id_item=item_sought.get('id_item'))
				target = EwUser(member = cmd.mentions[0])
				if target.apt_zone == user_data.poi:
					item.id_owner = str(cmd.mentions[0].id) + ewcfg.compartment_id_decorate
					item.persist()
					response = "You throw a brick through {}'s window. Oh shit! Quick, scatter before they see you!".format(cmd.mentions[0].display_name)
					if ewcfg.id_to_poi.get(target.poi).is_apartment	and target.visiting == ewcfg.location_id_empty:
						try:
							await ewutils.send_message(cmd.client, cmd.mentions[0], ewutils.formatMessage(cmd.mentions[0], "SMAAASH! A brick flies through your window!"))
						except:
							ewutils.logMsg("failed to send brick message to user {}".format(target.id_user))
				elif target.poi == user_data.poi:
					if target.life_state == ewcfg.life_state_corpse:
						response = "You reel back and chuck the brick at a ghost. As much as we both would like to teach the dirty staydead a lesson, the brick passes right through."
						item.id_owner = target.poi
						item.persist()
					elif target.life_state == ewcfg.life_state_shambler:
						response = "The brick is buried into the shambler's soft, malleable head, but the decayed fellow doesn't seem to notice. It looks like it phased into its inventory."
						item.id_owner = target.id_user
						item.persist()
					elif target.life_state == ewcfg.life_state_kingpin:
						response = "The brick is hurtling toward the kingpin's head, but they've long since gotten used to bricks to the head. It bounces off like nothing."
						item.id_owner = target.poi
						item.persist()
					else:
						response = ":bricks::boom: BONK! The brick slams against {}'s head!".format(cmd.mentions[0].display_name)
						item.id_owner = target.poi
						item.persist()
						try:
							await ewutils.send_message(cmd.client, cmd.mentions[0], ewutils.formatMessage(cmd.mentions[0], random.choice(["!!!!!!", "BRICK!", "FUCK", "SHIT", "?!?!?!?!?", "BONK!", "F'TAAAAANG!", "SPLAT!", "SPLAPP!", "WHACK"])))
						except:
							ewutils.logMsg("failed to send brick message to user {}".format(target.id_user))
				else:
					response = "There's nobody here."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			else:
				return await ewitem.discard(cmd=cmd)

	elif item_sought:
		item_obj = EwItem(id_item=item_sought.get('id_item'))
		if item_obj.soulbound == True:
			response = "That's soulbound. You can't get rid of it just because you're in a more dramatic looking place."

		elif item_obj.item_type == ewcfg.it_weapon and user_data.weapon >= 0 and item_obj.id_item == user_data.weapon:
			if user_data.weaponmarried:
				weapon = ewcfg.weapon_map.get(item_obj.item_props.get("weapon_type"))
				response = "You decide not to chuck your betrothed off the cliff because you care about them very very much. See {}? I'm not going to hurt you. You don't have to call that social worker again.".format(weapon.str_weapon)
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

			else:
				response = item_off(item_sought.get('id_item'), user_data.id_server, item_sought.get('name'))
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		else:
			response = item_off(item_sought.get('id_item'), user_data.id_server, item_sought.get('name'))
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		response = "You don't have that item."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))




def item_off(id_item, id_server, item_name = "", is_pushed_off = False):
	item_obj = EwItem(id_item=id_item)
	districtmodel = EwDistrict(id_server=id_server, district=ewcfg.poi_id_slimesendcliffs)
	slimetotal = 0

	if random.randrange(500) < 125 or item_obj.item_type == ewcfg.it_questitem or item_obj.item_type == ewcfg.it_medal or item_obj.item_props.get('rarity') == ewcfg.rarity_princeps or item_obj.item_props.get('id_cosmetic') == "soul" or item_obj.item_props.get('id_furniture') == "propstand":
		response = "You toss the {} off the cliff. It sinks into the ooze disappointingly.".format(item_name)
		ewitem.give_item(id_item=id_item, id_server=id_server, id_user=ewcfg.poi_id_slimesea)

	elif random.randrange(500) < 498:
		response = "You toss the {} off the cliff. A nearby kraken swoops in and chomps it down with the cephalapod's equivalent of a smile. Your new friend kicks up some sea slime for you. Sick!".format(item_name)
		slimetotal = 2000 + random.randrange(10000)
		ewitem.item_delete(id_item=id_item)

	else:
		response = "{} Oh fuck. FEEDING FRENZY!!! Sea monsters lurch down on the spoils like it's fucking christmas, and a ridiculous level of slime debris covers the ground. {}".format(ewcfg.emote_slime1, ewcfg.emote_slime1)
		slimetotal = 100000 + random.randrange(900000)

		ewitem.item_delete(id_item=id_item)

	districtmodel.change_slimes(n=slimetotal)
	districtmodel.persist()
	return response


async def purify(cmd):
	user_data = EwUser(member=cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	
	if cmd.message.channel.name == ewcfg.channel_sodafountain:
		poi = ewcfg.chname_to_poi.get(cmd.message.channel.name)
		district_data = EwDistrict(district = poi.id_poi, id_server = cmd.message.server.id)

		if district_data.is_degraded():
			response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		if user_data.life_state == ewcfg.life_state_corpse:
			response = "You're too ghastly for something like that. Besides, you couldn't even touch the water if you wanted to, it would just phase right through your ghostly form."
		else:
			if user_data.slimelevel < 50:
				response = "You're not big enough in slime levels to be worthy of purification"
			else:
				response = "You close your eyes and hold out your hands to the gentle waters of the bicarbonate soda fountain..."
				
				user_data.slimelevel = 1
				user_data.slimes = 0
				user_data.hardened_sap = 0
				
				new_weaponskill = int(user_data.weaponskill * 0.75)
				
				ewutils.weaponskills_clear(id_server = user_data.id_server, id_user = user_data.id_user, weaponskill = new_weaponskill)
				
				user_data.persist()
				
				response += "\n\nYou have purified yourself and are now a level 1 slimeboi.\nThe bond you've forged with your weapon has grown weaker as a result."
	else:
		response = "Purify yourself how? With what? Your own piss?"
		
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def flush_subzones(cmd):
	member = cmd.message.author
	
	if not member.server_permissions.administrator:
		return
	
	subzone_to_mother_district = {}

	for poi in ewcfg.poi_list:
		if poi.is_subzone:
			subzone_to_mother_district[poi.id_poi] = poi.mother_district


	for subzone in subzone_to_mother_district:
		mother_district = subzone_to_mother_district.get(subzone)
		
		ewutils.execute_sql_query("UPDATE items SET {id_owner} = %s WHERE {id_owner} = %s AND {id_server} = %s".format(
			id_owner = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server
		), (
			mother_district,
			subzone,
			cmd.message.server.id
		))

		subzone_data = EwDistrict(district = subzone, id_server = cmd.message.server.id)
		district_data = EwDistrict(district = mother_district, id_server = cmd.message.server.id)

		district_data.change_slimes(n = subzone_data.slimes)
		subzone_data.change_slimes(n = -subzone_data.slimes)

		district_data.persist()
		subzone_data.persist()
	
async def wrap(cmd):
	
	if cmd.tokens_count != 4:
		response = 'To !wrap a gift, you need to specify a recipient, message, and item, like so:\n```!wrap @munchy#6443 "Sample text." chickenbucket```'
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)
	
	if cmd.mentions_count == 0:
		response = "Who exactly are you giving your gift to?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	if cmd.mentions_count > 1:
		response = "Back it up man, the rules are one gift for one person!"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	recipient = cmd.mentions[0]
	recipient_data = EwUser(member=recipient)
	
	member = cmd.message.author
	user_data = EwUser(member=cmd.message.author)
	
	if recipient_data.id_user == user_data.id_user:
		response = "C'mon man, you got friends, don't you? Try and give a gift to someone other than yourself."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	paper_sought = ewitem.find_item(item_search="wrappingpaper", id_user=cmd.message.author.id, id_server=cmd.message.server.id, item_type_filter = ewcfg.it_item)
	
	if paper_sought:
		paper_item = EwItem(id_item=paper_sought.get('id_item'))
	
	if paper_sought and paper_item.item_props.get('context') == ewcfg.context_wrappingpaper:
		paper_name = paper_sought.get('name')
	else:
		response = "How are you going to wrap a gift without any wrapping paper?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	gift_message = cmd.tokens[2]
	
	item_search = ewutils.flattenTokenListToString(cmd.tokens[3:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.message.server.id)

	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item.item_type == ewcfg.it_item:
			if item.item_props.get('id_item') == "gift":
				response = "It's already wrapped."
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		if item.soulbound:
			response = "It's a nice gesture, but trying to gift someone a Soulbound item is going a bit too far, don't you think?"
		else:
			gift_name = "Gift"
			
			gift_address = 'To {}, {}. From, {}'.format(recipient.display_name, gift_message, member.display_name,)
			
			gift_desc = "A gift wrapped in {}. Wonder what's inside?\nThe front of the tag reads '{}'\nOn the back of the tag, an ID number reads **({})**.".format(paper_name, gift_address, item.id_item)

			response = "You shroud your {} in {} and slap on a premade bow. Onto it, you attach a note containing the following text: '{}'.\nThis small act of kindness manages to endow you with Slimernalia spirit, if only a little.".format(item_sought.get('name'), paper_name, gift_address)
			
			ewitem.item_create(
				id_user=cmd.message.author.id,
				id_server=cmd.message.server.id,
				item_type=ewcfg.it_item,
				item_props={
					'item_name': gift_name,
					'id_item': "gift",
					'item_desc': gift_desc,
					'context': gift_address,
					'acquisition': "{}".format(item_sought.get('id_item')),
					# flag indicating if the gift has already been given once so as to not have people farming festivity through !giving
					'gifted': "false"
				}
			)
			ewitem.give_item(id_item=item_sought.get('id_item'), id_user=cmd.message.author.id + "gift", id_server=cmd.message.server.id)
			ewitem.item_delete(id_item=paper_item.id_item)

			user_data.persist()
	else:
		if item_search == "" or item_search == None:
			response = "Specify the item you want to wrap."
		else:
			response = "Are you sure you have that item?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def unwrap(cmd):
	item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
	item_sought = ewitem.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.message.server.id)
	if item_sought:
		item = ewitem.EwItem(id_item=item_sought.get('id_item'))
		if item.item_type == ewcfg.it_item:
			if item.item_props.get('id_item') == "gift":
				ewitem.give_item(id_item=item.item_props.get('acquisition'), id_user=cmd.message.author.id, id_server=cmd.message.server.id)
				
				gifted_item = EwItem(id_item=item.item_props.get('acquisition'))
				
				gift_name_type = ''
				if gifted_item.item_type == ewcfg.it_item:
					gift_name_type = 'item_name'
				elif gifted_item.item_type == ewcfg.it_medal:
					gift_name_type = 'medal_name'
				elif gifted_item.item_type == ewcfg.it_questitem:
					gift_name_type = 'qitem_name'
				elif gifted_item.item_type == ewcfg. it_food:
					gift_name_type = 'food_name'
				elif gifted_item.item_type == ewcfg.it_weapon:
					gift_name_type = 'weapon_name'
				elif gifted_item.item_type == ewcfg.it_cosmetic:
					gift_name_type = 'cosmetic_name'
				elif gifted_item.item_type == ewcfg.it_furniture:
					gift_name_type = 'furniture_name'
				elif gifted_item.item_type == ewcfg.it_book:
					gift_name_type = 'title'
				
				gifted_item_name = gifted_item.item_props.get('{}'.format(gift_name_type))
				gifted_item_message = item.item_props.get('context')
				
				response = "You shred through the packaging formalities to reveal a {}!\nThere is a note attached: '{}'.".format(gifted_item_name, gifted_item_message)
				ewitem.item_delete(id_item=item_sought.get('id_item'))
			else:
				response = "You can't unwrap something that isn't a gift, bitch."
		else:
			response = "You can't unwrap something that isn't a gift, bitch."
	else:
		response = "Are you sure you have that item?"
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def yoslimernalia(cmd):
	await ewutils.send_message(cmd.client, cmd.message.channel, '@everyone Yo, Slimernalia!')

async def confirm(cmd):
	return

async def cancel(cmd):
	return

# Show a player's festivity
async def festivity(cmd):
	if cmd.mentions_count == 0:
		user_data = EwUser(member = cmd.message.author)
		response = "You currently have {:,} festivity.".format(user_data.get_festivity())

	else:
		member = cmd.mentions[0]
		user_data = EwUser(member = member)
		response = "{} currently has {:,} festivity.".format(member.display_name, user_data.get_festivity())

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
