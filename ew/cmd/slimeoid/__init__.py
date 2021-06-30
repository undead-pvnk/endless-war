from ew.static import cfg as ewcfg
from . import slimeoidcmds

cmd_map = {



    # Making slimeoids
    ewcfg.cmd_instructions: slimeoid_creation.instructions,

    # Incubation
    ewcfg.cmd_incubateslimeoid:  slimeoid_creation.incubate_slimeoid,

    # Grow body parts
    ewcfg.cmd_growbody:  slimeoid_creation.change_body_part,
    ewcfg.cmd_growhead:  slimeoid_creation.change_body_part,
    ewcfg.cmd_growlegs:  slimeoid_creation.change_body_part,
    ewcfg.cmd_growweapon:  slimeoid_creation.change_body_part,
    ewcfg.cmd_growarmor:  slimeoid_creation.change_body_part,
    ewcfg.cmd_growspecial:  slimeoid_creation.change_body_part,
    ewcfg.cmd_growbrain:  slimeoid_creation.change_body_part,
    
    # Change Stats
    ewcfg.cmd_raisemoxie:  slimeoid_creation.change_stat,
    ewcfg.cmd_lowermoxie:  slimeoid_creation.change_stat,
    ewcfg.cmd_raisegrit:  slimeoid_creation.change_stat,
    ewcfg.cmd_lowergrit:  slimeoid_creation.change_stat,
    ewcfg.cmd_raisechutzpah:  slimeoid_creation.change_stat,
    ewcfg.cmd_lowerchutzpah:  slimeoid_creation.change_stat,

    # Name slimeoid
    ewcfg.cmd_nameslimeoid:  slimeoid_creation.name_slimeoid,

    # Finish slimeoid creation
    ewcfg.cmd_spawnslimeoid:  slimeoid_creation.spawn_slimeoid,



    

    # Interacting with slimeoids
    ewcfg.cmd_dissolveslimeoid: slimeoidcmds.dissolveslimeoid,
    ewcfg.cmd_slimeoid: slimeoidcmds.slimeoid,
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
