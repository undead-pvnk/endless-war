from . import cmds
from ..static import cfg as ewcfg

cmd_map = {

    # Allow people to enlist
    ewcfg.cmd_vouch: cmds.vouch,

}