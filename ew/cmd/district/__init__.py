from ew.static import cfg as ewcfg
from . import districtcmds

cmd_map = {

    # Check your current POI capture progress
    #ewcfg.cmd_capture_progress: districtcmds.capture_progress,

    # Change your current POI capture progress
    # ewcfg.cmd_annex: cmds.annex,
    # ewcfg.cmd_annex_alt1: cmds.annex,

    # Change and use your graffiti signature
    ewcfg.cmd_changespray: districtcmds.change_spray,
    ewcfg.cmd_tag: districtcmds.tag,

    # Gankers Vs. Shamblers gang swapping
    # ewcfg.cmd_shamble: cmds.shamble,
    # ewcfg.cmd_rejuvenate: cmds.rejuvenate,

}

apt_dm_cmd_map = {

    # something with capping
    ewcfg.cmd_changespray: districtcmds.change_spray,
    ewcfg.cmd_tag: districtcmds.tag,

}
