from ew.static import cfg as ewcfg
from . import sportscmds

cmd_map = {

    # slimeball
    ewcfg.cmd_slimeball: sportscmds.slimeball,
    ewcfg.cmd_slimeballgo: sportscmds.slimeballgo,
    ewcfg.cmd_slimeballstop: sportscmds.slimeballstop,
    ewcfg.cmd_slimeballleave: sportscmds.slimeballleave,

}
