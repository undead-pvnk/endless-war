from . import cmds
from .utils import *

cmd_map = {

    # public transportation
    ewcfg.cmd_embark: cmds.embark,
    ewcfg.cmd_embark_alt1: cmds.embark,
    ewcfg.cmd_disembark: cmds.disembark,
    ewcfg.cmd_disembark_alt1: cmds.disembark,
    ewcfg.cmd_checkschedule: cmds.check_schedule,

}
