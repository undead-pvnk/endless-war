from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Allow people to enlist
    ewcfg.cmd_vouch: cmds.vouch,

}
