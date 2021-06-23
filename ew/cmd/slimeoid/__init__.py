from ew.static import cfg as ewcfg
from . import slimeoidcmds

cmd_map = {

    # Making slimeoids
    ewcfg.cmd_incubateslimeoid: slimeoidcmds.incubateslimeoid,
    ewcfg.cmd_growbody: slimeoidcmds.growbody,
    ewcfg.cmd_growhead: slimeoidcmds.growhead,
    ewcfg.cmd_growlegs: slimeoidcmds.growlegs,
    ewcfg.cmd_growweapon: slimeoidcmds.growweapon,
    ewcfg.cmd_growarmor: slimeoidcmds.growarmor,
    ewcfg.cmd_growspecial: slimeoidcmds.growspecial,
    ewcfg.cmd_growbrain: slimeoidcmds.growbrain,
    ewcfg.cmd_nameslimeoid: slimeoidcmds.nameslimeoid,
    ewcfg.cmd_raisemoxie: slimeoidcmds.raisemoxie,
    ewcfg.cmd_lowermoxie: slimeoidcmds.lowermoxie,
    ewcfg.cmd_raisegrit: slimeoidcmds.raisegrit,
    ewcfg.cmd_lowergrit: slimeoidcmds.lowergrit,
    ewcfg.cmd_raisechutzpah: slimeoidcmds.raisechutzpah,
    ewcfg.cmd_lowerchutzpah: slimeoidcmds.lowerchutzpah,
    ewcfg.cmd_spawnslimeoid: slimeoidcmds.spawnslimeoid,
    ewcfg.cmd_dissolveslimeoid: slimeoidcmds.dissolveslimeoid,

    # Interacting with slimeoids
    ewcfg.cmd_slimeoid: slimeoidcmds.slimeoid,
    ewcfg.cmd_instructions: slimeoidcmds.instructions,
    ewcfg.cmd_playfetch: slimeoidcmds.playfetch,
    ewcfg.cmd_petslimeoid: slimeoidcmds.petslimeoid,
    ewcfg.cmd_abuseslimeoid: slimeoidcmds.abuseslimeoid,
    ewcfg.cmd_walkslimeoid: slimeoidcmds.walkslimeoid,
    ewcfg.cmd_observeslimeoid: slimeoidcmds.observeslimeoid,
    ewcfg.cmd_slimeoidbattle: slimeoidcmds.slimeoidbattle,
    ewcfg.cmd_saturateslimeoid: slimeoidcmds.saturateslimeoid,
    ewcfg.cmd_restoreslimeoid: slimeoidcmds.restoreslimeoid,
    ewcfg.cmd_bottleslimeoid: slimeoidcmds.bottleslimeoid,
    ewcfg.cmd_bottleslimeoid_alt1: slimeoidcmds.bottleslimeoid,
    ewcfg.cmd_unbottleslimeoid: slimeoidcmds.unbottleslimeoid,
    ewcfg.cmd_unbottleslimeoid_alt1: slimeoidcmds.unbottleslimeoid,
    ewcfg.cmd_feedslimeoid: slimeoidcmds.feedslimeoid,
    ewcfg.cmd_dress_slimeoid: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt1: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_undress_slimeoid: slimeoidcmds.undress_slimeoid,
    ewcfg.cmd_undress_slimeoid_alt1: slimeoidcmds.undress_slimeoid,

    # Negaslimeoids
    ewcfg.cmd_negaslimeoid: slimeoidcmds.negaslimeoid,
    ewcfg.cmd_battlenegaslimeoid: slimeoidcmds.negaslimeoidbattle,
    ewcfg.cmd_battlenegaslimeoid_alt1: slimeoidcmds.negaslimeoidbattle,
    ewcfg.cmd_battlenegaslimeoid_alt2: slimeoidcmds.negaslimeoidbattle,
    ewcfg.cmd_battlenegaslimeoid_alt3: slimeoidcmds.negaslimeoidbattle,

    # Ghosts can spawn a (mostly) randomly generated negaslimeoid
    ewcfg.cmd_summonnegaslimeoid: slimeoidcmds.summon_negaslimeoid,
    ewcfg.cmd_summonnegaslimeoid_alt1: slimeoidcmds.summon_negaslimeoid,
    ewcfg.cmd_summonnegaslimeoid_alt2: slimeoidcmds.summon_negaslimeoid,

}

apt_dm_cmd_map = {

    # !slimeoid, get its data
    ewcfg.cmd_slimeoid: slimeoidcmds.slimeoid,

    # !dressslimeoid
    ewcfg.cmd_dress_slimeoid: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt1: slimeoidcmds.dress_slimeoid,

    # interact with the slimeoid
    ewcfg.cmd_petslimeoid: slimeoidcmds.petslimeoid,
    ewcfg.cmd_abuseslimeoid: slimeoidcmds.abuseslimeoid,
    ewcfg.cmd_playfetch: slimeoidcmds.playfetch,
    ewcfg.cmd_observeslimeoid: slimeoidcmds.observeslimeoid,
    ewcfg.cmd_walkslimeoid: slimeoidcmds.walkslimeoid,

    # slimeoid storage
    ewcfg.cmd_bottleslimeoid: slimeoidcmds.bottleslimeoid,
    ewcfg.cmd_bottleslimeoid_alt1: slimeoidcmds.bottleslimeoid,
    ewcfg.cmd_unbottleslimeoid: slimeoidcmds.unbottleslimeoid,
    ewcfg.cmd_unbottleslimeoid_alt1: slimeoidcmds.unbottleslimeoid,

}
