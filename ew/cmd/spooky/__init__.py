"""
	Commands and utilities related to dead players.
"""

from ew.static import cfg as ewcfg
from . import spookycmds

cmd_map = {

    # Show the total of negative slime in the market.
    ewcfg.cmd_negapool: spookycmds.negapool,

    # Show the total of negative slime in the world.
    ewcfg.cmd_negaslime: spookycmds.negaslime,

    # revive yourself as a juvenile after having been killed.
    ewcfg.cmd_revive: spookycmds.revive,

    # Ghosts can haunt enlisted players to reduce their slime score.
    ewcfg.cmd_haunt: spookycmds.haunt,
    ewcfg.cmd_haunt_alt1: spookycmds.haunt,
    ewcfg.cmd_haunt_alt2: spookycmds.haunt,
    ewcfg.cmd_haunt_alt3: spookycmds.haunt,
    ewcfg.cmd_haunt_alt4: spookycmds.haunt,
    ewcfg.cmd_haunt_alt5: spookycmds.haunt,
    ewcfg.cmd_haunt_alt6: spookycmds.haunt,

    # ghosts can inhabit players to follow them around
    ewcfg.cmd_inhabit: spookycmds.inhabit,
    ewcfg.cmd_inhabit_alt1: spookycmds.inhabit,
    ewcfg.cmd_inhabit_alt2: spookycmds.inhabit,
    ewcfg.cmd_inhabit_alt3: spookycmds.inhabit,

    # remove inhabitted status
    ewcfg.cmd_letgo: spookycmds.let_go,

    # ghosts can empower the weapon of the player they're inhabiting
    ewcfg.cmd_possess_weapon: spookycmds.possess_weapon,
    ewcfg.cmd_possess_weapon_alt1: spookycmds.possess_weapon,
    ewcfg.cmd_possess_weapon_alt2: spookycmds.possess_weapon,

    # ghosts can enhance fishing for the player they're inhabiting
    # Why can't this just be the same as possessing a weapon
    ewcfg.cmd_possess_fishing_rod: spookycmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt1: spookycmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt2: spookycmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt3: spookycmds.possess_fishing_rod,
    ewcfg.cmd_possess_fishing_rod_alt4: spookycmds.possess_fishing_rod,

    # ghosts can dissolve this contract if they want to
    ewcfg.cmd_unpossess_fishing_rod: spookycmds.unpossess_fishing_rod,
    ewcfg.cmd_unpossess_fishing_rod_alt1: spookycmds.unpossess_fishing_rod,
    ewcfg.cmd_unpossess_fishing_rod_alt2: spookycmds.unpossess_fishing_rod,

    # ghosts can turn their negaslime into negapoudrins
    ewcfg.cmd_crystalize_negapoudrin: spookycmds.crystalize_negapoudrin,
    ewcfg.cmd_crystalize_negapoudrin_alt1: spookycmds.crystalize_negapoudrin,
    ewcfg.cmd_crystalize_negapoudrin_alt2: spookycmds.crystalize_negapoudrin,
    ewcfg.cmd_crystalize_negapoudrin_alt3: spookycmds.crystalize_negapoudrin,

}
