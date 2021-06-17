from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Try to start going somewhere
    ewcfg.cmd_move: cmds.move,
    ewcfg.cmd_move_alt1: cmds.move,
    ewcfg.cmd_move_alt2: cmds.move,
    ewcfg.cmd_move_alt3: cmds.move,
    ewcfg.cmd_move_alt4: cmds.move,
    ewcfg.cmd_move_alt5: cmds.move,
    ewcfg.cmd_move_alt6: cmds.move,

    # go down
    ewcfg.cmd_descend: cmds.descend,

    # Cancel all moves in progress.
    ewcfg.cmd_halt: cmds.halt,
    ewcfg.cmd_halt_alt1: cmds.halt,

    # Look around the POI you find yourself in.
    ewcfg.cmd_look: cmds.look,

    # Look around the POI, but do not obtain the district's description (reduces clutter and response time).
    ewcfg.cmd_survey: cmds.survey,
    ewcfg.cmd_survey_alt1: cmds.survey,

    # Look around an adjacent POI
    ewcfg.cmd_scout: cmds.scout,
    ewcfg.cmd_scout_alt1: cmds.scout,

    # These two makes more sense than where some other mutation commands are
    # but cmon. put mutation commands. in ew/mutations
    ewcfg.cmd_teleport: cmds.teleport,
    ewcfg.cmd_teleport_alt1: cmds.teleport,
    ewcfg.cmd_loop: cmds.loop,

    # ---- Admin commands ---- #
    ewcfg.cmd_teleport_player: cmds.teleport_player,
    ewcfg.cmd_print_map_data: cmds.print_map_data,
    ewcfg.cmd_boot: cmds.boot,
    # flush items and slime from subzones into their mother district
    ewcfg.cmd_flushsubzones: cmds.flush_subzones,
    ewcfg.cmd_flushstreets: cmds.flush_streets,
    # ---- -------------- ---- #

    # SlimeCorp commands
    ewcfg.cmd_clockin: cmds.clockin,
    ewcfg.cmd_clockout: cmds.clockout,
    # Isn't this dead?
    ewcfg.cmd_surveil: cmds.surveil,

}

apt_dm_cmd_map = {

    # !goto. Navigate the world map.
    ewcfg.cmd_move: cmds.move,
    ewcfg.cmd_move_alt1: cmds.move,
    ewcfg.cmd_move_alt2: cmds.move,
    ewcfg.cmd_move_alt3: cmds.move,
    ewcfg.cmd_move_alt4: cmds.move,
    ewcfg.cmd_move_alt5: cmds.move,
    ewcfg.cmd_move_alt6: cmds.move,

    # !stop, Cancel all moves in progress.
    ewcfg.cmd_halt: cmds.halt,
    ewcfg.cmd_halt_alt1: cmds.halt,

    # Look around an adjacent POI
    ewcfg.cmd_scout: cmds.scout,
    ewcfg.cmd_scout_alt1: cmds.scout,

}
