import asyncio
import time

from .. import move as ewmap
from ..backend import core as bknd_core
from ..backend import item as bknd_item
from ..backend.apt import EwApartment
from ..backend.item import EwItem
from ..backend.market import EwStock
from ..backend.player import EwPlayer
from ..static import cfg as ewcfg
from ..static import poi as poi_static
from ..utils import core as ewutils
from ..utils import frontend as fe_utils
from ..utils import rolemgr as ewrolemgr
from ..utils.combat import EwUser

async def usekey(cmd, owner_user):
	user_data = EwUser(member=cmd.message.author)
	poi = poi_static.id_to_poi.get(user_data.poi)
	poi_dest = poi_static.id_to_poi.get(ewcfg.poi_id_apt + owner_user.apt_zone)  # there isn't an easy way to change this, apologies for being a little hacky
	inv = bknd_item.inventory(id_user=cmd.message.author.id, id_server=cmd.guild.id)
	apartment = EwApartment(id_server=cmd.guild.id, id_user=owner_user.id_user)

	key = None
	for item_inv in inv:
		if "key to" in item_inv.get('name'):
			item_key_check = EwItem(id_item=item_inv.get('id_item'))
			if item_key_check.item_props.get("houseID") == str(owner_user.id_user):
				key = item_key_check

	if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You must enter an apartment in a zone's channel.".format(cmd.tokens[0])))
	elif key == None:
		response = "You don't have a key for their apartment."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
	elif apartment.apt_class == ewcfg.property_class_c or (apartment.apt_class in [ewcfg.property_class_a, ewcfg.property_class_b] and key.id_item == apartment.key_2):
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Your key's not working at this new flat. Your roomates must've forgotten to upgrade apartments. Congratulations on the homelessness by the way.".format(cmd.tokens[0])))
	elif owner_user.apt_zone != poi.id_poi:
		response = "Your key doesn't match an apartment here."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author,  response))
	else:
		ewmap.move_counter += 1
		move_current = ewutils.moves_active[cmd.message.author.id] = ewmap.move_counter
		await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You start walking toward the apartment."))

		await asyncio.sleep(20)


		if move_current == ewutils.moves_active[cmd.message.author.id]:
			user_data = EwUser(member=cmd.message.author)
			user_data.poi = poi_dest.id_poi
			user_data.visiting = owner_user.id_user
			user_data.persist()
			await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
			response = "You're in the apartment."

			try:
				await fe_utils.send_message(cmd.client, cmd.message.author, response)
			except:
				await fe_utils.send_message(cmd.client, fe_utils.get_channel(cmd.guild, poi_dest.channel), fe_utils.formatMessage(cmd.message.author, response))

#returns a price based on the stock with the biggest change
def getPriceBase(cmd):
	#based on stock success
	user_data = EwUser(member=cmd.message.author) #market rates average to 1000. This fomula calculates prices to specification based on that amount.
	kfc = EwStock(stock='kfc', id_server = user_data.id_server)
	tcb = EwStock(stock='tacobell', id_server=user_data.id_server)
	hut = EwStock(stock='pizzahut', id_server=user_data.id_server)
	if abs(kfc.market_rate - 1000) > abs(tcb.market_rate - 1000) and abs(kfc.market_rate - 1000) > abs(hut.market_rate - 1000):
		return kfc.market_rate * 201
	elif abs(tcb.market_rate - 1000) > abs(hut.market_rate - 1000):
		return tcb.market_rate * 201
	else:
		return hut.market_rate * 201

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
                    sqt_data.poi = sqt_data.poi[3:]
                    sqt_data.visiting = ewcfg.location_id_empty
                    sqt_data.persist()
                    await ewrolemgr.updateRoles(client=client, member=member_object)
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)

def letter_up(letter = None):
	if letter == ewcfg.property_class_a:
		return ewcfg.property_class_s
	elif letter == ewcfg.property_class_b:
		return ewcfg.property_class_a
	elif letter == ewcfg.property_class_c:
		return ewcfg.property_class_b

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