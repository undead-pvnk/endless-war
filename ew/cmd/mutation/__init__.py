from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Setting mutations
    ewcfg.cmd_reroll_mutation: cmds.reroll_last_mutation,
    ewcfg.cmd_clear_mutations: cmds.clear_mutations,
    ewcfg.cmd_chemo: cmds.chemo,
    ewcfg.cmd_graft: cmds.graft,

    # Mutation only Cmds
    ewcfg.cmd_preserve: cmds.preserve,
    ewcfg.cmd_stink: cmds.waft,
    ewcfg.cmd_track: cmds.track_oneeyeopen,
    ewcfg.cmd_shakeoff: cmds.shakeoff,
    ewcfg.cmd_clench: cmds.clench,
    ewcfg.cmd_bleedout: cmds.bleedout,
    ewcfg.cmd_piss: cmds.piss,
    ewcfg.cmd_fursuit: cmds.fursuit,
    ewcfg.cmd_devour: cmds.devour,
    ewcfg.cmd_longdrop: cmds.longdrop,
    ewcfg.cmd_skullbash: cmds.skullbash,

}

apt_dm_cmd_map = {

    # !stink
    ewcfg.cmd_stink: cmds.waft,

    # !bleedout
    ewcfg.cmd_bleedout: cmds.bleedout,

    # more oeo
    ewcfg.cmd_track: cmds.track_oneeyeopen,

    # preserve
    ewcfg.cmd_preserve: cmds.preserve,

    # clench your cheeks
    ewcfg.cmd_clench: cmds.clench,

    # piss on the floor
    ewcfg.cmd_piss: cmds.piss,

    ewcfg.cmd_longdrop: cmds.longdrop,

}
