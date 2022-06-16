from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from . import ads
from . import apt
from . import book
from . import casino
from . import cmds
from . import cosmeticitem
try:
    from ew.cmd import debug as ewdebug
except:
    from . import debug_dummy as ewdebug
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

from . import prank
try:
    from ew.cmd import debugr
except:
    from . import debugr_dummy as debugr

import ew.utils.frontend as fe_utils
import ew.utils.poi as poi_utils
import ew.utils.rolemgr as ewrolemgr

import ew.backend.hunting as bknd_hunt

import ew.static.cfg as ewcfg

cmd_modules = [
    wep,
    apt,
    book,
    item,
    cmds,
    ads,
    casino,
    cosmeticitem,
    ewdebug,
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
    sports,
    debugr,
    prank

]

cmd_map = {

    # Enemies
    ewcfg.cmd_deleteallenemies: bknd_hunt.delete_all_enemies,

    # removes all user overwrites in the server's poi channels
    ewcfg.cmd_removeuseroverwrites: ewrolemgr.remove_user_overwrites,

    # Collects all channel topics.
    ewcfg.cmd_collectopics: fe_utils.collect_topics,

    # Changes those channel topics according to what's in their EwPoi definition
    ewcfg.cmd_synctopics: fe_utils.sync_topics,

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
