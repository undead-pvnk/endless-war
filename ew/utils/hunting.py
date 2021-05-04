
from ..static import cfg as ewcfg

from ..backend import core as bknd_core

from .. import hunting as ewhunting

from . import core as ewutils

from ..backend.user import EwUser
from ..backend.hunting import EwEnemy

# Clears out id_target in enemies with defender ai. Primarily used for when players die or leave districts the defender is in.
def check_defender_targets(user_data, enemy_data):
	defending_enemy = EwEnemy(id_enemy=enemy_data.id_enemy)
	searched_user = EwUser(id_user=user_data.id_user, id_server=user_data.id_server)

	if (defending_enemy.poi != searched_user.poi) or (searched_user.life_state == ewcfg.life_state_corpse):
		defending_enemy.id_target = 0
		defending_enemy.persist()
		return False
	else:
		return True

def gvs_create_gaia_grid_mapping(user_data):
	grid_map = {}

	# Grid print mapping and shambler targeting use different priority lists. Don't get these mixed up
	printgrid_low_priority = [ewcfg.enemy_type_gaia_rustealeaves]
	printgrid_mid_priority = [ewcfg.enemy_type_gaia_steelbeans]
	printgrid_high_priority = []
	for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
		if enemy_id not in printgrid_low_priority and enemy_id not in printgrid_mid_priority:
			printgrid_high_priority.append(enemy_id)

	gaias = bknd_core.execute_sql_query(
		"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1 AND {enemyclass} = %s".format(
			id_enemy=ewcfg.col_id_enemy,
			enemytype=ewcfg.col_enemy_type,
			poi=ewcfg.col_enemy_poi,
			life_state=ewcfg.col_enemy_life_state,
			gvs_coord=ewcfg.col_enemy_gvs_coord,
			enemyclass=ewcfg.col_enemy_class,
		), (
			user_data.id_server,
			user_data.poi,
			ewcfg.enemy_class_gaiaslimeoid
		))
	
	grid_conditions = bknd_core.execute_sql_query(
		"SELECT coord, grid_condition FROM gvs_grid_conditions WHERE district = %s".format(
		), (
			user_data.poi,
		))
	
	for condition in grid_conditions:
		grid_map[condition[0]] = condition[1]
	
	for gaia in gaias:
		try:
			gaia_in_coord = grid_map[gaia[2]]
			# No key error: Gaia is in coord already, check for priority
			is_filled = True
		except KeyError:
			gaia_in_coord = ''
			# Key error: Gaia was not in coord
			is_filled = False
			
		if is_filled:
			if gaia_in_coord in printgrid_low_priority and (gaia[1] in printgrid_mid_priority or gaia[1] in printgrid_high_priority):
				grid_map[gaia[2]] = gaia[1]
			if gaia_in_coord in printgrid_mid_priority and gaia[1] in printgrid_high_priority:
				grid_map[gaia[2]] = gaia[1]
		else:
			grid_map[gaia[2]] = gaia[1]
		
	return grid_map


def gvs_create_gaia_lane_mapping(user_data, row_used):

	# Grid print mapping and shambler targeting use different priority lists. Don't get these mixed up
	printlane_low_priority = [ewcfg.enemy_type_gaia_rustealeaves]
	printlane_mid_priority = []
	printlane_high_priority = [ewcfg.enemy_type_gaia_steelbeans]
	for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
		if enemy_id not in printlane_low_priority and enemy_id not in printlane_high_priority:
			printlane_mid_priority.append(enemy_id)

	gaias = bknd_core.execute_sql_query(
		"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} IN %s".format(
			id_enemy=ewcfg.col_id_enemy,
			enemytype=ewcfg.col_enemy_type,
			poi=ewcfg.col_enemy_poi,
			life_state=ewcfg.col_enemy_life_state,
			gvs_coord=ewcfg.col_enemy_gvs_coord,
			enemyclass=ewcfg.col_enemy_class,
		), (
			user_data.id_server,
			user_data.poi,
			ewcfg.enemy_class_gaiaslimeoid,
			tuple(row_used)
		))

	grid_conditions = bknd_core.execute_sql_query(
		"SELECT coord, grid_condition FROM gvs_grid_conditions WHERE district = %s AND coord IN %s".format(
		), (
			user_data.poi,
			tuple(row_used)
		))
	
	coord_sets = []

	for coord in row_used:
		current_coord_set = [] 
		for enemy in printlane_low_priority:
			for gaia in gaias:
				if gaia[1] == enemy and gaia[2] == coord:
					current_coord_set.append(gaia[0])
					
		for enemy in printlane_mid_priority:
			for gaia in gaias:
				if gaia[1] == enemy and gaia[2] == coord:
					current_coord_set.append(gaia[0])
					
		for enemy in printlane_high_priority:
			for gaia in gaias:
				if gaia[1] == enemy and gaia[2] == coord:
					current_coord_set.append(gaia[0])
					
		for condition in grid_conditions:
			if condition[0] == coord:
				if condition[1] == 'frozen':
					current_coord_set.append('frozen')
					
		coord_sets.append(current_coord_set)
	

	return coord_sets


def gvs_check_gaia_protected(enemy_data):
	is_protected = False
	
	low_attack_priority = [ewcfg.enemy_type_gaia_rustealeaves]
	high_attack_priority = [ewcfg.enemy_type_gaia_steelbeans]
	mid_attack_priority = []
	for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
		if enemy_id not in low_attack_priority and enemy_id not in high_attack_priority:
			mid_attack_priority.append(enemy_id)
	
	checked_coords = []
	enemy_coord = enemy_data.gvs_coord
	for row in ewcfg.gvs_valid_coords_gaia:
		if enemy_coord in row:
			index = row.index(enemy_coord)
			row_length = len(ewcfg.gvs_valid_coords_gaia)
			for i in range(index+1, row_length):
				checked_coords.append(ewcfg.gvs_valid_coords_gaia[i])
				
	gaias_in_front_coords = bknd_core.execute_sql_query(
		"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} IN %s".format(
			id_enemy=ewcfg.col_id_enemy,
			enemytype=ewcfg.col_enemy_type,
			life_state=ewcfg.col_enemy_life_state,
			gvs_coord=ewcfg.col_enemy_gvs_coord,
			enemyclass=ewcfg.col_enemy_class,
		), (
			ewcfg.enemy_class_gaiaslimeoid,
			tuple(checked_coords)
		))
	
	if len(gaias_in_front_coords) > 0:
		is_protected = True
	else:
		gaias_in_same_coord = bknd_core.execute_sql_query(
			"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} = %s".format(
				id_enemy=ewcfg.col_id_enemy,
				enemytype=ewcfg.col_enemy_type,
				life_state=ewcfg.col_enemy_life_state,
				gvs_coord=ewcfg.col_enemy_gvs_coord,
				enemyclass=ewcfg.col_enemy_class,
			), (
				ewcfg.enemy_class_gaiaslimeoid,
				enemy_coord
			))
		if len(gaias_in_same_coord) > 1:
			same_coord_gaias_types = []
			for gaia in gaias_in_same_coord:
				same_coord_gaias_types.append(gaia[1])
				
			for type in same_coord_gaias_types:
				if enemy_data.enemy_type in high_attack_priority:
					is_protected = False
					break
				elif enemy_data.enemy_type in mid_attack_priority and type in high_attack_priority:
					is_protected = True
					break
				elif enemy_data.enemy_type in low_attack_priority and (type in mid_attack_priority or type in high_attack_priority):
					is_protected = True
					break
	
		else:
			is_protected = False
	
	return is_protected

def gvs_check_operation_duplicate(id_user, district, enemytype, faction):
	entry = None
	
	if faction == ewcfg.psuedo_faction_gankers:
		entry = bknd_core.execute_sql_query(
			"SELECT * FROM gvs_ops_choices WHERE id_user = %s AND district = %s AND enemytype = %s AND faction = %s".format(
			), (
				id_user, 
				district, 
				enemytype, 
				faction
			))
	elif faction == ewcfg.psuedo_faction_shamblers:
		entry = bknd_core.execute_sql_query(
			"SELECT * FROM gvs_ops_choices WHERE district = %s AND enemytype = %s AND faction = %s".format(
			), (
				district,
				enemytype,
				faction
			))

	if len(entry) > 0:
		return True
	else:
		return False
	
def gvs_check_operation_limit(id_user, district, enemytype, faction):
	
	limit_hit = False
	tombstone_limit = 0
	
	if faction == ewcfg.psuedo_faction_gankers:
		data = bknd_core.execute_sql_query(
			"SELECT id_user FROM gvs_ops_choices WHERE id_user = %s AND district = %s AND faction = %s".format(
			), (
				id_user, 
				district,
				faction
			))
		
		if len(data) >= 6:
			limit_hit = True
		else:
			limit_hit = False
		
	elif faction == ewcfg.psuedo_faction_shamblers:
		sh_data = bknd_core.execute_sql_query(
			"SELECT enemytype FROM gvs_ops_choices WHERE district = %s AND faction = %s".format(
			), (
				district,
				faction
			))
		
		gg_data = bknd_core.execute_sql_query(
			"SELECT id_user FROM gvs_ops_choices WHERE district = %s AND faction = %s".format(
			), (
				district,
				enemytype,
			))
		
		gg_id_list = []
		for gg in gg_data:
			gg_id_list.append(gg[0])
			
		gg_id_set = set(gg_id_list) # Remove duplicate user IDs
		
		if len(gg_id_set) == 0:
			tombstone_limit = 3
		elif len(gg_id_set) <= 3:
			tombstone_limit = 6
		elif len(gg_id_set) <= 6:
			tombstone_limit = 10
		else:
			tombstone_limit = 12
		
		if len(sh_data) >= tombstone_limit:
			limit_hit = True
		else:
			limit_hit = False
			
	return limit_hit, tombstone_limit

def gvs_check_if_in_operation(user_data):
	
	op_data = bknd_core.execute_sql_query(
		"SELECT id_user, district FROM gvs_ops_choices WHERE id_user = %s".format(
		), (
			user_data.id_user,
		))

	if len(op_data) > 0:
		return True, op_data[0][1]
	else:
		return False, None

def gvs_get_gaias_from_coord(poi, checked_coord):
	gaias = bknd_core.execute_sql_query(
		"SELECT id_enemy, enemytype FROM enemies WHERE poi = %s AND gvs_coord = %s".format(
		), (
			poi,
			checked_coord
		))
	
	gaias_id_to_type_map = {}
	
	for gaia in gaias:
		if gaia[1] in ewcfg.gvs_enemies_gaiaslimeoids:
			gaias_id_to_type_map[gaia[0]] = gaia[1]
	
	return gaias_id_to_type_map

# If there are no player operations, spawn in ones that the bot uses
def gvs_insert_bot_ops(id_server, district, enemyfaction):
	bot_id = 56709
	
	if enemyfaction == ewcfg.psuedo_faction_gankers:
		possible_bot_types = [
			ewcfg.enemy_type_gaia_pinkrowddishes,
			ewcfg.enemy_type_gaia_purplekilliflower,
			ewcfg.enemy_type_gaia_poketubers,
			ewcfg.enemy_type_gaia_razornuts
		]
		for type in possible_bot_types:
			bknd_core.execute_sql_query("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_user,
				ewcfg.col_district,
				ewcfg.col_enemy_type,
				ewcfg.col_faction,
				ewcfg.col_id_item,
				ewcfg.col_shambler_stock,
			), (
				bot_id,
				district,
				type,
				enemyfaction,
				-1,
				0,
			))
			
			# To increase the challenge, a column of suganmanuts is placed down.
			for coord in ['A6', 'B6', 'C6', 'D6', 'E6']:
				ewhunting.spawn_enemy(
					id_server=id_server,
					pre_chosen_type=ewcfg.enemy_type_gaia_suganmanuts,
					pre_chosen_level=50,
					pre_chosen_poi=district,
					pre_chosen_identifier='',
					pre_chosen_faction=ewcfg.psuedo_faction_gankers,
					pre_chosen_owner=bot_id,
					pre_chosen_coord=coord,
					manual_spawn=True,
				)
		
	elif enemyfaction == ewcfg.psuedo_faction_shamblers:
		possible_bot_types = [
			ewcfg.enemy_type_defaultshambler,
			ewcfg.enemy_type_bucketshambler,
		]
		for type in possible_bot_types:
			bknd_core.execute_sql_query("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_user,
				ewcfg.col_district,
				ewcfg.col_enemy_type,
				ewcfg.col_faction,
				ewcfg.col_id_item,
				ewcfg.col_shambler_stock,
			), (
				bot_id,
				district,
				type,
				enemyfaction,
				-1,
				20,
			))
			
