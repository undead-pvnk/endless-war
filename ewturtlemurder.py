import asyncio
import random
import time
import math

import ewutils
import ewcfg
import ewmap
import ewitem

from ew import EwUser
from ewplayer import EwPlayer
from ewdistrict import EwDistrict

class EwTurtleMurder:
	id_server = ""

	time_start = 0
	game_state = ewcfg.tm_game_state_inactive
	casino_state = ewcfg.tm_casino_state_closed

	magic_blue = False
	magic_green = False
	magic_red = False
	magic_black = False
	magic_white = False

	boss_hp = 8
	boss_last_action = ""
	time_boss_last_action = 0
	current_victim = ""

	def __init__(
		self,
		id_server = None
	):
		if id_server != None:
			self.id_server = id_server

			data = ewutils.execute_sql_query("SELECT {time_start}, {game_state}, {casino_state}, {magic_blue}, {magic_green}, {magic_red}, {magic_black}, {magic_white}, {boss_hp}, {boss_last_action}, {time_boss_last_action}, {current_victim} FROM tm_turtles WHERE {id_server} = %s".format(
				id_server = ewcfg.col_id_server,
				time_start = ewcfg.col_tm_time_start,
				game_state = ewcfg.col_tm_game_state,
				casino_state = ewcfg.col_tm_casino_state,

				magic_blue = ewcfg.col_tm_magic_blue,
				magic_green = ewcfg.col_tm_magic_green,
				magic_red = ewcfg.col_tm_magic_red,
				magic_black = ewcfg.col_tm_magic_black,
				magic_white = ewcfg.col_tm_magic_white,

				boss_hp = ewcfg.col_tm_boss_hp,
				boss_last_action = ewcfg.col_tm_boss_last_action,
				time_boss_last_action = ewcfg.col_tm_time_boss_last_action,
				current_victim = ewcfg.col_tm_current_victim
			    
			),(
				id_server,
			))

			if len(data) > 0:
				self.time_start = data[0][0]
				self.game_state = data[0][1]
				self.casino_state = data[0][2]

				self.magic_blue = data[0][3]
				self.magic_green = data[0][4]
				self.magic_red = data[0][5]
				self.magic_black = data[0][6]
				self.magic_white = data[0][7]

				self.boss_hp = data[0][8]
				self.boss_last_action = data[0][9]
				self.time_boss_last_action = data[0][10]
				self.current_victim = data[0][11]
			else:
				self.persist()

	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO tm_turtles({id_server},{time_start}, {game_state}, {casino_state}, {magic_blue}, {magic_green}, {magic_red}, {magic_black}, {magic_white}, {boss_hp}, {boss_last_action}, {time_boss_last_action}, {current_victim}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(
				id_server = ewcfg.col_id_server,
				time_start = ewcfg.col_tm_time_start,
				game_state = ewcfg.col_tm_game_state,
				casino_state = ewcfg.col_tm_casino_state,

				magic_blue = ewcfg.col_tm_magic_blue,
				magic_green = ewcfg.col_tm_magic_green,
				magic_red = ewcfg.col_tm_magic_red,
				magic_black = ewcfg.col_tm_magic_black,
				magic_white = ewcfg.col_tm_magic_white,

				boss_hp = ewcfg.col_tm_boss_hp,
				boss_last_action = ewcfg.col_tm_boss_last_action,
				time_boss_last_action = ewcfg.col_tm_time_boss_last_action,
				current_victim = ewcfg.col_tm_current_victim
		),(
				self.id_server,
				self.time_start,
				self.game_state,
				self.casino_state,

				(1 if self.magic_blue else 0),
				(1 if self.magic_green else 0),
				(1 if self.magic_red else 0),
				(1 if self.magic_black else 0),
				(1 if self.magic_white else 0),

				self.boss_hp,
				self.boss_last_action,
				self.time_boss_last_action,
				self.current_victim

		))


class EwTurtle:
	id_user = ""
	id_server = ""

	id_target = ""
	weapon = ""
	life_state = ewcfg.tm_life_state_active
	win_state = ewcfg.tm_win_state_neutral
	combat_level = 0
	last_action = ""
	time_last_action = 0
	coins = 0
	

	def __init__(
		self,
		id_server = None,
		id_user = None
	):
		if id_server != None and id_user != None:
			self.id_server = id_server
			self.id_user = id_user

			data = ewutils.execute_sql_query("SELECT {id_target}, {weapon}, {life_state}, {win_state}, {combat_level}, {last_action}, {time_last_action}, {coins} FROM tm_turtles WHERE {id_server} = %s AND {id_user} = %s".format(
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user,
				id_target = ewcfg.col_tm_id_target,
				weapon = ewcfg.col_tm_weapon,
				life_state = ewcfg.col_tm_life_state,
				win_state = ewcfg.col_tm_win_state,
				combat_level = ewcfg.col_tm_combat_level,
				last_action = ewcfg.col_tm_last_action,
				time_last_action = ewcfg.col_tm_time_last_action,
				coins = ewcfg.col_tm_coins
			    
			),(
				id_server,
				id_user
			))

			if len(data) > 0:
				self.id_target = data[0][0]
				self.weapon = data[0][1]
				self.life_state = data[0][2]
				self.win_state = data[0][3]
				self.combat_level = data[0][4]
				self.last_action = data[0][5]
				self.time_last_action = data[0][6]
				self.coins = data[0][7]
			else:
				self.persist()

	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO tm_turtles({id_server},{id_user},{id_target},{weapon},{life_state},{win_state},{combat_level}, {last_action}, {time_last_action}, {coins}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user,
				id_target = ewcfg.col_tm_id_target,
				weapon = ewcfg.col_tm_weapon,
				life_state = ewcfg.col_tm_life_state,
				win_state = ewcfg.col_tm_win_state,
				combat_level = ewcfg.col_tm_combat_level,
				last_action = ewcfg.col_tm_last_action,
				time_last_action = ewcfg.col_tm_time_last_action,
				coins = ewcfg.col_tm_coins
		),(
				self.id_user,
				self.id_server,

				self.id_target,
				self.weapon,
				self.life_state,
				self.win_state,
				self.combat_level,
				self.last_action,
				self.time_last_action,
				self.coins

		))

	def die(self):
		self.life_state = ewcfg.tm_life_state_dead
		self.weapon = ""
		self.coins = 0
		self.combat_level = 0
		turtle_items = ewitems.inventory(
			id_server = self.id_server,
			id_user = self.id_user,
			item_type_filter = ewcfg.it_turtlemurder
		)
		for item in turtle_items:
			ewitem.give_item(
				id_item = item.get("id_item"),
				id_user = ewcfg.poi_id_turtlecasino,
				id_server = self.id_server
			)

	async def direct_message(self, message):
		client = ewutils.get_client()
		server = ewcfg.server_list[self.id_server]
		member = server.get_member(self.id_user)
		try:
			await ewutils.send_message(client, member, message)
		except:
			user_data = EwUser(id_user = self.id_user, id_server = self.id_server)
			poi = ewcfg.id_to_poi.get(user_data.poi)
			channel = ewutils.get_channel(server, poi.channel)
			await ewutils.send_message(client, channel, ewutils.formatMessage(member,message))

class EwMurder:
	id_server = ""
	id_culprit = ""

	id_victim = ""
	weapon = ""
	poi = ""
	resolved = False

	def __init__(
		self,
		id_server = None,
		id_culprit = None,
		id_victim = None,
		weapon = None,
		poi = None
	):
		if id_server != None and id_victim != None:
			self.id_server = id_server
			self.id_victim = id_victim

			data = ewutils.execute_sql_query("SELECT {id_culprit}, {weapon}, {poi}, {resolved} FROM tm_murders WHERE {id_server} = %s AND {id_victim} = %s".format(
				id_server = ewcfg.col_id_server,
				id_culprit = ewcfg.col_tm_id_culprit,
				id_victim = ewcfg.col_tm_id_victim,
				weapon = ewcfg.col_tm_weapon,
				poi = ewcfg.col_poi,
				resolved = ewcfg.col_tm_resolved
			    
			),(
				id_server,
				id_culprit
			))

			if len(data) > 0:
				self.id_culprit = data[0][0]
				self.weapon = data[0][1]
				self.poi = data[0][2]
				self.resolved = (1 == data[0][3])
			elif id_culprit != None and weapon != None and poi != None:
				self.id_culprit = id_culprit
				self.weapon = weapon
				self.poi = poi
				self.resolved = False
				self.persist()

	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO tm_murders({id_server},{id_victim},{id_culprit},{weapon},{poi},{resolved}) VALUES (%s,%s,%s,%s,%s,%s)".format(
				id_server = ewcfg.col_id_server,
				id_victim = ewcfg.col_tm_id_victim,
				id_culprit = ewcfg.col_tm_id_culprit,
				weapon = ewcfg.col_tm_weapon,
				poi = ewcfg.col_poi,
				resolved = ewcfg.col_tm_resolved
		),(
				self.id_server,
				self.id_victim,
				self.id_culprit,
				self.weapon,
				self.poi,
				(1 if self.resolved else 0)

		))
	def get_boss_next_action(self):
		next_action = ""
		if self.boss_last_action == ewcfg.tm_boss_action_charge:
			next_action = ewcfg.tm_boss_action_aoe
		elif random.random() > 0.33:
			next_action = ewcfg.tm_boss_action_strike
		else:
			next_action = ewcfg.tm_boss_action_charge
		return next_action

class EwVote:
	id_server = ""
	id_user = ""
	id_victim = ""
	id_votee = ""

	def __init__(
		self,
		id_server = None,
		id_user = None,
		id_victim = None
	):
		if id_server != None and id_user != None and id_victim != None:
			self.id_server = id_server
			self.id_user = id_user
			self.id_victim = id_victim

			data = ewutils.execute_sql_query("SELECT {id_votee} FROM tm_votes WHERE {id_server} = %s AND {id_user} = %s AND {id_victim} = %s".format(
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user,
				id_victim = ewcfg.col_tm_id_victim,
				id_votee = ewcfg.col_tm_id_votee
			    
			),(
				id_server,
				id_user,
				id_victim
			))

			if len(data) > 0:
				self.id_votee = data[0][0]
			else:
				self.persist()

	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO tm_votes({id_server},{id_user},{id_victim},{id_votee}) VALUES (%s,%s,%s,%s)".format(
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user,
				id_victim = ewcfg.col_tm_id_victim,
				id_votee = ewcfg.col_tm_id_votee
		),(
				self.id_server,
				self.id_user,
				self.id_victim,
				self.id_votee

		))

class EwTurtleItem:
	id_item = ""

	price = 0

	weapon = False
	weapon_level = -1
	weapon_special = False
	weapon_loud = False
	
	use_pois = []
	use_rewards = []

	str_name = ""
	str_desc = ""

	str_use_success = ""
	str_use_failure = ""

	str_kill = ""
	str_crime_scene = ""

	def __init__(
		self,
		id_item = "",
		price = 0,
		weapon = False,
		weapon_level = -1,
		weapon_special = False,
		weapon_loud = False,
		use_pois = [],
		use_rewards = [],
		str_name = "",
		str_desc = "",
		str_use_success = "",
		str_use_failure = "",
		str_kill = "",
		str_crime_scene = ""
	):
		self.id_item = id_item
		self.price = price
		self.weapon = weapon
		self.weapon_level = weapon_level
		self.weapon_special = weapon_special
		self.weapon_loud = weapon_loud

		self.use_pois = use_pois
		self.use_rewards = use_rewards
		self.str_name = str_name
		self.str_desc = str_desc
		self.str_use_success = str_use_success
		self.str_use_failure = str_use_failure

		self.str_kill = str_kill
		self.str_crime_scene = str_crime_scene



async def tm_reset(id_server):
	players = tm_get_players(id_server)
	client = ewutils.get_client()
	ewutils.execute_sql_query("DELETE FROM tm_turtles WHERE id_server = %s",(id_server,))
	ewutils.execute_sql_query("DELETE FROM tm_murders WHERE id_server = %s", (id_server,))
	ewutils.execute_sql_query("DELETE FROM tm_votes WHERE id_server = %s", (id_server,))
	ewutils.execute_sql_query("DELETE FROM tm_games WHERE id_server = %s", (id_server,))
	ewutils.execute_sql_query("DELETE FROM items WHERE id_server = %s AND {item_type} = %s".format(
		item_type = ewcfg.col_item_type
	), (
		id_server,
		ewcfg.it_turtlemurder
	))

	for id_player in players:
		user_data = EwUser(id_user = id_player, id_server = id_server)
		user_data.poi = ewcfg.poi_id_kameisland
		user_data.turtlemurder = False
		user_data.persist()
		server = ewcfg.server_list[id_server]
		member_object = server.get_member(id_player)
		await ewrolemgr.updateRoles(client = client, member = member_object)

def tm_get_players(id_server):
	players = []
	data = ewutils.execute_sql_query("SELECT {id_user} FROM tm_turtles WHERE id_server = %s".format(
		id_user = ewcfg.col_id_user
	),(
		id_server,
	))
	for row in data:
		players.append(row[0])

	return players

def tm_get_victims(id_server):
	players = []
	data = ewutils.execute_sql_query("SELECT {id_victim} FROM tm_murders WHERE id_server = %s".format(
		id_victim = ewcfg.col_tm_id_victim
	),(
		id_server,
	))
	for row in data:
		players.append(row[0])

	return players

def tm_get_votes(id_server, id_victim):
	votes = {}
	data = ewutils.execute_sql_query("SELECT {id_user}, {id_votee} FROM tm_votes WHERE id_server = %s AND {id_victim} = %s".format(
		id_user = ewcfg.col_id_user
		id_votee = ewcfg.col_tm_id_votee
		id_victim = ewcfg.col_tm_id_victim
	),(
		id_server,
		id_victim
	))
	for row in data:
		votes[row[0]] = row[1]

	return votes

async def tm_trial_begin(id_server):
	client = ewutils.get_client()
	server = ewcfg.server_list.get(id_server)
	response = ""
	resp_cont = ewutils.EwResponseContainer(id_server = id_server)
	game_data = EwTurtleMurder(id_server = id_server)
	players = tm_get_players(id_server)
	if game_data.game_state == ewcfg.tm_game_state_trial:
		return
	
	for id_user in players:
		user_data = EwUser(id_user = id_user, id_server = id_server)
		turtle_data = EwTurtle(id_user = id_user, id_server = id_server)
		if user_data.poi != ewcfg.poi_id_turtletrialgrounds and turtle_data.life_state == ewcfg.tm_life_state_active:
			return

	victims = tm_get_victims(id_server)
	for id_victim in victims:
		murder_data = EwMurder(id_server = id_server, id_victim = id_victim)
		if murder_data.resolved:
			victims.remove(id_victim)
	
	if len(victims) == 0:
		response = "Nobody has been murdered yet. Get out and start killing!"
		resp_cont.add_channel_response(ewcfg.channel_turtletrialgrounds, response)
		await resp_cont.post()
		for id_user in players:
			user_data = EwUser(id_user = id_user, id_server = id_server)
			if user_data.poi == ewcfg.poi_id_turtletrialgrounds:
				user_data.poi = ewcfg.poi_id_turtlelobby
				user_data.persist()
				await ewrolemgr.updateRoles(
					client = client,
					member = server.get_member(id_user)
				)

		return

	game_data.game_state = ewcfg.tm_game_state_trial
	game_data.current_victim = random.choice(victims)
	game_data.persist()
	victim_player = EwPlayer(id_user = game_data.current_victim)
	response = "Everyone has arrived. The first case is the murder of {}. You may cast your votes now.".format(victim_player.display_name)
	resp_cont.add_channel_response(ewcfg.channel_turtletrialgrounds, response)

	return await resp_cont.post()

async def tm_trial_advance(id_server):
	response = ""
	resp_cont = ewutils.EwResponseContainer(id_server = id_server)
	game_data = EwTurtleMurder(id_server = id_server)
	if game_data.game_state != ewcfg.tm_game_state_trial:
		return
	murder_data = EwMurder(id_server = id_server, id_victim = game_data.current_victim)
	votes = tm_get_votes(id_server, game_data.current_victim)
	players = tm_get_players(id_server)
	votes_map = {}
	for id_user in players:
		turtle_data = EwTurtle(id_server = id_server, id_user = id_user)
		if turtle_data.life_state == ewcfg.tm_life_state_dead or id_user not in votes:
			return
		votee_id = votes[id_user]
		if votee_id in votes_map:
			votes_map[votee_id] += 1
		else:
			votes_map[votee_id] = 1

	found_guilty_id = ""
	max_votes = 0

	for id_user, num_votes in votes_map:
		if num_votes > max_votes:
			found_guilty_id = id_user
	tie = False
	for id_user, num_votes in votes_map:
		if id_user != found_guilty_id and num_votes == max_votes:
			tie = True
			break;

	response = "The Results are in:\n"
	for id_user, num_votes in votes_map:
		player_data = EwPlayer(id_user = id_user)
		response += "{}: {} votes\n".format(player_data.display_name, num_votes)

	if tie:
		response += "The vote was inconclusive.\n"
	else:
		victim_player = EwPlayer(id_user = murder_data.id_victim)
		found_guilty_player = EwPlayer(id_user = found_guilty_id)
		response += "{} was found guilty of killing {}.\n".format(found_guilty_player.display_name, victim_player.display_name)
	
	culprit_data = EwTurtle(id_server = id_server, id_user = murder_data.id_culprit)
	if tie or found_guilty_id != murder_data.id_culprit:
		response += "You voted incorrectly. The culprit will not be punished. Case closed.\n"
		if game_data.current_victim == culprit_data.current_victim:
			if culprit_data.win_state != ewcfg.tm_win_state_lost
				culprit_data.win_state = ewcfg.tm_win_state_won
	else:
		response += "You voted correctly. The culprit will be punished. Case closed.\n"
		culprit_data.win_state = ewcfg.tm_win_state_lost
	culprit_data.persist()
	murder_data.resolved = True
	murder_data.persist()

	resp_cont.add_channel_response(ewcfg.channel_turtletrialgrounds, response)
	await resp_cont.post()
	return await tm_trial_next_case(id_server)

async def tm_trial_next_case(id_server):
	client = ewutils.get_client()
	server = ewcfg.server_list.get(id_server)
	resp_cont = ewutils.EwResponseContainer(id_server = id_server)
	victims = tm_get_victims(id_server)
	game_data = EwTurtleMurder(id_server = id_server)
	for id_victim in victims:
		murder_data = EwMurder(id_server = id_server, id_victim = id_victim)
		if murder_data.resolved:
			victims.remove(id_victim)

	if len(victims) == 0:
		response = "All cases closed."
		players = tm_get_players(id_server)
		winners = []
		losers = []
		for id_user in players:
			turtle_data = EwTurtle(id_server = id_server, id_user = id_user)
			if turtle_data.win_state == ewcfg.tm_win_state_won:
				winners.append(id_user)
			elif turtle_data.win_state == ewcfg.tm_win_state_lost:
				turtle_data.life_state = ewcfg.tm_life_state_dead
				turtle_data.persist()
				losers.append(id_user)

		if len(winners) > 0:
			response += "The following players have won:\n"
			for id_user in winners:
				player_data = EwPlayer(id_user = id_user)
				response += player_data.display_name + "\n"
			response += "The game is over. ({} to leave the mansion)".format(ewcfg.cmd_tm_endgame)
			game_data.game_state = ewcfg.tm_game_state_postgame
			game_data.persist()
			resp_cont.add_channel_response(ewcfg.channel_turtletrialgrounds, response)
			await resp_cont.post()
			for id_user in players:
				if id_user not in winners:
					turtle_data = EwTurtle(id_user = id_user)
					turtle_data.life_state == ewcfg.tm_life_state_dead
					turtle_data.poi = ewcfg.poi_id_turtlehell
					turtle_data.persist()
					await ewrolemgr.updateRoles(
						client = client,
						member = server.get_member(id_user)
					)
			return
		elif len(losers) > 0:
			response += "The following players will be punished:\n"
			for id_user in losers:
				player_data = EwPlayer(id_user = id_user)
				response += player_data.display_name + "\n"
			resp_cont.add_channel_response(ewcfg.channel_turtletrialgrounds, response)
			await resp_cont.post()

			for id_user in losers:
				turtle_data = EwTurtle(id_server = id_server, id_user = id_user)
				user_data = EwUser(id_server = id_server, id_user = id_user)
				turtle_data.life_state == ewcfg.tm_life_state_dead
				user_data.poi = ewcfg.poi_id_turtlehell
				turtle_data.persist()
				user_data.persist()
				await ewrolemgr.updateRoles(
					client = client,
					member = server.get_member(id_user)
				)

			left_alive = []
			resp_cont = ewutils.EwResponseContainer(id_server = id_server)
			for id_user in players:
				turtle_data = EwTurtle(id_user = id_user, id_server = id_server)
				if turtle_data.life_state == ewcfg.tm_life_state_active:
					left_alive.append(id_user)
			if len(left_alive) > 3:
				response = "The game continues. Ejecting everyone from the trial grounds."
			else:
				response = "The game is over. ({} to leave the mansion)".format(ewcfg.cmd_tm_endgame)
			resp_cont.add_channel_response(ewcfg.channel_turtletrialgrounds, response)
			await resp_cont.post()

			for id_user in left_alive:
				user_data = EwUser(id_user = id_user, id_server = id_server)
				user_data.poi = ewcfg.poi_id_turtlelobby
				await ewrolemgr.updateRoles(
					client = client,
					member = server.get_member(id_user)
				)
			return



	game_data.current_victim = random.choice(victims)
	game_data.persist()
	victim_player = EwPlayer(id_user = game_data.current_victim)
	response = "The next case is the murder of {}. You may cast your votes now.".format(victim_player.display_name)
	resp_cont.add_channel_response(ewcfg.channel_turtletrialgrounds, response)

	return await resp_cont.post()


async def tm_fix_targets(id_server):
	players = tm_get_players(id_server)
	victims = tm_get_victims(id_server)
	for id_user in players:
		turtle_data = EwTurtle(id_user = id_user, id_server = id_server)
		murder_data = EwMurder(id_server = id_server, id_victim = turtle_data.id_target)
		if murder_data.id_culprit == turtle_data.id_user:
			    break;
		changed_target = False
		while turtle_data.id_target in victims:
			victim_data = EwTurtle(id_server = id_server, id_user = turtle_data.id_target)
			turtle_data.id_target = victim_data.id_target
			changed_target = True
		turtle_data.persist()
		if changed_target:
			target_player = EwPlayer(id_user = turtle_data.id_target)
			response = "Your target has just died. Assigning new target: {}".format(target_player.display_name)
			await turtle_data.direct_message(response)
	return

	
	

async def tm_boss_act(id_server):
	client = ewutils.get_client()
	server = ewcfg.server_list.get(id_server)
	players = tm_get_players(id_server)
	game_data = EwTurtleMurder(id_server = id_server)
	for id_user in players:
		turtle_data = EwTurtle(id_user = id_user, id_server = id_server)
		if not (turtle_data.time_last_action > game_dta.time_boss_last_action or turtle_data.life_state != ewcfg.tm_life_state_active):
			return

	resp_cont = ewutils.EwResponseContainer(id_server = id_server)
	boss_action = game_data.get_boss_next_action()
	if boss_action == ewcfg.tm_boss_action_charge:
		response = "The Endless Turtle charges up its devastating shadow breath."
	elif boss_action == ewcfg.tm_boss_action_aoe:
		response = "The Endless Turtle unleashes its stored energy and bathes the whole room in shadow flames."
		for id_user in players:
			turtle_data = EwTurtle(id_user = id_user, id_server = id_server)
			player_data = EwPlayer(id_user = id_user)
			if turtle_data.life_state == ewcfg.tm_life_state_active:
				if turtle_data.last_action == ewcfg.tm_action_defend:
					response += "\n{} successfully defends.".format(player_data.display_name)
				else:
					response += "\n{} is incinerated. The Endless Turtle feeds on their soul and regenerates 2 HP.".format(player_data.display_name)
					game_data.boss_hp = min(game_data.boss_hp + 2, 8)
					turtle_data.life_state = ewcfg.tm_life_state_dead
					turtle_data.persist()
	elif boss_action == ewcfg.tm_boss_action_strike:
		id_user = random.choice(players)
		turtle_data = EwTurtle(id_user = id_user, id_server = id_server)
		while turtle_data.life_state != ewcfg.tm_life_state_active:
			id_user = random.choice(players)
			turtle_data = EwTurtle(id_user = id_user, id_server = id_server)
			
		player_data = EwPlayer(id_user = id_user)
		if turtle_data.last_action == ewcfg.tm_action_defend:
			response = "The Endless Turtle strikes at {}, but they successfully defend.".format(player_data.display_name)
		else:
			response = "The Endless Turtle strikes at {} and kills them. It feeds on their soul and regenerates 2 HP.".format(player_data.display_name)
			game_data.boss_hp = min(game_data.boss_hp + 2, 8)
			turtle_data.life_state = ewcfg.tm_life_state_dead
			turtle_data.persist()
					


	game_data.boss_last_action = boss_action
	game_data.time_boss_last_action = time.time()
	game_data.persist()
	resp_cont.add_channel_response(ewcfg.channel_turtlegraveyard, response)
	await resp_cont.post()
	for id_user in players:
		member = server.get_member(id_user)
		await ewrolemgr.updateRoles(
			client = client,
			member = member
		)

		




async def tm_defend(cmd):
	if ewmap.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))
	user_data = EwUser(member = cmd.message.author)
	response = ""
	time_now = time.time()
	if not user_data.turtlemurder:
		response = "The best defense is a good offense."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_user)

	if turtle_data.life_state == ewcfg.tm_life_state_dead:
		response = "You're too busy being dead to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if turtle_data.life_state == ewcfg.tm_life_state_pregame:
		response = "You have to wait for the game to begin to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if game_data.game_state != ewcfg.tm_game_state_bossfight:
		turtle_data.last_action = ""
		turtle_data.persist()
		response = "What are you afraid of?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if game_data.time_boss_last_action < turtle_data.time_last_action:
		response = "You've already acted this turn."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		turtle_data.last_action = ewcfg.tm_action_defend
		turtle_data.time_last_action = time_now
		turtle_data.persist()
		response = "You brace against incoming attacks."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		return await tm_boss_act(cmd.message.server.id)

		

async def tm_use(cmd, id_item):
	user_data = EwUser(member = cmd.message.author)
	id_server = cmd.message.server.id
	id_user = cmd.message.author.id
	response = ""
	time_now = time.time()
    
	game_data = EwTurtleMurder(id_server = id_server)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_user)
	item_data = EwItem(id_item = id_item)
	item_def = ewcfg.id_to_tmitem.get(item_data.item_props['tm_item_id'])
	poi = ewcfg.id_to_poi.get(user_data.poi)

	if turtle_data.life_state == ewcfg.tm_life_state_dead:
		response = "You're too busy being dead to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if turtle_data.life_state == ewcfg.tm_life_state_pregame:
		response = "You have to wait for the game to begin to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**YOUR TOYS WON'T SAVE YOU NOW.**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	if game_data.game_state == ewcfg.tm_game_state_voting:
		response = "You can't {} during the voting phase.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		

	if len(item_def.use_pois) == 0:
		response = "You can't use this item."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.poi not in item_def.use_pois:
		response = "There's nothing here to use {} on.".format(item_def.str_name)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	success = False
	user_inball = None
	format_map = {}
	turtle_data.last_action = ewcfg.tm_action_use
	turtle_data.time_last_action = time_now

	if item_def.id_item == ewcfg.tm_item_id_turtleknife:
		turtle_data.last_action = ewcfg.tm_action_bleed
		success = True

	elif item_def.id_item in [ewcfg.tm_item_id_fluoriteoctet, ewcfg.tm_item_id_dnddice]:
		ewitem.give_item(id_user = ewcfg.poi_id_turtlecasino, id_server = id_server, id_item = id_item)
		if turtle_data.weapon == id_item:
			turtle_data.weapon = ""
		if game_data.casino_state == ewcfg.tm_casino_state_closed:
			success = True
			turtle_data.coins += 10
			game_data.casino_state = ewcfg.tm_casino_state_open
		else:
			success = False
			turtle_data.coins += 5
	elif item_def.id_item == ewcfg.tm_item_id_pokeball:
		pokeball_district = EwDistrict(id_server = id_server, district = ewcfg.poi_id_turtlepokeball)
		players = pokeball_district.get_players_in_district()
		for id_inball in players:
			user_inball = EwUser(id_user = id_inball, id_server = id_server)
			if user_inball.turtlemurder:
				success = True
				user_inball.poi = user_data.poi
				ewitem.item_delete(id_item = id_item)
				break
	elif item_def.id_item in [ewcfg.tm_item_id_codexastartes, ewcfg.tm_item_id_nendoroid, ewcfg.tm_item_id_sburbbeta, ewcfg.tm_item_id_key]:
		success = True
		ewitem.item_delete(id_item = id_item)
		reward = random.choice(item_def.use_rewards)
		reward_item = ewcfg.id_to_tmitem.get(reward)
		reward_props = {
			"tm_item_id": reward_item.id_item,
			"tm_name": reward_item.str_name,
			"tm_desc": reward_item.str_desc
		}
		ewitem.item_create(
			item_type = ewcfg.it_turtlemurder,
			id_user = id_user,
			id_server = id_server,
			item_props = reward_props
		)
		format_map["reward1"] = reward_item.str_name

		if item_def.id_item == ewcfg.tm_item_id_codexastartes:
			reward = ewcfg.tm_id_item_miniature
			reward_item = ewcfg.id_to_tmitem.get(reward)
			reward_props = {
				"tm_item_id": reward_item.id_item,
				"tm_name": reward_item.str_name,
				"tm_desc": reward_item.str_desc
			}
			ewitem.item_create(
				item_type = ewcfg.it_turtlemurder,
				id_user = id_user,
				id_server = id_server,
				item_props = reward_props
			)
			format_map["reward2"] = reward_item.str_name
	elif item_def.id_item == ewcfg.tm_item_id_badge:
		ewitem.item_delete(id_item = id_item)
		success = True
		game_state.magic_red = True
	elif item_def.id_item == ewcfg.tm_item_id_dollarbill:
		ewitem.item_delete(id_item = id_item)
		success = True
		game_state.magic_green = True
	elif item_def.id_item == ewcfg.tm_item_id_pearl:
		ewitem.item_delete(id_item = id_item)
		success = True
		game_state.magic_white = True
	elif item_def.id_item == ewcfg.tm_item_id_miniature:
		ewitem.item_delete(id_item = id_item)
		success = True
		game_state.magic_blue = True
	elif item_def.id_item == ewcfg.tm_item_id_crystal:
		ewitem.item_delete(id_item = id_item)
		success = True
		game_state.magic_red = True
	elif item_def.id_item == ewcfg.tm_item_id_cheatcode:
		success = True
		user_data.poi = ewcfg.poi_id_turtleweebcorner
			


			
	turtle_data.persist()
	game_state.persist()
	if user_inball is not None:
		user_inball.persist()
		server = cmd.message.server
		member = server.get_member(user_inball.id_user)
		await ewrolemgr.updateRoles(
			client = cmd.client,
			member = member
		)
	if success:
		response = item_def.str_use_success
	else:
		response = item_def.str_use_failure
	response = response.format_map(format_map)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	user_data.persist()
	await ewrolemgr.updateRoles(
		client = cmd.client,
		member = cmd.message.author
	)



async def tm_vote(cmd):
	if ewmap.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))
	user_data = EwUser(member = cmd.message.author)
	response = ""
	time_now = time.time()
	if not user_data.turtlemurder:
		response = "Vote with your slime."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_user)

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**I'M NOT BOUND BY YOUR SILLY RULES.**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	if game_data.game_state != ewcfg.tm_game_state_trial:
		response = "You have to wait for the trial to begin to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if turtle_data.life_state == ewcfg.tm_life_state_dead:
		response = "You're too busy being dead to {}.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.mentions_count > 1:
		response = "You can only vote for one person per case."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	if cmd.mentions_count <= 0:
		response = "Please specify who you want to send to the gallows."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	member = cmd.mentions[0]
	votee_data = EwUser(member = member)
	if not votee_data.turtlemurder:
		response = "Who?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	vote_data = EwVote(id_server = user_data.id_server, id_user = user_data.id_user, id_victim = game_data.current_victim)

	if vote_data.id_votee != "":
		response = "You can only vote for one person per case."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	vote_data.id_votee = member.id
	vote_data.persist()
	response = "Successfully recorded your vote."
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	return await tm_trial_advance(cmd.message.server.id)

async def tm_pray(cmd):
	if ewmap.channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))
	user_data = EwUser(member = cmd.message.author)
	response = ""
	time_now = time.time()
	if not user_data.turtlemurder:
		response = "Your prayer goes unanswered."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_user)

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**HAHAHA! YES, BEG FOR YOUR PATHETIC LIVES!**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	if user_data.poi != ewcfg.poi_id_turtlegraveyard:
		response = "Your prayer goes unanswered."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	victims = tm_get_victims(id_server = user_data.id_server)
	if len(victims) == 0:
		response = "The dead remain silent."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	item_sought = ewitem.find_item(
		item_search = ewcfg.tm_item_id_pearl,
		id_user = user_data.id_user,
		id_server = user_data.id_server
	)
	response = "You open your mind to the spirits of the dead and they answer. Dark energies rise all around you, trying to take hold of you. "
		
	if item_sought == None:
		murder_data = EwMurder(
			id_server = user_data.id_server,
			id_victim = user_data.id_user,
			id_culprit = user_data.id_user,
			poi = user_data.poi,
			weapon = ewcfg.tm_weapon_prayer
		)
		user_data.poi = ewcfg.poi_id_turtlehell
		game_data.game_state = ewcfg.tm_game_state_investigation
		game_data.persist()
		user_data.persist()
		turtle_data.die()
		turtle_data.persist()

		resp_cont = ewutils.EwResponseContainer(id_server = user_data.id_server)
		response += "You struggle, but soon you lose hope. Your flesh blackens and cracks and you die in agony. The contents of your inventory are transferred to the casino."
		resp_cont.add_channel_response(cmd.message.channel.name, ewutils.formatMessage(cmd.message.author, response))
		deathreport = "You have been overwhelmed by the malice of the dead."
		resp_cont.add_channel_response(ewcfg.channel_turtlehell, ewutils.formatMessage(cmd.message.author, deathreport))
		await resp_cont.post()

		await ewrolemgr.updateRoles(
			client = cmd.client,
			member = cmd.message.author
		)
		return await tm_fix_targets(user_data.id_server)

	else:
		response += "But the hope in your heart protects you. The swirling despair crystallizes in your inventory."
		item_crystal = ewcfg.id_to_tmitem(ewcfg.tm_item_id_crystal)
		item_props = {
			"tm_item_id": item_crystal.id_item,
			"tm_name": item_crystal.str_name,
			"tm_desc": item_crystal.str_desc
		}
		ewitem.item_create(
			item_type = ewcfg.it_turtlemurder,
			id_user = user_data.id_user,
			id_server = user_data.id_server,
			item_props = item_props
		)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))



async def tm_oracle(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	resp_cont = ewutils.EwResponseContainer(id_server = cmd.message.server.id)
	time_now = time.time()
	if not user_data.turtlemurder:
		response = "There is no oracle here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_user)

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**THAT FOOL HAS NO POWER OVER MY REALM.**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	if user_data.poi != ewcfg.poi_id_turtlethroneroom:
		response = "There is no oracle here."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	if cmd.tokens_count < 2:
		response = "Hussie offers the following services:\nlocation: For 1 coin you will learn the location of a player.\nweapon: For 5 coins you will learn what weapon a player currently has equipped.\ninventory: For 10 coins you will learn the entire inventory of a player.\ntarget: For 20 coins you will learn the target of a player.",
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	if cmd.mentions_count == 0:
		response = "Please specify which player you want an oracle on."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.mentions_count > 1:
		response = "Only one oracle at a time."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	member = cmd.mentions[0]

	target_data = EwUser(member = member)
	target_turtle = EwTurtle(id_user = target_data.id_user, id_server = target_data.id_server)
	target_poi = ewcfg.id_to_poi.get(target_data.poi)
	if not target_data.turtlemurder:
		response = "That person is beyond my vision."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	arg_string = ewutils.flattenTokenListToString(cmd.tokens[1:])
	arg_int = ewutils.getIntToken(cmd.tokens[1:])
	if arg_int is None:
		arg_int = -1

	price = 0
	if arg_string == "target" or arg_int >= 20:
		price = 20
		if turtle_data.coins < price:
			response = "You can't afford this service."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		vision_player = EwPlayer(id_user = target_turtle.id_target)

		response = "{}'s target is {}.".format(member.display_name, vision_player.display_name)

	elif arg_string == "inventory" or arg_int >= 10:
		price = 10
		if turtle_data.coins < price:
			response = "You can't afford this service."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
		vision_items = ewitems.inventory(
			member = member,
			item_type_filer = ewcfg.it_turtlemurder
		)
		if len(vision_items) == 0:
			response = "{} has no items.".format(member.display_name)
		else:	
			str_items = ""
			for item in vision_items:
				str_items += "{}\n".format(item.get("name"))
			response = "{} has the following items:\n{}.".format(member.display_name, str_items)

	elif arg_string == "weapon" or arg_int >= 5:
		price = 5
		if turtle_data.coins < price:
			response = "You can't afford this service."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		item_sought = ewitem.find_item(
			id_user = target_data.id_user,
			id_server = target_data.id_server,
			item_search = target_data.weapon
		)
		if item_sought is None:
			response = "{} has no weapon equipped.".format(member.display_name)
		else:
			response = "{} has a {} equipped.".format(member.display_name, item_sought.get("name"))
	elif arg_string == "location" or arg_int >= 1:
		price = 1
		if turtle_data.coins < price:
			response = "You can't afford this service."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		response = "{} is currently in {}.".format(member.display_name, target_poi.str_name)

	resp_cont.add_channel_response(cmd.message.channel.name, ewutils.formatMessage(cmd.message.author, response))
	resp_cont.add_channel_response(target_poi.channel, ewutils.formatMessage(member, "You feel like you are being watched."))

	turtle_data.coins -= price
	turtle_data.persist()

	return await resp_cont.post()
	
async def tm_dance(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	resp_cont = ewutils.EwResponseContainer(id_server = cmd.message.server.id)
	time_now = time.time()
	if not user_data.turtlemurder:
		response = "No."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_user)

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**QUIT THE FANCY FOOTWORK.**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	if user_data.poi != ewcfg.poi_id_turtledisco:
		response = "You do a little jig, but you can't really get into it without some decent music."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	turtle_data.last_action = ewcfg.tm_action_dance
	turtle_data.persist()
	dancing_players = tm_get_players(id_server = cmd.message.server.id)

	for id_dancer in dancing_players:
		turtle_dance = EwTurtle(id_user = id_dancer, id_server = user_data.id_server)
		if turtle_dance.last_action != ewcfg.tm_action_dance:
			dancing_players.remove(id_dancer)

	if len(dancing_players) < 2:
		response = "You start busting out some moves on the dance floor. You notice the space marine tapping along with his foot, but when you look at him directly, he stops and looks away bashfully. Maybe if you got some more company, he would feel comfortable joining in."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	response = "{} enters the dance floor. Seeing everyone moving your bodies to the music, the space marine can't hold back any longer and finally lets loose. You are in awe of his sweet dance moves. You never would have guessed anyone could move like this in all that heavy armor.".format(cmd.message.author.display_name)
	resp_cont.add_channel_response(cmd.message.channel.name, response)

	for id_user in dancing_players:
		turtle_data = EwTurtle(id_user = id_user, id_server = cmd.message.server.id)
		member = cmd.message.server.get_member(id_user)
		if turtle_data.combat_level > 0:
			response = "You already have an edge."
		else:
			turtle_data.combat_level += 1
			response = "Dancing with the space marine has temporarily increased your physical prowess. You will have an edge for the next fight you're involved in."
			
		resp_cont.add_channel_response(cmd.message.channel.name, ewutils.formatMessage(member, response))
		turtle_data.last_action = ""
		turtle_data.persist()

	return await resp_cont.post()
	
async def tm_mine(cmd):
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	user_data = EwUser(member = cmd.message.author)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_server)
	response = ""
	time_now = time.time()

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**NO GRINDING YOURSELF PAST THIS ONE.**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	if user_data.poi != ewcfg.poi_id_turtleweebcorner:
		response = "You can't {} here.".format(cmd.tokens[0])
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	weeb_distracted = False
	players = tm_get_players(cmd.message.server.id)

	for id_distracter in players:
		if id_distracter == user_data.id_user:
			continue

		distract_data = EwUser(id_user = id_distracter, id_server = user_data.id_server)
		distract_turtle = EwTurtle(id_user = id_distracter, id_server = user_data.id_server)
		if distract_data == ewcfg.poi_id_turtleweebcorner and distract_turtle.last_action == ewcfg.tm_action_distract:
			weeb_distracted = True
			break

	if weeb_distracted:
		if turtle_data.time_last_action + ewcfg.cd_tm_mine > time_now:
			response = "You can only use this command once every {} seconds.".format(ewcfg.cd_tm_mine)
		else:
			turtle_data.last_action = ewcfg.tm_action_mine
			turtle_data.time_last_action = time_now
			response = ewitem.item_lootrandom(id_user = user_data.id_user, id_server = user_data.id_server)
	else:
		turtle_data.last_action = ewcfg.tm_action_mine
		turtle_data.time_last_action = time_now
		response = "As soon as you make a move for the anime piles, the otaku turns away from the TV and looks directly at you, like he *knows*. You decide it's better not to incur his wrath. It seems like you will need a distraction."

	turtle_data.persist()
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
async def tm_distract(cmd):
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	user_data = EwUser(member = cmd.message.author)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_server)
	response = ""
	time_now = time.time()

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**I DON'T FALL FOR CHEAP TRICKS LIKE THAT.**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	turtle_data.last_action = ewcfg.tm_action_distract
	turtle_data.time_last_action = time_now
	turtle_data.persist()

	if user_data.poi != ewcfg.poi_id_turtleweebcorner:
		response = "Behind you!"
	else:
		response = "You pretend to be interested in anime to get the otaku's attention. He pauses his TV and starts bombarding you with information about all of his favorite animes and waifus. It's the most mind-numbing stuff you've ever had to listen to. You immediately regret this decision."

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def tm_yahtzee(cmd):
	game_data = EwTurtleMurder(id_server = cmd.message.server.id)
	user_data = EwUser(member = cmd.message.author)
	turtle_data = EwTurtle(id_server = user_data.id_server, id_user = user_data.id_server)
	response = ""
	time_now = time.time()
	int_token = ewutils.getIntToken(cmd.tokens[1:])

	if game_data.game_state == ewcfg.tm_game_state_bossfight:
		response = "**NO MORE GAMES.**"
		return await ewutils.send_message(cmd.client, cmd.message.channel, response)

	turtle_data.last_action = ewcfg.tm_action_yahtzee
	turtle_data.time_last_action = time_now
	turtle_data.persist()

	if turtle_data.coins < ewcfg.tm_yahtzee_bet:
		response = "The bet for a round of turtle yahtzee is {} coins, but you only have {}.".format(ewcfg.tm_yahtzee_bet, turtle_data.coins)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if int_token is None:
		response = "Please specify which kind of dice you would like to use."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if user_data.poi != ewcfg.poi_id_turtlecasino:
		response = "You can only play turtle yahtzee at the turtle casino."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		dice_available = []
		if game_data.casino_state == ewcfg.tm_casino_state_closed:
			response = "The casino attendant regrets to inform you that they don't have any dice to play with. You can still buy and sell prizes for coins, though."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif game_data.casino_state == ewcfg.tm_casino_state_octet:
			dice_available.append(8)
		elif game_data.casino_state == ewcfg.tm_casino_state_dnd:
			dice_available = [4, 6, 8, 10, 12, 20]

		if int_token not in dice_available:
			response = "They don't have {}-sided dice. Try one of these: {}".format(int_token, dice_available)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		else:
			turtle_data.coins -= 2
			turtle_data.persist()

			response = "You pay {} coins and roll 2 {}-sided dice.".format(ewcfg.tm_yahtzee_bet, int_token)
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			dice = [int_token, int_token]
			result = []
			for die in dice:
				result.append(random.randrange(die) + 1)

			response = "{}".format(result)
			await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

			turtle_data = EwTurtle(id_user = turtle_data.id_user, id_server = turtle_data.id_server)
			if result[0] == result[1]:
				winnings = result[0] ** 2
				turtle_data.coins += winnings
				turtle_data.persist()
				response = "You win {} coins!".format(winnings)
			else:
				response = "You lost your bet..."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))




			
			
			


			case 'play':
				if (isPlayer) {
					activePlayer.distracting = false;
					activePlayer.dancing = false;
				}
				if(!(checkIfPlayer(userID) && playing && checkIfAlive(userID)) || channelID == turtlemurder.ch || channelID == trialgrounds.ch || channelID == pokeball.ch || channelID == ko.ch) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: you're not authorized to use this command",
						typing: true
					});
					break;
				} else if (bossFight) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: **I DON'T PLAY GAMES**",
						typing: true
					});
					break;
				} else if (channelID == channels.get("casino")) {
					if (!casinoOpen) {
						sendMessage({
							to: channelID,
							message: "**" + user + "**: the casino attendant regrets to inform you that they don't have any dice to play with. you can still buy and sell prizes for coins, though.",
							typing: true
						});
						break;

					} else {

						var dicetype;
						var price = 2;

						switch (obj) {
							case '4':
							case 'd4':
							case '2d4':
								if (casinoDice.includes(4)) {
									dicetype = 4;
									price = 1;
								}
								break;
							case '6':
							case 'd6':
							case '2d6':
								if (casinoDice.includes(6)) {
									dicetype = 6;
								}
								break;
							case '8':
							case 'd8':
							case '2d8':
							case '':
								if (casinoDice.includes(8)) {
									dicetype = 8;
								}
								break;
							case '10':
							case 'd10':
							case '2d10':
								if (casinoDice.includes(10)) {
									dicetype = 10;
								}
								break;
							case '12':
							case 'd12':
							case '2d12':
								if (casinoDice.includes(12)) {
									dicetype = 12;
								}
								break;
							case '20':
							case 'd20':
							case '2d20':
								if (casinoDice.includes(20)) {
									dicetype = 20;
									price = 4;
								}
								break;
							
						}

						if (dicetype == null) {
							sendMessage({
								to: channelID,
								message: "**" + user + "**: that's not a valid game to play at this time.",
								typing: true
							});
							break;
						}

						if (activePlayer.coins < price) {
							sendMessage({
								to: channelID,
								message: "**" + user + "**: you don't have enough coins to buy into this game.",
								typing: true
							});
							break;



						}

						players.forEach( function (p) {
							if (p.id == userID) {
								p.coins -= price;

								var dice = rollxdy(2,dicetype);
								var result;
								if (price == 1) {
									result = "**" + user + "**: You pay " + price + " coin to play. You roll 2d" + dicetype + ". If you get doubles, you win the number you got doubles of squared coins.\n" + dice + "\n";
								} else {
									result = "**" + user + "**: You pay " + price + " coins to play. You roll 2d" + dicetype + ". If you get doubles, you win the number you got doubles of squared coins.\n" + dice + "\n";
								}
								if (dice[0] == dice[1]) {
									var prize = dice[0] * dice[0];
									result += "It's your lucky day! You win " + prize + " coins. You can trade them for prizes."
									p.coins += prize;
								} else {
									result += "You lose. Better luck next time."
								}
								sendMessage({
									to: channelID,
									message: result,
									typing: true
								});

							}

						});
					}


				} else if (channelID == channels.get("arcade")) {
					var result = "**" + user + "**: ";
					players.forEach( function(p) {
						if (p.id == userID) {
							if (p.coins > 0) {
								p.coins--;

								var i;
								for (i = 0; i < 1000; i++) {
									arcadeGames = arcadeGames.sort(randomSort);
								}
								result += "You insert a coin into one of the machines.\n" + arcadeGames[0];
							} else {
								result += "you don't have any coins to play with."
							}
						}
					});
					sendMessage({
						to: channelID,
						message: result,
						typing: true
					});
					break;
					
				} else {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: there aren't any games to play here.",
						typing: true
					});
					break;

				}

			break;
async def tm_prizes(cmd):
			case 'prizes':
				if (isPlayer) {
					activePlayer.distracting = false;
					activePlayer.dancing = false;
				}
				if(!(checkIfPlayer(userID) && playing && checkIfAlive(userID)) || channelID == turtlemurder.ch || channelID == trialgrounds.ch || channelID == pokeball.ch || channelID == ko.ch) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: you're not authorized to use this command",
						typing: true
					});
					break;
				} else if (bossFight) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: **YOUR ONLY PRIZE WILL BE A SWIFT DEMISE, IF YOU SUBMIT NOW**",
						typing: true
					});
					break;
				} else if (channelID != channels.get("casino")) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: there are no prizes here.",
						typing: true
					});
					break;
				} else {
					var result = "**" + user + "**: the casino offers the following prizes:"

					casinoInventory.forEach( function (i) {
						result += "\n" + i + ": " + database.casinoprices[i] + " coins";
						
					});


					sendMessage({
						to: channelID,
						message: result,
						typing: true
					});
				}
			break;
async def tm_buy(cmd):
			case 'buy':
				if (isPlayer) {
					activePlayer.distracting = false;
					activePlayer.dancing = false;
				}
				if(!(checkIfPlayer(userID) && playing && checkIfAlive(userID)) || channelID == turtlemurder.ch || channelID == trialgrounds.ch || channelID == pokeball.ch || channelID == ko.ch) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: you're not authorized to use this command",
						typing: true
					});
					break;
				} else if (bossFight) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: **I HAVE NO USE FOR THOSE RIDICULOUS TOKENS OF YOURS**",
						typing: true
					});
					break;
				} else if (channelID != channels.get("casino")) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: there's nothing to buy here",
						typing: true
					});
					break;
				} else if (obj == "") {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: please specify what you want to buy. (!prizes to see what items are on offer)",
						typing: true
					});
					break;					
				} else if (!casinoInventory.includes(obj)) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: they don't have that item. (!prizes to see what items are on offer)",
						typing: true
					});
					break;					
				}  else {

					players.forEach (function (p) {
						if (p.id == userID) {
							var price = database.casinoprices[obj];
							if (p.coins < price) {
								result = "**" + user + "**: you can't afford this item";
							} else {
								p.coins -= price;
								casinoInventory = casinoInventory.filter( function (i) { return i != obj; });
								p.addItem(obj);
								result = "**" + user + "**: you successfully purchase the " + obj;
							}

						}

					});
					sendMessage({
						to: channelID,
						message: result,
						typing: true
					});
					break;					
				}
			break;
async def tm_sell(cmd):
			case 'sell':
				if (isPlayer) {
					activePlayer.distracting = false;
					activePlayer.dancing = false;
				}
				if(!(checkIfPlayer(userID) && playing && checkIfAlive(userID)) || channelID == turtlemurder.ch || channelID == trialgrounds.ch || channelID == pokeball.ch || channelID == ko.ch) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: you're not authorized to use this command",
						typing: true
					});
					break;
				} else if (bossFight) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: **I DON'T MAKE DEALS WITH VERMIN**",
						typing: true
					});
					break;
				} else if (channelID != channels.get("casino")) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: nobody here will buy this",
						typing: true
					});
					break;
				} else if (obj == "") {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: please specify what you want to sell. (!inventory to see what items you have)",
						typing: true
					});
					break;									
				}  else {

					players.forEach (function (p) {
						if (p.id == userID) {
							var price = database.casinoprices[obj] / 2;
							if (!p.hasItem(obj)) {
								result = "**" + user + "**: you don't own that item (!inventory to see what items you have)";
							} else {
								p.coins += price;
								casinoInventory.push(obj);
								p.removeItem(obj);
								if(p.weapon == obj) {p.weapon = "fists";}
								result = "**" + user + "**: you successfully sell the " + obj + " for " + price + " coins.";
							}

						}

					});
					casinoInventory = casinoInventory.filter(function(item) {return !animeMerch.includes(item);});
					sendMessage({
						to: channelID,
						message: result,
						typing: true
					});
					break;					
				}

			break;
async def tm_enter(cmd):
			case 'enter':
				if (players.some(function(value) {return value.id == userID;})) {
					if (bossFight) {
						sendMessage({
							to: channelID,
							message: "**" + user + "**: **YOU'RE ALREADY SUFFERING**",
							typing: true
						});
						break;
					} else {
						sendMessage({
							to: channelID,
							message: "**" + user + "**: you're already playing!",
							typing: true
						});
					}
				} else if (playing) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: game already in progress. you'll have to wait for the next round.",
						typing: true
					});
				} else {
					players.push(new Player(user, userID));
					sendMessage({
						to: channelID,
						message: user + " entered the game",
						typing: true
					});
				}
								
				break;
async def tm_players(cmd):
			case 'players':
				sendMessage({
					to: channelID,
					message: "players:",
					typing: true
				});

				players.forEach(function(value) {
					sendMessage({
						to: channelID,
						message: "<@" + value.id + ">",
						typing: true
					});
				});
				break;
async def tm_start(cmd):
			case 'start':
				if(!checkIfPlayer(userID)) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: you're not authorized to use this command",
						typing: true
					});
					break;
				}
				if(playing) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: game already in progress.",
						typing: true
					});
				} else {
					sendMessage({
						to: channelID,
						message: "initializing game",
						typing: true
					});

					players.forEach(function(p) {
						var guild = bot.channels.get(channelID).guild;
						var member = guild.members.get(p.id);
						member.addRole(p.room);
					});


					var targets = [];
					players.forEach(function(value,index) {targets[index] = players[index];});

					

					var i;
					for(i = 0; i < 1000; i++) {
						targets.sort(randomSort);
						players.sort(randomSort);
					}
					

					players.forEach(function(value, index) {
						if (index != players.length - 1) {
							while(value.id == targets[targets.length - 1].id) {
								targets.sort(randomSort);
							}
						}
						value.target = targets.pop().id;
					});
					for(i = 0; i < 1000; i++) {
						startingItems.sort(randomSort);
						players.sort(randomSort);
					}
					players.forEach(function(p) {
						if (startingItems.length > 0) {
							p.addItem(startingItems.pop());
							p.coins = 5;
						} else {
							p.coins = 10;
						}

						var i;
						var max = Math.random() * 2 + 4;
						for (i = 0; i < max; i++) {
							var rndm = Math.random();
							if (rndm < 0.35) {
								animePile.push(animeMerch[0]);
							} else if (rndm < 0.6) {
								animePile.push(animeMerch[1]);
							} else if (rndm < 0.75) {
								animePile.push(animeMerch[2]);
							} else if (rndm < 0.87) {
								animePile.push(animeMerch[3]);
							} else if (rndm < 0.95) {
								animePile.push(animeMerch[4]);
							} else {
								animePile.push(animeMerch[5]);
							}
						}

						
					});
					animePile.push("dnd-dice");
					for(i = 0; i < 1000; i++) {
						animePile.sort(randomSort);
					}
					playing = true;
					casinoInventory = casinoInventory.concat(startingItems);

					sendMessage({
						to: channelID,
						message: "you can start playing now (!help for help)",
						typing: true
					});
				}
				
				break;
async def tm_target(cmd):
			case 'target':
				if(!(checkIfPlayer(userID) && playing && checkIfAlive(userID)) || channelID == turtlemurder.ch ) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: you're not authorized to use this command",
						typing: true
					});
					break;
				} else if (bossFight) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: **YOUR PETTY SQUABBLES DON'T MATTER ANYMORE**",
						typing: true
					});
					break;
				}
				players.forEach(function(value) {
				if (value.id == userID)
				 {sendMessage({
					to: userID,
					message:"your target is <@" +  value.target + ">",
					typing: true
					});}});
				break;
async def tm_coins(cmd):
			case 'coin':
			case 'coins':
				if(!(checkIfPlayer(userID) && playing && checkIfAlive(userID)) || channelID == turtlemurder.ch ) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: you're not authorized to use this command",
						typing: true
					});
					break;
				} else if (bossFight) {
					sendMessage({
						to: channelID,
						message: "**" + user + "**: **YOUR RICHES ARE WORTHLESS NOW**",
						typing: true
					});
					break;
				}

				var result = "**" + user + "**: you have ";
				players.forEach( function(p) {
					
					if (p.id == userID) {
							result += p.coins + " coins.";
					}
				});

				sendMessage({
					to: channelID,
					message: result
				});
				break;
async def tm_endgame(cmd):
			case 'endgame':
				reset();

				sendMessage({
					to: turtlemurder.ch,
					message: "game ended by " + user + "."
				});
				break;
async def tm_help(cmd):
			case 'help':
				sendMessage({
					to: userID,
					message:"Welcome to Happy Turtle Murder Extravaganza. In this game you play an assassin, who has to kill their target without anyone noticing. But watch out, someone else has you as their target, too. After a murder has occurred, everyone gets to vote on who they think did it. If the culprit receives more votes than any other player, they are executed. Otherwise the killer wins and everyone else loses. The game continues, as long as there are at least 4 players left alive, or until a player wins.\n" +
						"__Note about weapons:__ Weapons are single use. You can only kill one person with each weapon. Most weapons will also be automatically left behind at the crime scene for everyone to see.\n" +
						"__Note about targets:__ If you kill someone other than your target, the player who had that target will immediately be notified to receive their substitute target, so avoid unnecessary bloodshed.\n" + 
						"__Note about the trial-grounds:__ The trial-grounds are where you can cast your votes on who you think the culprit was for each case. The trial-grounds are a strict no-combat zone. You are completely safe there. The voting only starts once everyone has entered the trial-grounds. You can go there at any time and from anywhere. However, it's a one-way trip. Once you enter the trial-grounds, you won't be able to leave, until a verdict has been reached.\n" 
				});

				sendMessage({
					to: userID,
					message:"**Game Setup:**\n" +
						"'!help': display this help message\n" +
						"'!enter': enter the game\n" + 
						"'!start': start a game with all entered players\n" +
						"'!players': list all entered players\n" +
						"'!endgame': ends the game for everyone\n" +
						"**Information:**\n" +
						"'!peek <room>': check which players are in an adjacent room.\n" +
						"'!look': shows information about the room you're currently in\n" +
						"'!target': find out who you're supposed to kill\n" +
						"'!inventory': shows what items you are carrying\n" +
						"'!weapon': check which weapon you have equipped\n" +
						"'!coins': check how many coins you have to your name\n" +
						"**Basic Actions:**\n" +
						"'!goto <room>': move to a new room. you can only move to rooms that are adjacent to yours, except for the trial-grounds\n" +
						"'!use <item>': use an item from your inventory\n" +
						"'!equip <weapon>': equip a weapon from your inventory\n" +
						"'!attack <@player>': attack a player with your equipped weapon. only works if you're in the same room with them\n" +
						"'!vote <@player>': cast your vote for who you think the killer is. only works in the trial-grounds"
				});
				break;
