from . import cmds
from .utils import *
from ..static import cfg as ewcfg

cmd_map = {

    # See what's for sale in the Food Court.
    ewcfg.cmd_menu: cmds.menu,
    ewcfg.cmd_menu_alt1: cmds.menu,
    ewcfg.cmd_menu_alt2: cmds.menu,

    # Order refreshing food and drinks!
    ewcfg.cmd_order: cmds.order,
    ewcfg.cmd_buy: cmds.order,

    # eat a food item from a player's inventory
    ewcfg.cmd_eat: cmds.eat_item,
    ewcfg.cmd_eat_alt1: cmds.eat_item,
    
    # Eat a non food item. put this is mutations dammit
    ewcfg.cmd_devour: cmds.devour,

}