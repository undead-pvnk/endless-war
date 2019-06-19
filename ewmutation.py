import asyncio
import math
import time
import random

import discord

import ewcfg
import ewstats
import ewutils
import ewitem

from ew import EwUser

class EwMutationFlavor:

	# The mutation's name
	id_mutation = ""

	# String used to describe the mutation when you !data yourself
	str_describe_self = ""

	# String used to describe the mutation when you !data another player
	str_describe_other = ""

	# String used when you acquire the mutation
	str_acquire = ""

	def __init__(self,
		id_mutation = "",
		str_describe_self = "",
		str_describe_other = "",
		str_acquire = ""):

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


class EwMutation:
	id_server = ""
	id_user = ""
	id_mutation = ""

	data = ""

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
				cursor.execute("SELECT {data}, {mutation_counter} FROM mutations WHERE id_user = %s AND id_server = %s AND {id_mutation} = %s".format(
					data = ewcfg.col_mutation_data,
					mutation_counter = ewcfg.col_mutation_counter,
					id_mutation = ewcfg.col_id_mutation
				), (
					id_user,
					id_server,
					id_mutation
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
			# Todo Preserve Farming Data 	farmActive, plantType, time_lastsow
			cursor.execute("REPLACE INTO mutations(id_user, id_server, {id_mutation}, {data}, {mutation_counter}) VALUES(%s, %s, %s, %s, %s)".format(
					id_mutation = ewcfg.col_id_mutation,
					data = ewcfg.col_mutation_data,
					mutation_counter = ewcfg.col_mutation_counter
				), (
					self.id_user,
					self.id_server,
					self.id_mutation,
					self.data,
					self.mutation_counter
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
	response = ""

	if user_data.poi != ewcfg.poi_id_slimeoidlab:
		response = "You require the advanced equipment at the Slimeoid Lab to modify your mutations."
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


	poudrins = ewitem.inventory(
		id_user = cmd.message.author.id,
		id_server = cmd.message.server.id,
		item_type_filter = ewcfg.it_slimepoudrin
	)

	if len(poudrins) < 1:
		response = "You need a slime poudrin to replace a mutation."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		ewitem.item_delete(id_item = poudrins[0].get('id_item'))  # Remove Poudrins


	mutation_data = EwMutation(id_server = user_data.id_server, id_user = user_data.id_user, id_mutation = last_mutation)
	new_mutation = random.choice(list(ewcfg.mutation_ids))
	while new_mutation in mutations:
		new_mutation = random.choice(list(ewcfg.mutation_ids))

	mutation_data.id_mutation = new_mutation
	mutation_data.time_lastuse = int(time.time())
	mutation_data.persist()

	response = "{}".format(ewcfg.mutations_map[new_mutation].str_acquire)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def clear_mutations(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	if user_data.poi != ewcfg.poi_id_slimeoidlab:
		response = "You require the advanced equipment at the Slimeoid Lab to modify your mutations."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "How do you expect to mutate without exposure to slime, dumbass?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


	mutations = user_data.get_mutations()
	if len(mutations) == 0:
		response = "You have not developed any specialized mutations yet."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	user_data.clear_mutations()
	response = "Your body returns to whatever might be considered normal for your species."
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
