import random
import math
import time
import asyncio

from ..static import cfg as ewcfg
from ..static import poi as poi_static
from ..static import items as static_items
from ..static import food as static_food
from ..static import cosmetics as static_cosmetics
from ..static import weapons as static_weapons
from ..static import hunting as hunt_static
from ..static import slimeoid as sl_static
from ..static import status as se_static

from ..backend import core as bknd_core
from ..backend import item as bknd_item
from ..backend import hunting as bknd_hunt

from . import core as ewutils
from . import item as itm_utils
from . import frontend as fe_utils
from . import rolemgr as ewrolemgr
from . import combat as cmbt_utils

from .. import wep as ewwep

from ..model.hunting import EwEnemyEffectContainer
from .user import EwUser
from .district import EwDistrict
from .frontend import EwResponseContainer
from ..backend.hunting import EwEnemyBase, EwOperationData
from ..backend.market import EwMarket
from ..backend.item import EwItem
from ..backend.player import EwPlayer
from ..backend.slimeoid import EwSlimeoidBase as EwSlimeoid
from ..backend.status import EwEnemyStatusEffect

""" Enemy data model for database persistence """


class EwEnemy(EwEnemyBase):
	# Function that enemies use to attack or otherwise interact with players.
	async def kill(self):

		client = ewutils.get_client()

		last_messages = []
		should_post_resp_cont = True

		enemy_data = self

		time_now = int(time.time())
		resp_cont = EwResponseContainer(id_server=enemy_data.id_server)
		district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)
		market_data = EwMarket(id_server=enemy_data.id_server)
		ch_name = poi_static.id_to_poi.get(enemy_data.poi).channel

		target_data = None
		target_player = None
		target_slimeoid = None

		used_attacktype = None

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			users = bknd_core.execute_sql_query(
				"SELECT {id_user}, {life_state} FROM users WHERE {poi} = %s AND {id_server} = %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin})".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				if random.randrange(100) > 95:
					response = random.choice(ewcfg.coward_responses)
					response = response.format(enemy_data.display_name, enemy_data.display_name)
					resp_cont.add_channel_response(ch_name, response)
					resp_cont.format_channel_response(ch_name, enemy_data)
					return resp_cont

		if enemy_data.ai == ewcfg.enemy_ai_sandbag:
			target_data = None
		else:
			target_data, group_attack = get_target_by_ai(enemy_data)

		if bknd_hunt.check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
			# Raid boss has activated!
			response = "*The ground quakes beneath your feet as slime begins to pool into one hulking, solidified mass...*" \
					   "\n{} **{} has arrived! It's level {} and has {} slime!** {}\n".format(
				ewcfg.emote_megaslime,
				enemy_data.display_name,
				enemy_data.level,
				enemy_data.slimes,
				ewcfg.emote_megaslime
			)
			resp_cont.add_channel_response(ch_name, response)

			enemy_data.life_state = ewcfg.enemy_lifestate_alive
			enemy_data.time_lastenter = time_now
			enemy_data.persist()

			target_data = None

		elif bknd_hunt.check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_alive:
			# Raid boss attacks.
			pass

		# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
		elif bknd_hunt.check_raidboss_countdown(enemy_data) == False:

			target_data = None

			timer = (enemy_data.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

			if timer < ewcfg.enemy_attack_tick_length and timer != 0:
				timer = ewcfg.enemy_attack_tick_length

			countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
			resp_cont.add_channel_response(ch_name, countdown_response)

			# TODO: Edit the countdown message instead of deleting and reposting
			last_messages = await resp_cont.post()
			asyncio.ensure_future(fe_utils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))

			# Don't post resp_cont a second time while the countdown is going on.
			should_post_resp_cont = False

		if enemy_data.attacktype != ewcfg.enemy_attacktype_unarmed:
			used_attacktype = hunt_static.attack_type_map.get(enemy_data.attacktype)
		else:
			return

		if target_data != None:

			target_player = EwPlayer(id_user=target_data.id_user)
			target_slimeoid = EwSlimeoid(id_user=target_data.id_user)

			target_weapon = None
			target_weapon_item = None
			if target_data.weapon >= 0:
				target_weapon_item = EwItem(id_item=target_data.weapon)
				target_weapon = static_weapons.weapon_map.get(target_weapon_item.item_props.get("weapon_type"))

			server = client.get_guild(target_data.id_server)
			# server = discord.guild(id=target_data.id_server)
			# print(target_data.id_server)
			# channel = discord.utils.get(server.channels, name=ch_name)

			# print(server)

			# member = discord.utils.get(channel.guild.members, name=target_player.display_name)
			# print(member)

			target_mutations = target_data.get_mutations()

			miss = False
			crit = False
			strikes = 0
			# sap_damage = 0
			# sap_ignored = 0
			hit_chance_mod = 0
			crit_mod = 0
			dmg_mod = 0

			# Weaponized flavor text.
			# randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]
			hitzone = ewwep.get_hitzone()
			randombodypart = hitzone.name
			if random.random() < 0.5:
				randombodypart = random.choice(hitzone.aliases)

			shooter_status_mods = ewwep.get_shooter_status_mods(enemy_data, target_data, hitzone)
			shootee_status_mods = ewwep.get_shootee_status_mods(target_data, enemy_data, hitzone)

			hit_chance_mod += round(shooter_status_mods['hit_chance'] + shootee_status_mods['hit_chance'], 2)
			crit_mod += round(shooter_status_mods['crit'] + shootee_status_mods['crit'], 2)
			dmg_mod += round(shooter_status_mods['dmg'] + shootee_status_mods['dmg'], 2)

			# maybe enemies COULD have weapon skills? could punishes players who die to the same enemy without mining up beforehand
			# slimes_damage = int((slimes_spent * 4) * (100 + (user_data.weaponskill * 10)) / 100.0)

			# since enemies dont use up slime or hunger, this is only used for damage calculation
			slimes_spent = int(ewutils.slime_bylevel(enemy_data.level) / 40 * ewcfg.enemy_attack_tick_length / 2)

			slimes_damage = int(slimes_spent * 4)

			if used_attacktype == ewcfg.enemy_attacktype_body:
				slimes_damage /= 2  # specific to juvies
			if enemy_data.enemytype == ewcfg.enemy_type_microslime:
				slimes_damage *= 20  # specific to microslime

			if enemy_data.weathertype == ewcfg.enemy_weathertype_rainresist:
				slimes_damage *= 1.5

			slimes_damage += int(slimes_damage * dmg_mod)

			# slimes_dropped = target_data.totaldamage + target_data.slimes

			target_iskillers = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_killers
			target_isrowdys = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_rowdys
			target_isslimecorp = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_slimecorp
			target_isexecutive = target_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
			target_isjuvie = target_data.life_state == ewcfg.life_state_juvenile
			target_isnotdead = target_data.life_state != ewcfg.life_state_corpse
			target_isshambler = target_data.life_state == ewcfg.life_state_shambler

			if target_data.life_state == ewcfg.life_state_kingpin:
				# Disallow killing generals.
				response = "The {} tries to attack the kingpin, but is taken aback by the sheer girth of their slime.".format(
					enemy_data.display_name)
				resp_cont.add_channel_response(ch_name, response)

			elif (time_now - target_data.time_lastrevive) < ewcfg.invuln_onrevive:
				# User is currently invulnerable.
				response = "The {} tries to attack {}, but they have died too recently and are immune.".format(
					enemy_data.display_name,
					target_player.display_name)
				resp_cont.add_channel_response(ch_name, response)

			# enemies dont fuck with ghosts, ghosts dont fuck with enemies.
			elif (
					target_iskillers or target_isrowdys or target_isjuvie or target_isexecutive or target_isshambler or target_isslimecorp) and (
			target_isnotdead):
				was_killed = False
				was_hurt = False

				if target_data.life_state in [ewcfg.life_state_shambler, ewcfg.life_state_enlisted,
											  ewcfg.life_state_juvenile, ewcfg.life_state_lucky,
											  ewcfg.life_state_executive]:

					# If a target is being attacked by an enemy with the defender ai, check to make sure it can be hit.
					if (enemy_data.ai == ewcfg.enemy_ai_defender) and (
							check_defender_targets(target_data, enemy_data) == False):
						return
					else:
						# Target can be hurt by enemies.
						was_hurt = True

				if was_hurt:
					# Attacking-type-specific adjustments
					if used_attacktype != ewcfg.enemy_attacktype_unarmed and used_attacktype.fn_effect != None:
						# Build effect container
						ctn = EwEnemyEffectContainer(
							miss=miss,
							crit=crit,
							slimes_damage=slimes_damage,
							enemy_data=enemy_data,
							target_data=target_data,
							# sap_damage=sap_damage,
							# sap_ignored=sap_ignored,
							hit_chance_mod=hit_chance_mod,
							crit_mod=crit_mod
						)

						# Make adjustments
						used_attacktype.fn_effect(ctn)

						# Apply effects for non-reference values
						miss = ctn.miss
						crit = ctn.crit
						slimes_damage = ctn.slimes_damage
						strikes = ctn.strikes
					# sap_damage = ctn.sap_damage
					# sap_ignored = ctn.sap_ignored

					# can't hit lucky lucy
					if target_data.life_state == ewcfg.life_state_lucky:
						miss = True

					if miss:
						slimes_damage = 0
						# sap_damage = 0
						crit = False

					# if crit:
					#	sap_damage += 1

					enemy_data.persist()
					target_data = EwUser(id_user=target_data.id_user, id_server=target_data.id_server, data_level=1)

					# apply defensive mods
					slimes_damage *= cmbt_utils.damage_mod_defend(
						shootee_data=target_data,
						shootee_mutations=target_mutations,
						shootee_weapon=target_weapon,
						market_data=market_data
					)

					# if target_weapon != None:
					#	if sap_damage > 0 and ewcfg.weapon_class_defensive in target_weapon.classes:
					#		sap_damage -= 1

					# apply hardened sap armor
					# sap_armor = ewwep.get_sap_armor(shootee_data = target_data, sap_ignored = sap_ignored)
					# slimes_damage *= sap_armor
					# slimes_damage = int(max(slimes_damage, 0))

					# sap_damage = min(sap_damage, target_data.hardened_sap)

					# injury_severity = ewwep.get_injury_severity(target_data, slimes_damage, crit)

					if slimes_damage >= target_data.slimes - target_data.bleed_storage:
						was_killed = True
						slimes_damage = max(target_data.slimes - target_data.bleed_storage, 0)

					sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=enemy_data.id_server)

					# move around slime as a result of the shot
					if target_isjuvie:
						slimes_drained = int(3 * slimes_damage / 4)  # 3/4
					else:
						slimes_drained = 0

					damage = slimes_damage

					slimes_tobleed = int((slimes_damage - slimes_drained) / 2)
					# if ewcfg.mutation_id_bleedingheart in target_mutations:
					#	slimes_tobleed *= 2

					slimes_directdamage = slimes_damage - slimes_tobleed
					slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained

					# Damage victim's wardrobe (heh, WARdrobe... get it??)
					victim_cosmetics = bknd_item.inventory(
						id_user=target_data.id_user,
						id_server=target_data.id_server,
						item_type_filter=ewcfg.it_cosmetic
					)

					onbreak_responses = []

					# the following code handles cosmetic durability loss

					# for cosmetic in victim_cosmetics:
					# 	if not int(cosmetic.get('soulbound')) == 1:
					# 		c = EwItem(cosmetic.get('id_item'))
					#
					# 		# Damage it if the cosmetic is adorned and it has a durability limit
					# 		if c.item_props.get("adorned") == 'true' and c.item_props['durability'] is not None:
					#
					# 			#print("{} current durability: {}:".format(c.item_props.get("cosmetic_name"), c.item_props['durability']))
					#
					# 			durability_afterhit = int(c.item_props['durability']) - slimes_damage
					#
					# 			#print("{} durability after next hit: {}:".format(c.item_props.get("cosmetic_name"), durability_afterhit))
					#
					# 			if durability_afterhit <= 0:  # If it breaks
					# 				c.item_props['durability'] = durability_afterhit
					# 				c.persist()
					#
					#
					# 				target_data.persist()
					#
					# 				onbreak_responses.append(
					# 					str(c.item_props['str_onbreak']).format(c.item_props['cosmetic_name']))
					#
					# 				ewitem.item_delete(id_item = c.id_item)
					#
					# 			else:
					# 				c.item_props['durability'] = durability_afterhit
					# 				c.persist()
					#
					# 		else:
					# 			pass

					market_data.splattered_slimes += slimes_damage
					market_data.persist()
					district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
					target_data.bleed_storage += slimes_tobleed
					target_data.change_slimes(n=-slimes_directdamage, source=ewcfg.source_damage)
					target_data.time_lasthit = int(time_now)

					# target_data.hardened_sap -= sap_damage
					sewer_data.change_slimes(n=slimes_drained)

					if was_killed:

						# Dedorn player cosmetics
						# ewitem.item_dedorn_cosmetics(id_server=target_data.id_server, id_user=target_data.id_user)
						# Drop all items into district
						# bknd_item.item_dropall(target_data)

						# Give a bonus to the player's weapon skill for killing a stronger player.
						# if target_data.slimelevel >= user_data.slimelevel and weapon is not None:
						# enemy_data.add_weaponskill(n = 1, weapon_type = weapon.id_weapon)

						explode_damage = ewutils.slime_bylevel(target_data.slimelevel) / 5
						# explode, damaging everyone in the district

						# release bleed storage
						slimes_todistrict = target_data.slimes

						district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)

						# Player was killed. Remove its id from enemies with defender ai.
						enemy_data.id_target = -1
						target_data.id_killer = enemy_data.id_enemy

						# target_data.change_slimes(n=-slimes_dropped / 10, source=ewcfg.source_ghostification)
						civ_weapon = random.choice(ewcfg.makeshift_weapons)

						kill_descriptor = "beaten to death"
						if used_attacktype != ewcfg.enemy_attacktype_unarmed:
							response = used_attacktype.str_damage.format(
								name_enemy=enemy_data.display_name,
								name_target=("<@!{}>".format(target_data.id_user)),
								hitzone=randombodypart,
								strikes=strikes,
								civ_weapon=civ_weapon
							)
							kill_descriptor = used_attacktype.str_killdescriptor
							if crit:
								response += " {}".format(used_attacktype.str_crit.format(
									name_enemy=enemy_data.display_name,
									name_target=target_player.display_name,
									civ_weapon=civ_weapon
								))

							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response += "\n\n" + onbreak_response

							response += "\n\n{}".format(used_attacktype.str_kill.format(
								name_enemy=enemy_data.display_name,
								name_target=("<@!{}>".format(target_data.id_user)),
								emote_skull=ewcfg.emote_slimeskull,
								civ_weapon=civ_weapon
							))
							target_data.trauma = used_attacktype.id_type

						else:
							response = ""

							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response = onbreak_response + "\n\n"

							response = "{name_target} is hit!!\n\n{name_target} has died.".format(
								name_target=target_player.display_name)

							target_data.trauma = ewcfg.trauma_id_environment

						if target_slimeoid.life_state == ewcfg.slimeoid_state_active:
							brain = sl_static.brain_map.get(target_slimeoid.ai)
							response += "\n\n" + brain.str_death.format(slimeoid_name=target_slimeoid.name)

						enemy_data.persist()
						district_data.persist()
						die_resp = target_data.die(
							cause=ewcfg.cause_killing_enemy)  # moved after trauma definition so it can gurantee .die knows killer
						district_data = EwDistrict(district=district_data.name, id_server=district_data.id_server)

						target_data.persist()
						resp_cont.add_response_container(die_resp)
						resp_cont.add_channel_response(ch_name, response)

						# don't recreate enemy data if enemy was killed in explosion
						if bknd_hunt.check_death(enemy_data) == False:
							enemy_data = EwEnemy(id_enemy=self.id_enemy)

						target_data = EwUser(id_user=target_data.id_user, id_server=target_data.id_server, data_level=1)
					else:
						# A non-lethal blow!
						# apply injury
						# if injury_severity > 0:
						#	target_data.apply_injury(hitzone.id_injury, injury_severity, enemy_data.id_enemy)

						if used_attacktype != ewcfg.enemy_attacktype_unarmed:
							if miss:
								response = "{}".format(used_attacktype.str_miss.format(
									name_enemy=enemy_data.display_name,
									name_target=target_player.display_name
								))
							else:
								response = used_attacktype.str_damage.format(
									name_enemy=enemy_data.display_name,
									name_target=("<@!{}>".format(target_data.id_user)),
									hitzone=randombodypart,
									strikes=strikes,
									civ_weapon=random.choice(ewcfg.makeshift_weapons)
								)
								if crit:
									response += " {}".format(used_attacktype.str_crit.format(
										name_enemy=enemy_data.display_name,
										name_target=target_player.display_name,
										civ_weapon=random.choice(ewcfg.makeshift_weapons)
									))
								# sap_response = ""
								# if sap_damage > 0:
								#	sap_response = " and {sap_damage} hardened sap".format(sap_damage = sap_damage)

								response += " {target_name} loses {damage:,} slime!".format(
									target_name=target_player.display_name,
									damage=damage
									# sap_response=sap_response
								)
								if len(onbreak_responses) != 0:
									for onbreak_response in onbreak_responses:
										response += "\n\n" + onbreak_response
						else:
							if miss:
								response = "{target_name} dodges the {enemy_name}'s strike.".format(
									target_name=target_player.display_name, enemy_name=enemy_data.display_name)
							else:
								response = "{target_name} is hit!! {target_name} loses {damage:,} slime!".format(
									target_name=target_player.display_name,
									damage=damage
								)
							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response += "\n" + onbreak_response

						resp_cont.add_channel_response(ch_name, response)
				else:
					response = '{} is unable to attack {}.'.format(enemy_data.display_name, target_player.display_name)
					resp_cont.add_channel_response(ch_name, response)

				# Persist user and enemy data.
				if enemy_data.life_state == ewcfg.enemy_lifestate_alive or enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
					enemy_data.persist()
				target_data.persist()

				district_data.persist()

				# Assign the corpse role to the newly dead player.
				if was_killed:
					member = server.get_member(target_data.id_user)
					await ewrolemgr.updateRoles(client=client, member=member)
			# announce death in kill feed channel
			# killfeed_channel = ewutils.get_channel(enemy_data.id_server, ewcfg.channel_killfeed)
			# killfeed_resp = resp_cont.channel_responses[ch_name]
			# for r in killfeed_resp:
			#	 resp_cont.add_channel_response(ewcfg.channel_killfeed, r)
			# resp_cont.format_channel_response(ewcfg.channel_killfeed, enemy_data)
			# resp_cont.add_channel_response(ewcfg.channel_killfeed, "`-------------------------`")
		# await ewutils.send_message(client, killfeed_channel, ewutils.formatMessage(enemy_data.display_name, killfeed_resp))

		# Send the response to the player.
		resp_cont.format_channel_response(ch_name, enemy_data)
		if should_post_resp_cont:
			await resp_cont.post()

	# Function that enemies used to attack each other in Gankers Vs. Shamblers.
	async def cannibalize(self):
		client = ewutils.get_client()

		last_messages = []
		should_post_resp_cont = True

		enemy_data = self

		time_now = int(time.time())
		resp_cont = EwResponseContainer(id_server=enemy_data.id_server)
		district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)
		market_data = EwMarket(id_server=enemy_data.id_server)
		ch_name = poi_static.id_to_poi.get(enemy_data.poi).channel

		used_attacktype = hunt_static.attack_type_map.get(enemy_data.attacktype)

		# Get target's info based on its AI.
		target_enemy, group_attack = get_target_by_ai(enemy_data, cannibalize=True)

		if enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid:
			if enemy_data.enemy_props.get('primed') != None:
				if enemy_data.enemy_props.get('primed') != 'true':
					return

			# target_enemy is a dict, enemy IDs are mapped to their coords
			if len(target_enemy) == 1 and not group_attack:
				# print('gaia found target')
				used_id = None

				for key in target_enemy.keys():
					used_id = key

				target_enemy = EwEnemy(id_enemy=used_id, id_server=enemy_data.id_server)

			# print('gaia changed target_enemy into enemy from dict')
			elif len(target_enemy) == 0:
				target_enemy = None

		elif enemy_data.enemyclass == ewcfg.enemy_class_shambler:
			if target_enemy == None:
				return await sh_move(enemy_data)
			elif enemy_data.enemytype == ewcfg.enemy_type_dinoshambler:
				if target_enemy.enemytype == ewcfg.enemy_type_gaia_suganmanuts and enemy_data.enemy_props.get(
						'jumping') == 'true':
					enemy_data.enemy_props['jumping'] = 'false'
				else:
					return await sh_move(enemy_data)

		if bknd_hunt.check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
			# Raid boss has activated!
			response = "*The ground quakes beneath your feet as slime begins to pool into one hulking, solidified mass...*" \
					   "\n{} **{} has arrived! It's level {} and has {} slime!** {}\n".format(
				ewcfg.emote_megaslime,
				enemy_data.display_name,
				enemy_data.level,
				enemy_data.slimes,
				ewcfg.emote_megaslime
			)
			resp_cont.add_channel_response(ch_name, response)

			enemy_data.life_state = ewcfg.enemy_lifestate_alive
			enemy_data.time_lastenter = time_now
			enemy_data.persist()

			target_enemy = None

		elif bknd_hunt.check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_alive:
			# Raid boss attacks.
			pass

		# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
		elif bknd_hunt.check_raidboss_countdown(enemy_data) == False:

			target_enemy = None

			timer = (enemy_data.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

			if timer < ewcfg.enemy_attack_tick_length and timer != 0:
				timer = ewcfg.enemy_attack_tick_length

			countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
			resp_cont.add_channel_response(ch_name, countdown_response)

			# TODO: Edit the countdown message instead of deleting and reposting
			last_messages = await resp_cont.post()
			asyncio.ensure_future(fe_utils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))

			# Don't post resp_cont a second time while the countdown is going on.
			should_post_resp_cont = False

		if target_enemy != None and not group_attack:

			miss = False

			# Weaponized flavor text.
			# hitzone = ewwep.get_hitzone()
			# randombodypart = hitzone.name
			# if random.random() < 0.5:
			# 	randombodypart = random.choice(hitzone.aliases)
			randombodypart = 'brainz' if enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid else 'stem'

			slimes_damage = 0
			set_damage = int(enemy_data.enemy_props.get('setdamage'))
			if set_damage != None:
				slimes_damage = set_damage

			# Enemies don't select for these types of lifestates in their AI, this serves as a backup just in case.
			if target_enemy.life_state != ewcfg.enemy_lifestate_unactivated and target_enemy.life_state != ewcfg.enemy_lifestate_dead:
				was_killed = False
				below_full = False
				below_half = False
				was_hurt = True

				# Attacking-type-specific adjustments
				if used_attacktype.fn_effect != None:
					# Apply effects for non-reference values
					miss = False  # Make sure to account for phosphorpoppies statuses

				if miss:
					slimes_damage = 0

				enemy_data.persist()
				target_enemy = EwEnemy(id_enemy=target_enemy.id_enemy, id_server=target_enemy.id_server)

				if slimes_damage >= target_enemy.slimes:  # - target_enemy.bleed_storage:
					was_killed = True
					slimes_damage = max(target_enemy.slimes, 0)  # - target_enemy.bleed_storage
				else:
					# In Gankers Vs. Shamblers, responses are only sent out after the initial hit and when the target reaches below 50% HP
					# This serves to ensure less responses cluttering up the channel and to preserve performance.
					if target_enemy.slimes < target_enemy.initialslimes and not target_enemy.enemy_props.get(
							'below_full') == 'true':
						target_enemy.enemy_props['below_full'] = 'true'
						below_full = True
					elif target_enemy.slimes < int(target_enemy.initialslimes / 2) and not target_enemy.enemy_props.get(
							'below_half') == 'true':
						target_enemy.enemy_props['below_half'] = 'true'
						below_half = True

				sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=enemy_data.id_server)

				# slimes_drained = int(3 * slimes_damage / 4)  # 3/4
				slimes_drained = int(7 * slimes_damage / 8)  # 7/8

				damage = slimes_damage

				# slimes_tobleed = int((slimes_damage - slimes_drained) / 2)

				slimes_directdamage = slimes_damage  # - slimes_tobleed
				slimes_splatter = slimes_damage - slimes_drained  # - slimes_tobleed

				market_data.splattered_slimes += slimes_damage
				market_data.persist()
				district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
				# target_enemy.bleed_storage += slimes_tobleed
				target_enemy.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
				sewer_data.change_slimes(n=slimes_drained)

				if target_enemy.enemytype == ewcfg.enemy_type_gaia_razornuts:
					bite_response = "{} [{}] ({}) bit on a razornut and got hurt! They lost 20000 slime!".format(
						enemy_data.display_name, enemy_data.identifier, enemy_data.gvs_coord)
					enemy_data.change_slimes(n=-20000)
					if enemy_data.slimes <= 0:
						bite_response += " The attack killed {} [{}] ({}) in the process.".format(
							enemy_data.display_name, enemy_data.identifier, enemy_data.gvs_coord)

						bknd_hunt.delete_enemy(enemy_data)
						resp_cont.add_channel_response(ch_name, bite_response)

						return await resp_cont.post()
					else:
						resp_cont.add_channel_response(ch_name, bite_response)
				elif enemy_data.enemytype == ewcfg.enemy_type_shambleballplayer:
					current_target_coord = target_enemy.gvs_coord
					row = current_target_coord[0]
					column = int(current_target_coord[1])

					if column < 9:
						new_coord = "{}{}".format(row, column + 1)

						gaias_in_coord = gvs_get_gaias_from_coord(enemy_data.poi, new_coord)

						if len(gaias_in_coord) > 0:
							pass
						else:
							punt_response = "{} [{}] ({}) punts a {} into {}!".format(enemy_data.display_name,
																					  enemy_data.identifier,
																					  enemy_data.gvs_coord,
																					  target_enemy.display_name,
																					  new_coord)
							resp_cont.add_channel_response(ch_name, punt_response)

							target_enemy.gvs_coord = new_coord
							target_enemy.persist()

				if was_killed:
					# Enemy was killed.
					bknd_hunt.delete_enemy(target_enemy)

					# release bleed storage
					slimes_todistrict = target_enemy.slimes

					district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)

					response = used_attacktype.str_damage.format(
						name_enemy=enemy_data.display_name,
						name_target=target_enemy.display_name,
						hitzone=randombodypart,
					)

					response += "\n\n{}".format(used_attacktype.str_kill.format(
						name_enemy=enemy_data.display_name,
						name_target=target_enemy.display_name,
						emote_skull=ewcfg.emote_slimeskull
					))

					enemy_data.persist()
					district_data.persist()

					resp_cont.add_channel_response(ch_name, response)

					# don't recreate enemy data if enemy was killed in explosion
					if bknd_hunt.check_death(enemy_data) == False:
						enemy_data = EwEnemy(id_enemy=self.id_enemy)

				else:
					# A non-lethal blow!
					if miss:
						response = "{}".format(used_attacktype.str_miss.format(
							name_enemy=enemy_data.display_name,
							name_target=target_enemy.display_name
						))
					else:
						response = used_attacktype.str_damage.format(
							name_enemy=enemy_data.display_name,
							name_target=target_enemy.display_name,
							hitzone=randombodypart,
						)
						response += " {target_name} loses {damage:,} slime!".format(
							target_name=target_enemy.display_name,
							damage=damage,
						)

					# if below_full == False and below_half == False:
					# 	should_post_resp_cont = False
					# 	response = ""

					target_enemy.persist()
					resp_cont.add_channel_response(ch_name, response)

				# Persist enemy data.
				if enemy_data.life_state == ewcfg.enemy_lifestate_alive or enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
					enemy_data.persist()

				district_data.persist()

			if enemy_data.attacktype == ewcfg.enemy_attacktype_gvs_g_explosion:
				bknd_hunt.delete_enemy(enemy_data)

		elif target_enemy != None and group_attack:
			# print('group attack...')

			for key in target_enemy.keys():

				used_id = key
				target_enemy = EwEnemy(id_enemy=used_id, id_server=enemy_data.id_server)

				miss = False

				# Weaponized flavor text.
				randombodypart = 'brainz' if enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid else 'stem'

				slimes_damage = 0
				set_damage = int(enemy_data.enemy_props.get('setdamage'))
				if set_damage != None:
					slimes_damage = set_damage

				# Enemies don't select for these types of lifestates in their AI, this serves as a backup just in case.
				if target_enemy.life_state != ewcfg.enemy_lifestate_unactivated and target_enemy.life_state != ewcfg.enemy_lifestate_dead:
					was_killed = False
					below_full = False
					below_half = False
					was_hurt = True

					enemy_data.persist()
					target_enemy = EwEnemy(id_enemy=target_enemy.id_enemy, id_server=target_enemy.id_server)

					if slimes_damage >= target_enemy.slimes:
						was_killed = True
						slimes_damage = max(target_enemy.slimes, 0)
					else:
						# In Gankers Vs. Shamblers, responses are only sent out after the initial hit and when the target reaches below 50% HP
						# This serves to ensure less responses cluttering up the channel and to preserve performance.
						if target_enemy.slimes < target_enemy.initialslimes and not target_enemy.enemy_props.get(
								'below_full') == 'true':
							target_enemy.enemy_props['below_full'] = 'true'
							below_full = True
						elif target_enemy.slimes < int(
								target_enemy.initialslimes / 2) and not target_enemy.enemy_props.get(
								'below_half') == 'true':
							target_enemy.enemy_props['below_half'] = 'true'
							below_half = True

					sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=enemy_data.id_server)

					# slimes_drained = int(3 * slimes_damage / 4)  # 3/4
					slimes_drained = int(7 * slimes_damage / 8)  # 7/8

					damage = slimes_damage

					# slimes_tobleed = int((slimes_damage - slimes_drained) / 2)

					slimes_directdamage = slimes_damage  # - slimes_tobleed
					slimes_splatter = slimes_damage - slimes_drained  # - slimes_tobleed

					market_data.splattered_slimes += slimes_damage
					market_data.persist()
					district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
					# target_enemy.bleed_storage += slimes_tobleed
					target_enemy.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
					sewer_data.change_slimes(n=slimes_drained)

					if was_killed:
						# Enemy was killed.
						bknd_hunt.delete_enemy(target_enemy)

						# release bleed storage
						slimes_todistrict = target_enemy.slimes

						district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)

						# target_data.change_slimes(n=-slimes_dropped / 10, source=ewcfg.source_ghostification)

						response = used_attacktype.str_damage.format(
							name_enemy=enemy_data.display_name,
							name_target=target_enemy.display_name,
							hitzone=randombodypart,
						)

						response += "\n\n{}".format(used_attacktype.str_kill.format(
							name_enemy=enemy_data.display_name,
							name_target=target_enemy.display_name,
							emote_skull=ewcfg.emote_slimeskull
						))

						enemy_data.persist()
						district_data.persist()

						resp_cont.add_channel_response(ch_name, response)

						# don't recreate enemy data if enemy was killed in explosion
						if bknd_hunt.check_death(enemy_data) == False:
							enemy_data = EwEnemy(id_enemy=self.id_enemy)

					else:
						# A non-lethal blow!

						if miss:
							response = "{}".format(used_attacktype.str_miss.format(
								name_enemy=enemy_data.display_name,
								name_target=target_enemy.display_name
							))
						else:
							response = used_attacktype.str_damage.format(
								name_enemy=enemy_data.display_name,
								name_target=target_enemy.display_name,
								hitzone=randombodypart,
							)
							response += " {target_name} loses {damage:,} slime!".format(
								target_name=target_enemy.display_name,
								damage=damage,
							)

						# if below_full == False and below_half == False:
						# 	should_post_resp_cont = False
						# 	response = ""

						target_enemy.persist()
						resp_cont.add_channel_response(ch_name, response)

					# Persist enemy data.
					if enemy_data.life_state == ewcfg.enemy_lifestate_alive or enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
						enemy_data.persist()

				district_data.persist()

			if enemy_data.attacktype == ewcfg.enemy_attacktype_gvs_g_explosion:
				bknd_hunt.delete_enemy(enemy_data)

		# Send the response to the player.
		resp_cont.format_channel_response(ch_name, enemy_data)
		if should_post_resp_cont:
			await resp_cont.post()

	def move(self):
		resp_cont = EwResponseContainer(id_server=self.id_server)

		old_district_response = ""
		new_district_response = ""
		gang_base_response = ""

		try:
			# Raid bosses can move into other parts of the outskirts as well as the city, including district zones.
			destinations = set(poi_static.poi_neighbors.get(self.poi))

			if self.enemytype in ewcfg.gvs_enemies:
				path = [ewcfg.poi_id_assaultflatsbeach, ewcfg.poi_id_vagrantscorner, ewcfg.poi_id_greenlightdistrict,
						ewcfg.poi_id_downtown]

				if self.poi == path[0]:
					destinations = [path[1]]
				elif self.poi == path[1]:
					destinations = [path[2]]
				elif self.poi == path[2]:
					destinations = [path[3]]
				elif self.poi == path[3]:
					# Raid boss has finished its path
					return

			# Filter subzones and gang bases out.
			# Nudge raidbosses into the city.
			for destination in destinations:

				destination_poi_data = poi_static.id_to_poi.get(destination)
				if destination_poi_data.is_subzone or destination_poi_data.is_gangbase:
					destinations.remove(destination)

				if self.poi in poi_static.outskirts_depths:
					if destination in poi_static.outskirts_depths:
						destinations.remove(destination)
				elif self.poi in poi_static.outskirts_middle:
					if (destination in poi_static.outskirts_middle) or (destination in poi_static.outskirts_depths):
						destinations.remove(destination)
				elif self.poi in poi_static.outskirts_edges:
					if (destination in poi_static.outskirts_edges) or (destination in poi_static.outskirts_middle):
						destinations.remove(destination)

			if len(destinations) > 0:

				old_poi = self.poi
				new_poi = random.choice(list(destinations))

				self.poi = new_poi
				self.time_lastenter = int(time.time())
				self.id_target = -1

				# print("DEBUG - {} MOVED FROM {} TO {}".format(self.display_name, old_poi, new_poi))

				# new_district = EwDistrict(district=new_poi, id_server=self.id_server)
				# if len(new_district.get_enemies_in_district() > 0:

				# When a raid boss enters a new district, give it a blank identifier
				self.identifier = ''

				new_poi_def = poi_static.id_to_poi.get(new_poi)
				new_ch_name = new_poi_def.channel
				new_district_response = "*A low roar booms throughout the district, as slime on the ground begins to slosh all around.*\n {} **{} has arrived!** {}".format(
					ewcfg.emote_megaslime,
					self.display_name,
					ewcfg.emote_megaslime
				)
				resp_cont.add_channel_response(new_ch_name, new_district_response)

				old_district_response = "{} has moved to {}!".format(self.display_name, new_poi_def.str_name)
				old_poi_def = poi_static.id_to_poi.get(old_poi)
				old_ch_name = old_poi_def.channel
				resp_cont.add_channel_response(old_ch_name, old_district_response)

				if new_poi not in poi_static.outskirts:
					gang_base_response = "There are reports of a powerful enemy roaming around {}.".format(
						new_poi_def.str_name)
					channels = ewcfg.hideout_channels
					for ch in channels:
						resp_cont.add_channel_response(ch, gang_base_response)
		finally:
			self.persist()
			return resp_cont

	def change_slimes(self, n=0, source=None):
		change = int(n)
		self.slimes += change

		if n < 0:
			change *= -1  # convert to positive number
			if source == ewcfg.source_damage or source == ewcfg.source_bleeding or source == ewcfg.source_self_damage:
				self.totaldamage += change

		self.persist()

	def getStatusEffects(self):
		values = []

		try:
			data = bknd_core.execute_sql_query(
				"SELECT {id_status} FROM enemy_status_effects WHERE {id_server} = %s and {id_enemy} = %s".format(
					id_status=ewcfg.col_id_status,
					id_server=ewcfg.col_id_server,
					id_enemy=ewcfg.col_id_enemy
				), (
					self.id_server,
					self.id_enemy
				))

			for row in data:
				values.append(row[0])

		except:
			pass
		finally:
			return values

	def applyStatus(self, id_status=None, value=0, source="", multiplier=1, id_target=-1):
		response = ""
		if id_status != None:
			status = None

			status = se_static.status_effects_def_map.get(id_status)
			time_expire = status.time_expire * multiplier

			if status != None:
				statuses = self.getStatusEffects()

				status_effect = EwEnemyStatusEffect(id_status=id_status, enemy_data=self, time_expire=time_expire,
													value=value, source=source, id_target=id_target)

				if id_status in statuses:
					status_effect.value = value

					if status.time_expire > 0 and id_status in ewcfg.stackable_status_effects:
						status_effect.time_expire += time_expire
						response = status.str_acquire

					status_effect.persist()
				else:
					response = status.str_acquire

		return response

	def clear_status(self, id_status=None):
		if id_status != None:
			try:
				conn_info = bknd_core.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Save the object.
				cursor.execute(
					"DELETE FROM enemy_status_effects WHERE {id_status} = %s and {id_enemy} = %s and {id_server} = %s".format(
						id_status=ewcfg.col_id_status,
						id_enemy=ewcfg.col_id_enemy,
						id_server=ewcfg.col_id_server
					), (
						id_status,
						self.id_enemy,
						self.id_server
					))

				conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				bknd_core.databaseClose(conn_info)

	def clear_allstatuses(self):
		try:
			bknd_core.execute_sql_query(
				"DELETE FROM enemy_status_effects WHERE {id_server} = %s AND {id_enemy} = %s".format(
					id_server=ewcfg.col_id_server,
					id_enemy=ewcfg.col_id_enemy
				), (
					self.id_server,
					self.id_enemy
				))
		except:
			ewutils.logMsg("Failed to clear status effects for enemy {}.".format(self.id_enemy))

	def dodge(self):
		enemy_data = self

		resp_cont = EwResponseContainer(id_server=enemy_data.id_server)

		target_data = None

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			users = bknd_core.execute_sql_query(
				"SELECT {id_user}, {life_state} FROM users WHERE {poi} = %s AND {id_server} = %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin})".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=random.choice(users)[0], id_server=enemy_data.id_server)
		elif enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != -1:
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server)
		else:
			target_data, group_attack = get_target_by_ai(enemy_data)

		if target_data != None:
			target = EwPlayer(id_user=target_data.id_user, id_server=enemy_data.id_server)
			ch_name = poi_static.id_to_poi.get(enemy_data.poi).channel

			id_status = ewcfg.status_evasive_id

			enemy_data.clear_status(id_status=id_status)

			enemy_data.applyStatus(id_status=id_status, source=enemy_data.id_enemy, id_target=(
				target_data.id_user if target_data.combatant_type == "player" else target_data.id_enemy))

			response = "{} focuses on dodging {}'s attacks.".format(enemy_data.display_name, target.display_name)
			resp_cont.add_channel_response(ch_name, response)

		return resp_cont

	def taunt(self):
		enemy_data = self

		resp_cont = EwResponseContainer(id_server=enemy_data.id_server)

		target_data = None

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			return
		elif enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != -1:
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server)
		else:
			target_data, group_attack = get_target_by_ai(enemy_data)

		if target_data != None:
			target = EwPlayer(id_user=target_data.id_user, id_server=enemy_data.id_server)
			ch_name = poi_static.id_to_poi.get(enemy_data.poi).channel

			id_status = ewcfg.status_taunted_id

			target_statuses = target_data.getStatusEffects()

			if id_status in target_statuses:
				return

			target_data.applyStatus(id_status=id_status, source=enemy_data.id_enemy, id_target=enemy_data.id_enemy)

			response = "{} taunts {} into attacking it.".format(enemy_data.display_name, target.display_name)
			resp_cont.add_channel_response(ch_name, response)

		return resp_cont

	def aim(self):
		enemy_data = self

		resp_cont = EwResponseContainer(id_server=enemy_data.id_server)

		target_data = None

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			return
		elif enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != -1:
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server)
		else:
			target_data, group_attack = get_target_by_ai(enemy_data)

		if target_data != None:
			target = EwPlayer(id_user=target_data.id_user, id_server=enemy_data.id_server)
			ch_name = poi_static.id_to_poi.get(enemy_data.poi).channel

			id_status = ewcfg.status_aiming_id

			enemy_data.clear_status(id_status=id_status)

			enemy_data.applyStatus(id_status=id_status, source=enemy_data.id_enemy, id_target=(
				target_data.id_user if target_data.combatant_type == "player" else target_data.id_enemy))

			enemy_data.persist()

			response = "{} aims at {}'s weak spot.".format(enemy_data.display_name, target.display_name)
			resp_cont.add_channel_response(ch_name, response)

		return resp_cont

	@property
	def slimelevel(self):
		return self.level


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
				spawn_enemy(
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


# Drops items into the district when an enemy dies.
def drop_enemy_loot(enemy_data, district_data):
	loot_poi = poi_static.id_to_poi.get(district_data.name)
	loot_resp_cont = EwResponseContainer(id_server=enemy_data.id_server)
	response = ""

	item_counter = 0
	loot_multiplier = 1

	drop_chance = None
	drop_min = None
	drop_max = None
	drop_range = None

	has_dropped_item = False
	drop_table = ewcfg.enemy_drop_tables[enemy_data.enemytype]

	for drop_data_set in drop_table:
		value = None
		for key in drop_data_set.keys():
			value = key
			break

		drop_chance = drop_data_set[value][0]
		drop_min = drop_data_set[value][1]
		drop_max = drop_data_set[value][2]

		item = static_items.item_map.get(value)

		item_type = ewcfg.it_item
		if item != None:
			item_id = item.id_item
			name = item.str_name

		# Finds the item if it's an EwFood item.
		if item == None:
			item = static_food.food_map.get(value)
			item_type = ewcfg.it_food
			if item != None:
				item_id = item.id_food
				name = item.str_name

		# Finds the item if it's an EwCosmeticItem.
		if item == None:
			item = static_cosmetics.cosmetic_map.get(value)
			item_type = ewcfg.it_cosmetic
			if item != None:
				item_id = item.id_cosmetic
				name = item.str_name

		if item == None:
			item = static_items.furniture_map.get(value)
			item_type = ewcfg.it_furniture
			if item != None:
				item_id = item.id_furniture
				name = item.str_name
				if item_id in static_items.furniture_pony:
					item.vendors = [ewcfg.vendor_bazaar]

		if item == None:
			item = static_weapons.weapon_map.get(value)
			item_type = ewcfg.it_weapon
			if item != None:
				item_id = item.id_weapon
				name = item.str_weapon

		# Some entries in the drop table aren't item IDs, they're general values for random drops like cosmetics/crops
		if item == None:

			if value == "crop":
				item = random.choice(static_food.vegetable_list)
				item_type = ewcfg.it_food

			elif value in [ewcfg.rarity_plebeian, ewcfg.rarity_patrician]:
				item_type = ewcfg.it_cosmetic

				cosmetics_list = []
				for result in static_cosmetics.cosmetic_items_list:
					if result.ingredients == "":
						cosmetics_list.append(result)
					else:
						pass

				if value == ewcfg.rarity_plebeian:
					items = []

					for cosmetic in cosmetics_list:
						if cosmetic.rarity == ewcfg.rarity_plebeian:
							items.append(cosmetic)

					item = items[random.randint(0, len(items) - 1)]
				elif value == ewcfg.rarity_patrician:
					items = []

					for cosmetic in cosmetics_list:
						if cosmetic.rarity == ewcfg.rarity_plebeian:
							items.append(cosmetic)

					item = items[random.randint(0, len(items) - 1)]

		if item != None:

			item_dropped = random.randrange(100) <= (drop_chance - 1)
			if item_dropped:
				has_dropped_item = True

				drop_range = list(range(drop_min, drop_max + 1))
				item_amount = random.choice(drop_range)

				if enemy_data.rare_status == 1:
					loot_multiplier *= 1.5

				if enemy_data.enemytype == ewcfg.enemy_type_unnervingfightingoperator:
					loot_multiplier *= math.ceil(enemy_data.slimes / 1000000)

				item_amount = math.ceil(item_amount * loot_multiplier)
			else:
				item_amount = 0

			for i in range(item_amount):
				item_props = itm_utils.gen_item_props(item)

				generated_item_id = bknd_item.item_create(
					item_type=item_type,
					id_user=enemy_data.poi,
					id_server=enemy_data.id_server,
					stack_max=-1,
					stack_size=0,
					item_props=item_props
				)

				response = "They dropped a {item_name}!".format(item_name=item.str_name)
				loot_resp_cont.add_channel_response(loot_poi.channel, response)

		else:
			ewutils.logMsg("ERROR: COULD NOT DROP ITEM WITH VALUE '{}'".format(value))
	if not has_dropped_item:
		response = "They didn't drop anything...\n"
		loot_resp_cont.add_channel_response(loot_poi.channel, response)

	return loot_resp_cont


# Spawns an enemy in a randomized outskirt district. If a district is full, it will try again, up to 5 times.
def spawn_enemy(
		id_server,
		pre_chosen_type=None,
		pre_chosen_level=None,
		pre_chosen_slimes=None,
		pre_chosen_displayname=None,
		pre_chosen_expiration=None,
		pre_chosen_initialslimes=None,
		pre_chosen_poi=None,
		pre_chosen_identifier=None,
		# pre_chosen_hardened_sap = None,
		pre_chosen_weather=None,
		pre_chosen_faction=None,
		pre_chosen_owner=None,
		pre_chosen_coord=None,
		pre_chosen_rarity=False,
		pre_chosen_props=None,
		manual_spawn=False,
):
	time_now = int(time.time())
	response = ""
	ch_name = ""
	resp_cont = EwResponseContainer(id_server=id_server)
	chosen_poi = ""
	potential_chosen_poi = ""
	threat_level = ""
	boss_choices = []

	enemies_count = ewcfg.max_enemies
	try_count = 0

	rarity_choice = random.randrange(10000)

	if rarity_choice <= 5200:
		# common enemies
		enemytype = random.choice(ewcfg.common_enemies)
	elif rarity_choice <= 8000:
		# uncommon enemies
		enemytype = random.choice(ewcfg.uncommon_enemies)
	elif rarity_choice <= 9700:
		# rare enemies
		enemytype = random.choice(ewcfg.rare_enemies)
	else:
		# raid bosses
		threat_level_choice = random.randrange(1000)

		if threat_level_choice <= 450:
			threat_level = "micro"
		elif threat_level_choice <= 720:
			threat_level = "monstrous"
		elif threat_level_choice <= 900:
			threat_level = "mega"
		else:
			threat_level = "mega"
		# threat_level = "nega"

		boss_choices = ewcfg.raid_boss_tiers[threat_level]
		enemytype = random.choice(boss_choices)

	if pre_chosen_type is not None:
		enemytype = pre_chosen_type

	if not manual_spawn:

		while enemies_count >= ewcfg.max_enemies and try_count < 5:

			# Sand bags only spawn in the dojo
			if enemytype == ewcfg.enemy_type_sandbag:
				potential_chosen_poi = ewcfg.poi_id_dojo
			else:
				potential_chosen_poi = random.choice(poi_static.outskirts)

			potential_chosen_district = EwDistrict(district=potential_chosen_poi, id_server=id_server)
			enemies_list = potential_chosen_district.get_enemies_in_district()
			enemies_count = len(enemies_list)

			if enemies_count < ewcfg.max_enemies:
				chosen_poi = potential_chosen_poi
				try_count = 5
			else:
				# Enemy couldn't spawn in that district, try again
				try_count += 1

		# If it couldn't find a district in 5 tries or less, back out of spawning that enemy.
		if chosen_poi == "":
			return resp_cont

		if enemytype == 'titanoslime':
			potential_chosen_poi = 'downtown'

		# If an enemy spawns in the Nuclear Beach, it should be remade as a 'pre-historic' enemy.
		if potential_chosen_poi in [ewcfg.poi_id_nuclear_beach_edge, ewcfg.poi_id_nuclear_beach,
									ewcfg.poi_id_nuclear_beach_depths]:
			enemytype = random.choice(ewcfg.pre_historic_enemies)
			# If the enemy is a raid boss, re-roll it once to make things fair
			if enemytype in ewcfg.raid_bosses:
				enemytype = random.choice(ewcfg.pre_historic_enemies)
	else:
		if pre_chosen_poi == None:
			return

	if pre_chosen_poi != None:
		chosen_poi = pre_chosen_poi

	if enemytype != None:
		enemy = get_enemy_data(enemytype)

		# Assign enemy attributes that weren't assigned in get_enemy_data
		enemy.id_server = id_server
		enemy.slimes = enemy.slimes if pre_chosen_slimes is None else pre_chosen_slimes
		enemy.display_name = enemy.display_name if pre_chosen_displayname is None else pre_chosen_displayname
		enemy.level = level_byslime(enemy.slimes) if pre_chosen_level is None else pre_chosen_level
		enemy.expiration_date = time_now + ewcfg.time_despawn if pre_chosen_expiration is None else pre_chosen_expiration
		enemy.initialslimes = enemy.slimes if pre_chosen_initialslimes is None else pre_chosen_initialslimes
		enemy.poi = chosen_poi
		enemy.identifier = set_identifier(chosen_poi,
										  id_server) if pre_chosen_identifier is None else pre_chosen_identifier
		# enemy.hardened_sap = int(enemy.level / 2) if pre_chosen_hardened_sap is None else pre_chosen_hardened_sap
		enemy.weathertype = ewcfg.enemy_weathertype_normal if pre_chosen_weather is None else pre_chosen_weather
		enemy.faction = '' if pre_chosen_faction is None else pre_chosen_faction
		enemy.owner = -1 if pre_chosen_owner is None else pre_chosen_owner
		enemy.gvs_coord = '' if pre_chosen_coord is None else pre_chosen_coord
		enemy.rare_status = enemy.rare_status if pre_chosen_rarity is None else pre_chosen_rarity

		if pre_chosen_weather != ewcfg.enemy_weathertype_normal:
			if pre_chosen_weather == ewcfg.enemy_weathertype_rainresist:
				enemy.display_name = "Bicarbonate {}".format(enemy.display_name)
				enemy.slimes *= 2

		# TODO delete after double halloween
		market_data = EwMarket(id_server=id_server)
		if (
				enemytype == ewcfg.enemy_type_doubleheadlessdoublehorseman or enemytype == ewcfg.enemy_type_doublehorse) and market_data.horseman_deaths >= 1:
			enemy.slimes *= 1.5

		props = None
		try:
			props = ewcfg.enemy_data_table[enemytype]["props"]
		except:
			pass

		enemy.enemy_props = props if pre_chosen_props is None else pre_chosen_props

		enemy.persist()

		# Recursively spawn enemies that belong to groups.
		if enemytype in ewcfg.enemy_group_leaders:
			sub_enemies_list = ewcfg.enemy_spawn_groups[enemytype]
			sub_enemies_list_item_max = len(sub_enemies_list)
			sub_enemy_list_item_count = 0

			while sub_enemy_list_item_count < sub_enemies_list_item_max:
				sub_enemy_type = sub_enemies_list[sub_enemy_list_item_count][0]
				sub_enemy_spawning_max = sub_enemies_list[sub_enemy_list_item_count][1]
				sub_enemy_spawning_count = 0

				sub_enemy_list_item_count += 1
				while sub_enemy_spawning_count < sub_enemy_spawning_max:
					sub_enemy_spawning_count += 1

					sub_resp_cont = spawn_enemy(id_server=id_server, pre_chosen_type=sub_enemy_type,
												pre_chosen_poi=chosen_poi, manual_spawn=True)

					resp_cont.add_response_container(sub_resp_cont)

		if enemytype not in ewcfg.raid_bosses:

			if enemytype in ewcfg.gvs_enemies_gaiaslimeoids:
				response = "**A {} has been planted in {}!!**".format(enemy.display_name, enemy.gvs_coord)
			elif enemytype in ewcfg.gvs_enemies_shamblers:
				response = "**A {} creeps forward!!** It spawned in {}!".format(enemy.display_name, enemy.gvs_coord)
			elif enemytype == ewcfg.enemy_type_doubleheadlessdoublehorseman:
				response = "***BEHOLD!!!***  The {} has arrvied to challenge thee! He is of {} slime, and {} in level. Happy Double Halloween, you knuckleheads!".format(
					enemy.display_name, enemy.slimes, enemy.level)

				if market_data.horseman_deaths >= 1:
					response += "\n***BACK SO SOON, MORTALS? I'M JUST GETTING WARMED UP, BAHAHAHAHAHAHA!!!***"

			elif enemytype == ewcfg.enemy_type_doublehorse:
				response = "***HARK!!!***  Clopping echoes throughout the cave! The {} has arrived with {} slime, and {} levels. And on top of him rides...".format(
					enemy.display_name, enemy.slimes, enemy.level)

			else:
				response = "**An enemy draws near!!** It's a level {} {}, and has {} slime.".format(enemy.level,
																									enemy.display_name,
																									enemy.slimes)
				if enemytype == ewcfg.enemy_type_sandbag:
					response = "A new {} just got sent in. It's level {}, and has {} slime.\n*'Don't hold back!'*, the Dojo Master cries out from afar.".format(
						enemy.display_name, enemy.level, enemy.slimes)

		ch_name = poi_static.id_to_poi.get(enemy.poi).channel

	if len(response) > 0 and len(ch_name) > 0:
		resp_cont.add_channel_response(ch_name, response)

	return resp_cont


# Determines what level an enemy is based on their slime count.
def level_byslime(slime):
	return int(abs(slime) ** 0.25)


# Assigns enemies most of their necessary attributes based on their type.
def get_enemy_data(enemy_type):
	enemy = EwEnemy()

	rare_status = 0
	if random.randrange(5) == 0 and enemy_type not in ewcfg.overkill_enemies and enemy_type not in ewcfg.gvs_enemies:
		rare_status = 1

	enemy.id_server = -1
	enemy.slimes = 0
	enemy.totaldamage = 0
	enemy.level = 0
	enemy.life_state = ewcfg.enemy_lifestate_alive
	enemy.enemytype = enemy_type
	enemy.bleed_storage = 0
	enemy.time_lastenter = 0
	enemy.initialslimes = 0
	enemy.id_target = -1
	enemy.raidtimer = 0
	enemy.rare_status = rare_status

	if enemy_type in ewcfg.raid_bosses:
		enemy.life_state = ewcfg.enemy_lifestate_unactivated
		enemy.raidtimer = int(time.time())

	slimetable = ewcfg.enemy_data_table[enemy_type]["slimerange"]
	minslime = slimetable[0]
	maxslime = slimetable[1]

	slime = random.randrange(minslime, (maxslime + 1))

	enemy.slimes = slime
	enemy.ai = ewcfg.enemy_data_table[enemy_type]["ai"]
	enemy.display_name = ewcfg.enemy_data_table[enemy_type]["displayname"]
	enemy.attacktype = ewcfg.enemy_data_table[enemy_type]["attacktype"]

	try:
		enemy.enemyclass = ewcfg.enemy_data_table[enemy_type]["class"]
	except:
		enemy.enemyclass = ewcfg.enemy_class_normal

	if rare_status == 1:
		enemy.display_name = ewcfg.enemy_data_table[enemy_type]["raredisplayname"]
		enemy.slimes *= 2

	return enemy


# Gives enemy an identifier so it's easier to pick out in a crowd of enemies
def set_identifier(poi, id_server):
	district = EwDistrict(district=poi, id_server=id_server)
	enemies_list = district.get_enemies_in_district()

	# A list of identifiers from enemies in a district
	enemy_identifiers = []

	new_identifier = ewcfg.identifier_letters[0]

	if len(enemies_list) > 0:
		for enemy_id in enemies_list:
			enemy = EwEnemy(id_enemy=enemy_id)
			enemy_identifiers.append(enemy.identifier)

		# Sort the list of identifiers alphabetically
		enemy_identifiers.sort()

		for checked_enemy_identifier in enemy_identifiers:
			# If the new identifier matches one from the list of enemy identifiers, give it the next applicable letter
			# Repeat until a unique identifier is given
			if new_identifier == checked_enemy_identifier:
				next_letter = (ewcfg.identifier_letters.index(checked_enemy_identifier) + 1)
				new_identifier = ewcfg.identifier_letters[next_letter]
			else:
				continue

	return new_identifier


# Gathers all enemies from the database (that are either raid bosses or have users in the same district as them) and has them perform an action
async def enemy_perform_action(id_server):
	# time_start = time.time()

	client = ewcfg.get_client()

	time_now = int(time.time())

	enemydata = bknd_core.execute_sql_query(
		"SELECT {id_enemy} FROM enemies WHERE ((enemies.poi IN (SELECT users.poi FROM users WHERE NOT (users.life_state = %s OR users.life_state = %s) AND users.id_server = {id_server})) OR (enemies.enemytype IN %s) OR (enemies.life_state = %s OR enemies.expiration_date < %s) OR (enemies.id_target != -1)) AND enemies.id_server = {id_server}".format(
			id_enemy=ewcfg.col_id_enemy,
			id_server=id_server
		), (
			ewcfg.life_state_corpse,
			ewcfg.life_state_kingpin,
			ewcfg.raid_bosses,
			ewcfg.enemy_lifestate_dead,
			time_now
		))
	# enemydata = bknd_core.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE id_server = %s".format(
	#	id_enemy = ewcfg.col_id_enemy
	# ),(
	#	id_server,
	# ))

	# Remove duplicates from SQL query
	# enemydata = set(enemydata)

	for row in enemydata:
		enemy = EwEnemy(id_enemy=row[0], id_server=id_server)
		enemy_statuses = enemy.getStatusEffects()
		resp_cont = EwResponseContainer(id_server=id_server)

		# If an enemy is marked for death or has been alive too long, delete it
		if enemy.life_state == ewcfg.enemy_lifestate_dead or (enemy.expiration_date < time_now):
			bknd_hunt.delete_enemy(enemy)
		else:
			# If an enemy is an activated raid boss, it has a 1/20 chance to move between districts.
			if enemy.enemytype in ewcfg.enemy_movers and enemy.life_state == ewcfg.enemy_lifestate_alive and check_raidboss_movecooldown(
					enemy):
				if random.randrange(20) == 0:
					resp_cont = enemy.move()
					if resp_cont != None:
						await resp_cont.post()

			# If an enemy is alive and not a sandbag, make it perform the kill function.
			if enemy.enemytype != ewcfg.enemy_type_sandbag:

				ch_name = poi_static.id_to_poi.get(enemy.poi).channel

				# Check if the enemy can do anything right now
				if enemy.life_state == ewcfg.enemy_lifestate_unactivated and bknd_hunt.check_raidboss_countdown(enemy):
					# Raid boss has activated!
					response = "*The ground quakes beneath your feet as slime begins to pool into one hulking, solidified mass...*" \
							   "\n{} **{} has arrived! It's level {} and has {} slime!** {}\n".format(
						ewcfg.emote_megaslime,
						enemy.display_name,
						enemy.level,
						enemy.slimes,
						ewcfg.emote_megaslime
					)
					resp_cont.add_channel_response(ch_name, response)

					enemy.life_state = ewcfg.enemy_lifestate_alive
					enemy.time_lastenter = int(time.time())
					enemy.persist()

				# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
				elif bknd_hunt.check_raidboss_countdown(enemy) == False:
					timer = (enemy.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

					if timer < ewcfg.enemy_attack_tick_length and timer != 0:
						timer = ewcfg.enemy_attack_tick_length

					countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
					resp_cont.add_channel_response(ch_name, countdown_response)

					# TODO: Edit the countdown message instead of deleting and reposting
					last_messages = await resp_cont.post()
					asyncio.ensure_future(
						fe_utils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))
					resp_cont = None

				elif any([ewcfg.status_evasive_id, ewcfg.status_aiming_id]) not in enemy_statuses and random.randrange(
						10) == 0:
					resp_cont = random.choice([enemy.dodge, enemy.taunt, enemy.aim])()
				else:
					resp_cont = await enemy.kill()
			else:
				resp_cont = None

			if resp_cont != None:
				await resp_cont.post()


# time_end = time.time()
# ewutils.logMsg("time spent on performing enemy actions: {}".format(time_end - time_start))

async def enemy_perform_action_gvs(id_server):
	client = ewcfg.get_client()

	time_now = int(time.time())

	# condition_gaia_sees_shambler_player = "enemies.poi IN (SELECT users.poi FROM users WHERE (users.life_state = '{}'))".format(ewcfg.life_state_shambler)
	# condition_gaia_sees_shampler_enemy = "enemies.poi IN (SELECT enemies.poi FROM enemies WHERE (enemies.enemyclass = '{}'))".format(ewcfg.enemy_class_shambler)
	# condition_shambler_sees_alive_player = "enemies.poi IN (SELECT users.poi FROM users WHERE (users.life_state IN {}))".format(tuple([ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive]))
	# condition_shambler_sees_gaia_enemy = "enemies.poi IN (SELECT enemies.poi FROM enemies WHERE (enemies.enemyclass = '{}'))".format(ewcfg.enemy_class_gaiaslimeoid)

	# print(despawn_timenow)
	# "SELECT {id_enemy} FROM enemies WHERE (enemies.enemytype IN %s) AND (({condition_1}) OR ({condition_2}) OR ({condition_3}) OR ({condition_4}) OR (enemies.enemytype IN %s) OR (enemies.life_state = %s OR enemies.expiration_date < %s) OR (enemies.id_target != '')) AND enemies.id_server = {id_server}"

	enemydata = bknd_core.execute_sql_query(
		"SELECT {id_enemy} FROM enemies WHERE ((enemies.enemytype IN %s) OR (enemies.life_state = %s OR enemies.expiration_date < %s) OR (enemies.id_target != -1)) AND enemies.id_server = {id_server}".format(
			id_enemy=ewcfg.col_id_enemy,
			id_server=id_server,
		), (
			ewcfg.gvs_enemies,
			ewcfg.enemy_lifestate_dead,
			time_now
		))
	# enemydata = bknd_core.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE id_server = %s".format(
	#	id_enemy = ewcfg.col_id_enemy
	# ),(
	#	id_server,
	# ))

	# Remove duplicates from SQL query
	# enemydata = set(enemydata)

	for row in enemydata:

		enemy = EwEnemy(id_enemy=row[0], id_server=id_server)

		if enemy == None:
			continue

		if poi_static.id_to_poi.get(enemy.poi) != None:
			ch_name = poi_static.id_to_poi.get(enemy.poi).channel
		else:
			continue

		server = client.get_guild(id_server)
		channel = fe_utils.get_channel(server, ch_name)

		# This function returns a false value if that enemy can't act on that turn.
		if not check_enemy_can_act(enemy):
			continue

		# Go through turn counters unrelated to the prevention of acting on that turn.
		turn_timer_response = handle_turn_timers(enemy)
		if turn_timer_response != None and turn_timer_response != "":
			await fe_utils.send_message(client, channel, turn_timer_response)

		enemy = EwEnemy(id_enemy=row[0], id_server=id_server)

		# Unarmed Gaiaslimeoids have no role in combat.
		if enemy.attacktype == ewcfg.enemy_attacktype_unarmed:
			continue

		resp_cont = EwResponseContainer(id_server=id_server)

		# If an enemy is marked for death or has been alive too long, delete it
		if enemy.life_state == ewcfg.enemy_lifestate_dead or (enemy.expiration_date < time_now):
			bknd_hunt.delete_enemy(enemy)
		else:
			# The GvS raidboss has pre-determined pathfinding
			if enemy.enemytype in ewcfg.raid_bosses and enemy.life_state == ewcfg.enemy_lifestate_alive and check_raidboss_movecooldown(
					enemy):
				resp_cont = enemy.move()
				if resp_cont != None:
					await resp_cont.post()

			# If an enemy is alive, make it perform the kill (or cannibalize) function.

			# Check if the enemy can do anything right now
			if enemy.life_state == ewcfg.enemy_lifestate_unactivated and bknd_hunt.check_raidboss_countdown(enemy):
				# Raid boss has activated!
				response = "*The dreaded creature of Dr. Downpour claws its way into {}.*" \
						   "\n{} **{} has arrived! It's level {} and has {} slime. Good luck.** {}\n".format(
					enemy.poi,
					ewcfg.emote_megaslime,
					enemy.display_name,
					enemy.level,
					enemy.slimes,
					ewcfg.emote_megaslime
				)
				resp_cont.add_channel_response(ch_name, response)

				enemy.life_state = ewcfg.enemy_lifestate_alive
				enemy.time_lastenter = int(time.time())
				enemy.persist()

			# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
			elif bknd_hunt.check_raidboss_countdown(enemy) == False:
				timer = (enemy.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

				if timer < ewcfg.enemy_attack_tick_length and timer != 0:
					timer = ewcfg.enemy_attack_tick_length

				countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
				resp_cont.add_channel_response(ch_name, countdown_response)

				# TODO: Edit the countdown message instead of deleting and reposting
				last_messages = await resp_cont.post()
				asyncio.ensure_future(
					fe_utils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))
				resp_cont = None
			else:
				district_data = EwDistrict(district=enemy.poi, id_server=enemy.id_server)

				# Look for enemies of the opposing 'class'. If none are found, look for players instead.
				if enemy.enemytype in ewcfg.gvs_enemies_gaiaslimeoids:
					if len(district_data.get_enemies_in_district(classes=[ewcfg.enemy_class_shambler])) > 0:
						await enemy.cannibalize()
				# elif len(district_data.get_players_in_district(life_states = [ewcfg.life_state_shambler])) > 0:
				# 	await enemy.kill()
				elif enemy.enemytype in ewcfg.gvs_enemies_shamblers:
					life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive]

					if enemy.gvs_coord in ewcfg.gvs_coords_end:
						if len(district_data.get_players_in_district(
								life_states=life_states)) > 0 and enemy.gvs_coord in ewcfg.gvs_coords_end:
							await enemy.kill()
						else:
							continue
					else:
						if len(district_data.get_enemies_in_district(classes=[ewcfg.enemy_class_gaiaslimeoid])) > 0:
							await enemy.cannibalize()
						else:
							await sh_move(enemy)
				else:
					continue

			if resp_cont != None:
				await resp_cont.post()


# Finds an enemy based on its regular/shorthand name, or its ID.
def find_enemy(enemy_search=None, user_data=None):
	enemy_found = None
	enemy_search_alias = None

	if enemy_search != None:

		enemy_search_tokens = enemy_search.split(' ')
		enemy_search_tokens_upper = enemy_search.upper().split(' ')

		for enemy_type in ewcfg.enemy_data_table:
			aliases = ewcfg.enemy_data_table[enemy_type]["aliases"]
			if enemy_search.lower() in aliases:
				enemy_search_alias = enemy_type
				break
			if not set(enemy_search_tokens).isdisjoint(set(aliases)):
				enemy_search_alias = enemy_type
				break

		# Check if the identifier letter inputted was a user's captcha. If so, ignore it.
		if user_data.weapon >= 0:
			weapon_item = EwItem(id_item=user_data.weapon)
			weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
			captcha = weapon_item.item_props.get('captcha')

			if weapon != None and ewcfg.weapon_class_captcha in weapon.classes and captcha not in [None,
																								   ""] and captcha in enemy_search_tokens_upper:
				enemy_search_tokens_upper.remove(captcha)

		tokens_set_upper = set(enemy_search_tokens_upper)

		identifiers_found = tokens_set_upper.intersection(set(ewcfg.identifier_letters))
		# coordinates_found = tokens_set_upper.intersection(set(ewcfg.gvs_valid_coords_gaia))

		if len(identifiers_found) > 0:

			# user passed in an identifier for a district specific enemy

			searched_identifier = identifiers_found.pop()

			enemydata = bknd_core.execute_sql_query(
				"SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {identifier} = %s AND {life_state} = 1".format(
					id_enemy=ewcfg.col_id_enemy,
					poi=ewcfg.col_enemy_poi,
					identifier=ewcfg.col_enemy_identifier,
					life_state=ewcfg.col_enemy_life_state
				), (
					user_data.poi,
					searched_identifier,
				))

			for row in enemydata:
				enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
				enemy_found = enemy
				break

		# elif len(coordinates_found) > 0:
		# 	# user passed in a GvS coordinate for a district specific enemy
		#
		# 	searched_coord= coordinates_found.pop()
		#
		# 	enemydata = bknd_core.execute_sql_query(
		# 		"SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {coord} = %s AND {life_state} = 1".format(
		# 			id_enemy=ewcfg.col_id_enemy,
		# 			poi=ewcfg.col_enemy_poi,
		# 			coord=ewcfg.col_enemy_gvs_coord,
		# 			life_state=ewcfg.col_enemy_life_state
		# 		), (
		# 			user_data.poi,
		# 			searched_coord,
		# 		))
		#
		# 	for row in enemydata:
		# 		enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
		# 		enemy_found = enemy
		# 		break
		else:
			# last token was a string, identify enemy by name

			enemydata = bknd_core.execute_sql_query(
				"SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {life_state} = 1".format(
					id_enemy=ewcfg.col_id_enemy,
					poi=ewcfg.col_enemy_poi,
					life_state=ewcfg.col_enemy_life_state
				), (
					user_data.poi,
				))

			# find the first (i.e. the oldest) item that matches the search
			for row in enemydata:
				enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)

				if (enemy.display_name.lower() == enemy_search) or (enemy.enemytype == enemy_search_alias):
					enemy_found = enemy
					break

				if (enemy.display_name.lower() in enemy_search) or (enemy.enemytype in enemy_search_tokens):
					enemy_found = enemy
					break

	return enemy_found


def check_raidboss_movecooldown(enemy_data):
	time_now = int(time.time())

	if enemy_data.enemytype in ewcfg.raid_bosses:
		if enemy_data.enemytype in ewcfg.gvs_enemies:
			if enemy_data.time_lastenter <= time_now - 600:
				# Raid boss can move
				return True
			elif enemy_data.time_lastenter > time_now - 600:
				# Raid boss can't move yet
				return False
		else:
			if enemy_data.time_lastenter <= time_now - ewcfg.time_raidboss_movecooldown:
				# Raid boss can move
				return True
			elif enemy_data.time_lastenter > time_now - ewcfg.time_raidboss_movecooldown:
				# Raid boss can't move yet
				return False


# This function takes care of all win conditions within Gankers Vs. Shamblers.
# It also handles turn counters, including gaiaslime generation, as well as spawning in shamblers
async def gvs_update_gamestate(id_server):
	op_districts = bknd_core.execute_sql_query("SELECT district FROM gvs_ops_choices GROUP BY district")
	for op_district in op_districts:
		district = op_district[0]

		graveyard_ops = bknd_core.execute_sql_query(
			"SELECT id_user, enemytype, shambler_stock FROM gvs_ops_choices WHERE faction = 'shamblers' AND district = '{}' AND shambler_stock > 0".format(
				district))
		bot_garden_ops = bknd_core.execute_sql_query(
			"SELECT id_user, enemytype FROM gvs_ops_choices WHERE faction = 'gankers' AND district = '{}' AND id_user = 56709".format(
				district))
		op_district_data = EwDistrict(district=district, id_server=id_server)

		# Generate Gaiaslime passively over time, but in small amounts
		op_district_data.gaiaslime += 5
		op_district_data.persist()

		victor = None
		time_now = int(time.time())

		op_poi = poi_static.id_to_poi.get(district)
		client = ewutils.get_client()
		server = client.get_guild(id_server)
		channel = fe_utils.get_channel(server, op_poi.channel)

		if len(bot_garden_ops) > 0:
			if random.randrange(25) == 0:

				# random_op = random.choice(bot_garden_ops)
				# random_op_data = EwOperationData(id_user=random_op[0], district=district, enemytype=random_op[1])

				possible_bot_types = [
					ewcfg.enemy_type_gaia_suganmanuts,
					ewcfg.enemy_type_gaia_pinkrowddishes,
					ewcfg.enemy_type_gaia_purplekilliflower,
					ewcfg.enemy_type_gaia_poketubers,
					ewcfg.enemy_type_gaia_razornuts
				]

				possible_bot_coords = [
					'A1', 'A2', 'A3', 'A4', 'A5',
					'B1', 'B2', 'B3', 'B4', 'B5',
					'C1', 'C2', 'C3', 'C4', 'C5',
					'D1', 'D2', 'D3', 'D4', 'D5',
					'E1', 'E2', 'E3', 'E4', 'E5'
				]

				for i in range(5):
					chosen_type = random.choice(possible_bot_types)
					chosen_coord = random.choice(possible_bot_coords)

					existing_gaias = gvs_get_gaias_from_coord(district, chosen_coord)

					# If the coordinate is completely empty, spawn a gaiaslimeoid there.
					# Otherwise, make up to 5 attempts when choosing random coordinates
					if len(existing_gaias) == 0:
						resp_cont = spawn_enemy(
							id_server=id_server,
							pre_chosen_type=chosen_type,
							pre_chosen_level=50,
							pre_chosen_poi=district,
							pre_chosen_identifier='',
							pre_chosen_faction=ewcfg.psuedo_faction_gankers,
							pre_chosen_owner=56709,
							pre_chosen_coord=chosen_coord,
							manual_spawn=True,
						)
						await resp_cont.post()

						break

		if len(graveyard_ops) > 0:

			# The chance for a shambler to spawn is inversely proportional to the amount of shamblers left in stock
			# The less shamblers there are left, the more likely they are to spawn
			current_stock = 0
			full_stock = 0

			for op in graveyard_ops:
				current_stock += op[2]
				full_stock += static_items.tombstone_fullstock_map[op[1]]

			# Example: If full_stock is 50, and current_stock is 20, then the spawn chance is 70%
			# ((1 - (20 / 50)) * 100) + 10 = 70

			shambler_spawn_chance = int(((1 - (current_stock / full_stock)) * 100) + 10)
			if random.randrange(100) + 1 < shambler_spawn_chance:

				random_op = random.choice(graveyard_ops)
				random_op_data = EwOperationData(id_user=random_op[0], district=district, enemytype=random_op[1])

				# Don't spawn if there aren't available identifiers
				if len(op_district_data.get_enemies_in_district(classes=[ewcfg.enemy_class_shambler])) < 26:
					resp_cont = spawn_enemy(
						id_server=id_server,
						pre_chosen_type=random_op_data.enemytype,
						pre_chosen_level=50,
						pre_chosen_poi=district,
						pre_chosen_faction=ewcfg.psuedo_faction_shamblers,
						pre_chosen_owner=random_op_data.id_user,
						pre_chosen_coord=random.choice(ewcfg.gvs_coords_start),
						manual_spawn=True
					)

					random_op_data.shambler_stock -= 1
					random_op_data.persist()

					if random_op_data.shambler_stock == 0:
						breakdown_response = "The tombstone spawning in {}s breaks down and collapses!".format(
							random_op_data.enemytype.capitalize())
						resp_cont.add_channel_response(channel, breakdown_response)
					else:
						random_op_data.persist()

					await resp_cont.post()
		else:
			shamblers = bknd_core.execute_sql_query(
				"SELECT id_enemy FROM enemies WHERE enemyclass = '{}' AND poi = '{}'".format(ewcfg.enemy_class_shambler,
																							 district))
			if len(shamblers) == 0:
				# No more stocked tombstones, and no more enemy shamblers. Garden Gankers win!
				victor = ewcfg.psuedo_faction_gankers

		op_juvies = bknd_core.execute_sql_query(
			"SELECT id_user FROM gvs_ops_choices WHERE faction = 'gankers' AND district = '{}' AND id_user != 56709 GROUP BY id_user".format(
				district))

		# No more Garden Gankers left. Shamblers win?
		if len(op_juvies) == 0:

			# Check if the shamblers are fighting against the bot.
			# If they are, they can only win if at least one shambler has reached the back.
			if len(bot_garden_ops) > 0:
				back_shamblers = bknd_core.execute_sql_query(
					"SELECT id_enemy FROM enemies WHERE gvs_coord IN {}".format(tuple(ewcfg.gvs_coords_end)))
				if len(back_shamblers) > 0:
					# Shambler reached the back while no juveniles were around to help the bot. Shamblers win!
					victor = ewcfg.psuedo_faction_shamblers
			else:
				# No juveniles left in the district, and there were no bot operations. Shamblers win!
				victor = ewcfg.psuedo_faction_shamblers

		all_garden_ops = bknd_core.execute_sql_query(
			"SELECT id_user FROM gvs_ops_choices WHERE faction = 'gankers' AND district = '{}'".format(district))
		# No garden ops at all. Shamblers win!
		if len(all_garden_ops) == 0:
			victor = ewcfg.psuedo_faction_shamblers

		if victor != None:
			if victor == ewcfg.psuedo_faction_gankers:
				response = "***All tombstones have been emptied out! The Garden Gankers take victory!\nThe district is rejuvenated completely!!***"

				for juvie in op_juvies:
					ewutils.active_restrictions[juvie[0]] = 0

				op_district_data.gaiaslime = 0
				op_district_data.degradation = 0
				op_district_data.time_unlock = time_now + 3600
				op_district_data.persist()
			else:
				response = "***The shamblers have eaten the brainz of the Garden Gankers and take control of the district!\nIt's shambled completely!!***"
				op_district_data.gaiaslime = 0
				op_district_data.degradation = ewcfg.district_max_degradation
				op_district_data.time_unlock = time_now + 3600
				op_district_data.persist()

			bknd_core.execute_sql_query("DELETE FROM gvs_ops_choices WHERE district = '{}'".format(district))
			await delete_all_enemies(cmd=None, query_suffix="AND poi = '{}'".format(district), id_server_sent=id_server)
			return await fe_utils.send_message(client, channel, response)


# Certain conditions may prevent a shambler from acting.
def check_enemy_can_act(enemy_data):
	enemy_props = enemy_data.enemy_props

	turn_countdown = enemy_props.get('turncountdown')
	dank_countdown = enemy_props.get('dankcountdown')
	sludge_countdown = enemy_props.get('sludgecountdown')
	hardened_sludge_countdown = enemy_props.get('hardsludgecountdown')

	waiting = False
	stoned = False
	sludged = False
	hardened = False

	if turn_countdown != None:
		if int(turn_countdown) > 0:
			waiting = True
			enemy_props['turncountdown'] -= 1
		else:
			waiting = False

	if dank_countdown != None:
		if int(dank_countdown) > 0:
			# If the countdown number is even, they can act. Otherwise, they cannot.
			if dank_countdown % 2 == 0:
				stoned = False
			else:
				stoned = True

			enemy_props['dankcountdown'] -= 1
		else:
			stoned = False

	# Regular sludge only slows a shambler down every other turn. Hardened sludge immobilizes them completely.
	if sludge_countdown != None:
		if int(sludge_countdown) > 0:
			# If the countdown number is even, they can act. Otherwise, they cannot.
			if sludge_countdown % 2 == 0:
				sludged = False
			else:
				sludged = True

			enemy_props['sludgecountdown'] -= 1
		else:
			sludged = False

	if hardened_sludge_countdown != None:
		if int(hardened_sludge_countdown) > 0:
			hardened = True
			enemy_props['hardsludgecountdown'] -= 1
		else:
			hardened = False

	enemy_data.persist()

	if not waiting and not stoned and not sludged and not hardened:
		return True
	else:
		return False


def handle_turn_timers(enemy_data):
	response = ""

	# Handle specific turn counters of all GvS enemies.
	if enemy_data.enemytype == ewcfg.enemy_type_gaia_brightshade:
		countdown = enemy_data.enemy_props.get('gaiaslimecountdown')

		if countdown != None:
			int_countdown = int(countdown)

			if int_countdown == 0:

				gaiaslime_amount = 0

				enemy_data.enemy_props['gaiaslimecountdown'] = 2
				district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)

				if enemy_data.enemy_props.get('joybean') != None:
					if enemy_data.enemy_props.get('joybean') == 'true':
						gaiaslime_amount = 50
					else:
						gaiaslime_amount = 25
				else:
					gaiaslime_amount = 25

				district_data.gaiaslime += gaiaslime_amount
				district_data.persist()

				response = "{} ({}) produced {} gaiaslime!".format(enemy_data.display_name, enemy_data.gvs_coord,
																   gaiaslime_amount)

			else:
				enemy_data.enemy_props['gaiaslimecountdown'] = int_countdown - 1

			enemy_data.persist()
			return response

	elif enemy_data.enemytype == ewcfg.enemy_type_gaia_poketubers:

		countdown = enemy_data.enemy_props.get('primecountdown')

		if countdown != None:
			int_countdown = int(countdown)

			if enemy_data.enemy_props.get('primed') != 'true':

				if int_countdown == 0:
					enemy_data.enemy_props['primed'] = 'true'

					response = "{} ({}) is primed and ready.".format(enemy_data.display_name, enemy_data.gvs_coord)

				else:
					enemy_data.enemy_props['primecountdown'] = int_countdown - 1

				enemy_data.persist()
				return response


async def delete_all_enemies(cmd=None, query_suffix="", id_server_sent=""):
	if cmd != None:
		author = cmd.message.author

		if not author.guild_permissions.administrator:
			return

		id_server = cmd.message.guild.id

		bknd_core.execute_sql_query("DELETE FROM enemies WHERE id_server = {id_server}".format(
			id_server=id_server
		))

		ewutils.logMsg("Deleted all enemies from database connected to server {}".format(id_server))

	else:
		id_server = id_server_sent

		bknd_core.execute_sql_query("DELETE FROM enemies WHERE id_server = {} {}".format(
			id_server,
			query_suffix
		))

		ewutils.logMsg(
			"Deleted all enemies from database connected to server {}. Query suffix was '{}'".format(id_server,
																									 query_suffix))

async def sh_move(enemy_data):
	current_coord = enemy_data.gvs_coord
	has_moved = False
	index = None
	row = None
	new_coord = None

	if current_coord in ewcfg.gvs_coords_start and enemy_data.enemytype == ewcfg.enemy_type_juvieshambler:
		bknd_hunt.delete_enemy(enemy_data)

	if current_coord not in ewcfg.gvs_coords_end:
		for row in ewcfg.gvs_valid_coords_shambler:

			if current_coord in row:
				index = row.index(current_coord)
				new_coord = row[index - 1]
				# print(new_coord)
				break

		if new_coord == None:
			return

		enemy_data.gvs_coord = new_coord
		enemy_data.persist()

		for gaia_row in ewcfg.gvs_valid_coords_gaia:
			if new_coord in gaia_row and index != None and row != None:
				poi_channel = poi_static.id_to_poi.get(enemy_data.poi).channel

				try:
					previous_gaia_coord = row[index - 2]
				except:
					break

				response = "The {} moved from {} to {}!".format(enemy_data.display_name, new_coord, previous_gaia_coord)
				client = ewutils.get_client()
				server = client.get_guild(enemy_data.id_server)
				channel = fe_utils.get_channel(server, poi_channel)

				await fe_utils.send_message(client, channel, response)

	# print('shambler moved from {} to {} in {}.'.format(current_coord, new_coord, enemy_data.poi))

	return has_moved

# Selects which non-ghost user to attack based on certain parameters.
def get_target_by_ai(enemy_data, cannibalize=False):
	target_data = None
	group_attack = False

	time_now = int(time.time())

	# If a player's time_lastenter is less than this value, it can be attacked.
	targettimer = time_now - ewcfg.time_enemyaggro
	raidbossaggrotimer = time_now - ewcfg.time_raidbossaggro

	if not cannibalize:
		if enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != -1:
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server, data_level=1)

		elif enemy_data.ai == ewcfg.enemy_ai_attacker_a:
			users = bknd_core.execute_sql_query(
				# "SELECT {id_user}, {life_state}, {time_lastenter} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({level} > {safe_level} OR {life_state} != {life_state_juvenile}) AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {time_lastenter} ASC".format(
				"SELECT {id_user}, {life_state}, {time_lastenter} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({life_state} != {life_state_juvenile}) AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {time_lastenter} ASC".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					time_lastenter=ewcfg.col_time_lastenter,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					targettimer=targettimer,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
					life_state_juvenile=ewcfg.life_state_juvenile,
					repel_status=ewcfg.status_repelled_id,
					slimes=ewcfg.col_slimes,
					# safe_level = ewcfg.max_safe_level,
					level=ewcfg.col_slimelevel
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level=1)

		elif enemy_data.ai == ewcfg.enemy_ai_attacker_b:
			users = bknd_core.execute_sql_query(
				# "SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({level} > {safe_level} OR {life_state} != {life_state_juvenile}) AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {slimes} DESC".format(
				"SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({life_state} != {life_state_juvenile}) AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {slimes} DESC".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					slimes=ewcfg.col_slimes,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					time_lastenter=ewcfg.col_time_lastenter,
					targettimer=targettimer,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
					life_state_juvenile=ewcfg.life_state_juvenile,
					repel_status=ewcfg.status_repelled_id,
					# safe_level = ewcfg.max_safe_level,
					level=ewcfg.col_slimelevel
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level=1)

		elif enemy_data.ai == ewcfg.enemy_ai_gaiaslimeoid:

			users = bknd_core.execute_sql_query(
				"SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({life_state} = {life_state_shambler}) ORDER BY {slimes} DESC".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					slimes=ewcfg.col_slimes,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					time_lastenter=ewcfg.col_time_lastenter,
					targettimer=targettimer,
					life_state_shambler=ewcfg.life_state_shambler,
					time_now=time_now,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level=1)

		elif enemy_data.ai == ewcfg.enemy_ai_shambler:

			users = bknd_core.execute_sql_query(
				"SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND NOT ({life_state} = {life_state_shambler} OR {life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin}) ORDER BY {slimes} DESC".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					slimes=ewcfg.col_slimes,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					time_lastenter=ewcfg.col_time_lastenter,
					targettimer=targettimer,
					life_state_shambler=ewcfg.life_state_shambler,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level=1)

		# If an enemy is a raidboss, don't let it attack until some time has passed when entering a new district.
		if enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.time_lastenter > raidbossaggrotimer:
			target_data = None

	elif cannibalize:
		if enemy_data.ai == ewcfg.enemy_ai_gaiaslimeoid:

			range = 1 if enemy_data.enemy_props.get('range') == None else int(enemy_data.enemy_props.get('range'))
			direction = 'right' if enemy_data.enemy_props.get('direction') == None else enemy_data.enemy_props.get(
				'direction')
			piercing = 'false' if enemy_data.enemy_props.get('piercing') == None else enemy_data.enemy_props.get(
				'piercing')
			splash = 'false' if enemy_data.enemy_props.get('splash') == None else enemy_data.enemy_props.get('splash')
			pierceamount = '0' if enemy_data.enemy_props.get('pierceamount') == None else enemy_data.enemy_props.get(
				'pierceamount')
			singletilepierce = 'false' if enemy_data.enemy_props.get(
				'singletilepierce') == None else enemy_data.enemy_props.get('singletilepierce')

			enemies = bknd_hunt.ga_check_coord_for_shambler(enemy_data, range, direction, piercing, splash, pierceamount,
												  singletilepierce)
			if len(enemies) > 1:
				group_attack = True

			target_data = enemies

		elif enemy_data.ai == ewcfg.enemy_ai_shambler:
			range = 1 if enemy_data.enemy_props.get('range') == None else int(enemy_data.enemy_props.get('range'))
			direction = 'left' if enemy_data.enemy_props.get('direction') == None else enemy_data.enemy_props.get(
				'direction')

			enemies = bknd_hunt.sh_check_coord_for_gaia(enemy_data, range, direction)
			if len(enemies) > 0:
				target_data = EwEnemyBase(id_enemy=enemies[0], id_server=enemy_data.id_server)

		# If an enemy is a raidboss, don't let it attack until some time has passed when entering a new district.
		if enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.time_lastenter > raidbossaggrotimer:
			target_data = None

	return target_data, group_attack


