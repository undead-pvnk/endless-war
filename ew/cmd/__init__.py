import ew.backend.hunting as bknd_hunt
import ew.static.cfg as ewcfg
import ew.utils.frontend as fe_utils
import ew.utils.poi as poi_utils
import ew.utils.rolemgr as ewrolemgr
from . import ads
from . import apt
from . import book
from . import casino
from . import cmds
from . import cosmeticitem
from . import debug
from . import district
from . import dungeons
from . import faction
from . import farm
from . import fish
from . import food
from . import hunting
from . import item
from . import juviecmd
from . import kingpin
from . import market
from . import move
from . import mutation
from . import quadrants
from . import race
from . import slimeoid
from . import slimetwitter
from . import smelting
from . import spooky
from . import sports
from . import transport
from . import wep

cmd_modules = [
    wep,
    apt,
    book,
    item,
    cmds,
    ads,
    casino,
    cosmeticitem,
    debug,
    district,
    slimeoid,
    move,
    market,
    spooky,
    transport,
    quadrants,
    mutation,
    race,
    farm,
    faction,
    fish,
    food,
    juviecmd,
    hunting,
    kingpin,
    slimetwitter,
    smelting,
    sports
]

cmd_map = {

    # kill all players in your district; could be re-used for a future raid boss
    # ewcfg.cmd_writhe: ewraidboss.writhe,

    # Enemies
    ewcfg.cmd_deleteallenemies: bknd_hunt.delete_all_enemies,

    # restores poi roles to their proper names, only usable by admins
    ewcfg.cmd_restoreroles: ewrolemgr.restoreRoleNames,

    # hides all poi role names, only usable by admins
    ewcfg.cmd_hiderolenames: ewrolemgr.hideRoleNames,

    # recreates all hidden poi roles in the server in case restoreRoleNames doesnt work, only usable by admins
    ewcfg.cmd_recreateroles: ewrolemgr.recreateRoles,

    # deletes all roles in the server of a particular type
    ewcfg.cmd_deleteroles: ewrolemgr.deleteRoles,

    # removes all user overwrites in the server's poi channels
    ewcfg.cmd_removeuseroverwrites: ewrolemgr.remove_user_overwrites,

    # Collects all channel topics.
    ewcfg.cmd_collectopics: fe_utils.collect_topics,

    # Changes those channel topics according to what's in their EwPoi definition
    ewcfg.cmd_synctopics: fe_utils.sync_topics,

    # Sets degradation values for GvS
    ewcfg.cmd_degradedistricts: poi_utils.degrade_districts,

}
dm_cmd_map = {}
apt_dm_cmd_map = {}

for mod in cmd_modules:
    try:
        cmd_map.update(mod.cmd_map)
    except:
        pass
    try:
        dm_cmd_map.update(mod.dm_cmd_map)
    except:
        pass
    try:
        apt_dm_cmd_map.update(mod.apt_dm_cmd_map)
    except:
        pass
