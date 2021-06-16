from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # ads
    ewcfg.cmd_advertise: cmds.advertise,
    ewcfg.cmd_ads: cmds.ads_look,

}
