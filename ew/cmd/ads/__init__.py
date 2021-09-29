from ew.static import cfg as ewcfg
from . import adscmds

cmd_map = {

    # ads
    ewcfg.cmd_advertise: adscmds.advertise,
    ewcfg.cmd_ads: adscmds.ads_look,

}
