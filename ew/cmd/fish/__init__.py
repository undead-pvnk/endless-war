from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Catching fish
    ewcfg.cmd_cast: cmds.cast,
    ewcfg.cmd_reel: cmds.reel,

    # Trading fish
    ewcfg.cmd_appraise: cmds.appraise,
    ewcfg.cmd_barter: cmds.barter,
    ewcfg.cmd_embiggen: cmds.embiggen,
    ewcfg.cmd_barterall: cmds.barter_all,

    # Admin Cmds
    # ewcfg.cmd_createfish: cmds.debug_create_random_fish,

}
