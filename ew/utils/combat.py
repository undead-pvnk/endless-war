import asyncio
import math
import random
import time

from . import core as ewutils
from . import frontend as fe_utils
from . import hunting as hunt_utils
from . import item as itm_utils
from . import rolemgr as ewrolemgr
from . import stats as ewstats
from .district import EwDistrict
from .frontend import EwResponseContainer
from .user import get_move_speed
from ..backend import core as bknd_core
from ..backend import hunting as bknd_hunt
from ..backend import item as bknd_item
from ..backend import status as bknd_status
from ..backend.hunting import EwEnemyBase
from ..backend.item import EwItem
from ..backend.market import EwMarket
from ..backend.player import EwPlayer
from ..backend.slimeoid import EwSlimeoidBase as EwSlimeoid
from ..backend.status import EwEnemyStatusEffect
from ..backend.status import EwStatusEffect
from ..backend.user import EwUserBase
from ..model.hunting import EwEnemyEffectContainer
from ..static import cfg as ewcfg
from ..static import cosmetics as static_cosmetics
from ..static import food as static_food
from ..static import hunting as hunt_static
from ..static import items as static_items
from ..static import mutations as static_mutations
from ..static import poi as poi_static
from ..static import slimeoid as sl_static
from ..static import status as se_static
from ..static import weapons as static_weapons

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
            hitzone = get_hitzone()
            randombodypart = hitzone.name
            if random.random() < 0.5:
                randombodypart = random.choice(hitzone.aliases)

            shooter_status_mods = get_shooter_status_mods(enemy_data, target_data, hitzone)
            shootee_status_mods = get_shootee_status_mods(target_data, enemy_data, hitzone)

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
                    slimes_damage *= damage_mod_defend(
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
                return await hunt_utils.sh_move(enemy_data)
            elif enemy_data.enemytype == ewcfg.enemy_type_dinoshambler:
                if target_enemy.enemytype == ewcfg.enemy_type_gaia_suganmanuts and enemy_data.enemy_props.get(
                        'jumping') == 'true':
                    enemy_data.enemy_props['jumping'] = 'false'
                else:
                    return await hunt_utils.sh_move(enemy_data)

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

                        gaias_in_coord = hunt_utils.gvs_get_gaias_from_coord(enemy_data.poi, new_coord)

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
            all_destinations = set(destinations)

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
            for destination in all_destinations:

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

    def change_slimes(self, n = 0, source = None):
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

    def applyStatus(self, id_status = None, value = 0, source = "", multiplier = 1, id_target = -1):
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

    def clear_status(self, id_status = None):
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


""" Damage all players in a district """


def explode(damage = 0, district_data = None, market_data = None):
    id_server = district_data.id_server
    poi = district_data.name

    if market_data == None:
        market_data = EwMarket(id_server=district_data.id_server)

    client = ewutils.get_client()
    server = client.get_guild(id_server)

    resp_cont = EwResponseContainer(id_server=id_server)
    response = ""
    channel = poi_static.id_to_poi.get(poi).channel

    life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive,
                   ewcfg.life_state_shambler]
    users = district_data.get_players_in_district(life_states=life_states, pvp_only=True)

    enemies = district_data.get_enemies_in_district()

    # damage players
    for user in users:
        user_data = EwUser(id_user=user, id_server=id_server, data_level=1)
        mutations = user_data.get_mutations()

        user_weapon = None
        user_weapon_item = None
        if user_data.weapon >= 0:
            user_weapon_item = EwItem(id_item=user_data.weapon)
            user_weapon = static_weapons.weapon_map.get(user_weapon_item.item_props.get("weapon_type"))

        # apply defensive mods
        slimes_damage_target = damage * damage_mod_defend(
            shootee_data=user_data,
            shootee_mutations=mutations,
            shootee_weapon=user_weapon,
            market_data=market_data
        )

        # apply sap armor
        # sap_armor = ewwep.get_sap_armor(shootee_data = user_data, sap_ignored = 0)
        # slimes_damage_target *= sap_armor
        # slimes_damage_target = int(max(0, slimes_damage_target))

        # apply fashion armor

        # disabled until held items update
        # fashion_armor = ewwep.get_fashion_armor(shootee_data = user_data)
        # slimes_damage_target *= fashion_armor
        slimes_damage_target = int(max(0, slimes_damage_target))

        player_data = EwPlayer(id_user=user_data.id_user)
        response = "{} is blown back by the explosion’s sheer force! They lose {:,} slime!!".format(
            player_data.display_name, slimes_damage_target)
        resp_cont.add_channel_response(channel, response)
        slimes_damage = slimes_damage_target
        if user_data.slimes < slimes_damage + user_data.bleed_storage:
            # die in the explosion
            district_data.change_slimes(n=user_data.slimes, source=ewcfg.source_killing)
            district_data.persist()
            slimes_dropped = user_data.totaldamage + user_data.slimes

            user_data.trauma = ewcfg.trauma_id_environment
            user_data.die(cause=ewcfg.cause_killing)
            # user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
            user_data.persist()

            response = "Alas, {} was caught too close to the blast. They are consumed by the flames, and die in the explosion.".format(
                player_data.display_name)
            resp_cont.add_channel_response(channel, response)

            resp_cont.add_member_to_update(server.get_member(user_data.id_user))
        else:
            # survive
            slime_splatter = 0.5 * slimes_damage
            district_data.change_slimes(n=slime_splatter, source=ewcfg.source_killing)
            district_data.persist()
            slimes_damage -= slime_splatter
            user_data.bleed_storage += slimes_damage
            user_data.change_slimes(n=-slime_splatter, source=ewcfg.source_killing)
            user_data.persist()

    # damage enemies
    for enemy in enemies:
        enemy_data = EwEnemy(id_enemy=enemy, id_server=id_server)

        response = "{} is blown back by the explosion’s sheer force! They lose {:,} slime!!".format(
            enemy_data.display_name, damage)
        resp_cont.add_channel_response(channel, response)

        slimes_damage_target = damage

        # apply sap armor
        # sap_armor = ewwep.get_sap_armor(shootee_data = enemy_data, sap_ignored = 0)
        # slimes_damage_target *= sap_armor
        # slimes_damage_target = int(max(0, slimes_damage_target))

        slimes_damage = slimes_damage_target
        if enemy_data.slimes < slimes_damage + enemy_data.bleed_storage:
            # die in the explosion
            district_data.change_slimes(n=enemy_data.slimes, source=ewcfg.source_killing)
            district_data.persist()
            # slimes_dropped = enemy_data.totaldamage + enemy_data.slimes
            # explode_damage = ewutils.slime_bylevel(enemy_data.level)

            response = "Alas, {} was caught too close to the blast. They are consumed by the flames, and die in the explosion.".format(
                enemy_data.display_name)
            resp_cont.add_response_container(drop_enemy_loot(enemy_data, district_data))
            resp_cont.add_channel_response(channel, response)

            enemy_data.life_state = ewcfg.enemy_lifestate_dead
            enemy_data.persist()

        else:
            # survive
            slime_splatter = 0.5 * slimes_damage
            district_data.change_slimes(n=slime_splatter, source=ewcfg.source_killing)
            district_data.persist()
            slimes_damage -= slime_splatter
            enemy_data.bleed_storage += slimes_damage
            enemy_data.change_slimes(n=-slime_splatter, source=ewcfg.source_killing)
            enemy_data.persist()
    return resp_cont


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
                status_data = EwStatusEffect(id_status=status, user_data=user_data)
            else:
                status_data = EwEnemyStatusEffect(id_status=status, enemy_data=user_data)

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
                status_data = EwStatusEffect(id_status=status, user_data=user_data)
            else:
                status_data = EwEnemyStatusEffect(id_status=status, enemy_data=user_data)

            if status_data.id_target != -1:
                if shooter_data.id_user != status_data.id_target:
                    continue

        if status_flavor is not None:
            mods['hit_chance'] += status_flavor.hit_chance_mod
            mods['crit'] += status_flavor.crit_mod
            mods['dmg'] += status_flavor.dmg_mod

    # apply trauma mods
    # if user_data.combatant_type == 'player':
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
            min_level=math.ceil((1 / 10) ** 0.25 * user_data.slimelevel),
            life_states=[ewcfg.life_state_enlisted],
            factions=[user_data.faction]
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
            min_level=math.ceil((1 / 10) ** 0.25 * user_data.slimelevel),
            life_states=[ewcfg.life_state_enlisted],
            factions=[user_data.faction]
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
    except:  # If shootee_data doesn't have defense, aka it's a monster
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
                        await resp_cont.post(delete_after=120)

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
        if not hunt_utils.check_enemy_can_act(enemy):
            continue

        # Go through turn counters unrelated to the prevention of acting on that turn.
        turn_timer_response = hunt_utils.handle_turn_timers(enemy)
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
                    await resp_cont.post(delete_after=120)

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
                            await hunt_utils.sh_move(enemy)
                else:
                    continue

            if resp_cont != None:
                await resp_cont.post()


# Finds an enemy based on its regular/shorthand name, or its ID.
def find_enemy(enemy_search = None, user_data = None):
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


# Selects which non-ghost user to attack based on certain parameters.
def get_target_by_ai(enemy_data, cannibalize = False):
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
                "SELECT {id_user}, {life_state}, {time_lastenter} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {time_lastenter} ASC".format(
                    id_user=ewcfg.col_id_user,
                    life_state=ewcfg.col_life_state,
                    time_lastenter=ewcfg.col_time_lastenter,
                    poi=ewcfg.col_poi,
                    id_server=ewcfg.col_id_server,
                    targettimer=targettimer,
                    life_state_corpse=ewcfg.life_state_corpse,
                    life_state_kingpin=ewcfg.life_state_kingpin,
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
                "SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {slimes} DESC".format(
                    id_user=ewcfg.col_id_user,
                    life_state=ewcfg.col_life_state,
                    slimes=ewcfg.col_slimes,
                    poi=ewcfg.col_poi,
                    id_server=ewcfg.col_id_server,
                    time_lastenter=ewcfg.col_time_lastenter,
                    targettimer=targettimer,
                    life_state_corpse=ewcfg.life_state_corpse,
                    life_state_kingpin=ewcfg.life_state_kingpin,
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


""" User model for database persistence """


class EwUser(EwUserBase):
    weaponskill = 0

    attack = 0
    defense = 0
    speed = 0
    freshness = 0

    def __init__(self, ew_id = None, member = None, id_user = None, id_server = None, data_level = 0):
        super().__init__(ew_id, member, id_user, id_server)

        self.weaponskill = bknd_item.get_weaponskill(self)

        if data_level > 0:
            result = self.get_fashion_stats()
            self.attack = result[0]
            self.defense = result[1]
            self.speed = result[2]

            if data_level > 1:
                self.freshness = self.get_freshness()

            self.move_speed = get_move_speed(self)

        self.limit_fix()

    """ gain or lose slime, recording statistics and potentially leveling up. """

    def change_slimes(self, n = 0, source = None):
        change = int(n)
        self.slimes += change
        # if self.life_state == ewcfg.life_state_juvenile:
        #
        #	if self.juviemode == 1 and self.slimes > ewcfg.max_safe_slime:
        #		self.slimes = ewcfg.max_safe_slime

        response = ""

        if n >= 0:
            ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimes, n=change)
            ewstats.track_maximum(user=self, metric=ewcfg.stat_max_slimes, value=self.slimes)

            if source == ewcfg.source_mining:
                ewstats.change_stat(user=self, metric=ewcfg.stat_slimesmined, n=change)
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimesmined, n=change)

            if source == ewcfg.source_killing:
                ewstats.change_stat(user=self, metric=ewcfg.stat_slimesfromkills, n=change)
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimesfromkills, n=change)

            if source == ewcfg.source_farming:
                ewstats.change_stat(user=self, metric=ewcfg.stat_slimesfarmed, n=change)
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimesfarmed, n=change)

            if source == ewcfg.source_scavenging:
                ewstats.change_stat(user=self, metric=ewcfg.stat_slimesscavenged, n=change)
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimesscavenged, n=change)

        else:
            change *= -1  # convert to positive number
            if source != ewcfg.source_spending and source != ewcfg.source_ghostification:
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimeloss, n=change)

            if source == ewcfg.source_damage or source == ewcfg.source_bleeding:
                self.totaldamage += change
                ewstats.track_maximum(user=self, metric=ewcfg.stat_max_hitsurvived, value=change)

            if source == ewcfg.source_self_damage:
                self.totaldamage += change
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_selfdamage, n=change)

            if source == ewcfg.source_decay:
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimesdecayed, n=change)

            if source == ewcfg.source_haunter:
                ewstats.track_maximum(user=self, metric=ewcfg.stat_max_hauntinflicted, value=change)
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimeshaunted, n=change)

        # potentially level up
        new_level = ewutils.level_byslime(self.slimes)
        if new_level > self.slimelevel:
            if self.life_state != ewcfg.life_state_corpse:
                response += "You have been empowered by slime and are now a level {} slimeboi.".format(new_level)
            for level in range(self.slimelevel + 1, new_level + 1):
                current_mutations = self.get_mutations()
                if (level >= self.get_mutation_level() + self.get_mutation_next_level()) and (self.life_state not in [ewcfg.life_state_corpse, ewcfg.life_state_shambler]) and (self.get_mutation_level() < 50):

                    new_mutation = self.get_mutation_next()

                    add_success = self.add_mutation(new_mutation)
                    if add_success:
                        response += "\n\nWhat’s this? You are mutating!! {}".format(static_mutations.mutations_map[new_mutation].str_acquire)

            self.slimelevel = new_level
            if self.life_state == ewcfg.life_state_corpse:
                ewstats.track_maximum(user=self, metric=ewcfg.stat_max_ghost_level, value=self.slimelevel)
            else:
                ewstats.track_maximum(user=self, metric=ewcfg.stat_max_level, value=self.slimelevel)

        return response

    def die(self, cause = None):

        time_now = int(time.time())

        ewutils.end_trade(self.id_user)

        resp_cont = EwResponseContainer(id_server=self.id_server)

        client = ewcfg.get_client()
        server = client.get_guild(self.id_server)

        deathreport = ''

        # remove ghosts inhabiting player
        self.remove_inhabitation()

        # Make The death report
        deathreport = fe_utils.create_death_report(cause=cause, user_data=self)
        resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)

        poi = poi_static.id_to_poi.get(self.poi)
        if cause == ewcfg.cause_weather:
            resp_cont.add_channel_response(poi.channel, deathreport)

        status = self.getStatusEffects()
        if "n1" in status:
            self.change_slimes(n=-self.slimes, source=ewcfg.source_killing)
            return (resp_cont)

        # Grab necessary data for spontaneous combustion before stat reset
        explosion_block_list = [ewcfg.cause_leftserver, ewcfg.cause_cliff]
        user_hasCombustion = False
        if (cause not in explosion_block_list) and (poi.pvp):
            if ewcfg.mutation_id_spontaneouscombustion in self.get_mutations():
                user_hasCombustion = True
                explode_damage = ewutils.slime_bylevel(self.slimelevel) / 5
                explode_district = EwDistrict(district=self.poi, id_server=self.id_server)
                explode_poi_channel = poi_static.id_to_poi.get(self.poi).channel

        if self.life_state == ewcfg.life_state_corpse:
            self.busted = True
            self.poi = ewcfg.poi_id_thesewers
        # self.slimes = int(self.slimes * 0.9)
        else:
            if cause != ewcfg.cause_suicide or self.slimelevel > 10:
                self.rand_seed = random.randrange(500000)

            if ewcfg.mutation_id_rigormortis in self.get_mutations():
                rigor = True
            else:
                rigor = False

            self.busted = False  # reset busted state on normal death; potentially move this to ewspooky.revive
            self.slimes = 0
            self.slimelevel = 1
            self.clear_mutations()
            self.clear_allstatuses()
            self.totaldamage = 0
            self.bleed_storage = 0
            self.hunger = 0
            self.inebriation = 0
            self.bounty = 0
            self.time_lastdeath = time_now

            # if self.life_state == ewcfg.life_state_shambler:
            # 	self.degradation += 1
            # else:
            # 	self.degradation += 5

            ewstats.increment_stat(user=self, metric=ewcfg.stat_lifetime_deaths)
            ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimeloss, n=self.slimes)

            if cause == ewcfg.cause_cliff:
                pass
            else:
                if self.life_state == ewcfg.life_state_juvenile:  # If you were a Juvenile.
                    item_fraction = 4
                    food_fraction = 4
                    cosmetic_fraction = 4

                    # Remove them from Garden Ops where applicable
                    bknd_core.execute_sql_query("DELETE FROM gvs_ops_choices WHERE id_user = {}".format(self.id_user))

                else:  # If you were a Gangster.
                    item_fraction = 2
                    food_fraction = 2
                    cosmetic_fraction = 2

                itm_utils.item_dropsome(id_server=self.id_server, id_user=self.id_user, item_type_filter=ewcfg.it_item, fraction=item_fraction, rigor=rigor)  # Drop a random fraction of your items on the ground.
                itm_utils.item_dropsome(id_server=self.id_server, id_user=self.id_user, item_type_filter=ewcfg.it_food, fraction=food_fraction, rigor=rigor)  # Drop a random fraction of your food on the ground.

                itm_utils.item_dropsome(id_server=self.id_server, id_user=self.id_user, item_type_filter=ewcfg.it_cosmetic, fraction=cosmetic_fraction, rigor=rigor)  # Drop a random fraction of your unadorned cosmetics on the ground.
                # bknd_item.item_dedorn_cosmetics(id_server=self.id_server, id_user=self.id_user)  # Unadorn all of your adorned hats.

                itm_utils.item_dropsome(id_server=self.id_server, id_user=self.id_user, item_type_filter=ewcfg.it_weapon, fraction=1, rigor=rigor)  # Drop random fraction of your unequipped weapons on the ground.
                ewutils.weaponskills_clear(id_server=self.id_server, id_user=self.id_user, weaponskill=ewcfg.weaponskill_max_onrevive)

            try:
                item_cache = bknd_core.get_cache(obj_type = "EwItem")
                if item_cache is not False:
                    tgt_itms = item_cache.find_entries(criteria={"item_props": {"preserved": self.id_user}})
                    for itm_dat in tgt_itms:
                        itm_dat.get("item_props").pop("preserved")
                        item_cache.set_entry(data=itm_dat)

                bknd_core.execute_sql_query(
                    "DELETE FROM items_prop WHERE {} = %s AND  {} = %s".format(
                        ewcfg.col_name,
                        ewcfg.col_value
                    ),
                    (
                        'preserved',
                        self.id_user
                    ))

            except:
                ewutils.logMsg('Failed to remove preserved tags from items.')

            self.life_state = ewcfg.life_state_corpse
            self.poi_death = self.poi
            self.poi = ewcfg.poi_id_thesewers
            self.weapon = -1
            self.sidearm = -1
            self.time_expirpvp = 0

        if cause == ewcfg.cause_killing_enemy:  # If your killer was an Enemy. Duh.
            ewstats.increment_stat(user=self, metric=ewcfg.stat_lifetime_pve_deaths)

        if cause == ewcfg.cause_leftserver:
            bknd_item.item_dropall(self)

        # self.sap = 0
        # self.hardened_sap = 0
        self.attack = 0
        self.defense = 0
        self.speed = 0

        ewutils.moves_active[self.id_user] = 0
        ewutils.active_target_map[self.id_user] = ""
        ewutils.active_restrictions[self.id_user] = 0
        ewstats.clear_on_death(id_server=self.id_server, id_user=self.id_user)

        self.persist()

        if cause not in explosion_block_list:  # Run explosion after location/stat reset, to prevent looping onto self
            if user_hasCombustion:
                explode_resp = "\n{} spontaneously combusts, horribly dying in a fiery explosion of slime and shrapnel!! Oh, the humanity!\n".format(server.get_member(self.id_user).display_name)
                ewutils.logMsg("")
                resp_cont.add_channel_response(explode_poi_channel, explode_resp)

                explosion = explode(damage=explode_damage, district_data=explode_district)
                resp_cont.add_response_container(explosion)

        # bknd_item.item_destroyall(id_server = self.id_server, id_user = self.id_user)

        ewutils.logMsg('server {}: {} was killed by {} - cause was {}'.format(self.id_server, self.id_user, self.id_killer, cause))

        return (resp_cont)

    def add_bounty(self, n = 0):
        self.bounty += int(n)
        ewstats.track_maximum(user=self, metric=ewcfg.stat_max_bounty, value=self.bounty)

    def change_slimecoin(self, n = 0, coinsource = None):
        change = int(n)
        self.slimecoin += change

        if change >= 0:
            ewstats.track_maximum(user=self, metric=ewcfg.stat_max_slimecoin, value=self.slimecoin)
            ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_slimecoin, n=change)
            if coinsource == ewcfg.coinsource_bounty:
                ewstats.change_stat(user=self, metric=ewcfg.stat_bounty_collected, n=change)
            if coinsource == ewcfg.coinsource_casino:
                ewstats.track_maximum(user=self, metric=ewcfg.stat_biggest_casino_win, value=change)
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_casino_winnings, n=change)
            if coinsource == ewcfg.coinsource_withdraw:
                ewstats.change_stat(user=self, metric=ewcfg.stat_total_slimecoin_withdrawn, n=change)
            if coinsource == ewcfg.coinsource_recycle:
                ewstats.change_stat(user=self, metric=ewcfg.stat_total_slimecoin_from_recycling, n=change)
        else:
            change *= -1
            if coinsource == ewcfg.coinsource_revival:
                ewstats.change_stat(user=self, metric=ewcfg.stat_slimecoin_spent_on_revives, n=change)
            if coinsource == ewcfg.coinsource_casino:
                ewstats.track_maximum(user=self, metric=ewcfg.stat_biggest_casino_loss, value=change)
                ewstats.change_stat(user=self, metric=ewcfg.stat_lifetime_casino_losses, n=change)
            if coinsource == ewcfg.coinsource_invest:
                ewstats.change_stat(user=self, metric=ewcfg.stat_total_slimecoin_invested, n=change)
            if coinsource == ewcfg.coinsource_swearjar:
                ewstats.change_stat(user=self, metric=ewcfg.stat_total_slimecoin_from_swearing, n=change)
            if coinsource == ewcfg.coinsource_salary:
                ewstats.change_stat(user=self, metric=ewcfg.stat_total_slimecoin_from_salary, n=change)

    def add_weaponskill(self, n = 0, weapon_type = None):
        # Save the current weapon's skill
        if self.weapon != None and self.weapon >= 0:
            if self.weaponskill == None:
                self.weaponskill = 0

            self.weaponskill += int(n)
            ewstats.track_maximum(user=self, metric=ewcfg.stat_max_wepskill, value=self.weaponskill)

            weapon = static_weapons.weapon_map.get(weapon_type)
            if ewcfg.weapon_class_paint in weapon.classes and self.weaponskill > 16:
                self.weaponskill = 16

            ewutils.weaponskills_set(
                id_server=self.id_server,
                id_user=self.id_user,
                weapon=weapon_type,
                weaponskill=self.weaponskill
            )

    def divide_weaponskill(self, fraction = 0, weapon_type = None):
        # Save the current weapon's skill.
        if self.weapon != None and self.weapon >= 0:
            if self.weaponskill == None:
                self.weaponskill = 0

            new_weaponskill = int(self.weaponskill / fraction)

            ewutils.weaponskills_set(
                id_server=self.id_server,
                id_user=self.id_user,
                weapon=weapon_type,
                weaponskill=new_weaponskill
            )

    def eat(self, food_item = None):
        item_props = food_item.item_props
        mutations = self.get_mutations()
        statuses = self.getStatusEffects()

        # Find out if the item is perishable
        if item_props.get('perishable') != None:
            perishable_status = item_props.get('perishable')
            if perishable_status == 'true' or perishable_status == '1':
                item_is_non_perishable = False
            else:
                item_is_non_perishable = True
        else:
            item_is_non_perishable = False

        user_has_spoiled_appetite = ewcfg.mutation_id_spoiledappetite in mutations
        item_has_expired = float(getattr(food_item, "time_expir", 0)) < time.time()
        if item_has_expired and not (user_has_spoiled_appetite or item_is_non_perishable):
            response = "You realize that the food you were trying to eat is already spoiled. Ugh, not eating that."
        # ewitem.item_drop(food_item.id_item)
        else:
            hunger_restored = int(item_props['recover_hunger'])
            if self.id_user in ewutils.food_multiplier and ewutils.food_multiplier.get(self.id_user) > 0:
                if ewcfg.mutation_id_bingeeater in mutations:
                    hunger_restored *= max(ewutils.food_multiplier.get(self.id_user), 1)
                    if ewutils.food_multiplier.get(self.id_user) >= 5 and ewcfg.status_foodcoma_id not in self.getStatusEffects():
                        self.applyStatus(id_status=ewcfg.status_foodcoma_id, source=self.id_user, id_target=self.id_user)
                ewutils.food_multiplier[self.id_user] = min(ewutils.food_multiplier[self.id_user] + 1, ewcfg.bingeeater_cap)
            else:
                ewutils.food_multiplier[self.id_user] = 1

            if ewcfg.status_high_id in statuses:
                hunger_restored *= 0.5

            hunger_restored = round(hunger_restored)

            self.hunger -= hunger_restored
            if self.hunger < 0:
                self.hunger = 0
            self.inebriation += int(item_props['inebriation'])
            if self.inebriation > 20:
                self.inebriation = 20

            try:
                if item_props['id_food'] in ["coleslaw", "bloodcabbagecoleslaw"]:
                    self.clear_status(id_status=ewcfg.status_ghostbust_id)
                    self.applyStatus(id_status=ewcfg.status_ghostbust_id)
                    # Bust player if they're a ghost
                    if self.life_state == ewcfg.life_state_corpse:
                        self.die(cause=ewcfg.cause_busted)
                if item_props['id_food'] == ewcfg.item_id_seaweedjoint:
                    self.applyStatus(id_status=ewcfg.status_high_id)

            except:
                # An exception will occur if there's no id_food prop in the database. We don't care.
                pass

            response = item_props['str_eat'] + ("\n\nYou're stuffed!" if self.hunger <= 0 else "")

            bknd_item.item_delete(food_item.id_item)

        return response

    def add_mutation(self, id_mutation, is_artificial = 0):
        mutations = self.get_mutations()
        if id_mutation in mutations:
            return False
        try:
            bknd_core.execute_sql_query("REPLACE INTO mutations({id_server}, {id_user}, {id_mutation}, {tier}, {artificial}) VALUES (%s, %s, %s, %s, %s)".format(
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user,
                id_mutation=ewcfg.col_id_mutation,
                tier=ewcfg.col_tier,
                artificial=ewcfg.col_artificial
            ), (
                self.id_server,
                self.id_user,
                id_mutation,
                static_mutations.mutations_map.get(id_mutation).tier,
                is_artificial
            ))

            return True
        except:
            ewutils.logMsg("Failed to add mutation for user {}.".format(self.id_user))
            return False

    def clear_mutations(self):
        try:
            bknd_core.execute_sql_query("DELETE FROM mutations WHERE {id_server} = %s AND {id_user} = %s".format(
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user
            ), (
                self.id_server,
                self.id_user
            ))
        except:
            ewutils.logMsg("Failed to clear mutations for user {}.".format(self.id_user))

    def get_mutation_level(self):
        result = 0

        try:
            tiers = bknd_core.execute_sql_query(
                "SELECT SUM({tier}) FROM mutations WHERE {id_server} = %s AND {id_user} = %s;".format(
                    tier=ewcfg.col_tier,
                    id_server=ewcfg.col_id_server,
                    id_user=ewcfg.col_id_user,

                ), (
                    self.id_server,
                    self.id_user
                ))

            for tier_data in tiers:
                result = tier_data[0]

            if result is None:
                result = 0

        # random.seed(self.rand_seed + mutation_dat)

        except:
            ewutils.logMsg("Failed to get mutation level for user {}.".format(self.id_user))

        finally:
            return result

    def get_mutation_next_level(self):
        next_mutation = self.get_mutation_next()
        next_mutation_obj = static_mutations.mutations_map.get(next_mutation)
        if next_mutation_obj != None:
            return next_mutation_obj.tier
        else:
            return 50

    def get_mutation_next(self):
        counter = 0
        result = ""
        current_mutations = self.get_mutations()

        if self.get_mutation_level() >= 50:
            return 0

        seed = int(self.rand_seed)
        try:
            counter_data = bknd_core.execute_sql_query(
                "SELECT SUM({mutation_counter}) FROM mutations WHERE {id_server} = %s AND {id_user} = %s;".format(
                    mutation_counter=ewcfg.col_mutation_counter,
                    id_server=ewcfg.col_id_server,
                    id_user=ewcfg.col_id_user,

                ), (
                    self.id_server,
                    self.id_user
                ))

            for ids in counter_data:
                counter = ids[0]
            if counter == None:
                counter = 0
            random.seed(counter + seed)

            for x in range(1000):
                result = random.choice(list(static_mutations.mutation_ids))
                result_mutation = static_mutations.mutations_map[result]

                for mutation in current_mutations:
                    mutation = static_mutations.mutations_map[mutation]
                    if result in mutation.incompatible:
                        continue

                if result not in current_mutations and result_mutation.tier + self.get_mutation_level() <= 50:
                    return result

            result = ""

        except:
            ewutils.logMsg("Failed to get next mutations for user {}.".format(self.id_user))

        finally:
            return result

    def equip(self, weapon_item = None):
        return bknd_item.equip(self, weapon_item)

    def equip_sidearm(self, sidearm_item = None):
        return bknd_item.equip_sidearm(self, sidearm_item)

    def getStatusEffects(self):
        values = []

        try:
            data = bknd_core.execute_sql_query("SELECT {id_status} FROM status_effects WHERE {id_server} = %s and {id_user} = %s".format(
                id_status=ewcfg.col_id_status,
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user
            ), (
                self.id_server,
                self.id_user
            ))

            for row in data:
                values.append(row[0])

        except:
            pass
        finally:
            return values

    def applyStatus(self, id_status = None, value = 0, source = "", multiplier = 1, id_target = -1):

        return bknd_status.applyStatus(self, id_status, value, source, multiplier, id_target)

    def clear_status(self, id_status = None):
        if id_status != None:
            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                # Save the object.
                cursor.execute("DELETE FROM status_effects WHERE {id_status} = %s and {id_user} = %s and {id_server} = %s".format(
                    id_status=ewcfg.col_id_status,
                    id_user=ewcfg.col_id_user,
                    id_server=ewcfg.col_id_server
                ), (
                    id_status,
                    self.id_user,
                    self.id_server
                ))

                conn.commit()
            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

    def clear_allstatuses(self):
        try:
            bknd_core.execute_sql_query("DELETE FROM status_effects WHERE {id_server} = %s AND {id_user} = %s".format(
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user
            ), (
                self.id_server,
                self.id_user
            ))
        except:
            ewutils.logMsg("Failed to clear status effects for user {}.".format(self.id_user))

    def apply_injury(self, id_injury, severity, source):
        return bknd_status.apply_injury(self, id_injury, severity, source)

    def get_weapon_capacity(self):
        mutations = self.get_mutations()
        base_capacity = ewutils.weapon_carry_capacity_bylevel(self.slimelevel)
        if ewcfg.mutation_id_2ndamendment in mutations:
            return base_capacity + 1
        else:
            return base_capacity

    def get_food_capacity(self):
        mutations = self.get_mutations()
        base_capacity = ewutils.food_carry_capacity_bylevel(self.slimelevel)
        if ewcfg.mutation_id_bigbones in mutations:
            return 2 * base_capacity
        else:
            return base_capacity

    def get_mention(self):
        return "<@{id_user}>".format(id_user=self.id_user)

    def ban(self, faction = None):
        if faction is None:
            return
        bknd_core.execute_sql_query("REPLACE INTO bans ({id_user}, {id_server}, {faction}) VALUES (%s,%s,%s)".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            faction=ewcfg.col_faction
        ), (
            self.id_user,
            self.id_server,
            faction
        ))

    def unban(self, faction = None):
        if faction is None:
            return
        bknd_core.execute_sql_query("DELETE FROM bans WHERE {id_user} = %s AND {id_server} = %s AND {faction} = %s".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            faction=ewcfg.col_faction
        ), (
            self.id_user,
            self.id_server,
            faction
        ))

    def get_bans(self):
        bans = []
        data = bknd_core.execute_sql_query("SELECT {faction} FROM bans WHERE {id_user} = %s AND {id_server} = %s".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            faction=ewcfg.col_faction
        ), (
            self.id_user,
            self.id_server
        ))

        for row in data:
            bans.append(row[0])

        return bans

    def vouch(self, faction = None):
        if faction is None:
            return
        bknd_core.execute_sql_query("REPLACE INTO vouchers ({id_user}, {id_server}, {faction}) VALUES (%s,%s,%s)".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            faction=ewcfg.col_faction
        ), (
            self.id_user,
            self.id_server,
            faction
        ))

    def unvouch(self, faction = None):
        if faction is None:
            return
        bknd_core.execute_sql_query("DELETE FROM vouchers WHERE {id_user} = %s AND {id_server} = %s AND {faction} = %s".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            faction=ewcfg.col_faction
        ), (
            self.id_user,
            self.id_server,
            faction
        ))

    def get_vouchers(self):
        vouchers = []
        data = bknd_core.execute_sql_query("SELECT {faction} FROM vouchers WHERE {id_user} = %s AND {id_server} = %s".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            faction=ewcfg.col_faction
        ), (
            self.id_user,
            self.id_server
        ))

        for row in data:
            vouchers.append(row[0])

        return vouchers

    def get_inhabitants(self):
        inhabitants = []
        data = bknd_core.execute_sql_query("SELECT {id_ghost} FROM inhabitations WHERE {id_fleshling} = %s AND {id_server} = %s".format(
            id_ghost=ewcfg.col_id_ghost,
            id_fleshling=ewcfg.col_id_fleshling,
            id_server=ewcfg.col_id_server,
        ), (
            self.id_user,
            self.id_server
        ))

        for row in data:
            inhabitants.append(row[0])

        return inhabitants

    def get_inhabitee(self):
        data = bknd_core.execute_sql_query("SELECT {id_fleshling} FROM inhabitations WHERE {id_ghost} = %s AND {id_server} = %s".format(
            id_fleshling=ewcfg.col_id_fleshling,
            id_ghost=ewcfg.col_id_ghost,
            id_server=ewcfg.col_id_server,
        ), (
            self.id_user,
            self.id_server
        ))

        try:
            # return ID of inhabited player if there is one
            return data[0][0]
        except:
            # otherwise return None
            return None

    async def move_inhabitants(self, id_poi = None):
        client = ewutils.get_client()
        inhabitants = self.get_inhabitants()
        if inhabitants:
            server = client.get_guild(self.id_server)
            for ghost in inhabitants:
                ghost_data = EwUser(id_user=ghost, id_server=self.id_server)
                ghost_data.poi = id_poi
                ghost_data.time_lastenter = int(time.time())
                ghost_data.persist()

                ghost_member = server.get_member(ghost)
                await ewrolemgr.updateRoles(client=client, member=ghost_member)

    def remove_inhabitation(self):
        user_is_alive = self.life_state != ewcfg.life_state_corpse
        bknd_core.execute_sql_query("DELETE FROM inhabitations WHERE {id_target} = %s AND {id_server} = %s".format(
            # remove ghosts inhabiting player if user is a fleshling,
            # or remove fleshling inhabited by player if user is a ghost
            id_target=ewcfg.col_id_fleshling if user_is_alive else ewcfg.col_id_ghost,
            id_server=ewcfg.col_id_server,
        ), (
            self.id_user,
            self.id_server
        ))

    def get_possession(self, possession_type = ''):
        user_is_alive = self.life_state != ewcfg.life_state_corpse
        data = bknd_core.execute_sql_query("SELECT {id_ghost}, {id_fleshling}, {id_server}, {empowered} FROM inhabitations WHERE {id_target} = %s AND {id_server} = %s AND {inverted} {empowered} = %s".format(
            id_ghost=ewcfg.col_id_ghost,
            id_fleshling=ewcfg.col_id_fleshling,
            id_server=ewcfg.col_id_server,
            id_target=ewcfg.col_id_fleshling if user_is_alive else ewcfg.col_id_ghost,
            empowered=ewcfg.col_empowered,
            inverted='' if possession_type else 'NOT'
        ), (
            self.id_user,
            self.id_server,
            possession_type
        ))

        try:
            # return inhabitation data if available
            return data[0]
        except:
            # otherwise return None
            return None

    def cancel_possession(self):
        user_is_alive = self.life_state != ewcfg.life_state_corpse
        bknd_core.execute_sql_query(
            "UPDATE inhabitations SET {empowered} = '' WHERE {id_target} = %s AND {id_server} = %s".format(
                empowered=ewcfg.col_empowered,
                id_target=ewcfg.col_id_fleshling if user_is_alive else ewcfg.col_id_ghost,
                id_server=ewcfg.col_id_server,
            ), (
                self.id_user,
                self.id_server,
            )
        )

    def get_fashion_stats(self):
        return bknd_item.get_fashion_stats(self)

    def get_freshness(self):
        return bknd_item.get_freshness(self)

    def get_festivity(self):
        # Use cache if available
        item_cache = bknd_core.get_cache(obj_type = "EwItem")
        if item_cache is not False:
            # Get all user furniture id'd as a sigil
            sigils = item_cache.find_entries(criteria={
                "id_owner": self.id_user,
                "item_type": ewcfg.it_furniture,
                "id_server": self.id_server,
                "item_props": {"id_furniture": ewcfg.item_id_sigillaria},
            })

            # return the sum of festivity props and 1000 per sigil
            return self.festivity + self.festivity_from_slimecoin + (len(sigils)*1000)


        data = bknd_core.execute_sql_query(
            "SELECT {festivity} + COALESCE(sigillaria, 0) + {festivity_from_slimecoin} FROM users " \
            "LEFT JOIN (SELECT {id_user}, {id_server}, COUNT(*) * 1000 as sigillaria FROM items INNER JOIN items_prop ON items.{id_item} = items_prop.{id_item} " \
            "WHERE {type} = %s AND {name} = %s AND {value} = %s GROUP BY items.{id_user}, items.{id_server}) f on users.{id_user} = f.{id_user} AND users.{id_server} = f.{id_server} WHERE users.{id_user} = %s AND users.{id_server} = %s".format(
                id_user=ewcfg.col_id_user,
                id_server=ewcfg.col_id_server,
                festivity=ewcfg.col_festivity,
                festivity_from_slimecoin=ewcfg.col_festivity_from_slimecoin,
                type=ewcfg.col_item_type,
                name=ewcfg.col_name,
                value=ewcfg.col_value,
                id_item=ewcfg.col_id_item,
            ), (
                ewcfg.it_furniture,
                "id_furniture",
                ewcfg.item_id_sigillaria,
                self.id_user,
                self.id_server
            ))
        res = 0

        for row in data:
            res = row[0]

        return res
