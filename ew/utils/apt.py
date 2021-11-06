import time

from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend.apt import EwApartment
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.player import EwPlayer
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as item_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser


async def rent_time(id_server = None):
    try:
        conn_info = bknd_core.databaseConnect()
        conn = conn_info.get('conn')
        cursor = conn.cursor()
        client = ewutils.get_client()
        if id_server != None:
            # get all players with apartments. If a player is evicted, thir rent is 0, so this will not affect any bystanders.
            cursor.execute("SELECT apartment.rent, users.id_user FROM users INNER JOIN apartment ON users.id_user=apartment.id_user WHERE users.id_server = %s AND apartment.id_server = %s AND apartment.rent > 0".format(

            ), (
                id_server,
                id_server,
            ))

            landowners = cursor.fetchall()

            for landowner in landowners:
                owner_id_user = int(landowner[1])
                owner_rent_price = landowner[0]

                user_data = EwUser(id_user=owner_id_user, id_server=id_server)
                user_poi = poi_static.id_to_poi.get(user_data.poi)
                poi = poi_static.id_to_poi.get(user_data.apt_zone)

                if owner_rent_price > user_data.slimecoin:

                    if (user_poi.is_apartment and user_data.visiting == ewcfg.location_id_empty):
                        user_data.poi = user_data.apt_zone  # toss out player
                        user_data.persist()
                        server = ewcfg.server_list[user_data.id_server]
                        member_object = server.get_member(owner_id_user)

                        await ewrolemgr.updateRoles(client=client, member=member_object)
                        player = EwPlayer(id_user=owner_id_user)
                        response = "{} just got evicted. Point and laugh, everyone.".format(player.display_name)
                        await fe_utils.send_message(client, fe_utils.get_channel(server, poi.channel), response)

                    user_data = EwUser(id_user=owner_id_user, id_server=id_server)
                    user_apt = EwApartment(id_user=owner_id_user, id_server=id_server)
                    poi = poi_static.id_to_poi.get(user_data.apt_zone)

                    toss_items(id_user=str(user_data.id_user) + 'closet', id_server=user_data.id_server, poi=poi)
                    toss_items(id_user=str(user_data.id_user) + 'fridge', id_server=user_data.id_server, poi=poi)
                    toss_items(id_user=str(user_data.id_user) + 'decorate', id_server=user_data.id_server, poi=poi)

                    user_data.apt_zone = ewcfg.location_id_empty
                    user_data.persist()
                    user_apt.rent = 0
                    user_apt.poi = " "
                    user_apt.persist()

                    await toss_squatters(user_id=user_data.id_user, server_id=id_server)

                else:
                    user_data.change_slimecoin(n=-owner_rent_price, coinsource=ewcfg.coinsource_spending)
                    user_data.persist()
    finally:
        cursor.close()
        bknd_core.databaseClose(conn_info)


async def setOffAlarms(id_server = None):
    ewutils.logMsg('Setting off alarms...')

    if id_server != None:
        client = ewutils.get_client()
        server = client.get_guild(id_server)
        time_current = EwMarket(id_server=id_server).clock
        if time_current <= 12:
            displaytime = str(time_current)
            ampm = 'am'
        if time_current > 12:
            displaytime = str(time_current - 12)
            ampm = 'pm'

        if time_current == 24:
            ampm = "am"
        elif time_current == 12:
            ampm = "pm"

        item_search = "alarm clock set to {}{}".format(displaytime, ampm)
        item_search_brick = "brick{:02d}".format(time_current)
        clockinv = item_utils.find_item_all(item_search="alarmclock", id_server=id_server, item_type_filter=ewcfg.it_furniture)
        brickinv = item_utils.find_item_all(item_search=item_search_brick, id_server=id_server, item_type_filter=ewcfg.it_furniture, search_names=True)

        for clock in clockinv:
            isFurnished = False
            clock_obj = EwItem(id_item=clock.get('id_item'))

            if clock_obj.item_props.get('furniture_name') == item_search:
                if "decorate" in clock_obj.id_owner:
                    isFurnished = True
                clock_user = clock_obj.id_owner.replace("decorate", "")
                clock_member = server.get_member(user_id=clock_user)
                if clock_member != None:
                    clock_player = EwUser(member=clock_member)
                    if (isFurnished == False or ("apt" in clock_player.poi and clock_player.visiting == "empty")) and clock_member:
                        try:
                            await fe_utils.send_message(client, clock_member, fe_utils.formatMessage(clock_member, "BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP"))
                        except:
                            ewutils.logMsg("failed to send alarm to user {}".format(clock_member.id))

        for brick in brickinv:
            brick_obj = EwItem(id_item=brick.get('id_item'))
            id_user = brick_obj.id_owner.replace("brickshit", "")
            brick_user = EwUser(id_server=id_server, id_user=id_user)
            brick_member = server.get_member(user_id=int(id_user))
            poi = poi_static.id_to_poi.get(brick_user.poi)
            channel_brick = fe_utils.get_channel(server, poi.channel)
            if brick_member != None:
                if brick_member:
                    try:
                        await fe_utils.send_message(client, channel_brick, fe_utils.formatMessage(brick_member, "UUUUUUUUUUGGGGGGGGGGGGHHHHHHHHHHH... OOOOOOOOOOOOOOOOOAAAAAAAAAAAAAAAHHHHH th-tunk. You just shit a brick. Congratulations?"))
                        brick_obj.id_owner = poi.id_poi
                        brick_obj.item_props['furniture_name'] = 'brick'
                        brick_obj.persist()
                    except:
                        ewutils.logMsg("failed to shit brick on user {}".format(brick_member.id))


def toss_items(id_user = None, id_server = None, poi = None):
    if id_user != None and id_server != None and poi != None:
        inv_toss = bknd_item.inventory(id_user=id_user, id_server=id_server)
        for stuff in inv_toss:  # toss all items out
            stuffing = EwItem(id_item=stuff.get('id_item'))
            stuffing.id_owner = poi.id_poi
            if stuff.get('item_type') == ewcfg.it_food and id_user[-6:] == ewcfg.compartment_id_fridge:
                if int(float(stuffing.item_props.get('time_fridged'))) != 0:
                    stuffing.item_props['time_expir'] = str(int(float(stuffing.item_props.get('time_expir'))) + (int(time.time()) - int(float(stuffing.item_props.get('time_fridged')))))
                else:
                    stuffing.item_props['time_expir'] = str(int(float(stuffing.item_props.get('time_fridged'))) + 43200)
                stuffing.time_expir = int(float(stuffing.item_props.get('time_expir')))
                stuffing.item_props['time_fridged'] = '0'
            stuffing.persist()


async def toss_squatters(user_id = None, server_id = None, keepKeys = False):
    player_info = EwPlayer(id_user=user_id)
    apt_info = EwApartment(id_user=user_id, id_server=server_id)

    client = ewutils.get_client()
    server = client.get_guild(server_id)

    member_data = server.get_member(player_info.id_user)

    if player_info.id_server != None and member_data != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()
            client = ewutils.get_client()

            # get all players visiting an evicted apartment and kick them out
            cursor.execute(
                "SELECT {} FROM users WHERE {} = %s AND {} = %s".format(
                    ewcfg.col_id_user,
                    ewcfg.col_visiting,
                    ewcfg.col_id_server,
                ), (
                    member_data.id,
                    server_id,
                ))

            squatters = cursor.fetchall()
            key_1 = EwItem(id_item=apt_info.key_1).id_owner
            key_2 = EwItem(id_item=apt_info.key_2).id_owner
            for squatter in squatters:
                sqt_data = EwUser(id_user=squatter[0], id_server=player_info.id_server)
                if keepKeys and (sqt_data.id_user == key_1 or sqt_data.id_user == key_2):
                    pass
                else:
                    server = ewcfg.server_list[sqt_data.id_server]
                    member_object = server.get_member(squatter[0])
                    sqt_data.poi = sqt_data.poi[3:] if sqt_data.poi[3:] in poi_static.id_to_poi.keys() else sqt_data.poi
                    sqt_data.visiting = ewcfg.location_id_empty
                    sqt_data.persist()
                    await ewrolemgr.updateRoles(client=client, member=member_object)
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


async def lobbywarning(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)

    poi = poi_static.id_to_poi.get(usermodel.poi)
    if poi.is_apartment:
        response = "Try that in a DM to ENDLESS WAR or in your apartment."
    else:
        response = "You're not in an apartment."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
