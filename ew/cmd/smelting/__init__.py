from ew.static import cfg as ewcfg
from . import smeltingcmds

cmd_map = {

    # Craft things
    ewcfg.cmd_smelt: smeltingcmds.smelt,

    # Check recipes
    ewcfg.cmd_wcim: smeltingcmds.find_recipes_by_item,
    ewcfg.cmd_wcim_alt1: smeltingcmds.find_recipes_by_item,
    ewcfg.cmd_wcim_alt2: smeltingcmds.find_recipes_by_item,
    ewcfg.cmd_wcim_alt3: smeltingcmds.find_recipes_by_item,

}

apt_dm_cmd_map = {

    # !smelt
    ewcfg.cmd_smelt: smeltingcmds.smelt,

}
