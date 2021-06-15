import random

from ..backend import item as bknd_item
from ..backend.item import EwItem
from ..static import items as static_items
from ..utils import frontend as fe_utils
from ..utils import item as itm_utils


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


def unwrap(id_user = None, id_server = None, item = None):
    response = "You eagerly rip open a pack of Secreatures™ trading cards!!"
    bknd_item.item_delete(item.id_item)
    slimexodia = False

    slimexodia_chance = 1 / 1000

    if random.random() < slimexodia_chance:
        slimexodia = True

    if slimexodia == True:
        # If there are multiple possible products, randomly select one.
        slimexodia_item = random.choice(static_items.slimexodia_parts)

        response += " There’s a single holographic card poking out of the swathes of repeats and late edition cards..."
        response += " ***...What’s this?! It’s the legendary card {}!! If you’re able to collect the remaining pieces of Slimexodia, you might be able to smelt something incomprehensibly powerful!!***".format(slimexodia_item.str_name)

        item_props = itm_utils.gen_item_props(slimexodia_item)

        bknd_item.item_create(
            item_type=slimexodia_item.item_type,
            id_user=id_user.id,
            id_server=id_server.id,
            item_props=item_props
        )

    else:
        response += " But… it’s mostly just repeats and late edition cards. You toss them away."

    return response


def popcapsule(id_user = None, id_server = None, item = None):
    rarity_roll = random.randrange(10)
    bknd_item.item_delete(item.id_item)

    if rarity_roll > 3:
        prank_item = random.choice(static_items.prank_items_heinous)
    elif rarity_roll > 0:
        prank_item = random.choice(static_items.prank_items_scandalous)
    else:
        prank_item = random.choice(static_items.prank_items_forbidden)

    item_props = itm_utils.gen_item_props(prank_item)

    prank_item_id = bknd_item.item_create(
        item_type=prank_item.item_type,
        id_user=id_user.id,
        id_server=id_server.id,
        item_props=item_props
    )

    response = "You pop open the Prank Capsule to reveal a {}! Whoa, sick!!".format(prank_item.str_name)

    return response
