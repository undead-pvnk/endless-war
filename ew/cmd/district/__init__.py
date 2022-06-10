from ew.static import cfg as ewcfg
from . import districtcmds

cmd_map = {

    # Check your current POI capture progress
    ewcfg.cmd_capture_progress: districtcmds.capture_progress,

    # Change your current POI capture progress
    # ewcfg.cmd_annex: cmds.annex,
    # ewcfg.cmd_annex_alt1: cmds.annex,

    # Change and use your graffiti signature
    ewcfg.cmd_changespray: districtcmds.change_spray,
    ewcfg.cmd_tag: districtcmds.tag,

    ewcfg.cmd_blockparty: districtcmds.blockparty,
    ewcfg.cmd_hailcab: districtcmds.hailcab,

}

apt_dm_cmd_map = {

    # something with capping
    ewcfg.cmd_changespray: districtcmds.change_spray,
    ewcfg.cmd_tag: districtcmds.tag,

}

if ewcfg.dh_stage == 3 and ewcfg.dh_active:
    cmd_map[ewcfg.cmd_observe] = districtcmds.ufo_observe
    cmd_map[ewcfg.cmd_abduct] = districtcmds.abduct
    cmd_map[ewcfg.cmd_launch] = districtcmds.launch
    cmd_map[ewcfg.cmd_land] = districtcmds.launch
    cmd_map[ewcfg.cmd_beammeup] = districtcmds.beam_me_up
