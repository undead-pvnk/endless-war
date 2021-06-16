import asyncio
import re
import time

import discord

from ew import prank as ewprank
from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.backend.player import EwPlayer
from ew.cmd import debug as ewdebug, smelting as ewsmelting
from ew.static import cfg as ewcfg
from ew.static import cosmetics
from ew.static import hue as hue_static
from ew.static import poi as poi_static
from ew.static import weapons as static_weapons
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as itm_utils
from ew.utils import loop as loop_utils
from ew.utils import poi as poi_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict
from .utils import item_drop


async def soulextract(cmd):
    usermodel = EwUser(member=cmd.message.author)
    playermodel = EwPlayer(id_user=cmd.message.author.id, id_server=cmd.guild.id)
    if usermodel.has_soul == 1 and (ewutils.active_target_map.get(usermodel.id_user) == None or ewutils.active_target_map.get(usermodel.id_user) == ""):
        bknd_item.item_create(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type=ewcfg.it_cosmetic,
            item_props={
                'id_cosmetic': "soul",
                'cosmetic_name': "{}'s soul".format(playermodel.display_name),
                'cosmetic_desc': "The immortal soul of {}. It dances with a vivacious energy inside its jar.\n If you listen to it closely you can hear it whispering numbers: {}.".format(playermodel.display_name, cmd.message.author.id),
                'str_onadorn': ewcfg.str_soul_onadorn,
                'str_unadorn': ewcfg.str_soul_unadorn,
                'str_onbreak': ewcfg.str_soul_onbreak,
                'rarity': ewcfg.rarity_patrician,
                'attack': 6,
                'defense': 6,
                'speed': 6,
                'ability': None,
                'durability': ewcfg.soul_durability,
                'size': 6,
                'fashion_style': ewcfg.style_cool,
                'freshness': 10,
                'adorned': 'false',
                'user_id': usermodel.id_user
            }
        )

        usermodel.has_soul = 0
        usermodel.persist()
        response = "You tremble at the thought of trying this. Nothing ventured, nothing gained, you suppose. With all your mental fortitude you jam your hand deep into your chest and begin to pull out the very essence of your being. Your spirit, aspirations, everything that made you who you are begins to slowly drain from your mortal effigy until you feel absolutely nothing. Your soul flickers about, taunting you from outside your body. You capture it in a jar, almost reflexively.\n\nWow. Your personality must suck now."
    elif usermodel.has_soul == 1 and ewutils.active_target_map.get(usermodel.id_user) != "":
        response = "Now's not the time to be playing with your soul, dumbass! You have to focus on pointing the gun at your head!"
    else:
        response = "There's nothing left in you to extract. You already spent the soul you had."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def returnsoul(cmd):
    usermodel = EwUser(member=cmd.message.author)
    # soul = bknd_item.find_item(item_search="soul", id_user=cmd.message.author.id, id_server=cmd.guild.id)
    user_inv = bknd_item.inventory(id_user=cmd.message.author.id, id_server=cmd.guild.id, item_type_filter=ewcfg.it_cosmetic)
    soul_item = None
    soul = None
    for inv_object in user_inv:
        soul = inv_object
        soul_item = EwItem(id_item=soul.get('id_item'))
        if soul_item.item_props.get('user_id') == str(cmd.message.author.id):
            break

    if usermodel.has_soul == 1:
        response = "Your current soul is a little upset you tried to give it a roommate. Only one fits in your body at a time."
    elif soul:

        if soul.get('item_type') == ewcfg.it_cosmetic and soul_item.item_props.get('id_cosmetic') == "soul":
            if soul_item.item_props.get('user_id') != str(cmd.message.author.id):
                response = "That's not your soul. Nice try, though."
            else:
                response = "You open the soul jar and hold the opening to your chest. The soul begins to crawl in, and a warmth returns to your body. Not exactly the warmth you had before, but it's too wonderful to pass up. You feel invigorated and ready to take on the world."
                bknd_item.item_delete(id_item=soul.get('id_item'))
                usermodel.has_soul = 1
                usermodel.persist()
        else:
            response = "Nice try, but your mortal coil recognizes a fake soul when it sees it."
    else:
        response = "You don't have a soul to absorb. Hopelessness is no fun, but don't get all delusional on us now."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def squeeze(cmd):
    usermodel = EwUser(member=cmd.message.author)
    soul_inv = bknd_item.inventory(id_user=cmd.message.author.id, id_server=cmd.guild.id, item_type_filter=ewcfg.it_cosmetic)

    if usermodel.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if usermodel.life_state == ewcfg.life_state_corpse:
        response = "Alas, you lack the mortal appendages required to wring the slime out of someone's soul."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count <= 0:
        response = "Specify a soul you want to squeeze the life out of."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    target = cmd.mentions[0]
    if target.id == cmd.message.author.id:
        targetmodel = usermodel
    else:
        targetmodel = EwUser(member=target)

    if cmd.mentions_count > 1:
        response = "One dehumanizing soul-clutch at a time, please."
    elif targetmodel.life_state == ewcfg.life_state_corpse:
        response = "Enough already. They're dead."
    else:

        playermodel = EwPlayer(id_user=targetmodel.id_user)
        receivingreport = ""  # the receiver of the squeeze gets this in their channel

        squeezetext = re.sub("<.+>", "", cmd.message.content[(len(cmd.tokens[0])):]).strip()
        if len(squeezetext) > 500:
            squeezetext = squeezetext[:-500]

        poi = None
        target_item = None
        for soul in soul_inv:
            soul_item = EwItem(id_item=soul.get('id_item'))
            if soul_item.item_props.get('id_cosmetic') == 'soul' and int(soul_item.item_props.get('user_id')) == targetmodel.id_user:
                target_item = soul

        if targetmodel.has_soul == 1:
            response = "They look pretty soulful right now. You can't do anything to them."
        elif target_item == None:
            response = "You don't have their soul."
        elif (int(time.time()) - usermodel.time_lasthaunt) < ewcfg.cd_squeeze:
            timeleft = ewcfg.cd_squeeze - (int(time.time()) - usermodel.time_lasthaunt)
            response = "It's still all rubbery and deflated from the last time you squeezed it. Give it {} seconds.".format(timeleft)
        else:
            if targetmodel.life_state == ewcfg.life_state_shambler:
                receivingreport = "You feel searing palpitations in your chest, but your lust for brains overwhelms the pain of {} squeezing your soul.".format(cmd.message.author.display_name)
            elif squeezetext != "":
                receivingreport = "A voice in your head screams: \"{}\"\nSuddenly, you feel searing palpitations in your chest, and vomit slime all over the floor. Dammit, {} must be fucking around with your soul.".format(squeezetext, cmd.message.author.display_name)
            else:
                receivingreport = "You feel searing palpitations in your chest, and vomit slime all over the floor. Dammit, {} must be fucking with your soul.".format(cmd.message.author.display_name)

            poi = poi_static.id_to_poi.get(targetmodel.poi)

            usermodel.time_lasthaunt = int(time.time())
            usermodel.persist()

            if targetmodel.life_state != ewcfg.life_state_shambler:
                penalty = (targetmodel.slimes * -0.25)
                targetmodel.change_slimes(n=penalty, source=ewcfg.source_haunted)
                targetmodel.persist()

                district_data = EwDistrict(district=targetmodel.poi, id_server=cmd.guild.id)
                district_data.change_slimes(n=-penalty, source=ewcfg.source_squeeze)
                district_data.persist()

            if receivingreport != "":
                loc_channel = fe_utils.get_channel(cmd.guild, poi.channel)
                await fe_utils.send_message(cmd.client, loc_channel, fe_utils.formatMessage(target, receivingreport))

            response = "You tightly squeeze {}'s soul in your hand, jeering into it as you do so. This thing was worth every penny.".format(playermodel.display_name)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
    Dump out a player's inventory.
"""


async def inventory_print(cmd):
    community_chest = False
    can_message_user = True
    item_type = None

    inventory_source = cmd.message.author.id

    player = EwPlayer(id_user=cmd.message.author.id)

    user_data = EwUser(id_user=cmd.message.author.id, id_server=player.id_server)
    poi = poi_static.id_to_poi.get(user_data.poi)
    if cmd.tokens[0].lower() == ewcfg.cmd_communitychest:
        if poi.community_chest == None:
            response = "There is no community chest here."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif cmd.message.channel.name != poi.channel:
            response = "You can't see the community chest from here."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        community_chest = True
        can_message_user = False
        inventory_source = poi.community_chest

    sort_by_type = False
    sort_by_name = False
    sort_by_id = False

    stacking = False
    search = False
    stacked_message_list = []
    stacked_item_map = {}

    if cmd.tokens_count > 1:
        token_list = cmd.tokens[1:]
        lower_token_list = []
        for token in token_list:
            token = token.lower()
            lower_token_list.append(token)

        if 'type' in lower_token_list:
            sort_by_type = True
        elif 'name' in lower_token_list:
            sort_by_name = True
        elif 'id' in lower_token_list:
            sort_by_id = True

        if 'stack' in lower_token_list:
            stacking = True

        if 'general' in lower_token_list:
            item_type = ewcfg.it_item

        if 'weapon' in lower_token_list:
            item_type = ewcfg.it_weapon

        if 'furniture' in lower_token_list:
            item_type = ewcfg.it_furniture

        if 'cosmetic' in lower_token_list:
            item_type = ewcfg.it_cosmetic

        if 'food' in lower_token_list:
            item_type = ewcfg.it_food

        if 'search' in lower_token_list:
            stacking = False
            sort_by_id = False
            sort_by_name = False
            sort_by_type = False
            search = True

    if sort_by_id:
        items = bknd_item.inventory(
            id_user=inventory_source,
            id_server=player.id_server,
            item_sorting_method='id',
            item_type_filter=item_type
        )
    elif sort_by_type:
        items = bknd_item.inventory(
            id_user=inventory_source,
            id_server=player.id_server,
            item_sorting_method='type',
            item_type_filter=item_type
        )
    elif search == True:
        items = itm_utils.find_item_all(
            item_search=ewutils.flattenTokenListToString(cmd.tokens[2:]),
            id_server=player.id_server,
            id_user=inventory_source,
            exact_search=False,
            search_names=True
        )
    else:
        items = bknd_item.inventory(
            id_user=inventory_source,
            id_server=player.id_server,
            item_type_filter=item_type
        )

    if community_chest:
        if len(items) == 0:
            response = "The community chest is empty."
        else:
            response = "__The community chest contains:__"
    else:
        if len(items) == 0:
            response = "You don't have anything."
        else:
            response = "__You are holding:__"

    msg_handle = None
    try:
        if can_message_user:
            msg_handle = await fe_utils.send_message(cmd.client, cmd.message.author, response)
    except discord.errors.Forbidden:
        response = "You'll have to allow Endless War to send you DMs to check your inventory!"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    except:
        can_message_user = False

    if msg_handle is None:
        can_message_user = False

    if not can_message_user:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if sort_by_name:
        items = sorted(items, key=lambda item: item.get('name').lower())

    if len(items) > 0:

        response = ""
        current_type = ""

        for item in items:
            id_item = item.get('id_item')
            quantity = item.get('quantity')

            if not stacking:
                response_part = "\n{id_item}: {soulbound_style}{name}{soulbound_style}{quantity}".format(
                    id_item=item.get('id_item'),
                    name=item.get('name'),
                    soulbound_style=("**" if item.get('soulbound') else ""),
                    quantity=(" x{:,}".format(quantity) if (quantity > 1) else "")
                )

                # Print item type labels if sorting by type and showing a new type of items
                if sort_by_type:
                    if current_type != item.get('item_type'):
                        current_type = item.get('item_type')
                        response_part = "\n**=={}==**".format(current_type.upper()) + response_part
            else:

                item_name = item.get('name')
                if item_name in stacked_item_map:
                    stacked_item = stacked_item_map.get(item_name)
                    stacked_item['quantity'] += item.get('quantity')
                else:
                    stacked_item_map[item_name] = item

            if not stacking and len(response) + len(response_part) > 1492:
                if can_message_user:
                    await fe_utils.send_message(cmd.client, cmd.message.author, response)
                else:
                    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                response = ""

            if not stacking:
                response += response_part

        if stacking:
            current_type = ""
            item_names = stacked_item_map.keys()
            if sort_by_name:
                item_names = sorted(item_names)
            for item_name in item_names:
                item = stacked_item_map.get(item_name)
                quantity = item.get('quantity')
                response_part = "\n{soulbound_style}{name}{soulbound_style}{quantity}".format(
                    name=item.get('name'),
                    soulbound_style=("**" if item.get('soulbound') else ""),
                    quantity=(" **x{:,}**".format(quantity) if (quantity > 0) else "")
                )

                # Print item type labels if sorting by type and showing a different type of items
                if sort_by_type:
                    if current_type != item.get('item_type'):
                        current_type = item.get('item_type')
                        response_part = "\n**=={}==**".format(current_type.upper()) + response_part

                if len(response) + len(response_part) > 1492:
                    if can_message_user:
                        await fe_utils.send_message(cmd.client, cmd.message.author, response)
                    else:
                        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    response = ""
                response += response_part

        if can_message_user:
            await fe_utils.send_message(cmd.client, cmd.message.author, response)
        else:
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
    Dump out the visual description of an item.
"""


async def item_look(cmd):
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    author = cmd.message.author
    player = EwPlayer(id_user=cmd.message.author.id)
    server = player.id_server
    user_data = EwUser(id_user=cmd.message.author.id, id_server=server)
    poi = poi_static.id_to_poi.get(user_data.poi)
    mutations = user_data.get_mutations()

    if user_data.visiting != ewcfg.location_id_empty:
        user_data = EwUser(id_user=user_data.visiting, id_server=server)

    item_dest = []

    item_sought_inv = bknd_item.find_item(item_search=item_search, id_user=author.id, id_server=server)
    item_dest.append(item_sought_inv)

    iterate = 0
    response = ""

    if poi.is_apartment:
        item_sought_closet = bknd_item.find_item(item_search=item_search,
                                                 id_user=str(user_data.id_user) + ewcfg.compartment_id_closet, id_server=server)
        item_sought_fridge = bknd_item.find_item(item_search=item_search,
                                                 id_user=str(user_data.id_user) + ewcfg.compartment_id_fridge, id_server=server)
        item_sought_decorate = bknd_item.find_item(item_search=item_search,
                                                   id_user=str(user_data.id_user) + ewcfg.compartment_id_decorate,
                                                   id_server=server)

        item_dest.append(item_sought_closet)
        item_dest.append(item_sought_fridge)
        item_dest.append(item_sought_decorate)

    for item_sought in item_dest:
        iterate += 1
        if item_sought:
            item = EwItem(id_item=item_sought.get('id_item'))

            id_item = item.id_item
            name = item_sought.get('name')
            response = item_sought.get('item_def').str_desc

            # Replace up to two levels of variable substitutions.
            if response.find('{') >= 0:
                response = response.format_map(item.item_props)

                if response.find('{') >= 0:
                    try:
                        response = response.format_map(item.item_props)
                    except:
                        pass

            if item.item_type == ewcfg.it_food:
                if float(item.item_props.get('time_expir') if not None else 0) < time.time() and item.id_owner[
                                                                                                 -6:] != ewcfg.compartment_id_fridge:
                    response += " This food item is rotten"
                    if ewcfg.mutation_id_spoiledappetite in mutations:
                        response += ". Yummy!"
                    else:
                        response += "."
                    # item_drop(id_item)

            if item.item_type == ewcfg.it_weapon:
                response += "\n\n"

                if item.item_props.get("married") != "":
                    previous_partner = EwPlayer(id_user=int(item.item_props.get("married")), id_server=server)

                    if not user_data.weaponmarried or int(item.item_props.get("married")) != str(
                            user_data.id_user) or item.id_item != user_data.weapon:
                        response += "There's a barely legible engraving on the weapon that reads *{} :heart: {}*.\n\n".format(
                            previous_partner.display_name, name)
                    else:
                        response += "Your beloved partner. You can't help but give it a little kiss on the handle.\n"

                weapon = static_weapons.weapon_map.get(item.item_props.get("weapon_type"))

                if ewcfg.weapon_class_ammo in weapon.classes:
                    response += "Ammo: {}/{}".format(item.item_props.get("ammo"), weapon.clip_size) + "\n"

                if ewcfg.weapon_class_captcha in weapon.classes:
                    captcha = item.item_props.get("captcha")
                    if captcha not in [None, ""]:
                        response += "Security Code: **{}**".format(ewutils.text_to_regional_indicator(captcha)) + "\n"

                totalkills = int(item.item_props.get("totalkills")) if item.item_props.get("totalkills") != None else 0

                if totalkills < 10:
                    response += "It looks brand new" + (
                        ".\n" if totalkills == 0 else ", having only killed {} people.\n".format(totalkills))
                elif totalkills < 100:
                    response += "There's some noticeable wear and tear on it. It has killed {} people.\n".format(
                        totalkills)
                else:
                    response += "A true legend in the battlefield, it has killed {} people.\n".format(totalkills)

                response += "You have killed {} people with it.".format(
                    item.item_props.get("kills") if item.item_props.get("kills") != None else 0)

            if item.item_type == ewcfg.it_cosmetic:
                response += "\n\n"

                response += "It's an article of {rarity} rank.\n".format(rarity=item.item_props['rarity'])
                """
                if any(stat in item.item_props.keys() for stat in ewcfg.playerstats_list):
                    response += "Adorning it "
                    stats_breakdown = []
                    for stat in ewcfg.playerstats_list:
                        if abs(int(item.item_props[stat])) > 0:
                            if int(item.item_props[stat]) > 0:
                                stat_response = "increases your "
                            else:
                                stat_response = "decreases your "
                            stat_response += "{stat} by {amount}".format(stat = stat, amount = item.item_props[stat])
                            stats_breakdown.append(stat_response)
                    if len(stats_breakdown) == 0:
                        response += "doesn't affect your stats at all.\n"
                    else:
                        response += ewutils.formatNiceList(names = stats_breakdown, conjunction = "and") + ". \n"
                """
                if item.item_props['durability'] is None:
                    response += "It can't be destroyed.\n"
                else:
                    if item.item_props['id_cosmetic'] == "soul":
                        original_durability = ewcfg.soul_durability
                    elif item.item_props['id_cosmetic'] == 'scalp':
                        if 'original_durability' in item.item_props.keys():
                            original_durability = int(float(item.item_props['original_durability']))
                        else:
                            original_durability = ewcfg.generic_scalp_durability
                    else:
                        if item.item_props.get('rarity') == ewcfg.rarity_princeps:
                            original_durability = ewcfg.base_durability * 100
                            original_item = None  # Princeps do not have existing templates
                        else:
                            try:
                                original_item = cosmetics.cosmetic_map.get(item.item_props['id_cosmetic'])
                                original_durability = original_item.durability
                            except:
                                original_durability = ewcfg.base_durability

                    current_durability = int(item.item_props['durability'])

                    # print('DEBUG -- DURABILITY COMPARISON\nCURRENT DURABILITY: {}, ORIGINAL DURABILITY: {}'.format(current_durability, original_durability))

                    if current_durability == original_durability:
                        response += "It looks brand new.\n"

                    elif original_durability != 0:
                        relative_change = round(current_durability / original_durability * 100)

                        if relative_change > 80:
                            response += "It's got a few minor scratches on it.\n"
                        elif relative_change > 60:
                            response += "It's a little torn from use.\n"
                        elif relative_change > 40:
                            response += "It's not looking so great...\n"
                        elif relative_change > 20:
                            response += "It's going to break soon!\n"

                    else:
                        response += "You have no idea how much longer this'll last. "

                if item.item_props['size'] == 0:
                    response += "It doesn't take up any space at all.\n"
                else:
                    response += "It costs about {amount} space to adorn.\n".format(amount=item.item_props['size'])

                if item.item_props['fashion_style'] == ewcfg.style_cool:
                    response += "It's got a cool feel to it. "
                if item.item_props['fashion_style'] == ewcfg.style_tough:
                    response += "It's lookin' tough as hell, my friend. "
                if item.item_props['fashion_style'] == ewcfg.style_smart:
                    response += "It's got sort of a smart vibe. "
                if item.item_props['fashion_style'] == ewcfg.style_beautiful:
                    response += "It's got a beautiful, refined feel. "
                if item.item_props['fashion_style'] == ewcfg.style_cute:
                    response += "It's super cuuuutttiieeeeeeeeeeeee~ deeeessuusususususususuusususufuswvgslgerphi4hjetbhjhjbetbjtrrpo"

                response += "\n\nIt's freshness rating is {rating}.".format(rating=item.item_props['freshness'])

                hue = hue_static.hue_map.get(item.item_props.get('hue'))
                if hue != None:
                    response += " It's been dyed in {} paint.".format(hue.str_name)

            if item.item_type == ewcfg.it_furniture:
                hue = hue_static.hue_map.get(item.item_props.get('hue'))
                if hue != None:
                    response += " It's been dyed in {} paint.".format(hue.str_name)

            durability = item.item_props.get('durability')
            if durability != None and item.item_type == ewcfg.it_item:
                if item.item_props.get('id_item') in ewcfg.durability_items:
                    if durability == 1:
                        response += " It can only be used one more time."
                    else:
                        response += " It has about {} uses left.".format(durability)

            response = name + (" x{:,}".format(item.stack_size) if (item.stack_size >= 1) else "") + "\n\n" + response

            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(player, response))
        else:
            if iterate == len(item_dest) and response == "":
                if item_search:  # if they didnt forget to specify an item and it just wasn't found
                    response = "You don't have one."
                else:
                    response = "Inspect which item? (check **!inventory**)"

                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# this is basically just the item_look command with some other stuff at the bottom
async def item_use(cmd):
    use_mention_displayname = False

    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    author = cmd.message.author
    server = cmd.guild

    item_sought = bknd_item.find_item(item_search=item_search, id_user=author.id, id_server=server.id)

    if item_sought:
        # Load the user before the item so that the right item props are used
        user_data = EwUser(member=author)

        item = EwItem(id_item=item_sought.get('id_item'))

        response = "The item doesn't have !use functionality"  # if it's not overwritten

        if item.item_type == ewcfg.it_food:
            response = user_data.eat(item)
            user_data.persist()
            asyncio.ensure_future(loop_utils.decrease_food_multiplier(user_data.id_user))

        if item.item_type == ewcfg.it_weapon:
            response = user_data.equip(item)
            user_data.persist()

        if item.item_type == ewcfg.it_item:
            name = item_sought.get('name')
            context = item.item_props.get('context')
            if name == "Trading Cards":
                response = ewsmelting.unwrap(id_user=author, id_server=server, item=item)
            elif (context == 'repel' or context == 'superrepel' or context == 'maxrepel'):
                statuses = user_data.getStatusEffects()
                if ewcfg.status_repelaftereffects_id in statuses:
                    response = "You need to wait a bit longer before applying more body spray."
                else:
                    if context == 'repel':
                        response = user_data.applyStatus(ewcfg.status_repelled_id)
                    elif context == 'superrepel':
                        response = user_data.applyStatus(ewcfg.status_repelled_id, multiplier=2)
                    elif context == 'maxrepel':
                        response = user_data.applyStatus(ewcfg.status_repelled_id, multiplier=4)
                    bknd_item.item_delete(item.id_item)
            elif context == 'pheromones':
                response = user_data.applyStatus(ewcfg.status_pheromones_id)
                bknd_item.item_delete(item.id_item)

            elif context == 'rain':
                # TODO : Rain dance code (this joke is that all this stuff is junk)
                response = "You begin the rain dance, jumping about with the feather as you perform the ancient ritual. The skys darken and grow heavy with the burden of moisture. Finally, in a final flourish to unleash the downpour, you fucking trip and fall flat on your face. Good job, dumbass!"

            elif context == ewcfg.item_id_gellphone:

                if user_data.has_gellphone():
                    gellphones = itm_utils.find_item_all(item_search=ewcfg.item_id_gellphone, id_user=user_data.id_user, id_server=user_data.id_server, item_type_filter=ewcfg.it_item)

                    for phone in gellphones:
                        phone_data = EwItem(id_item=phone.get('id_item'))
                        phone_data.item_props['gellphoneactive'] = 'false'
                        phone_data.persist()

                    response = "You turn off your gellphone."

                else:
                    response = "You turn on your gellphone."
                    item.item_props['gellphoneactive'] = 'true'
                    item.persist()


            elif context == ewcfg.context_prankitem:
                item_action = ""
                side_effect = ""

                if (ewutils.channel_name_is_poi(cmd.message.channel.name) == False):  # or (user_data.poi not in poi_static.capturable_districts):
                    response = "You need to be on the city streets to unleash that prank item's full potential."
                else:
                    if item.item_props['prank_type'] == ewcfg.prank_type_instantuse:
                        item_action, response, use_mention_displayname, side_effect = await ewprank.prank_item_effect_instantuse(cmd, item)
                        if side_effect != "":
                            response += await itm_utils.perform_prank_item_side_effect(side_effect, cmd=cmd)

                    elif item.item_props['prank_type'] == ewcfg.prank_type_response:
                        item_action, response, use_mention_displayname, side_effect = await ewprank.prank_item_effect_response(cmd, item)
                        if side_effect != "":
                            response += await itm_utils.perform_prank_item_side_effect(side_effect, cmd=cmd)

                    elif item.item_props['prank_type'] == ewcfg.prank_type_trap:
                        item_action, response, use_mention_displayname, side_effect = await ewprank.prank_item_effect_trap(cmd, item)

                    if item_action == "delete":
                        bknd_item.item_delete(item.id_item)
                        # prank_feed_channel = fe_utils.get_channel(cmd.guild, ewcfg.channel_prankfeed)
                        # await fe_utils.send_message(cmd.client, prank_feed_channel, fe_utils.formatMessage((cmd.message.author if use_mention_displayname == False else cmd.mentions[0]), (response+"\n`-------------------------`")))

                    elif item_action == "drop":
                        bknd_item.give_item(id_user=(user_data.poi + '_trap'), id_server=item.id_server, id_item=item.id_item)
                        # print(item.item_props)
            # elif context == "swordofseething":
            #
            # 	bknd_item.item_delete(item.id_item)
            # 	await ewdebug.begin_cataclysm(user_data)
            #
            # 	response = ewdebug.last_words

            elif context == "prankcapsule":
                response = ewsmelting.popcapsule(id_user=author, id_server=server, item=item)

            elif context == ewcfg.item_id_modelovaccine:

                if user_data.life_state == ewcfg.life_state_shambler:
                    user_data.life_state = ewcfg.life_state_juvenile
                    response = "You shoot the vaccine with the eagerness of a Juvenile on Slimernalia's Eve. It immediately dissolves throughout your bloodstream, causing your organs to feel like they're melting as your body undegrades." \
                               "Then, suddenly, you feel slime start to flow through you properly again. You feel rejuvenated, literally! Your genitals kinda itch, though.\n\n" \
                               "You have been cured! You are no longer a Shambler. Jesus Christ, finally."
                else:
                    user_data.clear_status(id_status=ewcfg.status_modelovaccine_id)
                    response = user_data.applyStatus(ewcfg.status_modelovaccine_id)

                user_data.degradation = 0
                user_data.persist()

                bknd_item.item_delete(item.id_item)

            elif context == "revive":
                # TODO Slimeoid revive code
                # Expect another argument after the context, being the name of the slimeoid to be revived
                response = "You try to \"revive\" your fallen Slimeoid. Too bad this ain't a video game, or it might have worked!"

            elif ewcfg.item_id_key in context and context != 'housekey':
                if user_data.poi == "room102" and context == 'reelkey':
                    response = ewdebug.reel_code
                if user_data.poi == "room103" and context == 'cabinetkey':
                    response = ewdebug.debug_code

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage((cmd.message.author if use_mention_displayname == False else cmd.mentions[0]), response))
        await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

    else:
        if item_search:  # if they didnt forget to specify an item and it just wasn't found
            response = "You don't have one."
        else:
            response = "Use which item? (check **!inventory**)"

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def manually_edit_item_properties(cmd):
    if not cmd.message.author.guild_permissions.administrator:
        return

    if cmd.tokens_count == 4:
        item_id = cmd.tokens[1]
        column_name = cmd.tokens[2]
        column_value = cmd.tokens[3]

        bknd_core.execute_sql_query("REPLACE INTO items_prop({}, {}, {}) VALUES(%s, %s, %s)".format(
            ewcfg.col_id_item,
            ewcfg.col_name,
            ewcfg.col_value
        ), (
            item_id,
            column_name,
            column_value
        ))

        response = "Edited item with ID {}. It's {} value has been set to {}.".format(item_id, column_name, column_value)

    else:
        response = 'Invalid number of options entered.\nProper usage is: !editprop [item ID] [name] [value], where [value] is in quotation marks if it is longer than one word.'

    await fe_utils.send_message(cmd.client, cmd.message.channel, response)


"""
    Command that lets players !give others items
"""


async def give(cmd):
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    author = cmd.message.author
    server = cmd.guild

    if cmd.mentions:  # if they're not empty
        recipient = cmd.mentions[0]
    else:
        response = "You have to specify the recipient of the item."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    user_data = EwUser(member=author)
    recipient_data = EwUser(member=recipient)

    if user_data.poi != recipient_data.poi:
        response = "You must be in the same location as the person you want to gift your item to, bitch."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    item_sought = bknd_item.find_item(item_search=item_search, id_user=author.id, id_server=server.id)

    if item_sought:  # if an item was found

        """
        # Slimernalia gifting
        if item_sought.get('item_type') == ewcfg.it_item:
            item_data = EwItem(id_item = item_sought.get('id_item'))

            if item_data.item_props.get('id_item') == 'gift' and item_data.item_props.get("gifted") == "false":
                item_data.item_props['gifted'] = "true"
                item_data.persist()
                user_data.festivity += ewcfg.festivity_on_gift_giving
                user_data.persist()
        """
        # don't let people give others food when they shouldn't be able to carry more food items
        if item_sought.get('item_type') == ewcfg.it_food:
            food_items = bknd_item.inventory(
                id_user=recipient.id,
                id_server=server.id,
                item_type_filter=ewcfg.it_food
            )

            if len(food_items) >= recipient_data.get_food_capacity():
                response = "They can't carry any more food items."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif item_sought.get('item_type') == ewcfg.it_weapon:
            weapons_held = bknd_item.inventory(
                id_user=recipient.id,
                id_server=server.id,
                item_type_filter=ewcfg.it_weapon
            )

            if user_data.weaponmarried and user_data.weapon == item_sought.get('id_item'):
                response = "Your cuckoldry is appreciated, but your {} will always remain faithful to you.".format(item_sought.get('name'))
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            elif recipient_data.life_state == ewcfg.life_state_corpse:
                response = "Ghosts can't hold weapons."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            elif len(weapons_held) >= recipient_data.get_weapon_capacity():
                response = "They can't carry any more weapons."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            # inventory limits for items that aren't food or weapons
            other_items = bknd_item.inventory(
                id_user=recipient.id,
                id_server=server.id,
                item_type_filter=item_sought.get('item_type')
            )

            if len(other_items) >= ewcfg.generic_inv_limit:
                response = "They can't carry any more of those."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        if item_sought.get('item_type') == ewcfg.it_cosmetic:
            item_data = EwItem(id_item=item_sought.get('id_item'))
            item_data.item_props["adorned"] = 'false'
            item_data.persist()

        if item_sought.get('soulbound') and EwItem(id_item=item_sought.get('id_item')).item_props.get("context") != "housekey":
            response = "You can't just give away soulbound items."
        else:
            bknd_item.give_item(
                member=recipient,
                id_item=item_sought.get('id_item')
            )

            response = "You gave {recipient} a {item}".format(
                recipient=recipient.display_name,
                item=item_sought.get('name')
            )

            if item_sought.get('id_item') == user_data.weapon:
                user_data.weapon = -1
                user_data.persist()
            elif item_sought.get('id_item') == user_data.sidearm:
                user_data.sidearm = -1
                user_data.persist()

            await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        if item_search:  # if they didnt forget to specify an item and it just wasn't found
            response = "You don't have one."
        else:
            response = "Give which item? (check **!inventory**)"

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
    Throw away an item
"""


async def discard(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""

    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)

    if item_sought:
        item = EwItem(id_item=item_sought.get("id_item"))

        if not item.soulbound:
            if item.item_type == ewcfg.it_weapon and user_data.weapon >= 0 and item.id_item == user_data.weapon:
                if user_data.weaponmarried and item.item_props.get('married') == user_data.id_user:
                    weapon = static_weapons.weapon_map.get(item.item_props.get("weapon_type"))
                    response = "As much as it would be satisfying to just chuck your {} down an alley and be done with it, here in civilization we deal with things *maturely.* You’ll have to speak to the guy that got you into this mess in the first place, or at least the guy that allowed you to make the retarded decision in the first place. Luckily for you, they’re the same person, and he’s at the Dojo.".format(
                        weapon.str_weapon)
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                else:
                    user_data.weapon = -1
                    user_data.persist()


            elif item.item_type == ewcfg.it_weapon and user_data.sidearm >= 0 and item.id_item == user_data.sidearm:
                if user_data.weaponmarried and item.item_props.get('married') == user_data.id_user:
                    weapon = static_weapons.weapon_map.get(item.item_props.get("weapon_type"))
                    response = "As much as it would be satisfying to just chuck your {} down an alley and be done with it, here in civilization we deal with things *maturely.* You’ll have to speak to the guy that got you into this mess in the first place, or at least the guy that allowed you to make the retarded decision in the first place. Luckily for you, they’re the same person, and he’s at the Dojo.".format(
                        weapon.str_weapon)
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                else:
                    user_data.sidearm = -1
                    user_data.persist()

            # elif item.item_type == ewcfg.it_cosmetic:
            # 	# Prevent the item from being dropped if it is adorned
            # 	if item_sought.get("adorned") == 'true':
            # 		response = "You need to !dedorn your {} first, before you can throw it away.".format(item_sought.get("name"))
            # 		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            response = "You throw away your " + item_sought.get("name")
            item_drop(id_item=item.id_item)

            await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

        else:
            response = "You can't throw away soulbound items."
    else:
        if item_search:
            response = "You don't have one"
        else:
            response = "Discard which item? (check **!inventory**)"

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
    Deletes a food item instead of dropping
"""


async def trash(cmd):
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    author = cmd.message.author
    server = cmd.guild

    item_sought = bknd_item.find_item(item_search=item_search, id_user=author.id, id_server=server.id)

    if item_sought:
        # Load the user before the item so that the right item props are used
        user_data = EwUser(member=author)

        item = EwItem(id_item=item_sought.get('id_item'))

        response = "You can't !trash an item that isn't food. Try **!drop**ing it instead."  # if it's not overwritten

        if item.item_type == ewcfg.it_food:
            response = "You throw away your {} into a nearby trash can.".format(item.item_props.get("food_name"))
            bknd_item.item_delete(item.id_item)
    else:
        response = "Are you sure you have that item?"

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def zuck(cmd):
    user_data = EwUser(member=cmd.message.author)

    tokens = ewutils.flattenTokenListToString(cmd.tokens[1:])

    syr_item = bknd_item.find_item(item_search="zuckerberg", id_user=cmd.message.author.id, id_server=cmd.guild.id)

    if syr_item:
        response = "The syringe is all rusted out. It's a shame you zucked the only person capable of maintainting it."
    else:
        response = "You'll need a corpse and the zuck syringe before you can do that."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def longdrop(cmd):
    user_data = EwUser(member=cmd.message.author)
    mutations = user_data.get_mutations()
    poi = poi_static.id_to_poi.get(user_data.poi)

    destination = ewutils.flattenTokenListToString(cmd.tokens[1])
    dest_poi = poi_static.id_to_poi.get(destination)

    item_search = ewutils.flattenTokenListToString(cmd.tokens[2:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=user_data.id_server)

    if ewcfg.mutation_id_longarms not in mutations:
        response = "As if anything on you was long enough to do that."
    elif cmd.tokens_count == 1:
        response = "You'll need for information that that. Try !longdrop <location> <item>."
    elif not item_sought:
        response = "You don't have that item."
    elif dest_poi == None:
        response = "Never heard of it."
    elif poi_utils.inaccessible(user_data=user_data, poi=dest_poi) or dest_poi.is_street:
        response = "Your arm hits a wall before it can make the drop off. Shit, probably can't take it over there."
    elif user_data.poi not in dest_poi.neighbors.keys() and dest_poi.id_poi not in poi.mother_districts:
        response = "You can't take it that far. What if a bird or car runs into your hand?"
    else:
        item_obj = EwItem(item_sought.get('id_item'))
        if item_obj.soulbound == True and item_obj.item_props.get('context') != 'housekey':
            response = "You still can't drop a soulbound item. Having really long arms doesn't grant you that ability."
        elif item_obj.item_type == ewcfg.it_weapon and user_data.weapon >= 0 and item_obj.id_item == user_data.weapon:
            if user_data.weaponmarried:
                weapon = static_weapons.weapon_map.get(item_obj.item_props.get("weapon_type"))
                response = "As much as it would be satisfying to just chuck your {} down an alley and be done with it, here in civilization we deal with things *maturely.* You’ll have to speak to the guy that got you into this mess in the first place, or at least the guy that allowed you to make the retarded decision in the first place. Luckily for you, they’re the same person, and he’s at the Dojo.".format(
                    weapon.str_weapon)
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            else:
                user_data.weapon = -1
                user_data.persist()

        item_drop(id_item=item_sought.get('id_item'), other_poi=dest_poi.id_poi)
        response = "You stretch your arms and drop your " + item_sought.get("name") + ' into {}.'.format(dest_poi.str_name)
        await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def skullbash(cmd):
    user_data = EwUser(member=cmd.message.author)
    item_stash = bknd_item.inventory(id_user=cmd.message.author.id, id_server=user_data.id_server)
    item_sought = None
    for item_piece in item_stash:
        item = EwItem(id_item=item_piece.get('id_item'))
        if item_piece.get('item_type') == ewcfg.it_furniture and item.item_props.get('id_furniture') == "brick":
            item_sought = item_piece

    if item_sought:
        if user_data.life_state == ewcfg.life_state_corpse:
            response = "Your head is too incorporeal to do that."
        elif user_data.life_state == ewcfg.life_state_shambler:
            response = "Your head is too soft and malleable to do that."
        else:
            ewutils.active_restrictions[user_data.id_user] = 2
            response = "You suck in your gut and mentally prepare to lose a few brain cells. 3...2...1...WHACK! Ugh. You're gonna need a minute."
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            await asyncio.sleep(600)
            ewutils.active_restrictions[user_data.id_user] = 0
            response = "The stars slowly begin to fade from your vision. Looks like you're lucid again."
    else:
        response = "You don't have a hard enough brick to bash your head in."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def makecostume(cmd):
    costumekit = bknd_item.find_item(item_search="costumekit", id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)

    user_data = EwUser(member=cmd.message.author)

    id_user = user_data.id_user
    id_server = user_data.id_server

    if not costumekit:
        response = "You don't know how to make one, bitch."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if len(cmd.tokens) != 3:
        response = 'Usage: !makecostume "[name]" "[description]".\nExample: !makecostume "Ghost Costume" "A bedsheet with holes for eyes."'
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    bknd_item.item_delete(id_item=costumekit.get('id_item'))

    item_name = cmd.tokens[1]
    item_desc = cmd.tokens[2]

    item_props = {
        "cosmetic_name": item_name,
        "cosmetic_desc": item_desc,
        "adorned": "false",
        "rarity": "Plebeian",
        "context": "costume",
    }

    new_item_id = bknd_item.item_create(
        id_server=id_server,
        id_user=id_user,
        item_type=ewcfg.it_cosmetic,
        item_props=item_props
    )

    response = "You fashion your **{}** Double Halloween costume using the creation kit.".format(item_name)
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
