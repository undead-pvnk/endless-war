import time
import random

import ewcfg
import ewutils

from ew import EwUser
from ewdistrict import EwDistrict

sb_count = 0

sb_games = {}
sb_poi_to_game = {}

sb_shambleid_to_player = {}
sb_userid_to_player = {}

#sports
class EwShambleBallPlayer:

	id_user = ""
	id_server = ""
	id_player = -1

	id_game = -1

	coords = None
	velocity = None
	team = ""

	def __init__(self, id_user, id_server, id_game, team):

		self.id_user = id_user
		self.id_server = id_server
		self.id_game = id_game
		self.team = team

		global sb_count

		self.id_player = sb_count
		sb_count += 1

		global sb_games

		self.velocity = (0, 0)
		

		game_data = sb_games.get(id_game)
		while not game_data.coords_free(self.coords):
			self.coords = get_starting_position(self.team)

		game_data.players.append(self)

		global sb_shambleid_to_player
		global sb_userid_to_player
		sb_userid_to_player[self.id_user] = self
		sb_shambleid_to_player[self.id_player] = self


		
			

class EwShambleBallGame:

	id_game = -1

	players = []

	poi = ""

	ball_coords = None

	ball_velocity = None

	def __init__(self, poi):
		self.poi = poi

		global sb_count
		self.id_game = sb_count

		sb_count += 1

		global sb_games
		sb_games[self.id_game] = self

		global sb_poi_to_game
		sb_poi_to_game[self.poi] = self

		self.players = []

		while not self.coords_free(self.ball_coords):
			self.ball_coords = get_starting_position("")

		self.ball_velocity = (0, 0)

	def coords_free(self, coords):

		if coords == None or len(coords) != 2:
			return False

		if coords == self.ball_coords:
			return False

		for p in self.players:
			if p.coords == coords:
				return False

		return True

def get_starting_position(team):
	coords = ()
	if team == "purple":
		coords.append(random.randrange(10, 40))
		coords.append(random.randrange(10, 40))
	elif team == "pink":
		coords.append(random.randrange(60, 90))
		coords.append(random.randrange(10, 40))
	else:
		coords.append(random.randrange(49, 51))
		coords.append(random.randrange(20, 30))

	return coords

def get_coords(tokens):

	coords = []
	for token in tokens:
		if len(coords) == 2:
			break
		try:
			int_token = int(token)
			coords.append(int_token)
		except:
			pass
	
	return coords

async def shambleball(cmd):

	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state != ewcfg.life_state_shambler:
		response = "You have too many higher brain functions left to play Shambleball."
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	if ewmap.channel_name_is_poi(cmd.message.channel.name):
		response = "You have to go into the city to play Shambleball."
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	poi_data = ewcfg.chname_to_poi.get(cmd.message.channel.name)

	if poi_data.is_subzone or poi_data.is_transport:
		response = "This place is too cramped for playing Shambleball. Go outside!"
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	district_data = EwDistrict(district = poi_data.id_poi, id_server = cmd.message.server.id)

	if not district_data.is_degraded:
		response = "This place is too functional and full of people to play Shambleball. You'll have to {} it first.".format(ewcfg.cmd_shamble)
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	team = ewutils.flattenTokenListToString(cmd.tokens[1:])
	if team not in ["purple", "pink"]:
		response = "Please choose if you want to play on the pink team or the purple team."
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	global sb_userid_to_player
	shamble_player = sb_userid_to_player.get(cmd.message.author.id)

	if shamble_player != None:
		global sb_games
		game_data = sb_games.get(shamble_player.id_game)

		if game_data.poi != poi_data.id_poi:
			game_data.players.remove(shamble_player)
			game_data = None

	if game_data == None:
		global sb_poi_to_game
		game_data = sb_poi_to_game.get(poi_data.id_poi)
		response = "You join the Shambleball game on the {team} team."
		if game_data == None:
			game_data = EwShambleBallGame(poi_data.id_poi)
			response = "You put your severed head on the floor and start a new game of Shambleball as a {team} team player."

		shamble_player = EwShambleBallPlayer(cmd.message.author.id, cmd.message.server.id, game_data.id_game, team)
	else:
		response = "You are playing Shambleball on the {team} team. You are currently at {player_coords} going in direction {player_vel}. The ball is currently at {ball_coords} going in direction {ball_vel}."

	response = response.format(team = shamble_player.team, player_coords = shamble_player.coords, ball_coords = game_data.ball_coords, player_vel = player.velocity, ball_vel = game_data.ball_velocity)
	return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

async def shamblego(cmd):

	global sb_userid_to_player
	shamble_player = sb_userid_to_player.get(cmd.message.author.id)

	if shamble_player == None:
		response = "You have to join a game using {} first.".format(ewcfg.cmd_shambleball)
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	if ewmap.channel_name_is_poi(cmd.message.channel.name):
		response = "You have to go into the city to play Shambleball."
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	global sb_games
	game_data = sb_games.get(shamble_player.id_game)

	poi_data = ewcfg.chname_to_poi.get(cmd.message.channel.name)

	if poi_data.id_poi != game_data.poi:
		game_poi = ewcfg.id_to_poi.get(game_data.poi)
		response = "Your Shambleball game is happening in the #{} channel.".format(game_poi.channel)
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))


	target_coords = get_coords(cmd.tokens[1:])

	if len(target_coords) != 2:
		response = "Specify where you want to {} to.".format(ewcfg.cmd_shamblego)

	target_vector = ewutils.EwVector2D(target_coords)
	current_vector = ewutils.EwVector2D(shamble_player.coords)

	target_direction = target_vector.subtract(current_vector)
	target_direction = target_direction.normalize()

	current_direction = ewutils.EwVector2D(shamble_player.velocity)

	result_direction = current_direction.add(target_direction)
	
	shamble_player.velocity = result_direction.vector

async def shamblestop(cmd):
	global sb_userid_to_player
	shamble_player = sb_userid_to_player.get(cmd.message.author.id)

	if shamble_player == None:
		response = "You have to join a game using {} first.".format(ewcfg.cmd_shambleball)
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	if ewmap.channel_name_is_poi(cmd.message.channel.name):
		response = "You have to go into the city to play Shambleball."
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	global sb_games
	game_data = sb_games.get(shamble_player.id_game)

	poi_data = ewcfg.chname_to_poi.get(cmd.message.channel.name)

	if poi_data.id_poi != game_data.poi:
		game_poi = ewcfg.id_to_poi.get(game_data.poi)
		response = "Your Shambleball game is happening in the #{} channel.".format(game_poi.channel)
		return await ewutils.send_response(cmd.client, cmd.message.channel, ewutils.formatResponse(cmd.message.author, response))

	shamble_player.velocity = (0, 0)
