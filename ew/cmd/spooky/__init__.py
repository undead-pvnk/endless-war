"""
	Commands and utilities related to dead players.
"""

from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Show the total of negative slime in the market.
    ewcfg.cmd_negapool: cmds.negapool,

    # Show the total of negative slime in the world.
    ewcfg.cmd_negaslime: cmds.negaslime,

    # revive yourself as a juvenile after having been killed.
    ewcfg.cmd_revive: cmds.revive,

    # Ghosts can haunt enlisted players to reduce their slime score.
    ewcfg.cmd_haunt: cmds.haunt,
    ewcfg.cmd_haunt_alt1: cmds.haunt,
    ewcfg.cmd_haunt_alt2: cmds.haunt,
    ewcfg.cmd_haunt_alt3: cmds.haunt,
    ewcfg.cmd_haunt_alt4: cmds.haunt,
    ewcfg.cmd_haunt_alt5: cmds.haunt,
    ewcfg.cmd_haunt_alt6: cmds.haunt,

    # ghosts can inhabit players to follow them around
    ewcfg.cmd_inhabit: cmds.inhabit,
    ewcfg.cmd_inhabit_alt1: cmds.inhabit,
    ewcfg.cmd_inhabit_alt2: cmds.inhabit,
    ewcfg.cmd_inhabit_alt3: cmds.inhabit,

    # remove inhabitted status
    ewcfg.cmd_letgo: cmds.let_go,

    # ghosts can empower the weapon of the player they're inhabiting
    ewcfg.cmd_possess_weapon: cmds.possess_weapon,
    ewcfg.cmd_possess_weapon_alt1: cmds.possess_weapon,
    ewcfg.cmd_possess_weapon_alt2: cmds.possess_weapon,

    # ghosts can enhance fishing for the player they're inhabiting
    # Why can't this just be the same as possessing a weapon
    ewcfg.cmd_possess_fishing_rod: cmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt1: cmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt2: cmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt3: cmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt4: cmds.possess_fishing_rod,

    # ghosts can dissolve this contract if they want to
    ewcfg.cmd_unpossess_fishing_rod: cmds.unpossess_fishing_rod,
    ewcfg.cmd_unpossess_fishing_rod_alt1: cmds.unpossess_fishing_rod,
    ewcfg.cmd_unpossess_fishing_rod_alt2: cmds.unpossess_fishing_rod,

    # ghosts can turn their negaslime into negapoudrins
    ewcfg.cmd_crystalize_negapoudrin: cmds.crystalize_negapoudrin,
    ewcfg.cmd_crystalize_negapoudrin_alt1: cmds.crystalize_negapoudrin,
    ewcfg.cmd_crystalize_negapoudrin_alt2: cmds.crystalize_negapoudrin,
    ewcfg.cmd_crystalize_negapoudrin_alt3: cmds.crystalize_negapoudrin,

    # Ghosts can spawn a (mostly) randomly generated negaslimeoid
    #ewcfg.cmd_summonnegaslimeoid: cmds.summon_negaslimeoid,
    #ewcfg.cmd_summonnegaslimeoid_alt1: cmds.summon_negaslimeoid,
    #ewcfg.cmd_summonnegaslimeoid_alt2: cmds.summon_negaslimeoid,

}
