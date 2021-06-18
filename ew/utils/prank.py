import random
import time

from . import core as ewutils
from . import frontend as fe_utils
from . import item as itm_utils
from ..backend import core as bknd_core
from ..backend import item as bknd_item
from ..backend.item import EwItem
from ..backend.user import EwUserBase as EwUser
from ..static import cfg as ewcfg
from ..static import poi as poi_static


response_timer = 6  # How long does it take for a response item to send out its attacks
afk_timer = 60 * 60 * 2  # 2 hours


async def activate_trap_items(district, id_server, id_user):
    # Return if --> User has 0 credence, there are no traps, or if the trap setter is the one who entered the district.
    # print("TRAP FUNCTION")
    trap_was_dud = False

    user_data = EwUser(id_user=id_user, id_server=id_server)
    # if user_data.credence == 0:
    # 	#print('no credence')
    # 	return

    if user_data.life_state == ewcfg.life_state_corpse:
        # print('get out ghosts reeeee!')
        return

    try:
        conn_info = bknd_core.databaseConnect()
        conn = conn_info.get('conn')
        cursor = conn.cursor()

        district_channel_name = poi_static.id_to_poi.get(district).channel

        client = ewutils.get_client()

        server = client.get_guild(id_server)

        member = server.get_member(id_user)

        district_channel = fe_utils.get_channel(server=server, channel_name=district_channel_name)

        searched_id = district + '_trap'

        cursor.execute("SELECT id_item, id_user FROM items WHERE id_user = %s AND id_server = %s".format(
            id_item=ewcfg.col_id_item,
            id_user=ewcfg.col_id_user
        ), (
            searched_id,
            id_server,
        ))

        traps = cursor.fetchall()

        if len(traps) == 0:
            # print('no traps')
            return

        trap_used = traps[0]

        trap_id_item = trap_used[0]
        # trap_id_user = trap_used[1]

        trap_item_data = EwItem(id_item=trap_id_item)

        trap_chance = int(trap_item_data.item_props.get('trap_chance'))
        trap_user_id = trap_item_data.item_props.get('trap_user_id')

        if int(trap_user_id) == user_data.id_user:
            # print('trap same user id')
            return

        if random.randrange(101) < trap_chance:
            # Trap was triggered!
            pranker_data = EwUser(id_user=int(trap_user_id), id_server=id_server)
            pranked_data = user_data

            response = trap_item_data.item_props.get('prank_desc')

            side_effect = trap_item_data.item_props.get('side_effect')

            if side_effect != None:
                response += await itm_utils.perform_prank_item_side_effect(side_effect, member=member)

        # calculate_gambit_exchange(pranker_data, pranked_data, trap_item_data, trap_used=True)
        else:
            # Trap was a dud.
            trap_was_dud = True
            response = "Close call! You were just about to eat shit and fall right into someone's {}, but luckily, it was a dud.".format(
                trap_item_data.item_props.get('item_name'))

        bknd_item.item_delete(trap_id_item)

    finally:
        # Clean up the database handles.
        cursor.close()
        bknd_core.databaseClose(conn_info)
    await fe_utils.send_message(client, district_channel, fe_utils.formatMessage(member, response))


# if not trap_was_dud:
# 	client = ewutils.get_client()
# 	server = client.get_server(id_server)
#
# 	prank_feed_channel = get_channel(server, 'prank-feed')
#
# 	response += "\n`-------------------------`"
# 	await send_message(client, prank_feed_channel, formatMessage(member, response))


# Use an instant use item
async def prank_item_effect_instantuse(cmd, item):
    item_action = ""
    mentions_user = False
    use_mention_displayname = False
    side_effect = ""

    if cmd.mentions_count == 1:
        mentions_user = True

    if mentions_user:
        member = cmd.mentions[0]

        pranker_data = EwUser(member=cmd.message.author)
        pranked_data = EwUser(member=member)

        if pranker_data.id_user == pranked_data.id_user:
            response = "A bit masochistic, don't you think?"
            return item_action, response, use_mention_displayname, side_effect

        if pranked_data.time_last_action < (int(time.time()) - afk_timer):
            response = "Whoa whoa WHOA! Slow down there, big guy, this person's practically asleep! Where's the fun in pranking them right now, when you won't even be able to get a reaction out of them?\n**(Hint: {} is AFK! Try pranking someone else.)**".format(member.display_name)
            return item_action, response, use_mention_displayname, side_effect

        if pranker_data.poi != pranked_data.poi:
            response = "You need to be in the same place as your target to prank them with that item."
            return item_action, response, use_mention_displayname, side_effect

        # if pranker_data.credence == 0 or pranked_data.credence == 0:
        # 	if pranker_data.credence == 0:
        #
        # 		response = "You can't prank that person right now, you don't have any credence!"
        # 	else:
        # 		response = "You can't prank that person right now, they don't have any credence!"
        #
        # 	return item_action, response, use_mention_displayname, side_effect

        if (ewutils.active_restrictions.get(pranker_data.id_user) != None and ewutils.active_restrictions.get(pranker_data.id_user) == 2) or (ewutils.active_restrictions.get(pranked_data.id_user) != None and ewutils.active_restrictions.get(pranked_data.id_user) == 2):
            response = "You can't prank that person right now."
            return item_action, response, use_mention_displayname, side_effect

        prank_item_data = item

        # calculate_gambit_exchange(pranker_data, pranked_data, prank_item_data)

        response = prank_item_data.item_props.get('prank_desc')

        side_effect = prank_item_data.item_props.get('side_effect')

        response = response.format(cmd.message.author.display_name)
        item_action = "delete"
        use_mention_displayname = True
    else:
        response = "You gotta find someone to prank someone with that item, first!\n**(Hint: !use item @player)**"

    return item_action, response, use_mention_displayname, side_effect


# Use a response item
async def prank_item_effect_response(cmd, item):
    item_action = ""
    mentions_user = False
    use_mention_displayname = False
    side_effect = ""

    if cmd.mentions_count == 1:
        mentions_user = True

    if mentions_user:
        member = cmd.mentions[0]

        pranker_data = EwUser(member=cmd.message.author)
        pranked_data = EwUser(member=member)

        if pranker_data.id_user == pranked_data.id_user:
            response = "A bit masochistic, don't you think?"
            return item_action, response, use_mention_displayname, side_effect

        if pranked_data.time_last_action < (int(time.time()) - afk_timer):
            response = "Whoa whoa WHOA! Slow down there, big guy, this person's practically asleep! Where's the fun in pranking them right now, when you won't even be able to get a reaction out of them?\n**(Hint: {} is AFK! Try pranking someone else.)**".format(member.display_name)
            return item_action, response, use_mention_displayname, side_effect

        if pranker_data.poi != pranked_data.poi:
            response = "You need to be in the same place as your target to prank them with that item."
            return item_action, response, use_mention_displayname, side_effect

        # if pranker_data.credence == 0 or pranked_data.credence == 0:
        # 	if pranker_data.credence == 0:
        #
        # 		response = "You can't prank that person right now, you don't have any credence!"
        # 	else:
        # 		response = "You can't prank that person right now, they don't have any credence!"
        #
        # 	return item_action, response, use_mention_displayname, side_effect

        if (ewutils.active_restrictions.get(pranker_data.id_user) != None and ewutils.active_restrictions.get(pranker_data.id_user) == 2) or (ewutils.active_restrictions.get(pranked_data.id_user) != None and ewutils.active_restrictions.get(pranked_data.id_user) == 2):
            response = "You can't prank that person right now."
            return item_action, response, use_mention_displayname, side_effect

        prank_item_data = item

        response = prank_item_data.item_props.get('prank_desc')
        extra_response_1 = prank_item_data.item_props.get('response_desc_1')
        extra_response_2 = prank_item_data.item_props.get('response_desc_2')
        extra_response_3 = prank_item_data.item_props.get('response_desc_3')
        extra_response_4 = prank_item_data.item_props.get('response_desc_4')

        possible_responses_list = [
            response,
            extra_response_1,
            extra_response_2,
            extra_response_3,
            extra_response_4,
        ]

        # response = response.format(cmd.message.author.display_name)

        # Apply restrictions, stop both users in their tracks
        # Restriction level 2 -- No one else can prank you at this time.
        ewutils.active_target_map[pranker_data.id_user] = pranked_data.id_user
        ewutils.active_target_map[pranked_data.id_user] = pranker_data.id_user
        ewutils.moves_active[pranker_data.id_user] = 0
        # ewutils.moves_active[pranked_data.id_user] = 0
        ewutils.active_restrictions[pranker_data.id_user] = 2
        ewutils.active_restrictions[pranked_data.id_user] = 2

        # The command needed to remove the response item
        response_command = prank_item_data.item_props.get('response_command')

        use_mention_displayname = True

        # The pranked person has 5 chances to type in the proper command before more and more gambit builds up
        limit = 0
        accepted = 0
        has_escaped = False
        has_escaped_fast = False
        while limit < 6:

            limit += 1

            if limit != 6:
                chosen_response = possible_responses_list[limit - 1]

                # Some response item messages wont have formatting in them.
                try:
                    chosen_response = chosen_response.format(cmd.message.author.display_name)
                except:
                    pass

                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage((cmd.message.author if use_mention_displayname == False else cmd.mentions[0]), chosen_response))
                # prank_feed_channel = fe_utils.get_channel(cmd.guild, 'prank-feed')
                # await fe_utils.send_message(cmd.client, prank_feed_channel, fe_utils.formatMessage((cmd.message.author if use_mention_displayname == False else cmd.mentions[0]), (chosen_response+"\n`-------------------------`")))

                # The longer time goes on without the pranked person typing in the command, the more gambit they lose
                pranker_data = EwUser(member=cmd.message.author)
                pranked_data = EwUser(member=member)

                # calculate_gambit_exchange(pranker_data, pranked_data, prank_item_data, limit)

                accepted = 0
                try:
                    msg = await cmd.client.wait_for('message', timeout=response_timer, check=lambda message: message.author == member)

                    if msg != None:
                        if msg.content.lower() == "!" + response_command:
                            accepted = 1

                            if limit != 5:
                                has_escaped = True
                            # if limit == 1:
                            # 	has_escaped_fast = True

                            limit = 6
                except:
                    accepted = 0

        if accepted == 1 and has_escaped:
            response = "You manage to resist {}'s prank efforts for now.".format(cmd.message.author.display_name)
        # if has_escaped_fast:
        # 	response = "You swiftly dodge {}'s prank attempt!".format(cmd.message.author.display_name)
        # 	limit = 7
        else:
            response = "It's over. The damage {} has done to you will stay with you until your death. Or at least for the rest of the week, whichever comes first.".format(cmd.message.author.display_name)

        pranker_data = EwUser(member=cmd.message.author)
        pranked_data = EwUser(member=member)

        # calculate_gambit_exchange(pranker_data, pranked_data, prank_item_data, limit)

        # Remove restrictions
        ewutils.active_target_map[pranker_data.id_user] = ""
        ewutils.active_target_map[pranked_data.id_user] = ""
        ewutils.active_restrictions[pranker_data.id_user] = 0
        ewutils.active_restrictions[pranked_data.id_user] = 0

        item_action = "delete"
    else:
        response = "You gotta find someone to prank someone with that item, first!\n**(Hint: !use item @player)**"

    return item_action, response, use_mention_displayname, side_effect


# Lay down a trap in a district.
async def prank_item_effect_trap(cmd, item):
    item_action = ""
    mentions_user = False
    use_mention_displayname = False
    side_effect = ""

    if cmd.mentions_count == 1:
        mentions_user = True

    if mentions_user:
        response = "You can't use that item on someone else! You gotta lay it down in a district!\n**(Hint: !use item)**"
    else:

        pranker_data = EwUser(member=cmd.message.author)

        # if pranker_data.credence == 0:
        # 	response = "You can't lay down a trap without any credence!"
        # 	return item_action, response, use_mention_displayname, side_effect

        # Store values inside the trap's item_props

        # halved_credence = int(pranker_data.credence / 2)
        # if halved_credence == 0:
        # 	halved_credence = 1
        #
        # pranker_data.credence = halved_credence
        # pranker_data.credence_used += halved_credence

        # item.item_props["trap_stored_credence"] = halved_credence
        item.item_props["trap_stored_credence"] = 0
        item.item_props["trap_user_id"] = str(pranker_data.id_user)

        item.persist()
        pranker_data.persist()

        response = "You lay down a {}. Hopefully someone's dumb enough to fall for it.".format(item.item_props.get('item_name'))
        item_action = "drop"

    return item_action, response, use_mention_displayname, side_effect
