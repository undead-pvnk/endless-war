from ew.static import cfg as ewcfg
from . import movecmds

cmd_map = {

    # Try to start going somewhere
    ewcfg.cmd_move: movecmds.move,
    ewcfg.cmd_move_alt1: movecmds.move,
    ewcfg.cmd_move_alt2: movecmds.move,
    ewcfg.cmd_move_alt3: movecmds.move,
    ewcfg.cmd_move_alt4: movecmds.move,
    ewcfg.cmd_move_alt5: movecmds.move,
    ewcfg.cmd_move_alt6: movecmds.move,

    # go down
    ewcfg.cmd_descend: movecmds.descend,

    # Cancel all moves in progress.
    ewcfg.cmd_halt: movecmds.halt,
    ewcfg.cmd_halt_alt1: movecmds.halt,

    # Look around the POI you find yourself in.
    ewcfg.cmd_look: movecmds.look,

    # Look around the POI, but do not obtain the district's description (reduces clutter and response time).
    ewcfg.cmd_survey: movecmds.survey,
    ewcfg.cmd_survey_alt1: movecmds.survey,

    # Look around an adjacent POI
    ewcfg.cmd_scout: movecmds.scout,
    ewcfg.cmd_scout_alt1: movecmds.scout,

    # These two makes more sense than where some other mutation commands are
    # but cmon. put mutation commands. in ew/mutations
    ewcfg.cmd_teleport: movecmds.teleport,
    ewcfg.cmd_teleport_alt1: movecmds.teleport,
    ewcfg.cmd_loop: movecmds.loop,

    # ---- Admin commands ---- #
    ewcfg.cmd_teleport_player: movecmds.teleport_player,
    ewcfg.cmd_print_map_data: movecmds.print_map_data,
    ewcfg.cmd_boot: movecmds.boot,
    # flush items and slime from subzones into their mother district
    ewcfg.cmd_flushsubzones: movecmds.flush_subzones,
    ewcfg.cmd_flushstreets: movecmds.flush_streets,
    # ---- -------------- ---- #

    # SlimeCorp commands
    ewcfg.cmd_clockin: movecmds.clockin,
    ewcfg.cmd_clockout: movecmds.clockout,
    # Isn't this dead?
    ewcfg.cmd_surveil: movecmds.surveil,

}

apt_dm_cmd_map = {

    # !goto. Navigate the world map.
    ewcfg.cmd_move: movecmds.move,
    ewcfg.cmd_move_alt1: movecmds.move,
    ewcfg.cmd_move_alt2: movecmds.move,
    ewcfg.cmd_move_alt3: movecmds.move,
    ewcfg.cmd_move_alt4: movecmds.move,
    ewcfg.cmd_move_alt5: movecmds.move,
    ewcfg.cmd_move_alt6: movecmds.move,

    # !stop, Cancel all moves in progress.
    ewcfg.cmd_halt: movecmds.halt,
    ewcfg.cmd_halt_alt1: movecmds.halt,

    # Look around an adjacent POI
    ewcfg.cmd_scout: movecmds.scout,
    ewcfg.cmd_scout_alt1: movecmds.scout,

}
