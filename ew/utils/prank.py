import random

from . import core as ewutils
from . import frontend as fe_utils
from . import item as itm_utils
from ..backend import core as bknd_core
from ..backend import item as bknd_item
from ..backend.item import EwItem
from ..backend.user import EwUserBase as EwUser
from ..static import cfg as ewcfg
from ..static import poi as poi_static


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
