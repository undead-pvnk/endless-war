import math
import time
import random

import ewutils
import ewcfg

from ew import EwUser


class EwFrogEnvironment:
	id_server = ""

	slime_viscosity = 0
	vegetation = 0
	sludge = 0

	
class EwFrogFood:
	id_server = ""

	id_faction = ""
	food_type = ""

	amount = 0


class EwFrogFaction:
	
	id_server = ""
	id_user = ""
	id_faction = ""

	faction_name = ""

	size = 0
	speed = 0
	stealth = 0
	perception = 0
	dexterity = 0
	constitution = 0
	intelligence = 0

	diet = 0
	respawn_rate = 0
	sludge = 0

	defense_strategy = 0

	population = 0
	evolution_points = 0
	technology_points = 0

class EwFactionEvolution:
	id_faction = ""
	id_evolution = ""

class EwFrogEvolution:

	id_evolution = ""

	prereq = []

	unlocks = []

def ff_get_factions(id_server):
	factions = []
	return factions

def ff_get_evolutions(id_faction):
	evolutions = []
	return evolutions

def ff_choose_target(faction_data, targets):
	target = None
	potential_gain = 0
	for tar in targets:
		target_data = EwFrogFaction(id_faction = tar)

		gain_mod = 1
		size_mod = faction_data.size / target_data.size
		stealth_mod = faction_data.perception / target_data.stealth
		speed_mod = faction_data.speed / target_data.speed


	return target

async def ff_tick(id_server):
	env_data = EwFrogEnvironment(id_server = id_server)
	factions = ff_get_factions(id_server)
	response = ""
	client = ewutils.get_client()
	server = ewcfg.server_list.get(id_server)
	channel = ewutils.get_channel(server = server, channel_name = ewcfg.channel_frogfactions)

	random.shuffle(factions)
	total_biomass_lost = 0


	for faction in factions:
		# eat
		faction_data = EwFrogFaction(id_faction = faction)
		eat_meat = False
		targets = random.sample(factions, min(faction_data.perception, len(factions)))

		for tar in targets:
			if tar == faction:
				targets.remove(tar)
				continue
			target_data = EwFrogFaction(id_faction = tar)
			if abs(target_data.size - faction_data.size) > 2:
				targets.remove(tar)

		if faction_data.diet == ewcfg.ff_diet_herbivore:
			eat_meat = False
		elif faction_data.diet == ewcfg.ff_diet_carnivore:
			eat_meat = True
		else:
			if random.random() < 0.5:
				eat_meat = True
			else:
				eat_meat = False
		
		if eat_meat:
			if len(targets) > 0:
				target = random.choice(targets)
				target_data = EwFrogFaction(id_faction = target)
				response += "{} preyed on {}.\n".format(faction_data.faction_name, target_data.faction_name)
			else:
				target = faction
				target_data = faction_data
				response += "{} couldn't find any prey, so they cannibalized themselves.\n".format(faction_data.faction_name)




			defense_mod = 0
			defense_strategy = None

			stealth_mod = target_data.stealth + int(env_data.vegetation/10) - 5 - faction_data.perception
			chase_mod = target_data.speed - env_data.slime_viscosity + 5 - faction_data.speed
			ambush_mod = target_data.perception - int(env_data.vegetation/10) + 5 - faction_data.stealth
			combat_mod = 1


			strategies = []
			if target_data.intelligence < 1 or target == faction:
				strategies = [ewcfg.ff_strategy_fight]
			elif target_data.intelligence < 3:
				strategies = [ewcfg.ff_strategy_fight, ewcfg.ff_strategy_run]
			elif target_data.intelligence < 5:
				strategies = [ewcfg.ff_strategy_fight, ewcfg.ff_strategy_run, ewcfg.ff_strategy_hide]
			elif target_data.intelligence < 7:
				best_stat = max(target_data.speed, target_data.stealth, target_data.perception, target_data.size+1)
				if target_data.speed == best_stat:
					strategies.append(ewcfg.ff_strategy_run)
				if target_data.stealth == best_stat:
					strategies.append(ewcfg.ff_strategy_hide)
				if target_data.perception == best_stat or target_data.size+1 == best_stat:
					strategies.append(ewcfg.ff_strategy_fight)

			else:
				best_matchup = max(
					stealth_mod,
					chase_mod,
					ambush_mod,
					combat_mod
				)
				if chase_mod == best_matchup:
					strategies.append(ewcfg.ff_strategy_run)
				if stealth_mod == best_matchup:
					strategies.append(ewcfg.ff_strategy_hide)
				if ambush_mod == best_matchup or combat_mod == best_matchup:
					strategies.append(ewcfg.ff_strategy_fight)


			defense_strategy = random.choice(strategies)

			if defense_strategy == ewcfg.ff_strategy_hide:
				hide = random.randrange(target_data.stealth + int(env_data.vegetation/10) - 5 )
				seek = random.randrange(faction_data.perception)
				defense_mod = seek - hide
				if defense_mod < 0:
					response += "{} hid from their attackers.\n".format(target_data.faction_name)
				else:
					response += "{} tried to conceal themselves from their attackers, but were discovered.\n".format(target_data.faction_name)
			elif defense_strategy == ewcfg.ff_strategy_run:
				run = random.randrange(target_data.speed - env_data.slime_viscosity + 5)
				chase = random.randrange(faction_data.speed)
				defense_mod = chase - run
				if defense_mod < 0:
					response += "{} ran from their attackers.\n".format(target_data.faction_name)
				else:
					response += "{} tried to flee from their attackers, but were chased down.\n".format(target_data.faction_name)
		
			elif defense_strategy == ewcfg.ff_strategy_fight:
				ambush = False
				if faction_data.intelligence < 5:
					ambush = False
				elif faction_data.intelligence < 7:
					if faction_data.stealth > faction_data.size:
						ambush = True
				else:
					if ambush_mod < 0:
						ambush = True

				if target == faction:
					defense_mod = 0
				elif ambush:
					ambush = random.randrange(faction_data.stealth + int(env_data.vegetation/10) - 5)
					awareness = random.randrange(target_data.perception)
					defense_mod = ambush - awareness - combat_mod
					if defense_mod < -combat_mod:
						response += "{} ambushed their prey.\n".format(faction_data.faction_name)
					else:
						response += "{} tried to sneak up on their prey, but were noticed.\n".format(faction_data.faction_name)
				else:
					defense_mod = 0


			attack = random.randrange(faction_data.size)
			defense = random.randrange(max(target_data.size - defense_mod, 1))
			result = 0.5 + (attack - defense) / 10
			result = max(0, min(result, 1))

			attacker_losses = 0.01 * (1 - result) * target_data.population
			defender_losses = 0.01 * result * faction_data.population * faction_data.size / target_data.size

			faction_data.population -= attacker_losses
			target_data.population -= defender_losses

			ev_points_gain = 10 * defender_losses * target_data.size

			faction_data.evolution_points += ev_points_gain

			sludge_damage = random.randrange(target_data.sludge)
			sludge_resistance = random.randrange(faction_data.constitution)
			sludge_losses = 0.1 * max(0, sludge_damage - sludge_resistance) * defender_losses * target_data.size

			faction_data.population -= sludge_losses

			total_biomass_lost += (attacker_losses + sludge_losses) * faction_data.size
			total_biomass_lost += 0.5 * defender_losses * target_data.size

			target_data.persist()
			if target == faction:
				response += "{} lost {} frogs from eating their own kind.\n".format(faction_data.faction_name)
			else:
				if defender_losses > 0:
					response += "{} lost {} frogs in the attack.\n".format(target_data.faction_name, defender_losses)
					response += "{} gained {} Evolution Points.\n".format(faction_data.faction_name, ev_points_gain)
				if attacker_losses > 0:
					response += "{} lost {} frogs in the fighting.\n".format(faction_data.faction_name, attacker_losses)
				if sludge_losses > 0:
					response += "{} lost {} frogs to sludge poisoning.\n".format(faction_data.faction_name, sludge_losses)

		else:
			vegetation_eaten = 0.01 * faction_data.population * faction_data.size
			vegetation_eaten = min(vegetation_eaten, 0.5 * env_data.vegetation)

			env_data.vegetation -= vegetation_eaten
			
			ev_points_gain = vegetation_eaten

			faction_data.evolution_points += ev_points_gain

			sludge_damage = random.randrange(env_data.sludge)
			sludge_resistance = random.randrange(faction_data.constitution)
			sludge_losses = 0.1 * max(0, sludge_damage - sludge_resistance) * vegetation_eaten

			faction_data.population -= sludge_losses

			total_biomass_lost += sludge_losses * faction_data.size

			response += "{} gained {} Evolution Points by eating plants.\n".format(faction_data.faction_name, ev_points_gain)
			if sludge_losses > 0:
				response += "{} lost {} frogs to sludge poisoning.\n".format(faction_data.faction_name, sludge_losses)

		faction_data.persist()
		env_data.persist()

		# reproduce

		respawn = int(faction_data.population * faction_data.respawn_rate / 100)

		faction_data.population += respawn
		faction_data.persist()

		response += "{} produced {} new frogs.\n".format(faction_data.faction_name, respawn)

		if len(response) > 1500:
			await ewutils.send_message(client, channel, response)
			response = ""

	if len(response) > 0:
		await ewutils.send_message(client, channel, response)



	env_data.vegetation += int(env_data.vegetation * 0.1)
	env_data.vegetation += total_biomass_lost
	env_data.persist()

	
	
