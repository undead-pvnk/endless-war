"""
	Commands for kingpins only.
"""

from . import cmds
from ..static import cfg as ewcfg

cmd_map = {

    # Kingpin announcements
    ewcfg.cmd_paspeaker: cmds.pa_command,
    ewcfg.cmd_pacommand: cmds.pa_command,

    # Remove a megaslime (1 mil slime) from a general.
    ewcfg.cmd_deadmega: cmds.deadmega,

    # Release a player from their faction.
    ewcfg.cmd_pardon: cmds.pardon,
    ewcfg.cmd_banish: cmds.banish,
    
    # Create soulbound items
    ewcfg.cmd_create: cmds.create,
    # ewcfg.cmd_exalt: cmds.exalt,
    
    # Stop a player from speaking out of game
    ewcfg.cmd_hogtie: cmds.hogtie

}