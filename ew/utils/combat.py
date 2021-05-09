import math

from ..static import cfg as ewcfg
from ..static import weapons as static_weapons

from . import core as ewutils

from ..backend.item import EwItem


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
