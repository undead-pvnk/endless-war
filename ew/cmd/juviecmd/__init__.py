from ew.static import cfg as ewcfg
from . import juviecmds

cmd_map = {

    # Crush a poudrin to get some slime.
    ewcfg.cmd_crush: juviecmds.crush,
    ewcfg.cmd_crush_alt1: juviecmds.crush,

    # move from juvenile to one of the armies (rowdys or killers)
    ewcfg.cmd_enlist: juviecmds.enlist,
    ewcfg.cmd_renounce: juviecmds.renounce,

    # gives slime to the miner (message.author)
    ewcfg.cmd_mine: juviecmds.mine,

    # flags a vein as dangerous
    ewcfg.cmd_flag: juviecmds.flag,

    # scavenging
    ewcfg.cmd_scavenge: juviecmds.scavenge,
    ewcfg.cmd_scavenge_alt1: juviecmds.scavenge,
    ewcfg.cmd_scavenge_alt2: juviecmds.scavenge,
    ewcfg.cmd_scavenge_alt3: juviecmds.scavenge,    
    ewcfg.cmd_scavenge_alt4: juviecmds.scavenge,

    # LOL
    ewcfg.cmd_juviemode: juviecmds.juviemode,

    # gender??? OMG???
    ewcfg.cmd_identify: juviecmds.identify,
}
