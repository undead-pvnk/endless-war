from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # public transportation
    ewcfg.cmd_embark: cmds.embark,
    ewcfg.cmd_embark_alt1: cmds.embark,
    ewcfg.cmd_disembark: cmds.disembark,
    ewcfg.cmd_disembark_alt1: cmds.disembark,
    ewcfg.cmd_checkschedule: cmds.check_schedule,

}
