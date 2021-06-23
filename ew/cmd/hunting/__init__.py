from ew.static import cfg as ewcfg
from . import huntingcmds

cmd_map = {

    # Enemies
    ewcfg.cmd_summonenemy: huntingcmds.summonenemy,
    ewcfg.cmd_summongvsenemy: huntingcmds.summongvsenemy,

}
