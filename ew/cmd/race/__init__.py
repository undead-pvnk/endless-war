from ew.static import cfg as ewcfg
from . import racecmds

cmd_map = {

    # Setting your race
    ewcfg.cmd_set_race: racecmds.set_race,
    ewcfg.cmd_set_race_alt1: racecmds.set_race,

    # Race flavor cmds
    ewcfg.cmd_exist: racecmds.exist,
    ewcfg.cmd_ree: racecmds.ree,
    ewcfg.cmd_autocannibalize: racecmds.autocannibalize,
    ewcfg.cmd_autocannibalize_alt1: racecmds.autocannibalize,
    ewcfg.cmd_rattle: racecmds.rattle,
    ewcfg.cmd_beep: racecmds.beep,
    ewcfg.cmd_yiff: racecmds.yiff,
    ewcfg.cmd_hiss: racecmds.hiss,
    ewcfg.cmd_jiggle: racecmds.jiggle,
    ewcfg.cmd_flutter: racecmds.flutter,
    ewcfg.cmd_request_petting: racecmds.request_petting,
    ewcfg.cmd_request_petting_alt1: racecmds.request_petting,
    ewcfg.cmd_rampage: racecmds.rampage,
    ewcfg.cmd_entomize: racecmds.entomize,
    ewcfg.cmd_confuse: racecmds.confuse,

    # Fuck Shamblers
    ewcfg.cmd_shamble: racecmds.shamble,

    ewcfg.cmd_netrun: racecmds.netrun,
    ewcfg.cmd_strike_deal: racecmds.strike_deal,

}
