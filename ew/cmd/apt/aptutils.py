import asyncio

from ew.backend import item as bknd_item
from ew.backend.apt import EwApartment
from ew.backend.item import EwItem
from ew.backend.market import EwStock
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import move as move_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser


# This is quite literally not used anywhere
def check(str):
    if str.content == ewcfg.cmd_sign or str.content == ewcfg.cmd_rip:
        return True

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
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        move_utils.move_counter += 1
        move_current = ewutils.moves_active[cmd.message.author.id] = move_utils.move_counter
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


# returns a price based on the stock with the biggest change
def getPriceBase(cmd):
    # based on stock success
    user_data = EwUser(member=cmd.message.author)  # market rates average to 1000. This fomula calculates prices to specification based on that amount.
    kfc = EwStock(stock='kfc', id_server=user_data.id_server)
    tcb = EwStock(stock='tacobell', id_server=user_data.id_server)
    hut = EwStock(stock='pizzahut', id_server=user_data.id_server)
    if abs(kfc.market_rate - 1000) > abs(tcb.market_rate - 1000) and abs(kfc.market_rate - 1000) > abs(hut.market_rate - 1000):
        return kfc.market_rate * 201
    elif abs(tcb.market_rate - 1000) > abs(hut.market_rate - 1000):
        return tcb.market_rate * 201
    else:
        return hut.market_rate * 201


def letter_up(letter = None):
    if letter == ewcfg.property_class_a:
        return ewcfg.property_class_s
    elif letter == ewcfg.property_class_b:
        return ewcfg.property_class_a
    elif letter == ewcfg.property_class_c:
        return ewcfg.property_class_b


"""
	Apartments were originally intended to be read-only channels
	with all interaction being in the dms only. Someone apparently
	forgot maps existed and created this behemoth to parse the 
	proper commands from dms. DM command parsing will be redone
	with the same update that releases this package so this is 
	entirely nonsensical to keep around.

	--Crank Note: I removed it. Just imagine the biggest if else chain you've ever seen, and double it.
"""