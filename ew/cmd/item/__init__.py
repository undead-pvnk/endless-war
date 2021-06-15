from . import cmds
from .cmds import item_look
from .utils import *

cmd_map = {

    # Fiddle with souls
    ewcfg.cmd_extractsoul: cmds.soulextract,
    ewcfg.cmd_returnsoul: cmds.returnsoul,
    ewcfg.cmd_squeeze: cmds.squeeze,

    # show player inventory
    ewcfg.cmd_inventory: cmds.inventory_print,
    ewcfg.cmd_inventory_alt1: cmds.inventory_print,
    ewcfg.cmd_inventory_alt2: cmds.inventory_print,
    ewcfg.cmd_inventory_alt3: cmds.inventory_print,
    ewcfg.cmd_communitychest: cmds.inventory_print,

    # get an item's description
    ewcfg.cmd_inspect: cmds.item_look,
    ewcfg.cmd_inspect_alt1: cmds.item_look,

    # use an item
    ewcfg.cmd_use: cmds.item_use,

    # Edit props from discord
    ewcfg.cmd_editprops: cmds.manually_edit_item_properties,

    # give an item to another player
    ewcfg.cmd_give: cmds.give,

    # drop item into your current district
    ewcfg.cmd_discard: cmds.discard,
    ewcfg.cmd_discard_alt1: cmds.discard,

    # delete a food item from your inventory
    ewcfg.cmd_trash: cmds.trash,

    # delete a person
    ewcfg.cmd_zuck: cmds.zuck,

    # Why aren't these in mutations
    ewcfg.cmd_longdrop: cmds.longdrop,
    ewcfg.cmd_skullbash: cmds.skullbash,

    # Make a costume for Double Halloween
    # ewcfg.cmd_makecostume: ewitem.makecostume,

}

dm_cmd_map = {

    # show player !inventory
    ewcfg.cmd_inventory: cmds.inventory_print,
    ewcfg.cmd_inventory_alt1: cmds.inventory_print,
    ewcfg.cmd_inventory_alt2: cmds.inventory_print,
    ewcfg.cmd_inventory_alt3: cmds.inventory_print,
    ewcfg.cmd_communitychest: cmds.inventory_print,

    # !inspect
    ewcfg.cmd_inspect: cmds.item_look,
    ewcfg.cmd_inspect_alt1: cmds.item_look,

}

apt_dm_cmd_map = {

    # !use
    ewcfg.cmd_use: cmds.item_use,

    # !extract/returnsoul
    ewcfg.cmd_extractsoul: cmds.soulextract,
    ewcfg.cmd_returnsoul: cmds.returnsoul,

    # give an item to another player
    ewcfg.cmd_give: cmds.give,

    # !squeeze
    ewcfg.cmd_squeeze: cmds.squeeze,

    # drop something but really far away
    ewcfg.cmd_longdrop: cmds.longdrop,

}
