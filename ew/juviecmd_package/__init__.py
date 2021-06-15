from . import cmds
from .utils import *
from ..static import cfg as ewcfg

cmd_map = {

    # Crush a poudrin to get some slime.
    ewcfg.cmd_crush: cmds.crush,
    ewcfg.cmd_crush_alt1: cmds.crush,

    # move from juvenile to one of the armies (rowdys or killers)
    ewcfg.cmd_enlist: cmds.enlist,
    ewcfg.cmd_renounce: cmds.renounce,

    # gives slime to the miner (message.author)
    ewcfg.cmd_mine: cmds.mine,

    # flags a vein as dangerous
    ewcfg.cmd_flag: cmds.flag,

    # scavenging
    ewcfg.cmd_scavenge: cmds.scavenge,
    ewcfg.cmd_scavenge_alt1: cmds.scavenge,
    ewcfg.cmd_scavenge_alt2: cmds.scavenge,
    
    # LOL
    ewcfg.cmd_juviemode: cmds.juviemode,

}