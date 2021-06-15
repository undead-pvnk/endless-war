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

cmd_map = {}
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