from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Used for !accept/!refuse (put somewhere more general than apt?)
    ewcfg.cmd_haveastroke: cmds.nothing,
    ewcfg.cmd_moonhurtingbeam: cmds.nothing,
    ewcfg.cmd_rip: cmds.nothing,
    ewcfg.cmd_sign: cmds.nothing,

    # !retire
    ewcfg.cmd_retire: cmds.retire,

    # !depart (shouldnt this be in move?)
    ewcfg.cmd_depart: cmds.depart,

    # !consult
    ewcfg.cmd_consult: cmds.consult,

    # !signlease
    ewcfg.cmd_sign_lease: cmds.signlease,

    # !apartment
    ewcfg.cmd_apartment: cmds.apartment,

    # !udgrade
    ewcfg.cmd_upgrade: cmds.upgrade,

    # !knock
    ewcfg.cmd_knock: cmds.knock,

    # !trickortreat
    ewcfg.cmd_trickortreat: cmds.trickortreat,

    # !breaklease
    ewcfg.cmd_breaklease: cmds.cancel,

    # !pot (shouldn't this be with farming?)
    ewcfg.cmd_pot: cmds.flowerpot,

    # In server parsing of DM only commands.
    # This should be in a more general file,
    # maybe make a module (and separate map) for dm commands?

    # !releaseprop (isnt this a bazaar thing?)
    ewcfg.cmd_releaseprop: cmds.releaseprop,

    # !releasefish (why is it dm only to aquarium them anyway?)
    ewcfg.cmd_releasefish: cmds.releasefish,

    # !unpot (this can be done anywhere. why store in apt?)
    ewcfg.cmd_unpot: cmds.unpot,

    # !frame (consistency, cmon, why isnt this dm only too?)
    ewcfg.cmd_frame: cmds.frame,

    # !dyefurniture
    ewcfg.cmd_dyefurniture: cmds.dyefurniture,

    # !addkey
    ewcfg.cmd_addkey: cmds.add_key,

    # !changelocks
    ewcfg.cmd_changelocks: cmds.manual_changelocks,

    # !setalarm
    ewcfg.cmd_setalarm: cmds.set_alarm,

    # !jam (This is bassed on your current weapon. What does it have to do with apt?)
    ewcfg.cmd_jam: cmds.jam,

    # put your fish in your !aquarium
    ewcfg.cmd_aquarium: cmds.aquarium,

    # !propstand
    ewcfg.cmd_propstand: cmds.propstand,

    # !wash your clothes
    ewcfg.cmd_wash: cmds.wash,

    # !stow's aprtment variations, though !stow itself will call the version in cmd.py
    ewcfg.cmd_fridge: cmds.store_item,
    ewcfg.cmd_closet: cmds.store_item,
    ewcfg.cmd_decorate: cmds.store_item,
    ewcfg.cmd_shelve: cmds.store_item,
    ewcfg.cmd_shelve_alt_1: cmds.store_item,

    # !snag's apartment variations. Same deal as stow
    ewcfg.cmd_uncloset: cmds.remove_item,
    ewcfg.cmd_unfridge: cmds.remove_item,
    ewcfg.cmd_undecorate: cmds.remove_item,
    ewcfg.cmd_unshelve: cmds.remove_item,
    ewcfg.cmd_unshelve_alt_1: cmds.remove_item,

    # !watch, tv of course
    ewcfg.cmd_watch: cmds.watch,

    # !freeze and !unfreeze your slimeoid
    ewcfg.cmd_freeze: cmds.freeze,
    ewcfg.cmd_unfreeze: cmds.unfreeze,

    # !aptname/desc
    ewcfg.cmd_aptname: cmds.customize,
    ewcfg.cmd_aptdesc: cmds.customize,

    # !bootall
    ewcfg.cmd_bootall: cmds.bootall,

}

apt_dm_cmd_map = {

    # put your fish in your !aquarium
    ewcfg.cmd_aquarium: cmds.aquarium,

    # !propstand
    ewcfg.cmd_propstand: cmds.propstand,

    # !wash your clothes
    ewcfg.cmd_wash: cmds.wash,

    # !browse your bookshelf, or apartment
    ewcfg.cmd_browse: cmds.browse,

    # !stow's aprtment variations, though !stow itself will call the version in cmd.py outside of dms
    ewcfg.cmd_store: cmds.store_item,
    ewcfg.cmd_fridge: cmds.store_item,
    ewcfg.cmd_closet: cmds.store_item,
    ewcfg.cmd_decorate: cmds.store_item,
    ewcfg.cmd_shelve: cmds.store_item,
    ewcfg.cmd_shelve_alt_1: cmds.store_item,

    # !snag's apartment variations. Same deal as stow
    ewcfg.cmd_take: cmds.remove_item,
    ewcfg.cmd_uncloset: cmds.remove_item,
    ewcfg.cmd_unfridge: cmds.remove_item,
    ewcfg.cmd_undecorate: cmds.remove_item,
    ewcfg.cmd_unshelve: cmds.remove_item,
    ewcfg.cmd_unshelve_alt_1: cmds.remove_item,

    # !watch, tv of course
    ewcfg.cmd_watch: cmds.watch,

    # !freeze and !unfreeze your slimeoid
    ewcfg.cmd_freeze: cmds.freeze,
    ewcfg.cmd_unfreeze: cmds.unfreeze,

    # !aptname/desc
    ewcfg.cmd_aptname: cmds.customize,
    ewcfg.cmd_aptdesc: cmds.customize,

    # !bootall
    ewcfg.cmd_bootall: cmds.bootall,

    # !depart and !retire for some reason
    ewcfg.cmd_depart: cmds.depart,
    ewcfg.cmd_retire: cmds.depart,

    # !aptupgrade
    ewcfg.cmd_upgrade: cmds.upgrade,

    # !breaklease
    ewcfg.cmd_breaklease: cmds.cancel,

    # !look
    ewcfg.cmd_look: cmds.apt_look,

    # !knock
    ewcfg.cmd_knock: cmds.knock,

    # !trickortreat
    ewcfg.cmd_trickortreat: cmds.trickortreat,

    # !pot and !unpot
    ewcfg.cmd_pot: cmds.flowerpot,
    ewcfg.cmd_unpot: cmds.unpot,

    # !releaseprop (This literally cant be used in dms but I'm just porting what I see)
    ewcfg.cmd_releaseprop: cmds.releaseprop,

    # !releasefish
    ewcfg.cmd_releasefish: cmds.releasefish,

    # !apartment
    ewcfg.cmd_apartment: cmds.apartment,

    # !setalarm
    ewcfg.cmd_setalarm: cmds.set_alarm,

}
