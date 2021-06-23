from ew.static import cfg as ewcfg
from . import fishcmds

cmd_map = {

    # Catching fish
    ewcfg.cmd_cast: fishcmds.cast,
    ewcfg.cmd_reel: fishcmds.reel,

    # Trading fish
    ewcfg.cmd_appraise: fishcmds.appraise,
    ewcfg.cmd_barter: fishcmds.barter,
    ewcfg.cmd_embiggen: fishcmds.embiggen,
    ewcfg.cmd_barterall: fishcmds.barter_all,

    # Admin Cmds
    # ewcfg.cmd_createfish: cmds.debug_create_random_fish,

}
