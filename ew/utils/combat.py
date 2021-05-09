import math

from ..static import cfg as ewcfg
from ..static import weapons as static_weapons
from ..static import status as se_static

from . import core as ewutils

from ..backend.item import EwItem
from ..backend.status import EwStatusEffect, EwEnemyStatusEffect
from ..backend.user import EwUserBase as EwUser

def get_hitzone(injury_map = None):
	if injury_map == None:
		injury_map = ewcfg.injury_weights

	injury = ewutils.weightedChoice(injury_map)

	hitzone = se_static.hitzone_map.get(injury)

	return hitzone


# Returns the total modifier of all statuses of a certain type and target of a given player
def get_shooter_status_mods(user_data = None, shootee_data = None, hitzone = None):
	mods = {
		'dmg': 0,
		'crit': 0,
		'hit_chance': 0
	}

	user_statuses = user_data.getStatusEffects()

	for status in user_statuses:
		status_flavor = se_static.status_effects_def_map.get(status)

		# check target for targeted status effects
		if status in [ewcfg.status_taunted_id, ewcfg.status_aiming_id, ewcfg.status_evasive_id]:
			if user_data.combatant_type == "player":
				status_data = EwStatusEffect(id_status = status, user_data = user_data)
			else:
				status_data = EwEnemyStatusEffect(id_status = status, enemy_data = user_data)

			if status_data.id_target != -1:
				if status == ewcfg.status_taunted_id:
					if shootee_data.combatant_type == ewcfg.combatant_type_player and shootee_data.id_user == status_data.id_target:
						continue
					elif shootee_data.combatant_type == ewcfg.combatant_type_enemy and shootee_data.id_enemy == status_data.id_target:
						continue
				elif status == ewcfg.status_aiming_id:
					if shootee_data.combatant_type == ewcfg.combatant_type_player and shootee_data.id_user != status_data.id_target:
						continue
					elif shootee_data.combatant_type == ewcfg.combatant_type_enemy and shootee_data.id_enemy != status_data.id_target:
						continue

		if status_flavor is not None:
			if status == ewcfg.status_taunted_id:
				# taunting has decreased effectiveness the lower the taunter's level is compared to the tauntee
				taunter = EwUser(id_user=status_data.source, id_server=user_data.id_server)

				if taunter.slimelevel < user_data.slimelevel:
					mods['hit_chance'] += round(status_flavor.hit_chance_mod_self / (user_data.slimelevel / taunter.slimelevel), 2)
				else:
					mods['hit_chance'] += status_flavor.hit_chance_mod_self

			else:
				mods['hit_chance'] += status_flavor.hit_chance_mod_self
			mods['crit'] += status_flavor.crit_mod_self

			mods['dmg'] += status_flavor.dmg_mod_self

	return mods

# Returns the total modifier of all statuses of a certain type and target of a given player
def get_shootee_status_mods(user_data = None, shooter_data = None, hitzone = None):

	mods = {
		'dmg': 0,
		'crit': 0,
		'hit_chance': 0
	}

	user_statuses = user_data.getStatusEffects()
	for status in user_statuses:
		status_flavor = se_static.status_effects_def_map.get(status)

		# check target for targeted status effects
		if status in [ewcfg.status_evasive_id]:
			if user_data.combatant_type == "player":
				status_data = EwStatusEffect(id_status = status, user_data = user_data)
			else:
				status_data = EwEnemyStatusEffect(id_status = status, enemy_data = user_data)

			if status_data.id_target != -1:
				if shooter_data.id_user != status_data.id_target:
					continue

		if status_flavor is not None:

			mods['hit_chance'] += status_flavor.hit_chance_mod
			mods['crit'] += status_flavor.crit_mod
			mods['dmg'] += status_flavor.dmg_mod

	#apply trauma mods
	#if user_data.combatant_type == 'player':
	#	trauma = se_static.trauma_map.get(user_data.trauma)

	#	if trauma != None and trauma.trauma_class == ewcfg.trauma_class_accuracy:
	#		mods['miss'] -= 0.2 * user_data.degradation / 100

	return mods

def damage_mod_attack(user_data, market_data, user_mutations, district_data):
	damage_mod = 1

	# Weapon possession
	if user_data.get_possession('weapon'):
		damage_mod *= 1.2

	# Lone wolf
	if ewcfg.mutation_id_lonewolf in user_mutations:
		allies_in_district = district_data.get_players_in_district(
			min_level = math.ceil((1/10) ** 0.25 * user_data.slimelevel),
			life_states = [ewcfg.life_state_enlisted],
			factions = [user_data.faction]
		)
		if user_data.id_user in allies_in_district:
			allies_in_district.remove(user_data.id_user)

		if len(allies_in_district) == 0:
			damage_mod *= 1.5

	# Organic fursuit
	if ewcfg.mutation_id_organicfursuit in user_mutations and (
		ewutils.check_fursuit_active(market_data)
	):
		damage_mod *= 2

	# Social animal
	if ewcfg.mutation_id_socialanimal in user_mutations:
		allies_in_district = district_data.get_players_in_district(
			min_level = math.ceil((1/10) ** 0.25 * user_data.slimelevel),
			life_states = [ewcfg.life_state_enlisted],
			factions = [user_data.faction]
		)
		if user_data.id_user in allies_in_district:
			allies_in_district.remove(user_data.id_user)

		damage_mod *= 1 + 0.1 * len(allies_in_district)

	# Dressed to kill
	if ewcfg.mutation_id_dressedtokill in user_mutations:
		if user_data.freshness >= 250:
			damage_mod *= 1.5

	if ewcfg.mutation_id_2ndamendment in user_mutations:
		if user_data.weapon != -1 and user_data.sidearm != -1:
			weapon_item = EwItem(id_item=user_data.weapon)
			weapon_c = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
			sidearm_item = EwItem(id_item=user_data.sidearm)
			sidearm_c = static_weapons.weapon_map.get(sidearm_item.item_props.get("weapon_type"))
			if weapon_c.is_tool == 0 and sidearm_c.is_tool == 0:
				damage_mod *= 1.25

	return damage_mod

def damage_mod_defend(shootee_data, shootee_mutations, market_data, shootee_weapon):

	damage_mod = 1
	if ewcfg.mutation_id_organicfursuit in shootee_mutations and (
		ewutils.check_fursuit_active(market_data)
	):
		damage_mod *= 0.1

	# Fat chance
	if ewcfg.mutation_id_fatchance in shootee_mutations and shootee_data.hunger / shootee_data.get_hunger_max() > 0.5:
		damage_mod *= 0.75


	# defensive weapon
	if shootee_weapon != None:
		if ewcfg.weapon_class_defensive in shootee_weapon.classes:
			damage_mod *= 0.75

	return damage_mod


def damage_mod_cap(user_data, market_data, user_mutations, district_data, weapon):
	damage_mod = 1

	time_current = market_data.clock

	# Weapon possession
	if user_data.get_possession('weapon'):
		damage_mod *= 1.2

	if weapon.id_weapon == ewcfg.weapon_id_thinnerbomb:
		if user_data.faction == district_data.controlling_faction:
			slimes_damage = round(damage_mod * .1)
		else:
			damage_mod *= 2

	if ewcfg.mutation_id_patriot in user_mutations:
		damage_mod *= 1.5
	if ewcfg.mutation_id_unnaturalcharisma in user_mutations:
		damage_mod *= 1.2

	if 3 <= time_current <= 10:
		damage_mod *= 2

	return damage_mod


def get_sap_armor(shootee_data, sap_ignored):
	# apply hardened sap armor
	try:
		effective_hardened_sap = shootee_data.hardened_sap - sap_ignored + int(shootee_data.defense / 2)
	except: # If shootee_data doesn't have defense, aka it's a monster
		effective_hardened_sap = shootee_data.hardened_sap - sap_ignored
	level = 0

	if hasattr(shootee_data, "slimelevel"):
		level = shootee_data.slimelevel
	elif hasattr(shootee_data, "level"):
		level = shootee_data.level

	if effective_hardened_sap >= 0:
		sap_armor = 10 / (10 + effective_hardened_sap)
	else:
		sap_armor = (10 + abs(effective_hardened_sap)) / 10
	return sap_armor

def get_fashion_armor(shootee_data):
	effective_armor = int(shootee_data.defense / 2)

	if effective_armor >= 0:
		return 10 / (10 + effective_armor)
	else:
		return (10 + abs(effective_armor)) / 10
