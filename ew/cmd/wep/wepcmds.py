import asyncio
import math
import random
import time

from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.player import EwPlayer
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.static import slimeoid as sl_static
from ew.static import weapons as static_weapons
from ew.utils import combat as cmbt_utils
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as itm_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils import stats as ewstats
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict
from ew.utils.frontend import EwResponseContainer
from ew.utils.slimeoid import EwSlimeoid
from .weputils import EwEffectContainer
from .weputils import attackEnemy
from .weputils import burn_bystanders
from .weputils import canAttack
from .weputils import canCap
from .weputils import fulfill_ghost_weapon_contract
from .weputils import weapon_explosion

""" Player attacks a target """


async def attack(cmd, n1_die = None):
    time_now_float = time.time()
    time_now = int(time_now_float)
    response = ""
    deathreport = ""
    levelup_response = ""
    shambler_resp = ""
    coinbounty = 0
    resp_cont = EwResponseContainer(id_server=cmd.guild.id)
    market_data = EwMarket(id_server=cmd.guild.id)
    amb_switch = 0
    user_data = EwUser(member=cmd.message.author, data_level=1)

    slimeoid = EwSlimeoid(member=cmd.message.author)
    weapon = None
    weapon_item = None
    user_mutations = user_data.get_mutations()
    killfeed = 0

    if user_data.weapon >= 0:
        weapon_item = EwItem(id_item=user_data.weapon)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))

        if weapon.is_tool == 1 and user_data.sidearm >= 0 and ewcfg.mutation_id_ambidextrous in user_mutations:
            sidearm_item = EwItem(id_item=user_data.sidearm)
            sidearm = static_weapons.weapon_map.get(sidearm_item.item_props.get("weapon_type"))

            if sidearm.is_tool == 0:
                weapon_item = sidearm_item
                weapon = sidearm
                amb_switch = 1


    elif ewcfg.mutation_id_ambidextrous in user_mutations and user_data.sidearm >= 0:
        weapon_item = EwItem(id_item=user_data.sidearm)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
        amb_switch = 1

    elif ewcfg.mutation_id_lethalfingernails in user_mutations:
        id_item = itm_utils.get_fingernail_item(cmd=cmd)
        weapon_item = EwItem(id_item=id_item)
        weapon = static_weapons.weapon_map.get(ewcfg.weapon_id_fingernails)
        ewutils.weaponskills_set(member=cmd.message.author, weapon=ewcfg.weapon_id_fingernails, weaponskill=10)
        user_data.weaponskill = 10

    # todo Created a weapon object to cover my bases, check if this is necessary. Also see if you can move this somewhere else

    if n1_die is None:
        response = canAttack(cmd=cmd, amb_switch=amb_switch)

    if response == "":
        # Get shooting player's info
        if user_data.slimelevel <= 0:
            user_data.slimelevel = 1
            user_data.persist()

        # Get target's info.
        if n1_die is None:
            member = cmd.mentions[0]
            if member.id == cmd.message.author.id:
                response = "Try {}.".format(ewcfg.cmd_suicide)
                resp_cont.add_channel_response(cmd.message.channel.name, response)
                return await resp_cont.post()
            else:
                shootee_data = EwUser(member=member, data_level=1)
            shootee_slimeoid = EwSlimeoid(member=member)
            shootee_name = member.display_name
        else:
            member = cmd.guild.get_member(n1_die)
            shootee_data = EwUser(id_server=cmd.guild.id, id_user=n1_die, data_level=1)
            shootee_slimeoid = EwSlimeoid(id_user=n1_die, id_server=cmd.guild.id)
            shootee_player = EwPlayer(id_user=n1_die, id_server=cmd.guild.id)
            shootee_name = shootee_player.display_name

        shootee_weapon = None
        shootee_weapon_item = None
        if shootee_data.weapon >= 0:
            shootee_weapon_item = EwItem(id_item=shootee_data.weapon)
            shootee_weapon = static_weapons.weapon_map.get(shootee_weapon_item.item_props.get("weapon_type"))

        shootee_mutations = shootee_data.get_mutations()

        district_data = EwDistrict(district=user_data.poi, id_server=cmd.guild.id)

        miss = False
        crit = False
        bystander_damage = 0
        hit_chance_mod = 0
        crit_mod = 0
        dmg_mod = 0
        # sap_damage = 0
        # sap_ignored = 0

        # Weaponized flavor text.
        hitzone = cmbt_utils.get_hitzone()
        randombodypart = hitzone.name
        if random.random() < 0.5:
            randombodypart = random.choice(hitzone.aliases)

        shooter_status_mods = cmbt_utils.get_shooter_status_mods(user_data, shootee_data, hitzone)
        shootee_status_mods = cmbt_utils.get_shootee_status_mods(shootee_data, user_data, hitzone)

        hit_chance_mod += round(shooter_status_mods['hit_chance'] + shootee_status_mods['hit_chance'], 2)
        crit_mod += round(shooter_status_mods['crit'] + shootee_status_mods['crit'], 2)
        dmg_mod += round(shooter_status_mods['dmg'] + shootee_status_mods['dmg'], 2)

        if ewcfg.mutation_id_airlock in user_mutations and market_data.weather == ewcfg.weather_foggy:
            crit_mod += .1

        min_level_3as = math.ceil((1 / 10) ** 0.25 * user_data.slimelevel)
        if ewcfg.mutation_id_threesashroud in user_mutations:
            allies_in_district = district_data.get_players_in_district(min_level=min_level_3as, life_states=[user_data.life_state], factions=[user_data.faction])
            if len(allies_in_district) > 3:
                crit_mod *= 2

        if weapon.is_tool == 1:
            capped_level = min(35, user_data.slimelevel)
        else:
            capped_level = user_data.slimelevel

        slimes_spent = int(ewutils.slime_bylevel(capped_level) / 30)

        # disabled until held items update
        # attack_stat_multiplier = 1 + (user_data.attack / 50) # 2% more damage per stat point
        attack_stat_multiplier = 1
        weapon_skill_multiplier = 1 + ((user_data.weaponskill * 5) / 100)  # 5% more damage per skill point
        slimes_damage = int(5 * slimes_spent * attack_stat_multiplier * weapon_skill_multiplier)  # ten times slime spent, multiplied by both multipliers

        # Tool damage is maximized at level 35 but proportional cost remains the same
        slimes_spent = int(ewutils.slime_bylevel(capped_level) / 30)

        if user_data.weaponskill < 5:
            hit_chance_mod -= (5 - user_data.weaponskill) / 10

        if weapon is None:
            slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons
        slimes_dropped = shootee_data.totaldamage + shootee_data.slimes

        slimes_damage += int(slimes_damage * dmg_mod)

        user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers

        if shootee_data.life_state == ewcfg.life_state_corpse:
            # Attack a ghostly target
            coinbounty = int(shootee_data.bounty / ewcfg.slimecoin_exchangerate)
            user_data.change_slimecoin(n=coinbounty, coinsource=ewcfg.coinsource_bounty)

            ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_bust_level, value=shootee_data.slimelevel)

            # Steal items
            # bknd_item.item_loot(member = member, id_user_target = cmd.message.author.id)

            shootee_data.id_killer = user_data.id_user
            die_resp = shootee_data.die(cause=ewcfg.cause_busted)

            response = "{name_target}\'s ghost has been **BUSTED**!!".format(name_target=member.display_name)

            if coinbounty > 0:
                response += "\n\n SlimeCorp transfers {:,} SlimeCoin to {}\'s account.".format(coinbounty, cmd.message.author.display_name)

            # adjust busts
            ewstats.increment_stat(user=user_data, metric=ewcfg.stat_ghostbusts)

            # pay sap cost
            # if weapon != None:
            #	user_data.sap -= weapon.sap_cost
            #	user_data.limit_fix()

            # Persist every users' data.
            user_data.persist()
            shootee_data.persist()
            if die_resp != resp_cont:
                resp_cont.add_response_container(die_resp)
            resp_cont.add_channel_response(cmd.message.channel.name, response)

            resp_cont.add_member_to_update(member)

        else:
            # hunger drain
            user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)

            # randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]
            if ewcfg.mutation_id_napalmsnot in user_mutations:
                bystander_damage = slimes_damage * 0.5
            # Weapon-specific adjustments
            if weapon != None and weapon.fn_effect != None:

                # Build effect container
                ctn = EwEffectContainer(
                    miss=miss,
                    crit=crit,
                    slimes_damage=slimes_damage,
                    slimes_spent=slimes_spent,
                    user_data=user_data,
                    weapon_item=weapon_item,
                    shootee_data=shootee_data,
                    time_now=time_now_float,
                    bystander_damage=bystander_damage,
                    hit_chance_mod=hit_chance_mod,
                    crit_mod=crit_mod,
                    market_data=market_data,
                    # sap_damage = sap_damage,
                    # sap_ignored = sap_ignored,
                )

                # Make adjustments
                weapon.fn_effect(ctn)

                # Apply effects for non-reference values
                miss = ctn.miss
                crit = ctn.crit
                slimes_damage = ctn.slimes_damage
                slimes_spent = ctn.slimes_spent
                bystander_damage = ctn.bystander_damage
                # sap_damage = ctn.sap_damage
                # sap_ignored = ctn.sap_ignored
                # user_data and shootee_data should be passed by reference, so there's no need to assign them back from the effect container.

                no_slime_cost = False
                user_status_effects = user_data.getStatusEffects()
                for stat in ewcfg.nocost:
                    if stat in user_status_effects:
                        no_slime_cost = True

                if no_slime_cost != True:
                    if (slimes_spent > user_data.slimes):
                        # Not enough slime to shoot.
                        response = "You don't have enough slime to attack. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    # Spend slimes, to a minimum of zero
                    user_data.change_slimes(n=(-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent), source=ewcfg.source_spending)

                    user_data.limit_fix()
                    user_data.persist()

                weapon_item.item_props['time_lastattack'] = time_now_float
                weapon_item.persist()
                if weapon.id_weapon == ewcfg.weapon_id_garrote:
                    shootee_data.persist()
                    response = "You wrap your wire around {}'s neck...".format(member.display_name)
                    resp_cont.add_channel_response(cmd.message.channel.name, response)
                    resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
                    await resp_cont.post()
                    msg = await cmd.client.wait_for('message', timeout=5, check=lambda message: message.author == member)

                    user_data = EwUser(member=cmd.message.author, data_level=1)
                    shootee_data = EwUser(member=member, data_level=1)

                    # One of the players died in the meantime
                    if user_data.life_state == ewcfg.life_state_corpse or shootee_data.life_state == ewcfg.life_state_corpse:
                        return
                    # A user left the district or strangling was broken
                    elif msg != None or user_data.poi != shootee_data.poi:
                        return
                    else:
                        shootee_data.clear_status(ewcfg.status_strangled_id)
                # shootee_data.persist()

                # Remove a bullet from the weapon
                if ewcfg.weapon_class_ammo in weapon.classes:
                    weapon_item.item_props['ammo'] = int(weapon_item.item_props.get("ammo")) - 1

                life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_shambler]
                factions = ["", shootee_data.faction]

                # Burn players in district
                if ewcfg.weapon_class_burning in weapon.classes:
                    if not miss:
                        resp = burn_bystanders(user_data=user_data, burn_dmg=bystander_damage, life_states=life_states, factions=factions, district_data=district_data)
                        resp_cont.add_response_container(resp)

                elif ewcfg.weapon_class_exploding in weapon.classes:
                    if not miss:
                        resp = weapon_explosion(user_data=user_data, shootee_data=shootee_data, district_data=district_data, market_data=market_data, life_states=life_states, factions=factions, slimes_damage=bystander_damage, time_now=time_now, target_enemy=False)
                        resp_cont.add_response_container(resp)

                elif ewcfg.mutation_id_napalmsnot in user_mutations and ewcfg.mutation_id_napalmsnot not in shootee_mutations and (ewcfg.mutation_id_airlock not in shootee_mutations or market_data.weather != ewcfg.weather_rainy):
                    resp = "**HCK-PTOOO!** " + shootee_data.applyStatus(id_status=ewcfg.status_burning_id, value=bystander_damage * .5, source=user_data.id_user).format(name_player=cmd.mentions[0].display_name)
                    resp_cont.add_channel_response(cmd.message.channel.name, resp)

            # can't hit lucky lucy
            if shootee_data.life_state == ewcfg.life_state_lucky or ewcfg.status_n4 in shootee_data.getStatusEffects():
                miss = True

            if miss:
                slimes_damage = 0
                weapon_item.item_props["consecutive_hits"] = 0
                crit = False

            # Remove !revive invulnerability.
            user_data.time_lastrevive = 0

            # apply attacker damage mods
            slimes_damage *= cmbt_utils.damage_mod_attack(
                user_data=user_data,
                user_mutations=user_mutations,
                market_data=market_data,
                district_data=district_data
            )

            # apply defender damage mods
            slimes_damage *= cmbt_utils.damage_mod_defend(
                shootee_data=shootee_data,
                shootee_mutations=shootee_mutations,
                market_data=market_data,
                shootee_weapon=shootee_weapon
            )

            # sap_armor = get_sap_armor(shootee_data = shootee_data, sap_ignored = sap_ignored)
            # slimes_damage *= sap_armor
            # slimes_damage = int(max(slimes_damage, 0))

            # disabled until held items update
            # fashion_armor = get_fashion_armor(shootee_data)
            # slimes_damage *= fashion_armor
            slimes_damage = int(max(0, slimes_damage))

            # sap_damage = min(sap_damage, shootee_data.hardened_sap)

            # injury_severity = get_injury_severity(shootee_data, slimes_damage, crit)

            # Damage stats
            ewstats.track_maximum(user=user_data, metric=ewcfg.stat_max_hitdealt, value=slimes_damage)
            ewstats.change_stat(user=user_data, metric=ewcfg.stat_lifetime_damagedealt, n=slimes_damage)

            # Slimes from this shot might be awarded to the boss.
            role_boss = (ewcfg.role_copkiller if user_iskillers else ewcfg.role_rowdyfucker)
            boss_slimes = 0
            user_inital_level = user_data.slimelevel

            was_juvenile = False
            was_shambler = False
            was_killed = False
            was_shot = False

            if shootee_data.life_state in [ewcfg.life_state_shambler, ewcfg.life_state_enlisted, ewcfg.life_state_juvenile, ewcfg.life_state_lucky, ewcfg.life_state_executive]:
                # User can be shot.
                if shootee_data.life_state == ewcfg.life_state_juvenile:
                    was_juvenile = True

                if shootee_data.life_state == ewcfg.life_state_shambler:
                    was_shambler = True
                was_shot = True

            if was_shot:

                resp_cont.add_member_to_update(cmd.message.author)

                if slimes_damage >= shootee_data.slimes - shootee_data.bleed_storage:
                    was_killed = True
                    # if ewcfg.mutation_id_thickerthanblood in user_mutations:
                    slimes_damage = 0
                # else:
                #	slimes_damage = max(shootee_data.slimes - shootee_data.bleed_storage, 0)

                sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=cmd.guild.id)
                # move around slime as a result of the shot
                if was_shambler or was_juvenile or user_data.faction == shootee_data.faction or user_data.life_state == ewcfg.life_state_juvenile:
                    slimes_drained = 0  # int(3 * slimes_damage / 4) # 3/4
                    slimes_toboss = 0
                else:
                    slimes_drained = 0
                    slimes_toboss = int(slimes_damage / 2)

                damage = slimes_damage

                slimes_tobleed = int((slimes_damage - slimes_toboss - slimes_drained) / 2)
                # if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
                #	slimes_tobleed = 0
                # if ewcfg.mutation_id_bleedingheart in shootee_mutations:
                #	slimes_tobleed *= 2

                slimes_directdamage = slimes_damage - slimes_tobleed
                slimes_splatter = slimes_damage - slimes_toboss - slimes_tobleed - slimes_drained

                # Damage victim's wardrobe (heh, WARdrobe... get it??)
                # victim_cosmetics = bknd_item.inventory(
                #	id_user = member.id,
                #	id_server = cmd.guild.id,
                #	item_type_filter = ewcfg.it_cosmetic
                # )

                onbreak_responses = []

                # the following code handles cosmetic durability loss

                # for cosmetic in victim_cosmetics:
                # 	if not int(cosmetic.get('soulbound')) == 1:
                #
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
                # 			if durability_afterhit <= 0: # If it breaks
                # 				c.item_props['durability'] = durability_afterhit
                # 				c.persist()
                #
                #
                # 				shootee_data.persist()
                #
                # 				onbreak_responses.append(str(c.item_props['str_onbreak']).format(c.item_props['cosmetic_name']))
                #
                # 				bknd_item.item_delete(id_item = c.id_item)
                #
                # 			else:
                # 				c.item_props['durability'] = durability_afterhit
                # 				c.persist()
                #
                # 		else:
                # 			pass

                if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
                    user_data.change_slimes(n=slimes_splatter * 0.6, source=ewcfg.source_killing)
                    slimes_splatter *= .4

                market_data.splattered_slimes += slimes_damage
                market_data.persist()
                user_data.splattered_slimes += slimes_damage
                user_data.persist()
                boss_slimes += slimes_toboss
                district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
                shootee_data.bleed_storage += slimes_tobleed
                shootee_data.time_lasthit = int(time_now)
                shootee_data.persist()
                shootee_data.change_slimes(n=-slimes_directdamage, source=ewcfg.source_damage)
                shootee_data.persist()
                # shootee_data.hardened_sap -= sap_damage
                sewer_data.change_slimes(n=slimes_drained)
                sewer_data.persist()

                if was_killed:
                    # adjust statistics
                    ewstats.increment_stat(user=user_data, metric=ewcfg.stat_kills)
                    ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
                    if user_data.slimelevel > shootee_data.slimelevel:
                        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_ganks)
                    elif user_data.slimelevel < shootee_data.slimelevel:
                        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_takedowns)

                    if shootee_data.life_state == ewcfg.life_state_shambler:
                        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_shamblers_killed)

                    if weapon != None:
                        weapon_item.item_props["kills"] = (int(weapon_item.item_props.get("kills")) if weapon_item.item_props.get("kills") != None else 0) + 1
                        weapon_item.item_props["totalkills"] = (int(weapon_item.item_props.get("totalkills")) if weapon_item.item_props.get("totalkills") != None else 0) + 1
                        ewstats.increment_stat(user=user_data, metric=weapon.stat)

                        # Give a bonus to the player's weapon skill for killing a stronger player.
                        if shootee_data.slimelevel >= user_data.slimelevel and shootee_data.slimelevel >= user_data.weaponskill:
                            user_data.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

                    # Collect bounty
                    coinbounty = int(shootee_data.bounty / ewcfg.slimecoin_exchangerate)  # 100 slime per coin

                    if shootee_data.slimes >= 0:
                        user_data.change_slimecoin(n=coinbounty, coinsource=ewcfg.coinsource_bounty)

                    # Steal items
                    # bknd_item.item_loot(member = member, id_user_target = cmd.message.author.id)

                    # add bounty
                    user_data.add_bounty(n=(shootee_data.bounty / 2) + (slimes_dropped / 4))

                    # Scalp text
                    if weapon != None:
                        scalp_text = weapon.str_scalp
                    else:
                        scalp_text = ""

                    if shootee_data.life_state != ewcfg.life_state_shambler:
                        # Drop shootee scalp
                        bknd_item.item_create(
                            item_type=ewcfg.it_cosmetic,
                            id_user=cmd.message.author.id,
                            id_server=cmd.guild.id,
                            item_props={
                                'id_cosmetic': 'scalp',
                                'cosmetic_name': "{}'s scalp".format(shootee_name),
                                'cosmetic_desc': "A scalp.{}".format(scalp_text),
                                'str_onadorn': ewcfg.str_generic_onadorn,
                                'str_unadorn': ewcfg.str_generic_unadorn,
                                'str_onbreak': ewcfg.str_generic_onbreak,
                                'rarity': ewcfg.rarity_patrician,
                                'attack': 1,
                                'defense': 0,
                                'speed': 0,
                                'ability': None,
                                'durability': int(ewutils.slime_bylevel(shootee_data.slimelevel) / 4),
                                'original_durability': int(ewutils.slime_bylevel(shootee_data.slimelevel) / 4),
                                'size': 1,
                                'fashion_style': ewcfg.style_cool,
                                'freshness': 10,
                                'adorned': 'false'
                            }
                        )
                    elif ewcfg.status_modelovaccine_id in user_data.getStatusEffects():
                        shootee_data.degradation = 0
                        shambler_resp = "Your purified slime seeps into and emulsifies in their mangled corpse, healing their degraded body. When they revive, they’ll be a normal slimeboi like the rest of us. A pure, homogenous race of ENDLESS WAR fearing juveniles. It brings a tear to your eye."

                    # release bleed storage
                    # if ewcfg.mutation_id_thickerthanblood in user_mutations:
                    # slimes_todistrict = 0
                    slimes_tokiller = shootee_data.slimes
                    # else:
                    #	slimes_todistrict = shootee_data.slimes / 2
                    #	slimes_tokiller = shootee_data.slimes / 2
                    # district_data.change_slimes(n = slimes_todistrict, source = ewcfg.source_killing)
                    levelup_response = user_data.change_slimes(n=slimes_tokiller, source=ewcfg.source_killing)
                    if ewcfg.mutation_id_fungalfeaster in user_mutations:
                        user_data.hunger = 0

                    # if shootee_data.life_state != ewcfg.life_state_shambler:
                    # 	user_data.degradation -= int(shootee_data.slimelevel / 10)

                    user_data.persist()
                    district_data.persist()
                    # Player was killed.
                    shootee_data.id_killer = user_data.id_user
                    die_resp = shootee_data.die(cause=ewcfg.cause_killing)
                    # shootee_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)

                    user_data = EwUser(member=cmd.message.author, data_level=1)
                    district_data = EwDistrict(district=district_data.name, id_server=district_data.id_server)

                    kill_descriptor = "beaten to death"
                    if weapon != None:
                        response = weapon.str_damage.format(
                            name_player=cmd.message.author.display_name,
                            name_target=member.display_name,
                            hitzone=randombodypart,
                        )
                        kill_descriptor = weapon.str_killdescriptor
                        if crit:
                            response += " {}".format(weapon.str_crit.format(
                                name_player=cmd.message.author.display_name,
                                name_target=member.display_name,
                                hitzone=randombodypart,
                            ))

                        response = ""

                        if len(onbreak_responses) != 0:
                            for onbreak_response in onbreak_responses:
                                response += "\n\n" + onbreak_response

                        response += "\n\n{}".format(weapon.str_kill.format(
                            name_player=cmd.message.author.display_name,
                            name_target=member.display_name,
                            emote_skull=ewcfg.emote_slimeskull
                        ))

                        if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
                            response += "\n" + weapon.str_reload_warning.format(name_player=cmd.message.author.display_name)

                        if ewcfg.weapon_class_captcha in weapon.classes:
                            new_captcha = ewutils.generate_captcha(length=weapon.captcha_length, user_data=user_data)
                            response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
                            weapon_item.item_props['captcha'] = new_captcha
                            weapon_item.persist()

                        shootee_data.trauma = weapon.id_weapon

                    else:
                        response = ""

                        if len(onbreak_responses) != 0:
                            for onbreak_response in onbreak_responses:
                                response = onbreak_response + "\n\n"

                        response += "{name_target} is hit!!\n\n{name_target} has died.".format(name_target=member.display_name)

                        shootee_data.trauma = ewcfg.trauma_id_environment

                    if shootee_data.faction != "" and shootee_data.faction == user_data.faction:
                        shootee_data.trauma = ewcfg.trauma_id_betrayal

                    if slimeoid.life_state == ewcfg.slimeoid_state_active:
                        brain = sl_static.brain_map.get(slimeoid.ai)
                        response += "\n\n" + brain.str_kill.format(slimeoid_name=slimeoid.name)

                    if shootee_slimeoid.life_state == ewcfg.slimeoid_state_active:
                        brain = sl_static.brain_map.get(shootee_slimeoid.ai)
                        response += "\n\n" + brain.str_death.format(slimeoid_name=shootee_slimeoid.name)

                    if coinbounty > 0:
                        response += "\n\n SlimeCorp transfers {:,} SlimeCoin to {}\'s account.".format(coinbounty, cmd.message.author.display_name)

                    if "n1" in shootee_data.getStatusEffects():
                        response += "\n\n But N1 doesn't die!"

                    weapon_possession = user_data.get_possession('weapon')
                    if weapon_possession:
                        response += fulfill_ghost_weapon_contract(weapon_possession, market_data, user_data, cmd.message.author.display_name)

                    if shambler_resp != "":
                        response += "\n\n" + shambler_resp

                    shootee_data.persist()
                    resp_cont.add_response_container(die_resp)
                    resp_cont.add_channel_response(cmd.message.channel.name, response)
                else:
                    # A non-lethal blow!

                    # apply injury
                    # if injury_severity > 0:
                    #	shootee_data.apply_injury(hitzone.id_injury, injury_severity, user_data.id_user)

                    if weapon != None:
                        if miss:
                            response = "{}".format(weapon.str_miss.format(
                                name_player=cmd.message.author.display_name,
                                name_target=member.display_name
                            ))
                        else:
                            response = weapon.str_damage.format(
                                name_player=cmd.message.author.display_name,
                                name_target=member.display_name,
                                hitzone=randombodypart,
                            )
                            if crit:
                                response += " {}".format(weapon.str_crit.format(
                                    name_player=cmd.message.author.display_name,
                                    name_target=member.display_name,
                                    hitzone=randombodypart,
                                ))

                            # sap_response = ""
                            # if sap_damage > 0:
                            #	sap_response = " and {sap_damage} hardened sap".format(sap_damage = sap_damage)

                            response += " {target_name} loses {damage:,} slime!".format(
                                target_name=member.display_name,
                                damage=damage
                                #	sap_response = sap_response
                            )

                            if len(onbreak_responses) != 0:
                                for onbreak_response in onbreak_responses:
                                    response += "\n\n" + onbreak_response

                        if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
                            response += "\n" + weapon.str_reload_warning.format(name_player=cmd.message.author.display_name)

                        if ewcfg.weapon_class_captcha in weapon.classes:
                            new_captcha = ewutils.generate_captcha(length=weapon.captcha_length, user_data=user_data)
                            response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
                            weapon_item.item_props['captcha'] = new_captcha
                            weapon_item.persist()
                    else:
                        if miss:
                            response = "{target_name} dodges your strike.".format(target_name=member.display_name)
                        else:
                            response = "{target_name} is hit!! {target_name} loses {damage:,} slime!".format(
                                target_name=member.display_name,
                                damage=damage
                            )

                            if len(onbreak_responses) != 0:
                                for onbreak_response in onbreak_responses:
                                    response += "\n\n" + onbreak_response

                    resp_cont.add_channel_response(cmd.message.channel.name, response)
            else:
                response = 'You are unable to attack {}.'.format(member.display_name)
                resp_cont.add_channel_response(cmd.message.channel.name, response)

            # Add level up text to response if appropriate
            if user_inital_level < user_data.slimelevel:
                resp_cont.add_channel_response(cmd.message.channel.name, "\n" + levelup_response)
            # Team kills don't award slime to the kingpin.
            if user_data.faction != shootee_data.faction and user_data.life_state not in (ewcfg.life_state_shambler, ewcfg.life_state_juvenile) and user_data.faction != ewcfg.faction_slimecorp:
                # Give slimes to the boss if possible.
                kingpin = fe_utils.find_kingpin(id_server=cmd.guild.id, kingpin_role=role_boss)
                kingpin = EwUser(id_server=cmd.guild.id, id_user=kingpin.id_user)

                if kingpin:
                    if ewcfg.mutation_id_handyman in user_mutations and weapon.is_tool == 1:
                        boss_slimes *= 2
                    kingpin.change_slimes(n=boss_slimes)
                    kingpin.persist()

            # Persist every users' data.
            user_data.persist()
            if user_data.weapon > 0:
                weapon_item.persist()

            shootee_data.persist()
            if shootee_weapon_item != None:
                shootee_weapon_item = EwItem(id_item=shootee_weapon_item.id_item)
                shootee_weapon_item.item_props["consecutive_hits"] = 0
                shootee_weapon_item.persist()

            district_data.persist()

            # Assign the corpse role to the newly dead player.
            if was_killed:
                resp_cont.add_member_to_update(member)
                # announce death in kill feed channel
                # killfeed_channel = fe_utils.get_channel(cmd.guild, ewcfg.channel_killfeed)
                killfeed_resp = resp_cont.channel_responses[cmd.message.channel.name]
                killfeed_resp_cont = EwResponseContainer(id_server=cmd.guild.id)

                for r in killfeed_resp:
                    killfeed_resp_cont.add_channel_response(ewcfg.channel_killfeed, r)
                    killfeed = 1
                killfeed_resp_cont.format_channel_response(ewcfg.channel_killfeed, cmd.message.author)
                killfeed_resp_cont.add_channel_response(ewcfg.channel_killfeed, "`-------------------------`")

                user_data.persist()
                resp_cont.add_member_to_update(cmd.message.author)

            # await fe_utils.send_message(cmd.client, killfeed_channel, fe_utils.formatMessage(cmd.message.author, killfeed_resp))

            # Send the response to the player.
            resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)

        await resp_cont.post()
        if killfeed:
            if ewcfg.mutation_id_amnesia in user_mutations:
                await asyncio.sleep(60)
            await killfeed_resp_cont.post()

    elif response == ewcfg.enemy_targeted_string:
        # TODO - Move this to it's own function in ewhunting or merge it into the previous code block somehow

        # Enemy has been targeted rather than a player
        await attackEnemy(cmd, user_data, weapon, resp_cont, weapon_item, slimeoid, market_data, time_now_float)

    else:
        resp_cont.add_channel_response(cmd.message.channel.name, response)
        resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)

        await resp_cont.post()

    if weapon_item:
        if weapon_item.item_props.get("weapon_type") == "fingernails":
            bknd_item.item_delete(id_item=weapon_item.id_item)


""" Reload ammo based weapons """


async def reload(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    response = ""
    reload_mismatch = True

    if user_data.weapon > 0:
        weapon_item = EwItem(id_item=user_data.weapon)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))

        if ewcfg.weapon_class_ammo in weapon.classes:
            if weapon.id_weapon == ewcfg.weapon_id_harpoon:
                # Because this takes so long, we check a couple times if the player has died
                response = "You start frantically reloading the harpoon gun..."
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                await asyncio.sleep(2)
                if user_data.life_state == ewcfg.life_state_corpse:
                    return
                response = "...oh god oh fuck oh fuck oh god oh fuck oh shit..."
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                await asyncio.sleep(3)
                if user_data.life_state == ewcfg.life_state_corpse:
                    return

            weapon_item.item_props["ammo"] = weapon.clip_size
            weapon_item.persist()
            response = weapon.str_reload
            reload_mismatch = False

    if user_data.sidearm > 0:
        sidearm_item = EwItem(id_item=user_data.sidearm)
        sidearm = static_weapons.weapon_map.get(sidearm_item.item_props.get("weapon_type"))

        if ewcfg.weapon_class_ammo in sidearm.classes and sidearm.id_weapon != ewcfg.weapon_id_harpoon:
            sidearm_item.item_props["ammo"] = sidearm.clip_size
            sidearm_item.persist()
            if response != "":
                response += "\n"
            response += sidearm.str_reload
            reload_mismatch = False

    if user_data.weapon == -1 and user_data.sidearm == -1:
        response = "What are you expecting to reload, dumbass? {} a weapon first!".format(ewcfg.cmd_equip)
    elif reload_mismatch:
        response = "What do you think you're going to be reloading with that?"

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" Set active weapon """


async def equip(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    time_now = int(time.time())

    if user_data.time_lastenlist > time_now:
        response = "You've enlisted way too recently! You can't equip any weapons just yet."

    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)

    if item_sought:
        item = EwItem(id_item=item_sought.get("id_item"))

        if item.item_type == ewcfg.it_weapon:
            weapon = static_weapons.weapon_map.get(item.item_props.get("weapon_type"))
            # if weapon.is_tool == 1 and (user_data.sidearm < 0 or user_data.weapon >= 0):
            #	return await sidearm(cmd =cmd)

            item.item_props['roomba'] = ""
            response = user_data.equip(item)
            user_data.persist()
            item.persist()
        else:
            response = "Not a weapon, you ignorant juvenile."
    else:
        response = "You don't have one."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" Set sidearm slot """


async def sidearm(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to equip a {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    time_now = int(time.time())

    if user_data.time_lastenlist > time_now:
        response = "You've enlisted way too recently! You can't sidearm any weapons just yet."

    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)

    if item_sought:
        item = EwItem(id_item=item_sought.get("id_item"))

        if item.item_type == ewcfg.it_weapon:
            item.item_props['roomba'] = ""
            response = user_data.equip_sidearm(sidearm_item=item)
            user_data.persist()
            item.persist()

        else:
            response = "Not a tool, you ignorant juvenile."
    else:
        response = "You don't have one."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" Player kills themselves """


async def suicide(cmd):
    response = ""

    resp_cont = EwResponseContainer(id_server=cmd.guild.id)

    # Only allowed in the combat zone.
    if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
        response = "You must go into the city to commit {}.".format(cmd.tokens[0][1:])
    else:
        # Get the user data.
        user_data = EwUser(member=cmd.message.author)
        mutations = user_data.get_mutations()
        if user_data.life_state == ewcfg.life_state_shambler:
            response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers
        user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_rowdys
        user_isslimecorp = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_slimecorp
        user_isgeneral = user_data.life_state == ewcfg.life_state_kingpin
        user_isjuvenile = user_data.life_state == ewcfg.life_state_juvenile
        user_isdead = user_data.life_state == ewcfg.life_state_corpse
        user_isexecutive = user_data.life_state == ewcfg.life_state_executive
        user_islucky = user_data.life_state == ewcfg.life_state_lucky

        if user_isdead:
            response = "Too late for that."
        elif user_isjuvenile and ewcfg.mutation_id_nervesofsteel not in mutations:
            response = "Juveniles are too cowardly for suicide."
        elif user_isgeneral:
            response = "\*click* Alas, your gun has jammed."
        elif user_iskillers or user_isrowdys or user_isexecutive or user_islucky or user_isjuvenile or user_isslimecorp:
            if ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
                response = "You can't do that right now."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            slimes_total = user_data.slimes
            slimes_drained = int(slimes_total * 0.1)
            slimes_todistrict = slimes_total - slimes_drained

            sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=user_data.id_server)
            sewer_data.change_slimes(n=slimes_drained)
            # print(sewer_data.degradation)
            sewer_data.persist()

            district_data = EwDistrict(district=user_data.poi, id_server=cmd.guild.id)
            district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)
            district_data.persist()

            # Set the id_killer to the player himself, remove his slime and slime poudrins.
            user_data.id_killer = cmd.message.author.id
            user_data.trauma = ewcfg.trauma_id_suicide
            user_data.visiting = ewcfg.location_id_empty
            die_resp = user_data.die(cause=ewcfg.cause_suicide)
            resp_cont.add_response_container(die_resp)
            user_data.persist()

            # Assign the corpse role to the player. He dead.
            await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

            if user_data.has_soul == 1:
                response = '{} has willingly returned to the slime. {}'.format(cmd.message.author.display_name, ewcfg.emote_slimeskull)
            else:
                response = "Ahh. As it should be. {}".format(ewcfg.emote_slimeskull)

        else:
            # This should never happen. We handled all the role cases. Just in case.
            response = "\*click* Alas, your gun has jammed."

    # Send the response to the player.
    resp_cont.add_channel_response(cmd.message.channel.name, fe_utils.formatMessage(cmd.message.author, response))
    await resp_cont.post()


""" Player spars with a friendly player to gain slime. """


async def spar(cmd):
    time_now = int(time.time())
    response = ""

    if cmd.message.channel.name != ewcfg.channel_dojo:
        response = "You must go to the dojo to spar."

    elif cmd.mentions_count > 1:
        response = "One sparring partner at a time!"

    elif cmd.mentions_count == 1:
        member = cmd.mentions[0]

        if (member.id == cmd.message.author.id):
            response = "How do you expect to spar with yourself?"
        else:
            # Get killing player's info.
            user_data = EwUser(member=cmd.message.author)
            if user_data.life_state == ewcfg.life_state_shambler:
                response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            weapon_item = EwItem(id_item=user_data.weapon)

            # Get target's info.
            sparred_data = EwUser(member=member)
            sparred_weapon_item = EwItem(id_item=sparred_data.weapon)

            user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers
            user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_rowdys
            user_isslimecorp = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_slimecorp
            user_isexecutive = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
            user_isdead = user_data.life_state == ewcfg.life_state_corpse

            if user_data.hunger >= user_data.get_hunger_max():
                response = "You are too exhausted to train right now. Go get some grub!"
            elif user_data.poi != ewcfg.poi_id_dojo or sparred_data.poi != ewcfg.poi_id_dojo:
                response = "Both players need to be in the dojo to spar."
            elif sparred_data.hunger >= user_data.get_hunger_max():
                response = "{} is too exhausted to train right now. They need a snack!".format(member.display_name)
            elif user_isdead == True:
                response = "The dead think they're too cool for conventional combat. Pricks."
            elif (user_iskillers == False and user_isrowdys == False and user_isexecutive == False and user_isslimecorp == False) or user_data.life_state == ewcfg.life_state_corpse:
                # Only killers, rowdys, the cop killer, and the rowdy fucker can spar
                response = "Juveniles lack the backbone necessary for combat."
            else:
                was_juvenile = False
                was_sparred = False
                was_dead = False
                was_player_tired = False
                was_target_tired = False
                was_enemy = False
                duel = False

                # Determine if the !spar is a duel:
                weapon = None
                if user_data.weapon >= 0 and sparred_data.weapon >= 0 and weapon_item.item_props.get("weapon_type") == sparred_weapon_item.item_props.get("weapon_type"):
                    weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
                    duel = True

                if sparred_data.life_state == ewcfg.life_state_corpse:
                    # Target is already dead.
                    was_dead = True
                elif (user_data.time_lastspar + ewcfg.cd_spar) > time_now:
                    # player sparred too recently
                    was_player_tired = True
                    timeuntil_player_spar = ewcfg.cd_spar - (time_now - user_data.time_lastspar)
                elif (sparred_data.time_lastspar + ewcfg.cd_spar) > time_now:
                    # taret sparred too recently
                    was_target_tired = True
                    timeuntil_target_spar = ewcfg.cd_spar - (time_now - sparred_data.time_lastspar)
                elif sparred_data.life_state == ewcfg.life_state_juvenile:
                    # Target is a juvenile.
                    was_juvenile = True
                elif (user_iskillers and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction == ewcfg.faction_killers)) or (user_isrowdys and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction == ewcfg.faction_rowdys)) or (
                        user_isslimecorp and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction == ewcfg.faction_slimecorp)):
                    # User can be sparred.
                    was_sparred = True
                elif (user_iskillers and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction != ewcfg.faction_killers)) or (user_isrowdys and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction != ewcfg.faction_rowdys)) or (
                        user_isslimecorp and (sparred_data.life_state == ewcfg.life_state_enlisted and sparred_data.faction != ewcfg.faction_slimecorp)):
                    # Target is a member of the opposing faction.
                    was_enemy = True

                # if the duel is successful
                if was_sparred:
                    weaker_player = sparred_data if sparred_data.slimes < user_data.slimes else user_data
                    stronger_player = sparred_data if user_data is weaker_player else user_data

                    # Weaker player gains slime based on the slime of the stronger player.
                    possiblegain = int(ewcfg.slimes_perspar_base * (2.2 ** weaker_player.slimelevel))
                    slimegain = min(possiblegain, stronger_player.slimes / 20)
                    weaker_player.change_slimes(n=slimegain)

                    # hunger drain for both players
                    user_data.hunger += ewcfg.hunger_perspar * ewutils.hunger_cost_mod(user_data.slimelevel)
                    sparred_data.hunger += ewcfg.hunger_perspar * ewutils.hunger_cost_mod(sparred_data.slimelevel)

                    # Bonus 50% slime to both players in a duel.
                    if duel:
                        weaker_player.change_slimes(n=slimegain / 2)
                        stronger_player.change_slimes(n=slimegain / 2)

                        if weaker_player.weaponskill < 5 or (weaker_player.weaponskill + 1) < stronger_player.weaponskill:
                            weaker_player.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

                        if stronger_player.weaponskill < 5 or (stronger_player.weaponskill + 1) < weaker_player.weaponskill:
                            stronger_player.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

                    weaker_player.time_lastspar = time_now

                    user_data.persist()
                    sparred_data.persist()
                    # await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

                    # player was sparred with
                    if duel and weapon != None:
                        response = weapon.str_duel.format(name_player=cmd.message.author.display_name, name_target=member.display_name)
                    else:
                        response = '{} parries the attack. :knife: {}'.format(member.display_name, ewcfg.emote_slime5)

                    # Notify if max skill is reached
                    if weapon != None:
                        if user_data.weaponskill >= 5:
                            response += ' {} is a master of the {}.'.format(cmd.message.author.display_name, weapon.id_weapon)
                        if sparred_data.weaponskill >= 5:
                            response += ' {} is a master of the {}.'.format(member.display_name, weapon.id_weapon)

                else:
                    if was_dead:
                        # target is already dead
                        response = '{} is already dead.'.format(member.display_name)
                    elif was_target_tired:
                        # target has sparred too recently
                        response = '{} is too tired to spar right now. They\'ll be ready in {} seconds.'.format(member.display_name, int(timeuntil_target_spar))
                    elif was_player_tired:
                        # player has sparred too recently
                        response = 'You are too tired to spar right now. Try again in {} seconds'.format(int(timeuntil_player_spar))
                    elif was_enemy:
                        # target and player are different factions
                        response = "You cannot spar with your enemies."
                    else:
                        # otherwise unkillable
                        response = '{} cannot spar now.'.format(member.display_name)
    else:
        response = 'Your fighting spirit is appreciated, but ENDLESS WAR didn\'t understand that name.'

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" name a weapon using a slime poudrin """


async def annoint(cmd):
    response = ""

    if cmd.tokens_count < 2:
        response = "Specify a name for your weapon!"
    else:
        annoint_name = cmd.message.content[(len(ewcfg.cmd_annoint)):].strip()

        if len(annoint_name) > 32:
            response = "That name is too long. ({:,}/32)".format(len(annoint_name))
        else:
            user_data = EwUser(member=cmd.message.author)
            if user_data.life_state == ewcfg.life_state_shambler:
                response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            poudrin = bknd_item.find_item(item_search="slimepoudrin", id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)

            all_weapons = bknd_item.inventory(
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_weapon
            )
            for weapon in all_weapons:
                if weapon.get("name") == annoint_name and weapon.get("id_item") != user_data.weapon:
                    response = "**ORIGINAL WEAPON NAME DO NOT STEAL.**"
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            if poudrin is None:
                response = "You need a slime poudrin."
            elif user_data.slimes < 100:
                response = "You need more slime."
            elif user_data.weapon < 0:
                response = "Equip a weapon first."
            else:
                # Perform the ceremony.
                user_data.change_slimes(n=-100, source=ewcfg.source_spending)
                weapon_item = EwItem(id_item=user_data.weapon)
                weapon_item.item_props["weapon_name"] = annoint_name
                weapon_item.persist()

                if user_data.weaponskill < 10:
                    user_data.add_weaponskill(n=1, weapon_type=weapon_item.item_props.get("weapon_type"))

                # delete a slime poudrin from the player's inventory
                bknd_item.item_delete(id_item=poudrin.get('id_item'))

                user_data.persist()

                response = "You place your weapon atop the poudrin and annoint it with slime. It is now known as {}!\n\nThe name draws you closer to your weapon. The poudrin was destroyed in the process.".format(annoint_name)

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" Bind player to active weapon, slightly increase mastery """


async def marry(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    weapon_item = EwItem(id_item=user_data.weapon)
    weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
    display_name = cmd.message.author.display_name
    if weapon != None:
        weapon_name = weapon_item.item_props.get("weapon_name") if len(weapon_item.item_props.get("weapon_name")) > 0 else weapon.str_weapon

    # Checks to make sure you're in the dojo.
    if user_data.poi != ewcfg.poi_id_dojo:
        response = "Do you really expect to just get married on the side of the street in this war torn concrete jungle? No way, you need to see a specialist for this type of thing, someone who can empathize with a man’s love for his arsenal. Maybe someone in the Dojo can help, *hint hint*."
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    # Informs you that you cannot be a fucking faggot.
    elif cmd.mentions_count > 0:
        response = "Ewww, gross! You can’t marry another juvenile! That’s just degeneracy, pure and simple. What happened to the old days, where you could put a bullet in someone’s brain for receiving a hug? You people have gone soft on me, I tells ya."
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    # Makes sure you have a weapon to marry.
    elif weapon is None:
        response = "How do you plan to get married to your weapon if you aren’t holding any weapon? Goddamn, think these things through, I have to spell out everything for you."
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    # Makes sure you have a displayed rank 4 or higher weapon.
    elif user_data.weaponskill < 8:
        response = "Slow down, Casanova. You do not nearly have a close enough bond with your {} to engage in holy matrimony with it. You’ll need to reach rank 4 mastery or higher to get married.".format(weapon_name)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    # Makes sure you aren't trying to farm the extra weapon mastery ranks by marrying over and over again.
    elif user_data.weaponmarried == True:
        response = "Ah, to recapture the magic of the first nights together… Sadly, those days are far behind you now. You’ve already had your special day, now it’s time to have the same boring days forever. Aren’t you glad you got married??"
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        user_data.weaponmarried = True
        user_data.persist()

        # Sets their weaponmarried table to true, so that "you are married to" appears instead of "you are wielding" intheir !data, you get an extra two mastery levels, and you can't change your weapon.
        weapon_item.item_props["married"] = user_data.id_user
        weapon_item.persist()

        # Preform the ceremony 2: literally this time
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "You decide it’s finally time to take your relationship with your {} to the next level. You approach the Dojo Master with your plight, requesting his help to circumvent the legal issues of marrying your weapon. He takes a moment to unfurl his brow before letting out a raspy chuckle. He hasn’t been asked to do something like this for a long time, or so he says. You scroll up to the last instance of this flavor text and conclude he must have Alzheimer's or something. Regardless, he agrees.".format(
                weapon.str_weapon)
        ))
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "Departing from the main floor of the Dojo, he rounds a corner and disappears for a few minutes before returning with illegally doctor marriage paperwork and cartoonish blotches of ink on his face and hands to visually communicate the hard work he’s put into the forgeries. You see, this is a form of visual shorthand that artists utilize so they don’t have to explain every beat of their narrative explicitly, but I digress."
        ))
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "You express your desire to get things done as soon as possible so that you can stop reading this boring wall of text and return to your busy agenda of murder, and so he prepares to officiate immediately. You stand next to your darling {}, the only object of your affection in this godforsaken city. You shiver with anticipation for the most anticipated in-game event of your ENDLESS WAR career. A crowd of enemy and allied gangsters alike forms around you three as the Dojo Master begins the ceremony...".format(
                weapon_name)
        ))
        await asyncio.sleep(3)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "”We are gathered here today to witness the combined union of {} and {}.".format(display_name, weapon_name)
        ))
        await asyncio.sleep(3)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "Two of the greatest threats in the current metagame. No greater partners, no worse adversaries."
        ))
        await asyncio.sleep(3)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "Through thick and thin, these two have stood together, fought together, and gained experience points--otherwise known as “EXP”--together."
        ))
        await asyncio.sleep(3)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "It was not through hours mining or stock exchanges that this union was forged, but through iron and slime."
        ))
        await asyncio.sleep(3)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "Without the weapon, the wielder would be defenseless, and without the wielder, the weapon would have no purpose."
        ))
        await asyncio.sleep(3)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "It is this union that we are here today to officially-illegally affirm.”"
        ))
        await asyncio.sleep(6)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "He takes a pregnant pause to increase the drama, and allow for onlookers to press 1 in preparation."
        ))
        await asyncio.sleep(6)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "“I now pronounce you juvenile and armament!! You may anoint the {}”".format(weapon.str_weapon)
        ))
        await asyncio.sleep(3)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(
            cmd.message.author,
            "You begin to tear up, fondly regarding your last kill with your {} that you love so much. You lean down and kiss your new spouse on the handle, anointing an extra two mastery ranks with pure love. It remains completely motionless, because it is an inanimate object. The Dojo Master does a karate chop midair to bookend the entire experience. Sick, you’re married now!".format(
                weapon_name)
        ))

        user_data = EwUser(member=cmd.message.author)
        user_data.add_weaponskill(n=2, weapon_type=weapon.id_weapon)
        user_data.persist()
        return


""" Destroy Spouse, ending the marriage """


async def divorce(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    weapon_item = EwItem(id_item=user_data.weapon)
    weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
    if weapon != None:
        weapon_name = weapon_item.item_props.get("weapon_name") if len(weapon_item.item_props.get("weapon_name")) > 0 else weapon.str_weapon

    # Makes sure you have a partner to divorce.
    if user_data.weaponmarried == False:
        response = "I appreciate your forward thinking attitude, but how do you expect to get a divorce when you haven’t even gotten married yet? Throw your life away first, then we can talk."
    # Checks to make sure you're in the dojo.
    elif user_data.poi != ewcfg.poi_id_dojo:
        response = "As much as it would be satisfying to just chuck your {} down an alley and be done with it, here in civilization we deal with things *maturely.* You’ll have to speak to the guy that got you into this mess in the first place, or at least the guy that allowed you to make the retarded decision in the first place. Luckily for you, they’re the same person, and he’s at the Dojo.".format(
            weapon.str_weapon)
    # elif user_data.life_state == ewcfg.life_state_juvenile:
    #     response = "The Dojo Master offers annulment services to paying customers only. Enlist in a gang and he'll consider removing you from your hellish facade of a relationship."
    else:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        # Unpreform the ceremony
        response = "You decide it’s finally time to end the frankly obviously retarded farce that is your marriage with your {}. Things were good at first, you both wanted the same things out of life. But, that was then and this is now. You reflect briefly on your myriad of woes; the constant bickering, the mundanity of your everyday routine, the total lack of communication. You’re a slave. But, a slave you will be no longer! You know what you must do." \
                   "\nYou approach the Dojo Master yet again, and explain to him your troubles. He solemnly nods along to every beat of your explanation. Luckily, he has a quick solution. He rips apart the marriage paperwork he forged last flavor text, and just like that you’re divorced from {}. It receives half of your SlimeCoin in the settlement, a small price to pay for your freedom. You hand over what used to be your most beloved possession and partner to the old man, probably to be pawned off to whatever bumfuck juvie waddles into the Dojo next. You don’t care, you just don’t want it in your data. " \
                   "So, yeah. You’re divorced. Damn, that sucks.".format(weapon.str_weapon, weapon_name)

        # You divorce your weapon, discard it, lose it's rank, and loose half your SlimeCoin in the aftermath.
        user_data.weaponmarried = False
        user_data.weapon = -1
        ewutils.weaponskills_set(member=cmd.message.author, weapon=weapon_item.item_props.get("weapon_type"), weaponskill=0)

        fee = (user_data.slimecoin / 2)
        user_data.change_slimecoin(n=-fee, coinsource=ewcfg.coinsource_revival)

        user_data.persist()

        # delete weapon item
        bknd_item.item_delete(id_item=weapon_item.id_item)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def taunt(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    response = ""

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "A bit late for that, don't you think?"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count > 1:
        response = "You can only focus on taunting one person at a time."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count == 1:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)
    else:
        huntedenemy = " ".join(cmd.tokens[1:]).lower()
        target_data = target = cmbt_utils.find_enemy(enemy_search=huntedenemy, user_data=user_data)

    if target_data == None:
        response = "ENDLESS WAR didn't understand that name."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        try:
            if (target_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (target_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
                response = "Hey ASSHOLE! They're on your side!!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            elif (target_data.enemyclass == ewcfg.enemy_class_shambler and target_data.gvs_coord not in ewcfg.gvs_coords_end):
                response = "It's no use, they're too far away!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        except:
            pass

    if target_data.poi != user_data.poi:
        response = "You can't {} someone, who's not even here.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    id_status = ewcfg.status_taunted_id

    target_statuses = target_data.getStatusEffects()

    if id_status in target_statuses:
        response = "{} has already been taunted.".format(target.display_name)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    target_data.applyStatus(id_status=id_status, source=cmd.message.author.id, id_target=cmd.message.author.id)

    user_data.persist()

    response = "You taunt {} into attacking you.".format(target.display_name)
    await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def aim(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    response = ""

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "A bit late for that, don't you think?"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count > 1:
        response = "You can only focus on aiming at one person at a time."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count == 1:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)
    else:
        huntedenemy = " ".join(cmd.tokens[1:]).lower()
        target_data = target = cmbt_utils.find_enemy(enemy_search=huntedenemy, user_data=user_data)

    if target_data == None:
        response = "ENDLESS WAR didn't understand that name."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        try:
            if (target_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (target_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
                response = "Hey ASSHOLE! They're on your side!!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            elif (target_data.enemyclass == ewcfg.enemy_class_shambler and target_data.gvs_coord not in ewcfg.gvs_coords_end):
                response = "It's no use, they're too far away!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        except:
            pass

    if target_data.poi != user_data.poi:
        response = "You can't {} at someone, who's not even here.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    id_status = ewcfg.status_aiming_id

    user_data.clear_status(id_status=id_status)

    user_data.applyStatus(id_status=id_status, source=cmd.message.author.id, id_target=(target.id if target_data.combatant_type == "player" else target_data.id_enemy))

    user_data.persist()

    response = "You aim at {}'s weak spot.".format(target.display_name)
    await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def dodge(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    response = ""

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "A bit late for that, don't you think?"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count > 1:
        response = "You can only focus on dodging one person at a time."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count == 1:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)
    else:
        huntedenemy = " ".join(cmd.tokens[1:]).lower()
        target_data = target = cmbt_utils.find_enemy(enemy_search=huntedenemy, user_data=user_data)

    if target_data == None:
        response = "ENDLESS WAR didn't understand that name."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        try:
            if (target_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (target_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
                response = "Hey ASSHOLE! They're on your side!!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            elif (target_data.enemyclass == ewcfg.enemy_class_shambler and target_data.gvs_coord not in ewcfg.gvs_coords_end):
                response = "It's no use, they're too far away!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        except:
            pass

    if target_data.poi != user_data.poi:
        response = "You can't {} someone, who's not even here.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    id_status = ewcfg.status_evasive_id

    user_data.clear_status(id_status=id_status)

    user_data.applyStatus(id_status=id_status, source=cmd.message.author.id, id_target=(target.id if target_data.combatant_type == "player" else target_data.id_enemy))

    user_data.persist()

    response = "You focus on dodging {}'s attacks.".format(target.display_name)
    await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" Attack the control of a district, or buff your team's control """


async def spray(cmd):
    roomba_loop = 0
    while True:
        # Get user data, then flag for PVP
        user_data = EwUser(id_user=cmd.message.author.id, id_server=cmd.guild.id)

        market_data = EwMarket(id_server=cmd.guild.id)
        time_current = market_data.clock

        time_now_float = time.time()
        time_now = int(time_now_float)

        # Get shooting player's info
        weapon = None
        weapon_item = None
        sidearm_viable = 0
        user_mutations = user_data.get_mutations()

        # if user_data.sidearm >= 0:
        #	weapon_item = EwItem(id_item=user_data.sidearm)
        #	weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
        #	captcha = weapon_item.item_props.get('captcha')
        #	if ewcfg.weapon_class_paint in weapon.classes:
        #		sidearm_viable = 1

        if user_data.weapon >= 0 and sidearm_viable == 0:
            weapon_item = EwItem(id_item=user_data.weapon)
            weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
            captcha = weapon_item.item_props.get('captcha')

        if weapon_item is not None and roomba_loop == 0:
            if weapon_item.item_props.get("weapon_type") == 'roomba':
                if weapon_item.item_props.get("roomba") == user_data.poi:
                    weapon_item.item_props['roomba'] = ""
                    weapon_item.persist()
                    response = "You pick the roomba back up and have it stop spraying down the floor."
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                else:
                    weapon_item.item_props['roomba'] = user_data.poi
                    weapon_item.persist()

        response = canCap(cmd, "spray", roomba_loop)

        if response == "":
            if user_data.slimelevel <= 0:
                user_data.slimelevel = 1
                user_data.persist()

            # Get district data
            poi = poi_static.id_to_poi.get(user_data.poi)
            district_data = EwDistrict(id_server=cmd.guild.id, district=poi.id_poi)

            gangsters_in_district = district_data.get_players_in_district(min_slimes=ewcfg.min_slime_to_cap, life_states=[ewcfg.life_state_enlisted], ignore_offline=True)

            miss = False
            crit = False
            bystander_damage = 0
            hit_chance_mod = 0
            crit_mod = 0
            dmg_mod = 0
            # sap_damage = 0
            # sap_ignored = 0

            weapon.fn_effect = static_weapons.weapon_type_convert.get(weapon.id_weapon)

            shooter_status_mods = cmbt_utils.get_shooter_status_mods(user_data, None, None)

            hit_chance_mod += round(shooter_status_mods['hit_chance'], 2)
            crit_mod += round(shooter_status_mods['crit'], 2)
            dmg_mod += round(shooter_status_mods['dmg'], 2)

            slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 300)
            slimes_damage = int((50000 + slimes_spent * 10) * (100 + (user_data.weaponskill * 5)) / 100.0)
            slimes_spent = round(slimes_spent * .1125)
            statuses = user_data.getStatusEffects()

            if weapon is None:
                slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons

            slimes_damage += int(slimes_damage * dmg_mod)
            # user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)

            if weapon != None and weapon.fn_effect != None:
                # Build effect container
                ctn = EwEffectContainer(
                    miss=miss,
                    crit=crit,
                    slimes_damage=slimes_damage,
                    slimes_spent=slimes_spent,
                    user_data=user_data,
                    weapon_item=weapon_item,
                    shootee_data=None,
                    time_now=time_now,
                    bystander_damage=bystander_damage,
                    hit_chance_mod=hit_chance_mod,
                    crit_mod=crit_mod,
                    market_data=market_data,
                    # sap_damage=sap_damage,
                    # sap_ignored=sap_ignored,
                )

                # Make adjustments

                weapon.fn_effect(ctn)

                # Apply effects for non-reference values
                resp_cont = EwResponseContainer(id_server=cmd.guild.id)
                miss = ctn.miss
                crit = ctn.crit
                slimes_damage = ctn.slimes_damage
                slimes_spent = ctn.slimes_spent
                # sap_damage = ctn.sap_damage

                if miss is True and random.randint(0, 1) == 0:
                    miss = False

                if (slimes_spent > user_data.slimes):
                    # Not enough slime to shoot.
                    response = "You don't have enough slime to cap. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                weapon_item.item_props['time_lastattack'] = time_now_float
                weapon_item.persist()
                user_data.change_slimes(n=(-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent), source=ewcfg.source_spending)
                user_data.persist()

                # Remove a bullet from the weapon
                if ewcfg.weapon_class_ammo in weapon.classes:
                    weapon_item.item_props['ammo'] = int(weapon_item.item_props.get("ammo")) - 1

                if miss:
                    slimes_damage = 0

                    weapon_item.item_props["consecutive_hits"] = 0
                    crit = False
                weapon_item.persist()
                # Remove !revive invulnerability.
                user_data.time_lastrevive = 0
                market_data = EwMarket(id_server=cmd.guild.id)
                # apply attacker damage mods
                slimes_damage *= cmbt_utils.damage_mod_cap(
                    user_data=user_data,
                    user_mutations=user_mutations,
                    market_data=market_data,
                    district_data=district_data,
                    weapon=weapon
                )

                if weapon.id_weapon == ewcfg.weapon_id_watercolors:
                    if not miss:
                        slimes_damage = ewcfg.min_garotte
                # if (user_data.faction != district_data.controlling_faction and (user_data.faction is None or user_data.faction == '')) and district_data.capture_points > ewcfg.limit_influence[district_data.property_class]:
                #	slimes_damage = round(slimes_damage / 5)
                #	pass
                if weapon != None:
                    if miss:
                        response = weapon.tool_props[0].get('miss_spray')
                    else:

                        response = weapon.tool_props[0].get('reg_spray').format(gang=user_data.faction[:-1].capitalize(), curse=random.choice(list(ewcfg.curse_words.keys())))
                        response += " You got {:,} influence for the {}!".format(int(abs(slimes_damage)), user_data.faction.capitalize())

                        if (user_data.faction != district_data.cap_side and district_data.cap_side != "") and (user_data.faction is not None or user_data.faction != ''):
                            slimes_damage = round(slimes_damage * -.8)
                        # district_data.change_capture_points()

                        district_data.change_capture_points(progress=slimes_damage, actor=user_data.faction)

                        if crit and weapon.id_weapon == ewcfg.weapon_id_watercolors:
                            district_data.change_capture_points(progress=-district_data.capture_points, actor=user_data.faction)

                        district_data.persist()

                        district_data = EwDistrict(district=district_data.name, id_server=district_data.id_server)
                        # district_data.capture_points += slimes_damage
                        # if district_data.capture_points < 0:
                        #	district_data.controlling_faction = user_data.faction
                        #	district_data.capture_points *= -1
                        # district_data.persist()
                        # response = weapon.str_damage.format(
                        #	name_player=cmd.message.author.display_name,
                        #	name_target=enemy_data.display_name,
                        #	hitzone=randombodypart,
                        #	strikes=strikes
                        # )

                        if crit:
                            if user_data.faction == ewcfg.faction_rowdys:
                                color = "pink"
                            elif user_data.faction == "slimecorp":
                                color = "Slimecorp propaganda"
                            else:
                                color = "purple"
                            response = user_data.spray + "\n\n"
                            response += weapon.tool_props[0].get('crit_spray').format(color=color)
                            response += " It gets you {:,} influence!".format(abs(slimes_damage))
                    # response += " {}".format(weapon.str_crit.format(
                    #	name_player=cmd.message.author.display_name,
                    #	name_target=enemy_data.display_name,
                    #	hitzone=randombodypart,
                    # ))

                    if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
                        response += "\n" + weapon.str_reload_warning.format(
                            name_player=cmd.message.author.display_name)

                    if (ewcfg.weapon_class_captcha in weapon.classes) and roomba_loop == 0:
                        if weapon.id_weapon != ewcfg.weapon_id_paintgun:
                            new_captcha_low = ewutils.generate_captcha(length=weapon.captcha_length, user_data=user_data)
                            new_captcha = ewutils.text_to_regional_indicator(new_captcha_low)
                            # new_loc = new_loc.replace(new_captcha_low, new_captcha)
                            response += "\nNew captcha is {}.".format(new_captcha)
                            weapon_item.item_props['captcha'] = new_captcha_low
                        # new_captcha = ewutils.generate_captcha(length = weapon.captcha_length)
                        else:
                            riflearray = ewcfg.riflecap
                            direction = str(random.choice(riflearray))
                            weapon_item.item_props['captcha'] = direction
                            new_captcha_gun = ewutils.text_to_regional_indicator(direction)
                            response += "\nNext target is {}.".format(new_captcha_gun)
                        weapon_item.persist()

                    if district_data.controlling_faction == user_data.faction and abs(district_data.capture_points) >= ewcfg.limit_influence[poi.property_class]:
                        if user_data.faction == ewcfg.faction_rowdys:
                            color = "pink"
                        elif user_data.faction == "slimecorp":
                            color = "Slimecorp propaganda"
                        else:
                            color = "purple"
                        response += "\nThe street is awash in a sea of {}. It's hard to imagine where else you could spray down.".format(color)
                    elif district_data.controlling_faction == user_data.faction and abs(district_data.capture_points) > (ewcfg.min_influence[poi.property_class] + ewcfg.limit_influence[poi.property_class]) / 2:
                        response += "\nThe {} have developed a decent grip on this district.".format(user_data.faction)
                    elif district_data.controlling_faction == user_data.faction and abs(district_data.capture_points) > ewcfg.min_influence[poi.property_class]:
                        response += "\nThe {} have developed a loose grip on this district.".format(user_data.faction)
            else:
                if miss:
                    response = "You spray something so obscure nobody notices."
                else:
                    response = "Nice vandalism! You get {damage} influence out of it!".format(
                        damage=abs(slimes_damage)
                    )
        else:
            if weapon_item is not None:
                weapon_item.item_props['roomba'] = ""
                weapon_item.persist()
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        user_data = EwUser(member=cmd.message.author)
        if user_data.weapon >= 0:
            weapon_item = EwItem(id_item=user_data.weapon)
            if weapon_item.item_props.get('roomba') == user_data.poi:
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                await asyncio.sleep(7)
                roomba_loop = 1
            else:
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" Attack control of a district, slimecorp only """


async def sanitize(cmd):
    roomba_loop = 0
    while 1:
        # Get user data, then flag for PVP
        user_data = EwUser(id_user=cmd.message.author.id, id_server=cmd.guild.id)

        market_data = EwMarket(id_server=cmd.guild.id)
        time_current = market_data.clock

        time_now_float = time.time()
        time_now = int(time_now_float)

        user_data.persist()

        # Get shooting player's info

        weapon = None
        weapon_item = None
        sidearm_viable = 0
        user_mutations = user_data.get_mutations()

        # if user_data.sidearm >= 0:
        #	weapon_item = EwItem(id_item=user_data.sidearm)
        #	weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
        #	captcha = weapon_item.item_props.get('captcha')
        #	if ewcfg.weapon_class_paint in weapon.classes:
        #		sidearm_viable = 1

        if user_data.weapon >= 0 and sidearm_viable == 0:
            weapon_item = EwItem(id_item=user_data.weapon)
            weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
            captcha = weapon_item.item_props.get('captcha')

        if weapon_item is not None and roomba_loop == 0:
            if weapon_item.item_props.get("weapon_type") == 'roomba':
                if weapon_item.item_props.get("roomba") == user_data.poi:
                    weapon_item.item_props['roomba'] = ""
                    weapon_item.persist()
                    response = "You pick the roomba back up and have it stop cleaning up the floor."
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                else:
                    weapon_item.item_props['roomba'] = user_data.poi
                    weapon_item.persist()

        response = canCap(cmd, "sanitize", roomba_loop)
        if response == "":
            if user_data.slimelevel <= 0:
                user_data.slimelevel = 1
                user_data.persist()

            # Get district data
            poi = poi_static.id_to_poi.get(user_data.poi)
            district_data = EwDistrict(id_server=cmd.guild.id, district=poi.id_poi)

            gangsters_in_district = district_data.get_players_in_district(min_slimes=ewcfg.min_slime_to_cap, life_states=[ewcfg.life_state_enlisted], ignore_offline=True)

            miss = False
            crit = False

            bystander_damage = 0
            hit_chance_mod = 0
            crit_mod = 0
            dmg_mod = 0
            # sap_damage = 0
            # sap_ignored = 0

            weapon.fn_effect = static_weapons.weapon_type_convert.get(weapon.id_weapon)

            shooter_status_mods = cmbt_utils.get_shooter_status_mods(user_data, None, None)

            hit_chance_mod += round(shooter_status_mods['hit_chance'], 2)
            crit_mod += round(shooter_status_mods['crit'], 2)
            dmg_mod += round(shooter_status_mods['dmg'], 2)

            slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 300)
            slimes_damage = int((50000 + slimes_spent * 10) * (100 + (user_data.weaponskill * 5)) / 100.0)
            slimes_spent = round(slimes_spent * .1125)
            statuses = user_data.getStatusEffects()

            if weapon is None:
                slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons

            slimes_damage += int(slimes_damage * dmg_mod)
            # user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)

            if weapon != None and weapon.fn_effect != None:
                # Build effect container
                ctn = EwEffectContainer(
                    miss=miss,
                    crit=crit,
                    slimes_damage=slimes_damage,
                    slimes_spent=slimes_spent,
                    user_data=user_data,
                    weapon_item=weapon_item,
                    shootee_data=None,
                    time_now=time_now,
                    bystander_damage=bystander_damage,
                    hit_chance_mod=hit_chance_mod,
                    crit_mod=crit_mod,
                    market_data=market_data,
                    # sap_damage=sap_damage,
                    # sap_ignored=sap_ignored,
                )

                # Make adjustments

                weapon.fn_effect(ctn)

                # Apply effects for non-reference values
                resp_cont = EwResponseContainer(id_server=cmd.guild.id)
                miss = ctn.miss
                crit = ctn.crit
                slimes_damage = ctn.slimes_damage
                slimes_spent = ctn.slimes_spent
                # sap_damage = ctn.sap_damage

                if miss is True and random.randint(0, 1) == 0:
                    miss = False

                if (slimes_spent > user_data.slimes):
                    # Not enough slime to shoot.
                    response = "You don't have enough slime to sanitize. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                # if district_data.controlling_faction == "" and district_data.capture_points == 0:
                #	response = "There's no graffiti to clean up here."
                #	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                weapon_item.item_props['time_lastattack'] = time_now_float
                weapon_item.persist()
                user_data.change_slimes(n=(-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent), source=ewcfg.source_spending)
                user_data.persist()

                # Remove a bullet from the weapon
                if ewcfg.weapon_class_ammo in weapon.classes:
                    weapon_item.item_props['ammo'] = int(weapon_item.item_props.get("ammo")) - 1

                if miss:
                    slimes_damage = 0

                    weapon_item.item_props["consecutive_hits"] = 0
                    crit = False
                weapon_item.persist()
                # Remove !revive invulnerability.
                user_data.time_lastrevive = 0
                market_data = EwMarket(id_server=cmd.guild.id)
                # apply attacker damage mods
                slimes_damage *= cmbt_utils.damage_mod_attack(
                    user_data=user_data,
                    user_mutations=user_mutations,
                    market_data=market_data,
                    district_data=district_data
                )
                if weapon.id_weapon == ewcfg.weapon_id_watercolors:
                    if not miss:
                        slimes_damage = ewcfg.min_garotte

                elif weapon.id_weapon == ewcfg.weapon_id_thinnerbomb:
                    if user_data.faction == district_data.controlling_faction:
                        slimes_damage = round(slimes_damage * .2)
                    else:
                        slimes_damage *= 3

                if ewcfg.mutation_id_patriot in user_mutations:
                    slimes_damage *= 1.25
                if len(gangsters_in_district) == 1 and ewcfg.mutation_id_lonewolf in user_mutations:
                    slimes_damage *= 1.25

                if 3 <= time_current <= 10:
                    slimes_damage *= (4 / 3)

                credits_added = int(abs(slimes_damage)) * 25

                # if (user_data.faction != district_data.controlling_faction and (user_data.faction is None or user_data.faction == '')) and district_data.capture_points > ewcfg.limit_influence[district_data.property_class]:
                #	slimes_damage = round(slimes_damage / 5)
                #	pass
                if weapon != None:
                    if miss:
                        response = weapon.tool_props[0].get('miss_spray')
                    else:
                        response = "Your sanitizer-filled {} washes away the filth from the city streets.".format(weapon.str_name)
                        response += " You removed {:,} existing influence from gangsters.".format(int(abs(slimes_damage)))

                        if district_data.cap_side == "slimecorp" or district_data.cap_side == "":
                            response = "Your paint-filled {} covers the city in Slimecorp propaganda.".format(weapon.str_name)
                            response += " You added {:,} existing influence for Slimecorp.".format(round(int(abs(slimes_damage))))

                        if (user_data.faction != district_data.cap_side and district_data.cap_side != "") and (user_data.faction is not None or user_data.faction != ''):
                            slimes_damage = round(slimes_damage * -.8)
                        # district_data.change_capture_points()

                        district_data.change_capture_points(progress=slimes_damage, actor=user_data.faction)

                        if crit and weapon.id_weapon == ewcfg.weapon_id_watercolors: district_data.change_capture_points(progress=-district_data.capture_points, actor=user_data.faction)

                        district_data.persist()

                        district_data = EwDistrict(district=district_data.name, id_server=district_data.id_server)
                        # district_data.capture_points += slimes_damage
                        # if district_data.capture_points < 0:
                        #	district_data.controlling_faction = user_data.faction
                        #	district_data.capture_points *= -1
                        # district_data.persist()
                        # response = weapon.str_damage.format(
                        #	name_player=cmd.message.author.display_name,
                        #	name_target=enemy_data.display_name,
                        #	hitzone=randombodypart,
                        #	strikes=strikes
                        # )
                        if (district_data.cap_side == "slimecorp" or district_data.cap_side == '') == "" and crit:
                            response += " You score a critical hit adding {:,} additional influence!".format(round(abs(slimes_damage)))
                        elif crit:
                            response += " You score a critical hit, removing {:,} additional influence!".format(abs(slimes_damage))

                        response += " {:,} salary credits have been added to your profile.".format(credits_added)
                        user_data.salary_credits += credits_added
                        user_data.persist()

                    # response += " {}".format(weapon.str_crit.format(
                    #	name_player=cmd.message.author.display_name,
                    #	name_target=enemy_data.display_name,
                    #	hitzone=randombodypart,
                    # ))

                    if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
                        response += "\n" + weapon.str_reload_warning.format(name_player=cmd.message.author.display_name)

                    if (ewcfg.weapon_class_captcha in weapon.classes) and roomba_loop == 0:
                        if weapon.id_weapon != ewcfg.weapon_id_paintgun:
                            new_captcha_low = ewutils.generate_captcha(length=weapon.captcha_length)
                            new_captcha = ewutils.text_to_regional_indicator(new_captcha_low)
                            # new_loc = new_loc.replace(new_captcha_low, new_captcha)
                            response += "\nNew captcha is {}.".format(new_captcha)
                            weapon_item.item_props['captcha'] = new_captcha_low
                        # new_captcha = ewutils.generate_captcha(length = weapon.captcha_length)
                        else:
                            riflearray = ewcfg.riflecap
                            direction = str(random.choice(riflearray))
                            weapon_item.item_props['captcha'] = direction
                            new_captcha_gun = ewutils.text_to_regional_indicator(direction)
                            response += "\nNext target is {}.".format(new_captcha_gun)
                        weapon_item.persist()

            else:
                if miss:
                    response = "Your sanitizer completely misses any graffiti..."
                else:
                    response = "Nice community service effort! You clean {damage} influence off the streets!".format(
                        damage=abs(slimes_damage)
                    )
        else:
            if user_data.weapon >= 0:
                weapon_item = EwItem(id_item=user_data.weapon)
                weapon_item.item_props['roomba'] = ""
                weapon_item.persist()
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        user_data = EwUser(member=cmd.message.author)
        if user_data.weapon >= 0:
            weapon_item = EwItem(id_item=user_data.weapon)
            if weapon_item.item_props.get('roomba') == user_data.poi:
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                await asyncio.sleep(7)
                roomba_loop = 1
            else:
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" Switch to set sidearm """


async def switch_weapon(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.weaponmarried:
        response = "You don't have the heart to cheat on your wife with your side ho. Not right in front of her. Not like this."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    weapon_holder = user_data.weapon
    user_data.weapon = user_data.sidearm
    user_data.sidearm = weapon_holder
    user_data.persist()

    if user_data.weapon == -1 and user_data.sidearm == -1:
        response = "You switch your nothing for nothing. What a notable exchange."
    elif user_data.weapon == -1 and user_data.sidearm:
        response = "You put your weapon away."
    elif user_data.weapon >= 0:
        weapon_item = EwItem(id_item=user_data.weapon)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
        response = "**FWIP-CLICK!** You whip out your {}.".format(weapon_item.item_props.get("weapon_name") if weapon_item.item_props.get("weapon_name") != "" else weapon.str_name)
        if ewcfg.weapon_class_captcha in weapon.classes:
            newcaptcha = ewutils.text_to_regional_indicator(weapon_item.item_props.get('captcha'))
            response += " New captcha is {}.".format(newcaptcha)
    else:
        response = ""
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def null_cmd(cmd):
    return


async def duel(cmd):
    time_now = int(time.time())

    if cmd.mentions_count != 1:
        # Must mention only one player
        response = "Mention the player you want to challenge."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    author = cmd.message.author
    member = cmd.mentions[0]

    if author.id == member.id:
        response = "You might be looking for !suicide."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    challenger = EwUser(member=author)
    challengee = EwUser(member=member)

    if challenger.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif challengee.life_state == ewcfg.life_state_shambler:
        response = "They lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    challenger_poi = poi_static.id_to_poi.get(challenger.poi)
    challengee_poi = poi_static.id_to_poi.get(challengee.poi)
    if not challenger_poi.is_district or not challengee_poi.is_district:
        response = "Both participants need to be in a district zone."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # Players have been challenged
    if ewutils.active_target_map.get(challenger.id_user) != None and ewutils.active_target_map.get(challenger.id_user) != "":
        response = "You are already in the middle of a challenge."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    if ewutils.active_target_map.get(challengee.id_user) != None and ewutils.active_target_map.get(challengee.id_user) != "":
        response = "{} is already in the middle of a challenge.".format(member.display_name).replace("@", "\{at\}")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    if challenger.poi != challengee.poi:
        response = "Both duelers must be in the same location."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    # Players have to be enlisted
    playable_life_states = [ewcfg.life_state_enlisted, ewcfg.life_state_lucky, ewcfg.life_state_executive]
    if challenger.life_state not in playable_life_states or challengee.life_state not in playable_life_states:
        if challenger.life_state == ewcfg.life_state_corpse:
            response = "Ghosts can't duel people. Alas, they can only watch from afar and !haunt."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
        elif challengee.life_state == ewcfg.life_state_corpse:
            response = "Ghosts can't duel people. Alas, they can only watch from afar and !haunt."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
        elif challenger.life_state == ewcfg.life_state_kingpin:
            response = "Throwing all of your gang's hard earned slime on the line strikes you as a bad idea..."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
        elif challengee.life_state == ewcfg.life_state_kingpin:
            response = "They think about accepting for a moment, but then back away, remembering all the hard work their gangsters have put forth. Bummer..."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
    # else:
    # 	response = "Juveniles are too cowardly to throw their lives away in a duel."
    # 	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    # Assign a challenger so players can't be challenged
    ewutils.active_target_map[challenger.id_user] = challengee.id_user
    ewutils.active_target_map[challengee.id_user] = challenger.id_user

    # Apply restrictions to prevent movement, !tp, etc. This also lets the !accept command differentiate RR from duels.
    ewutils.active_restrictions[challenger.id_user] = 2
    ewutils.active_restrictions[challengee.id_user] = 2

    response = "You have been challenged by {} to a duel. Do you !accept or !refuse?".format(author.display_name).replace("@", "\{at\}")
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(member, response))

    # Wait for an answer
    accepted = False
    try:
        msg = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == member and
                                                                                     message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

        if msg != None:
            if msg.content == ewcfg.cmd_accept:
                accepted = True
    except:
        accepted = False

    # Start game
    if accepted == 1:
        challenger = EwUser(member=author)
        challengee = EwUser(member=member)

        # Start the countdown. Set restriction level to 3, which causes either user to die if they type during the countdown.
        ewutils.active_restrictions[challenger.id_user] = 3
        ewutils.active_restrictions[challengee.id_user] = 3

        countdown = 10

        while countdown != 0:
            # check if either user has had their restriction level set back to 0, indicating a death.
            if ewutils.active_restrictions[challenger.id_user] == 0 or ewutils.active_restrictions[challengee.id_user] == 0:
                ewutils.active_target_map[challenger.id_user] = ""
                ewutils.active_target_map[challengee.id_user] = ""

                ewutils.active_restrictions[challenger.id_user] = 0
                ewutils.active_restrictions[challengee.id_user] = 0

                response = "The duel is over before it even began."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, response)

            if countdown > 8:
                text_mod = ""
            elif countdown > 6:
                text_mod = "*"
            elif countdown > 3:
                text_mod = "**"
            else:
                text_mod = "***"

            if countdown == 10:
                countdown_resp = "ENDLESS WAR begins to count down. Don't try anything funny...\n{}{}{}".format(text_mod, countdown, text_mod)
            else:
                countdown_resp = "{}{}{}".format(text_mod, countdown, text_mod)

            countdown -= 1
            await fe_utils.send_message(cmd.client, cmd.message.channel, countdown_resp)
            await asyncio.sleep(1)
            challenger = EwUser(member=author)
            challengee = EwUser(member=member)

        ewutils.active_restrictions[challenger.id_user] = 2
        ewutils.active_restrictions[challengee.id_user] = 2

        response = "{}***DRAW!***{}".format(ewcfg.emote_slimegun, ewcfg.emote_slimegun)
        await fe_utils.send_message(cmd.client, cmd.message.channel, response)

        await ewrolemgr.updateRoles(client=cmd.client, member=author)
        await ewrolemgr.updateRoles(client=cmd.client, member=member)
        challenger = EwUser(member=author)
        challengee = EwUser(member=member)

        duel_timer = ewcfg.time_pvp_duel

        challenger_slimes = challenger.slimes
        challengee_slimes = challengee.slimes

        while challenger_slimes > 0 and challengee_slimes > 0 and duel_timer > 0:
            # count down from 2 minutes, the max possible time a duel should last
            duel_timer -= 1
            await asyncio.sleep(1)

            # re-grab slime counts from both duelers
            challenger = EwUser(member=author)
            challengee = EwUser(member=member)
            challenger_slimes = challenger.slimes
            challengee_slimes = challengee.slimes

        if challenger.slimes <= 0:
            # challenger lost
            response = "**{} has won the duel!!**".format(member.display_name).replace("@", "\{at\}")
            await fe_utils.send_message(cmd.client, cmd.message.channel, response)
            challengee = EwUser(member=member)

        elif challengee.slimes <= 0:
            # challengee lost
            response = "**{} has won the duel!!**".format(author.display_name).replace("@", "\{at\}")
            await fe_utils.send_message(cmd.client, cmd.message.channel, response)
            challenger = EwUser(member=author)

        else:
            # timer stall
            response = "**Neither dueler was bloodthirsty enough to finish the job in time! The duel is over!**"
            await fe_utils.send_message(cmd.client, cmd.message.channel, response)

        await ewrolemgr.updateRoles(client=cmd.client, member=author)
        await ewrolemgr.updateRoles(client=cmd.client, member=member)


    # Or cancel the challenge
    else:
        response = "{} was too cowardly to accept your challenge.".format(member.display_name).replace("@", "\{at\}")
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    challenger = EwUser(member=author)
    challengee = EwUser(member=member)

    ewutils.active_target_map[challenger.id_user] = ""
    ewutils.active_target_map[challengee.id_user] = ""

    ewutils.active_restrictions[challenger.id_user] = 0
    ewutils.active_restrictions[challengee.id_user] = 0

    challenger.persist()
    challengee.persist()

    return
