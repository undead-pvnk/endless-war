from . import cmds
from .utils import *
from ..static import cfg as ewcfg

cmd_map = {

    # slimeball
    ewcfg.cmd_slimeball: cmds.slimeball,
    ewcfg.cmd_slimeballgo: cmds.slimeballgo,
    ewcfg.cmd_slimeballstop: cmds.slimeballstop,
    ewcfg.cmd_slimeballleave: cmds.slimeballleave,

}