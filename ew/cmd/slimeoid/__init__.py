from ew.static import cfg as ewcfg
from . import slimeoidcmds
from . import slimeoid_creation

cmd_map = {

    # Making slimeoids
    ewcfg.cmd_instructions: slimeoid_creation.instructions,

    # Incubation
    ewcfg.cmd_incubateslimeoid:  slimeoid_creation.incubate_slimeoid,
    ewcfg.cmd_conjure_negaslimeoid: slimeoid_creation.incubate_negaslimeoid,
    ewcfg.cmd_conjure_negaslimeoid_alt1: slimeoid_creation.incubate_negaslimeoid,
    ewcfg.cmd_conjure_negaslimeoid_alt2: slimeoid_creation.incubate_negaslimeoid,
    ewcfg.cmd_conjure_negaslimeoid_alt3: slimeoid_creation.incubate_negaslimeoid,

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
    ewcfg.cmd_nameslimeoid_alt1:  slimeoid_creation.name_slimeoid,

    # Finish slimeoid creation
    ewcfg.cmd_spawnslimeoid:  slimeoid_creation.spawn_slimeoid,
    ewcfg.cmd_spawnslimeoid_alt1:  slimeoid_creation.spawn_slimeoid,

    # Destroy slimeoid
    ewcfg.cmd_destroyslimeoid: slimeoid_creation.destroy_slimeoid,
    ewcfg.cmd_destroyslimeoid_alt1: slimeoid_creation.destroy_slimeoid,



    

    # Interacting with slimeoids
    ewcfg.cmd_dissolveslimeoid: slimeoidcmds.dissolveslimeoid,
    ewcfg.cmd_dissolveslimeoid_alt1: slimeoidcmds.dissolveslimeoid,
    ewcfg.cmd_slimeoid: slimeoidcmds.slimeoid,
    ewcfg.cmd_slimeoid_alt1: slimeoidcmds.slimeoid,
    ewcfg.cmd_playfetch: slimeoidcmds.playfetch,
    ewcfg.cmd_petslimeoid: slimeoidcmds.petslimeoid,
    ewcfg.cmd_petslimeoid_alt1: slimeoidcmds.petslimeoid,
    ewcfg.cmd_abuseslimeoid: slimeoidcmds.abuseslimeoid,
    ewcfg.cmd_abuseslimeoid_alt1: slimeoidcmds.abuseslimeoid,
    ewcfg.cmd_walkslimeoid: slimeoidcmds.walkslimeoid,
    ewcfg.cmd_walkslimeoid_alt1: slimeoidcmds.walkslimeoid,
    ewcfg.cmd_observeslimeoid: slimeoidcmds.observeslimeoid,
    ewcfg.cmd_observeslimeoid_alt1: slimeoidcmds.observeslimeoid,
    ewcfg.cmd_slimeoidbattle: slimeoidcmds.slimeoidbattle,
    ewcfg.cmd_slimeoidbattle_alt1: slimeoidcmds.slimeoidbattle,
    ewcfg.cmd_slimeoidbattle_alt2: slimeoidcmds.slimeoidbattle,
    ewcfg.cmd_slimeoidbattle_alt3: slimeoidcmds.slimeoidbattle,
    ewcfg.cmd_saturateslimeoid: slimeoidcmds.saturateslimeoid,
    ewcfg.cmd_restoreslimeoid: slimeoidcmds.restoreslimeoid,
    ewcfg.cmd_restoreslimeoid_alt1: slimeoidcmds.restoreslimeoid,
    ewcfg.cmd_bottleslimeoid: slimeoidcmds.bottleslimeoid,
    ewcfg.cmd_bottleslimeoid_alt1: slimeoidcmds.bottleslimeoid,
    ewcfg.cmd_unbottleslimeoid: slimeoidcmds.unbottleslimeoid,
    ewcfg.cmd_unbottleslimeoid_alt1: slimeoidcmds.unbottleslimeoid,
    ewcfg.cmd_feedslimeoid: slimeoidcmds.feedslimeoid,
    ewcfg.cmd_feedslimeoid_alt1: slimeoidcmds.feedslimeoid,
    ewcfg.cmd_dress_slimeoid: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt1: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt2: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt3: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt4: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_dress_slimeoid_alt5: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_undress_slimeoid: slimeoidcmds.undress_slimeoid,
    ewcfg.cmd_undress_slimeoid_alt1: slimeoidcmds.undress_slimeoid,
    ewcfg.cmd_undress_slimeoid_alt2: slimeoidcmds.undress_slimeoid,
    ewcfg.cmd_undress_slimeoid_alt3: slimeoidcmds.undress_slimeoid,
    ewcfg.cmd_undress_slimeoid_alt4: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_undress_slimeoid_alt5: slimeoidcmds.dress_slimeoid,
    ewcfg.cmd_tagslimeoid: slimeoidcmds.tagslimeoid,
    ewcfg.cmd_tagslimeoid_alt1: slimeoidcmds.tagslimeoid,
    ewcfg.cmd_untagslimeoid: slimeoidcmds.untagslimeoid,
    ewcfg.cmd_untagslimeoid_alt1: slimeoidcmds.untagslimeoid,

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
