from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Craft things
    ewcfg.cmd_smelt: cmds.smelt,

    # Check recipes
    ewcfg.cmd_wcim: cmds.find_recipes_by_item,
    ewcfg.cmd_wcim_alt1: cmds.find_recipes_by_item,
    ewcfg.cmd_wcim_alt2: cmds.find_recipes_by_item,
    ewcfg.cmd_wcim_alt3: cmds.find_recipes_by_item,

}

apt_dm_cmd_map = {

    # !smelt
    ewcfg.cmd_smelt: cmds.smelt,

}
