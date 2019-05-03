import asyncio
import time
import math

from copy import deepcopy

import ewutils
import ewcmd
import ewrolemgr
import ewcfg

from ew import EwUser
from ewdistrict import EwDistrict
from ewtransport import EwTransport

move_counter = 0

"""
	Returns true if the specified point of interest is a PvP zone.
"""
def poi_is_pvp(poi_name = None):
	poi = ewcfg.id_to_poi.get(poi_name)

	if poi != None:
		return poi.pvp
	
	return False

"""
	Returns true if the specified name is used by any POI.
"""
def channel_name_is_poi(channel_name):
	if channel_name != None:
		for poi in ewcfg.poi_list:
			if poi.channel == channel_name:
				return True

	return False

"""
	Point of Interest (POI) data model
"""
class EwPoi:
	# The typable single-word ID of this location.
	id_poi = ""

	# Acceptable alternative typable single-word names for this place.
	alias = []

	# The nice name for this place.
	str_name = ""

	# You find yourself $str_in $str_name
	str_in = "in"

	# You $str_enter $str_name
	str_enter = "enter"

	# A description provided when !look-ing here.
	str_desc = ""

	# (X, Y) location on the map (left, top) zero-based origin.
	coord = None
	coord_alias = []

	# Channel name associated with this POI
	channel = ""

	# Discord role associated with this zone (control channel visibility).
	role = None

	# Zone allows PvP combat and interactions.
	pvp = True

	# Factions allowed in this zone.
	factions = []

	# Life states allowed in this zone.
	life_states = []

	# If true, the zone is inaccessible.
	closed = False

	# Message shown before entering the zone fails when it's closed.
	str_closed = None

	# Vendor names available at this POI.
	vendors = []

	# The value of the district
	property_class = ""

	# If true, the zone is a district that can be controlled/captured
	is_capturable = False

	# If it's a subzone
	is_subzone = False

	# What District each subzone is in
	mother_district = ""

	# If it's a mobile zone
	is_transport = False

	# which type of transport
	transport_type = ""
	
	# default line to follow, if it's a transport
	default_line = ""

	# default station to start at, if it's a transport
	default_stop = ""
	
	# If a transport line stops here
	is_transport_stop = True

	# which transport lines stop here
	transport_lines = set()


	def __init__(
		self,
		id_poi = "unknown", 
		alias = [],
		str_name = "Unknown",
		str_desc = "...",
		str_in = "in",
		str_enter = "enter",
		coord = None,
		coord_alias = [],
		channel = "",
		role = None,
		pvp = True,
		factions = [],
		life_states = [],
		closed = False,
		str_closed = None,
		vendors = [],
		property_class = "",
		is_capturable = False,
		is_subzone = False,
		mother_district = "",
		is_transport = False,
		transport_type = "",
		default_line = "",
		default_stop = "",
		is_transport_stop = False,
		transport_lines = None
	):
		self.id_poi = id_poi
		self.alias = alias
		self.str_name = str_name
		self.str_desc = str_desc
		self.str_in = str_in
		self.str_enter = str_enter
		self.coord = coord
		self.coord_alias = coord_alias
		self.channel = channel
		self.role = role
		self.pvp = pvp
		self.factions = factions
		self.life_states = life_states
		self.closed = closed
		self.str_closed = str_closed
		self.vendors = vendors
		self.property_class = property_class
		self.is_capturable = is_capturable
		self.is_subzone = is_subzone
		self.mother_district = mother_district
		self.is_transport = is_transport
		self.transport_type = transport_type
		self.default_line = default_line
		self.default_stop = default_stop
		self.is_transport_stop = is_transport_stop
		self.transport_lines = transport_lines

map_world = [
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, -1, -1, -1, -2, -1, -2, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1, 20, -1, -1, -1, 20, -1, 20, -1, -1, -1, -1, 20, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -2, 30,  0, -1, -1, -1, 20, -1, -1, -1, -1, -1, -2, 20, -3, 20, -2, -1, -2, -3, -3, 30,  0,  0, 30, -2, 30,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, 20, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1,  0,  0,  0, 30, -2, 30,  0,  0,  0, -1, -1, -1, -3, -1, -1, -1, 30, -1, -1, -1,  0, -1, -1, 30, -1, -1, -1, -1,  0,  0, 30, -2, 30,  0, 30, -3, 20, -2, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1,  0, -1, -1, -1, 20, -1, -1, -1,  0,  0,  0, -1, -3, -1,  0,  0,  0,  0, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -3, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1,  0, -1, -1, -1, -2, -1, -1, -1, -1, -1,  0, 30, -2, 30,  0, -1, -1,  0, -1, -1, 30, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, 30, -2, 20, -2, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1,  0,  0,  0, -1, 30, -1, -1, -1, -1,  0, -1, -1, -2, 30,  0,  0,  0, -1, -1, -1, -1, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, 30, -1,  0,  0,  0,  0,  0, -1, 30, -1, -1, -1,  0, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1,  0, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, 30, -2, 30,  0, -1, -1, -1,  0, 30, -2, 20, -2, -1,  0, -1, -1, -1, -1,  0,  0, -1, -2, -1, -1, -1,  0,  0, 30, -2, 30,  0,  0,  0,  0, -1, -3, 20, -2, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1,  0, -1, -1,  0, -1, -1, -2, -1, -1, -3, -1, -1, -1,  0, -1, -1, -1, -1, -1, 30, -1, 20, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, 30, -1, -3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1,  0, -1, -1,  0, -1, -1, 20, -1, -1, -3, 20, -2, -1,  0, -1, -1, -1, -2, 20, -2, -3, -3, 30,  0,  0,  0,  0,  0,  0, -1,  0,  0, 30, -2, -3, -3, 20, -2, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1,  0, -1, -1,  0,  0, 30, -2, -1, -1, 30, -1, -1, -1, 30, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, 30, -1, 20, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, 30, -1, -1,  0,  0,  0, 30, -2, 30,  0,  0,  0,  0,  0, -1,  0,  0, 30, -2, -3, -3, 30,  0, -1,  0, -1, -1,  0, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -2, 20, -2, 30,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, 20, -1, -1, -1, -1, -1,  0, -1,  0, -1, -1, 20, -1, 20, -1,  0,  0,  0, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, 30, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, 30, -1, 30, -1, -1, -2, -1, -2, -1,  0, -1, -1, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1,  0, 30, -3, -3, -2, 30,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -2, 20, -2, -3, -3, 20, -2, -1, -1, -1, -1,  0, -1, -1, -1, -1,  0,  0, 30, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1,  0, -1, 20, -1, 30, -1,  0, -1, -1, -1,  0, -1, -2, -1, -2, -1, -1, -1, -1, -3, -1, -3, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, 30, -1, -2, -1,  0, -1, 30, -1, -1, -1,  0, -1, 20, -1, 20, -1,  0,  0, 30, -3, -1, -3, 20, -2, -1, -1, -2, 20, -2, 20, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -2, 20, -2, -3, -1,  0,  0, 30, -2, 20, -2, -1,  0, 30, -2, -3, -3, 30,  0, -1, -1, 20, -1, 30, -1, -1, -1, -1, -1, -1, 20, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -3, 30,  0, -1, -1, -3, -1, -1, -1, -1, -1, 30, -1, -1, -1,  0, -1, -1, -2, -1, 30, -1, -1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, 30, -1, -1,  0, 30, -3, 30, 30, -1, -1, -1,  0, -1, -1,  0,  0, -1, -1, -1, -1, -2, -3, -3, 20, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1,  0, -1, -1, 30, -1, 20, -1, -2, 30,  0,  0,  0, -1, -1, 30, -1,  0,  0,  0,  0, 30, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -2, 20, -2, 30,  0,  0, 30, -2, -1, -2, -1, -3, -1,  0, -1, -1,  0, 30, -2, 30,  0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, 20, -1, -1, -1, -1, 30, -1, -1, -1, -3, -1, 30, -1, -1,  0, -1, 20, -1, -1, -1, -1, -1, -2, 20, -2, 20, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -2, -1, -1, -1, -1,  0,  0,  0, 30, -3, -1, -2, 30,  0,  0, -1, -2, -1, -1, -1, -1, -1, -1, -1, -3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -3, -1, 20, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -2, 20, -3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, 20, -3, -1, -2, -1, -1,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 20, -1, -1, -1, -1,  0, 30, -2, -3, -3, 30,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, 20, -1, 20, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ],
	[ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ]
]
map_width = len(map_world[0])
map_height = len(map_world)

sem_wall = -1
sem_city = -2
sem_city_alias = -3

def pairToString(pair):
	return "({},{})".format("{}".format(pair[0]).rjust(2), "{}".format(pair[1]).ljust(2))

"""
	Find the cost to move through ortho-adjacent cells.
"""
def neighbors(coord):
	neigh = []

	if coord[1] > 0 and map_world[coord[1] - 1][coord[0]] != sem_wall:
		neigh.append((coord[0], coord[1] - 1))
	if coord[1] < (map_height - 1) and map_world[coord[1] + 1][coord[0]] != sem_wall:
		neigh.append((coord[0], coord[1] + 1))

	if coord[0] > 0 and map_world[coord[1]][coord[0] - 1] != sem_wall:
		neigh.append((coord[0] - 1, coord[1]))
	if coord[0] < (map_width - 1) and map_world[coord[1]][coord[0] + 1] != sem_wall:
		neigh.append((coord[0] + 1, coord[1]))

	return neigh


"""
	Directions and cost from coord to arrive at a destination.
"""
class EwPath:
	visited = None
	steps = None
	cost = 0
	iters = 0
	pois_visited = None

	def __init__(
		self,
		path_from = None,
		steps = [],
		cost = 0,
		visited = {},
		pois_visited = set()
	):
		if path_from != None:
			self.steps = deepcopy(path_from.steps)
			self.cost = path_from.cost
			self.visited = deepcopy(path_from.visited)
			self.pois_visited = deepcopy(path_from.pois_visited)
		else:
			self.steps = steps
			self.cost = cost
			self.visited = visited
			self.pois_visited = pois_visited
			

"""
	Add coord_next to the path.
"""
def path_step(path, coord_next, user_data, coord_end):
	mutations = user_data.get_mutations()
	visited_set_y = path.visited.get(coord_next[0])
	if visited_set_y == None:
		path.visited[coord_next[0]] = { coord_next[1]: True }
	elif visited_set_y.get(coord_next[1]) == True:
		# Already visited
		return False
	else:
		path.visited[coord_next[0]][coord_next[1]] = True

	cost_next = map_world[coord_next[1]][coord_next[0]]

	if cost_next == sem_city or cost_next == sem_city_alias:
		next_poi = ewcfg.coord_to_poi.get(coord_next)

		if inaccessible(user_data = user_data, poi = next_poi):
			return False
		else:
			cost_next = 0
			
			# check if we already got the movement bonus/malus for this district
			if not next_poi.id_poi in path.pois_visited:
				path.pois_visited.add(next_poi.id_poi)
				if len(user_data.faction) > 0 and next_poi.coord != coord_end and next_poi.coord != path.steps[0]:
					district = EwDistrict(
						id_server = user_data.id_server,
						district = next_poi.id_poi
					)

					if district != None and len(district.controlling_faction) > 0:
						if user_data.faction == district.controlling_faction:
							cost_next = -ewcfg.territory_time_gain
						else:
							cost_next = ewcfg.territory_time_gain
					else:
						cost_next = 0
				else:
					cost_next = 0

	path.steps.append(coord_next)
	if ewcfg.mutation_id_bigbones in mutations:
		cost_next *= 2

	if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() > 0.9:
		cost_next = int(cost_next / 2)

	path.cost += cost_next

	return True

"""
	Returns a new path including all of path_base, with the next step coord_next.
"""
def path_branch(path_base, coord_next, user_data, coord_end):
	path_next = EwPath(path_from = path_base)

	if path_step(path_next, coord_next, user_data, coord_end) == False:
		return None
	
	return path_next

def path_to(
	coord_start = None,
	coord_end = None,
	poi_start = None,
	poi_end = None,
	user_data = None
):
	score_golf = math.inf
	score_map = []
	for row in map_world:
		score_map.append(list(map(replace_with_inf, row)))

	paths_finished = []
	paths_walking = []

	pois_adjacent = []

	if poi_start != None:
		poi = ewcfg.id_to_poi.get(poi_start)

		if poi != None:
			coord_start = poi.coord

	if poi_end != None:
		poi = ewcfg.id_to_poi.get(poi_end)

		if poi != None:
			coord_end = poi.coord

	path_base = EwPath(
		steps = [ coord_start ],
		cost = 0,
		visited = { coord_start[0]: { coord_start[1]: True } }
	)


	paths_walking.append(path_base)

	count_iter = 0
	while len(paths_walking) > 0:
		count_iter += 1

		paths_walking_new = []

		for path in paths_walking:
			step_last = path.steps[-1]
			score_current = score_map[step_last[1]][step_last[0]]
			if path.cost >= score_golf or path.cost >= score_current:
				continue

			score_map[step_last[1]][step_last[0]] = path.cost

			step_penult = path.steps[-2] if len(path.steps) >= 2 else None


			if coord_end != None:
				# Arrived at the actual destination?
				if step_last == coord_end:
					path_final = path
					if path_final.cost < score_golf:
						score_golf = path_final.cost
						paths_finished = []
					if path_final.cost <= score_golf:
						paths_finished.append(path_final)
					continue

			else:
				# Looking for adjacent points of interest.
				sem_current = map_world[step_last[1]][step_last[0]]
				poi_adjacent_coord = step_last
				if sem_current == sem_city_alias:
					poi_adjacent_coord = ewcfg.alias_to_coord.get(step_last)

					if poi_adjacent_coord != None:
						sem_current = sem_city

				if sem_current == sem_city and poi_adjacent_coord != coord_start:
					poi_adjacent = ewcfg.coord_to_poi.get(poi_adjacent_coord)

					if poi_adjacent != None:
						pois_adjacent.append(poi_adjacent)
						continue

			path_base = EwPath(path_from = path)
			for neigh in neighbors(step_last):
				if neigh == step_penult:
					continue

				branch = path_branch(path_base, neigh, user_data, coord_end)
				if branch != None:
					paths_walking_new.append(branch)


		paths_walking = paths_walking_new

	if coord_end != None:
		path_true = None
		if len(paths_finished) > 0:
			path_true = paths_finished[0]
			path_true.iters = count_iter
		if path_true is None:
			ewutils.logMsg("Could not find a path.")
		return path_true
	else:
		return pois_adjacent

def replace_with_inf(n):
	return math.inf

"""
	Debug method to draw the map, optionally with a path/route on it.
"""
def map_draw(path = None, coord = None):
	y = 0
	for row in map_world:
		outstr = ""
		x = 0

		for col in row:
			if col == sem_wall:
				col = "  "
			elif col == sem_city:
				col = "CT"
			elif col == sem_city_alias:
				col = "ct"
			elif col == 0:
				col = "██"
			elif col == 30:
				col = "[]"
			elif col == 20:
				col = "••"

			if path != None:
				visited_set_y = path.visited.get(x)
				if visited_set_y != None and visited_set_y.get(y) != None:
					col = "." + col[-1]

			if coord != None and coord == (x, y):
				col = "O" + col[-1]
					
			outstr += "{}".format(col)
			x += 1

		print(outstr)
		y += 1

def inaccessible(user_data = None, poi = None):
	if poi == None or user_data == None:
		return True;

	if(
		len(poi.factions) > 0 and
		len(user_data.faction) > 0 and
		user_data.faction not in poi.factions
	) or (
		len(poi.life_states) > 0 and
		user_data.life_state not in poi.life_states
	):
		return True
	else:
		return False


"""
	Player command to move themselves from one place to another.
"""
async def move(cmd):
	if channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

	target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
	if target_name == None or len(target_name) == 0:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Where to?"))

	user_data = EwUser(member = cmd.message.author)
	poi_current = ewcfg.id_to_poi.get(user_data.poi)
	poi = ewcfg.id_to_poi.get(target_name)

	if poi == None:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Never heard of it."))

	if poi.id_poi == user_data.poi:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're already there, bitch."))

	if inaccessible(user_data = user_data, poi = poi):
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're not allowed to go there (bitch)."))

	if user_data.life_state == ewcfg.life_state_corpse and user_data.busted:
		if user_data.poi == ewcfg.poi_id_thesewers:
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You're busted, bitch. You can't leave the sewers until your !revive."))
		else:  # sometimes busted ghosts get stuck outside the sewers
			user_data.poi = ewcfg.poi_id_thesewers
			user_data.persist()
			await ewrolemgr.updateRoles(cmd.client, cmd.message.author)
			return

	if poi.coord == None or poi_current == None or poi_current.coord == None:
		if user_data.life_state == ewcfg.life_state_corpse:
			path = EwPath(cost = 60)
		else:
			path = None
	else:
		path = path_to(
			poi_start = user_data.poi,
			poi_end = target_name,
			user_data = user_data
		)

	if path == None:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You don't know how to get there."))

	global move_counter

	# Check if we're already moving. If so, cancel move and change course. If not, register this course.
	move_current = ewutils.moves_active.get(cmd.message.author.id)
	move_counter += 1

	# Take control of the move for this player.
	move_current = ewutils.moves_active[cmd.message.author.id] = move_counter

	minutes = int(path.cost / 60)
	seconds = path.cost % 60

	msg_walk_start = await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You begin walking to {}.{}".format(
		poi.str_name,
		(" It's {} minute{}{} away.".format(
			minutes,
			("s" if minutes != 1 else ""),
			(" and {} seconds".format(seconds) if seconds > 4 else "")
		) if minutes > 0 else (" It's {} seconds away.".format(seconds) if seconds > 30 else ""))
	)))

	life_state = user_data.life_state
	faction = user_data.faction

	# Moving to or from a place not on the map (e.g. the sewers)
	if poi.coord == None or poi_current == None or poi_current.coord == None:
		if path.cost > 0:
			await asyncio.sleep(path.cost)

		if ewutils.moves_active[cmd.message.author.id] != move_current:
			return

		user_data = EwUser(member = cmd.message.author)

		# If the player dies or enlists or whatever while moving, cancel the move.
		if user_data.life_state != life_state or faction != user_data.faction:
			try:
				await cmd.client.delete_message(msg_walk_start)
			except:
				pass

			return

		user_data.poi = poi.id_poi
		user_data.time_lastenter = int(time.time())
		user_data.persist()

		await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

		channel = cmd.message.channel

		# Send the message in the channel for this POI if possible, else in the origin channel for the move.
		for ch in cmd.message.server.channels:
			if ch.name == poi.channel:
				channel = ch
				break

		msg_walk_enter = await ewutils.send_message(cmd.client, 
			channel,
			ewutils.formatMessage(
				cmd.message.author,
				"You {} {}.".format(poi.str_enter, poi.str_name)
			)
		)
		try:
			await cmd.client.delete_message(msg_walk_start)
			await asyncio.sleep(30)
			await cmd.client.delete_message(msg_walk_enter)
		except:
			pass

	else:
		boost = 0

		# Perform move.
		for step in path.steps[1:]:
			# Check to see if we have been interrupted and need to not move any farther.
			if ewutils.moves_active[cmd.message.author.id] != move_current:
				break

			val = map_world[step[1]][step[0]]
			poi_current = None

			# Standing on the actual city node.
			if val == sem_city:
				poi_current = ewcfg.coord_to_poi.get(step)

			# Standing on a node which is aliased (a part of the city).
			elif val == sem_city_alias:
				poi_current = ewcfg.coord_to_poi.get(ewcfg.alias_to_coord.get(step))

			user_data = EwUser(member = cmd.message.author)
			mutations = user_data.get_mutations()
			if poi_current != None:

				# If the player dies or enlists or whatever while moving, cancel the move.
				if user_data.life_state != life_state or faction != user_data.faction:
					try:
						await cmd.client.delete_message(msg_walk_start)
					except:
						pass

					return

				channel = cmd.message.channel

				# Prevent access to the zone if it's closed.
				if poi_current.closed == True:
					try:
						if poi_current.str_closed != None:
							message_closed = poi_current.str_closed
						else:
							message_closed = "The way into {} is blocked.".format(poi_current.str_name)

						# Send the message in the player's current if possible, else in the origin channel for the move.
						poi_current = ewcfg.id_to_poi.get(user_data.poi)
						for ch in cmd.message.server.channels:
							if ch.name == poi_current.channel:
								channel = ch
								break
					finally:
						return await ewutils.send_message(cmd.client, 
							channel,
							ewutils.formatMessage(
								cmd.message.author,
								message_closed
							)
						)

				# Send the message in the channel for this POI if possible, else in the origin channel for the move.
				for ch in cmd.message.server.channels:
					if ch.name == poi_current.channel:
						channel = ch
						break

				if user_data.poi != poi_current.id_poi:
					user_data.poi = poi_current.id_poi
					user_data.time_lastenter = int(time.time())
					user_data.persist()

					await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

					try:
						await cmd.client.delete_message(msg_walk_start)
					except:
						pass

					msg_walk_start = await ewutils.send_message(cmd.client, 
						channel,
						ewutils.formatMessage(
							cmd.message.author,
							"You {} {}.".format(poi_current.str_enter, poi_current.str_name)
						)
					)

					if len(user_data.faction) > 0 and user_data.poi in ewcfg.capturable_districts:
						district = EwDistrict(
							id_server = user_data.id_server,
							district = user_data.poi
						)

						if district != None and len(district.controlling_faction) > 0:
							if user_data.faction == district.controlling_faction:
								boost = ewcfg.territory_time_gain
							else:
								territory_slowdown = ewcfg.territory_time_gain
								if ewcfg.mutation_id_bigbones in mutations:
									territory_slowdown *= 2
								if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() > 0.9:
									territory_slowdown = int(territory_slowdown / 2)
								await asyncio.sleep(territory_slowdown)
			else:
				if val > 0:
					val_actual = val - boost
					boost = 0
					if ewcfg.mutation_id_bigbones in mutations:
					    val_actual *= 2
					if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() > 0.9:
					    val_actual = int(val_actual / 2)

					if val_actual > 0:
						await asyncio.sleep(val_actual)

		await asyncio.sleep(30)
		try:
			await cmd.client.delete_message(msg_walk_start)
		except:
			pass


"""
	Cancel any in progress move.
"""
async def halt(cmd):
	ewutils.moves_active[cmd.message.author.id] = 0
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You {} dead in your tracks.".format(cmd.cmd[1:])))


"""
	Dump out the visual description of the area you're in.
"""
async def look(cmd):
	user_data = EwUser(member = cmd.message.author)
	district_data = EwDistrict(district = user_data.poi, id_server = user_data.id_server)
	poi = ewcfg.id_to_poi.get(user_data.poi)

	# get information about slime levels in the district
	slimes = district_data.slimes
	slimes_resp = "\n\n"
	if slimes < 10000:
		slimes_resp += "There are a few specks of slime splattered across the city streets."
	elif slimes < 100000:
		slimes_resp += "There are sparse puddles of slime filling potholes in the cracked city streets."
	elif slimes < 1000000:
		slimes_resp += "There are good amounts of slime pooling around storm drains and craters in the rundown city streets."
	else:
		slimes_resp += "There are large heaps of slime shoveled into piles to clear the way for cars and pedestrians on the slime-soaked city streets."

	# don't show low level players
	min_level = math.ceil((1/10) ** 0.25 * user_data.slimelevel)

	life_states = [ewcfg.life_state_corpse, ewcfg.life_state_juvenile, ewcfg.life_state_enlisted]
	# get information about players in the district
	players_in_district = district_data.get_players_in_district(min_level = min_level, life_states = life_states)
	if user_data.id_user in players_in_district:
		players_in_district.remove(user_data.id_user)

	num_players = len(players_in_district)
	players_resp = "\n\n"
	if num_players == 1:
		players_resp += "You notice 1 suspicious figure in this location."
	else:
		players_resp += "You notice {} suspicious figures in this location.".format(num_players)

	# post result to channel
	if poi != None:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"You stand {} {}.\n\n{}{}{}".format(
				poi.str_in,
				poi.str_name,
				poi.str_desc,
				slimes_resp,
				players_resp,
				("\n\n{}".format(
					ewcmd.weather_txt(cmd.message.server.id)
				) if cmd.message.server != None else "")
			)
		))


"""
	Get information about an adjacent zone.
"""
async def scout(cmd):
	if channel_name_is_poi(cmd.message.channel.name) == False:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

	user_data = EwUser(member = cmd.message.author)
	user_poi = ewcfg.id_to_poi.get(user_data.poi)
	mutations = user_data.get_mutations()

	# if no arguments given, scout own location
	if not len(cmd.tokens) > 1:
		poi = user_poi
	else:
		target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
		poi = ewcfg.id_to_poi.get(target_name)


	if poi == None:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Never heard of it."))

	else:
		# if scouting own location, treat as a !look alias
		#if poi.id_poi == user_poi.id_poi:
		#	return await look(cmd)



		# check if district is in scouting range
		is_neighbor = user_poi.id_poi in ewcfg.poi_neighbors and poi.id_poi in ewcfg.poi_neighbors[user_poi.id_poi]
		is_current_transport_station = False
		if user_poi.is_transport:
			transport_data = EwTransport(id_server = user_data.id_server, poi = user_poi.id_poi)
			is_current_transport_station = transport_data.current_stop == poi.id_poi
		is_transport_at_station = False
		if poi.is_transport:
			transport_data = EwTransport(id_server = user_data.id_server, poi = poi.id_poi)
			is_transport_at_station = transport_data.current_stop == user_poi.id_poi
			
			
		#is_subzone = poi.is_subzone and poi.mother_district == user_poi.id_poi
		#is_mother_district = user_poi.is_subzone and user_poi.mother_district == poi.id_poi

		if (not is_neighbor) and (not is_current_transport_station) and (not is_transport_at_station) and (not poi.id_poi == user_poi.id_poi):
			response = "You can't scout that far."
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


		district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

		# don't show low level players
		min_level = math.ceil((1/10) ** 0.25 * user_data.slimelevel)

		life_states = [ewcfg.life_state_corpse, ewcfg.life_state_juvenile, ewcfg.life_state_enlisted]
		# get information about players in the district
		players_in_district = district_data.get_players_in_district(min_level = min_level, life_states = life_states)
		if user_data.id_user in players_in_district:
			players_in_district.remove(user_data.id_user)
	
		num_players = len(players_in_district)
		players_resp = "\n\n"
		if num_players == 1:
			players_resp += "You notice 1 suspicious figure in this location"
		else:
			players_resp += "You notice {} suspicious figures in this location".format(num_players)

		if ewcfg.mutation_id_keensmell in mutations:
			players_resp += ":"
			for player in players_in_district:
				scoutee_data = EwUser(id_user = player, id_server = user_data.id_server)
				players_resp += "\n" + scoutee_data.get_mention()
		else:
			players_resp += "."

		# post result to channel
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(
			cmd.message.author,
			"**{}**: {}".format(
				poi.str_name,
				players_resp
			)
		))

"""
	Kicks idle players from subzones. Called every 15 minutes.
"""
async def kick(id_server):
	# Gets data for all living players from the database
	all_living_players = ewutils.execute_sql_query("SELECT {poi}, {id_user} FROM users WHERE id_server = %s AND {life_state} > 0 AND {time_last_action} < %s".format(
		poi = ewcfg.col_poi,
		id_user = ewcfg.col_id_user,
		time_last_action = ewcfg.col_time_last_action,
		life_state = ewcfg.col_life_state
	), (
		id_server,
		(int(time.time()) - ewcfg.time_kickout)
	))

	client = ewutils.get_client()

	for player in all_living_players:
		try:
			poi = ewcfg.id_to_poi[player[0]]
			id_user = player[1]
			user_data = EwUser(id_user = id_user, id_server = id_server)

			# checks if the player should be kicked from the subzone and kicks them if they should.
			if poi.is_subzone and not inaccessible(user_data = user_data, poi = ewcfg.id_to_poi.get(poi.mother_district)):
				server = ewcfg.server_list[id_server]
				member_object = server.get_member(id_user)

				user_data.poi = poi.mother_district
				user_data.time_lastenter = int(time.time())
				user_data.persist()
				await ewrolemgr.updateRoles(client = client, member = member_object)

				mother_district_channel = ewutils.get_channel(server, ewcfg.id_to_poi[poi.mother_district].channel)
				response = "You have been kicked out for loitering! You can only stay in a sub-zone and twiddle your thumbs for 1 hour at a time."
				await ewutils.send_message(client, mother_district_channel, ewutils.formatMessage(member_object, response))
		except:
			ewutils.logMsg('failed to move inactive player out of subzone: {}'.format(id_user))
