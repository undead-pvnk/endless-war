from ew.static import cfg as ewcfg
from . import foodcmds

cmd_map = {

    # See what's for sale in the Food Court.
    ewcfg.cmd_menu: foodcmds.menu,
    ewcfg.cmd_menu_alt1: foodcmds.menu,
    ewcfg.cmd_menu_alt2: foodcmds.menu,

    # Order refreshing food and drinks!
    ewcfg.cmd_order: foodcmds.order,
    ewcfg.cmd_buy: foodcmds.order,

    # eat a food item from a player's inventory
    ewcfg.cmd_eat: foodcmds.eat_item,
    ewcfg.cmd_eat_alt1: foodcmds.eat_item,

}
