from . import cmds
from .utils import *
from ew.static import cfg as ewcfg

cmd_map = {

    # Making slimeoids
    ewcfg.cmd_incubateslimeoid: cmds.incubateslimeoid,
    ewcfg.cmd_growbody: cmds.growbody,
    ewcfg.cmd_growhead: cmds.growhead,
    ewcfg.cmd_growlegs: cmds.growlegs,
    ewcfg.cmd_growweapon: cmds.growweapon,
    ewcfg.cmd_growarmor: cmds.growarmor,
    ewcfg.cmd_growspecial: cmds.growspecial,
    ewcfg.cmd_growbrain: cmds.growbrain,
    ewcfg.cmd_nameslimeoid: cmds.nameslimeoid,
    ewcfg.cmd_raisemoxie: cmds.raisemoxie,
    ewcfg.cmd_lowermoxie: cmds.lowermoxie,
    ewcfg.cmd_raisegrit: cmds.raisegrit,
    ewcfg.cmd_lowergrit: cmds.lowergrit,
    ewcfg.cmd_raisechutzpah: cmds.raisechutzpah,
    ewcfg.cmd_lowerchutzpah: cmds.lowerchutzpah,
    ewcfg.cmd_spawnslimeoid: cmds.spawnslimeoid,
    ewcfg.cmd_dissolveslimeoid: cmds.dissolveslimeoid,

    # Interacting with slimeoids
    ewcfg.cmd_slimeoid: cmds.slimeoid,
    ewcfg.cmd_instructions: cmds.instructions,
    ewcfg.cmd_playfetch: cmds.playfetch,
    ewcfg.cmd_petslimeoid: cmds.petslimeoid,
    ewcfg.cmd_abuseslimeoid: cmds.abuseslimeoid,
    ewcfg.cmd_walkslimeoid: cmds.walkslimeoid,
    ewcfg.cmd_observeslimeoid: cmds.observeslimeoid,
    ewcfg.cmd_slimeoidbattle: cmds.slimeoidbattle,
    ewcfg.cmd_saturateslimeoid: cmds.saturateslimeoid,
    ewcfg.cmd_restoreslimeoid: cmds.restoreslimeoid,
    ewcfg.cmd_bottleslimeoid: cmds.bottleslimeoid,
    ewcfg.cmd_bottleslimeoid_alt1: cmds.bottleslimeoid,
    ewcfg.cmd_unbottleslimeoid: cmds.unbottleslimeoid,
    ewcfg.cmd_unbottleslimeoid_alt1: cmds.unbottleslimeoid,
    ewcfg.cmd_feedslimeoid: cmds.feedslimeoid,
    ewcfg.cmd_dress_slimeoid: cmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt1: cmds.dress_slimeoid,
    ewcfg.cmd_undress_slimeoid: cmds.undress_slimeoid,
    ewcfg.cmd_undress_slimeoid_alt1: cmds.undress_slimeoid,

    # Negaslimeoids
    ewcfg.cmd_negaslimeoid: cmds.negaslimeoid,
    ewcfg.cmd_battlenegaslimeoid: cmds.negaslimeoidbattle,
    ewcfg.cmd_battlenegaslimeoid_alt1: cmds.negaslimeoidbattle,
    ewcfg.cmd_battlenegaslimeoid_alt2: cmds.negaslimeoidbattle,
    ewcfg.cmd_battlenegaslimeoid_alt3: cmds.negaslimeoidbattle,

}

apt_dm_cmd_map = {

    # !slimeoid, get its data
    ewcfg.cmd_slimeoid: cmds.slimeoid,

    # !dressslimeoid
    ewcfg.cmd_dress_slimeoid: cmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt1: cmds.dress_slimeoid,

    # interact with the slimeoid
    ewcfg.cmd_petslimeoid: cmds.petslimeoid,
    ewcfg.cmd_abuseslimeoid: cmds.abuseslimeoid,
    ewcfg.cmd_playfetch: cmds.playfetch,
    ewcfg.cmd_observeslimeoid: cmds.observeslimeoid,
    ewcfg.cmd_walkslimeoid: cmds.walkslimeoid,

    # slimeoid storage
    ewcfg.cmd_bottleslimeoid: cmds.bottleslimeoid,
    ewcfg.cmd_bottleslimeoid_alt1: cmds.bottleslimeoid,
    ewcfg.cmd_unbottleslimeoid: cmds.unbottleslimeoid,
    ewcfg.cmd_unbottleslimeoid_alt1: cmds.unbottleslimeoid,

}