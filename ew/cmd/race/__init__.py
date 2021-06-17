from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Setting your race
    ewcfg.cmd_set_race: cmds.set_race,
    ewcfg.cmd_set_race_alt1: cmds.set_race,

    # Race flavor cmds
    ewcfg.cmd_exist: cmds.exist,
    ewcfg.cmd_ree: cmds.ree,
    ewcfg.cmd_autocannibalize: cmds.autocannibalize,
    ewcfg.cmd_autocannibalize_alt1: cmds.autocannibalize,
    ewcfg.cmd_rattle: cmds.rattle,
    ewcfg.cmd_beep: cmds.beep,
    ewcfg.cmd_yiff: cmds.yiff,
    ewcfg.cmd_hiss: cmds.hiss,
    ewcfg.cmd_jiggle: cmds.jiggle,
    ewcfg.cmd_flutter: cmds.flutter,
    ewcfg.cmd_request_petting: cmds.request_petting,
    ewcfg.cmd_request_petting_alt1: cmds.request_petting,
    ewcfg.cmd_rampage: cmds.rampage,
    ewcfg.cmd_entomize: cmds.entomize,
    ewcfg.cmd_confuse: cmds.confuse,

    # Fuck Shamblers
    ewcfg.cmd_shamble: cmds.shamble,

}
