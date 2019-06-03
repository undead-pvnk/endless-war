"""
	Commands and utilities related to dead players.
"""
import time
import random

import ewcmd
import ewcfg
import ewutils
import ewmap
import ewrolemgr
import ewslimeoid
from ew import EwUser
from ewmarket import EwMarket
from ewslimeoid import EwSlimeoid

""" revive yourself from the dead. """
async def revive(cmd):
	time_now = int(time.time())
	response = ""

	if cmd.message.channel.name != ewcfg.channel_endlesswar and cmd.message.channel.name != ewcfg.channel_sewers:
		response = "Come to me. I hunger. #{}.".format(ewcfg.channel_sewers)
	else:
		player_data = EwUser(member = cmd.message.author)
		slimeoid = EwSlimeoid(member = cmd.message.author)

		if player_data.life_state == ewcfg.life_state_corpse:
			market_data = EwMarket(id_server = cmd.message.server.id)

			# Endless War collects his fee.
			fee = (player_data.slimecoin / 10)
			player_data.change_slimecoin(n = -fee, coinsource = ewcfg.coinsource_revival)
			market_data.slimes_revivefee += fee
			player_data.busted = False
			
			# Preserve negaslime
			if player_data.slimes < 0:
				market_data.negaslime += player_data.slimes
				player_data.change_slimes(n = -player_data.slimes) # set to 0

			# Give player some initial slimes.
			player_data.slimelevel = 0
			player_data.change_slimes(n = ewcfg.slimes_onrevive)

			# Set time of last revive. This used to provied spawn protection, but currently isn't used.
			player_data.time_lastrevive = time_now

			# Set life state. This is what determines whether the player is actually alive.
			player_data.life_state = ewcfg.life_state_juvenile

			# Get the player out of the sewers.
			player_data.poi = ewcfg.poi_id_endlesswar

			player_data.persist()
			market_data.persist()

			# Give some slimes to every living player (currently online)
			for member in cmd.message.server.members:
				if member.id != cmd.message.author.id and member.id != cmd.client.user.id:
					member_data = EwUser(member = member)

					if member_data.life_state != ewcfg.life_state_corpse and member_data.life_state != ewcfg.life_state_grandfoe:
						member_data.change_slimes(n = ewcfg.slimes_onrevive_everyone)
						member_data.persist()

			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

			response = '{slime4} A geyser of fresh slime erupts, showering Rowdy, Killer, and Juvenile alike. {slime4} {name} has been reborn in slime. {slime4}'.format(slime4 = ewcfg.emote_slime4, name = cmd.message.author.display_name)
		else:
			response = 'You\'re not dead just yet.'

	#	deathreport = "You were {} by {}. {}".format(kill_descriptor, cmd.message.author.display_name, ewcfg.emote_slimeskull)
	#	deathreport = "{} ".format(ewcfg.emote_slimeskull) + ewutils.formatMessage(member, deathreport)

		if slimeoid.life_state == ewcfg.slimeoid_state_active:
			reunite = ""
			brain = ewcfg.brain_map.get(slimeoid.ai)
			reunite += brain.str_revive.format(
			slimeoid_name = slimeoid.name
			)
			new_poi = ewcfg.id_to_poi.get(player_data.poi)
			revivechannel = ewutils.get_channel(cmd.message.server, new_poi.channel)
			reunite = ewutils.formatMessage(cmd.message.author, reunite)
			await ewutils.send_message(cmd.client, revivechannel, reunite)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" haunt living players to steal slime """
async def haunt(cmd):
	time_now = int(time.time())
	response = ""

	if cmd.mentions_count > 1:
		response = "You can only spook one person at a time. Who do you think you are, the Lord of Ghosts?"
	elif cmd.mentions_count == 1:
		# Get the user and target data from the database.
		user_data = EwUser(member = cmd.message.author)

		member = cmd.mentions[0]
		haunted_data = EwUser(member = member)
		market_data = EwMarket(id_server = cmd.message.server.id)

		if user_data.life_state != ewcfg.life_state_corpse:
			# Only dead players can haunt.
			response = "You can't haunt now. Try {}.".format(ewcfg.cmd_suicide)
		elif haunted_data.life_state == ewcfg.life_state_kingpin:
			# Disallow haunting of generals.
			response = "He is too far from the sewers in his ivory tower, and thus cannot be haunted."
		elif (time_now - user_data.time_lasthaunt) < ewcfg.cd_haunt:
			# Disallow haunting if the user has haunted too recently.
			response = "You're being a little TOO spooky lately, don't you think?"
		elif ewmap.channel_name_is_poi(cmd.message.channel.name) == False:
			response = "You can't commit violence from here."
		elif ewmap.poi_is_pvp(haunted_data.poi) == False:
			# Require the target to be flagged for PvP
			response = "{} is not mired in the ENDLESS WAR right now.".format(member.display_name)
		elif haunted_data.life_state == ewcfg.life_state_corpse:
			# Dead players can't be haunted.
			response = "{} is already dead.".format(member.display_name)
		elif haunted_data.life_state == ewcfg.life_state_grandfoe:
			# Grand foes can't be haunted.
			response = "{} is invulnerable to ghosts.".format(member.display_name)
		elif haunted_data.life_state == ewcfg.life_state_enlisted or haunted_data.life_state == ewcfg.life_state_juvenile:
			# Target can be haunted by the player.
			haunted_slimes = int(haunted_data.slimes / ewcfg.slimes_hauntratio)
			if user_data.poi == haunted_data.poi:  # when haunting someone face to face, there is no cap and you get double the amount
				haunted_slimes *= 2
			elif haunted_slimes > ewcfg.slimes_hauntmax:
				haunted_slimes = ewcfg.slimes_hauntmax

			if -user_data.slimes < haunted_slimes:  # cap on for how much you can haunt
				haunted_slimes = -user_data.slimes

			haunted_data.change_slimes(n = -haunted_slimes, source = ewcfg.source_haunted)
			user_data.change_slimes(n = -haunted_slimes, source = ewcfg.source_haunter)
			market_data.negaslime -= haunted_slimes
			user_data.time_lasthaunt = time_now
			user_data.busted = False

			# Persist changes to the database.
			user_data.persist()
			haunted_data.persist()
			market_data.persist()

			response = "{} has been haunted by the ghost of {}! Slime has been lost!".format(member.display_name, cmd.message.author.display_name)
		else:
			# Some condition we didn't think of.
			response = "You cannot haunt {}.".format(member.display_name)
	else:
		# No mentions, or mentions we didn't understand.
		response = "Your spookiness is appreciated, but ENDLESS WAR didn\'t understand that name."

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def negaslime(cmd):
	# Add persisted negative slime.
	market_data = EwMarket(id_server = cmd.message.server.id)
	negaslime = market_data.negaslime

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "The dead have amassed {:,} negative slime.".format(negaslime)))

async def summon_negaslimeoid(cmd):
	response = ""
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state != user_data.life_state_corpse:
		response = "Only the dead have the occult knowledge required to summon a cosmic horror."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.poi not in ewcfg.capturable_districts:
		response = "You can't conduct the ritual here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))



	value = None
	if cmd.tokens_count > 1:
		value = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True, negate = True)
	if value != None:
		slimeoid = EwSlimeoid(member = cmd.message.author, sltype = ewcfg.sltype_nega)
		if slimeoid.life_state != ewcfg.slimeoid_state_none:
			response = "You already have an active negaslimeoid."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		market_data = EwMarket(id_server = cmd.message.author.server.id)
		if value < 0:
			value = -user_data.slimes * 10
		if -value / 10 < user_data.slimes:
			response = "You do not have enough negative slime to use in the ritual."
		elif -value < market_data.negaslime:
			response = "The dead have not gathered enough negative slime."

		else:
			level = len(str(value))
			user_data.change_slimes(n = int(value/10))
			market_data.negaslime += value
			slimeoid.life_state = ewcfg.slimeoid_state_active
			slimeoid.level = level
			slimeoid.id_user = user_data.id_user
			slimeoid.id_server = user_data.id_server
			slimeoid.poi = user_data.poi
			slimeoid.name = generate_negaslimeoid_name()
			slimeoid.body = random.choice(ewcfg.body_names)
			slimeoid.head = random.choice(ewcfg.head_names)
			slimeoid.legs = random.choice(ewcfg.mobility_names)
			slimeoid.armor = random.choice(ewcfg.defense_names)
			slimeoid.weapon = random.choice(ewcfg.offense_names)
			slimeoid.special = random.choice(ewcfg.special_names)
			slimeoid.ai = random.choice(ewcfg.brain_names)
			for i in range(level):
				rand = random.randrange(3)
				if rand == 0:
					slimeoid.atk += 1
				elif rand == 1:
					slimeoid.defense += 1
				else:
					slimeoid.intel += 1



			user_data.persist()
			slimeoid.persist()

			response = "You have summoned **{}**, a {}-feet tall Negaslimeoid.".format(slimeoid.name, slimeoid.level)
			desc = ewslimeoid.slimeoid_describe(slimeoid)
			response += "\n\n" + desc

	else:
		response = "Specify how much negative slime you will sacrifice."
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

def generate_negaslimeoid_name():
	titles = ["Angel", "Emissary", "Gaping Maw", "Apostle", "Nemesis", "Harbinger", "Reaper", "Incarnation", "Wanderer", "Berserker", "Outcast", "Monarch", "Anomaly"]
	domains = ["Curses", "Doom", "Oblivion", "Darkness", "Madness", "the Void", "the Deep", "Nightmares", "Wrath", "Pestilence", "the End", "Terror", "Sorrow", "Pain", "Despair", "Souls", "Secrets", "Ruin", "Hatred", "Shadows", "the Night"]
	title = "{} of {}".format(random.choice(titles), random.choice(domains))
	name_length = random.randrange(5,min(10,31-len(title)))
	consonants = random.choice(["chlt","crwx","fhlt","bghl","brpq"])
	vowels = "aeuuooyy"
	num_vowels = random.randrange(int(name_length / 4), int(name_length/3)+1)
	name_list = []
	for i in range(name_length):
		if i < num_vowels:
			name_list.append(random.choice(vowels))
		else:
			name_list.append(random.choice(consonants))
	random.shuffle(name_list)
	apostrophe = random.randrange(1,name_length)
	name = ewutils.flattenTokenListToString(name_list[:apostrophe]) + "'" + ewutils.flattenTokenListToString(name_list[apostrophe:])
	name = name.capitalize()
	full_name = "{}, {}".format(name, title)
	return full_name
