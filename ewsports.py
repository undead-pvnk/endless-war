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

	def __init__(self, id_user, id_server, id_game):

		self.id_user = id_user
		self.id_server = id_server
		self.id_game = id_game
		
		global sb_count

		self.id_player = sb_count
		sb_count += 1

		global sb_games

		game_data = sb_games.get(id_game)

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

		shamble_player = EwShambleBallPlayer(cmd.message.author.id, cmd.message.server.id, game_data.id_game)
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

	poi_data = ewcfg.chname_to_poi.get(cmd.message.channel.name)

	

async def shamblestop(cmd):
