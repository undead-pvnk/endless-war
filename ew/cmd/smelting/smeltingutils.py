from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.utils import frontend as fe_utils


async def smeltsoul(cmd):
    item = bknd_item.find_item(item_search="reanimatedcorpse", id_user=cmd.message.author.id, id_server=cmd.guild.id)
    if not item:
        response = "You can't rip a soul out of a nonexistent object."
    else:
        item_obj = EwItem(id_item=item.get('id_item'))
        if item_obj.item_props.get('target') != None and item_obj.item_props.get('target') != "":
            targetid = item_obj.item_props.get('target')
            if bknd_item.give_item(id_user=cmd.message.author.id, id_item=targetid, id_server=cmd.guild.id):
                response = "You ripped the soul out of the reanimated corpse. It's in mangled bits now."
                bknd_item.item_delete(id_item=item.get('id_item'))
            else:
                response = "You reach for the soul in the reanimated corpse, but your hands are full of cosmetics! Get rid of a few, freak."
        else:
            response = "That's not a reanimated corpse. It only looks like one. Get rid of the fake shit and we'll get started."
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
