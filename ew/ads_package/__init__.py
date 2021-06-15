from . import cmds
from .utils import *
from ..static import cfg as ewcfg

cmd_map = {

    # ads
	ewcfg.cmd_advertise: cmds.advertise,
	ewcfg.cmd_ads: cmds.ads_look,

}