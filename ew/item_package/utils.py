from ..backend import item as bknd_item
from ..backend.item import EwItem
from ..backend.player import EwPlayer
from ..static import cfg as ewcfg
from ..utils import core as ewutils
from ..utils.combat import EwUser

"""
    Drop item into current district.
"""
def item_drop(
    id_item = None,
    other_poi = None
):
    try:
        item_data = EwItem(id_item = id_item)
        user_data = EwUser(id_user = item_data.id_owner, id_server = item_data.id_server)
        if other_poi == None:
            dest = user_data.poi
        else:
            dest = other_poi

        if item_data.item_type == ewcfg.it_cosmetic:
            item_data.item_props["adorned"] = "false"
        item_data.persist()
        bknd_item.give_item(id_user = dest, id_server = item_data.id_server, id_item = item_data.id_item)
    except:
        ewutils.logMsg("Failed to drop item {}.".format(id_item))

def item_lootspecific(id_server = None, id_user = None, item_search = None):
    response = ""
    if id_server is not None and id_user is not None:
        user_data = EwUser(id_user = id_user, id_server = id_server)
        item_sought = bknd_item.find_item(
            item_search = item_search,
            id_server = user_data.id_server,
            id_user = user_data.poi
        )
        if item_sought is not None:
            item_type = item_sought.get("item_type")
            response += "You found a {}!".format(item_sought.get("name"))
            can_loot = bknd_item.check_inv_capacity(user_data = user_data, item_type = item_type)
            if can_loot:
                bknd_item.give_item(
                    id_item = item_sought.get("id_item"),
                    id_user = user_data.id_user,
                    id_server = user_data.id_server
                )
            else:
                response += " But you couldn't carry any more {}s, so you tossed it back.".format(item_type)
    return response

def soulbind(id_item):
    item = EwItem(id_item = id_item)
    item.soulbound = True
    item.persist()

"""
    Find every item matching the search in the player's inventory (returns a list of (non-EwItem) item)
"""
def find_item_all(item_search = None, id_user = None, id_server = None, item_type_filter = None, exact_search = True, search_names = False):
    items_sought = []
    props_to_search = [
        'weapon_type',
        'id_item',
        'id_food',
        'id_cosmetic',
        'id_furniture'
    ]

    if search_names == True:
        props_to_search = [
            'cosmetic_name',
            'furniture_name',
            'food_name',
            'title',
            'weapon_type',
            'weapon_name',
            'item_name'
        ]

    if item_search:
        items = bknd_item.inventory(id_user = id_user, id_server = id_server, item_type_filter = item_type_filter)

        # find the first (i.e. the oldest) item that matches the search
        for item in items:
            item_data = EwItem(id_item = item.get('id_item'))
            for prop in props_to_search:
                if prop in item_data.item_props and (ewutils.flattenTokenListToString(item_data.item_props.get(prop)) == item_search or (exact_search == False and item_search in ewutils.flattenTokenListToString(item_data.item_props.get(prop)))):
                    items_sought.append(item)
                    break

    return items_sought

def surrendersoul(giver = None, receiver = None, id_server=None):

    if giver != None and receiver != None:
        receivermodel = EwUser(id_server=id_server, id_user=receiver)
        givermodel = EwUser(id_server=id_server, id_user=giver)
        giverplayer = EwPlayer(id_user=givermodel.id_user)
        if givermodel.has_soul == 1:
            givermodel.has_soul = 0
            givermodel.persist()

            item_id = bknd_item.item_create(
                id_user=receivermodel.id_user,
                id_server=id_server,
                item_type=ewcfg.it_cosmetic,
                item_props={
                    'id_cosmetic': "soul",
                    'cosmetic_name': "{}'s soul".format(giverplayer.display_name),
                    'cosmetic_desc': "The immortal soul of {}. It dances with a vivacious energy inside its jar.\n If you listen to it closely you can hear it whispering numbers: {}.".format(
                        giverplayer.display_name, givermodel.id_user),
                    'str_onadorn': ewcfg.str_generic_onadorn,
                    'str_unadorn': ewcfg.str_generic_unadorn,
                    'str_onbreak': ewcfg.str_generic_onbreak,
                    'rarity': ewcfg.rarity_patrician,
                    'attack': 6,
                    'defense': 6,
                    'speed': 6,
                    'ability': None,
                    'durability': None,
                    'size': 6,
                    'fashion_style': ewcfg.style_cool,
                    'freshness': 10,
                    'adorned': 'false',
                    'user_id': givermodel.id_user
                }
            )

            return item_id

async def lower_durability(general_item):
    general_item_data = EwItem(id_item=general_item.get('id_item'))

    current_durability = general_item_data.item_props.get('durability')
    general_item_data.item_props['durability'] = (int(current_durability) - 1)
    general_item_data.persist()
