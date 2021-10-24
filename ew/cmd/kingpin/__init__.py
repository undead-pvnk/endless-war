"""
	Commands for kingpins only.
"""

from ew.static import cfg as ewcfg
from . import kingpincmds

cmd_map = {

    # Kingpin announcements
    ewcfg.cmd_paspeaker: kingpincmds.pa_command,
    ewcfg.cmd_pacommand: kingpincmds.pa_command,

    # Remove a megaslime (1 mil slime) from a general.
    ewcfg.cmd_deadmega: kingpincmds.deadmega,

    # Release a player from their faction.
    ewcfg.cmd_pardon: kingpincmds.pardon,
    ewcfg.cmd_banish: kingpincmds.banish,

    # Create soulbound items
    ewcfg.cmd_create: kingpincmds.create,
    # ewcfg.cmd_exalt: cmds.exalt,

    # Stop a player from speaking out of game
    ewcfg.cmd_hogtie: kingpincmds.hogtie,
    ewcfg.cmd_defect: kingpincmds.defect
}
if ewcfg.dh_active:
    cmd_map[ewcfg.cmd_exalt] = kingpincmds.exalt