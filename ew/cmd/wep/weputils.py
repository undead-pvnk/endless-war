import asyncio
import math
import random
import time

from ew.backend import hunting as bknd_hunt
from ew.backend.dungeons import EwGamestate
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
from ew.utils import move as move_utils
from ew.utils import stats as ewstats
from ew.utils.combat import EwEnemy
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict
from ew.utils.frontend import EwResponseContainer

""" A data-moving class which holds references to objects we want to modify with weapon effects. """


class EwEffectContainer:
    miss = False
    crit = False
    slimes_damage = 0
    slimes_spent = 0
    user_data = None
    shootee_data = None
    market_data = None
    weapon_item = None
    time_now = 0
    bystander_damage = 0
    hit_chance_mod = 0
    crit_mod = 0

    explode = False
    apply_status = None
    mass_apply_status = None
    # sap_damage = 0
    # sap_ignored = 0

    # Debug method to dump out the members of this object.
    def dump(self):
        print("effect:\nmiss: {miss}\ncrit: {crit}\nslimes_damage: {slimes_damage}\nslimes_spent: {slimes_spent}\nexplosion_dmg: {bystander_damage}".format(
            miss=self.miss,
            crit=self.crit,
            slimes_damage=self.slimes_damage,
            slimes_spent=self.slimes_spent,
            bystander_damage=self.bystander_damage
        ))

    def __init__(
            self,
            miss = False,
            crit = False,
            slimes_damage = 0,
            slimes_spent = 0,
            user_data = None,
            shootee_data = None,
            weapon_item = None,
            time_now = 0,
            bystander_damage = 0,
            hit_chance_mod = 0,
            crit_mod = 0,
            market_data = None,
            # sap_damage = 0,
            # sap_ignored = 0,
    ):
        self.miss = miss
        self.crit = crit
        self.slimes_damage = slimes_damage
        self.slimes_spent = slimes_spent
        self.user_data = user_data
        self.shootee_data = shootee_data
        self.weapon_item = weapon_item
        self.time_now = time_now
        self.bystander_damage = bystander_damage
        self.hit_chance_mod = hit_chance_mod
        self.crit_mod = crit_mod
        self.market_data = market_data


# self.sap_damage = sap_damage
# self.sap_ignored = sap_ignored


def apply_status_bystanders(user_data = None, value = 0, life_states = None, factions = None, district_data = None, status = None):
    if life_states != None and factions != None and district_data != None and status != None:
        bystander_users = district_data.get_players_in_district(life_states=life_states, factions=factions, pvp_only=True)
        resp_cont = EwResponseContainer(id_server=user_data.id_server)
        channel = poi_static.id_to_poi.get(district_data.name).channel
        market_data = EwMarket(id_server=user_data.id_server)

        for bystander in bystander_users:
            bystander_user_data = EwUser(id_user=bystander, id_server=user_data.id_server)
            bystander_player_data = EwPlayer(id_user=bystander, id_server=user_data.id_server)
            bystander_mutation = bystander_user_data.get_mutations()

            if market_data.weather == ewcfg.weather_rainy and status == ewcfg.status_burning_id:
                if ewcfg.mutation_id_napalmsnot in bystander_mutation or (ewcfg.mutation_id_airlock in bystander_mutation): 
                    return
                else:
                    value = value // 2
        
            resp = bystander_user_data.applyStatus(id_status=status, value=value, source=user_data.id_user).format(name_player=bystander_player_data.display_name)
            resp_cont.add_channel_response(channel, resp)


        bystander_enemies = district_data.get_enemies_in_district()

        for bystander in bystander_enemies:
            bystander_enemy_data = EwEnemy(id_enemy=bystander, id_server=user_data.id_server)
            resp = bystander_enemy_data.applyStatus(id_status=status, value=value, source=user_data.id_user).format(name_player=bystander_enemy_data.display_name)
            resp_cont.add_channel_response(channel, resp)

        return resp_cont


def weapon_explosion(user_data = None, shootee_data = None, district_data = None, market_data = None, life_states = None, factions = None, slimes_damage = 0, time_now = 0, target_enemy = None):
    enemy_data = None
    if user_data != None and shootee_data != None and district_data != None:
        user_player = EwPlayer(id_user=user_data.id_user, id_server=user_data.id_server)
        user_mutations = user_data.get_mutations()
        if target_enemy == False:
            shootee_player = EwPlayer(id_user=shootee_data.id_user, id_server=shootee_data.id_server)
        else:
            enemy_data = shootee_data

            # This makes it so that a display name can still be accessed regardless if a player or enemy is the target of the attack
            shootee_player = shootee_data

        weapon_item = EwItem(id_item=user_data.weapon)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))

        client = ewutils.get_client()
        server = client.get_guild(user_data.id_server)

        channel = poi_static.id_to_poi.get(user_data.poi).channel

        resp_cont = EwResponseContainer(id_server=user_data.id_server)

        bystander_users = district_data.get_players_in_district(life_states=life_states, factions=factions, pvp_only=True)
        bystander_enemies = district_data.get_enemies_in_district()

        for bystander in bystander_users:
            # Don't damage the shooter or the shootee a second time

            # If an enemy is being targeted, check id_enemy instead of id_user when going through bystander_users
            checked_id = None
            if target_enemy:
                checked_id = shootee_data.id_enemy
            else:
                checked_id = shootee_data.id_user

            if bystander != user_data.id_user and bystander != checked_id:
                response = ""

                target_data = EwUser(id_user=bystander, id_server=user_data.id_server, data_level=1)
                target_player = EwPlayer(id_user=bystander, id_server=user_data.id_server)

                target_iskillers = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_killers
                target_isrowdys = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_rowdys
                target_isslimecorp = target_data.life_state == ewcfg.life_state_enlisted and target_data.life_state == ewcfg.faction_slimecorp
                target_isjuvenile = target_data.life_state == ewcfg.life_state_juvenile
                target_isshambler = target_data.life_state == ewcfg.life_state_shambler

                role_boss = (ewcfg.role_copkiller if user_data.faction == ewcfg.faction_killers else ewcfg.role_rowdyfucker)
                boss_slimes = 0

                target_weapon = None
                if target_data.weapon >= 0:
                    target_weapon_item = EwItem(id_item=target_data.weapon)
                    target_weapon = static_weapons.weapon_map.get(target_weapon_item.item_props.get("weapon_type"))

                # apply defensive mods
                slimes_damage_target = slimes_damage * cmbt_utils.damage_mod_defend(
                    shootee_data=target_data,
                    shootee_mutations=target_data.get_mutations(),
                    shootee_weapon=target_weapon,
                    market_data=market_data,
                )

                # apply sap armor
                # sap_armor = get_sap_armor(shootee_data = target_data, sap_ignored = sap_ignored)
                # slimes_damage_target *= sap_armor
                # slimes_damage_target = int(max(0, slimes_damage_target))

                # disabled until held items update
                # fashion_armor = get_fashion_armor(target_data)
                # slimes_damage_target *= fashion_armor
                slimes_damage_target = int(max(0, slimes_damage_target))

                slimes_dropped = target_data.totaldamage + target_data.slimes

                was_killed = False

                if slimes_damage_target >= target_data.slimes - target_data.bleed_storage:
                    was_killed = True
                    slimes_damage_target = max(target_data.slimes - target_data.bleed_storage, 0)

                sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=user_data.id_server)

                # move around slime as a result of the shot
                if target_isshambler or target_isjuvenile or user_data.faction == target_data.faction or user_data.life_state == ewcfg.life_state_juvenile:
                    slimes_drained = int(3 * slimes_damage_target / 4)  # 3/4
                    slimes_toboss = 0
                else:
                    slimes_drained = 0
                    slimes_toboss = int(slimes_damage_target / 2)

                damage = slimes_damage_target

                slimes_tobleed = int((slimes_damage_target - slimes_toboss - slimes_drained) / 2)

                slimes_directdamage = slimes_damage_target - slimes_tobleed
                slimes_splatter = slimes_damage_target - slimes_toboss - slimes_tobleed - slimes_drained

                if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
                    user_data.change_slimes(n=slimes_splatter * 0.6, source=ewcfg.source_killing)
                    slimes_splatter *= .4

                boss_slimes += slimes_toboss
                district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
                target_data.bleed_storage += slimes_tobleed
                target_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
                target_data.time_lasthit = int(time_now)
                target_data.persist()
                sewer_data.change_slimes(n=slimes_drained)
                sewer_data.persist()

                # sap_damage_target = min(sap_damage, target_data.hardened_sap)
                # target_data.hardened_sap -= sap_damage_target

                if was_killed:
                    # adjust statistics
                    ewstats.increment_stat(user=user_data, metric=ewcfg.stat_kills)
                    ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
                    if user_data.slimelevel > target_data.slimelevel:
                        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_ganks)
                    elif user_data.slimelevel < target_data.slimelevel:
                        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_takedowns)

                    # Collect bounty
                    coinbounty = int(target_data.bounty / ewcfg.slimecoin_exchangerate)

                    # add bounty
                    user_data.add_bounty(n=(target_data.bounty / 2) + (slimes_dropped / 4))

                    user_data.change_slimecoin(n=coinbounty, coinsource=ewcfg.coinsource_bounty)

                    # Give a bonus to the player's weapon skill for killing a stronger player.
                    if target_data.slimelevel >= user_data.slimelevel:
                        user_data.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

                    district_data.change_slimes(n=target_data.slimes / 2, source=ewcfg.source_killing)
                    levelup_resp = user_data.change_slimes(n=target_data.slimes / 2, source=ewcfg.source_killing)

                    target_data.id_killer = user_data.id_user

                    target_data.trauma = ewcfg.trauma_id_environment
                    target_data.die(cause=ewcfg.cause_killing)
                    # target_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
                    target_data.persist()

                    response += "{} was killed by an explosion during your fight with {}!".format(target_player.display_name, shootee_player.display_name)
                    if coinbounty > 0:
                        response += "\n\n SlimeCorp transfers {:,} SlimeCoin to {}\'s account.".format(coinbounty, user_player.display_name)

                    resp_cont.add_channel_response(channel, response)

                    resp_cont.add_member_to_update(server.get_member(target_data.id_user))
                # Survived the explosion
                else:
                    # sap_response = ""
                    # if sap_damage_target > 0:
                    #	sap_response = " and {} hardened sap".format(sap_damage_target)

                    response += "{} was caught in an explosion during your fight with {} and lost {:,} slime!".format(target_player.display_name, shootee_player.display_name, damage)
                    resp_cont.add_channel_response(channel, response)
                    target_data.persist()

                if user_data.faction != target_data.faction and user_data.faction != ewcfg.faction_slimecorp and user_data.life_state != ewcfg.life_state_juvenile:
                    # Give slimes to the boss if possible.
                    kingpin = fe_utils.find_kingpin(id_server=server.id, kingpin_role=role_boss)
                    kingpin = EwUser(id_server=server.id, id_user=kingpin.id_user)
                    if kingpin:
                        kingpin.change_slimes(n=boss_slimes)
                        kingpin.persist()

        for bystander in bystander_enemies:
            # Don't damage the shooter or the enemy a second time

            if enemy_data != None:
                id_enemy_used = enemy_data.id_enemy
            else:
                id_enemy_used = None

            if bystander != user_data.id_user and bystander != id_enemy_used:
                response = ""

                slimes_damage_target = slimes_damage
                target_enemy_data = EwEnemy(id_enemy=bystander, id_server=user_data.id_server)

                # apply sap armor
                # sap_armor = get_sap_armor(shootee_data = target_enemy_data, sap_ignored = sap_ignored)
                # slimes_damage_target *= sap_armor
                # slimes_damage_target = int(max(0, slimes_damage_target))

                slimes_dropped = target_enemy_data.totaldamage + target_enemy_data.slimes

                was_killed = False

                if slimes_damage >= target_enemy_data.slimes - target_enemy_data.bleed_storage:
                    was_killed = True

                sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=user_data.id_server)

                # move around slime as a result of the shot
                slimes_drained = int(3 * slimes_damage / 4)  # 3/4

                damage = slimes_damage

                slimes_tobleed = int((slimes_damage - slimes_drained) / 2)

                slimes_directdamage = slimes_damage - slimes_tobleed
                slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained

                if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
                    user_data.change_slimes(n=slimes_splatter * 0.6, source=ewcfg.source_killing)
                    slimes_splatter *= .4

                district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
                target_enemy_data.bleed_storage += slimes_tobleed
                target_enemy_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
                sewer_data.change_slimes(n=slimes_drained)
                sewer_data.persist()

                # sap_damage_target = min(sap_damage, target_enemy_data.hardened_sap)
                # target_enemy_data.hardened_sap -= sap_damage_target

                if was_killed:
                    # adjust statistics
                    ewstats.increment_stat(user=user_data, metric=ewcfg.stat_kills)
                    ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
                    if user_data.slimelevel > target_enemy_data.level:
                        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_ganks)
                    elif user_data.slimelevel < target_enemy_data.level:
                        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_takedowns)

                    # Give a bonus to the player's weapon skill for killing a stronger player.
                    if target_enemy_data.level >= user_data.slimelevel:
                        user_data.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

                    district_data.change_slimes(n=target_enemy_data.slimes / 2, source=ewcfg.source_killing)
                    levelup_resp = user_data.change_slimes(n=target_enemy_data.slimes / 2, source=ewcfg.source_killing)

                    bknd_hunt.delete_enemy(target_enemy_data)

                    response += "{} was killed by an explosion during your fight with {}!".format(target_enemy_data.display_name, shootee_player.display_name)
                    resp_cont.add_response_container(cmbt_utils.drop_enemy_loot(target_enemy_data, district_data))
                    resp_cont.add_channel_response(channel, response)

                # Survived the explosion
                else:
                    # sap_response = ""
                    # if sap_damage_target > 0:
                    #	sap_response = " and {} hardened sap".format(sap_damage_target)
                    response += "{} was caught in an explosion during your fight with {} and lost {:,} slime!".format(target_enemy_data.display_name, shootee_player.display_name, damage)
                    resp_cont.add_channel_response(channel, response)
                    target_enemy_data.persist()
        user_data.persist()
        return resp_cont


def fulfill_ghost_weapon_contract(possession_data, market_data, user_data, user_name):
    ghost_id = possession_data[0]
    ghost_data = EwUser(id_user=ghost_id, id_server=user_data.id_server)

    # shooter 20%, which ghost gains as negative slime up to a cap of 300k
    slime_sacrificed = int(user_data.slimes * 0.2)
    user_data.change_slimes(n=-slime_sacrificed, source=ewcfg.source_ghost_contract)
    negaslime_gained = min(300000, slime_sacrificed)
    ghost_data.change_slimes(n=-negaslime_gained, source=ewcfg.source_ghost_contract)
    ghost_data.persist()
    market_data.negaslime -= -negaslime_gained
    market_data.persist()

    user_data.cancel_possession()

    server = ewutils.get_client().get_guild(user_data.id_server)
    ghost_name = server.get_member(ghost_id).display_name
    return "\n\n {} winces in pain as their slime is corrupted into negaslime. {}'s contract has been fulfilled.".format(user_name, ghost_name)


def canAttack(cmd, amb_switch = 0):
    response = ""
    time_now_float = time.time()
    time_now = int(time_now_float)
    user_data = EwUser(member=cmd.message.author)
    mutations = user_data.get_mutations()
    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(id_server=user_data.id_server, district=user_data.poi)
    weapon_item = None
    weapon = None
    captcha = None
    hacked = EwGamestate(id_server=user_data.id_server, id_state="n13door")
    tokens_lower = []
    for token in cmd.tokens:
        tokens_lower.append(token.lower())

    code_count = 0
    for code in tokens_lower:
        if code.upper() in ewcfg.captcha_dict:
            code_count += 1

    if amb_switch == 1:
        weapon_item = EwItem(id_item=user_data.sidearm)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
        captcha = weapon_item.item_props.get('captcha')
    elif user_data.weapon >= 0:
        weapon_item = EwItem(id_item=user_data.weapon)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
        captcha = weapon_item.item_props.get('captcha')

    channel_poi = poi_static.chname_to_poi.get(cmd.message.channel.name)
    """
    if user_data.life_state == ewcfg.life_state_enlisted or user_data.life_state == ewcfg.life_state_corpse:
        if user_data.life_state == ewcfg.life_state_enlisted:
            response = "Not so fast, you scrooge! Only Juveniles can attack during Slimernalia."
        else:
            response = "You lack the moral fiber necessary for violence."
    elif user_data.slimelevel <= ewcfg.max_safe_level:
        response = "You are still too cowardly to hurt another being."
    """

    if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
        response = "You can't commit violence from here."
    # elif ewmap.poi_is_pvp(user_data.poi) == False and cmd.mentions_count >= 1:
    # 	response = "You must go elsewhere to commit gang violence."
    elif channel_poi.id_poi != user_data.poi and user_data.poi not in channel_poi.mother_districts:
        # Only way to do this right now is by using the gellphone
        response = "Alas, you still can't shoot people through your phone."
    elif cmd.mentions_count > 1:
        response = "One shot at a time!"
    elif user_data.hunger >= user_data.get_hunger_max():
        response = "You are too exhausted for gang violence right now. Go get some grub!"
    elif weapon != None and ewcfg.weapon_class_ammo in weapon.classes and int(weapon_item.item_props.get('ammo')) == 0:
        response = "You've run out of ammo and need to {}!".format(ewcfg.cmd_reload)
    elif weapon != None and weapon.cooldown + (float(weapon_item.item_props.get("time_lastattack")) if weapon_item.item_props.get("time_lastattack") != None else 0) > time_now_float:
        response = "Your {weapon_name} isn't ready for another attack yet!".format(weapon_name=weapon.id_weapon)
    elif weapon != None and (ewcfg.weapon_class_captcha in weapon.classes and captcha not in [None, ""] and captcha.lower() not in tokens_lower) or code_count > 1:
        if (ewcfg.weapon_class_burning in weapon.classes or ewcfg.weapon_class_exploding in weapon.classes):
            slime_backfired = int(user_data.slimes * (0.1 + random.random() / 20))
            user_data.change_slimes(n=-slime_backfired, source=ewcfg.source_self_damage)
            user_data.persist()
            if (ewcfg.weapon_class_burning in weapon.classes):
                response = random.choice([
                    "In an amazing display of discipline you let idle embers catch onto a chunk of dry cloth, turning you into a bonfire.",
                    "You learn first hand the pain you wish to inflict upon thine enemy, and suffer, like a bitch.",
                    "The bright flames sear your retina, blinding you long enough for the fire to scorch the rest of your body."
                ])
            else:
                response = random.choice([
                    "Your lacking explosive safety causes the payload to explode right in your grip, separating you from your hands!",
                    "You're thrown to the pavement by the blast of your bomb, with each finger bent and broken. Looks like some bone's sticking out, too!",
                    "Why don't these explosives have proper training manuals? You'll never get to know, as you're splattered across the concrete."
                ])
            response += "\nYou lose {} slime. Learn to type, you fucking idiot.".format(slime_backfired)
        else:
            response = "ERROR: Invalid security code.\nEnter **{}** to proceed.".format(ewutils.text_to_regional_indicator(captcha))

    elif user_data.weapon == -1 and user_data.life_state != ewcfg.life_state_shambler and ewcfg.mutation_id_lethalfingernails not in mutations and ewcfg.mutation_id_ambidextrous not in mutations:
        response = "How do you expect to engage in gang violence if you don't even have a weapon yet? Head to the Dojo in South Sleezeborough to pick one up!"
    elif ewcfg.mutation_id_ambidextrous in mutations and user_data.weapon == -1 and user_data.sidearm == -1 and user_data.life_state != ewcfg.life_state_shambler and ewcfg.mutation_id_lethalfingernails not in mutations:
        response = "How do you expect to engage in gang violence if you don't even have a weapon yet? Head to the Dojo in South Sleezeborough to pick one up!"

    elif cmd.mentions_count <= 0:
        # user is going after enemies rather than players

        # Get target's info.
        # converts ['THE', 'Lost', 'juvie'] into 'the lost juvie'
        huntedenemy = " ".join(cmd.tokens[1:]).lower()

        enemy_data = cmbt_utils.find_enemy(huntedenemy, user_data)

        user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers
        user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_rowdys
        user_isslimecorp = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_slimecorp

        user_isexecutive = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
        user_isshambler = user_data.life_state == ewcfg.life_state_shambler

        if (time_now - user_data.time_lastkill) < ewcfg.cd_kill:
            # disallow kill if the player has killed recently
            response = "Take a moment to appreciate your last slaughter."

        elif user_iskillers == False and user_isrowdys == False and user_isexecutive == False and user_isshambler == False and user_isslimecorp == False:
            # Only killers, rowdys, the cop killer, and rowdy fucker can shoot people.
            if user_data.life_state == ewcfg.life_state_juvenile:
                response = "Juveniles lack the moral fiber necessary for violence."
            else:
                response = "You lack the moral fiber necessary for violence."

        elif enemy_data != None:
            # enemy found, redirect variables to code in ewhunting
            response = ewcfg.enemy_targeted_string

        else:
            # no enemy is found within that district
            response = "Your bloodlust is appreciated, but ENDLESS WAR couldn't find what you were trying to kill."

    elif cmd.mentions_count == 1:
        # Get target's info.
        member = cmd.mentions[0]
        shootee_data = EwUser(member=member)

        user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers
        user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_rowdys
        user_isslimecorp = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_slimecorp
        user_isexecutive = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
        user_isshambler = user_data.life_state == ewcfg.life_state_shambler

        possession_data = user_data.get_possession()

        if shootee_data.life_state == ewcfg.life_state_kingpin:
            # Disallow killing generals.
            response = "He is hiding in his ivory tower and playing video games like a retard."

        elif (time_now - user_data.time_lastkill) < ewcfg.cd_kill:
            # disallow kill if the player has killed recently
            response = "Take a moment to appreciate your last slaughter."

        elif shootee_data.poi != user_data.poi:
            response = "You can't reach them from where you are."

        elif move_utils.poi_is_pvp(shootee_data.poi) == False:
            response = "{} is not mired in the ENDLESS WAR right now.".format(member.display_name)

        elif user_isshambler == True and len(district_data.get_enemies_in_district(classes=[ewcfg.enemy_class_gaiaslimeoid])) > 0:
            response = "You can't attack them, they're protected by Gaiaslimeoids!"

        # elif shootee_data.life_state == ewcfg.life_state_shambler and (user_iskillers == True or user_isrowdys == True or user_isexecutive == True or user_isslimecorp == True) and len(district_data.get_enemies_in_district(classes = [ewcfg.enemy_class_shambler])) > 0:
        # 	response = "You can't attack them, they're protected by a horde of enemy Shamblers!"

        elif user_iskillers == False and user_isrowdys == False and user_isexecutive == False and user_isshambler == False and user_isslimecorp == False:
            # Only killers, rowdys, the cop killer, and rowdy fucker can shoot people.
            if user_data.life_state == ewcfg.life_state_juvenile:
                response = "Juveniles lack the moral fiber necessary for violence."
            else:
                response = "You lack the moral fiber necessary for violence."

        elif (time_now - shootee_data.time_lastrevive) < ewcfg.invuln_onrevive:
            # User is currently invulnerable.
            response = "{} has died too recently and is immune.".format(member.display_name)

        elif shootee_data.life_state == ewcfg.life_state_corpse and shootee_data.busted == True:
            # Target is already dead and not a ghost.
            response = "{} is already dead.".format(member.display_name)

        elif shootee_data.life_state == ewcfg.life_state_corpse and ewcfg.status_ghostbust_id not in user_data.getStatusEffects() and ewcfg.mutation_id_coleblooded not in mutations:
            # Target is a ghost but user is not able to bust
            response = "You don't know how to fight a ghost."

        elif shootee_data.life_state == ewcfg.life_state_corpse and shootee_data.poi in [ewcfg.poi_id_thevoid, ewcfg.poi_id_blackpond]:
            # Can't bust ghosts in their realm
            response = "{} is empowered by the void, and deflects your attacks without breaking a sweat.".format(member.display_name)

        elif possession_data and (shootee_data.id_user == possession_data[0]):
            # Target is possessing user's weapon
            response = "{}'s contract forbids you from harming them. You should've read the fine print.".format(member.display_name)

        elif not poi.pvp and not (shootee_data.life_state == ewcfg.life_state_shambler or shootee_data.get_inhabitee() == user_data.id_user or user_isshambler):  # or (shootee_data.life_state == ewcfg.life_state_juvenile and shootee_data.slimelevel <= ewcfg.max_safe_level):
            # Target is neither flagged for PvP, nor a shambler, nor a ghost inhabiting the player, nor a juvie above a certain threshold slime. Player is not a shambler.
            response = "{} is not mired in the ENDLESS WAR right now.".format(member.display_name)

    # Identify if the shooter and the shootee are on the same team.
    # same_faction = False
    # if user_iskillers and shootee_data.faction == ewcfg.faction_killers:
    #	same_faction = True
    # if user_isrowdys and shootee_data.faction == ewcfg.faction_rowdys:
    #	same_faction = True
    # if user_isslimecorp and shootee_data.faction == ewcfg.faction_slimecorp:
    #	same_faction = True

    return response


async def attackEnemy(cmd, user_data, weapon, resp_cont, weapon_item, slimeoid, market_data, time_now_float):
    time_now = int(time_now_float)
    # Get shooting player's info
    if user_data.slimelevel <= 0:
        user_data.slimelevel = 1
        user_data.persist()

    # Get target's info.
    huntedenemy = " ".join(cmd.tokens[1:]).lower()
    enemy_data = cmbt_utils.find_enemy(huntedenemy, user_data)

    sandbag_mode = False
    if enemy_data.enemytype == ewcfg.enemy_type_sandbag:
        sandbag_mode = True

    if (enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state in [ewcfg.life_state_executive, ewcfg.life_state_enlisted]) or (enemy_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler):
        response = "Hey ASSHOLE! They're on your side!!"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif (enemy_data.enemyclass == ewcfg.enemy_class_shambler and enemy_data.gvs_coord not in ewcfg.gvs_coords_end):
        response = "It's best not to interfere with whatever those Juveniles are up to. If it gets close, that's your time to strike."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    # elif (enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and ewutils.gvs_check_gaia_protected(enemy_data)):
    # 	response = "It's no use, there's another gaiaslimeoid in front that's protecting them!"
    # 	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif user_data.life_state == ewcfg.life_state_shambler and enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid:
        response = "It's not worth going near those... *things*. You'd get torn to shreds, it's better to send out lackeys to do your job for you."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # if (time_now - user_data.time_lasthaunt) < ewcfg.cd_shambler_attack:
    # 	response = "Your shitty zombie jaw is too tired to chew on that {}. Try again in {} seconds.".format(enemy_data.display_name, int(ewcfg.cd_shambler_attack-(time_now-user_data.time_lasthaunt)))
    # 	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    # else:
    # 	user_data.time_lasthaunt = time_now
    # 	user_data.persist()

    user_mutations = user_data.get_mutations()

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

    shooter_status_mods = cmbt_utils.get_shooter_status_mods(user_data, enemy_data, hitzone)
    shootee_status_mods = cmbt_utils.get_shootee_status_mods(enemy_data, user_data, hitzone)

    hit_chance_mod += round(shooter_status_mods['hit_chance'] + shootee_status_mods['hit_chance'], 2)
    crit_mod += round(shooter_status_mods['crit'] + shootee_status_mods['crit'], 2)
    dmg_mod += round(shooter_status_mods['dmg'] + shootee_status_mods['dmg'], 2)

    slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 30)
    # disabled until held items update
    # attack_stat_multiplier = 1 + (user_data.attack / 50) # 2% more damage per stat point
    attack_stat_multiplier = 1
    weapon_skill_multiplier = 1 + ((user_data.weaponskill * 5) / 100)  # 5% more damage per skill point
    slimes_damage = int(5 * slimes_spent * attack_stat_multiplier * weapon_skill_multiplier)  # ten times slime spent, multiplied by both multipliers

    if user_data.weaponskill < 5:
        hit_chance_mod -= (5 - user_data.weaponskill) / 10

    # If the player is using a repel, remove the repel, and make the first hit do 99.9% less damage, rounded up.
    statuses = user_data.getStatusEffects()
    if ewcfg.status_repelled_id in statuses:
        user_data.clear_status(ewcfg.status_repelled_id)
        after_effects_response = user_data.applyStatus(ewcfg.status_repelaftereffects_id)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, after_effects_response))
        slimes_damage /= 1000
        slimes_damage = math.ceil(slimes_damage)

    # If the player has cancelled a repel by attacking an enemy, make all their hits do 99% less damage for two seconds, rounded up.
    if ewcfg.status_repelaftereffects_id in statuses:
        slimes_damage /= 100
        slimes_damage = math.ceil(slimes_damage)

    if weapon is None:
        slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons
    slimes_dropped = enemy_data.totaldamage + enemy_data.slimes

    slimes_damage += int(slimes_damage * dmg_mod)

    user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers
    user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_rowdys
    user_isslimecorp = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_slimecorp
    user_isexecutive = user_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]

    # hunger drain
    if not sandbag_mode:
        user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)

    # randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]

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
            shootee_data=enemy_data,
            time_now=time_now_float,
            bystander_damage=bystander_damage,
            hit_chance_mod=hit_chance_mod,
            crit_mod=crit_mod,
            market_data=market_data,
            # sap_damage=sap_damage,
            # sap_ignored=sap_ignored,
        )

        # Make adjustments
        if weapon.id_weapon != ewcfg.weapon_id_garrote:
            weapon.fn_effect(ctn)

        # Apply effects for non-reference values
        miss = ctn.miss
        crit = ctn.crit
        slimes_damage = ctn.slimes_damage
        slimes_spent = ctn.slimes_spent
        bystander_damage = ctn.bystander_damage
        # sap_damage = ctn.sap_damage
        # sap_ignored = ctn.sap_ignored
        # user_data and enemy_data should be passed by reference, so there's no need to assign them back from the effect container.

        if sandbag_mode:
            slimes_spent_sandbag = slimes_spent
            slimes_spent = 0
            slimes_dropped = 0

        if (slimes_spent > user_data.slimes):
            # Not enough slime to shoot.
            response = "You don't have enough slime to attack. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        weapon_item.item_props['time_lastattack'] = time_now_float
        weapon_item.persist()

        # print(user_data.slimes)
        # print(slimes_spent)

        # Spend slimes, to a minimum of zero
        user_data.change_slimes(n=(-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent), source=ewcfg.source_spending)

        # Spend sap
        # user_data.sap -= weapon.sap_cost
        user_data.limit_fix()
        user_data.persist()

        if weapon.id_weapon == ewcfg.weapon_id_garrote:
            enemy_data.persist()
            response = "You wrap your wire around {}'s neck...\n**...to no avail! {} breaks free with ease!**".format(
                enemy_data.display_name, enemy_data.display_name)
            resp_cont.add_channel_response(cmd.message.channel.name, response)
            resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
            await resp_cont.post()

            user_data = EwUser(member=cmd.message.author)

            # TODO - Make enemies able to be strangled
            # One of the players/enemies died in the meantime
            if user_data.life_state == ewcfg.life_state_corpse or enemy_data.life_state == ewcfg.enemy_lifestate_dead:
                return
            else:
                return

        # else:
        # pass
        # enemy_data.persist()

        # Remove a bullet from the weapon
        if ewcfg.weapon_class_ammo in weapon.classes:
            weapon_item.item_props['ammo'] = int(weapon_item.item_props.get("ammo")) - 1

        if not sandbag_mode:
            life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_shambler]
            bystander_faction = ""
            if user_data.faction == "rowdys":
                bystander_faction = "killers"
            elif user_data.faction == "killers":
                bystander_faction = "rowdys"

            # SLIMERNALIA
            factions = ["", bystander_faction]

            # Burn players in district
            if ewcfg.weapon_class_burning in weapon.classes:
                if enemy_data.enemyclass in [ewcfg.enemy_class_gaiaslimeoid, ewcfg.enemy_class_shambler]:
                    miss = True

                if not miss:
                    resp = apply_status_bystanders(user_data=user_data, status=ewcfg.status_burning_id, value=bystander_damage, life_states=life_states, factions=factions, district_data=district_data)
                    resp_cont.add_response_container(resp)

            if ewcfg.weapon_class_exploding in weapon.classes:
                if enemy_data.enemyclass in [ewcfg.enemy_class_gaiaslimeoid, ewcfg.enemy_class_shambler]:
                    miss = True

                user_data.persist()
                enemy_data.persist()

                if not miss:
                    # Damage players/enemies in district
                    resp = weapon_explosion(user_data=user_data, shootee_data=enemy_data, district_data=district_data, market_data=market_data, life_states=life_states, factions=factions, slimes_damage=bystander_damage, time_now=time_now, target_enemy=True)
                    resp_cont.add_response_container(resp)

            user_data = EwUser(member=cmd.message.author)

    if miss:
        slimes_damage = 0
        # sap_damage = 0
        weapon_item.item_props["consecutive_hits"] = 0
        crit = False

    # if crit:
    #	sap_damage += 1

    # if user_data.life_state == ewcfg.life_state_shambler:
    #	sap_damage += 1

    # Remove !revive invulnerability.
    user_data.time_lastrevive = 0

    # apply attacker damage mods
    slimes_damage *= cmbt_utils.damage_mod_attack(
        user_data=user_data,
        user_mutations=user_mutations,
        market_data=market_data,
        district_data=district_data
    )

    # Defender enemies take less damage
    if enemy_data.ai == ewcfg.enemy_ai_defender:
        slimes_damage *= 0.5

    # Bicarbonate enemies take more damage
    if enemy_data.weathertype == ewcfg.enemy_weathertype_rainresist:
        slimes_damage *= 1.5

    # # Shamblers deal less damage to gaiaslimeoids
    # if enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state == ewcfg.life_state_shambler:
    # 	slimes_damage *= 0.25

    # if not sandbag_mode:
    # apply hardened sap armor
    # sap_armor = get_sap_armor(shootee_data = enemy_data, sap_ignored = sap_ignored)
    # slimes_damage *= sap_armor
    # slimes_damage = int(max(slimes_damage, 0))

    # sap_damage = min(sap_damage, enemy_data.hardened_sap)

    # Damage stats
    ewstats.track_maximum(user=user_data, metric=ewcfg.stat_max_hitdealt, value=slimes_damage)
    ewstats.change_stat(user=user_data, metric=ewcfg.stat_lifetime_damagedealt, n=slimes_damage)

    user_inital_level = user_data.slimelevel

    was_killed = False

    if slimes_damage >= enemy_data.slimes - enemy_data.bleed_storage:
        was_killed = True
        # if ewcfg.mutation_id_thickerthanblood in user_mutations:
        #	slimes_damage = 0
        # else:
        slimes_damage = max(enemy_data.slimes - enemy_data.bleed_storage, 0)

    sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=cmd.guild.id)
    # move around slime as a result of the shot
    slimes_drained = int(3 * slimes_damage / 4)  # 3/4

    damage = slimes_damage

    slimes_tobleed = int((slimes_damage - slimes_drained) / 2)
    # if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
    #	slimes_tobleed = 0

    slimes_directdamage = slimes_damage - slimes_tobleed
    slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained

    if sandbag_mode:
        slimes_drained = 0
        slimes_tobleed = 0
        # slimes_directdamage = 0
        slimes_splatter = 0

    if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
        user_data.change_slimes(n=slimes_splatter * 0.6, source=ewcfg.source_killing)
        slimes_splatter *= .4

    district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
    enemy_data.bleed_storage += slimes_tobleed
    enemy_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
    # enemy_data.hardened_sap -= sap_damage
    enemy_data.persist()
    sewer_data.change_slimes(n=slimes_drained)
    sewer_data.persist()

    slimeoid_name = ""
    slimeoid_kill = ""
    slimeoid_crit = ""
    slimeoid_dmg = ""

    if weapon.id_weapon == ewcfg.weapon_id_slimeoidwhistle:
        if slimeoid.life_state == ewcfg.slimeoid_state_none:
            slimeoid_name = cmd.message.author.display_name
            slimeoid_kill = 'goes full child gorilla and tears their victim to hideous chunks, before wailing a ferocious battle cry.'
            slimeoid_crit = 'a full speed donkey kick'
            slimeoid_dmg = 'knocked upside the head'
        else:
            slimeoid_name = slimeoid.name
            slimeoid_kill = static_weapons.slimeoid_kill_text.get(slimeoid.weapon)
            slimeoid_crit = static_weapons.slimeoid_crit_text.get(slimeoid.special)
            slimeoid_dmg = static_weapons.slimeoid_dmg_text.get(slimeoid.weapon)

    if was_killed:
        # adjust statistics
        ewstats.increment_stat(user=user_data, metric=ewcfg.stat_pve_kills)
        ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
        if user_data.slimelevel > enemy_data.level:
            ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_pve_ganks)
        elif user_data.slimelevel < enemy_data.level:
            ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_pve_takedowns)

        if weapon != None:
            weapon_item.item_props["kills"] = (int(weapon_item.item_props.get("kills")) if weapon_item.item_props.get("kills") != None else 0) + 1
            weapon_item.item_props["totalkills"] = (int(weapon_item.item_props.get("totalkills")) if weapon_item.item_props.get("totalkills") != None else 0) + 1
            ewstats.increment_stat(user=user_data, metric=weapon.stat)

        # Give a bonus to the player's weapon skill for killing a stronger enemy.
        if enemy_data.enemytype != ewcfg.enemy_type_sandbag and enemy_data.level >= user_data.slimelevel and weapon is not None:
            user_data.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

        # release bleed storage
        # if ewcfg.mutation_id_thickerthanblood in user_mutations:
        #	slimes_todistrict = enemy_data.slimes * 0.25
        #	slimes_tokiller = enemy_data.slimes * 0.75
        # else:
        slimes_todistrict = enemy_data.slimes / 2
        slimes_tokiller = enemy_data.slimes / 2

        if sandbag_mode:
            slimes_todistrict = 0
            slimes_tokiller = 0

        district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)
        levelup_response = user_data.change_slimes(n=slimes_tokiller, source=ewcfg.source_killing)
        if ewcfg.mutation_id_fungalfeaster in user_mutations:
            user_data.hunger = 0

        # Enemy was killed.
        bknd_hunt.delete_enemy(enemy_data)

        kill_descriptor = "beaten to death"
        if weapon != None:
            response = weapon.str_damage.format(
                name_player=cmd.message.author.display_name,
                name_target=enemy_data.display_name,
                hitzone=randombodypart,
                slimeoid_name=slimeoid_name,
                slimeoid_dmg=slimeoid_dmg
            )
            kill_descriptor = weapon.str_killdescriptor
            if crit:
                response += " {}".format(weapon.str_crit.format(
                    name_player=cmd.message.author.display_name,
                    name_target=enemy_data.display_name,
                    hitzone=randombodypart,
                    slimeoid_name=slimeoid_name,
                    slimeoid_crit=slimeoid_crit
                ))

            response += "\n\n{}".format(weapon.str_kill.format(
                name_player=cmd.message.author.display_name,
                name_target=enemy_data.display_name,
                emote_skull=ewcfg.emote_slimeskull,
                slimeoid_name=slimeoid_name,
                slimeoid_kill=slimeoid_kill
            ))

            if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
                response += "\n" + weapon.str_reload_warning.format(
                    name_player=cmd.message.author.display_name)

            if ewcfg.weapon_class_captcha in weapon.classes:
                new_captcha = ewutils.generate_captcha(length=weapon.captcha_length, user_data=user_data)
                response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
                weapon_item.item_props['captcha'] = new_captcha
                weapon_item.persist()
        else:
            response = "{name_target} is hit!!\n\n{name_target} has died.".format(
                name_target=enemy_data.display_name)

        weapon_possession = user_data.get_possession('weapon')
        if weapon_possession:
            response += fulfill_ghost_weapon_contract(weapon_possession, market_data, user_data, cmd.message.author.display_name)

        # When a raid boss dies, use this response instead so its drops aren't shown in the killfeed
        old_response = response

        # give player item for defeating an enemy
        resp_cont.add_response_container(cmbt_utils.drop_enemy_loot(enemy_data, district_data))

        if slimeoid.life_state == ewcfg.slimeoid_state_active:
            brain = sl_static.brain_map.get(slimeoid.ai)
            response += "\n" + brain.str_kill.format(slimeoid_name=slimeoid.name)

        user_data.persist()
        resp_cont.add_channel_response(cmd.message.channel.name, response)

        # TODO remove after double halloween
        # if enemy_data.enemytype == ewcfg.enemy_type_doubleheadlessdoublehorseman:
        #	horseman_deaths = market_data.horseman_deaths
        #
        #			if horseman_deaths == 0:
        #				defeat_response = "***AHA... AHAHAHAHA...***\n*COUGH*... *HACK*...\nYOU HAVE ALL TRULY PUT ON A SPLENDID PERFORMANCE.\nI KNOW WHEN I AM DEFEATED. PLEASE, TAKE THESE GIFTS OFF OF MY CORPSE...\nTHEY ARE OF NO USE TO ME ANYMORE.\nFOR NOW THOUGH, THIS IS WHERE I GET OFF.\nSAVE A SEAT FOR ME, WON'T YOU, PHOEBUS?\n"
        #			else:
        #				defeat_response = "***GAHAHAH... AHAHA...***\n*WHEEZE*... *PUKE*...\nBESTED A SECOND TIME...\nIF I WEREN'T GONE FOR GOOD... THIS WOULD FEEL LIKE AN INSULT.\nNOW, HOWEVER, I HAVE REACHED MY LIMIT.\nTHE GREAT BEYOND CALLS TO ME ONCE AGAIN, AND I ANSWER.\nI JUST HOPE I HAVE THE HEART TO TELL HIM HOW I FEEL...\nUNTIL WE MEET AGAIN AT NEXT DOUBLE HOLLOW'S EVE, ***MORTALS!!!***\n"

        #			market_data.horseman_deaths += 1
        #			market_data.horseman_timeofdeath = int(time_now)
        #			market_data.persist()

        #			resp_cont.add_channel_response(cmd.message.channel.name, defeat_response)

        user_data = EwUser(member=cmd.message.author)
    else:
        # A non-lethal blow!
        if weapon != None:
            if miss:
                response = "{}".format(weapon.str_miss.format(
                    name_player=cmd.message.author.display_name,
                    name_target=enemy_data.display_name,
                    slimeoid_name=slimeoid_name
                ))
            else:
                response = weapon.str_damage.format(
                    name_player=cmd.message.author.display_name,
                    name_target=enemy_data.display_name,
                    hitzone=randombodypart,
                    slimeoid_name=slimeoid_name,
                    slimeoid_dmg=slimeoid_dmg
                )
                if crit:
                    response += " {}".format(weapon.str_crit.format(
                        name_player=cmd.message.author.display_name,
                        name_target=enemy_data.display_name,
                        hitzone=randombodypart,
                        slimeoid_name=slimeoid_name,
                        slimeoid_crit=slimeoid_crit
                    ))

                # sap_response = ""
                # if sap_damage > 0:
                #	sap_response = " and {sap_damage} hardened sap".format(sap_damage = sap_damage)

                response += " {target_name} loses {damage:,} slime!".format(
                    target_name=enemy_data.display_name,
                    damage=damage
                    #	sap_response=sap_response
                )

                if enemy_data.ai == ewcfg.enemy_ai_coward:
                    response += random.choice(ewcfg.coward_responses_hurt).format(enemy_data.display_name)
                elif enemy_data.ai == ewcfg.enemy_ai_defender:
                    enemy_data.id_target = user_data.id_user
                    enemy_data.persist()

            if ewcfg.weapon_class_ammo in weapon.classes and weapon_item.item_props.get("ammo") == 0:
                response += "\n" + weapon.str_reload_warning.format(
                    name_player=cmd.message.author.display_name)

            if ewcfg.weapon_class_captcha in weapon.classes:
                new_captcha = ewutils.generate_captcha(length=weapon.captcha_length, user_data=user_data)
                response += "\nNew security code: **{}**".format(ewutils.text_to_regional_indicator(new_captcha))
                weapon_item.item_props['captcha'] = new_captcha
                weapon_item.persist()
        else:
            if miss:
                response = "{target_name} dodges your strike.".format(target_name=enemy_data.display_name)
            else:
                response = "{target_name} is hit!! {target_name} loses {damage:,} slime!".format(
                    target_name=enemy_data.display_name,
                    damage=damage
                )

                if enemy_data.ai == ewcfg.enemy_ai_coward:
                    response += random.choice(ewcfg.coward_responses_hurt).format(enemy_data.display_name)
                elif enemy_data.ai == ewcfg.enemy_ai_defender:
                    enemy_data.id_target = user_data.id_user
                    enemy_data.persist()

        if sandbag_mode:
            response += '\n*The dojo master cries out from afar:*\n"If this were a real fight, you would have spent **{}** slime on that attack!"'.format(slimes_spent_sandbag)

        resp_cont.add_channel_response(cmd.message.channel.name, response)

    # Add level up text to response if appropriate
    if user_inital_level < user_data.slimelevel:
        resp_cont.add_channel_response(cmd.message.channel.name, "\n" + levelup_response)
    # Enemy kills don't award slime to the kingpin.

    # Persist user data.

    resp_cont.add_member_to_update(cmd.message.author)
    user_data.persist()
    if user_data.weapon > 0:
        weapon_item.persist()

    district_data.persist()

    # If an enemy is a raidboss, announce that kill in the killfeed
    if was_killed and (enemy_data.enemytype in ewcfg.raid_bosses):
        # announce raid boss kill in kill feed channel

        resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)
        await resp_cont.post()

        killfeed_resp = "*{}*: {}".format(cmd.message.author.display_name, old_response)
        killfeed_resp += "\n`-------------------------`{}".format(ewcfg.emote_megaslime)

        killfeed_resp_cont = EwResponseContainer(id_server=cmd.guild.id)
        killfeed_resp_cont.add_channel_response(ewcfg.channel_killfeed, killfeed_resp)

        if ewcfg.mutation_id_amnesia in user_mutations:
            await asyncio.sleep(60)

        await killfeed_resp_cont.post()

    # Send the response to the player.

    else:
        resp_cont.format_channel_response(cmd.message.channel.name, cmd.message.author)

        await resp_cont.post()


def canCap(cmd, capture_type, roomba_loop = 0):
    response = ""
    time_now_float = time.time()
    time_now = int(time_now_float)
    user_data = EwUser(member=cmd.message.author)
    sidearm_item = None
    sidearm = None
    captcha = None
    sidearm_viable = 0
    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district=poi.id_poi, id_server=cmd.guild.id)
    market_data = EwMarket(id_server=cmd.guild.id)
    mutations = user_data.get_mutations()

    tokens_lower = []
    for token in cmd.tokens:
        tokens_lower.append(token.lower())

    code_count = 0
    for code in tokens_lower:
        if code.upper() in ewcfg.captcha_dict:
            code_count += 1

    # print(code_count)

    # alternate sidearm model that i'm saving just in case
    # if user_data.sidearm >= 0:
    #	sidearm_item = EwItem(id_item=user_data.sidearm)
    #	sidearm = static_weapons.weapon_map.get(sidearm_item.item_props.get("weapon_type"))
    #	captcha = sidearm_item.item_props.get('captcha')
    #	if ewcfg.weapon_class_paint in sidearm.classes:
    #		sidearm_viable = 1

    if user_data.weapon >= 0:  # and sidearm_viable == 0
        sidearm_item = EwItem(id_item=user_data.weapon)
        sidearm = static_weapons.weapon_map.get(sidearm_item.item_props.get("weapon_type"))
        captcha = sidearm_item.item_props.get('captcha')
        if ewcfg.weapon_class_paint in sidearm.classes:
            sidearm_viable = 1

    if user_data.faction == ewcfg.faction_slimecorp and capture_type == "spray":
        response = 'Your SlimeCorp headset chatters in your ear...\n"Reminder: Engaging in vandalism is strictly prohibited. Consider district sanitization your primary goal as an on-duty security officer."'
        return response
    elif user_data.faction != ewcfg.faction_slimecorp and capture_type == "sanitize":
        response = "You don't have the equipment necessary to clean up graffiti."
        return response

    if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
        response = "You can't spray graffiti from here."
    elif user_data.poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown]:
        response = "There’s no point, the rest of your gang has already covered this place in spraypaint. Focus on exporting your graffiti instead."
    elif user_data.poi == ewcfg.poi_id_juviesrow:
        response = "Nah, the Rowdys and Killers have both agreed this is neutral ground. You don’t want to start a diplomatic crisis, " \
                   "just stick to spraying down sick graffiti and splattering your rival gang across the pavement in the other districts."
    # elif district_data.is_degraded():
    # response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
    elif not user_data.poi in poi_static.capturable_districts:
        response = "This zone cannot be captured."
    elif sidearm != None and sidearm.cooldown + (float(sidearm_item.item_props.get("time_lastattack")) if sidearm_item.item_props.get("time_lastattack") != None else 0) > time_now_float:
        response = "Your {weapon_name} isn't ready for another {command} yet!".format(weapon_name=sidearm.id_weapon, command=cmd.tokens[0].lower())
    elif district_data.all_neighbors_friendly() is True and district_data.controlling_faction != user_data.faction and ewcfg.mutation_id_nervesofsteel not in mutations:
        response = "You're scared out of your mind and deep into enemy territory! Spraying here is just beyond you at this point."
    elif sidearm != None and ewcfg.weapon_class_captcha in sidearm.classes and captcha not in [None, ""] and captcha.lower() not in tokens_lower and roomba_loop == 0:
        response = "ERROR: Invalid security code. Enter **{}** to proceed.".format(ewutils.text_to_regional_indicator(captcha))
    elif code_count > 1 and roomba_loop == 0:
        response = "ERROR: Invalid security code. Enter **{}** to proceed.".format(ewutils.text_to_regional_indicator(captcha))
    elif user_data.life_state != ewcfg.life_state_enlisted and user_data.faction != ewcfg.faction_slimecorp:
        response = "Juveniles are too cowardly and/or centrist to be vandalizing anything."
    elif user_data.life_state != ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_slimecorp:
        response = 'Your SlimeCorp headset chatters in your ear...\n"Off-duty security officers are strictly prohibited from engaging in sanitization. Please follow standard protocol and enlist before you take any further action."'
    elif sidearm != None and ewcfg.weapon_class_ammo in sidearm.classes and int(sidearm_item.item_props.get('ammo')) <= 0:
        response = "You've run out of ammo and need to {}!".format(ewcfg.cmd_reload)
    elif sidearm_viable == 0:
        response = "With what, your piss? Get some paint from Based Hardware and stop fucking around."
    # elif not 3 <= market_data.clock <= 10 and user_data.faction != ewcfg.faction_slimecorp:
    #	response = "You can't !spray while all these people are around. The cops are no problem but the street sweepers will fucking kill you."
    # elif not 3 <= market_data.clock <= 10 and user_data.faction == ewcfg.faction_slimecorp:
    #	response = 'Your SlimeCorp headset chatters in your ear...\n"SlimeCorp protocol only allows sanitization during hours where federal sanitizers are not at work. Please cease and desist."'

    return response
