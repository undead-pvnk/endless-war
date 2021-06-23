from ew.static import cfg as ewcfg
from . import factioncmds

cmd_map = {

    # Allow people to enlist
    ewcfg.cmd_vouch: factioncmds.vouch,

}
