"""
	Commands and utilities related to Juveniles.
"""
import math
import random
import time

from ew.backend import item as bknd_item
from ew.backend import worldevent as bknd_worldevent
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.worldevent import EwWorldEvent
from ew.static import cfg as ewcfg
from ew.static import food as static_food
from ew.static import items as static_items
from ew.static import poi as poi_static
from ew.static import vendors
from ew.static import weapons as static_weapons
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as itm_utils
from ew.utils import poi as poi_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils import stats as ewstats
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict
from . import juviecmdutils
from .juviecmdutils import create_mining_event
from .juviecmdutils import gen_scavenge_captcha
from .juviecmdutils import get_mining_yield_by_grid_type
from .juviecmdutils import init_grid
from .juviecmdutils import mismine
from .juviecmdutils import print_grid


async def crush(cmd):
    member = cmd.message.author
    user_data = EwUser(member=member)
    response = ""  # if it's not overwritten
    crush_slimes = ewcfg.crush_slimes

    command = "crush"
    if cmd.tokens[0] == (ewcfg.cmd_prefix + 'crunch'):
        command = "crunch"

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Alas, your ghostly form cannot {} anything. Lame.".format(command)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=user_data.id_user, id_server=user_data.id_server)

    if item_sought:
        sought_id = item_sought.get('id_item')
        item_data = EwItem(id_item=sought_id)

        response = "The item doesn't have !{} functionality".format(command)  # if it's not overwritten

        if item_data.item_props.get("id_item") == ewcfg.item_id_slimepoudrin:
            # delete a slime poudrin from the player's inventory
            bknd_item.item_delete(id_item=sought_id)

            levelup_response = user_data.change_slimes(n=crush_slimes, source=ewcfg.source_crush)
            user_data.persist()

            response = "You {} the hardened slime crystal with your bare teeth.\nYou gain {} slime. Sick, dude!!".format(command, crush_slimes)

            if len(levelup_response) > 0:
                response += "\n\n" + levelup_response

        elif item_data.item_props.get("id_item") == ewcfg.item_id_royaltypoudrin:
            # delete a royalty poudrin from the player's inventory
            bknd_item.item_delete(id_item=sought_id)
            crush_slimes = 5000

            levelup_response = user_data.change_slimes(n=crush_slimes, source=ewcfg.source_crush)
            user_data.persist()

            response = "You {} your hard-earned slime crystal with your bare teeth.\nYou gain {} slime. Ah, the joy of writing!".format(command, crush_slimes)

            if len(levelup_response) > 0:
                response += "\n\n" + levelup_response

        elif item_data.item_props.get("id_food") in static_food.vegetable_to_cosmetic_material.keys():
            bknd_item.item_delete(id_item=sought_id)

            crop_name = item_data.item_props.get('food_name')
            # Turn the crop into its proper cosmetic material item.
            cosmetic_material_id = static_food.vegetable_to_cosmetic_material[item_data.item_props.get("id_food")]
            new_item = static_items.item_map.get(cosmetic_material_id)

            new_item_type = ewcfg.it_item
            if new_item != None:
                new_name = new_item.str_name
                new_item_props = itm_utils.gen_item_props(new_item)
            else:
                ewutils.logMsg("ERROR: !crunch failed to retrieve proper cosmetic material for crop {}.".format(item_data.item_props.get("id_food")))
                new_name = None
                new_item_props = None

            generated_item_id = bknd_item.item_create(
                item_type=new_item_type,
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_props=new_item_props
            )

            response = "You {} your {} in your mouth and spit it out to create some {}!!".format(command, crop_name, new_name)

        elif item_data.item_props.get("id_food") in static_food.candy_ids_list:

            bknd_item.item_delete(id_item=sought_id)
            item_name = item_data.item_props.get('food_name')

            if float(getattr(item_data, "time_expir", 0)) < time.time():
                response = "The {} melts disappointingly in your hand...".format(item_name)

            else:
                gristnum = random.randrange(2) + 1
                gristcount = 0

                response = "You crush the {} with an iron grip. You gain {} piece(s) of Double Halloween Grist!".format(item_name, gristnum)

                while gristcount < gristnum:
                    grist = static_items.item_map.get(ewcfg.item_id_doublehalloweengrist)
                    grist_props = itm_utils.gen_item_props(grist)

                    bknd_item.item_create(
                        item_type=grist.item_type,
                        id_user=cmd.message.author.id,
                        id_server=cmd.message.guild.id,
                        item_props=grist_props
                    )

                    gristcount += 1
        elif item_data.item_props.get("id_item") == ewcfg.item_id_negapoudrin:
            # delete a negapoudrin from the player's inventory
            bknd_item.item_delete(id_item=sought_id)
            crush_slimes = -1000000
            # kill player if they have less than 1 million slime
            if user_data.slimes < 1000000:
                user_data.die(cause=ewcfg.cause_suicide)
            # remove 1 million slime from the player
            else:
                levelup_response = user_data.change_slimes(n = crush_slimes, source = ewcfg.source_crush)
                user_data.persist()

                response = "You {} your hard-earned slime crystal with your bare teeth.\nAs the nerve endings in your teeth explode, you realize you bit into negapoudrin! You writhe on the ground as slime gushes from all of your orifices.".format(command)
            
                if len(levelup_response) > 0:
                    response += "\n\n" + levelup_response	

    else:
        if item_search:  # if they didnt forget to specify an item and it just wasn't found
            response = "You don't have one."
        else:
            response = "{} which item? (check **!inventory**)".format(command)

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" player enlists in a faction/gang """


async def enlist(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    user_slimes = user_data.slimes
    time_now = int(time.time())
    bans = user_data.get_bans()
    vouchers = user_data.get_vouchers()

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "You're dead, bitch."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    elif ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
        response = "You can't do that right now."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    elif user_slimes < ewcfg.slimes_toenlist:
        response = "You need to mine more slime to rise above your lowly station. ({}/{})".format(user_slimes, ewcfg.slimes_toenlist)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.tokens_count > 1:
        desired_faction = cmd.tokens[1].lower()
    else:
        response = "Which faction? Say '{} {}', '{} {}', or '{} {}'.".format(ewcfg.cmd_enlist, ewcfg.faction_killers, ewcfg.cmd_enlist, ewcfg.faction_rowdys, ewcfg.cmd_enlist, ewcfg.faction_slimecorp)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if desired_faction == ewcfg.faction_killers:
        if ewcfg.faction_killers in bans:
            response = "You are banned from enlisting in the {}.".format(ewcfg.faction_killers)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif ewcfg.faction_killers not in vouchers and user_data.faction != ewcfg.faction_killers:
            response = "You need a current gang member's permission to join the {}.".format(ewcfg.faction_killers)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif user_data.life_state in [ewcfg.life_state_enlisted, ewcfg.life_state_kingpin] and user_data.faction == ewcfg.faction_killers:
            response = "You are already enlisted in the {}! Look, your name is purple! Get a clue, idiot.".format(user_data.faction)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif user_data.faction == ewcfg.faction_rowdys or user_data.faction == ewcfg.faction_slimecorp:
            response = "Traitor! You can only {} in the {}, you treacherous cretin. Ask for a {} if you're that weak-willed.".format(ewcfg.cmd_enlist, user_data.faction, ewcfg.cmd_pardon)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        # elif user_data.poi not in [ewcfg.poi_id_copkilltown]:
        #	response = "How do you want to enlist in a gang's forces without even being in their headquarters? Get going to Cop Killtown, bitch."
        #	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            response = "Enlisting in the {}.".format(ewcfg.faction_killers)
            user_data.life_state = ewcfg.life_state_enlisted
            user_data.faction = ewcfg.faction_killers
            user_data.time_lastenlist = time_now + ewcfg.cd_enlist
            # user_data.juviemode = 0
            for faction in vouchers:
                user_data.unvouch(faction)
            user_data.persist()
            await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

    elif desired_faction == ewcfg.faction_rowdys:
        if ewcfg.faction_rowdys in bans:
            response = "You are banned from enlisting in the {}.".format(ewcfg.faction_rowdys)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        if ewcfg.faction_rowdys not in vouchers and user_data.faction != ewcfg.faction_rowdys:
            response = "You need a current gang member's permission to join the {}.".format(ewcfg.faction_rowdys)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif user_data.life_state in [ewcfg.life_state_enlisted, ewcfg.life_state_kingpin] and user_data.faction == ewcfg.faction_rowdys:
            response = "You are already enlisted in the {}! Look, your name is pink! Get a clue, idiot.".format(user_data.faction)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif user_data.faction == ewcfg.faction_killers or user_data.faction == ewcfg.faction_slimecorp:
            response = "Traitor! You can only {} in the {}, you treacherous cretin. Ask for a {} if you're that weak-willed.".format(ewcfg.cmd_enlist, user_data.faction, ewcfg.cmd_pardon)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        # elif user_data.poi not in [ewcfg.poi_id_rowdyroughhouse]:
        #	response = "How do you want to enlist in a gang's forces without even being in their headquarters? Get going to the Rowdy Roughhouse, bitch."
        #	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            response = "Enlisting in the {}.".format(ewcfg.faction_rowdys)
            user_data.life_state = ewcfg.life_state_enlisted
            user_data.faction = ewcfg.faction_rowdys
            user_data.time_lastenlist = time_now + ewcfg.cd_enlist
            # user_data.juviemode = 0

            for faction in vouchers:
                user_data.unvouch(faction)
            user_data.persist()
            await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

    elif desired_faction == ewcfg.faction_slimecorp:
        response = "Sorry, pal. That ship has sailed."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        response = "That's not a valid gang you can enlist in, bitch."

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def renounce(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "You're dead, bitch."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    elif user_data.life_state != ewcfg.life_state_enlisted:
        response = "What exactly are you renouncing? Your lackadaisical, idyllic life free of vice and violence? You aren't actually currently enlisted in any gang, retard."

    elif user_data.poi not in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown, ewcfg.poi_id_thebreakroom]:
        response = "To turn in your badge, you must return to your soon-to-be former gang base."

    else:
        renounce_fee = int(user_data.slimes) / 2
        user_data.change_slimes(n=-renounce_fee)
        faction = user_data.faction
        user_data.life_state = ewcfg.life_state_juvenile
        user_data.weapon = -1
        user_data.sidearm = -1
        user_data.persist()
        response = "You are no longer enlisted in the {}, but you are not free of association with them. Your former teammates immediately begin to beat the shit out of you, knocking {} slime out of you before you're able to get away.".format(faction, renounce_fee)
        await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" mine for slime (or endless rocks) """


async def mine(cmd):
    market_data = EwMarket(id_server=cmd.message.author.guild.id)
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    mutations = user_data.get_mutations()
    cosmetic_abilites = itm_utils.get_cosmetic_abilities(id_user=cmd.message.author.id, id_server=cmd.guild.id)
    time_now = int(time.time())
    poi = poi_static.id_to_poi.get(user_data.poi)

    response = ""
    # Kingpins can't mine.
    if user_data.life_state == ewcfg.life_state_kingpin or user_data.life_state == ewcfg.life_state_grandfoe:
        return

    # ghosts cant mine (anymore)
    if user_data.life_state == ewcfg.life_state_corpse:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You can't mine while you're dead. Try {}.".format(ewcfg.cmd_revive)))

    # Enlisted players only mine at certain times.
    if user_data.life_state == ewcfg.life_state_enlisted:
        if user_data.faction == ewcfg.faction_rowdys and (market_data.clock < 8 or market_data.clock > 17) and ewcfg.mutation_id_lightminer not in mutations:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Rowdies only mine in the daytime. Wait for full daylight at 8am.".format(ewcfg.cmd_revive)))

        if user_data.faction == ewcfg.faction_killers and (market_data.clock < 20 and market_data.clock > 5) and ewcfg.mutation_id_lightminer not in mutations:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Killers only mine under cover of darkness. Wait for nightfall at 8pm.".format(ewcfg.cmd_revive)))

    # Mine only in the mines.
    if cmd.message.channel.name in ewcfg.mining_channels:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        if user_data.hunger >= user_data.get_hunger_max():
            return await mismine(cmd, user_data, "exhaustion")
        # return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You've exhausted yourself from mining. You'll need some refreshment before getting back to work."))

        else:
            printgrid = True
            hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
            extra = hunger_cost_mod - int(hunger_cost_mod)  # extra is the fractional part of hunger_cost_mod

            world_events = bknd_worldevent.get_world_events(id_server=cmd.guild.id)
            mining_type = ewcfg.mines_mining_type_map.get(user_data.poi)
            for id_event in world_events:

                if world_events.get(id_event) == ewcfg.event_type_minecollapse:
                    event_data = EwWorldEvent(id_event=id_event)
                    if int(event_data.event_props.get('id_user')) == user_data.id_user and event_data.event_props.get('poi') == user_data.poi:
                        captcha = event_data.event_props.get('captcha').lower()
                        tokens_lower = []
                        for token in cmd.tokens[1:]:
                            tokens_lower.append(token.lower())

                        if captcha in tokens_lower:
                            bknd_worldevent.delete_world_event(id_event=id_event)
                            response = "You escape from the collapsing mineshaft."
                            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        elif ewcfg.mutation_id_lightminer in mutations:
                            bknd_worldevent.delete_world_event(id_event=id_event)
                            response = "You nimbly step outside the collapse without even thinking about it."
                            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        else:
                            return await mismine(cmd, user_data, ewcfg.event_type_minecollapse)

            if user_data.poi not in juviecmdutils.mines_map:
                response = "You can't mine here! Go to the mines in Juvie's Row, Toxington, or Cratersville!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            elif user_data.id_server not in juviecmdutils.mines_map.get(user_data.poi):
                init_grid(user_data.poi, user_data.id_server)
                printgrid = True

            grid_cont = juviecmdutils.mines_map.get(user_data.poi).get(user_data.id_server)
            grid = grid_cont.grid

            grid_type = ewcfg.grid_type_by_mining_type.get(mining_type)
            if grid_type != grid_cont.grid_type:
                init_grid(user_data.poi, user_data.id_server)
                printgrid = True
                grid_cont = juviecmdutils.mines_map.get(user_data.poi).get(user_data.id_server)
                grid = grid_cont.grid

            # minesweeper = True
            # grid_multiplier = grid_cont.cells_mined ** 0.4
            # flag = False
            mining_yield = get_mining_yield_by_grid_type(cmd, grid_cont)

            if type(mining_yield) == type(""):
                response = mining_yield
                if len(response) > 0:
                    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                if time_now > grid_cont.time_last_posted + 10:
                    await print_grid(cmd)
                return

            if mining_yield == 0:
                user_data.hunger += ewcfg.hunger_permine * int(hunger_cost_mod)
                user_data.persist()
                # response = "This vein has already been mined dry."
                # await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                if printgrid:
                    return await print_grid(cmd)
                else:
                    return

            has_pickaxe = False

            if user_data.weapon >= 0:
                weapon_item = EwItem(id_item=user_data.weapon)
                weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
                if weapon.id_weapon == ewcfg.weapon_id_pickaxe and user_data.life_state != ewcfg.life_state_juvenile:
                    has_pickaxe = True
            # if user_data.sidearm >= 0:
            #	sidearm_item = EwItem(id_item=user_data.sidearm)
            #	sidearm = static_weapons.weapon_map.get(sidearm_item.item_props.get("weapon_type"))
            #	if sidearm.id_weapon == ewcfg.weapon_id_pickaxe:
            #		has_pickaxe = True

            # Determine if an item is found.
            unearthed_item = False
            unearthed_item_amount = (random.randrange(3) + 5)  # anywhere from 5-7 drops

            # juvies get items 4 times as often as enlisted players
            unearthed_item_chance = 1 / ewcfg.unearthed_item_rarity
            if user_data.life_state == ewcfg.life_state_juvenile:  # and not user_data.juviemode:
                unearthed_item_chance *= 2
            if has_pickaxe == True:  # and not user_data.juviemode:
                unearthed_item_chance *= 1.5
            if ewcfg.mutation_id_lucky in mutations:  # and not user_data.juviemode:
                unearthed_item_chance *= 1.33
            if ewcfg.cosmeticAbility_id_lucky in cosmetic_abilites:  # and not user_data.juviemode:
                unearthed_item_chance *= 1.33

            # event bonus
            for id_event in world_events:

                if world_events.get(id_event) == ewcfg.event_type_slimefrenzy:
                    event_data = EwWorldEvent(id_event=id_event)
                    if event_data.event_props.get('poi') == user_data.poi and int(event_data.event_props.get('id_user')) == user_data.id_user:
                        mining_yield *= 2

                if world_events.get(id_event) == ewcfg.event_type_poudrinfrenzy:
                    event_data = EwWorldEvent(id_event=id_event)
                    if event_data.event_props.get('poi') == user_data.poi and int(event_data.event_props.get('id_user')) == user_data.id_user:
                        unearthed_item_chance = 1
                        unearthed_item_amount = 1

            if random.random() < 0.05:
                id_event = create_mining_event(cmd)
                event_data = EwWorldEvent(id_event=id_event)

                if event_data.id_event == -1:
                    return ewutils.logMsg("Error couldn't find world event with id {}".format(id_event))

                if event_data.event_type == ewcfg.event_type_slimeglob:
                    mining_yield *= 4
                    bknd_worldevent.delete_world_event(id_event=id_event)

                if event_data.time_activate <= time.time():

                    event_def = poi_static.event_type_to_def.get(event_data.event_type)
                    if event_def == None:
                        return ewutils.logMsg("Error, couldn't find event def for event type {}".format(event_data.event_type))
                    str_event_start = event_def.str_event_start

                    if event_data.event_type == ewcfg.event_type_minecollapse:
                        str_event_start = str_event_start.format(cmd=ewcfg.cmd_mine, captcha=ewutils.text_to_regional_indicator(event_data.event_props.get('captcha')))
                        await fe_utils.send_response(str_event_start, cmd)
                        event_data.time_expir = time_now + 60
                        event_data.persist()
                        str_event_start = ""

                    if str_event_start != "":
                        response += str_event_start + "\n"

            if random.random() < unearthed_item_chance:
                unearthed_item = True

            if unearthed_item == True:
                # If there are multiple possible products, randomly select one.
                item = random.choice(vendors.mine_results)

                if bknd_item.check_inv_capacity(user_data=user_data, item_type=item.item_type):

                    item_props = itm_utils.gen_item_props(item)

                    for creation in range(unearthed_item_amount):
                        bknd_item.item_create(
                            item_type=item.item_type,
                            id_user=cmd.message.author.id,
                            id_server=cmd.guild.id,
                            item_props=item_props
                        )

                    if unearthed_item_amount == 1:
                        response += "You unearthed a {}! ".format(item.str_name)
                    else:
                        response += "You unearthed {} {}s! ".format(unearthed_item_amount, item.str_name)

                    ewstats.change_stat(user=user_data, metric=ewcfg.stat_lifetime_poudrins, n=unearthed_item_amount)

            # ewutils.logMsg('{} has found {} {}(s)!'.format(cmd.message.author.display_name, item.str_name, unearthed_item_amount))

            user_initial_level = user_data.slimelevel

            # Add mined slime to the user.
            slime_bylevel = ewutils.slime_bylevel(user_data.slimelevel)

            # mining_yield = math.floor((slime_bylevel / 10) + 1)
            # alternate_yield = math.floor(200 + slime_bylevel ** (1 / math.e))

            # mining_yield = min(mining_yield, alternate_yield)

            controlling_faction = poi_utils.get_subzone_controlling_faction(user_data.poi, user_data.id_server)

            if controlling_faction != "" and controlling_faction == user_data.faction:
                mining_yield *= 2

            if has_pickaxe == True:
                mining_yield *= 2
            if user_data.life_state == ewcfg.life_state_juvenile:
                mining_yield *= 2

            # trauma = se_static.trauma_map.get(user_data.trauma)
            # if trauma != None and trauma.trauma_class == ewcfg.trauma_class_slimegain:
            #	mining_yield *= (1 - 0.5 * user_data.degradation / 100)

            mining_yield = max(0, round(mining_yield))

            # Fatigue the miner.

            user_data.hunger += ewcfg.hunger_permine * int(hunger_cost_mod)
            if extra > 0:  # if hunger_cost_mod is not an integer
                # there's an x% chance that an extra stamina is deducted, where x is the fractional part of hunger_cost_mod in percent (times 100)
                if random.randint(1, 100) <= extra * 100:
                    user_data.hunger += ewcfg.hunger_permine

            levelup_response = user_data.change_slimes(n=mining_yield, source=ewcfg.source_mining)

            was_levelup = True if user_initial_level < user_data.slimelevel else False

            # Tell the player their slime level increased and/or they unearthed an item.
            if was_levelup:
                response += levelup_response

            user_data.persist()

            if printgrid:
                await print_grid(cmd)

            # gangsters don't need their roles updated
            if user_data.life_state == ewcfg.life_state_juvenile:
                await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

    else:
        return await mismine(cmd, user_data, "channel")
    # response = "You can't mine here! Go to the mines in Juvie's Row, Toxington, or Cratersville!"

    if len(response) > 0:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" mine for slime (or endless rocks) """


async def flag(cmd):
    market_data = EwMarket(id_server=cmd.message.author.guild.id)
    user_data = EwUser(member=cmd.message.author)
    mutations = user_data.get_mutations()
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    mutations = user_data.get_mutations()
    time_now = int(time.time())

    response = ""
    # Kingpins can't mine.
    if user_data.life_state == ewcfg.life_state_kingpin or user_data.life_state == ewcfg.life_state_grandfoe:
        return

    # ghosts cant mine (anymore)
    if user_data.life_state == ewcfg.life_state_corpse:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You can't mine while you're dead. Try {}.".format(ewcfg.cmd_revive)))

    # Enlisted players only mine at certain times.
    if user_data.life_state == ewcfg.life_state_enlisted:
        if user_data.faction == ewcfg.faction_rowdys and (market_data.clock < 8 or market_data.clock > 17) and ewcfg.mutation_id_lightminer not in mutations:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Rowdies only mine in the daytime. Wait for full daylight at 8am.".format(ewcfg.cmd_revive)))

        if user_data.faction == ewcfg.faction_killers and (market_data.clock < 20 and market_data.clock > 5) and ewcfg.mutation_id_lightminer not in mutations:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Killers only mine under cover of darkness. Wait for nightfall at 8pm.".format(ewcfg.cmd_revive)))

    # Mine only in the mines.
    if cmd.message.channel.name in ewcfg.mining_channels:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        if user_data.hunger >= user_data.get_hunger_max():
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You've exhausted yourself from mining. You'll need some refreshment before getting back to work."))

        else:
            printgrid = True
            hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
            extra = hunger_cost_mod - int(hunger_cost_mod)  # extra is the fractional part of hunger_cost_mod

            mining_type = ewcfg.mines_mining_type_map.get(user_data.poi)

            if mining_type != ewcfg.mining_type_minesweeper:
                response = "What do you think you can flag here?"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            if user_data.poi not in juviecmdutils.mines_map:
                response = "You can't mine here! Go to the mines in Juvie's Row, Toxington, or Cratersville!"
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            elif user_data.id_server not in juviecmdutils.mines_map.get(user_data.poi):
                init_grid(user_data.poi, user_data.id_server)
                printgrid = True

            grid_cont = juviecmdutils.mines_map.get(user_data.poi).get(user_data.id_server)
            grid = grid_cont.grid

            grid_type = ewcfg.grid_type_by_mining_type.get(mining_type)
            if grid_type != grid_cont.grid_type:
                init_grid(user_data.poi, user_data.id_server)
                printgrid = True
                grid_cont = juviecmdutils.mines_map.get(user_data.poi).get(user_data.id_server)
                grid = grid_cont.grid

            row = -1
            col = -1
            if cmd.tokens_count < 2:
                response = "Please specify which Minesweeper vein to flag."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            for token in cmd.tokens[1:]:

                coords = token.lower()
                if col < 1:

                    for char in coords:
                        if char in ewcfg.alphabet:
                            col = ewcfg.alphabet.index(char)
                            coords = coords.replace(char, "")
                if row < 1:
                    try:
                        row = int(coords)
                    except:
                        row = -1

            row -= 1

            if row not in range(len(grid)) or col not in range(len(grid[row])):
                response = "Invalid Minesweeper vein."


            elif grid[row][col] == ewcfg.cell_empty_marked:
                grid[row][col] = ewcfg.cell_empty

            elif grid[row][col] == ewcfg.cell_mine_marked:
                grid[row][col] = ewcfg.cell_mine

            elif grid[row][col] == ewcfg.cell_empty_open:
                response = "This vein has already been mined dry."

            elif grid[row][col] == ewcfg.cell_mine:
                grid[row][col] = ewcfg.cell_mine_marked

            elif grid[row][col] == ewcfg.cell_empty:
                grid[row][col] = ewcfg.cell_empty_marked

            if printgrid:
                await print_grid(cmd)


    else:
        response = "You can't mine here! Go to the mines in Juvie's Row, Toxington, or Cratersville!"

    if len(response) > 0:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


""" scavenge for slime """


async def scavenge(cmd):
    market_data = EwMarket(id_server=cmd.message.author.guild.id)
    user_data = EwUser(member=cmd.message.author)
    mutations = user_data.get_mutations()

    time_now = int(time.time())
    response = ""

    time_since_last_scavenge = time_now - user_data.time_lastscavenge

    # Kingpins can't scavenge.
    if user_data.life_state == ewcfg.life_state_kingpin or user_data.life_state == ewcfg.life_state_grandfoe:
        return

    # ghosts cant scavenge
    if user_data.life_state == ewcfg.life_state_corpse:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "What would you want to do that for? You're a ghost, you have no need for such lowly materialistic possessions like slime. You only engage in intellectual pursuits now. {} if you want to give into your base human desire to see numbers go up.".format(ewcfg.cmd_revive)))
    # currently not active - no cooldown
    if time_since_last_scavenge < ewcfg.cd_scavenge:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Slow down, you filthy hyena."))

    if user_data.poi == ewcfg.poi_id_slimesea:
        if user_data.life_state == ewcfg.life_state_shambler:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Are you trying to grab random trash instead of !searchingforbrainz? Pretty cringe bro..."))
        else:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You consider diving down to the bottom of the sea to grab some sick loot, but quickly change your mind when you {}.".format(random.choice(ewcfg.sea_scavenge_responses))))

    # Scavenge only in location channels
    if ewutils.channel_name_is_poi(cmd.message.channel.name) == True:
        if user_data.hunger >= user_data.get_hunger_max():
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You are too exhausted to scrounge up scraps of slime off the street! Go get some grub!"))
        else:

            if juviecmdutils.scavenge_combos.get(user_data.id_user) == None:
                juviecmdutils.scavenge_combos[user_data.id_user] = 0

            combo = juviecmdutils.scavenge_combos.get(user_data.id_user)

            district_data = EwDistrict(district=user_data.poi, id_server=cmd.message.author.guild.id)

            user_initial_level = user_data.slimelevel
            # add scavenged slime to user
            if ewcfg.mutation_id_trashmouth in mutations:
                combo += 5

            time_since_last_scavenge = min(max(1, time_since_last_scavenge), ewcfg.soft_cd_scavenge)

            # scavenge_mod = 0.003 * (time_since_last_scavenge ** 0.9)
            scavenge_mod = 0.005 * combo

            if (ewcfg.mutation_id_whitenationalist in mutations or ewcfg.mutation_id_airlock in mutations) and market_data.weather == "snow":
                scavenge_mod *= 1.5

            if ewcfg.mutation_id_airlock in mutations and market_data.weather == "snow":
                scavenge_mod *= 1.5

            if ewcfg.mutation_id_webbedfeet in mutations:
                district_slimelevel = len(str(district_data.slimes))
                scavenge_mod *= max(1, min(district_slimelevel - 3, 4))

            scavenge_yield = math.floor(scavenge_mod * district_data.slimes)

            levelup_response = user_data.change_slimes(n=scavenge_yield, source=ewcfg.source_scavenging)
            district_data.change_slimes(n=-1 * scavenge_yield, source=ewcfg.source_scavenging)
            district_data.persist()

            if levelup_response != "":
                response += levelup_response + "\n\n"
            # response += "You scrape together {} slime from the streets.\n\n".format(scavenge_yield)
            if cmd.tokens_count > 1:

                item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
                has_comboed = False

                if juviecmdutils.scavenge_combos.get(user_data.id_user) > 0 and (time_now - user_data.time_lastscavenge) < 60:
                    if juviecmdutils.scavenge_captchas.get(user_data.id_user).lower() == item_search.lower():
                        juviecmdutils.scavenge_combos[user_data.id_user] += 1
                        new_captcha = gen_scavenge_captcha(n=juviecmdutils.scavenge_combos.get(user_data.id_user), user_data=user_data)
                        response += "New captcha: **" + ewutils.text_to_regional_indicator(new_captcha) + "**"
                        if ewcfg.mutation_id_webbedfeet in mutations:
                            response += "\nYour flippers pick up {:,} slime.".format(scavenge_yield)
                        juviecmdutils.scavenge_captchas[user_data.id_user] = new_captcha
                        has_comboed = True

                        if ewcfg.mutation_id_dumpsterdiver in mutations:
                            has_comboed = False
                            item_search = item_search[random.randrange(len(item_search))]

                    else:
                        juviecmdutils.scavenge_combos[user_data.id_user] = 0

                if not has_comboed:
                    loot_resp = itm_utils.item_lootspecific(
                        user_data=user_data,
                        item_search=item_search
                    )

                    if loot_resp != "":
                        response = loot_resp + "\n\n" + response

            else:
                loot_multiplier = 1.0 + bknd_item.get_inventory_size(owner=user_data.poi, id_server=user_data.id_server)
                loot_chance = loot_multiplier / ewcfg.scavenge_item_rarity
                if ewcfg.mutation_id_dumpsterdiver in mutations:
                    loot_chance *= 10
                if random.random() < loot_chance:
                    loot_resp = itm_utils.item_lootrandom(
                        user_data
                    )

                    if loot_resp != "":
                        response += loot_resp + "\n\n"

                juviecmdutils.scavenge_combos[user_data.id_user] = 1
                new_captcha = gen_scavenge_captcha(n=1, user_data=user_data)
                response += "New captcha: **" + ewutils.text_to_regional_indicator(new_captcha) + "**"
                if ewcfg.mutation_id_webbedfeet in mutations:
                    response += "\nYour flippers pick up {:,} slime.".format(scavenge_yield)
                juviecmdutils.scavenge_captchas[user_data.id_user] = new_captcha

            # Fatigue the scavenger.
            hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
            extra = hunger_cost_mod - int(hunger_cost_mod)  # extra is the fractional part of hunger_cost_mod

            user_data.hunger += ewcfg.hunger_perscavenge * int(hunger_cost_mod)
            if extra > 0:  # if hunger_cost_mod is not an integer
                # there's an x% chance that an extra stamina is deducted, where x is the fractional part of hunger_cost_mod in percent (times 100)
                if random.randint(1, 100) <= extra * 100:
                    user_data.hunger += ewcfg.hunger_perscavenge

            user_data.time_lastscavenge = time_now

            user_data.persist()

            if not response == "":
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            # gangsters don't need their roles updated
            if user_data.life_state == ewcfg.life_state_juvenile:
                await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
    else:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You'll find no slime here, this place has been picked clean. Head into the city to try and scavenge some slime."))


""" LOL """


async def juviemode(cmd):
    # user_data = EwUser(member = cmd.message.author)
    response = "What law? Juvies die, bitch."
    # if user_data.juviemode == 1:
    #	user_data.juviemode = 0
    #	user_data.persist()
    #	response = "You can't fucking take anymore. Slime. You need slime. SLIME. **SLLLLLLLLIIIIIIIIIMMMMMMMEEEEE!!!!!!!**"
    # elif user_data.life_state != ewcfg.life_state_juvenile:
    #	response = "You think anyone but a cowardly ass Juvie would follow the law? You're not cut out for that life."
    # elif user_data.slimelevel > ewcfg.max_safe_level:
    #	response = "You need to be level 18 and under. You're too plump with slime to start following the law now. Get dead, kid."
    # else:
    #	user_data.juviemode = 1
    #	user_data.persist()
    #	response = "You summon forth all the cowardice in your heart, to forgo even slime, the most basic joy. You vow to carry no more than 100,000, the NLACakaNM's legal limit, on your person at any time."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
