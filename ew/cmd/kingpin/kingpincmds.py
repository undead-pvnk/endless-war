import re

from ew.backend import item as bknd_item
from ew.static import cfg as ewcfg
from ew.static import cosmetics
from ew.static import poi as poi_static
from ew.utils import cmd as cmd_utils
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as itm_utils
from ew.utils import move as move_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser


async def pa_command(cmd):
    user_data = EwUser(member=cmd.message.author)
    if not cmd.message.author.guild_permissions.administrator and user_data.life_state != ewcfg.life_state_executive:
        return await cmd_utils.fake_failed_command(cmd)
    else:
        if cmd.tokens_count >= 3:
            poi = ewutils.flattenTokenListToString(cmd.tokens[1])

            poi_obj = poi_static.id_to_poi.get(poi)
            if poi == "auditorium":
                channel = "auditorium"
            else:
                channel = poi_obj.channel

            loc_channel = fe_utils.get_channel(cmd.guild, channel)

            if poi is not None:
                patext = re.sub("<.+>", "", cmd.message.content[(len(cmd.tokens[0]) + len(cmd.tokens[1]) + 1):]).strip()
                if len(patext) > 500:
                    patext = patext[:-500]
                return await fe_utils.send_message(cmd.client, loc_channel, patext)


""" Destroy a megaslime of your own for lore reasons. """


async def deadmega(cmd):
    response = ""
    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state != ewcfg.life_state_kingpin:
        response = "Only the Rowdy Fucker {} and the Cop Killer {} can do that.".format(ewcfg.emote_rowdyfucker, ewcfg.emote_copkiller)
    else:
        value = 1000000
        user_slimes = 0

        if value > user_data.slimes:
            response = "You don't have that much slime to lose ({:,}/{:,}).".format(user_data.slimes, value)
        else:
            user_data.change_slimes(n=-value)
            user_data.persist()
            response = "Alas, poor megaslime. You have {:,} slime remaining.".format(user_data.slimes)

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
	Release the specified player from their commitment to their faction.
	Returns enlisted players to juvenile.
"""


async def pardon(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state != ewcfg.life_state_kingpin and user_data.life_state != ewcfg.life_state_executive and not cmd.message.author.guild_permissions.administrator:
        response = "Only the Rowdy Fucker {} and the Cop Killer {} can do that.".format(ewcfg.emote_rowdyfucker, ewcfg.emote_copkiller, ewcfg.emote_slimecorp)
    else:
        member = None
        if cmd.mentions_count == 1:
            member = cmd.mentions[0]
            if member.id == cmd.message.author.id:
                member = None

        if member == None:
            response = "Who?"
        else:
            member_data = EwUser(member=member)
            member_data.unban(faction=user_data.faction)

            if member_data.faction == "":
                response = "{} has been allowed to join the {} again.".format(member.display_name, user_data.faction)
            else:
                faction_old = member_data.faction
                member_data.faction = ""

                if member_data.life_state == ewcfg.life_state_enlisted:
                    member_data.life_state = ewcfg.life_state_juvenile
                    member_data.weapon = -1

                response = "{} has been released from their association with the {}.".format(member.display_name, faction_old)

            member_poi = poi_static.id_to_poi.get(member_data.poi)
            if move_utils.inaccessible(user_data=member_data, poi=member_poi):
                member_data.poi = ewcfg.poi_id_downtown
            member_data.persist()
            await ewrolemgr.updateRoles(client=cmd.client, member=member)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def defect(cmd):
    accepted = False

    member = cmd.message.author

    modauth = 0

    response = "You feel...traitor-ish today. Hey mods, any takers? Let them free, !yes or !no?"
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    try:
        message = await cmd.client.wait_for('message', timeout=30, check=lambda message: 0 < ewrolemgr.checkClearance(member=message.author) <= 4 and
                                                                                         message.content.lower() in [ewcfg.cmd_yes, ewcfg.cmd_no])

        if message != None:
            if message.content.lower() == ewcfg.cmd_yes:
                accepted = True
                modauth = message.author
            if message.content.lower() == ewcfg.cmd_no:
                accepted = False

    except Exception as e:
        print(e)
        accepted = False

    if not accepted:
        response = "Well if it isn't the boy who cried backstab. Guess you won't be going anywhere."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


    else:
        member_data = EwUser(member=cmd.message.author)
        mod_data = EwUser(member=modauth)
        member_data.unban(faction=mod_data.faction)


        if member_data.faction == "":
            response = "{} has been allowed to join the {} again.".format(member.display_name, mod_data.faction)
        else:
            faction_old = member_data.faction
            member_data.faction = ""

            if member_data.life_state == ewcfg.life_state_enlisted:
                member_data.life_state = ewcfg.life_state_juvenile
                member_data.weapon = -1

            response = "{} has been released from their association with the {}.".format(member.display_name, faction_old)

        member_poi = poi_static.id_to_poi.get(member_data.poi)
        if move_utils.inaccessible(user_data=member_data, poi=member_poi):
            member_data.poi = ewcfg.poi_id_downtown
        member_data.persist()
        await ewrolemgr.updateRoles(client=cmd.client, member=member)

        leak_channel = fe_utils.get_channel(server=cmd.guild, channel_name='squickyleaks')
        await fe_utils.send_message(cmd.client, leak_channel,  "{}: Let {} defect.".format(modauth.display_name, member.display_name))


    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def banish(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state != ewcfg.life_state_kingpin and user_data.life_state != ewcfg.life_state_executive and not cmd.message.author.guild_permissions.administrator:
        response = "Only the Rowdy Fucker {} and the Cop Killer {} can do that.".format(ewcfg.emote_rowdyfucker, ewcfg.emote_copkiller)
    else:
        member = None
        if cmd.mentions_count == 1:
            member = cmd.mentions[0]

        # >:]

        # if member.id == cmd.message.author.id:
        # 	member = None

        if member == None:
            response = "Who?"
        else:
            member_data = EwUser(member=member)
            member_data.ban(faction=user_data.faction)
            member_data.unvouch(faction=user_data.faction)

            if member_data.faction == user_data.faction:
                member_data.faction = ""
                if member_data.life_state == ewcfg.life_state_enlisted:
                    member_data.life_state = ewcfg.life_state_juvenile

            member_poi = poi_static.id_to_poi.get(member_data.poi)
            if move_utils.inaccessible(user_data=member_data, poi=member_poi):
                member_data.poi = ewcfg.poi_id_downtown
            member_data.persist()
            response = "{} has been banned from enlisting in the {}".format(member.display_name, user_data.faction)
            await ewrolemgr.updateRoles(client=cmd.client, member=member)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
	Command that creates a princeps cosmetic item
"""


async def create(cmd):
    # if not cmd.message.author.guild_permissions.administrator:
    if EwUser(member=cmd.message.author).life_state != ewcfg.life_state_kingpin and not cmd.message.author.guild_permissions.administrator:
        response = 'Lowly Non-Kingpins cannot hope to create items with their bare hands.'
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if len(cmd.tokens) not in [4, 5, 6]:
        response = 'Usage: !create "<item_name>" "<item_desc>" <recipient> <rarity(optional)>, <context>(optional)'
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    item_name = cmd.tokens[1]
    item_desc = cmd.tokens[2]
    rarity = cmd.tokens[4] if len(cmd.tokens) >= 5 and ewutils.flattenTokenListToString(cmd.tokens[4]) in ['princeps', 'plebeian', 'patrician'] else 'princeps'
    context = cmd.tokens[5] if len(cmd.tokens) >= 6 else ''

    if cmd.mentions[0]:
        recipient = cmd.mentions[0]
    else:
        response = 'You need to specify a recipient. Usage: !create "<item_name>" "<item_desc>" <recipient>'
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    item_props = {
        "cosmetic_name": item_name,
        "cosmetic_desc": item_desc,
        "adorned": "false",
        "rarity": rarity,
        "context": context
    }

    new_item_id = bknd_item.item_create(
        id_server=cmd.guild.id,
        id_user=recipient.id,
        item_type=ewcfg.it_cosmetic,
        item_props=item_props
    )

    itm_utils.soulbind(new_item_id)

    response = 'Item "{}" successfully created.'.format(item_name)
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
	Command that grants someone a specific cosmetic for an event.
"""


async def exalt(cmd):
    author = cmd.message.author
    user_data = EwUser(member=author)

    if not author.guild_permissions.administrator and user_data.life_state != ewcfg.life_state_kingpin:
        response = "You do not have the power within you worthy of !exalting another player."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count > 0:
        recipient = cmd.mentions[0]
    else:
        response = 'You need to specify a recipient. Usage: !exalt @[recipient].'
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    recipient_data = EwUser(member=recipient)

    # 	DOUBLE HALLOWEEN
    #
    # 	# Gather the Medallion
    medallion_results = []
    for m in cosmetics.cosmetic_items_list:
        if m.ingredients == 'HorsemanSoul':
            medallion_results.append(m)
        else:
            pass

    medallion = medallion_results[0]
    medallion_props = itm_utils.gen_item_props(medallion)

    medallion_id = bknd_item.item_create(
        item_type=medallion.item_type,
        id_user=recipient.id,
        id_server=cmd.guild.id,
        item_props=medallion_props
    )

    # Soulbind the medallion. A player can get at most twice, but later on a new command could be added to destroy them/trade them in.
    # I imagine this would be something similar to how players can destroy Australium Wrenches in TF2, which broadcasts a message to everyone in the game, or something.
    itm_utils.soulbind(medallion_id)

    response = "**{} has been gifted the Double Halloween Medallion!!**\n".format(recipient.display_name)
    #
    # 	SWILLDERMUK
    #
    # 	if recipient_data.gambit > 0:
    # 		# Give the user the Janus Mask
    #
    # 		mask_results = []
    # 		for m in cosmetics.cosmetic_items_list:
    # 			if m.ingredients == 'SwilldermukFinalGambit':
    # 				mask_results.append(m)
    # 			else:
    # 				pass
    #
    # 		mask = mask_results[0]
    # 		mask_props = itm_utils.gen_item_props(mask)
    #
    # 		mask_id = bknd_item.item_create(
    # 			item_type=mask.item_type,
    # 			id_user=recipient.id,
    # 			id_server=cmd.guild.id,
    # 			item_props=mask_props
    # 		)
    #
    # 		ewitem.soulbind(mask_id)
    #
    # 		response = "In light of their supreme reign over Swilldermuk, and in honor of their pranking prowess, {} recieves the Janus Mask!".format(recipient.display_name)
    #
    # 	else:
    # 		# Give the user the Sword of Seething
    # 		sword_results = []
    # 		for s in items.item_list:
    # 			if s.context == 'swordofseething':
    # 				sword_results.append(s)
    # 			else:
    # 				pass
    #
    # 		sword = sword_results[0]
    # 		sword_props = itm_utils.gen_item_props(sword)
    #
    # 		sword_id = bknd_item.item_create(
    # 			item_type=sword.item_type,
    # 			id_user=recipient.id,
    # 			id_server=cmd.guild.id,
    # 			item_props=sword_props
    # 		)
    #
    # 		ewitem.soulbind(sword_id)
    #
    # 		response = "In response to their unparalleled ability to let everything go to shit and be the laughingstock of all of NLACakaNM, {} recieves the SWORD OF SEETHING! God help us all...".format(recipient.display_name)
    #
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def hogtie(cmd):

    if not 0 < ewrolemgr.checkClearance(member=cmd.message.author) < 4:
        return await cmd_utils.fake_failed_command(cmd)
    else:
        if cmd.mentions_count == 1:
            target_data = EwUser(member=cmd.mentions[0])
            member = cmd.mentions[0]
            if target_data.hogtied == 1:
                target_data.hogtied = 0
                target_data.persist()
                response = "Whew-whee! She's buckin' so we gotta let 'er go."
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                leak_channel = fe_utils.get_channel(server=cmd.guild, channel_name='squickyleaks')
                await fe_utils.send_message(cmd.client, leak_channel, "{}:Released {} from eternal bondage.".format(cmd.message.author.display_name, member.display_name))
            else:
                target_data.hogtied = 1
                target_data.persist()
                response = "Boy howdy! Looks like we lasso'd up a real heifer there! A dang ol' big'un."
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                leak_channel = fe_utils.get_channel(server=cmd.guild, channel_name='squickyleaks')
                await fe_utils.send_message(cmd.client, leak_channel, "{}: Hogtied {}.".format(cmd.message.author.display_name, member.display_name))
