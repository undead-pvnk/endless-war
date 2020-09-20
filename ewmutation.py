import asyncio
import math
import time
import random

import discord

import ewcfg
import ewstats
import ewutils
import ewitem
from ewmarket import EwMarket
from ewplayer import EwPlayer

from ew import EwUser
from ewstatuseffects import EwStatusEffect
from ewdistrict import EwDistrict

class EwMutationFlavor:

	# The mutation's name
	id_mutation = ""

	# String used to describe the mutation when you !data yourself
	str_describe_self = ""

	# String used to describe the mutation when you !data another player
	str_describe_other = ""

	# String used when you acquire the mutation
	str_acquire = ""

	#The level of the mutation
	tier = 0

	#String used when you transplant a mutation
	str_transplant = ""

	#Alternate names for the mutation
	alias = []

	def __init__(self,
		id_mutation = "",
		str_describe_self = "",
		str_describe_other = "",
		str_acquire = "",
		tier = 1,
		str_transplant = "",
		alias = None):

		self.id_mutation = id_mutation

		if str_describe_self == "":
			str_describe_self = "You have the {} mutation.".format(self.id_mutation)
		self.str_describe_self = str_describe_self

		if str_describe_other == "":
			str_describe_other = "They have the {} mutation.".format(self.id_mutation)
		self.str_describe_other = str_describe_other

		if str_acquire == "":
			str_acquire = "You have acquired the {} mutation.".format(self.id_mutation)
		self.str_acquire = str_acquire

		if tier == "":
			tier = 5
		self.tier = tier

		if str_transplant == "":
			str_transplant = "Auntie Dusttrap injects a syringe full of carcinogens into your back. You got the {} mutation!".format(self.id_mutation)
		self.str_transplant = str_transplant

		if alias == None:
			alias = []
		self.alias = alias

class EwMutation:
	id_server = -1
	id_user = -1
	id_mutation = ""

	data = ""
	#whether or not a mutation is gained through surgery
	artificial = 0

	#the level of a mutation
	tier = 0

	# unique id for every instance of a mutation. auto increments
	# a counter of -1 means the player doesn't have this mutation
	mutation_counter = -1

	""" Create a new EwMutation and optionally retrieve it from the database. """
	def __init__(self, id_user = None, id_server = None, id_mutation = None):
		# Retrieve the object from the database if the user is provided.
		if(id_user != None) and (id_server != None) and (id_mutation != None):
			self.id_server = id_server
			self.id_user = id_user
			self.id_mutation = id_mutation

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute("SELECT {data}, {mutation_counter}, {tier}, {artificial} FROM mutations WHERE id_user = %s AND id_server = %s AND {id_mutation} = %s".format(
					data = ewcfg.col_mutation_data,
					mutation_counter = ewcfg.col_mutation_counter,
					id_mutation = ewcfg.col_id_mutation,
					tier = ewcfg.col_tier,
					artificial = ewcfg.col_artificial
				), (
					id_user,
					id_server,
					id_mutation,
				))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.data = result[0]
					self.mutation_counter = result[1]

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save this mutation object to the database. """
	def persist(self):
	
		try:
			# Get database handles if they weren't passed.
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();


			# Save the object.
			cursor.execute("REPLACE INTO mutations(id_user, id_server, {id_mutation}, {data}, {mutation_counter}, {tier}, {artificial},) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
					id_mutation = ewcfg.col_id_mutation,
					data = ewcfg.col_mutation_data,
					mutation_counter = ewcfg.col_mutation_counter,
					tier = ewcfg.col_tier,
					artificial = ewcfg.col_artificial
				), (
					self.id_user,
					self.id_server,
					self.id_mutation,
					self.data,
					self.mutation_counter,
					self.tier,
					self.artificial
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

	def clear(self):
		try:
			ewutils.execute_sql_query("DELETE FROM mutations WHERE {mutation_counter} = %s".format(
					mutation_counter = ewcfg.col_mutation_counter
				),(
					self.mutation_counter
				))
		except:
			ewutils.logMsg("Failed to clear mutation {} for user {}.".format(self.id_mutation, self.id_user))

async def reroll_last_mutation(cmd):
	last_mutation_counter = -1
	last_mutation = ""
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	market_data = EwMarket(id_server = user_data.id_server)
	response = ""

	if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
		response = "You require the advanced equipment at the Slimeoid Lab to modify your mutations."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	if user_data.life_state == ewcfg.life_state_corpse:
		response = "How do you expect to mutate without exposure to slime, dumbass?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	mutations = user_data.get_mutations()
	if len(mutations) == 0:
		response = "You have not developed any specialized mutations yet."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	for id_mutation in mutations:
		mutation_data = EwMutation(id_server = user_data.id_server, id_user = user_data.id_user, id_mutation = id_mutation)
		if mutation_data.mutation_counter > last_mutation_counter:
			last_mutation_counter = mutation_data.mutation_counter
			last_mutation = id_mutation

	reroll_fatigue = EwStatusEffect(id_status = ewcfg.status_rerollfatigue_id, user_data = user_data)

	poudrins_needed = int(1.5 ** int(reroll_fatigue.value))

	poudrins = ewitem.find_item_all(item_search = ewcfg.item_id_slimepoudrin, id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None, item_type_filter = ewcfg.it_item)

	poudrins_have = len(poudrins)

	if poudrins_have < poudrins_needed:
		response = "You need {} slime poudrin{} to replace a mutation, but you only have {}.".format(poudrins_needed, "" if poudrins_needed == 1 else "s", poudrins_have)

		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		for delete in range(poudrins_needed):
			ewitem.item_delete(id_item = poudrins.pop(0).get('id_item'))  # Remove Poudrins
		market_data.donated_poudrins += poudrins_needed
		market_data.persist()
		user_data.poudrin_donations += poudrins_needed
		user_data.persist()
		reroll_fatigue.value = int(reroll_fatigue.value) + 1
		reroll_fatigue.persist()

	mutation_data = EwMutation(id_server = user_data.id_server, id_user = user_data.id_user, id_mutation = last_mutation)
	new_mutation = random.choice(list(ewcfg.mutation_ids))
	while new_mutation in mutations:
		new_mutation = random.choice(list(ewcfg.mutation_ids))

	mutation_data.id_mutation = new_mutation
	mutation_data.time_lastuse = int(time.time())
	mutation_data.persist()

	response = "After several minutes long elevator descents, in the depths of some basement level far below the laboratory's lobby, you lay down on a reclined medical chair. A SlimeCorp employee finishes the novel length terms of service they were reciting and asks you if you have any questions. You weren’t listening so you just tell them to get on with it so you can go back to getting slime. They oblige.\nThey grab a butterfly needle and carefully stab you with it, draining some strangely colored slime from your bloodstream. Almost immediately, the effects of your last mutation fade away… but, this feeling of respite is fleeting. The SlimeCorp employee writes down a few notes, files away the freshly drawn sample, and soon enough you are stabbed with syringes. This time, it’s already filled with some bizarre, multi-colored serum you’ve never seen before. The effects are instantaneous. {}\nYou hand off {} of your hard-earned poudrins to the SlimeCorp employee for their troubles.".format(ewcfg.mutations_map[new_mutation].str_acquire, poudrins_needed)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def chemo(cmd):
	user_data = EwUser(member=cmd.message.author)

	if cmd.message.channel.name != ewcfg.channel_goonyinfirmary:
		response = "Chemotherapy doesn't just grow on trees. You'll need to go to Goony Infirmary in Poudrin Alley to get some."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.life_state == ewcfg.life_state_shambler:
		response = '"Oh goodness me, it seems like another one of these decaying subhumans has wandered into my office. Go on, shoo!"\n\nTough luck, seems shamblers aren\'t welcome here.'.format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.life_state == ewcfg.life_state_corpse:
		response = '"You get out of here. We don\'t serve your kind." \n\n Auntie Dusttrap threatingly flails a jar of cole slaw at you. Looks like you need a body to operate on one.'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	mutations = user_data.get_mutations()
	if len(mutations) == 0:
		response = '"I can chemo you all day long, sonny. You\'re not getting any cleaner than you are."'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif len(cmd.tokens) <= 1:
		response = '"Are you into chemo for the thrill, boy? You have to tell me what you want taken out."'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif cmd.tokens[1] == "all":

		for mutation in mutations:
			mutation_obj = EwMutation(id_mutation=mutation, id_user=user_data.id_user, id_server=cmd.message.guild.id)
			if mutation_obj.artificial == 0:
				try:
					ewutils.execute_sql_query(
						"DELETE FROM mutations WHERE {id_server} = %s AND {id_user} = %s AND {mutation} = %s".format(
							id_server=ewcfg.col_id_server,
							id_user=ewcfg.col_id_user,
							mutation=ewcfg.col_id_mutation
						), (
							user_data.id_server,
							user_data.id_user,
							mutation,
						))
				except:
					ewutils.logMsg("Failed to clear mutations for user {}.".format(user_data.id_user))
			response = '"Everything, eh? All right then. This might hurt a lottle!" Auntie Dusttrap takes a specialized shop vac and sucks the slime out of you. While you\'re reeling in slimeless existential dread, she runs it through a filtration process that gets rid of the carcinogens that cause mutation. She grabs the now purified canister and haphazardly dumps it back into you. You feel pure, energized, and ready to dirty up your slime some more!'
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
		target = ewutils.get_mutation_alias(target_name)
		mutation_obj = EwMutation(id_mutation=target, id_user=user_data.id_user, id_server=cmd.message.guild.id)

		if target == 0:
			response = '"I don\'t know what kind of gold-rush era disease that is, but I have no idea how to take it out of you."'
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif target not in mutations:
			response = '"Oy vey, another hypochondriac. You don\'t have that mutation, so I can\'t remove it."'
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif ewcfg.mutations_map.get(target).tier * 5000 < user_data.slimes:
			response = '"We\'re not selling gumballs here. It\'s chemotherapy. It\'ll cost at least {} slime, ya idjit!"'.format(ewcfg.mutations_map.get(target).tier * 5000)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif mutation_obj.artificial == 1:
			response = '"Hey, didn\'t I do that to ya? Well no refunds!"\n\nGuess you can\'t get rid of artificial mutations with chemo.'
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		else:
			try:
				ewutils.execute_sql_query("DELETE FROM mutations WHERE {id_server} = %s AND {id_user} = %s AND {mutation} = %s".format(
					id_server=ewcfg.col_id_server,
					id_user=ewcfg.col_id_user,
					mutation = ewcfg.col_id_mutation
				), (
					user_data.id_server,
					user_data.id_user,
					target,
				))
			except:
				ewutils.logMsg("Failed to clear mutations for user {}.".format(user_data.id_user))
			response = '"Alright, dearie, let\'s get you purged." You enter a dingy looking operating room, with slime strewn all over the floor. Dr. Dusttrap pulls out a needle the size of your bicep and injects into odd places on your body. After a few minutes of this, you get fatigued and go under.\n\n You wake up missing the {} mutation. Nice!'
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def graft(cmd):
	user_data = EwUser(member=cmd.message.author)

	if cmd.message.channel.name != ewcfg.channel_goonyinfirmary:
		response = "Chemotherapy doesn't just grow on trees. You'll need to go to Goony Infirmary in Poudrin Alley to get some."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.life_state == ewcfg.life_state_shambler:
		response = '"Oh goodness me, it seems like another one of these decaying subhumans has wandered into my office. Go on, shoo!"\n\nTough luck, seems shamblers aren\'t welcome here.'.format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)


	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.life_state == ewcfg.life_state_corpse:
		response = '"You get out of here, dirty nega. We don\'t serve your kind." \n\n Auntie Dusttrap threatingly flails a jar of cole slaw at you. Looks like you need a body to mutate a body.'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif len(cmd.tokens) <= 1:
		response = '"What, just anything? I love a good improv surgery! I had to leave town the last one I did though, so you\'ll have to pick an actual surgical procedure. Sorry, sonny."'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
	target = ewutils.get_mutation_alias(target_name)

	mutations = user_data.get_mutations()

	if target == 0:
		response = '"What? My ears aren\'t what they used to be. I thought you suggested I give you {}. Only braindead squicks would say that."'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif target in mutations:
		response = '"Nope, you already have that mutation. Hey, I thought I was supposed to be the senile one here!"'
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif user_data.get_mutation_level() + ewcfg.mutations_map[target].tier > min([user_data.slimelevel, 50]):
		response = '"Your body\'s already full of mutations. Your sentient tumors will probably start bitin\' once I take out my scalpel."\n\nLevel:{}/50\nMutation Levels Added:{}/{}'.format(user_data.slimelevel,user_data.get_mutation_level(),user_data.slimelevel)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	elif ewcfg.mutations_map.get(target).tier * 10000 < user_data.slimes:
		response = '"We\'re not selling gumballs here. It\'s cosmetic surgery. It\'ll cost at least {} slime, ya idjit!"'.format(ewcfg.mutations_map.get(target).tier * 10000)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		user_data.add_mutation(id_mutation=target, is_artificial=1)
		response = ewcfg.mutations_map[target].str_transplant
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def clear_mutations(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	market_data = EwMarket(id_server = user_data.id_server)
	response = ""
	if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
		response = "You require the advanced equipment at the Slimeoid Lab to modify your mutations."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poi = ewcfg.id_to_poi.get(user_data.poi)
	district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "How do you expect to mutate without exposure to slime, dumbass?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	mutations = user_data.get_mutations()
	if len(mutations) == 0:
		response = "You have not developed any specialized mutations yet."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	poudrin = ewitem.find_item(item_search = "slimepoudrin", id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None, item_type_filter = ewcfg.it_item)

	if poudrin == None:
		response = "You need a slime poudrin to replace a mutation."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		ewitem.item_delete(id_item = poudrin.get('id_item'))  # Remove Poudrins
		market_data.donated_poudrins += 1
		market_data.persist()
		user_data.poudrin_donations += 1
		user_data.persist()

	user_data.clear_mutations()
	response = "After several minutes long elevator descents, in the depths of some basement level far below the laboratory's lobby, you lay down on a reclined medical chair. A SlimeCorp employee finishes the novel length terms of service they were reciting and asks you if you have any questions. You weren’t listening so you just tell them to get on with it so you can go back to getting slime. They oblige.\nThey grab a random used syringe with just a dash of black serum still left inside it. They carefully stab you with it, injecting the mystery formula into your bloodstream. Almost immediately, normalcy returns to your inherently abnormal life… your body returns to whatever might be considered normal for your species. You hand off one of your hard-earned poudrins to the SlimeCorp employee for their troubles."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def track_oneeyeopen(cmd):
	user_data = EwUser(id_user=cmd.message.author.id, id_server=cmd.message.guild.id)
	target_data = EwUser(member = cmd.mentions[0])
	mutations = user_data.get_mutations()

	if ewcfg.mutation_id_oneeyeopen not in mutations:
		response = "No can do. Your third eye is feeling pretty flaccid today."
	elif cmd.mentions_count == 0:
		response = "Who are you tracking?"
	elif cmd.mentions_count > 1:
		response = "Nice try, but you're not the NSA. Limit your espionage to one poor sap."
	elif cmd.mentions[0] == cmd.message.author:
		response = "You set your third eye to track yourself. However, you are too uncomfortable with your body to keep it there. Better try something else."
	else:
		response = "Your third eye slips out of your forehead and wanders its way to {}'s location. Just a matter of time..."
		mutation_data = EwMutation(id_user=user_data.id_user, id_server=user_data.id_server, id_mutation=ewcfg.mutation_id_oneeyeopen)
		mutation_data.data = target_data.id_user
		mutation_data.persist()

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def shakeoff(cmd):
	user_data = EwUser(member=cmd.message.author)

	if cmd.mentions_count == 0:
		response = "God knows there are like a million third eyes floating around. You'll have to specify whose you're looking for."

	elif cmd.mentions_count > 1:
		response = "Cut your poor eye some slack. It can only stalk 1 poor sucker."

	else:
		target_data = EwUser(member=cmd.mentions[0])
		try:
			ewutils.execute_sql_query(
				"UPDATE mutations SET {data} = %s WHERE {id_server} = %s AND {mutation} = %s and {id_user} = %s;".format(
					data=ewcfg.col_mutation_data,
					id_server=ewcfg.col_id_server,
					id_user=ewcfg.col_id_user,
					mutation=ewcfg.col_id_mutation,
				), (
					"",
					user_data.id_server,
					ewcfg.mutation_id_oneeyeopen,
					target_data.id_user
				))
			response = "You search high and low for {}'s third eye, shouting a bit to give it a good scare. If it was stalking you it certainly isn't now.".format(cmd.mentions[0].display_name)
		except:
			ewutils.logMsg("Failed to undo tracking for {}.".format(user_data.id_user))
			response = ""
	return await ewutils.send_message(cmd.client, cmd.message.channel,ewutils.formatMessage(cmd.message.author, response))

async def clench(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = "You clench your butt cheeks together..."
	ewutils.clenched[user_data.id_user] = 1
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	await asyncio.sleep(5)
	ewutils.clenched[user_data.id_user] = 0