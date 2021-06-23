from ew.static import cfg as ewcfg
from . import transportcmds

cmd_map = {

    # public transportation
    ewcfg.cmd_embark: transportcmds.embark,
    ewcfg.cmd_embark_alt1: transportcmds.embark,
    ewcfg.cmd_disembark: transportcmds.disembark,
    ewcfg.cmd_disembark_alt1: transportcmds.disembark,
    ewcfg.cmd_checkschedule: transportcmds.check_schedule,

}
