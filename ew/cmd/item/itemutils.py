import sys

from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.static import cfg as ewcfg
from ew.utils import core as ewutils
from ew.utils.combat import EwUser

"""
    Drop item into current district.
"""


def item_drop(
        id_item = None,
        other_poi = None
):
    try:
        item_data = EwItem(id_item=id_item)
        user_data = EwUser(id_user=item_data.id_owner, id_server=item_data.id_server)
        if other_poi == None:
            dest = user_data.poi
        else:
            dest = other_poi

        if item_data.item_type == ewcfg.it_cosmetic:
            item_data.item_props["adorned"] = "false"
        item_data.persist()
        bknd_item.give_item(id_user=dest, id_server=item_data.id_server, id_item=item_data.id_item)
    except:
        ewutils.logMsg("Failed to drop item {}.".format(id_item))
