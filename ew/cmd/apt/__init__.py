from ew.static import cfg as ewcfg
from . import aptcmds

cmd_map = {

    # Used for accepting contracts
    ewcfg.cmd_rip: aptcmds.nothing,
    ewcfg.cmd_sign: aptcmds.nothing,

    # !retire
    ewcfg.cmd_retire: aptcmds.retire,

    # !depart (shouldnt this be in move?)
    ewcfg.cmd_depart: aptcmds.depart,

    # !consult
    ewcfg.cmd_consult: aptcmds.consult,

    # !signlease
    ewcfg.cmd_sign_lease: aptcmds.signlease,

    # !apartment
    ewcfg.cmd_apartment: aptcmds.apartment,

    # !udgrade
    ewcfg.cmd_upgrade: aptcmds.upgrade,

    # !knock
    ewcfg.cmd_knock: aptcmds.knock,

    # !trickortreat
    ewcfg.cmd_trickortreat: aptcmds.trickortreat,

    # !breaklease
    ewcfg.cmd_breaklease: aptcmds.cancel,

    # !frame -- flavors item, move to item?
    ewcfg.cmd_frame: aptcmds.frame,

    # !dyefurniture -- flavors item, move to item?
    ewcfg.cmd_dyefurniture: aptcmds.dyefurniture,

    # !addkey
    ewcfg.cmd_addkey: aptcmds.add_key,

    # !changelocks
    ewcfg.cmd_changelocks: aptcmds.manual_changelocks,

    # !setalarm -- What do alarms have to do with apt specifically?
    ewcfg.cmd_setalarm: aptcmds.set_alarm,

    # !wash your clothes
    ewcfg.cmd_wash: aptcmds.wash,

    # !stow's aprtment variations, though !stow itself will call the version in item.py
    ewcfg.cmd_fridge: aptcmds.store_item,
    ewcfg.cmd_closet: aptcmds.store_item,
    ewcfg.cmd_decorate: aptcmds.store_item,
    ewcfg.cmd_shelve: aptcmds.store_item,
    ewcfg.cmd_shelve_alt_1: aptcmds.store_item,

    # !snag's apartment variations. Same deal as stow
    ewcfg.cmd_uncloset: aptcmds.remove_item,
    ewcfg.cmd_unfridge: aptcmds.remove_item,
    ewcfg.cmd_undecorate: aptcmds.remove_item,
    ewcfg.cmd_unshelve: aptcmds.remove_item,
    ewcfg.cmd_unshelve_alt_1: aptcmds.remove_item,

    # !watch, tv of course
    ewcfg.cmd_watch: aptcmds.watch,

    # !freeze and !unfreeze your slimeoid
    ewcfg.cmd_freeze: aptcmds.freeze,
    ewcfg.cmd_unfreeze: aptcmds.unfreeze,

    # !aptname/desc
    ewcfg.cmd_aptname: aptcmds.customize,
    ewcfg.cmd_aptdesc: aptcmds.customize,

    # !bootall
    ewcfg.cmd_bootall: aptcmds.bootall,

}

apt_dm_cmd_map = {

    # !wash your clothes
    ewcfg.cmd_wash: aptcmds.wash,

    # !browse your bookshelf, or apartment
    ewcfg.cmd_browse: aptcmds.browse,

    # !stow and it's apt exclusive variants
    ewcfg.cmd_store: aptcmds.store_item,
    ewcfg.cmd_fridge: aptcmds.store_item,
    ewcfg.cmd_closet: aptcmds.store_item,
    ewcfg.cmd_decorate: aptcmds.store_item,
    ewcfg.cmd_shelve: aptcmds.store_item,
    ewcfg.cmd_shelve_alt_1: aptcmds.store_item,

    # !snag and it's apt exclusive variants
    ewcfg.cmd_take: aptcmds.remove_item,
    ewcfg.cmd_uncloset: aptcmds.remove_item,
    ewcfg.cmd_unfridge: aptcmds.remove_item,
    ewcfg.cmd_undecorate: aptcmds.remove_item,
    ewcfg.cmd_unshelve: aptcmds.remove_item,
    ewcfg.cmd_unshelve_alt_1: aptcmds.remove_item,

    # !watch, tv of course
    ewcfg.cmd_watch: aptcmds.watch,

    # !freeze and !unfreeze your slimeoid
    ewcfg.cmd_freeze: aptcmds.freeze,
    ewcfg.cmd_unfreeze: aptcmds.unfreeze,

    # !aptname/desc
    ewcfg.cmd_aptname: aptcmds.customize,
    ewcfg.cmd_aptdesc: aptcmds.customize,

    # !bootall
    ewcfg.cmd_bootall: aptcmds.bootall,

    # !depart and !retire for some reason
    ewcfg.cmd_depart: aptcmds.depart,
    ewcfg.cmd_retire: aptcmds.depart,

    # !aptupgrade
    ewcfg.cmd_upgrade: aptcmds.upgrade,

    # !breaklease
    ewcfg.cmd_breaklease: aptcmds.cancel,

    # !look
    ewcfg.cmd_look: aptcmds.apt_look,

    # !knock
    ewcfg.cmd_knock: aptcmds.knock,

    # !trickortreat
    ewcfg.cmd_trickortreat: aptcmds.trickortreat,

    # !apartment
    ewcfg.cmd_apartment: aptcmds.apartment,

    # !setalarm
    ewcfg.cmd_setalarm: aptcmds.set_alarm,

}
