from . import cmds
from ew.static import cfg as ewcfg

cmd_map = {

    # farming
    ewcfg.cmd_sow: cmds.sow,
    ewcfg.cmd_reap: cmds.reap,
    ewcfg.cmd_reap_alt: cmds.reap,
    ewcfg.cmd_check_farm: cmds.check_farm,
    ewcfg.cmd_irrigate: cmds.cultivate,
    ewcfg.cmd_weed: cmds.cultivate,
    ewcfg.cmd_fertilize: cmds.cultivate,
    ewcfg.cmd_pesticide: cmds.cultivate,
    ewcfg.cmd_mill: cmds.mill,
    
}

apt_dm_cmd_map = {

    # !checkfarm
    # Why was this in here btw? it doesnt even work
    ewcfg.cmd_check_farm: cmds.check_farm,
    
}