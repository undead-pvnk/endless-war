from ew.static import cfg as ewcfg
from . import mutationcmds

cmd_map = {

    # Setting mutations
    ewcfg.cmd_reroll_mutation: mutationcmds.reroll_last_mutation,
    ewcfg.cmd_clear_mutations: mutationcmds.clear_mutations,
    ewcfg.cmd_chemo: mutationcmds.chemo,
    ewcfg.cmd_graft: mutationcmds.graft,

    # Mutation only Cmds
    ewcfg.cmd_preserve: mutationcmds.preserve,
    ewcfg.cmd_stink: mutationcmds.waft,
    ewcfg.cmd_track: mutationcmds.track_oneeyeopen,
    ewcfg.cmd_shakeoff: mutationcmds.shakeoff,
    ewcfg.cmd_clench: mutationcmds.clench,
    ewcfg.cmd_bleedout: mutationcmds.bleedout,
    ewcfg.cmd_piss: mutationcmds.piss,
    ewcfg.cmd_fursuit: mutationcmds.fursuit,
    ewcfg.cmd_devour: mutationcmds.devour,
    ewcfg.cmd_longdrop: mutationcmds.longdrop,
    ewcfg.cmd_skullbash: mutationcmds.skullbash,
    ewcfg.cmd_slap: mutationcmds.slap,
    ewcfg.cmd_thirdeye: mutationcmds.tracker,

}

apt_dm_cmd_map = {

    # !stink
    ewcfg.cmd_stink: mutationcmds.waft,

    # !bleedout
    ewcfg.cmd_bleedout: mutationcmds.bleedout,

    # more oeo
    ewcfg.cmd_track: mutationcmds.track_oneeyeopen,

    # preserve
    ewcfg.cmd_preserve: mutationcmds.preserve,

    # clench your cheeks
    ewcfg.cmd_clench: mutationcmds.clench,

    # piss on the floor
    ewcfg.cmd_piss: mutationcmds.piss,

    ewcfg.cmd_longdrop: mutationcmds.longdrop,

    ewcfg.cmd_thirdeye: mutationcmds.tracker,

}
