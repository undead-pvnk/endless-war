from ew.static import cfg as ewcfg
from . import farmcmds

cmd_map = {

    # farming
    ewcfg.cmd_sow: farmcmds.sow,
    ewcfg.cmd_reap: farmcmds.reap,
    ewcfg.cmd_reap_alt: farmcmds.reap,
    ewcfg.cmd_check_farm: farmcmds.check_farm,
    ewcfg.cmd_irrigate: farmcmds.cultivate,
    ewcfg.cmd_weed: farmcmds.cultivate,
    ewcfg.cmd_fertilize: farmcmds.cultivate,
    ewcfg.cmd_pesticide: farmcmds.cultivate,
    ewcfg.cmd_mill: farmcmds.mill,

}

apt_dm_cmd_map = {

    # !checkfarm
    # Why was this in here btw? it doesnt even work
    ewcfg.cmd_check_farm: farmcmds.check_farm,

}
