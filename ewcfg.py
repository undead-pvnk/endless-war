import random

from ewcosmeticitem import EwCosmeticItem
from ewwep import EwWeapon
from ewweather import EwWeather
from ewfood import EwFood
from ewitem import EwItemDef, EwDefaultItem
from ewmap import EwPoi
from ewslimeoid import EwBody, EwHead, EwMobility, EwOffense, EwDefense, EwSpecial, EwBrain, EwHue
from ewquadrants import EwQuadrantFlavor
from ewtransport import EwTransportLine

# Global configuration options.
version = "v3.3"
dir_msgqueue = 'msgqueue'

# Update intervals
update_hookstillactive = 60 * 60 * 3
update_twitch = 60
update_pvp = 60
update_market = 900 #15 min

# Time saved moving through friendly territory (or lost in hostile territory).
territory_time_gain = 5

# Market delta
max_iw_swing = 30

# Life states. How the player is living (or deading) in the database
life_state_corpse = 0
life_state_juvenile = 1
life_state_enlisted = 2
life_state_grandfoe = 8
life_state_kingpin = 10
life_state_observer = 20

slimeoid_tick_length = 5 * 60 #5 minutes

# slimeoid life states
slimeoid_state_none = 0
slimeoid_state_forming = 1
slimeoid_state_active = 2
slimeoid_state_stored = 3

# slimeoid types
sltype_lab = 'Lab'
sltype_nega = 'Nega'
sltype_wild = 'Wild'

# slimeoid battle types
battle_type_arena = 0
battle_type_nega = 1

# ID tags for points of interest that are needed in code.
poi_id_thesewers = "thesewers"
poi_id_slimeoidlab = "slimecorpslimeoidlaboratory"
poi_id_mine = "themines"
poi_id_thecasino = "thecasino"
poi_id_711 = "outsidethe711"
poi_id_speakeasy = "thekingswifessonspeakeasy"
poi_id_dojo = "thedojo"
poi_id_arena = "thebattlearena"
poi_id_nlacu = "newlosangelescityuniversity"
poi_id_foodcourt = "thefoodcourt"
poi_id_cinema = "nlacakanmcinemas"
poi_id_bazaar = "thebazaar"
poi_id_stockexchange = "theslimestockexchange"
poi_id_endlesswar = "endlesswar"
poi_id_slimecorphq = "slimecorphq"
poi_id_cv_mines = "cratersvillemines"
poi_id_tt_mines = "toxingtonmines"
poi_id_diner = "smokerscough"
poi_id_seafood = "redmobster"
poi_id_jr_farms = "juviesrowfarms"
poi_id_og_farms = "oozegardensfarms"
poi_id_ab_farms = "arsonbrookfarms"
poi_id_neomilwaukeestate = "neomilwaukeestate"
poi_id_beachresort = "thebeachresort"
poi_id_countryclub = "thecountryclub"
poi_id_slimesea = "slimesea"

# transports
poi_id_ferry = "ferry"
poi_id_subway_red01 = "subwayred01"
poi_id_subway_red02 = "subwayred02"
poi_id_subway_yellow01 = "subwayyellow01"
poi_id_subway_yellow02 = "subwayyellow02"
poi_id_subway_green01 = "subwaygreen01"
poi_id_subway_green02 = "subwaygreen02"
poi_id_subway_white01 = "subwaywhite01"
poi_id_subway_blue01 = "subwayblue01"
poi_id_subway_blue02 = "subwayblue02"
poi_id_blimp = "blimp"


# ferry ports
poi_id_wt_port = "wreckingtonport"
poi_id_vc_port = "vagrantscornerport"

# subway stations
poi_id_tt_subway_station = "toxingtonsubwaystation"
poi_id_ah_subway_station = "astatineheightssubwaystation"
poi_id_gd_subway_station = "gatlingsdalesubwaystation"
poi_id_ck_subway_station = "copkilltownsubwaystation"
poi_id_ab_subway_station = "arsonbrooksubwaystation"
poi_id_sb_subway_station = "smogsburgsubwaystation"
poi_id_dt_subway_station = "downtownsubwaystation"
poi_id_kb_subway_station = "krakbaysubwaystation"
poi_id_gb_subway_station = "glocksburysubwaystation"
poi_id_wgb_subway_station = "westglocksburysubwaystation"
poi_id_jp_subway_station = "jaywalkerplainsubwaystation"
poi_id_nsb_subway_station = "northsleezesubwaystation"
poi_id_ssb_subway_station = "southsleezesubwaystation"
poi_id_cv_subway_station = "cratersvillesubwaystation"
poi_id_wt_subway_station = "wreckingtonsubwaystation"
poi_id_rr_subway_station = "rowdyroughhousesubwaystation"
poi_id_gld_subway_station = "greenlightsubwaystation"
poi_id_jr_subway_station = "juviesrowsubwaystation"
poi_id_vc_subway_station = "vagrantscornersubwaystation"
poi_id_afb_subway_station = "assaultflatssubwaystation"

# ferry ports
poi_id_df_blimp_tower = "dreadfordblimptower"
poi_id_afb_blimp_tower = "assaultflatsblimptower"

# district pois
poi_id_downtown = "downtown"
poi_id_smogsburg = "smogsburg"
poi_id_copkilltown = "copkilltown"
poi_id_krakbay = "krakbay"
poi_id_poudrinalley = "poudrinalley"
poi_id_rowdyroughhouse = "rowdyroughhouse"
poi_id_greenlightdistrict = "greenlightdistrict"
poi_id_oldnewyonkers = "oldnewyonkers"
poi_id_littlechernobyl = "littlechernobyl"
poi_id_arsonbrook = "arsonbrook"
poi_id_astatineheights = "astatineheights"
poi_id_gatlingsdale = "gatlingsdale"
poi_id_vandalpark = "vandalpark"
poi_id_glocksbury = "glocksbury"
poi_id_northsleezeborough = "northsleezeborough"
poi_id_southsleezeborough = "southsleezeborough"
poi_id_oozegardens = "oozegardens"
poi_id_cratersville = "cratersville"
poi_id_wreckington = "wreckington"
poi_id_juviesrow = "juviesrow"
poi_id_slimesend = "slimesend"
poi_id_vagrantscorner = "vagrantscorner"
poi_id_assaultflatsbeach = "assaultflatsbeach"
poi_id_newnewyonkers = "newnewyonkers"
poi_id_brawlden = "brawlden"
poi_id_toxington = "toxington"
poi_id_charcoalpark = "charcoalpark"
poi_id_poloniumhill = "poloniumhill"
poi_id_westglocksbury = "westglocksbury"
poi_id_jaywalkerplain = "jaywalkerplain"
poi_id_crookline = "crookline"
poi_id_dreadford = "dreadford"

# Transport types
transport_type_ferry = "ferry"
transport_type_subway = "subway"
transport_type_blimp = "blimp"

# Ferry lines
transport_line_ferry_wt_to_vc = "ferrywttovc"
transport_line_ferry_vc_to_wt = "ferryvctowt"

# Subway lines
transport_line_subway_yellow_northbound = "subwayyellownorth"
transport_line_subway_yellow_southbound = "subwayyellowsouth"
transport_line_subway_red_northbound = "subwayrednorth"
transport_line_subway_red_southbound = "subwayredsouth"
transport_line_subway_blue_eastbound = "subwayblueeast"
transport_line_subway_blue_westbound = "subwaybluewest"
transport_line_subway_white_eastbound = "subwaywhiteeast"
transport_line_subway_white_westbound = "subwaywhitewest"
transport_line_subway_green_eastbound = "subwaygreeneast"
transport_line_subway_green_westbound = "subwaygreenwest"

# Blimp lines
transport_line_blimp_df_to_afb = "blimpdftoafb"
transport_line_blimp_afb_to_df = "blimpafbtodf"


# Role names. All lower case with no spaces.
role_juvenile = "juveniles"
role_juvenile_pvp = "juvenilepvp"
role_rowdyfucker = "rowdyfucker"
role_rowdyfuckers = "rowdys"
role_rowdyfuckers_pvp = "rowdypvp"
role_copkiller = "copkiller"
role_copkillers = "killers"
role_copkillers_pvp = "killerpvp"
role_corpse = "corpse"
role_corpse_pvp = "corpsepvp"
role_kingpin = "kingpin"
role_grandfoe = "grandfoe"

faction_roles = [
	role_juvenile,
	role_juvenile_pvp,
	role_rowdyfucker,
	role_rowdyfuckers,
	role_rowdyfuckers_pvp,
	role_copkiller,
	role_copkillers,
	role_copkillers_pvp,
	role_corpse,
	role_corpse_pvp,
	role_kingpin,
	role_grandfoe
	]

role_to_pvp_role = {
	role_juvenile : role_juvenile_pvp,
	role_rowdyfuckers : role_rowdyfuckers_pvp,
	role_copkillers : role_copkillers_pvp,
	role_corpse : role_corpse_pvp
	}

# Faction names and bases
faction_killers = "killers"
gangbase_killers = "Cop Killtown"
faction_rowdys = "rowdys"
gangbase_rowdys = "Rowdy Roughhouse"
faction_banned = "banned"
factions = [faction_killers, faction_rowdys]

# Channel names
channel_mines = "the-mines"
channel_downtown = "downtown"
channel_combatzone = "combat-zone"
channel_endlesswar = "endless-war"
channel_sewers = "the-sewers"
channel_dojo = "the-dojo"
channel_twitch_announcement = "rfck-chat"
channel_casino = "slime-casino"
channel_stockexchange = "slimecorp-stock-exchange"
channel_foodcourt = "food-court"
channel_slimeoidlab = "slimecorp-labs"
channel_711 = "outside-the-7-11"
channel_speakeasy = "speakeasy"
channel_arena = "battle-arena"
channel_nlacu = "nlac-university"
channel_cinema = "nlacakanm-cinemas"
channel_bazaar = "bazaar"
channel_slimecorphq = "slimecorp-hq"
channel_leaderboard = "leaderboard"
channel_cv_mines = "cratersville-mines"
channel_tt_mines = "toxington-mines"
channel_diner = "smokers-cough"
channel_seafood = "red-mobster"
channel_jr_farms = "juvies-row-farms"
channel_og_farms = "ooze-gardens-farms"
channel_ab_farms = "arsonbrook-farms"
channel_neomilwaukeestate = "neo-milwaukee-state"
channel_beachresort = "the-resort"
channel_countryclub = "the-country-club"
channel_rowdyroughhouse = "rowdy-roughhouse"
channel_copkilltown = "cop-killtown"
channel_slimesea = "slime-sea"

channel_wt_port = "wreckington-port"
channel_vc_port = "vagrants-corner-port"
channel_tt_subway_station = "toxington-subway-station"
channel_ah_subway_station = "astatine-heights-subway-station"
channel_gd_subway_station = "gatlingsdale-subway-station"
channel_ck_subway_station = "cop-killtown-subway-station"
channel_ab_subway_station = "arsonbrook-subway-station"
channel_sb_subway_station = "smogsburg-subway-station"
channel_dt_subway_station = "downtown-subway-station"
channel_kb_subway_station = "krak-bay-subway-station"
channel_gb_subway_station = "glocksbury-subway-station"
channel_wgb_subway_station = "west-glocksbury-subway-station"
channel_jp_subway_station = "jaywalker-plain-subway-station"
channel_nsb_subway_station = "north-sleeze-subway-station"
channel_ssb_subway_station = "south-sleeze-subway-station"
channel_cv_subway_station = "cratersville-subway-station"
channel_wt_subway_station = "wreckington-subway-station"
channel_rr_subway_station = "rowdy-roughhouse-subway-station"
channel_gld_subway_station = "green-light-subway-station"
channel_jr_subway_station = "juvies-row-subway-station"
channel_vc_subway_station = "vagrants-corner-subway-station"
channel_afb_subway_station = "assault-flats-subway-station"
channel_df_blimp_tower = "dreadford-blimp-tower"
channel_afb_blimp_tower = "assault-flats-blimp-tower"

channel_ferry = "ferry"
channel_subway_red01 = "subway-train-r-01"
channel_subway_red02 = "subway-train-r-02"
channel_subway_yellow01 = "subway-train-y-01"
channel_subway_yellow02 = "subway-train-y-02"
channel_subway_green01 = "subway-train-g-01"
channel_subway_green02 = "subway-train-g-02"
channel_subway_white01 = "subway-train-w-01"
channel_subway_blue01 = "subway-train-b-01"
channel_subway_blue02 = "subway-train-b-02"
channel_blimp = "blimp"

channel_killfeed = "kill-feed"

hideout_channels = [channel_rowdyroughhouse, channel_copkilltown]
hideout_by_faction = {
	faction_rowdys: channel_rowdyroughhouse,
	faction_killers: channel_copkilltown
}

# Commands
cmd_prefix = '!'
cmd_enlist = cmd_prefix + 'enlist'
cmd_renounce = cmd_prefix + 'renounce'
cmd_revive = cmd_prefix + 'revive'
cmd_kill = cmd_prefix + 'kill'
cmd_shoot = cmd_prefix + 'shoot'
cmd_shoot_alt1 = cmd_prefix + 'bonk'
cmd_shoot_alt2 = cmd_prefix + 'pat'
cmd_attack = cmd_prefix + 'attack'
cmd_devour = cmd_prefix + 'devour'
cmd_mine = cmd_prefix + 'mine'
cmd_score = cmd_prefix + 'slimes'
cmd_score_alt1 = cmd_prefix + 'slime'
cmd_giveslime = cmd_prefix + 'giveslime'
cmd_giveslime_alt1 = cmd_prefix + 'giveslimes'
cmd_help = cmd_prefix + 'help'
cmd_help_alt1 = cmd_prefix + 'command'
cmd_help_alt2 = cmd_prefix + 'commands'
cmd_help_alt3 = cmd_prefix + 'guide'
cmd_harvest = cmd_prefix + 'harvest'
cmd_salute = cmd_prefix + 'salute'
cmd_unsalute = cmd_prefix + 'unsalute'
cmd_hurl = cmd_prefix + 'hurl'
cmd_spar = cmd_prefix + 'spar'
cmd_suicide = cmd_prefix + 'suicide'
cmd_suicide_alt1 = cmd_prefix + 'seppuku'
cmd_suicide_alt2 = cmd_prefix + 'sudoku'
cmd_haunt = cmd_prefix + 'haunt'
cmd_summonnegaslimeoid = cmd_prefix + 'summon'
cmd_negaslimeoid = cmd_prefix + 'negaslimeoid'
cmd_battlenegaslimeoid = cmd_prefix + 'battlenegaslimeoid'
cmd_slimepachinko = cmd_prefix + 'slimepachinko'
cmd_slimeslots = cmd_prefix + 'slimeslots'
cmd_slimecraps = cmd_prefix + 'slimecraps'
cmd_slimeroulette = cmd_prefix + 'slimeroulette'
cmd_slimebaccarat = cmd_prefix + 'slimebaccarat'
cmd_slimeskat = cmd_prefix + 'slimeskat'
cmd_slimeskat_join = cmd_prefix + 'skatjoin'
cmd_slimeskat_decline = cmd_prefix + 'skatdecline'
cmd_slimeskat_bid = cmd_prefix + 'skatbid'
cmd_slimeskat_call = cmd_prefix + 'skatcall'
cmd_slimeskat_pass = cmd_prefix + 'skatpass'
cmd_slimeskat_play = cmd_prefix + 'skatplay'
cmd_slimeskat_hearts = cmd_prefix + 'skathearts'
cmd_slimeskat_slugs = cmd_prefix + 'skatslugs'
cmd_slimeskat_hats = cmd_prefix + 'skathats'
cmd_slimeskat_shields = cmd_prefix + 'skatshields'
cmd_slimeskat_grand = cmd_prefix + 'skatgrand'
cmd_slimeskat_null = cmd_prefix + 'skatnull'
cmd_slimeskat_take = cmd_prefix + 'skattake'
cmd_slimeskat_hand = cmd_prefix + 'skathand'
cmd_slimeskat_choose = cmd_prefix + 'skatchoose'
cmd_deadmega = cmd_prefix + 'deadmega'
cmd_donate = cmd_prefix + 'donate'
cmd_slimecoin = cmd_prefix + 'slimecoin'
cmd_slimecoin_alt1 = cmd_prefix + 'slimecredit'
cmd_slimecoin_alt2 = cmd_prefix + 'coin'
cmd_slimecoin_alt3 = cmd_prefix + 'sc'
cmd_invest = cmd_prefix + 'invest'
cmd_withdraw = cmd_prefix + 'withdraw'
cmd_exchangerate = cmd_prefix + 'exchangerate'
cmd_exchangerate_alt1 = cmd_prefix + 'exchange'
cmd_exchangerate_alt2 = cmd_prefix + 'rate'
cmd_exchangerate_alt3 = cmd_prefix + 'exchangerates'
cmd_exchangerate_alt4 = cmd_prefix + 'rates'
cmd_shares = cmd_prefix + 'shares'
cmd_stocks = cmd_prefix + 'stocks'
cmd_negaslime = cmd_prefix + 'negaslime'
cmd_equip = cmd_prefix + 'equip'
cmd_data = cmd_prefix + 'data'
cmd_clock = cmd_prefix + 'clock'
cmd_time = cmd_prefix + 'time'
cmd_weather = cmd_prefix + 'weather'
cmd_patchnotes = cmd_prefix + 'patchnotes'
cmd_howl = cmd_prefix + 'howl'
cmd_howl_alt1 = cmd_prefix + '56709'
cmd_transfer = cmd_prefix + 'transfer'
cmd_transfer_alt1 = cmd_prefix + 'xfer'
cmd_menu = cmd_prefix + 'menu'
cmd_order = cmd_prefix + 'order'
cmd_annoint = cmd_prefix + 'annoint'
cmd_annoint_alt1 = cmd_prefix + 'anoint'
cmd_disembody = cmd_prefix + 'disembody'
cmd_war = cmd_prefix + 'war'
cmd_toil = cmd_prefix + 'toil'
cmd_inventory = cmd_prefix + 'inventory'
cmd_inventory_alt1 = cmd_prefix + 'inv'
cmd_inventory_alt2 = cmd_prefix + 'stuff'
cmd_inventory_alt3 = cmd_prefix + 'bag'
cmd_move = cmd_prefix + 'move'
cmd_move_alt1 = cmd_prefix + 'goto'
cmd_move_alt2 = cmd_prefix + 'walk'
cmd_move_alt3 = cmd_prefix + 'sny'
cmd_halt = cmd_prefix + 'halt'
cmd_halt_alt1 = cmd_prefix + 'stop'
cmd_embark = cmd_prefix + 'embark'
cmd_embark_alt1 = cmd_prefix + 'board'
cmd_disembark = cmd_prefix + 'disembark'
cmd_disembark_alt1 = cmd_prefix + 'alight'
cmd_checkschedule = cmd_prefix + 'schedule'
cmd_inspect = cmd_prefix + 'inspect'
cmd_inspect_alt1 = cmd_prefix + 'examine'
cmd_look = cmd_prefix + 'look'
cmd_scout = cmd_prefix + 'scout'
cmd_map = cmd_prefix + 'map'
cmd_wiki = cmd_prefix + 'wiki'
cmd_booru = cmd_prefix + 'booru'
cmd_pardon = cmd_prefix + 'pardon'
cmd_banish = cmd_prefix + 'banish'
cmd_writhe = cmd_prefix + 'writhe'
cmd_use = cmd_prefix + 'use'
cmd_news = cmd_prefix + 'news'
cmd_buy = cmd_prefix + 'buy'
cmd_thrash = cmd_prefix + 'thrash'
cmd_dab = cmd_prefix + 'dab'
cmd_russian = cmd_prefix + 'russianroulette'
cmd_accept = cmd_prefix + 'accept'
cmd_refuse = cmd_prefix + 'refuse'
cmd_reap = cmd_prefix + 'reap'
cmd_sow = cmd_prefix + 'sow'
cmd_mill = cmd_prefix + 'mill'
cmd_smelt = cmd_prefix + 'smelt'
cmd_adorn = cmd_prefix + 'adorn'
cmd_create = cmd_prefix + 'create'
cmd_give = cmd_prefix + 'give'
cmd_discard = cmd_prefix + 'discard'
cmd_discard_alt1 = cmd_prefix + 'drop'
cmd_leaderboard = cmd_prefix + 'leaderboard'
cmd_leaderboard_alt1 = cmd_prefix + 'leaderboards'
cmd_marry = cmd_prefix + 'marry'
cmd_divorce = cmd_prefix + 'divorce'
cmd_scavenge = cmd_prefix + 'scavenge'
cmd_arm = cmd_prefix + 'arm'
cmd_arsenalize = cmd_prefix + 'arsenalize'
cmd_capture_progress = cmd_prefix + 'progress'
cmd_quarterly_report = cmd_prefix + 'quarterlyreport'

cmd_restoreroles = cmd_prefix + 'restoreroles'

#slimeoid commands
cmd_incubateslimeoid = cmd_prefix + 'incubateslimeoid'
cmd_growbody = cmd_prefix + 'growbody'
cmd_growhead = cmd_prefix + 'growhead'
cmd_growlegs = cmd_prefix + 'growlegs'
cmd_growweapon = cmd_prefix + 'growweapon'
cmd_growarmor = cmd_prefix + 'growarmor'
cmd_growspecial = cmd_prefix + 'growspecial'
cmd_growbrain = cmd_prefix + 'growbrain'
cmd_nameslimeoid = cmd_prefix + 'nameslimeoid'
cmd_raisemoxie = cmd_prefix + 'raisemoxie'
cmd_lowermoxie = cmd_prefix + 'lowermoxie'
cmd_raisegrit = cmd_prefix + 'raisegrit'
cmd_lowergrit = cmd_prefix + 'lowergrit'
cmd_raisechutzpah = cmd_prefix + 'raisechutzpah'
cmd_lowerchutzpah = cmd_prefix + 'lowerchutzpah'
cmd_spawnslimeoid = cmd_prefix + 'spawnslimeoid'
cmd_dissolveslimeoid = cmd_prefix + 'dissolveslimeoid'
cmd_slimeoid = cmd_prefix + 'slimeoid'
cmd_challenge = cmd_prefix + 'challenge'
cmd_instructions = cmd_prefix + 'instructions'
cmd_playfetch = cmd_prefix + 'playfetch'
cmd_petslimeoid = cmd_prefix + 'petslimeoid'
cmd_walkslimeoid = cmd_prefix + 'walkslimeoid'
cmd_observeslimeoid = cmd_prefix + 'observeslimeoid'
cmd_slimeoidbattle = cmd_prefix + 'slimeoidbattle'
cmd_saturateslimeoid = cmd_prefix + 'saturateslimeoid'

cmd_add_quadrant = cmd_prefix + "addquadrant"
cmd_get_quadrants = cmd_prefix + "quadrants"
cmd_get_flushed = cmd_prefix + "flushed"
cmd_get_flushed_alt1 = cmd_prefix + "matesprit"
cmd_get_pale = cmd_prefix + "pale"
cmd_get_pale_alt1 = cmd_prefix + "moirail"
cmd_get_caliginous = cmd_prefix + "caliginous"
cmd_get_caliginous_alt1 = cmd_prefix + "kismesis"
cmd_get_ashen = cmd_prefix + "ashen"
cmd_get_ashen_alt1 = cmd_prefix + "auspistice"

# Slime costs/values
slimes_onrevive = 20
slimes_onrevive_everyone = 20
slimes_toenlist = 50000
slimes_perspar_base = 0
slimes_hauntratio = 400
slimes_hauntmax = 20000
slimes_perslot = 100
slimes_perpachinko = 500
slimecoin_exchangerate = 100
slimes_permill = 75000

# hunger
min_stamina = 100
hunger_pershot = 10
hunger_perspar = 30
hunger_perfarm = 50
hunger_permine = 1
hunger_perscavenge = 2
hunger_pertick = 3

#inebriation
inebriation_max = 20
inebriation_pertick = 2

# max item amounts
max_food_in_inv_mod = 8  # modifier for how much food you can carry. the player's slime level is divided by this number to calculate the number of carriable food items
max_adorn_mod = 4
max_weapon_mod = 16

# price multipliers
togo_price_increase = 2

# standard food expiration in seconds
std_food_expir = 12 * 3600  # 12 hours
farm_food_expir = 12 * 3600 * 4 # 2 days
milled_food_expir = 12 * 3600 * 28 # 2 weeks

# property classes
property_class_s = "s"
property_class_a = "a"
property_class_b = "b"
property_class_c = "c"

# district capturing
capture_tick_length = 10  # in seconds; also affects how much progress is made per tick
max_capture_points_s = 4915  # 90 min
max_capture_points_a = 3277  # 60 min
max_capture_points_b = 2458  # 45 min
max_capture_points_c = 1638   # 30 min

# district capture rates assigned to property classes
max_capture_points = {
	property_class_s: max_capture_points_s,
	property_class_a: max_capture_points_a,
	property_class_b: max_capture_points_b,
	property_class_c: max_capture_points_c
}

# capture messages
capture_milestone = 5  # after how many percent of progress the players are notified of the progress

# capture speed at 0% progress
baseline_capture_speed = 2

# accelerates capture speed depending on current progress
capture_gradient = 1

# district de-capturing
decapture_speed_multiplier = 1  # how much faster de-capturing is than capturing

# district control decay
decay_modifier = 1  # more means slower

# time values
seconds_per_ingame_day = 21600
ticks_per_day = seconds_per_ingame_day / update_market  # how often the kingpins receive slime per in-game day

# kingpin district control slime yields (per tick, i.e. in-game-hourly)
slime_yield_class_s = int(60000 / ticks_per_day)  # dividing the daily amount by the amount of method calls per day
slime_yield_class_a = int(40000 / ticks_per_day)
slime_yield_class_b = int(30000 / ticks_per_day)
slime_yield_class_c = int(20000 / ticks_per_day)

# district control slime yields assigned to property classes
district_control_slime_yields = {
	property_class_s: slime_yield_class_s,
	property_class_a: slime_yield_class_a,
	property_class_b: slime_yield_class_b,
	property_class_c: slime_yield_class_c
}

# Slime decay rate
slime_half_life = 60 * 60 * 24 * 14 #two weeks

# Rate of bleeding stored damage into the environment
bleed_half_life = 60 * 5 #five minutes

# how often to bleed
bleed_tick_length = 10

# Poudrin rarity (for enlisted players)
poudrin_rarity = 1500

# Chance to loot an item while scavenging
scavenge_item_rarity = 1000

# Lifetimes
invuln_onrevive = 0

# Weapon fee
weapon_fee = 100

# farming
crops_time_to_grow = 180  # in minutes; 180 minutes are 3 hours
reap_gain = 300000  # this takes about 1 hour to mine, so mining is more efficient

# Cooldowns
cd_kill = 5
cd_spar = 300
cd_haunt = 600
cd_invest = 1200
cd_boombust = 22
#For possible time limit on russian roulette
cd_rr = 600
#slimeoid downtime after a defeat
cd_slimeoiddefeated = 900
cd_scavenge = 0

# PvP timer pushouts
time_pvp_kill = 600
time_pvp_mine = 180
time_pvp_haunt = 600
time_pvp_invest_withdraw = 180
time_pvp = 1800

# time to get kicked out of subzone
time_kickout = 60 * 60  # 1 hour

# time after coming online before you can act
time_offline = 10

# Emotes
emote_tacobell = "<:tacobell:431273890195570699>"
emote_pizzahut = "<:pizzahut:431273890355085323>"
emote_kfc = "<:kfc:431273890216673281>"
emote_moon = "<:moon:431418525303963649>"
emote_111 = "<:111:431547758181220377>"

emote_copkiller = "<:copkiller:431275071945048075>"
emote_rowdyfucker = "<:rowdyfucker:431275088076079105>"
emote_ck = "<:ck:504173691488305152>"
emote_rf = "<:rf:504174176656162816>"

emote_theeye = "<:theeye:431429098909466634>"
emote_slime1 = "<:slime1:431564830541873182>"
emote_slime2 = "<:slime2:431570132901560320>"
emote_slime3 = "<:slime3:431659469844381717>"
emote_slime4 = "<:slime4:431570132901560320>"
emote_slime5 = "<:slime5:431659469844381717>"
emote_slimeskull = "<:slimeskull:431670526621122562>"
emote_slimeheart = "<:slimeheart:431673472687669248>"
emote_dice1 = "<:dice1:436942524385329162>"
emote_dice2 = "<:dice2:436942524389654538>"
emote_dice3 = "<:dice3:436942524041527298>"
emote_dice4 = "<:dice4:436942524406300683>"
emote_dice5 = "<:dice5:436942524444049408>"
emote_dice6 = "<:dice6:436942524469346334>"
emote_negaslime = "<:negaslime:453826200616566786>"
emote_bustin = "<:bustin:455194248741126144>"
emote_ghost = "<:lordofghosts:434002083256205314>"
emote_slimefull = "<:slimefull:496397819154923553>"
emote_purple = "<:purple:496397848343216138>"
emote_pink = "<:pink:496397871180939294>"
emote_slimecoin = "<:slimecoin:440576133214240769>"
emote_slimegun = "<:slimegun:436500203743477760>"
emote_slimecorp = "<:slimecorp:522416869127225344>"
emote_nlacakanm = "<:nlacakanm:499615025544298517>"

# Emotes for the negaslime writhe animation
emote_vt = "<:vt:492067858160025600>"
emote_ve = "<:ve:492067844930928641>"
emote_va = "<:va:492067850878451724>"
emote_v_ = "<:v_:492067837565861889>"
emote_s_ = "<:s_:492067830624157708>"
emote_ht = "<:ht:492067823150039063>"
emote_hs = "<:hs:492067783396294658>"
emote_he = "<:he:492067814933266443>"
emote_h_ = "<:h_:492067806465228811>"
emote_blank = "<:blank:570060211327336472>"

# Emotes for troll romance
emote_hearts = ":hearts:"
emote_diamonds = ":diamonds:"
emote_spades = ":spades:"
emote_clubs = ":clubs:"
emote_broken_heart = ":broken_heart:"

# Common strings.
str_casino_closed = "The Slime Casino only operates at night."
str_exchange_closed = "The Exchange has closed for the night."
str_exchange_specify = "Specify how much {currency} you will {action}."
str_exchange_channelreq = "You must go to the #" + channel_stockexchange + " to {action} your {currency}."
str_exchange_busy = "You can't {action} right now. Your slimebroker is busy."
str_food_channelreq = "There's no food here. Go to the Food Court, the Smoker's Cough, the Red Mobster, or the Speakeasy to {action}."
str_weapon_wielding_self = "You are wielding"
str_weapon_wielding = "They are wielding"
str_weapon_married_self = "You are married to"
str_weapon_married = "They are married to"

generic_role_name = 'NLACakaNM'

str_generic_subway_description = "A grimy subway train."
str_generic_subway_station_description = "A grimy subway station."
str_blimp_description = "This luxury zeppelin contains all the most exquisite amenities a robber baron in transit could ask for. A dining room, a lounge, a pool table, you know, rich people stuff. Being a huge, highly flammable balloon filled with hydrogen, it is the safest way to travel in the city only because it's out of the price range of most juveniles' budget. It's used by the rich elite to travel from their summer homes in Assault Flats Beach to their winter homes in Dreadford, and vice versa, without having to step foot in the more unsavory parts of the city. It does it's job well and only occasionally bursts into flames."
str_blimp_tower_description = "This mooring mast is mostly used for amassing millionaire mooks into the marvelous Neo Milwaukee multi-story zeppelin, m'lady. Basically, you can board a blimp here. All you have to do is walk up an extremely narrow spiral staircase without an adequate handrail for about 40 feet straight up and then you can embark onto the highest airship this side of the River of Slime! It'll be great! Don't mind the spontaneously combusting zeppelins crashing into the earth in the distance. That's normal."
str_downtown_station_description = "This large, imposing structure is the central hub for the entire city's rapid transit system. A public transportation powerhouse, it contains connections to every subway line in the city, and for dirt cheap. Inside of it's main terminal, a humongous split-flap display is constantly updating with the times of subway arrivals and departures. Hordes of commuters from all across the city sprint to their connecting trains, or simply spill out into the Downtown streets, ready to have their guts do the same.\n\nExits into Downtown NLACakaNM."
str_red_subway_description = "Red Line trains are strictly uniform, with dull, minimalistic furnishings producing a borderline depressing experience. Almost completely grey aside from it's style guide mandated red accents, everything is purely practical. It provides just enough for its commuting salarymen to get to work in the morning and home at night."
str_red_subway_station_description = "This sparsely decorated terminal replicates the feeling of riding on a Red Line train, otherwise known as inducing suicidal thoughts. Dim lighting barely illuminates the moldy, stained terminal walls. Inbound and outbound trains arrive and departure one after another with unreal temporal precision. You're not sure if you've ever seen a Red Line train be late. Still doesn't make you like being on one though."
str_green_subway_description = "Easily the oldest subway line in the city, with the interior design and general cleanliness to prove it. Once cutting edge, it's art deco stylings have begun to deteriorate due to overuse and underfunding. That goes double for the actual trains themselves, with a merely bumpy ride on the Green Line being the height of luxury compared to the far worse potential risks."
str_green_subway_station_description = "Much like its trains, Green Line terminals have fallen into disrepair. It's vintage aesthetic only exasperating it's crumbling infrastructure, making the whole line seem like a old, dilapidated mess. But, you'll give it one thing, it's pretty cool looking from the perspective of urban exploration. You've dreamed of exploring it's vast, abandoned subway networks ever since you first rode on it. They could lead to anywhere. So close, and yet so mysterious."
str_blue_subway_description = "Probably the nicest subway line in the city, the Blue Line isn't defined by its poor hygiene or mechanical condition. Instead, it's defined by its relative normality. More-or-less clean floors, brightly lit interiors, upholstery on the seats. These stunning, almost sci-fi levels of perfection are a sight to behold. Wow!"
str_blue_subway_station_description = "It is clean and well-kempt, just like the Blue Line trains. This relatively pristine subway terminal hosts all manner of unusualities. With limited amounts of graffiti sprayed unto the otherwise sort-of white walls, there's actually some semblance of visual simplicity. For once in this city, your eyes aren't being completely assaulted with information or blinding lights. Boring, this place sucks. Board whatever train you're getting on and get back to killing people as soon as possible."
str_yellow_subway_description = "If there's one word to describe the Yellow Line, it's \"confusing\". It's by far the filthiest subway line in the city, which is exponentially worsened by it's bizarre, unexplainable faux wood paneling that lines every train. You can only imagine that this design decision was made to make the subway feel less sterile and more homely, but the constant stench of piss and homeless people puking sort of ruins that idea. Riding the Yellow Line makes you feel like you're at your grandma's house every single time you ride it, if your grandma's house was in Jaywalker Plain."
str_yellow_subway_station_description = "It's absolutely fucking disgusting. By far the worst subway line, the Yellow Line can't keep it's terrible interior design choices contained to its actual trains. Even in its terminals, the faux wood paneling clashes with every other aesthetic element present. It's ghastly ceilings have turned a delightful piss-soaked shade of faded white. It's bizarre mixture of homely decorations and completely dilapidated state makes you oddly beguiled in a way. How did they fuck up the Yellow Line so bad? The world may never know."
str_subway_connecting_sentence = "Below it, on a lower level of the station, is a {} line terminal."

# Common database columns
col_id_server = 'id_server'

#Database columns for roles
col_id_role = 'id_role'
col_role_name = 'name'

# Database columns for items
col_id_item = "id_item"
col_item_type = "item_type"
col_time_expir = "time_expir"
col_value = "value"
col_stack_max = 'stack_max'
col_stack_size = 'stack_size'
col_soulbound = 'soulbound'

# Database columns for server
col_icon = "icon"

# Database columns for players
col_avatar = "avatar"
col_display_name = "display_name"

# Database columns for users
col_id_user = 'id_user'
col_slimes = 'slimes'
col_slimelevel = 'slimelevel'
col_hunger = 'hunger'
col_totaldamage = 'totaldamage'
col_weapon = 'weapon'
col_weaponskill = 'weaponskill'
col_trauma = 'trauma'
col_slimecoin = 'slimecoin'
col_time_lastkill = 'time_lastkill'
col_time_lastrevive = 'time_lastrevive'
col_id_killer = 'id_killer'
col_time_lastspar = 'time_lastspar'
col_time_lasthaunt = 'time_lasthaunt'
col_time_lastinvest = 'time_lastinvest'
col_bounty = 'bounty'
col_weaponname = 'weaponname'
col_name = 'name'
col_inebriation = 'inebriation'
col_ghostbust = 'ghostbust'
col_faction = 'faction'
col_poi = 'poi'
col_life_state = 'life_state'
col_busted = 'busted'
col_rrchallenger = 'rr_challenger_id'
col_time_lastsow = 'time_lastsow'
col_farm = 'farm'
col_time_last_action = 'time_last_action'
col_weaponmarried = 'weaponmarried'
col_time_lastscavenge = 'time_lastscavenge'
col_bleed_storage = 'bleed_storage'
col_time_lastenter = 'time_lastenter'
col_time_lastoffline = 'time_lastoffline'
col_time_joined = 'time_joined'
col_poi_death = 'poi_death'

#Database columns for slimeoids
col_id_slimeoid = 'id_slimeoid'
col_body = 'body'
col_head = 'head'
col_legs = 'legs'
col_armor = 'armor'
col_weapon = 'weapon'
col_special = 'special'
col_ai = 'ai'
col_type = 'type'
col_name = 'name'
col_atk = 'atk'
col_defense = 'defense'
col_intel = 'intel'
col_level = 'level'
col_time_defeated = 'time_defeated'
col_clout = 'clout'
col_hue = 'hue'

# Database columns for user statistics
col_stat_metric = 'stat_metric'
col_stat_value = 'stat_value'

# Database columns for markets
col_time_lasttick = 'time_lasttick'
col_slimes_revivefee = 'slimes_revivefee'
col_negaslime = 'negaslime'
col_clock = 'clock'
col_weather = 'weather'
col_day = 'day'
col_decayed_slimes = 'decayed_slimes'
col_donated_slimes = 'donated_slimes'

# Database columns for stocks
col_stock = 'stock'
col_market_rate = 'market_rate'
col_exchange_rate = 'exchange_rate'
col_boombust = 'boombust'
col_total_shares = 'total_shares'

# Database columns for companies
col_total_profits = 'total_profits'
col_recent_profits = 'recent_profits'

# Database columns for shares
col_shares = 'shares'

# Database columns for stats
col_total_slime = 'total_slime'
col_total_slimecoin = 'total_slimecoin'
col_total_players = 'total_players'
col_total_players_pvp = 'total_players_pvp'
col_timestamp = 'timestamp'

# Database columns for districts
col_district = 'district'
col_controlling_faction = 'controlling_faction'
col_capturing_faction = 'capturing_faction'
col_capture_points = 'capture_points'
col_district_slimes = 'slimes'

# Database columns for transports
col_transport_type = 'transport_type'
col_current_line = 'current_line'
col_current_stop = 'current_stop'

# Database columns for troll romance
col_quadrant = 'quadrant'
col_quadrants_target = 'id_target'
col_quadrants_target2 = 'id_target2'

# Item type names
it_item = "item"
it_medal = "medal"
it_slimepoudrin = "slimepoudrin"
it_questitem = "questitem"
it_food = "food"
it_weapon = "weapon"
it_cosmetic = 'cosmetic'

# Cosmetic item rarities
rarity_plebeian = "Plebeian"
rarity_patrician = "Patrician"
rarity_princeps = "Princeps"

# Leaderboard score categories
leaderboard_slimes = "SLIMIEST"
leaderboard_slimecoin = "SLIMECOIN BARONS"
leaderboard_ghosts = "ANTI-SLIMIEST"
leaderboard_podrins = "PODRIN LORDS"
leaderboard_bounty = "MOST WANTED"
leaderboard_kingpins = "KINGPINS' COFFERS"
leaderboard_districts = "DISTRICTS CONTROLLED"

# leaderboard entry types
entry_type_player = "player"
entry_type_districts = "districts"

# district control channel topic text
control_topic_killers = "Currently controlled by the killers."
control_topic_rowdys = "Currently controlled by the rowdys."
control_topic_neutral = "Currently controlled by no one."

control_topics = {
	faction_killers: control_topic_killers,
	faction_rowdys: control_topic_rowdys,
	"": control_topic_neutral  # no faction
}

# district control actors
actor_decay = "decay"

# The highest level your weaponskill may be on revive. All skills over this level reset to this level.
weaponskill_max_onrevive = 3

# Places you might get !shot
hitzone_list = [
	"wrist",
	"leg",
	"arm",
	"upper back",
	"foot",
	"shoulder",
	"neck",
	"kneecap",
	"obliques",
	"solar plexus",
	"Achilles' tendon",
	"jaw",
	"ankle",
	"trapezius",
	"thigh",
	"chest",
	"gut",
	"abdomen",
	"lower back",
	"calf"
]

# User statistics we track
stat_max_slimes = 'max_slimes'
stat_lifetime_slimes = 'lifetime_slimes'
stat_lifetime_slimeloss = 'lifetime_slime_loss'
stat_lifetime_slimesdecayed = 'lifetime_slimes_decayed'
stat_slimesmined = 'slimes_mined'
stat_max_slimesmined = 'max_slimes_mined'
stat_lifetime_slimesmined = 'lifetime_slimes_mined'
stat_slimesfromkills = 'slimes_from_kills'
stat_max_slimesfromkills = 'max_slimes_from_kills'
stat_lifetime_slimesfromkills = 'lifetime_slimes_from_kills'
stat_slimesfarmed = 'slimes_farmed'
stat_max_slimesfarmed = 'max_slimes_farmed'
stat_lifetime_slimesfarmed = 'lifetime_slimes_farmed'
stat_slimesscavenged = 'slimes_scavenged'
stat_max_slimesscavenged = 'max_slimes_scavenged'
stat_lifetime_slimesscavenged = 'lifetime_slimes_scavenged'
stat_lifetime_slimeshaunted = 'lifetime_slimes_haunted'
stat_max_level = 'max_level'
stat_max_ghost_level = 'max_ghost_level'
stat_max_hitsurvived = 'max_hit_survived'
stat_max_hitdealt = 'max_hit_dealt'
stat_max_hauntinflicted = 'max_haunt_inflicted'
stat_kills = 'kills'
stat_max_kills = 'max_kills'
stat_biggest_kill = 'biggest_kill'
stat_lifetime_kills = 'lifetime_kills'
stat_lifetime_ganks = 'lifetime_ganks'
stat_lifetime_takedowns = 'lifetime_takedowns'
stat_max_wepskill = 'max_wep_skill'
stat_max_slimecoin = 'max_slime_coins'
stat_lifetime_slimecoin = 'lifetime_slime_coins'
stat_slimecoin_spent_on_revives = 'slimecoins_spent_on_revives'
stat_biggest_casino_win = 'biggest_casino_win'
stat_biggest_casino_loss = 'biggest_casino_loss'
stat_lifetime_casino_winnings = 'lifetime_casino_winnings'
stat_lifetime_casino_losses = 'lifetime_casino_losses'
stat_total_slimecoin_invested = 'total_slimecoin_invested'
stat_total_slimecoin_withdrawn = 'total_slimecoin_withdrawn'
stat_bounty_collected = 'bounty_collected'
stat_max_bounty = 'max_bounty'
stat_ghostbusts = 'ghostbusts'
stat_biggest_bust_level = 'biggest_bust_level'
stat_lifetime_ghostbusts = 'lifetime_ghostbusts'
stat_max_ghostbusts = 'max_ghostbusts'
stat_max_poudrins = 'max_poudrins'
stat_poudrins_looted = 'poudrins_looted'
stat_lifetime_poudrins = 'lifetime_poudrins'
stat_lifetime_damagedealt = 'lifetime_damage_dealt'
stat_lifetime_selfdamage = 'lifetime_self_damage'
stat_lifetime_deaths = 'lifetime_deaths'
stat_lifetime_pve_deaths = 'lifetime_pve_deaths'
#Track revolver trigger pulls survived?
stat_lifetime_spins_survived = 'lifetime_spins_survived'
stat_max_spins_survived = 'max_spins_survived'
stat_capture_points_contributed = 'capture_points_contributed'

# Categories of events that change your slime total, for statistics tracking
source_mining = 0
source_damage = 1
source_killing = 2
source_self_damage = 3
source_busting = 4
source_haunter = 5
source_haunted = 6
source_spending = 7
source_decay = 8
source_ghostification = 9
source_bleeding = 10
source_scavenging = 11
source_farming = 12

# Categories of events that change your slimecoin total, for statistics tracking
coinsource_spending = 0
coinsource_donation = 1
coinsource_bounty = 2
coinsource_revival = 3
coinsource_casino = 4
coinsource_transfer = 5
coinsource_invest = 6
coinsource_withdraw = 7

# Causes of death, for statistics tracking
cause_killing = 0
cause_mining = 1
cause_grandfoe = 2
cause_donation = 3
cause_busted = 4
cause_suicide = 5
cause_leftserver = 6
cause_drowning = 7
cause_falling = 8
cause_bleeding = 9

# List of user statistics that reset to 0 on death
stats_clear_on_death = [
	stat_slimesmined,
	stat_slimesfromkills,
	stat_kills,
	stat_ghostbusts,
        stat_slimesfarmed,
        stat_slimesscavenged
]

# List of normal items.
item_list = [
	EwDefaultItem(
		id_item = "whitedye",
		context = "dye",
		subcontext = "white",
		str_name = "White Dye",
		str_desc = "A small vial of white dye.",
		ingredients = "poketuber",
	),
	EwDefaultItem(
		id_item = "yellowdye",
		context = "dye",
		subcontext = "yellow",
		str_name = "Yellow Dye",
		str_desc = "A small vial of yellow dye.",
		ingredients = "pulpgourds",
	),
	EwDefaultItem(
		id_item = "orangedye",
		context = "dye",
		subcontext = "orange",
		str_name = "Orange Dye",
		str_desc = "A small vial of orange dye.",
		ingredients = "sourpotatoes",
	),
	EwDefaultItem(
		id_item = "reddye",
		context = "dye",
		subcontext = "red",
		str_name = "Red Dye",
		str_desc = "A small vial of red dye.",
		ingredients = "bloodcabbages",
	),
	EwDefaultItem(
		id_item = "magentadye",
		context = "dye",
		subcontext = "magenta",
		str_name = "Magenta Dye",
		str_desc = "A small vial of magenta dye.",
		ingredients = "joybeans",
	),
	EwDefaultItem(
		id_item = "purpledye",
		context = "dye",
		subcontext = "purple",
		str_name = "Purple Dye",
		str_desc = "A small vial of purple dye.",
		ingredients = "purplekilliflower",
	),
	EwDefaultItem(
		id_item = "bluedye",
		context = "dye",
		subcontext = "blue",
		str_name = "Blue Dye",
		str_desc = "A small vial of blue dye.",
		ingredients = "razornuts",
	),
	EwDefaultItem(
		id_item = "greendye",
		context = "dye",
		subcontext = "green",
		str_name = "Green Dye",
		str_desc = "A small vial of green dye.",
		ingredients = "pawpaw",
	),
	EwDefaultItem(
		id_item = "tealdye",
		context = "dye",
		subcontext = "teal",
		str_name = "Teal Dye",
		str_desc = "A small vial of teal dye.",
		ingredients = "sludgeberries",
	),
	EwDefaultItem(
		id_item = "rainbowdye",
		context = "dye",
		subcontext = "rainbow",
		str_name = "***Rainbow Dye!!***",
		str_desc = "***A small vial of Rainbow dye!!***",
		ingredients = "suganmanuts",
	),
	EwDefaultItem(
		id_item = "pinkdye",
		context = "dye",
		subcontext = "pink",
		str_name = "Pink Dye",
		str_desc = "A small vial of pink dye.",
		ingredients = "pinkrowddishes",
	),
	EwDefaultItem(
		id_item = "greydye",
		context = "dye",
		subcontext = "grey",
		str_name = "Grey Dye",
		str_desc = "A small vial of grey dye.",
		ingredients = "dankwheat",
	),
	EwDefaultItem(
		id_item = "cobaltdye",
		context = "dye",
		subcontext = "cobalt",
		str_name = "Cobalt Dye",
		str_desc = "A small vial of cobalt dye.",
		ingredients = "brightshade",
	),
	EwDefaultItem(
		id_item = "blackdye",
		context = "dye",
		subcontext = "black",
		str_name = "Black Dye",
		str_desc = "A small vial of black dye.",
		ingredients = "blacklimes",
	),
	EwDefaultItem(
		id_item = "limedye",
		context = "dye",
		subcontext = "lime",
		str_name = "Lime Dye",
		str_desc = "A small vial of lime dye.",
		ingredients = "phosphorpoppies",
	),
	EwDefaultItem(
		id_item = "cyandye",
		context = "dye",
		subcontext = "cyan",
		str_name = "Cyan Dye",
		str_desc = "A small vial of cyan dye.",
		ingredients = "direapples",
	),
]

# A map of id_item to EwDefaultItem objects.
item_map = {}

# A list of food names
item_names = []

# Populate food map, including all aliases.
for item in item_list:
	item_map[item.id_item] = item
	item_names.append(item.id_item)

	for alias in item.alias:
		item_map[alias] = item

# list of dyes you're able to saturate your Slimeoid with
dye_list = []

# seperate the dyes from the other normal items
for c in dye_list:
	if c.context != "dye":
		pass
	else:
		dye_list.append(c)

# A Weapon Effect Function for "gun". Takes an EwEffectContainer as ctn.
def wef_gun(ctn = None):
	aim = (random.randrange(10) + 1)

	if aim == 1:
		ctn.miss = True
		ctn.slimes_damage = 0
	elif aim == 10:
		ctn.crit = True
		ctn.slimes_damage *= 2

# weapon effect function for "rifle"
def wef_rifle(ctn = None):
	aim = (random.randrange(10) + 1)

	if aim <= 2:
		ctn.miss = True
		ctn.slimes_damage = 0
	elif aim >= 9:
		ctn.crit = True
		ctn.slimes_damage *= 2

# weapon effect function for "nun-chucks"
def wef_nunchucks(ctn = None):
	ctn.strikes = 0
	dmg = ctn.slimes_damage
	ctn.slimes_damage = 0

	for count in range(5):
		if random.randint(1, 3) == 1:
			ctn.strikes += 1
			ctn.slimes_damage += int((dmg * 3) / 5)

	if ctn.strikes == 5:
		ctn.crit = True
	elif ctn.strikes == 0:
		ctn.miss = True
		ctn.user_data.change_slimes(n = (-ctn.slimes_damage / 2), source = source_self_damage)

# weapon effect function for "katana"
def wef_katana(ctn = None):
	ctn.miss = False
	ctn.slimes_damage = int(0.85 * ctn.slimes_damage)
	if(random.randrange(10) + 1) == 10:
		ctn.crit = True
		ctn.slimes_damage *= 2.1

# weapon effect function for "bat"
def wef_bat(ctn = None):
	aim = (random.randrange(21) - 10)
	if aim <= -9:
		ctn.miss = True
		ctn.slimes_damage = 0

	ctn.slimes_damage = int(ctn.slimes_damage * (1 + (aim / 10)))

	if aim >= 9:
		ctn.crit = True
		ctn.slimes_damage = int(ctn.slimes_damage * 1.5)

# weapon effect function for "garrote"
def wef_garrote(ctn = None):
	ctn.slimes_damage *= 0.5
	aim = (random.randrange(100) + 1)
	if aim <= 50:
		ctn.miss = True
		ctn.slimes_damage = 0
	elif aim == 100:
		ctn.slimes_damage *= 100
		ctn.crit = True

# weapon effect function for "brassknuckles"
def wef_brassknuckles(ctn = None):
	aim1 = (random.randrange(21) - 10)
	aim2 = (random.randrange(21) - 10)
	whiff1 = 1
	whiff2 = 1

	if aim1 == -9:
		whiff1 = 0
	if aim2 == -9:
		whiff2 = 0

	if whiff1 == 0 and whiff2 == 0:
		ctn.miss = True
		ctn.slimes_damage = 0
	else:
		ctn.slimes_damage = int((((ctn.slimes_damage * (1 + (aim1 / 20))) * whiff1) / 2) + (((ctn.slimes_damage * (1 + (aim2 / 20))) * whiff2) / 2))

# weapon effect function for "molotov"
def wef_molotov(ctn = None):
	ctn.slimes_damage += int(ctn.slimes_damage / 2)
	aim = (random.randrange(100) + 1)

	if aim <= 10:
		ctn.crit = True
		ctn.user_data.change_slimes(n = -ctn.slimes_damage, source = source_self_damage)
	elif aim > 10 and aim <= 20:
		ctn.miss = True
		ctn.slimes_damage = 0

# weapon effect function for "knives"
def wef_knives(ctn = None):
	ctn.user_data.slimes += int(ctn.slimes_spent * 0.33)
	ctn.slimes_damage = int(ctn.slimes_damage * 0.85)
	aim = (random.randrange(10) + 1)

	if aim <= 1:
		ctn.miss = True
		ctn.slimes_damage = 0
	elif aim >= 10:
		ctn.crit = True
		ctn.slimes_damage = int(ctn.slimes_damage * 2)

# weapon effect function for "scythe"
def wef_scythe(ctn = None):
	ctn.user_data.change_slimes(n = (-ctn.slimes_spent * 0.33), source = source_self_damage)
	ctn.slimes_damage = int(ctn.slimes_damage * 1.25)
	aim = (random.randrange(10) + 1)

	if aim <= 2:
		ctn.miss = True
		ctn.slimes_damage = 0
	elif aim >= 9:
		ctn.crit = True
		ctn.slimes_damage *= 2

# All weapons in the game.
weapon_list = [
	EwWeapon( # 1
		id_weapon = "gun",
		alias = [
			"pistol",
			"pistols",
			"dualpistols"
		],
		str_crit = "**Critical Hit!** {name_player} has put dealt {name_target} a serious wound!",
		str_miss = "**You missed!** Your shot failed to land!",
		str_equip = "You equip the dual pistols.",
		str_weapon = "dual pistols",
		str_weaponmaster_self = "You are a rank {rank} master of the dual pistols.",
		str_weaponmaster = "They are a rank {rank} master of the dual pistols.",
		str_trauma_self = "You have scarring on both temples, which occasionally bleeds.",
		str_trauma = "They have scarring on both temples, which occasionally bleeds.",
		str_kill = "{name_player} puts their gun to {name_target}'s head. **BANG**. Execution-style. Blood pools across the hot asphalt. {emote_skull}",
		str_killdescriptor = "gunned down",
		str_damage = "{name_target} takes a bullet to the {hitzone}!!",
		str_duel = "**BANG BANG.** {name_player} and {name_target} practice their quick-draw, bullets whizzing past one another's heads.",
		fn_effect = wef_gun,
		str_description = "They're dual pistols"
	),
	EwWeapon( # 2
		id_weapon = "rifle",
		alias = [
			"assaultrifle",
			"machinegun",
			"mg"
		],
		str_crit = "**Critical hit!!** You unload an entire magazine into the target!!",
		str_miss = "**You missed!** Not one of your bullets connected!!",
		str_equip = "You equip the assault rifle.",
		str_weapon = "an assault rifle",
		str_weaponmaster_self = "You are a rank {rank} master of the assault rifle.",
		str_weaponmaster = "They are a rank {rank} master of the assault rifle.",
		str_trauma_self = "Your torso is riddled with scarred-over bulletholes.",
		str_trauma = "Their torso is riddled with scarred-over bulletholes.",
		str_kill = "**RAT-TAT-TAT-TAT-TAT!!** {name_player} rains a hail of bullets directly into {name_target}!! They're officially toast! {emote_skull}",
		str_killdescriptor = "gunned down",
		str_damage = "Bullets rake over {name_target}'s {hitzone}!!",
		str_duel = "**RAT-TAT-TAT-TAT-TAT!!** {name_player} and {name_target} practice shooting at distant targets with quick, controlled bursts.",
		fn_effect = wef_rifle,
		str_description = "It's a rifle"
	),
	EwWeapon( # 3
		id_weapon = "nun-chucks",
		alias = [
			"nanchacku",
			"nunchaku",
			"chucks",
			"numchucks",
			"nunchucks"
		],
		str_crit = "**COMBO!** {name_player} strikes {name_target} with a flurry of 5 vicious blows!",
		str_miss = "**Whack!!** {name_player} fucks up his kung-fu routine and whacks himself in the head with his own nun-chucks!!",
		str_equip = "You equip the nun-chucks.",
		str_weapon = "nun-chucks",
		str_weaponmaster_self = "You are a rank {rank} kung-fu master.",
		str_weaponmaster = "They are a rank {rank} kung-fu master.",
		str_trauma_self = "You are covered in deep bruises. You hate martial arts of all kinds.",
		str_trauma = "They are covered in deep bruises. They hate martial arts of all kinds.",
		str_kill = "**HIIII-YAA!!** With expert timing, {name_player} brutally batters {name_target} to death, then strikes a sweet kung-fu pose. {emote_skull}",
		str_killdescriptor = "fatally bludgeoned",
		str_damage = "{name_target} takes {strikes} nun-chuck whacks directly in the {hitzone}!!",
		str_duel = "**HII-YA! HOOOAAAAAHHHH!!** {name_player} and {name_target} twirl wildly around one another, lashing out with kung-fu precision.",
		fn_effect = wef_nunchucks,
		str_description = "They're nunchucks"
	),
	EwWeapon( # 4
		id_weapon = "katana",
		alias = [
			"sword",
			"ninjasword",
			"samuraisword",
			"blade"
		],
		str_crit = "**Critical hit!!** {name_target} is cut deep!!",
		str_miss = "",
		str_equip = "You equip the katana.",
		str_weapon = "a katana",
		str_weaponmaster_self = "You are a rank {rank} blademaster.",
		str_weaponmaster = "They are a rank {rank} blademaster.",
		str_trauma_self = "A single clean scar runs across the entire length of your body.",
		str_trauma = "A single clean scar runs across the entire length of their body.",
		str_kill = "Faster than the eye can follow, {name_player}'s blade glints in the greenish light. {name_target} falls over, now in two pieces. {emote_skull}",
		str_killdescriptor = "bisected",
		str_damage = "{name_target} is slashed across the {hitzone}!!",
		str_duel = "**CRACK!! THWACK!! CRACK!!** {name_player} and {name_target} duel with bamboo swords, viciously striking at head, wrist and belly.",
		fn_effect = wef_katana,
		str_description = "It's a katana"
	),
	EwWeapon( # 5
		id_weapon = "bat",
		alias = [
			"club",
			"batwithnails",
			"nailbat",
		],
		str_crit = "**Critical hit!!** {name_player} has bashed {name_target} up real bad!",
		str_miss = "**MISS!!** {name_player} swung wide and didn't even come close!",
		str_equip = "You equip the bat with nails in it.",
		str_weaponmaster_self = "You are a rank {rank} master of the nailbat.",
		str_weaponmaster = "They are a rank {rank} master of the nailbat.",
		str_weapon = "a bat full of nails",
		str_trauma_self = "Your head appears to be slightly concave on one side.",
		str_trauma = "Their head appears to be slightly concave on one side.",
		str_kill = "{name_player} pulls back for a brutal swing! **CRUNCCHHH.** {name_target}'s brains splatter over the sidewalk. {emote_skull}",
		str_killdescriptor = "nail bat battered",
		str_damage = "{name_target} is struck with a hard blow to the {hitzone}!!",
		str_duel = "**SMASHH! CRAASH!!** {name_player} and {name_target} run through the neighborhood, breaking windshields, crushing street signs, and generally having a hell of a time.",
		fn_effect = wef_bat,
		str_description = "It's a nailbat"
	),
	EwWeapon( # 6
		id_weapon = "garrote",
		alias = [
			"wire",
			"garrotewire",
			"garrottewire"
		],
		str_crit = "**CRITICAL HIT!!** {name_player} got lucky and caught {name_target} completely unaware!!",
		str_miss = "**MISS!** {name_player}'s target got away in time!",
		str_equip = "You equip the garrotte wire.",
		str_weapon = "a garrotte wire",
		str_weaponmaster_self = "You are a rank {rank} master of the garrotte.",
		str_weaponmaster = "They are a rank {rank} master of the garrotte.",
		str_trauma_self = "There is noticeable bruising and scarring around your neck.",
		str_trauma = "There is noticeable bruising and scarring around their neck.",
		str_kill = "{name_player} quietly moves behind {name_target} and... **!!!** After a brief struggle, only a cold body remains. {emote_skull}",
		str_killdescriptor = "garrote wired",
		str_damage = "{name_target} is ensnared by {name_player}'s wire!!",
		str_duel = "{name_player} and {name_target} compare their dexterity by playing Cat's Cradle with deadly wire.",
		fn_effect = wef_garrote,
		str_description = "It's a garrote"
	),
	EwWeapon( # 7
		id_weapon = "brassknuckles",
		alias = [
			"knuckles",
			"knuckledusters",
			"dusters"
		],
		str_crit = "",
		str_miss = "**MISS!** {name_player} couldn't land a single blow!!",
		str_equip = "You equip the brass knuckles.",
		str_weapon = "brass knuckles",
		str_weaponmaster_self = "You are a rank {rank} master pugilist.",
		str_weaponmaster = "They are a rank {rank} master pugilist.",
		str_trauma_self = "You've got two black eyes, missing teeth, and a profoundly crooked nose.",
		str_trauma = "They've got two black eyes, missing teeth, and a profoundly crooked nose.",
		str_kill = "{name_player} slugs {name_target} right between the eyes! *POW! THWACK!!* **CRUNCH.** Shit. May have gotten carried away there. Oh, well. {emote_skull}",
		str_killdescriptor = "pummeled to death",
		str_damage = "{name_target} is socked in the {hitzone}!!",
		str_duel = "**POW! BIFF!!** {name_player} and {name_target} take turns punching each other in the abs. It hurts so good.",
		fn_effect = wef_brassknuckles,
		str_description = "They're brass knuckles"
	),
	EwWeapon( # 8
		id_weapon = "molotov",
		alias = [
			"firebomb",
			"molotovcocktail",
			"bomb",
			"bombs"
		],
		str_crit = "**Oh, the humanity!!** The bottle bursts in {name_player}'s hand, burning them terribly!!",
		str_miss = "**A dud!!** the rag failed to ignite the molotov!",
		str_equip = "You equip the molotov cocktail.",
		str_weapon = "molotov cocktails",
		str_weaponmaster_self = "You are a rank {rank} master arsonist.",
		str_weaponmaster = "They are a rank {rank} master arsonist.",
		str_trauma_self = "You're wrapped in bandages. What skin is showing appears burn-scarred.",
		str_trauma = "They're wrapped in bandages. What skin is showing appears burn-scarred.",
		str_kill = "**SMASH!** {name_target}'s front window shatters and suddenly flames are everywhere!! The next morning, police report that {name_player} is suspected of arson. {emote_skull}",
		str_killdescriptor = "exploded",
		str_damage = "{name_target} dodges a bottle, but is singed on the {hitzone} by the blast!!",
		str_duel = "{name_player} and {name_target} compare notes on frontier chemistry, seeking the optimal combination of combustibility and fuel efficiency.",
		fn_effect = wef_molotov,
		str_description = "They're molotov bottles"
	),
	EwWeapon( # 9
		id_weapon = "knives",
		alias = [
			"knife",
			"dagger",
			"daggers",
			"throwingknives",
			"throwingknife"
		],
		str_crit = "**Critical hit!!** {name_player}'s knife strikes a vital point!",
		str_miss = "**MISS!!** {name_player}'s knife missed its target!",
		str_equip = "You equip the throwing knives.",
		str_weapon = "throwing knives",
		str_weaponmaster_self = "You are a rank {rank} master of the throwing knife.",
		str_weaponmaster = "They are a rank {rank} master of the throwing knife.",
		str_trauma_self = "You are covered in scarred-over lacerations and puncture wounds.",
		str_trauma = "They are covered in scarred-over lacerations and puncture wounds.",
		str_kill = "A blade flashes through the air!! **THUNK.** {name_target} is a goner, but {name_player} slits their throat before fleeing the scene, just to be safe. {emote_skull}",
		str_killdescriptor = "knifed",
		str_damage = "{name_target} is stuck by a knife in the {hitzone}!!",
		str_duel = "**TING! TING!!** {name_player} and {name_target} take turns hitting one another's knives out of the air.",
		fn_effect = wef_knives,
		str_description = "They're throwing knives"
	),
	EwWeapon( # 10
		id_weapon = "scythe",
		alias = [
			"sickle"
		],
		str_crit = "**Critical hit!!** {name_target} is carved by the wicked curved blade!",
		str_miss = "**MISS!!** {name_player}'s swings wide of the target!",
		str_equip = "You equip the scythe.",
		str_weapon = "a scythe",
		str_weaponmaster_self = "You are a rank {rank} master of the scythe.",
		str_weaponmaster = "They are a rank {rank} master of the scythe.",
		str_trauma_self = "You are wrapped tightly in bandages that hold your two halves together.",
		str_trauma = "They are wrapped tightly in bandages that hold their two halves together.",
		str_kill = "**SLASHH!!** {name_player}'s scythe cleaves the air, and {name_target} staggers. A moment later, {name_target}'s torso topples off their waist. {emote_skull}",
		str_killdescriptor = "sliced in twain",
		str_damage = "{name_target} is cleaved through the {hitzone}!!",
		str_duel = "**WHOOSH, WHOOSH** {name_player} and {name_target} swing their blades in wide arcs, dodging one another's deadly slashes.",
		fn_effect = wef_scythe,
		str_description = "It's a scythe"
	)
]

# A map of id_weapon to EwWeapon objects.
weapon_map = {}

# A list of weapon names
weapon_names = []

# Populate weapon map, including all aliases.
for weapon in weapon_list:
	weapon_map[weapon.id_weapon] = weapon
	weapon_names.append(weapon.id_weapon)

	for alias in weapon.alias:
		weapon_map[alias] = weapon

# All weather effects in the game.
weather_list = [
	EwWeather(
		name = "sunny",
		sunrise = "The smog is beginning to clear in the sickly morning sunlight.",
		day = "The sun is blazing on the cracked streets, making the air shimmer.",
		sunset = "The sky is darkening, the low clouds an iridescent orange.",
		night = "The moon looms yellow as factories belch smoke all through the night."
	),
	EwWeather(
		name = "rainy",
		sunrise = "Rain gently beats against the pavement as the sky starts to lighten.",
		day = "Rain pours down, collecting in oily rivers that run down sewer drains.",
		sunset = "Distant thunder rumbles as it rains, the sky now growing dark.",
		night = "Silverish clouds hide the moon, and the night is black in the heavy rain."
	),
	EwWeather(
		name = "windy",
		sunrise = "Wind whips through the city streets as the sun crests over the horizon.",
		day = "Paper and debris are whipped through the city streets by the winds, buffetting pedestrians.",
		sunset = "The few trees in the city bend and strain in the wind as the sun slowly sets.",
		night = "The dark streets howl, battering apartment windows with vicious night winds."
	),
	EwWeather(
		name = "lightning",
		sunrise = "An ill-omened morning dawns as lighting streaks across the sky in the sunrise.",
		day = "Flashes of bright lightning and peals of thunder periodically startle the citizens out of their usual stupor.",
		sunset = "Bluish white arcs of electricity tear through the deep red dusky sky.",
		night = "The dark night periodically lit with bright whitish-green bolts that flash off the metal and glass of the skyscrapers."
	),
	EwWeather(
		name = "cloudy",
		sunrise = "The dim morning light spreads timidly across the thickly clouded sky.",
		day = "The air hangs thick, and the pavement is damp with mist from the clouds overhead.",
		sunset = "The dusky light blares angry red on a sky choked with clouds and smog.",
		night = "Everything is dark and still but the roiling clouds, reflecting the city's eerie light."
	),
	EwWeather(
		name = "snow",
		sunrise = "The morning sun glints off the thin layer or powdery snow that blankets the city.",
		day = "Flakes of snow clump together and whip through the bitter cold air in the winder wind.",
		sunset = "The cold air grows colder as the sky darkens and the snow piles higher in the streets.",
		night = "Icy winds whip through the city, white snowflakes glittering in the black of night."
	),
		EwWeather(
		name = "foggy",
		sunrise = "Fog hangs thick in the air, stubbornly refusing to dissipate as the sun clears the horizon.",
		day = "You can barely see to the next block in the sickly greenish NLAC smog.",
		sunset = "Visibility only grows worse in the fog as the sun sets and the daylight fades.",
		night = "Everything is obscured by the darkness of night and the thick city smog."
	)
]

# Food vendor names
vendor_bar = 'bar'	#rate of non-mtn dew drinks are 1 slimecoin to 9 hunger
vendor_pizzahut = 'Pizza Hut'	#rate of fc vendors are 1 slimecoin to 10 hunger
vendor_tacobell = 'Taco Bell'
vendor_kfc = 'KFC'
vendor_mtndew = 'Mtn Dew Fountain'
vendor_vendingmachine = 'vending machine'
vendor_seafood = 'Red Mobster Seafood'	#rate of seafood is 1 slimecoin to 9 hunger
vendor_diner = "Smoker's Cough"	#rate of drinks are 1 slimecoin to 15 hunger
vendor_beachresort = "Beach Resort" #Just features clones from the Speakeasy and Red Mobster
vendor_countryclub = "Country Club" #Just features clones from the Speakeasy and Red Mobster
vendor_farm = "Farm" #contains all the vegetables you can !reap
vendor_none = "None" #Currently used for millable items so that they can't be bought from any vendor
# stock ids
stock_kfc = "kfc"
stock_pizzahut = "pizzahut"
stock_tacobell = "tacobell"

# default stock rates
default_stock_market_rate = 1000
default_stock_exchange_rate = 1000000

# dye ids
dye_black = "blackdye"
dye_maroon = "maroondye"
dye_green = "greendye"
dye_brown = "browndye"
dye_tan = "tandye"
dye_purple = "purpledye"
dye_teal = "tealdye"
dye_orange = "orangedye"
dye_gray = "graydye"
dye_red = "reddye"
dye_lime = "limedye"
dye_yellow = "yellowdye"
dye_blue = "bluedye"
dye_fuchsia = "fuchsiadye"
dye_aqua = "aquadye"
dye_white = "whitedye"


# A map of name to EwWeather objects.
weather_map = {}
for weather in weather_list:
	weather_map[weather.name] = weather

# All food items in the game.
food_list = [
	EwFood(
		id_food = "slimentonic",
		alias = [
			"tonic",
		],
		recover_hunger = 18,
		price = 2,
		inebriation = 2,
		str_name = 'slime n\' tonic',
		vendors = [vendor_bar, vendor_countryclub],
		str_eat = "You stir your slime n' tonic with a thin straw before chugging it lustily.",
		str_desc = "The drink that has saved more juveniles’ lives than any trip to the nurse’s office could.",
		ingredients = "purplekilliflower",
	),
	EwFood(
		id_food = "slimacolada",
		alias = [
			"colada",
		],
		recover_hunger = 27,
		price = 3,
		inebriation = 2,
		str_name = 'slima colada',
		vendors = [vendor_bar, vendor_beachresort],
		str_eat = "You slurp down the delicious tropical delicacy and you are temporarily immobilized by a severly, splitting brain freeze. You double down to numb the pain.",
		str_desc = "Perfect for if you like getting caught in the acid raid, training at the dojo, have half a megaslime, "
				   "or like gunning down juvies at midnight in the dunes of the Mojave. Not great for much else, though."
	),
	EwFood(
		id_food = "slimekashot",
		alias = [
			"shot",
			"slimeka",
		],
		recover_hunger = 9,
		price = 1,
		inebriation = 2,
		str_name = 'shot of slimeka',
		vendors = [vendor_bar],
		str_eat = "You toss back the glowing, hissing substance, searing the back of your throat and tearing up a bit. You might need to see a doctor.",
		str_desc = "Made with pure, unrefined sludge from the city’s harbor. Just about as damaging to the colon as a sawed-off shotgun blast."
	),
	EwFood(
		id_food = "cabernetslimeignon",
		alias = [
			"wine",
			"cabernet",
			"slimeignon",
			"bottle",
		],
		recover_hunger = 36,
		price = 99,
		inebriation = 4,
		str_name = 'bottle of vintage cabernet slimeignon',
		vendors = [vendor_bar],
		str_eat = "Ahh, you have a keen eye. 19XX was an excellent year. You pop the cork and gingerly have a sniff. "
				  "Then you gulp the whole bottle down in seconds, because fuck it.",
		str_desc = "A sophisticated drink for a sophisticated delinquent such as yourself. You're so mature for your age."
	),
	EwFood(
		id_food = "slimynipple",
		alias = [
			"nipple",
		],
		recover_hunger = 9,
		price = 1,
		inebriation = 2,
		str_name = 'slimy nipple',
		vendors = [vendor_bar],
		str_eat = "You gulp down the green, creamy beverage with little care to its multi-layered presentation.",
		str_desc = "Of all the drinks with shitty names, this one tastes the worst."
	),
	EwFood(
		id_food = "slimeonthebeach",
		alias = [
			"beach",
		],
		recover_hunger = 27,
		price = 3,
		inebriation = 2,
		str_name = 'slime on the beach',
		vendors = [vendor_bar],
		str_eat = "You look pretty stupid drinking this fluorescent drink with a lil umbrella in it, but you don't care. Bottoms up!",
		str_desc = "When you told the bartender you wanted slime on the beach, about a dozen other guys at the bar chuckled under their breath and "
				   "hilariously added “Yeah, wouldn’t we all,” before beating the shit out of you outside afterward."
	),
		EwFood(
		id_food = "goobalibre",
		alias = [
			"goo",
		],
		recover_hunger = 27,
		price = 3,
		inebriation = 2,
		str_name = 'gooba libre',
		vendors = [vendor_bar],
		str_eat = "You sip the slime and soft drink concoction, causing it to ooze tartly down your throat. Sorta nasty, but you still like it!",
		str_desc = "A sickening, bright green marriage of slime and Mountain Dew. Last time you attempted to ordered it you had tried to convince the bartender you were over 21 "
				   "for half an hour, before finally giving up and just ordering the Dew."
	),
		EwFood(
		id_food = "manhattanproject",
		alias = [
			"manhattan",
			"mp",
		],
		recover_hunger = 45, #hehe dude like 1945 like when we bombed japan haha fuck yeah dude up high
		price = 5,
		inebriation = 8,
		str_name = 'manhattan project',
		vendors = [vendor_bar],
		str_eat = "You guzzle your drink before slamming it back down on the countertop. Your courage soars as the alcohol hits your bloodstream with the force of an atomic bomb.",
		str_desc = "We got tired of waiting for the bombs to drop so we made our own."
	),
	EwFood(
		id_food = "slimymary",
		alias = [
			"mary",
		],
		recover_hunger = 27,
		price = 3,
		inebriation = 2,
		str_name = 'slimy mary',
		vendors = [vendor_bar],
		str_eat = "This drink smells pretty nasty even by NLACakaNM standards. But what are you gonna do, NOT drink it?",
		str_desc = "This drink contains an easter egg. To find it, all you have to do is stand in your bathroom with the lights off and your back turned from the mirror. "
				   "Say it’s name three times, turn around and open your eyes. Congratulations! Your wallets missing and I’m fucking your girlfriend."
	),
	EwFood(
		id_food = "slimestout",
		alias = [
			"stout",
			"beer",
		],
		recover_hunger = 36,
		price = 4,
		inebriation = 2,
		str_name = 'stein of dark slime stout',
		vendors = [vendor_bar],
		str_eat = "You chug the heavy liquor with moderate vigor. It’s strong taste causes you to flinch, but in the end your thirst is quenched. "
				  "You’ve won this bout with the mighty slime stout. Thank you, goodnight.",
		str_desc = "A rich, dark green slime stout straight from the tap, with a head so thick you could rest a SlimeCoin on it. If it were a physical currency, which it isn’t. "
				   "It’s a cryptocurrency. Duh, idiot. Maybe SlimeCorp will release a limited edition physical release for all those freak coin collectors out there one day."
	),
	EwFood(
		id_food = "water",
		alias = [
			"h20",
		],
		recover_hunger = 0,
		price = 0,
		inebriation = 0,
		str_name = 'glass of water',
		vendors = [vendor_bar],
		str_eat = "The bartender sighs as he hands you a glass of water. You drink it. You're not sure why you bothered, though.",
		str_desc = "It’s a room temperature glass of tap water. Abstaining from drinking calories has never tasted this adequate!"
	),
	EwFood(
		id_food = "razornutspacket",
		alias = [
			"rn",
			"razor",
			"nuts",
			"packet"
		],
		recover_hunger = 50,
		price = 8,
		inebriation = 0,
		str_name = 'packet of salted razornuts',
		vendors = [vendor_bar],
		str_eat = "You tear into the packet and eat the small, pointy nuts one at a time, carefully avoiding any accidental lacerations.",
		str_desc = "It's a packet of locally-grown razornuts, roasted and salted to perfection. Perfect for snacking!"
	),
	EwFood(
		id_food = "breadsticks",
		alias = [
			"sticks",
		],
		recover_hunger = 20,
		price = 2,
		inebriation = 0,
		str_name = 'bundle of five breadsticks',
		vendors = [vendor_pizzahut],
		str_eat = "You gnaw on each stale breadstick like a dog chews on his bone, that is to say for hours and with little purpose. You let it soak underneath a nearby soda machine, "
				  "allowing the carbonation to eat away at the carbohydrate rod. You swallow the soggy appetizer whole, in one long gulp with no chewing necessary. Nasty!!",
		str_desc = "A hard slab of five breadsticks, all stuck together to form a stale brick of cheap bread and even cheaper pre-grated parmesan and oregano flakes. "
				   "Eating this is going to require some creative thinking. Hell, you might as well !equip it, you could probably drop it from a two story building and "
				   "split someone’s fucking skull open with it like an anvil in an old cartoon."
	),
	EwFood(
		id_food = "pizza",
		alias = [
			"cheese",
			"slice",
		],
		recover_hunger = 40,
		price = 4,
		inebriation = 0,
		str_name = 'slice of cheese pizza',
		vendors = [vendor_pizzahut],
		str_eat = "You nab a hot, greasy slice of that cheesy pie and cram it into your eager craw! Radical, dude!!",
		str_desc = "A supposedly hot slice of cheese pizza. Some of it’s pre-grated cheese hasn't fully melted yet, and it’s crust is hard and chewy. Reality is a cruel mistress."
	),
	EwFood(
		id_food = "pepperoni",
		alias = [
			"peperoni",
			"pep"
		],
		recover_hunger = 60,
		price = 6,
		inebriation = 0,
		str_name = 'slice of pepperoni pizza',
		vendors = [vendor_pizzahut],
		str_eat = "You chomp right into the salty, spicy sausage slice, bro! Cowabunga, my dude!!",

		str_desc = "An apparently appetizing slice of pepperoni pizza. It’s crust is limp and soggy from the excess grease it's slathered in, which is about the only thing you can taste on it. Pure Bliss."

	),
	EwFood(
		id_food = "meatlovers",
		alias = [
			"meatlovers",
			"meat"
		],
		recover_hunger = 80,
		price = 8,
		inebriation = 0,
		str_name = 'slice of Meat Lover\'s® pizza',
		vendors = [vendor_pizzahut],
		str_eat = "You happily scarf down this carnivore's delight! You’re neausiating both metaphorically and literally by the sheer volume of animal fat you're ingesting! Tubular!! Hell yes!!",
		str_desc = "A thoroughly revolting slice Meat Lover's® pizza. You like meat, but you aren't sure if you're ready to love again."
	),
	EwFood(
		id_food = "wings",
		alias = [
			"buffalowings",
			"hotwings",
		],
		recover_hunger = 120,
		price = 12,
		inebriation = 0,
		str_name = 'box of twelve buffalo wings',
		vendors = [vendor_pizzahut],
		str_eat = "Hell yeah, bro! Your mouth burns with passion! Your lips are in agony! You accidentally wiped away a tear with a sauce salthered finger and now you’re blind! You’ve never felt so alive!!",
		str_desc = "Best eaten with several of your closest bros, forming a spicy pact that elevates your meager friendship to the highest form of union one can have with their bros. "
				   "Forged while eating the hottest chicken wings available and preferably crying in the process, the camaraderie experienced while sweating through the agony together lasts a lifetime. "
				   "It is a form of matrimony unparalleled in sentimentality, and it is not to be trifled with lightly. Nothing can break a spicy bro pact. Nothing."
	),
	EwFood(
		id_food = "taco",
		alias = [
			"softtaco",
		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'soft taco',
		vendors = [vendor_tacobell],
		str_eat = "You bite into the taco. Pretty good, you guess. It’s missing something… a blast of flavor, perhaps?",
		str_desc = "A limp, pitiful soft-shelled taco. Mirroring its own flabby, flaccid facade, it is the perfect food for weak-willed men without "
				   "the strong moral character needed to tame the wild, wicked blast of flavor found in more iconic Taco Bell tacos."
	),
	EwFood(
		id_food = "nachocheesetaco",
		alias = [
			"nachocheese",
			"nachotaco"
		],
		recover_hunger = 30,
		price = 3,
		inebriation = 0,
		str_name = 'Nacho Cheese taco',
		vendors = [vendor_tacobell],
		str_eat = "You slam your mouth into a cheesy blast of that iconic Nacho Cheese flavor!! **YEEAAAHHHH!!!!**",
		str_desc = "This flavor…!! It’s an explosion of artificial cheese flavors and shrapnel sized bits of soggy shell that vaguely reminds you of world famous Nacho Cheese Doritos!!"
	),
	EwFood(
		id_food = "coolranchtaco",
		alias = [
			"coolranch",
			"ranchtaco",
			"cr"
		],
		recover_hunger = 30,
		price = 3,
		inebriation = 0,
		str_name = 'Cool Ranch taco',
		vendors = [vendor_tacobell],
		str_eat = "You crash your teeth into an explosion of that dark horse Cool Ranch flavor!! Uhhhh... yeeaaahhhh!!",
		str_desc = "This flavor…?? It’s a mushy mess of poorly seasoned mystery meat and pre-grated cheese trapped in a miserable shell that unfortunately reminds you of Doritos’ *other flavor* that isn't Nacho Cheese."
	),
	EwFood(
		id_food = "quesarito",
		alias = [
			"qsr",
		],
		recover_hunger = 50,
		price = 5,
		inebriation = 0,
		str_name = 'chicken quesarito',
		vendors = [vendor_tacobell],
		str_eat = "You bite into a burrito, or something. It's got cheese in it. Whatever. You eat it and embrace nothingness.",
		str_desc = "This travesty reminds you of your favorite My Little Pony: Friendship is Magic character Fluttershy for reasons you can’t quite remember..."
	),
	EwFood(
		id_food = "steakvolcanoquesomachorito",
		alias = [
			"machorito",
			"quesomachorito"
			"svqmr",
			"volc"
		],
		recover_hunger = 130,
		price = 13,
		inebriation = 0,
		str_name = 'SteakVolcanoQuesoMachoRito',
		vendors = [vendor_tacobell],
		str_eat = "It's a big fucking mess of meat, vegetables, tortilla, cheese, and whatever else happened to be around. You gobble it down greedily!!",
		str_desc = "This pound of greasy, soggy, and flavorless artificially flavored fast food just broke through the damp, leaking paper bag they doubled wrapped it in. "
				   "Guess you're going to have to eat it off the floor."
	),
	EwFood(
		id_food = "coleslaw",
		alias = [
			"slaw",
			"op",
			"ghst"

		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'tub of cole slaw',
		vendors = [vendor_kfc],
		str_eat = "You lap at the cup of some gross white cabbage swimming in watery mayo. Why the fuck would you order this?",
		str_desc = "This side is so horrific you might just start being able to shoot dead people if you eat it."
	),
	EwFood(
		id_food = "biscuitngravy",
		alias = [
			"biscuit",
			"gravy"
		],
		recover_hunger = 20,
		price = 2,
		inebriation = 0,
		str_name = 'biscuit with a side of gravy',
		vendors = [vendor_kfc],
		str_eat = "You dip the stale biscuit into the miniature bucket of gravy, scarf it down, and then chug the rest. *Burp.*",
		str_desc = "A cold biscuit that could break the glass if you threw it at window and scalding hot gravy that they let burn away the filth and grime in their pots so they don't have to clean them."
	),
	EwFood(
		id_food = "chickenbucket",
		alias = [
			"bucket",
			"cucket", #kraks favorite
			"chicken"
		],
		recover_hunger = 320,
		price = 32,
		inebriation = 0,
		str_name = '8-piece bucket of fried chicken',
		vendors = [vendor_kfc],
		str_eat = "You stuff your face on the eight pieces of juicy limbs and hot, crispy skin carved from a winged beast. It’s calorie-rich flesh arouses your base instincts as a human, "
				  "triggering growls and snarls to all approach you while you feed. Your fingers and tongue are scalded and you don't give a shit.",
		str_desc = "An obscure amount of calories in a simple bucket, a convenient trough for you to consume your dystopian meal. While children are starving in third world countries, "
				   "you crush these family meals often and without remorse. Well, to be fair I don’t think even the starving African children would touch KFC. That shit is nasty. You have a problem."
	),
	EwFood(
		id_food = "famousbowl",
		alias = [
			"bowl",
		],
		recover_hunger = 40,
		price = 4,
		inebriation = 0,
		str_name = 'Famous Mashed Potato Bowl',
		vendors = [vendor_kfc],
		str_eat = "You scarf down a shitty plastic bowl full of jumbled-up bullshit. It really hits the spot!",
		str_desc = "It’s just not a meal unless it’s a potato-based meal with a calorie count in the six digits."
	),
	EwFood(
		id_food = "barbecuesauce",
		alias = [
			"bbq",
			"sauce",
			"saucepacket",
		],
		recover_hunger = 1,
		price = 0,
		inebriation = 0,
		str_name = 'packet of BBQ Sauce',
		vendors = [vendor_kfc],
		str_eat = "You discard what little is left of your dignity and steal a packet of barbeque sauce to slurp down. What is wrong with you?",
		str_desc = "You're not alone. Confidential help is available for free."
	),
	EwFood(
		id_food = "mtndew",
		alias = [
			"dew",
			"mountaindew",
			"greendew"
		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'Mtn Dew',
		vendors = [vendor_mtndew, vendor_vendingmachine],
		str_eat = "You fill your jumbo fountain drink vessel with vivid green swill and gulp it down.",
		str_desc = "Ah, a nice cold brew resembling a mix between battery acid and artificial various citrus flavorings. Sick!!"
	),
	EwFood(
		id_food = "bajablast",
		alias = [
			"bluedew",
		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'Mtn Dew Baja Blast',
		vendors = [vendor_mtndew, vendor_vendingmachine],
		str_eat = "You fill your jumbo fountain drink vessel with light bluish swill and gulp it down.",
		str_desc = "Ah, a nice cold brew resembling a mix between battery acid and artificial lime flavoring. Cool!!"
	),
	EwFood(
		id_food = "codered",
		alias = [
			"reddew",
		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'Mtn Dew Code Red',
		vendors = [vendor_mtndew, vendor_vendingmachine],
		str_eat = "You fill your jumbo fountain drink vessel with red swill and gulp it down.",
		str_desc = "Ah, a nice cold brew resembling a mix between battery acid and artificial cherry flavoring. Sweet!!"
	),
	EwFood(
		id_food = "pitchblack",
		alias = [
			"blackdew",
		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'Mtn Dew Pitch Black',
		vendors = [vendor_mtndew, vendor_vendingmachine],
		str_eat = "You fill your jumbo fountain drink vessel with dark purple swill and gulp it down.",
		str_desc = "Ah, a nice cold brew resembling a mix between battery acid and artificial grape flavoring. Gnarly!!"
	),
	EwFood(
		id_food = "whiteout",
		alias = [
			"whitedew",
		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'Mtn Dew White-Out',
		vendors = [vendor_mtndew, vendor_vendingmachine],
		str_eat = "You fill your jumbo fountain drink vessel with pale cloudy swill and gulp it down.",
		str_desc = "Ah, a nice cold brew resembling a mix between battery acid and artificial lemon flavoring. Bodacious!!"
	),
	EwFood(
		id_food = "livewire",
		alias = [
			"orangedew",
		],
		recover_hunger = 10,
		price = 1,
		inebriation = 0,
		str_name = 'Mtn Dew Livewire',
		vendors = [vendor_mtndew, vendor_vendingmachine],
		str_eat = "You fill your jumbo fountain drink vessel with orange swill and gulp it down.",
		str_desc = "Ah, a nice cold brew resembling a mix between battery acid and artificial orange flavoring. Tubular!!"
	),
	EwFood(
		id_food = "shrimpcocktail",
		alias = [
			"shimp",
			"shrimp",
			"cocktail",
		],
		recover_hunger = 180,
		price = 18,
		inebriation = 0,
		str_name = 'a shrimp cocktail',
		vendors = [vendor_seafood, vendor_beachresort, vendor_countryclub],
		str_eat = "You pull out the prawns and pop ‘em into your mouth one after without removing their shell. You take vigorous swigs of the cocktail sauce straight "
				  "out of the glass to wash down the shards of crustacean getting lodged in the roof of your mouth.",
		str_desc = "A wavy glass of some shelled shrimp dipped in a weird, bitter ketchup that assaults your snout and mouth with unfortunate strength. Nothing is sacred."
	),
	EwFood(
		id_food = "halibut",
		alias = [
			"halibut",
		],
		recover_hunger = 270,
		price = 30,
		inebriation = 0,
		str_name = 'a grilled halibut',
		vendors = [vendor_seafood],
		str_eat = "You scarf down some delicious grilled halibut for the helluvit and it’s accompanying sides for the sidesuvit.",
		str_desc = "A grilled hunk of halibut, served with chipotle dirty rice and corn."
	),
	EwFood(
		id_food = "salmon",
		alias = [
			"salmon",
		],
		recover_hunger = 450,
		price = 52,
		inebriation = 0,
		str_name = 'a wood fired salmon',
		vendors = [vendor_seafood],
		str_eat = "You swallow the wood fired salmon without saving any of its smoky aftertaste! Aww man, so much for the extra 2 SlimeCoin…",
		str_desc = "A wood fired slice of salmon, served with a Dijon glaze and scalloped potatoes and broccoli on the side."
	),
	EwFood(
		id_food = "mahimahi",
		alias = [
			"mahimahi",
		],
		recover_hunger = 360,
		price = 40,
		inebriation = 0,
		str_name = 'a sauteed mahi mahi',
		vendors = [vendor_seafood],
		str_eat = "You gobble up the sauteed mahi mahi with lighting speed, reducing the proud fish into liquid in a matter of seconds.",
		str_desc = "A sauteed measurement of mahi mahi, with a lemon pepper crust and served with scalloped potatoes and spinach."
	),
	EwFood(
		id_food = "scallops",
		alias = [
			"scallops",
			"scl",
			"fish nuggies"
		],
		recover_hunger = 540,
		price = 60,
		inebriation = 0,
		str_name = 'pan-seared scallops',
		vendors = [vendor_seafood],
		str_eat = "You lean your head back, grab a few scallops, and try throwing them up into air and landing them in your mouth. This goes extremely poorly.",
		str_desc = "Some pan-seared scallops, served with goat cheese grits, sweet corn, and asparagus."
	),
	EwFood(
		id_food = "clamchowder",
		alias = [
			"clam",
			"chowder",
		],
		recover_hunger = 90,
		price = 10,
		inebriation = 0,
		str_name = 'a cup of clam chowder',
		vendors = [vendor_seafood],
		str_eat = "You scoop out a glob of the hearty chowder and clench your fist above your head, letting it drizzle down all over your face and into your eager mouth. You’re a fucking freak.",
		str_desc = "A bowl of New England clam chowder, served to you cold and runny in Arizona."
	),
	EwFood(
		id_food = "steaknlobster",
		alias = [
			"lobster",
			"lob",
			"snl",
			"lb"
		],
		recover_hunger = 720,
		price = 80,
		inebriation = 0,
		str_name = 'a rock lobster tail and a sirloin steak',
		vendors = [vendor_seafood],
		str_eat = "You discard the napkin immediately, along with the silverware trapped inside of it, opting to instead to eat the meal with your hands. "
				  "You pry the lobster from its shell first, ramming it into your mouth and taking a shot of melted butter to soften it up while you chew. "
				  "You continue onto the steak, carefully sliced against the grain, and smother it in half a bottle of A1 sauce and just start to suck on the two inch pieces "
				  "as if they were a jawbreaker or some other hard candy. You suck on the dead animal until it moistens to the point of liquefying, a solid hour and a half each. "
				  "You burp loudly. Man, what an unforgettable dinner!",
		str_desc = "A grilled 12oz sirloin steak and similarly sized rock lobster tail, served with scalloped potatoes, broccoli, asparagus, shallot herb butter "
				   "along side a portrait of the chef that was autographed and kissed with a vibrant red lipstick. What, does he think he’s better than you? "
				   "You break the portrait with your fist and your hand starts to bleed."
	),
	EwFood(
		id_food = "kingpincrab",
		alias = [
			"crab",
			"kingpin",
			"kp",
			"crb",
			"krb",
			"pin"
		],
		recover_hunger = 630,
		price = 70,
		inebriation = 0,
		str_name = 'an Arizonian Kingpin Crab',
		vendors = [vendor_seafood],
		str_eat = "You’re too weak to properly crack the mighty crabs’ carapaces, even with the proper crab carapace cracking crackers. After about 10 minutes of desperately trying to, "
				  "you just whip out whatever weapon you currently have quiped and start to viciously strike the crustaceans in a vain attempt to release their inner, delectable meat. "
				  "You just end up destroying the entire table you’re eating at.",
		str_desc = "Two imposing 1½ lb Arizonian Kingpin Crabs, steamed and split, served with a small side of melted butter. Their unique pink and purple carapaces that distinguish them are purely cosmetic, "
				   "but you’ll always think one color tastes better than the other. D’awww...",
	),
	EwFood(
		id_food = "champagne",
		alias = [
			"champagne",
		],
		recover_hunger = 99,
		price = 99,
		inebriation = 99,
		str_name = 'a bottle of champagne',
		vendors = [vendor_seafood],
		str_eat = "You shake the bottle violently before popping off the cork and letting the geyser of pink alcohol blast your waiter in the face. Haha, what a fucking dumbass.",
		str_desc = "The bubbly, carbonated bright pink liquid contained inside this bottle is very reminiscent of of the alcohol in Disney’s The Great Mouse Detective, "
				   "otherwise known as most appealing liquid on Earth until you remember it’s not straight edge."
	),
	EwFood(
		id_food = "sparklingwater",
		alias = [
			"sparklingwater",
		],
		recover_hunger = 9,
		price = 1,
		inebriation = 0,
		str_name = 'a glass of sparkling water',
		vendors = [vendor_bar, vendor_seafood, vendor_countryclub, vendor_beachresort],
		str_eat = "You savor every bubble of this lightly carbonated bliss. Your eyes begin to tear up as you fondly regard your own ecstasy. ‘Ah, just like in Roma…’",
		str_desc = "It’s some water with bubbles in it. Snore!"
	),
	EwFood(
		id_food = "juviesroe",
		alias = [
			"roe",
		],
		recover_hunger = 99,
		price = 999,
		inebriation = 0,
		str_name = 'a bowl of decadent Juvie’s Roe',
		vendors = [vendor_seafood],
		str_eat = "You don’t really know how to eat caviar, so you just scoop some of the disgusting slop out of the tin with your bare hands and get crushed fish eggs all over your mouth "
				  "as you shovel it into your uncultured maw. It tastes, uh… high class? This was a waste of money.",
		str_desc = "A small tin of wild, matured Juvie’s roe. A highly sought after delicacy by the upper crust of the critical improshived juveniles of the city. "
				   "Considered by many to be the height of luxury, an utterly decadent show of unrivalled epicurean ecstasy. "
				   "Sure, some of the unwashed masses COULD describe the understated burst of flavor non-existent, reducing the whole dish to a weird, goopy mess, but you know better."

	),
	EwFood(
		id_food = "homefries",
		alias = [
			"fries",
		],
		recover_hunger = 15,
		price = 1,
		inebriation = 0,
		str_name = 'home fries',
		vendors = [vendor_diner],
		str_eat = "You cram as many overcooked cubes of potato into your oversized maw as possible.You choke painfully on some of the tiny bits that that bypass your poor attempts at chewing. You hunger for more.",
		str_desc = "A greasy, over salted, crispy pile of miniature potato chunks, ranging from the average cubes to smaller irregularly shaped, condensed bits of pure fried potato skin. "
				   "With a calorie count well above your recommended daily consumption in just a handful, you could subsist on these preservative riddled species of spud for well over a week and still gain weight. "
				   "Too bad you can’t stop yourself from guzzling an entire plates worth in 5 minutes. Oops."
	),
	EwFood(
		id_food = "pancakes",
		alias = [
			"flapjacks",
		],
		recover_hunger = 105,
		price = 7,
		inebriation = 0,
		str_name = 'stack of three pancakes',
		vendors = [vendor_diner],
		str_eat = "You drench your three flapjacks in a generous helping of maple syrup and slap a stick of butter on top for good measure. It’s a good thing you’ve drowned your pancakes in all this excess shit, "
				  "or you might have actually tasted them! The soggy, limp fried dough is so much more appetizing when all it’s innate flavor is overrun by pure sugary excess.",
		str_desc = "Pancakes are usually a pretty safe bet, no matter where you are. You can’t really mess up a pancake unless you’re specifically trying to burn it. Luckily, "
				   "the dedicated chefs in the kitchen are doing just that! Thank God, you almost got a decent meal in this city."
	),
	EwFood(
		id_food = "chickennwaffles",
		alias = [
			"belgium",
			"cnw",
		],
		recover_hunger = 135,
		price = 9,
		inebriation = 0,
		str_name = 'two chicken strips and a waffle',
		vendors = [vendor_diner],
		str_eat = "You promptly seperate the two chicken strips and waffle on to separate plates, quarantining them off completely from one another. "
				  "You dip the chicken strips into some ketchup and drizzle some syrup onto the waffles, making sure to NEVER combine the two bitter rivals and to cleanse your palette before switching between them. "
				  "Ah, the life of a picky eater, it’s hard and no one understands.",
		str_desc = "Waffles are the perfect test subject. Whether it’s a good waffle or a bad waffle, they’re all going to hover around the same average quality. So, "
				   "whenever you’re in a new town and you wanna judge the quality of any given breakfast diner, order the waffle and rest easy knowing that even the worst waffle isn’t really that bad. "
				   "Oh, this waffle? It’s terrible. At least you have two chicken strips that were clearly frozen and only heated up a couple of minutes before you received them. "
				   "For all of the loss in quality and flavor, you can't fuck up microwaving something."
	),
	EwFood(
		id_food = "frenchtoast",
		alias = [
			"toast",
			"ft",
			"egg bread"
		],
		recover_hunger = 90,
		price = 6,
		inebriation = 0,
		str_name = 'four slices of french toast',
		vendors = [vendor_diner],
		str_eat = "You brace untold misery, for your hopes and dreams to be smashed utterly and irreparably, and most importantly to have wasted 12 SlimeCoin on the worst meal of your life. "
				  "Every hair on your body stands upright, as if preparing for a betrayal fueled stroke. You bite into the toast, and "
				  "as soon as the sweet pastry touches your tongue you feel as though you finally resonate with the ending of critically acclaimed children’s movie Ratatouille. "
				  "The bread is fluffy, light, and pleasantly moist, the perfect distribution of cinnamon and nutmeg, mixed with light sprinkles of sugar and vanilla, "
				  "create a french toast that is sweet but not sickeningly so. You can’t believe you’re saying this, but… it’s perfect! Your compliments to the chef, you guess.",
		str_desc = "French toast is the hardest to perfect out of the legendary fried dough trio. Requiring even cursory amounts of knowledge or expertise in the kitchen proves "
				   "to be too much for the chefs of diners nationwide. And unlike both the pancake and the waffle, there is a huge difference between a good french toast and a bad french toast. "
				   "There is nothing more euphoric than biting into a fluffy, moist, and sweet piece of good french toast, while conversely there is nothing that invokes the image of pigs greedily "
				   "eating trash in their trough than the feeling of a sticky glob of undercooked dough slide down your throat from a bad french toast. You really have to be sure that the restaurant "
				   "you’re ordering french toast knows what they’re doing, or else your night is ruined. Now, take a wild guess if the chefs at the Smoker’s Cough know what they’re doing."
	),
	EwFood(
		id_food = "friedeggs",
		alias = [
			"eggs",
		],
		recover_hunger = 45,
		price = 3,
		inebriation = 0,
		str_name = 'two sunny side up eggs',
		vendors = [vendor_diner],
		str_eat = "You isolate the yolks from your two fried eggs with surgical precision, leaving a clump of egg whites scraps and two perfectly contained yellow bubbles waiting to burst. "
				  "You salt and pepper them both thoroughly before eating one after another, first chewing on the slightly discolored egg whites and then bursting each egg yolk whole in your "
				  "mouth and letting the runny, golden goo to coat your insides.",
		str_desc = "Sure, you like your egg yolks runny, but given by their snotty, green discoloration, it’s pretty likely these eggs were severely undercooked. Oh well, salmonella here we come!"
	),
	EwFood(
		id_food = "eggsbenedict",
		alias = [
			"benedict",
			"benny",
		],
		recover_hunger = 75,
		price = 5,
		inebriation = 0,
		str_name = 'an eggs benedict',
		vendors = [vendor_diner],
		str_eat = "Even though you’re pretty sure you know what an eggs benedict is, you aren’t sure you know how to eat it. You pick up the muffin and just take a bite out of it directly, "
				  "hollandaise sauce and egg yolk coat your nostrils and generally splatters all over your face. Who would eat something like this????",
		str_desc = "An English muffin topped off with some ham, a poached egg, and hollandaise sauce. It seems like the sort of food that’d you would enjoy, it’s customizable and leans itself "
				   "to quirky variants, it’s pretty easy to make, it has an egg on it… still, the food comes across as menacing. It’s thick sauce masks it’s ingredients, what secrets could it be "
				   "hiding? You guess there’s only one way to find out. Gulp!"
	),
	EwFood(
		id_food = "scrambledeggs",
		alias = [
			"scrambled",
		],
		recover_hunger = 60,
		price = 4,
		inebriation = 0,
		str_name = 'two scrambled eggs',
		vendors = [vendor_diner],
		str_eat = "You attempt to strangle your ketchup bottle for the state mandated dollop of ketchup to be adequately mixed into your scrambled egg when tragedy strikes! The bottle is empty! "
				  "It blasts out specs of ketchup and a funny noise a few times before you throw it against the wall in ballistic anger. You are forced to eat the eggs… plain. DEAR GOD!!!!",
		str_desc = "Some scrambled eggs. Come on, you know what scrambled eggs are, right? Do I have to spell out everything for you? Do you want me to stay awake all night and come up with immature "
				   "jokes and puns for every one of these fucking things? Come on kid, get real."
	),
	EwFood(
		id_food = "omelette",
		alias = [
			"om",
		],
		recover_hunger = 120,
		price = 8,
		inebriation = 0,
		str_name = 'a western omelette',
		vendors = [vendor_diner],
		str_eat = "You pour plenty of hot sauce all over your omelette and shove bite after bite into your slobbering mouth. The heat from the sauce and the bell peppers builds to a breaking point, "
				  "causing you to blackout. You wake up an indeterminate amount of time later, covered in dried tears and sweat and your abdomen feeling as though you’re pregnant with Satan. You love pain.",
		str_desc = "A delicious Denver omelette, stuffed with diced ham, onions, and green peppers. Looks great! Hm? Excuse me? What the fuck is a ‘western omelette’? Do people on the east coast "
				   "seriously call Denver omelettes that? Are you joking me? You ask anyone on the sensible half of the country what the name of the best omelette is and they’ll bark back the long "
				   "and storied history of John D. Omelette and his rough-and-tumble youth growing up in the mean streets of the great state of Colorado’s capital. Do they not know what Denver is? "
				   "Do they think everything past the Appalachians are uncharted wilderness? Man, fuck you guys. We know were New York is, we know where Boston is, we know where Cincinnati is, we know "
				   "our geography of the east coast like the back of our hand and it’s about time you start memorizing ours. Eat shit."
	),
	EwFood(
		id_food = "orangejuice",
		alias = [
			"oj",
			"juice",
		],
		recover_hunger = 9,
		price = 1,
		inebriation = 0,
		str_name = 'a glass of orange juice',
		vendors = [vendor_diner],
		str_eat = "You swish around the decadent, pulpy orange juice in your mouth. This exacerbates your already poor dental hygiene, sending shockwaves of pain through your mouth as the "
				  "sugary liquid washes up against dozens of cavities all throughout your mouth. But, you don’t care. You’re in heaven.",
		str_desc = "A cavity creating, dental decaying, and enamel eroding glass of delicious orange juice. This vibrant citrus drink hits the spot any day of the week, any minute of the day, "
				   "and every second of your short, pathetic life. Coffee is a myth, water is a joke, soda is piss. #juiceprideworldwide"
	),
	EwFood(
		id_food = "milk",
		alias = [
			"cowjuice"
		],
		recover_hunger = 9,
		price = 1,
		inebriation = 0,
		str_name = 'a glass of milk',
		vendors = [vendor_diner],
		str_eat = "You take a swig of a nice, cold glass of whole milk and your palette is instantly clear of any sugary or syrupy foods you may have been eating. You are left in total cow induced euphoria.",
		str_desc = "A simple glass of milk. No more, no less. "
	),
	EwFood(
		id_food = "steakneggs",
		alias = [
			"steak",
			"sne",
		],
		recover_hunger = 150,
		price = 15,
		inebriation = 0,
		str_name = "two steak tips and two sunny side up eggs",
		vendors = [vendor_diner],
		str_eat = "You break the yolk of your two fried eggs immediately, letting the yolk run and pool around the steak tips, acting as a dipping sauce. With each mouthwatering bite of juicy, "
				  "medium rare steak coated in delicious, runny yolk, you reach a higher level of christ consciousness. How does no one else but you do this?",
		str_desc = "The only actually filling meal they serve at the diner. Between the two medium rare steak tips and the perfectly cooked sunny side up eggs, you’ve got enough protein in this one "
				   "meal to grow an extra muscle."
	),
	EwFood(
		id_food = "doubledown",
		alias = [
			"double",
			"down",
		],
		recover_hunger = 80,
		price = 8,
		inebriation = 0,
		str_name = 'Double Down',
		vendors = [vendor_kfc],
		str_eat = "You chomp into the meaty pseudo-sandwich! The Colonol's Special Sauce oozes over your lips and fingers, making you feel absolutely filthy.",
		str_desc = "From between two crispy chicken filets oozes the Colonel's Special Sauce. Haha, nasty!"
	),
	EwFood(
		id_food = "familymeal",
		alias = [
			"family",
			"meal",
			"fm",
		],
		recover_hunger = 480,
		price = 48,
		inebriation = 0,
		str_name = 'KFC Family Meal',
		vendors = [vendor_kfc],
		str_eat = "You feast on all manner of Southern homestyle delicacies out of this greasy fast food banquet! Your hands turn to blurs as you shovel handfuls of juicy fried calorie nuggets "
				  "into your biological furnace as possible, only slowly down to chug the mushy sides down the very same abyss. You reduce the dinner intend for 5+ in a manner of minutes, causing "
				  "frightened onlookers to scream and faint. You chew and chew until your jaw aches and tears stream down your cheeks.",
		str_desc = "A veritable menagerie of cheap crap and homestyle goodness. Various fried, dismembered limbs of a chicken, instant mashed potatoes and gravy, oily mac n' cheese, stale biscuits, "
				   "the list goes on and on. It’s enough to feed an army, or one you."
	),
	EwFood(
		id_food = "plutoniumchicken",
		alias = [
			"pluto",
			"plutonium",
		],
		recover_hunger = 160,
		price = 16,
		inebriation = 0,
		str_name = 'whole plutonium-battered fried baby chicken',
		vendors = [vendor_kfc],
		str_eat = "You crunch into the remains of this once-adorable animal. It’s odd metallic taste makes your tongue tingle in a most unsettling way. You try and blow a bubble with it but "
				  "you just end up spitting baby chicken bones five feet in front of you.",
		str_desc = "It resembles a miniature cooked chicken, save for an extra wing or too, or an hyperrealistic green peep. It is encrusted with an odd greenish-brown coating, which tickles "
				   "your skin upon touch. You could pop a few of these tiny things into your mouth at a time and feel their soul exit their body as you grind them into crispy dust. May adversely affect sperm count."
	),
	EwFood(
		id_food = "giantdeepdish",
		alias = [
			"gdd",
			"deepdish",
		],
		recover_hunger = 300,
		price = 30,
		inebriation = 0,
		str_name = 'giant deep-dish pizza',
		vendors = [vendor_pizzahut],
		str_eat = "You slurp down soupy slice after soupy slice of the sopping sauce-soaked pizza in a gruesome spectacle. Gnarly!!",
		str_desc = "This goopy, near liquid mass of cheap marinara and pre-grated mozzarella resembles a hearty soup more so than a pizza. It’s sauce and cheese acts as quicksand, "
				   "with anything placed on its surface sinking to the bottom, never to be seen again."
	),
	EwFood(
		id_food = "whackcalzone",
		alias = [
			"wc",
			"whack",
			"calzone",
		],
		recover_hunger = 210,
		price = 21,
		inebriation = 0,
		str_name = 'Whack Calzone',
		vendors = [vendor_pizzahut],
		str_eat = "You chomp into the colossal Italian confection in a mad craze, searing hot grease pours out from the edges and melted cheese explodes in every direction. De-LISH!!",
		str_desc = "It is literally just an upside-down pizza on top of another pizza. Your base, carnal desires will be the end of you one of these days."
	),
	EwFood(
		id_food = "nachosupreme",
		alias = [
			"ns",
			"nacho",
			"nachos",
			"supreme",
		],
		recover_hunger = 110,
		price = 11,
		inebriation = 0,
		str_name = 'Nacho Supreme',
		vendors = [vendor_tacobell],
		str_eat = "You shovel fistfuls of nacho detritus into your gaping maw. Your gums are savaged by the sharp edges of the crips corny chips.",
		str_desc = "A plate full of crisp tortilla chips onto which ground beef, sour cream, cheese, tomatoes, and various assorted bullshit has been dumped.",
	),
	EwFood(
		id_food = "energytaco",
		alias = [
			"et",
			"energy",
			"etaco",
		],
		recover_hunger = 90,
		price = 9,
		inebriation = 0,
		str_name = 'Energy Taco',
		vendors = [vendor_tacobell],
		str_eat = "Biting into this taco, your mouth is numbed by a sudden discharge of stored energy, accompanied by a worrisome flash of greenish light. You can't say for sure if it tasted good or not.",
		str_desc = "This resembles a normal taco, but where the cheese might normally be is a strange glowing green fluid. It occasionally sparks and crackles with limic energy."
	),
	EwFood(
		id_food = "mtndewsyrup",
		alias = [
			"syrup",
			"mdsyrup",
			"mds",
			"greensyrup",
		],
		recover_hunger = 100,
		price = 10,
		inebriation = 0,
		str_name = 'cup of pure undiluted MTN DEW syrup',
		vendors = [vendor_mtndew],
		str_eat = "You pour the molasses-like liquid down your throat. It stings your teeth and clings to your esophagus on the way down, but you feel suddenly invigorated as your blood sugar skyrockets!!",
		str_desc = "This thick, viscous green fluid reeks with a sickly-sweet citrusy odor.",
	),
	EwFood(
		id_food = "bajablastsyrup",
		alias = [
			"bbsyrup",
			"bbs",
			"bluesyrup",
		],
		recover_hunger = 100,
		price = 10,
		inebriation = 0,
		str_name = 'cup of pure undiluted MTN DEW Baja Blast syrup',
		vendors = [vendor_mtndew],
		str_eat = "You pour the molasses-like liquid down your throat. It stings your teeth and clings to your esophagus on the way down, but you feel suddenly invigorated as your blood sugar skyrockets!!",
		str_desc = "This thick, viscous blue fluid reeks with a sickly-sweet tropical odor."
	),
	EwFood(
		id_food = "coderedsyrup",
		alias = [
			"crsyrup",
			"crs",
			"redsyrup",
		],
		recover_hunger = 100,
		price = 10,
		inebriation = 0,
		str_name = 'cup of pure undiluted MTN DEW Code Red syrup',
		vendors = [vendor_mtndew],
		str_eat = "You pour the molasses-like liquid down your throat. It stings your teeth and clings to your esophagus on the way down, but you feel suddenly invigorated as your blood sugar skyrockets!!",
		str_desc = "This thick, viscous red fluid reeks with a sickly-sweet cherry odor."
	),
	EwFood(
		id_food = "pitchblacksyrup",
		alias = [
			"pbsyrup",
			"pbs",
			"blacksyrup",
			"purplesyrup"
		],
		recover_hunger = 100,
		price = 10,
		inebriation = 0,
		str_name = 'cup of pure undiluted MTN DEW Pitch Black syrup',
		vendors = [vendor_mtndew],
		str_eat = "You pour the molasses-like liquid down your throat. It stings your teeth and clings to your esophagus on the way down, but you feel suddenly invigorated as your blood sugar skyrockets!!",
		str_desc = "This thick, viscous purple fluid reeks with a sickly-sweet grapey odor."
	),
	EwFood(
		id_food = "whiteoutsyrup",
		alias = [
			"wosyrup",
			"wos",
			"whitesyrup",
		],
		recover_hunger = 100,
		price = 10,
		inebriation = 0,
		str_name = 'cup of pure undiluted MTN DEW White Out syrup',
		vendors = [vendor_mtndew],
		str_eat = "You pour the molasses-like liquid down your throat. It stings your teeth and clings to your esophagus on the way down, but you feel suddenly invigorated as your blood sugar skyrockets!!",
		str_desc = "This thick, viscous pale fluid reeks with a sickly-sweet citrusy odor."
	),
	EwFood(
		id_food = "livewiresyrup",
		alias = [
			"lwsyrup",
			"lws",
			"orangesyrup",
		],
		recover_hunger = 100,
		price = 10,
		inebriation = 0,
		str_name = 'cup of pure undiluted MTN DEW Livewire syrup',
		vendors = [vendor_mtndew],
		str_eat = "You pour the molasses-like liquid down your throat. It stings your teeth and clings to your esophagus on the way down, but you feel suddenly invigorated as your blood sugar skyrockets!!",
		str_desc = "This thick, viscous orange fluid reeks with a sickly-sweet orangey odor."
	),
	EwFood(
		id_food = "mexicanpizza",
		alias = [
			"mp",
			"mexican",
		],
		recover_hunger = 70,
		price = 7,
		inebriation = 0,
		str_name = 'Mexican pizza',
		vendors = [vendor_tacobell],
		str_eat = "You chomp right into the damp, haphazard mess of ethnic flavors and poor ingredients. The four sauces inexplicably just dumped on top drizzle down your chin and ruin your shirt. "
				  "You feel like a complete dumbass, because you are.",
		str_desc = "What the hell. A nauseating layer of refried beans and mushy, paste-like ground beef on top of and topped with a soggy, limp corn tortilla, finished with pre-grated, "
				   "processed cheese maxed out on preservatives, weeks-old diced tomatoes, and a mysterious dark red, viscous liquid referred to only as “Mexican Pizza Sauce.” Oh joy!"
	),
	EwFood(
		id_food = "doublestuffedcrust",
		alias = [
			"dsc",
			"stuffed",
			"stuffedcrust",
			"double",
			"doub",
			"dou"
		],
		recover_hunger = 500,
		price = 50,
		inebriation = 0,
		str_name = 'double Original Stuffed Crust® pizza',
		vendors = [vendor_pizzahut],
		str_eat = "You gaze upon the unholy, excessive pile of dough, pepperoni, grease, marinara and cheese you imprudently ordered. Tepidly, you bring the first crud slice to your tongue, "
				  "letting the melted cheese drizzle unto your awaiting tongue. And, just as a beast would be reduced to a state of pure carnal hunger and lust after acquiring it’s first taste of flesh and blood, "
				  "you enter a state of sheer wilderness, stuffing each stuffed crust into your teeth and gums and tongue and throat. You scream at the top of your lungs. Sicknasty, dude!!",
		str_desc = "Nothing can articulate the sheer awesomeness of this pizza. Always thought to be theoretically possible and discussed in hushed tones in obscure circles on the fringe of acceptable dialogue, "
				   "but never achieved in practice, this heap of diary and dough can only truly be comprehended through several layers of abstraction. It is too big, too thick, too heavy and too deep. "
				   "To put it simply, however, it is a pizza. Specifically, an Original Stuffed Crust® pizza. But, everything is doubled. Every ingredient is doubled. The toppings are doubled, "
				   "the cheese is doubled, the pepperoni is doubled, the grease is doubled, the yeast is doubled and you fucking bet you could fit your whole forearm into the caverns they dare call a crust, "
				   "if it weren’t overflowing with double the molten, stretchy string cheese. And it doesn’t stop there, double the size, double the weight, "
				   "double the budget required to ward off lawsuits for double the colohestral, double the heart attacks. People die because of this pizza, "
				   "someone you know has or will die because of this item in your inventory right now. It’s made to order, piping hot and ready to be devoured by "
				   "whatever foolish egomaniac with enough hubris to challenge it’s supremacy. Bow down before it, beg and weep for your life and the life of the ones you love. "
				   "Chant it’s name, praise the harbinger of death you just acquired from Pizza Hut. Doubled Stuffed Crust. Doubled Stuffed Crust. DOUBLE STUFFED CRUST!! AAAAAAAAAH!!"
	),
	EwFood(
		id_food = "boxofchocolates",
		alias = [
			"box",
			"chocolates",
		],
		recover_hunger = 500,
		price = 25,

		inebriation = 0,
		str_name = 'box of chocolates',
		#vendors = [vendor_tacobell, vendor_pizzahut, vendor_kfc, vendor_bar, vendor_diner, vendor_seafood],
		#This was a Valenslime's Day only item, you shouldn't be able to order it anymore.
		str_eat = "You pop open the lid of the heart-shaped box and shower yourself in warm sugary delicates! Your face and shirt is grazed numerous times by the melted confections, smearing brown all over you. Baby made a mess.",
		str_desc = "A huge heart-shaped box of assorted, partially melted chocolates and other sweet hors d'oeuvres. Sickeningly sweet literally and metaphorically.",
	),
	EwFood(
		id_food = "pinkrowddishes",
		recover_hunger = 60,
		str_name = 'Pink Rowddishes',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Pink Rowddishes. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The sweet-smelling tubers stain your hands pink.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "sludgeberries",
		recover_hunger = 60,
		str_name = 'Sludgeberries',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Sludgeberries. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The thick syrup covering the green and teal berries makes your hands sticky.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "pulpgourds",
		recover_hunger = 60,
		str_name = 'Pulp Gourds',
		vendors = [vendor_farm],
		str_eat = "a",
		str_desc = "The easily malleable gourds form indents from even your lightest touch.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "joybeans",
		recover_hunger = 60,
		str_name = 'Joybeans',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Joybeans. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The sugary candy-like beans have a thick gel interior that rots your teeth.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "brightshade",
		recover_hunger = 60,
		str_name = 'Brightshade',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Brightshade. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The dangerously toxic chemicals that cover the flower bud burn your eyes and nose.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "direapples",
		recover_hunger = 60,
		str_name = 'Dire Apples',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Dire Apples. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The vicious acidity from from the cyan and orange apples makes your mouth contort in pain with every bite.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "purplekilliflower",
		recover_hunger = 60,
		str_name = 'Purple Killiflower',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Purple Killiflower. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The deep purple head has an extremely bitter aftertaste.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "razornuts",
		recover_hunger = 60,
		str_name = 'Razornuts',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Razornuts. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The sharp edges of the hard nut slice open your mouth so that you taste slight hints of copper from your blood every bite.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "poketubers",
		recover_hunger = 60,
		str_name = 'Poke-tubers',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Poke-tubers. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The lame, sad, lumpy roots barely support a bulbous crop that’s indiscernible taste is not complemented by it’s awkward texture.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "suganmanuts",
		recover_hunger = 60,
		str_name = 'Suganma Nuts',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Suganmanuts. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The difficult nuts infuriate you for reasons you don’t really underst-- HEY WAIT A SECOND!!",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "dankwheat",
		recover_hunger = 60,
		str_name = 'Dankwheat',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Dankwheat. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The damp barley milled from this moist wheat causes hallucinations and intoxication once digested fully.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "blacklimes",
		recover_hunger = 60,
		str_name = 'Black Limes',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Black Limes. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The sour juice squeezed from just one of these small dark grey limes can flavor an entire production of Warheads hard candy.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "phosphorpoppies",
		recover_hunger = 60,
		str_name = 'Phosphorpoppies',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Phosphorpoppies. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The vivid and unnatural colors of this plant reveal it’s man made origin. Some say SlimeCorp designed the plant’s addictive and anxiety/paranoia inducing nature to keep juveniles weak and disenfranchised.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "sourpotatoes",
		recover_hunger = 60,
		str_name = 'Sour Potatoes',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Sour Potatoes. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The staple of many unhealthy juveniles’ diet. It’s revolting taste leaves much to be desired.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "bloodcabbages",
		recover_hunger = 60,
		str_name = 'Blood Cabbages',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Blood Cabbages. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "The dripping mass of dark crimson leaves have become the staple special effects tool for aspiration amatuer filmmakers in the city for it’s uncanny resemblance to human blood.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "pawpaw",
		recover_hunger = 60,
		str_name = 'Pawpaw',
		vendors = [vendor_farm],
		str_eat = "You chomp into the raw Pawpaw. It isn't terrible, but you feel like there is a more constructive use for it.",
		str_desc = "An American classic.",
		time_expir = farm_food_expir,
	),
	EwFood(
		id_food = "pinkrowdatouille",
		recover_hunger = 1200,
		str_name = 'Pink Rowdatouille',
		ingredients = "pinkrowddishes",
		str_eat = "You gingerly nibble on the fancy vegetables. It’s nostalgic taste sends you right back to your childhood, and your first encounter with the law. You had to get sent to the New Los Angeles City aka Neo Milwaukee Juvenile Detention Center somehow, after all. It feels like it happened so long ago, and yet, you can remember it like it was yesterday.",
		str_desc = "Thinly sliced rounds of Pink Rowddish and other colorful vegetables are slow roasted and drizzled with special sauce. It seems simple enough, it can’t taste THAT good, can it?",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "sludgeberrypancakes",
		recover_hunger = 800,
		str_name = 'Sludgeberry Pancakes',
		ingredients = "sludgeberries",
		str_eat = "You pick up the stack of pancakes with your hands, holding and biting into them as if they were a hamburger. Thick syrup coats your hands and mouth, ready to be licked off after the main meal has concluded.",
		str_desc = "Fluffy flapjacks filled with assorted Sludgeberries and topped with a heaping helping of viscous syrup. You’ve died and washed up in the sewers. But, like, a nice part of the sewers. This express doesn’t really translate well into the setting.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "pulpgourdpie",
		recover_hunger = 800,
		str_name = 'Pulp Gourd Pie',
		ingredients = "pulpgourds",
		str_eat = "You pick up a piece like it's a goddamn slice of pizza, demolishing it in a few barbaric bites. Eventually you get your fill of the crust and just start scraping out the delicious Pulp Gourd filling goop and slathering it all over your mouth and tongue like you're a fucking mindless pig at his trough.",
		str_desc = "A warm, freshly baked pie. It's still molten, still solidifying Pulp Gourd filling beckons you like a siren lures a sailor. So many holidays have been ruined because of your addiction to this cinnamon imbued delicacy, and so many more will be in the future.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "joybeanpastemochi",
		recover_hunger = 800,
		str_name = 'Joybean Paste Mochi',
		ingredients = "joybeans",
		str_eat = "You pop the delicate confectionary into your mouth and start ravenously shredding it into barely digestible chewy chunks. Sweet paste is slathered across your mouth. Your teeth enamel is decimated, execution style.",
		str_desc = "A sickeningly sweet  Joy Bean paste filling encased in a small, round mochi covered in powdered sugar. It’s *proper* name is “Daifucku.”",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "brightshadeseeds",
		recover_hunger = 800,
		str_name = 'Brightshade Seeds',
		ingredients = "brightshade",
		str_eat = "You pop a few seeds into your mouth at a time, grinding them into dust with your molars and digesting their sweet, sweet single digit calories.",
		str_desc = "A bag of Brightshade seeds, unsalted and ready for ill-advised consumption.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "direapplejuice",
		recover_hunger = 800,
		str_name = 'Dire Apple Juice',
		ingredients = "direapple",
		str_eat = "You slurp down the delicious sugary juice! Hell yeah!",
		str_desc = "A 99% juice-like substance that tastes vaguely like Dire Apples! It’s so ubiquitous that you guarantee that if you rummaged through every school kid’s lunch in the city, you’d be sent to jail.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "purplekilliflowercrustpizza",
		recover_hunger = 1200,
		str_name = 'Purple Killiflower Crust Pizza',
		ingredients = "purplekilliflower",
		str_eat = "You take a hesitant nibble of the famously keto pizza slice before coming to the reality that sometimes healthy things CAN taste good! You shove the rest of the slice in your mouth, nearly choking. Deep inside of your body, you can feel your kidney begin to churn and convulse. That’s probably fine.",
		str_desc = "A deliciously dietary-accordant slice of Killiflower crusted pizza. Made by milling down Killiflower into fine crumbs, combining with various irradiated cheeses, and baking until even notorious ENDLSS WAR critic Arlo is impressed. Now THIS is how you lose weight!",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "razornutbutter",
		recover_hunger = 800,
		str_name = 'Razornut Butter',
		ingredients = "razornuts",
		str_eat = "You take a hefty spoonful of the thick mucilage, coating your mouth completely. It’ll take weeks to swallow the last of it.",
		str_desc = "A tub of chunky, creamy Razonut Butter. Co-star of countless childhood classics. You know it was invented by a Juvie, right?",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "jellyfilleddoughnut",
		recover_hunger = 800,
		str_name = 'Jelly-Filled Doughnut',
		ingredients = "poketubers",
		str_eat = "You chomp into the delicious jelly-filled doughnuOH GOD WHY THE FUCK DOES IT TASTE LIKE A TRADITIONAL JAPANESE ONIGIRI WITH A PICKLE PLUM FILLING WHO COULD HAVE PREDICTED THIS?!?!",
		str_desc = "These jelly-filled doughnuts seem appetizing enough, but you're no expert. You never really cared much for jelly-filled doughnuts. In fact, in most scenarios you'd pass them up in favor of another pastry or sugary snack.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "yourfavoritefood",
		recover_hunger = 800,
		str_name = '***Your Favorite Food***',
		ingredients = "suganmanuts",
		str_eat = "***You bite into your favorite meal!! It’s taste is literally indescribable!! You feel like you’re going retarded, your mind is clearly breaking!! Uwahhh!!***",
		str_desc = "***Your favorite meal!! You could go on for hours about how great this food is!! But, you won’t, because no one appreciates it as much as you do.***",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "dankwheattoast",
		recover_hunger = 800,
		str_name = 'Dankwheat Toast',
		ingredients = "dankwheat",
		str_eat = "You take a bite out of the Dank Wheat Toast, and immediately you begin to start staggering around, clearly lost in some sort of unearned pleasure.",
		str_desc = "A burnt, slightly soggy slice of Dank Wheat Toast. What more do you want out of me?",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "blacklimesour",
		recover_hunger = 800,
		str_name = 'Black Lime Sour',
		ingredients = "blacklimes",
		str_eat = "You take a swig of the obscure southern delicacy. Its overwhelming acidity tricks your mouth into generating quarts of saliva, refreshing your mouth and destroying your taste buds. Nifty!",
		str_desc = "A small paper cup with nothing but crushed ice, the juice of a Black Lime, a little salt, and about a pound of cocaine.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "phosphorpoppiesmuffin",
		recover_hunger = 800,
		str_name = 'Phosphorpoppies Muffin',
		ingredients = "phosphorpoppies",
		str_eat = "You remove the muffin head from the stump, before devouring the former and throwing the later as far away from you as humanly possible. Good riddance.",
		str_desc = "Oooh, muffins! Remember that? Gimme a thumbs up with you get this joke.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "sourpotatofrenchfries",
		recover_hunger = 800,
		str_name = 'Sour Potato French Fries',
		ingredients = "sourpotatoes",
		str_eat = "You bite into the fluffy, acidic french fries, occasionally dipping in into a selection of various dipping sauces such as hot slime and sweet slime. You divorce the actual flavor of the crispy exterior from it’s sour innards with a technique not unlike the one used to get the last drop of toothpaste out of it’s tube. Your face convulses in pain.",
		str_desc = "Some gloriously thick cut Sour Potato french fries accompanied by an embarrassment of tasty slime-based dipping sauces. What else could a juvenile asked for?? Maybe some sugar and baking soda, this shit is unbelievably acidic.",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "bloodcabbagecoleslaw",
		recover_hunger = 800,
		str_name = 'Blood Cabbage Coleslaw',
		ingredients = "bloodcabbage",
		str_eat = "You drop the semi-solidified puck of red coleslaw into your eager maw, upon which the faux gelletain instantly loses it’s form and start to crumble into drop down your face. You manage to digest a cabbage shred.",
		str_desc = "A congealed dark crimson slab of myoglobin encasing sparse strands of Blood Cabbage. It jiggles when you shake the cup it’s stored in. Why the fuck would you mill this?",
		time_expir = milled_food_expir,
	),
	EwFood(
		id_food = "pawpawfood",
		recover_hunger = 800,
		str_name = 'Pawpaw Food',
		ingredients = "pawpaw",
		str_eat = "You slowly drink the bitter, flavorless mush. Its… uh… food?",
		str_desc = "An unappetizing pile of Pawpaw Gruel. It’s just Pawpaw milled into something halfway between puke and diarrhea. The staple of a traditional Juvenile diet. ",
		time_expir = milled_food_expir,
	),
]

# A map of id_food to EwFood objects.
food_map = {}

# A list of food names
food_names = []

# A map of vendor names to their foods.
food_vendor_inv = {}

# Populate food map, including all aliases.
for food in food_list:
	food_map[food.id_food] = food
	food_names.append(food.id_food)

	# Add food to its vendors' lists.
	for vendor in food.vendors:
		vendor_list = food_vendor_inv.get(vendor)

		if vendor_list == None:
			vendor_list = []
			food_vendor_inv[vendor] = vendor_list

		vendor_list.append(food.id_food)

	for alias in food.alias:
		food_map[alias] = food

# list of crops you're able to !reap
vegetable_list = []

# seperate the crops from the normal foods
for v in food_list:
	if v.vendors != [vendor_farm]:
		pass
	else:
		vegetable_list.append(v)

vendor_stock_map = {
	vendor_kfc : stock_kfc,
	vendor_pizzahut : stock_pizzahut,
	vendor_tacobell : stock_tacobell
	}

howls = [
	'**AWOOOOOOOOOOOOOOOOOOOOOOOO**',
	'**5 6 7 0 9**',
	'**awwwwwWWWWWooooOOOOOOOOO**',
	'**awwwwwwwwwooooooooooooooo**',
	'*awoo* *awoo* **AWOOOOOOOOOOOOOO**',
	'*awoo* *awoo* *awoo*',
	'**awwwwwWWWWWooooOOOOOOOoo**',
	'**AWOOOOOOOOOOOOOOOOOOOOOOOOOOOOO**',
	'**AWOOOOOOOOOOOOOOOOOOOO**',
	'**AWWWOOOOOOOOOOOOOOOOOOOO**'
]

"""
	The list of item definitions. Instances of items are always based on these
	skeleton definitions.
"""
item_def_list = [
	EwItemDef(
		# Unique item identifier. Not shown to players.
		item_type = "demo",

		# The name of the item that players will see.
		str_name = "Demo",

		# The description shown when you look at an item.
		str_desc = "A demonstration item."
	),

	EwItemDef(
		item_type = it_item,
		str_name = "{item_name}",
		str_desc = "{item_desc}",
		item_props = {
			'id_name': 'normalitem',
			'context': 'context',
			'subcontext': 'subocontext',
			'item_name': 'Normal Item.',
			'item_desc': 'This is a normal item.',
			'ingredients': 'vegetable'
		}
	),

	# A customizable award object.
	EwItemDef(
		item_type = it_medal,
		str_name = "{medal_name}",
		str_desc = "{medal_desc}",
		soulbound = True,
		item_props = {
			'medal_name': 'Blank Medal',
			'medal_desc': 'An uninscribed medal with no remarkable features.'
		}
	),

	EwItemDef(
		item_type = it_slimepoudrin,
		str_name = "Slime Poudrin",
		str_desc = "A dense, crystalized chunk of precious slime."
	),

	EwItemDef(
		item_type = it_questitem,
		str_name = "{qitem_name}",
		str_desc = "{qitem_desc}",
		soulbound = True,
		item_props = {
			'qitem_name': 'Quest Item',
			'qitem_desc': 'Something important to somebody.'
		}
	),

	EwItemDef(
		item_type = it_food,
		str_name = "{food_name}",
		str_desc = "{food_desc}",
		soulbound = False,
		item_props = {
			'food_name': 'Food Item',
			'food_desc': 'Food.',
			'recover_hunger': 0,
			'price': 0,
			'inebriation': 0,
			'vendor': None,
			'str_eat': 'You eat the food item.',
			'time_expir': std_food_expir,
		}
	),

	EwItemDef(
		item_type = it_weapon,
		str_name = "{weapon_name}",
		str_desc = "{weapon_desc}",
		soulbound = False,
		item_props = {
			'weapon_type': 'Type of weapon',
			'weapon_desc': 'It\'s a weapon of some sort.',
			'weapon_name': 'Weapon\'s name',
			'ammo': 0,
			'married': 'User Id'
		}
	),
	EwItemDef(
		item_type = it_cosmetic,
		str_name = "{cosmetic_name}",
		str_desc = "{cosmetic_desc}",
		soulbound = False,
		item_props = {
			'cosmetic_name': 'Cosmetic Item',
			'cosmetic_desc': 'Cosmetic Item.',
			'rarity': rarity_plebeian
		}
	),
]

# A map of item_type to EwItemDef objects.
item_def_map = {}

# Populate the item def map.
for item_def in item_def_list:
	item_def_map[item_def.item_type] = item_def

poi_list = [
	EwPoi( # ENDLESS WAR
		id_poi = poi_id_endlesswar,
		alias = [
			"obelisk",
			"war",
			"ew"
		],
		str_in = "at the base of",
		str_enter = "arrive at",
		str_name = "ENDLESS WAR",
		str_desc = "Its bright, neon green color nearly blinds you when observed from this close. You are overwhelmed by an acute, menacing aura as you crane your neck to observe the obelisk in its entirety. You almost thought you saw it looking back down at you, but it was probably just your imagination. You shouldn’t stay here any longer than you have to, you always get a weird feeling in the pit of your stomach when you stick around for too long.",
		coord = (27, 16),
		channel = channel_endlesswar,
		role = "Endless War"
	),
	EwPoi( # slimecorp HQ
		id_poi = poi_id_slimecorphq,
		alias = [
			"slimecorp",
			"hq",
			"corp"
		],
		str_in = "in the lobby of",
		str_name = "SlimeCorp HQ",
		str_desc = "Here, businessmen carrying briefcases dripping with slime powerwalk from every direction to every other direction. They barely acknowledge your existence outside of muttering under their breath when they’re forced to sidestep around you and the other clueless juveniles loitering in their lobby. Above the first few floors begins the endless labyrinths of cubicles and office spaces that comprised the majority of the building. This corporate nightmare repeats itself for nearly every floor of the towering skyscraper. With its sleek, modern architecture and high-tech amenities, SlimeCorp HQ looks nothing like the rest of the city.\nPast countless receptionists' desks, waiting rooms, legal waivers, and at least one or two stainless steel vault doors, lay several slime donation rooms. All that wait for you in these secluded rooms is a reclined medical chair with an attached IV bag and the blinding light of a fluorescent light bulb. If you choose to !donate some of your slime, a SlimeCorp employee will take you to one of these rooms and inform you of the vast and varied uses of SlimeCoin, SlimeCorp’s hot new cryptocurrency.",
		coord = (27, 18),
		channel = channel_slimecorphq,
		role = "SlimeCorp HQ",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_downtown
	),
	EwPoi( # 1
		id_poi = poi_id_downtown,
		alias = [
			"central",
			"dt",
		],
		str_name = "Downtown NLACakaNM",
		str_desc = "Skyscrapers and high-rise apartments tower above the jam-packed, bustling city streets below for as far as the eye can see. In this dense concrete jungle, your attention is constantly being divided among a thousand different things. Neon, fluorescent signs flash advertisements for all manner of amenities and businesses. The streets rumble with the sound of engines and metal scraping from the subway system deep underground. Hordes of men and women from every imaginable background walk these cruel streets, trying desperately to eke out a pitiful existence for themselves. This district never unwinds from its constant 24/7 slime-induced mania for even a moment, let alone sleep.\nDowntown is the beating heart of New Los Angeles City, aka Neo Milwaukee. With settlements in the area predating the emergence of slime, its prime location along the newly formed coastline naturally grew it into the cultural, economic, and literal center of the city. Due to its symbolic and strategic importance, it's home to the most intense gang violence of the city. Gunshots and screams followed by police sirens are background noises for this district. Some say that this propensity for violence is result of the sinister influence from an old obelisk in the center of town, ominously called ENDLESS WAR. You aren’t sure if you believe that, though.\n\nThis area contains ENDLESS WAR, SlimeCorp HQ, the Slime Stock Exchange and the Downtown Subway Station. To the north is Smogsburg. To the East is the Green Light District. To the South is the Rowdy Roughhouse. To the Southwest is Poudrin Alley. To the West is Krak Bay. To the Northwest is Cop Killtown.",
		coord = (23, 16),
		coord_alias = [
			(24, 16),
			(25, 16),
			(25, 17),
			(25, 18),
			(23, 17),
			(23, 18)
		],
		channel = "downtown",
		role = "Downtown",
		property_class = property_class_s,
		is_capturable = True
	),
	EwPoi( # 2
		id_poi = poi_id_smogsburg,
		alias = [
			"smog",
			"smogs",
			"sb"
		],
		str_name = "Smogsburg",
		str_desc = "In every direction, smokestacks belch out copious amounts of pollution into the atmosphere, creating a thick cloud that shrouds the district in sickening smog. It covers the district so completely that you can barely make out what time day it is. Your lungs can’t take much more of standing here, just do what you want to do and get out.\nSmogsburg is comprise of dozens of slime refineries and poudrin mills that turn unrefined, raw materials like the sludge from the city’s harbor into useful, pure slime. Functioning as the city’s premier industrial sector, it is by far the district hardest on the environment.\n\nThis area contains the Bazaar and the Smogsburg Subway Station. To the North is Arsonbrook. To the Northeast is Little Chernobyl. To the East is Old New Yonkers. To the South is Downtown NLACakaNM. To the West is Cop Killtown. To the Northwest is Astatine Heights.",
		coord = (23, 11),
		coord_alias = [
			(24, 11),
			(25, 11)
		],
		channel = "smogsburg",
		role = "Smogsburg",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 3
		id_poi = poi_id_copkilltown,
		alias = [
			"cop",
			"cops",
			"killers",
			"killer",
			"killtown",
			"copkt",
			"ck",
			"cct",
			"ckt",
			"cathedral"
		],
		str_name = "Cop Killtown",
		str_desc = "Edifices of various sinister architectural styles rise above the pavement. Gothic cathedrals, Victorian buildings, and New England brownstone apartments all dyed cool, dark colors. This district even hosts a miniature Japantown, featuring stores and restaurants that clutter your vision with densely packed fluorescent signage and other visual noise. Often cloaked in shadow from the height of these imposing buildings, the narrow, cobblestone streets of this district are perfect to brood and foster your angst in.\nCop Killtown is the gang base of the hardboiled, and calculating Killers. St. Ben’s Cathedral looms menacing on the horizon.\nhttps://discord.gg/xSQQD2M\n\nThis area contains the Cop Killtown Subway Station. To the North is Astatine Heights. To the East is Smogsburg. To the Southeast is Downtown NLACakaNM. To the Northwest is Gatlingsdale.",
		coord = (17, 13),
		channel = channel_copkilltown,
		role = "Cop Killtown",
		factions = [
			faction_killers
		],
		pvp = False,
		property_class = property_class_a
	),
	EwPoi( # 4
		id_poi = poi_id_krakbay,
		alias = [
			"krak",
			"kb"
		],
		str_name = "Krak Bay",
		str_desc = "Long street blocks are are densely packed with stores and restaurants, mixed in with townhouses and accompanied by modern skyscrapers and sprawling in-door shopping malls. These amenities and a scenic view of the River of Slime on its coast makes this district a favorite of a juvenile out on the town.\nKrak Bay is a bustling commercial district, featuring stores from across the retail spectrum. From economic, practical convenience stores to high-class, swanky restaurants, Krak Bay has it all. It is also home to some of the most recognizable fixtures of the city’s skyline, most notably the Poudrintial Tower and the shopping mall at its base which contains the city’s prized food court.\n\nThis area contains the Food Court and the Krak Bay Subway Station. To the East is Downtown NLACakaNM. To the Southeast is Poudrin Alley. To the South is Ooze Gardens. To the Southwest is South Sleezeborough. To the West is North Sleezeborough. To the Northwest is Glocksbury.",
		coord = (16, 19),
		coord_alias = [
			(17, 19),
			(18, 19)
		],
		channel = "krak-bay",
		role = "Krak Bay",
		property_class = property_class_a,
		is_capturable = True
	),
	EwPoi( # 5
		id_poi = poi_id_poudrinalley,
		alias = [
			"poudrin",
			"pa"
		],
		str_name = "Poudrin Alley",
		str_desc = "Densely packed, claustrophobic mazes of residential apartments stand above poorly planned roads with broken streetlights that spark and flicker over the cracked pavement. Only the locals know how to navigate the residential labyrinth effectively, by utilizing the interconnected, narrow alleyways the district is named for.\nPoudrin Alley is the principal residential district of the city, outfitted with enough low-rent apartments for the lower-middle class to house the entire city on its own. Sadly, for most of the impoverished dredges of the city, these low rents just aren’t low enough and the majority of the apartments go unused.\n\nThis area contains the 7-11. To the Northeast is Downtown NLACakaNM. To the East is the Rowdy Roughhouse. To the South is Cratersville. To the Southwest is Ooze Gardens. To the Northwest is Krak Bay.",
		coord = (19, 23),
		channel = "poudrin-alley",
		role = "Poudrin Alley",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 6
		id_poi = poi_id_rowdyroughhouse,
		alias = [
			"rowdy",
			"rowdys",
			"rowdies",
			"roughhouse",
			"rowdyrh",
			"rr",
			"rrh"
		],
		str_name = "Rowdy Roughhouse",
		str_desc = "Cheap townhouses and abandoned warehouses host graffiti art on basically every surface. An almost completely overrun slum, many of the deteriorated buildings have been painted a bright pink by the gangsters that seized them. Overpopulated and underhoused, the majority of the residents have constructed shanty houses for themselves and gather around trash can bonfires. Loud music blasts from bass-heavy speakers all hours of the night, fueling the seemingly constant parties this district is known for.\nRowdy Roughhouse is the gang base of the hot blooded, and reckless Rowdys. In the heart of the district stands the Rowdy Roughhouse, for which the district is named. Yes, it’s confusing, we know.\nhttps://discord.gg/D6jwpU3\n\nThis area contains the Rowdy Roughhouse Subway Station. To the North is Downtown NLACakaNM. To the South is Wreckington. To the Southwest is Cratersville. To the West is Poudrin Alley.",
		coord = (25, 21),
		coord_alias = [
			(26, 21),
			(27, 21)
		],
		channel = channel_rowdyroughhouse,
		role = "Rowdy Roughhouse",
		factions = [
			faction_rowdys
		],
		pvp = False,
		property_class = property_class_c
	),
	EwPoi( # 7
		id_poi = poi_id_greenlightdistrict,
		alias = [
			"greenlight",
			"gld"
		],
		str_name = "Green Light District",
		str_desc = "Animated neon, fluorescent signs dominate your vision, advertising all conceivable earthly pleasures. This district’s main street consists of a long, freshly-paved road with brothels, bars, casinos and other institutions of sin lining either side of it. Among these is the city-famous Slime Casino, where you can gamble away your hard-earned SlimeCoin playing various slime-themed games. The ground is tacky with some unknown but obviously sinful grime.\nThe Green Light District is well-known for its illegal activities, almost completely being comprised by amenities of ill repute and vice.\n\nThis area contains the Slime Casino and the Green Light District Subway Station. To the East is Vagrant's Corner. To the Southeast is Juvie's Row. To the West is Downtown NLACakaNM.",
		coord = (28, 13),
		coord_alias = [
			(29, 13),
			(30, 13)
		],
		channel = "green-light-district",
		role = "Green Light District",
		property_class = property_class_a,
		is_capturable = True
	),
	EwPoi( # 8
		id_poi = poi_id_oldnewyonkers,
		alias = [
			"ony"
		],
		str_name = "Old New Yonkers",
		str_desc = "Rows of three-story brick condominiums with white marble moulding wind along lanes of old asphalt roads with faded markings. Spiked wrought-iron gates protect the lawn of the district’s principal institutions, like the senior center.\nOld New Yonkers is popular with the older citizens of the city, due to its incredibly boring, gentrified residential landscape. Modest outdoor malls sells useless shit like candles and soaps, and the elderly population fills up their lumpy, sagging bodies at chain restaurants like Applebee’s and fucking IHOP.\n\nTo the Northeast is New New Yonkers. To the Southeast is Vagrant's Corner. To the Southwest is Smogsburg. To the East is Little Chernobyl. To the Northwest is Brawlden.",
		coord = (32, 9),
		channel = "old-new-yonkers",
		role = "Old New Yonkers",
		property_class = property_class_a,
		is_capturable = True
	),
	EwPoi( # 9
		id_poi = poi_id_littlechernobyl,
		alias = [
			"chernobyl",
			"lilchernobyl",
			"lilchern",
			"lc"
		],
		str_name = "Little Chernobyl",
		str_desc = "Dilapidated office buildings overgrown with ivy and the bombed-out frames of unidentifiable structures comprise the majority of the housing for this sparsely populated district. Radioactive almost to the point of warding off thieves and vandals (but not quite), many people report seeing strange creatures and various cryptids roaming the abandoned power plant complex at night.\nLittle Chernobyl might not be much to look at or often discussed nowadays, but don’t be fooled by its current irrelevance. Long ago, it was home to Arizona's largest nuclear power plant. An electrical blackout caused a total safety system failure, leading in a cataclysmic nuclear meltdown. This caused nuclear waste to flood into the Grand Canyon and create the Slime Sea we know and love today.\n\nTo the North is Brawlden. To the East is Old New Yonkers. To the West is Arsonbrook.",
		coord = (25, 7),
		channel = "little-chernobyl",
		role = "Little Chernobyl",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 10
		id_poi = poi_id_arsonbrook,
		alias = [
			"arson",
			"ab"
		],
		str_name = "Arsonbrook",
		str_desc = "This district is seemingly eternally overcast, allowing the dark plumes of smoke from distant fires fade into the soft grey clouds. A thin layer of soot rests upon basically the entire district, providing nutrient-rich soil which the rural farmers in the north of the district take advantage of. In the south, enclaves of civilization have started to pop up, learning from the mistakes of previous generations and building out of brick instead of wood. Aesthetically, these settlements resemble a small mining town from the mountainous forests of the northwest, just replace the rugged terrain with flat land and the evergreens with burnt, charcoal frames of trees that used to be. A Starbucks tried to open here once.\nArsonbook is easily among the most peaceful districts of the city, as long as you count constant wildfires and destruction of property from arson as peaceful. The locals are used to that sort of thing though, so they’re pretty mellow. Kick back, relax, and don’t get too attached to your house if you plan on living here.\n\nThis area contains the Arsonbrook Farms and the Arsonbrook Subway Station. To the East is Brawlden. To the Southeast is Little Chernobyl. To the South is Smogsburg. To the West is Astatine Heights.",
		coord = (21, 3),
		coord_alias = [
			(22, 3),
			(23, 3)
		],
		channel = "arsonbrook",
		role = "Arsonbrook",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 11
		id_poi = poi_id_astatineheights,
		alias = [
			"astatine",
			"heights",
			"ah"
		],
		str_name = "Astatine Heights",
		str_desc = "Swanky modern condominiums jut out of the steep hills to the north, while to the south rows of picture-perfect suburban homes with disgustingly well-maintained lawns constrict around freshly-laid roads. Luxury boutiques and high-class restaurants compete for the wallets of privileged, rich yuppies.\nAstatine Heights is the home to many of the wealthiest men and women of the city, with many of the residents forcing their fratty Republican sons to the prestigious college N.L.A.C.U. in neighboring Gatlingsdale. The difference between Astatine Heights and other affluent districts of the city is that the majority of residents have not passed onto the elysian fields of retirement, and thus have at least a sliver of personality and ambition left in their community, however gentrified it might be.\n\nThis area contains NLACakaNM Cinemas, the Red Mobster Seafood Restaurant and the Astatine Heights Subway Station. To the East is Arsonbrook. To the Southeast is Smogsburg. To the South is Cop Killtown. To the Southwest is Gatlingsdale. To the West is Toxington.",
		coord = (17, 6),
		coord_alias = [
			(17, 5),
			(17, 4),
			(17, 3)
		],
		channel = "astatine-heights",
		role = "Astatine Heights",
		property_class = property_class_a,
		is_capturable = True
	),
	EwPoi( # 12
		id_poi = poi_id_gatlingsdale,
		alias = [
			"gatlings",
			"gatling",
			"gd"
		],
		str_name = "Gatlingsdale",
		str_desc = "Hundreds of small “nerdy” retail stores and ethnically-diverse restaurants are compact into a dense, bustling plaza just minutes from the prestigious N.L.A.C.U. college campus. Almost all of district is comprised of or controlled by the sprawling ivy league university. Featuring smoky cafes, vintage clothing boutiques, and independent bookstores, this district is perfectly catered to the pompous hipsters that flood its streets every day after class.\nGatlingsdale is a historic district, with many of its winding cobblestone roads and gaslamp streetlights dating back to the early days of the city.\n\nThis District contains New Los Angeles City University and the Gatlingsdale Subway Station. To the Northeast is Astatine Heights. To the Southeast is Cop Killtown. To the Southwest is Vandal Park. To the West is Polonium Hill. To the Northwest is Toxington.",
		coord = (13, 9),
		coord_alias = [
			(13, 10),
			(13, 11)
		],
		channel = "gatlingsdale",
		role = "Gatlingsdale",
		property_class = property_class_a,
		is_capturable = True
	),
	EwPoi( # 13
		id_poi = poi_id_vandalpark,
		alias = [
			"vandal",
			"park",
			"vp"
		],
		str_name = "Vandal Park",
		str_desc = "A laundry list of various sports amenities and public parks dot the landscape of this athletically minded district. These include soccer fields, skate parks, swimming pools, and of course the district’s famous Battle Arena.\nVandal Park’s numerous open spaces and its more-or-less clean air make it an attractive destination for juveniles seeking a stroll. Despite this you’ve still got to keep your wits about you here if you want to not get publicly executed against one of the pretty trees.\n\nThis area contains the Battle Arena. To the Northeast is Gatlingsdale. To the South is Glocksbury. To the Southwest is West Glocksbury. To the Northwest is Polonium Hill.",
		coord = (10, 12),
		channel = "vandal-park",
		role = "Vandal Park",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 14
		id_poi = poi_id_glocksbury,
		alias = [
			"glocks",
			"glock",
			"gb"
		],
		str_name = "Glocksbury",
		str_desc = "Semi-orderly residential neighborhoods with discolored white picket fences protecting unkempt lawns for as far as the eye can far. This district likes to pretend its a quiet suburb, but the regular screams and gunshots coupled with numerous chalk outlines of human bodies on the street make this hard to believe. You smell bacon. *Figurative* bacon. The cops must be lurking nearby somewhere.\nGlocksbury’s flaccid attempts at normalcy are fueled by it hosting the city’s police department, which is hilariously ineffectual and underfunded to the point of absurdity. In this city, the bumbling police act as target practice to the local gangs rather than actual authorities to be obeyed. But, they sure like to pretend they are.\n\nThis area contains the Glocksbury Subway Station. To the North is Vandal Park. To the Southeast is Krak Bay. To the South is North Sleezeborough. To the West is West Glocksbury.",
		coord = (8, 16),
		coord_alias = [
			(7, 16),
			(6, 16)
		],
		channel = "glocksbury",
		role = "Glocksbury",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 15
		id_poi = poi_id_northsleezeborough,
		alias = [
			"northsleezeboro",
			"nsleezeborough",
			"nsleezeboro",
			"nsleeze",
			"northsleeze",
			"nsb",
			"ns"
		],
		str_name = "North Sleezeborough",
		str_desc = "Sleepy brownstone apartments and about 50,000 different terrible pizza places populate this slow paced, gentrifying district. Outdoor malls have started to spring up here and there, mostly around the college campus of Neo Milwaukee State. Retired parents rest on benches, throwing crumbs of bread at birds and squandering the twilight years of their misspent life. Students with curious facial hair and suspenders lurk in vinyl record stores and horde ironic knick-knacks.\nNorth Sleezeborough residents really, really don't care about anything. It wouldn’t be fair to call them nihilistic, that implies self-reflection or philosophical quandary, they are just so lethargic that they might as well categorically be considered legally dead. Alongside these generally older occupants are younger students who have flocked to the dirt cheap public college of Neo Milwaukee State to continue their mediocre education.\n\nThis area contains Neo Milwaukee State and the North Sleezeborough Subway Station. To the North is Glocksbury. To the East is Krak Bay. To the South is South Sleezeborough.",
		coord = (10, 19),
		coord_alias = [
			(10, 20),
			(10, 21)
		],
		channel = "north-sleezeborough",
		role = "North Sleezeborough",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 16
		id_poi = poi_id_southsleezeborough,
		alias = [
			"southsleezeboro",
			"ssleezeborough",
			"ssleezeboro",
			"ssleeze",
			"southsleeze",
			"ssb",
			"ss"
		],
		str_name = "South Sleezeborough",
		str_desc = "Dreary townhouses and red brick apartments brush up against the embarrassingly inauthentic approximations oriental architectural styles of the city’s Chinatown. There, pagodas and dragon gates take up every square inch of land that asian restaurants and law firms don’t. From the streets it’s hard to make out the sky from the tacky lanterns and web of unintelligible business signs.\nSouth Sleezeborough’s residential streets are as boring as can be, but wade through them and you’ll have a fun time ordering popping bubble tea and lemon roll cakes from bakeries and sparing with your buddies at the Dojo.\n\nThis area contains the Dojo and the South Sleezeborough Subway Station. To the North is North Sleezeborough. To the Northeast is Krak Bay. To the East is Ooze Gardens. To the West is Crookline.",
		coord = (12, 22),
		coord_alias = [
			(12, 23),
			(12, 24),
			(12, 25),
			(12, 26),
			(12, 27)
		],
		channel = "south-sleezeborough",
		role = "South Sleezeborough",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 17
		id_poi = poi_id_oozegardens,
		alias = [
			"ooze",
			"gardens",
			"og"
		],
		str_name = "Ooze Gardens",
		str_desc = "Walking paths connect dozens of greenhouses and gardens featuring rare, exotic, and irradiated flora. This district is really just one big park, broken up into several sections hosting different types of botanical attractions, as well as several museums and even the city’s zoo. Musical concerts are often held in one of the several outdoor amphitheatres that are scattered across the district. Truly, an amusement park for lovers of nature and culture.\nOoze Gardens is a clear cultural outlier of the city. The residents of this district are largely pacifist, choosing music, love, and psychedelic drugs over violent crime. They make you sick.\n\nThis area contains the Ooze Gardens Farms. To the North is Krak Bay. To the Northeast is Poudrin Alley. To the East is Cratersville. To the West is South Sleezeborough.",
		coord = (14, 25),
		channel = "ooze-gardens",
		role = "Ooze Gardens",
		property_class = property_class_a,
		is_capturable = True
	),
	EwPoi( # 18
		id_poi = poi_id_cratersville,
		alias = [
			"craters",
			"cville",
			"cv"
		],
		str_name = "Cratersville",
		str_desc = "Crumbling infrastructure is commonplace here. The craters and smaller potholes that give this district its name are scattered liberally across the streets and sidewalks. Unruly miners have refused to limit their excavating to the designated mining sector and scavenge even the residential roads for meager drops of slime.\nCratersville really sucks to live in. I mean, obviously. Look at this place. Even aside from the huge fucking holes everywhere, you’ve still got to deal with the constant sound of mining and dynamite explosions underground.\n\nThis area contains the Cratersville Mines and the Cratersville Subway Station. To the North is Poudrin Alley. To the Northeast is the Rowdy Roughhouse. To the East is Wreckington. To the West is Ooze Gardens.",
		coord = (19, 28),
		coord_alias = [
			(20, 28),
			(21, 28)
		],
		channel = "cratersville",
		role = "Cratersville",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 19
		id_poi = poi_id_wreckington,
		alias = [
			"wrecking",
			"wton",
			"ton",
			"wt"
		],
		str_name = "Wreckington",
		str_desc = "Piles of rubble and scrap metal lean against partially demolished buildings that barely remain standing. Sadly, these structures are often all the critically impoverished residents of Wreckington have to house themselves. Constant new construction projects promise new opportunities for the deteriorating district, but these promises are too often broken by lack of funding and interest. Jackhammers pummeling the asphalt and wrecking balls knocking down apartment complexes can be heard throughout the entire district, 24/7.\nWreckington isn’t completely barren however, its strategic location on the coast and cheap property makes its shipyard a favorite among unscrupulous sailors. It also features a ferry connection to Vagrant’s Corner, if you’re so inclined to visit the eastern districts.\n\nThis area contains the Smoker's Cough Diner, the Wreckington Ferry Port and the Wreckington Subway Station. To the North is the Rowdy Roughhouse. To the West is Cratersville.",
		coord = (27, 24),
		coord_alias = [
			(27, 25),
			(27, 26)
		],
		channel = "wreckington",
		role = "Wreckington",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 20
		id_poi = poi_id_juviesrow,
		alias = [
			"juvies",
			"jrow",
			"jr"
		],
		str_name = "Juvie's Row",
		str_desc = "The landscape of this district is completely defined by it containing the city’s largest mineshafts. Almost the entire district is has been dug up, the earth overturned by a crazed populace trying to soak up every drop of slime it can get its hands on. There are few permanent structures here, and even less infrastructure. Swathes of juveniles have constructed shanty houses out of discarded building materials, suffering from the intense pollution and poor living conditions just to be closer to the mine shaft entrances that jut out of the otherwise useless, rugged terrain. Makeshift bazaars and other rudimentary amenities have popped up in the horribly overcrowded tent cities.\nJuvie’s Row might just be the most populous district of the city, with every ambitious juvenile spending at least some of their formative days toiling underground to eke out a pitiful existence. Seeing all the gang unaligned juvies here fills you with pity, as well as disgust.\n\nThis area contains the Juvie's Row Mines, the Juvie's Row Farms and the Juvie's Row Subway Station. To the Northeast is Vagrant's Corner. To the Northwest is the Green Light District.",
		coord = (32, 18),
		channel = "juvies-row",
		role = "Juvie's Row",
		pvp = False,
		property_class = property_class_b
	),
	EwPoi( # 21
		id_poi = poi_id_slimesend,
		alias = [
			"slimes",
			"send",
			"end",
			"se"
		],
		str_name = "Slime's End",
		str_desc = "There’s not much to see here, as this sparsely populated district is mainly comprised of small residential enclaves and barren terrain. Maybe a tree here and there, I don’t know.\nSlime’s End is a narrow peninsula is bordered on both sides by the Slime Sea. The phosphorescence illuminates the sky with an eerily green glow.\n\n To the North is Vagrant's Corner.",
		coord = (40, 16),
		channel = "slimes-end",
		role = "Slime's End",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 22
		id_poi = poi_id_vagrantscorner,
		alias = [
			"vagrants",
			"vcorner",
			"vc"
		],
		str_name = "Vagrant's Corner",
		str_desc = "A foul, fishy smell pervades the entire district, emanating from the harbor. This wretched wharf is home to the seediest underbelly of the city, besides the neighboring Green Light District of course. Pirates and other seafaring scoundrels patron the local taverns and other haunts of ill repute while on shore leave. The harsh glow of the Slimea Sea illuminates the undersides of the innumerable docks that extend out from this district, as well as the heavy industrial equipment designed to pump slime into the cargo holds of outbound barges.\nVagrant’s Corner features the largest seaport of the city, with almost all seabound imports and exports funnel through it. It also features a ferry connection to Wreckington, if you’re so inclined to visit the southern districts.\n\nThis area contains The King's Wife's Son Speakeasy, and the Vagrant's Corner Ferry Port. To the North is New New Yonkers. To the Northeast is Assault Flats Beach. To the South is Slime's End. To the Southwest is Juvie's Row. To the West is the Green Light District. To the Northwest is Old New Yonkers.",
		coord = (37, 11),
		coord_alias = [
			(38, 11),
			(39, 11),
			(39, 10),
			(39, 9)
		],
		channel = "vagrants-corner",
		role = "Vagrant's Corner",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 23
		id_poi = poi_id_assaultflatsbeach,
		alias = [
			"assaultflats",
			"assault",
			"flats",
			"beach"
			"assflats",
			"afb"
		],
		str_name = "Assault Flats Beach",
		str_desc = "Colorfully painted wooden storefronts and towering condominium complexes peer out from the coastline of this scenic beach town. Most of the district is owned by the sprawling luxury resort the district is best known for, as well as virtually the entirety of the actual beach of Assault Flats Beach.\nAssault Flats Beach is by far one of if not the most expensive districts in the city to live in, due to its complete subjugation by the resort and accompanying security force, it is also the safest district to live in by a long shot. But, as you venture away from the coast you’ll begin to see more of the city’s standard crime rate return. Interestingly, the district is a favorite among archaeologists for its unprecedented density of jurassic fossils hidden deep underground. Some even say dinosaurs still roam the outskirts of the district to the north, but frankly that just seems ridiculous. I mean, we all know dinosaurs aren’t real.\n\nThis area contains the Resort, the Assault Flats Beach Blimp Tower and the Assault Flats Beach Subway Station. To the South is Vagrant's Corner. To the West is New New Yonkers.",
		coord = (40, 6),
		coord_alias = [
			(40, 5),
			(40, 4)
		],
		channel = "assault-flats-beach",
		role = "Assault Flats Beach",
		property_class = property_class_s,
		is_capturable = True
	),
	EwPoi( # 24
		id_poi = poi_id_newnewyonkers,
		alias = [
			"nnewyonkers",
			"nnyonkers",
			"nny"
		],
		str_name = "New New Yonkers",
		str_desc = "Nightclubs and trendy restaurants have popped up in slick, modern buildings while the same old, reliable brownstones host arcades, bowling alleys and other teenage favorites. Featuring probably the best nightlife in the city, New New Yonkers is a favorite hangout spot among the juveniles of the city and consequently has an alarming crime rate. Many of the older residents want to see these fun times come to an end however, seeking to emulate the gentrified suburbia of Old New Yonkers to the south. This is adamantly resisted by the rough-and-tumble youth, those who’s to say if this district will remain the bastion of good times it is today.\nNew New Yonkers is the best district to hang out in on a weekend with your friends. Really, what else can a district aspire to?\n\nTo the East is Assault Flats Beach. To the South is Vagrant's Corner. To the Southwest is Old New Yonkers. To the West is Brawlden.",
		coord = (36, 4),
		channel = "new-new-yonkers",
		role = "New New Yonkers",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 25
		id_poi = poi_id_brawlden,
		alias = [
			"den",
			"bd"
		],
		str_name = "Brawlden",
		str_desc = "Sturdy red brick apartments rise above the hard-knock streets. Gruff mechanics, plummers, and other workers of dirty jobs like to make their homes here, away from the pissy baby fucker fapper bullshit of the juvenile-populated inner districts. You can see them roaming the streets in their stained wife beaters, popping open the hoods of their cars and grunting dad noises. Sometimes they cross paths with one another and immediately upon locked eyesight engage in brutal fist fights. No one really knows why.\nBrawlden, despite being a largely rumble-and-tough inhabited primarily by dads is inexplicability the home of a high-tech laboratory run by SlimeCorp. Deep underground in an unassuming corner of this district lays a not-so-secret top secret laboratory dedicated to the study of Slimeoids. What are Slimeoids? You’ll just have to find out, buddy.\n\nThis area contains the Slimeoid Laboratory. To the East is New New Yonkers. To the Southeast is Old New Yonkers. To the South is Little Chernobyl. To the West is Arsonbrook.",
		coord = (28, 3),
		channel = "brawlden",
		role = "Brawlden",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 26
		id_poi = poi_id_toxington,
		alias = [
			"tox",
			"tton",
			"ttn",
			"tt",
			"tx"
		],
		str_name = "Toxington",
		str_desc = "You cover your mouth in a futile attempt to avoid breathing in the toxins rising from the nearby lakes and mineshafts. A thick fog of this foul-smelling, poisonous gas shrouds the entire district, making the land virtually uninhabitable. But, where there’s slime, people will settle. Juveniles from across the city are happy to spend their short lives in this hellhole for a chance to strike it rich.\nToxington has no redeemable aspects, outside of its abundance of slime veins underground and its lovely fishing spots above.\n\nThis area contains the Toxington Mines and the Toxington Subway Station. To the East is Astatine Heights. To the Southeast is Gatlingsdale. To the South is Polonium Hill. To the East is Charcoal Park.",
		coord = (9, 4),
		channel = "toxington",
		role = "Toxington",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 27
		id_poi = poi_id_charcoalpark,
		alias = [
			"charcoal",
			"park2",
			"cpark",
			"awkwardinitials",
			"cp",
			"ch"
		],
		str_name = "Charcoal Park",
		str_desc = "A completely unremarkable, quiet retirement community. The citizens are fed up with slime, honestly. Pathetic little gardens rest in front of the uneven parking lots of corporate complexes housing dentists, fortune-tellers, real estate agencies, and other equally dull and pointless ventures.\nCharcoal Park is where boring people go to die. No one is happy to be here.\n\nTo the East is Toxington. To the South is Polonium Hill.",
		coord = (3, 3),
		channel = "charcoal-park",
		role = "Charcoal Park",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi( # 28
		id_poi = poi_id_poloniumhill,
		alias = [
			"polonium",
			"hill",
			"phill",
			"ph"
		],
		str_name = "Polonium Hill",
		str_desc = "The gently rolling astroturf hills are sprinkled with hideous mansions that obviously cost a fortune but look like complete shit. This whole district feels like it tries way to hard to come across as high-society, when it's really just some residential district on the far-flung edges of the city.\nPolonium Hills residents really want you to think they're rich.\n\nTo the North is Charcoal Park. To the Northeast is Toxington. To the East is Gatlingsdale. To the Southeast is Vandal park. To the South is West Glocksbury.",
		coord = (5, 9),
		channel = "polonium-hill",
		role = "Polonium Hill",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi( # 29
		id_poi = poi_id_westglocksbury,
		alias = [
			"wglocksbury",
			"westglocks",
			"wglocks",
			"wglock",
			"wgb",
			"wg"
		],
		str_name = "West Glocksbury",
		str_desc = "Glocksbury-styled neighborhoods continue into its western counterpart, though liberated from the oppressive yolk of the city’s police department enforcing its poor attempts at enforcing societal values. This, coupled with its location on the outer edge of the city leads to some brutal, cruel crimes being perpetrated by maniacs with little grip on reality. Gunshots ring out regularly from somewhere in the distance, behind laundromats and barber shops.\nWest Glocksbury’s startlingly high violent crime rate may make even some of the most jaded residents of the city may get nervous.\n\nThis area contains the West Glocksbury Subway Station. To the North is Polonium Hill. To the Northeast is Vandal Park. To the East is Glocksbury.",
		coord = (4, 14),
		channel = "west-glocksbury",
		role = "West Glocksbury",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi(  # 30
		id_poi = poi_id_jaywalkerplain,
		alias = [
			"jaywalker",
			"jay",
			"walker",
			"plain",
			"jp",
		],
		str_name = "Jaywalker Plain",
		str_desc = "Though about half of this district is made of up parks, don’t mistake this for a wealthy district. These neglected, overgrown open spaces only help to congest the poor communities of Jaywalker Plains into tightly packed slums. This, coupled with being a backwater on the edge of the city with nothing to do, has bred a district that leads the city only in amount of narcotics injected per capita. Everyone is on a bad trip in Jaywalker Plain. Maniacs roam the street, screaming obscenities and striping naked in public. Homeless men ramble incoherent nonsense while picking drunken fights with one another on the side of the street. Many strange and unusual crimes are perpetrated here and reported on by local news teams to the amusement of residents of neighboring districts. “Did you hear what that guy from Jaywalker Plain did the other day,” is a common conversation starter in the western districts.\nJaywalker Plain has actually become a common residential district for lower income students attending the nearby Neo Milwaukee State wanting to avoid the already cheap rates of apartments in North Sleezebrorough. Because of this, you’re guaranteed to see a lot of young artists and hipsters roaming this broken, nightmare hellscape of a district looking for cafes to leech Wi-Fi access off of. Good luck with that.\n\nThis area contains the Jaywalker Plain Subway Station. To the North is West Glocksbury. To the Northeast is Glocksbury. To the East is North Sleezeborough. To the Southwest is Crookline. To the South is Dreadford.",
		coord = (4, 19),
		coord_alias = [
			(5, 19),
			(5, 20)
		],
		channel = "jaywalker-plain",
		role = "Jaywalker Plain",
		property_class = property_class_c,
		is_capturable = True
	),
	EwPoi(  # 31
		id_poi = poi_id_crookline,
		alias = [
			"crook",
			"line",
			"cl",
		],
		str_name = "Crookline",
		str_desc = "Most of this district is shrouded in total darkness, the unregulated construction of skyscrapers obstructing sunlight from ever reaching the streets far below them. Streetlights and the dense arrays of neon signs advertising speakeasy after speakeasy are the only illumination you’re provided with while traveling the narrow, twisting streets of this district. You’ll have to keep your wits about you if you want to leave here with your wallet, Crookline is perhaps most known for its hordes of petty thieves who specialise in stealing from clueless juveniles from the posher districts. Despite these hurdles, or possibly because of them, Crookline has a bustling nightlife heavily featuring those aforementioned speakeasies. No matter where you are in this district, you’re not more than a block or two from a jazz club. You sort of feel like you’re on the set of a film noir movie when you traverse these dark alleyways.\nCrookline was a historically rebellious settlement on the edge of New Los Angeles City aka Neo Milwaukee, resisting full annexation for years until it was fully culturally and economically dominated by the city. Because of this, the residents have always kept an independent streak, and remain vehemently opposed most aspects of slime past its purely utilitarian purposes. You get the feeling the denizens of this district would have been happier if there was gold discovered in the area rather than the green, morality obliterating substance they’re stuck with.\n\n To the North is Jaywalker Plain. To the Northeast is North Sleezeborough. To the East is South Sleezeborough. To the West is Dreadford.",
		coord = (8, 23),
		channel = "crookline",
		role = "Crookline",
		property_class = property_class_b,
		is_capturable = True
	),
	EwPoi(  # 32
		id_poi = poi_id_dreadford,
		alias = [
			"dread",
			"ford",
			"df",
		],
		str_name = "Dreadford",
		str_desc = "Neatly spaced colonial revival mansions and chapels are broken up by botches of thick, twisting woods. This district is largely rural and suburban, with a small town center with various necessities like Whole Foods and a cemetery. The residents of this district are very, very wealthy and meticulously maintain the gated community they’ve grown for themselves. Perhaps the most obvious example of this is the country club and its accompanying golf course, which comprises a large chunk of the district.\nDreadford is one of the oldest settlements of the area, being inhabited by humans as far back as 1988. The original founders were fleeing restrict criminals rights laws, and established the town of Dreadford in what was then a barren Arizonian desert. These first settlers had quite the pension of holding kangaroo courts, which often amounted to just reading the list of crimes the accused was charged with before hanging them immediately. Some nooses still hang on trees around the district, begging to be finally used.\n\n This area contains the Country Club and the Dreadford Blimp Tower. To the North is Jaywalker Plain. To the East is Crookline.",
		coord = (3, 23),
		channel = "dreadford",
		role = "Dreadford",
		property_class = property_class_s,
		is_capturable = True
	),
	EwPoi( # the-sewers
		id_poi = poi_id_thesewers,
		alias = [
			"drain",
			"sewers",
			"sewer",
			"ghost",
			"ghosts",
			"ts",
			"s",
			"loser"
		],
		str_name = "The Sewers",
		str_desc = "A vast subterranean maze of concrete tunnels, eternally echoing with the dripping of water and decayed slime runoff. All the waste of NLACakaNM eventually winds up here, citizens included.",
		channel = channel_sewers,
		life_states = [
			life_state_corpse
		],
		role = "Sewers"
	),
	EwPoi( # stock-exchange
		id_poi = poi_id_stockexchange,
		alias = [
			"stocks",
			"stock",
			"exchange",
			"sexchange",
			"stockexchange",
			"slimecorpstockexchange",
			"sex",  # slime's end is "se"
			"sec",
			"sx",
			"scex",
			"scx",
			"findom"
		],
		str_name = "The SlimeCorp Stock Exchange",
		str_desc = "A huge, cluttered space bursting at the seams with teller booths and data screens designed to display market data, blasting precious economic insight into your retinas. Discarded punch cards and ticker tape as trampled on by the mass of investors and shareholders that are constantly screaming \"BUY, SELL, BUY, SELL,\" over and over again at no one in particular. Recently reopened, tents line the streets, filled with eager investors. \n\nExits into Downtown NLACakaNM.",
		channel = channel_stockexchange,
		role = "Stock Exchange",
		coord = (21, 16),
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_downtown
	),
	EwPoi( # the-bazaar
		id_poi = poi_id_bazaar,
		alias = [
			"bazaar",
			"market",
			"bz",
			"b"
		],
		str_name = "The Bazaar",
		str_desc = "An open-air marketplace where professional merchants and regular citizens alike can hock their wares. Its currently completely barren.\n\nExits into Brawlden.",
		channel = channel_bazaar,
		role = "Bazaar",
		coord = (21, 11),
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_smogsburg
	),
	EwPoi( # the-cinema
		id_poi = poi_id_cinema,
		alias = [
			"nlacakanmcinema",
			"cinema",
			"cinemas",
			"theater",
			"movie",
			"movies",
			"nc"
		],
		str_name = "NLACakaNM Cinemas",
		str_desc = "A delightfully run-down movie theater, with warm carpeted walls fraying ever so slightly. Films hand picked by the Rowdy Fucker and/or Cop Killer are regularly screened.\n\nExits into Astatine Heights.",
		channel = channel_cinema,
		role = "Cinema",
		coord = (19, 3),
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_astatineheights
	),
	EwPoi( # food-court
		id_poi = poi_id_foodcourt,
		alias = [
			"thenlacakanmfoodcourt",
			"food",
			"foodcourt",
			"food-court",
			"pizzahut",
			"tacobell",
			"kfc",
			"fcourt",
			"fc",
			"marketmanipulation"
		],
		str_name = "The NLACakaNM Food Court",
		str_desc = "Inside a large shopping mall lies the city’s prized food court. This large, brightly-lit area with tiled walls and floors and numerous clashing, "
				   "gaudy color schemes has probably not been renovated since the ‘90s, which is just the way you like it. You are surrounded on all sides by Yum! Brands "
				   "restaurants, specifically the area is one big combination Pizza Hut/Taco Bell/Kentucky Fried Chicken. In the court’s center lies the esteemed "
				   "Mountain Dew fountain, dispensing that glorious piss yellow elixir for all who patron it. Bustling with life, this is the happeningest place in New Los Angeles City "
				   "aka Neo Milwaukee for a hip juvenile such as yourself. So hang out with your fellow gangsters, soak in the outdated mall music and savor the moment. When you’re old "
				   "and brittle, you’ll wish you spent your time doing this more.\n\nExits into Krak Bay.",
		channel = channel_foodcourt,
		role = "Food Court",
		coord = (16, 17),
		pvp = False,
		vendors = [
			vendor_pizzahut,
			vendor_tacobell,
			vendor_kfc,
			vendor_mtndew
		],
		is_subzone = True,
		mother_district = poi_id_krakbay
	),
	EwPoi( # nlac-u
		id_poi = poi_id_nlacu,
		alias = [
			"nlacu",
			"university",
			"nlacuniversity",
			"uni",
			"nu",
			"school",
			"nlac"
		],
		str_name = "New Los Angeles City University",
		str_desc = "An expansive campus housing massive numbers of students and administrators, all here in pursuit of knowledge. The campus is open to visitors, but there's nobody here.\n\nExits into Gatlingsdale.",
		channel = channel_nlacu,
		role = "NLAC U",
		coord = (15, 9),
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_gatlingsdale
	),
	EwPoi( # battle-arena
		id_poi = poi_id_arena,
		alias = [
			"thearena",
			"arena",
			"battlearena",
			"a",
			"ba"
		],
		str_name = "The Battle Arena",
		str_desc = "A huge arena stadium capable of housing tens of thousands of battle enthusiasts, ringing a large field where Slimeoid Battles are held. All the seats are empty.\n\nExits into Vandal Park.",
		channel = channel_arena,
		role = "Arena",
		coord = (10, 10),
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_vandalpark
	),
	EwPoi( # the-dojo
		id_poi = poi_id_dojo,
		alias = [
			"dojo",
			"training",
			"sparring",
			"thedojo",
			"td",
			"d"
		],
		str_name = "The Dojo",
		str_desc = "A traditional, modest Dojo, containing all the facilities and armaments necessary for becoming a cold-blooded killing machine. It’s rustic wood presentation is accentuated by bamboo and parchment walls that separate the Dojo floor into large tatami-matted sections. Groups of juveniles gather here to increase their viability in combat. These sparring children are overseen by the owner of the Dojo, an elderly master of martial artists, fittingly known as the Dojo Master. He observes you train from a distance, brooding, and lamenting his lost youth.\n\nExits into South Sleezeborough.",
		channel = channel_dojo,
		role = "Dojo",
		coord = (12, 29),
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_southsleezeborough
	),
	EwPoi( # speakeasy
		id_poi = poi_id_speakeasy,
		alias = [
			"kingswifessonspeakeasy",
			"kingswifesson",
			"speakeasy",
			"bar",
			"sons",
			"sez",  # se is already slime's end
			"ez",
			"kws",
			"king",
			"kings"
		],
		str_name = "The King's Wife's Son Speakeasy",
		str_desc = "A rustic tavern with dark wooden walls and floor, bearing innumerable knickknacks on the walls and high wooden stools arranged in front of a bar made of patina'd copper. It is crowded with seedy lowlifes and other generally undesirables, such as yourself.\n\nExits into Vagrant's Corner.",
		channel = channel_speakeasy,
		role = "Speakeasy",
		coord = (39, 13),
		pvp = False,
		vendors = [
			vendor_bar
		],
		is_subzone = True,
		mother_district = poi_id_vagrantscorner
	),
	EwPoi( # 7-11
		id_poi = poi_id_711,
		alias = [
			"outsidethe7-11",
			"outside7-11",
			"outside711",
			"7-11",
			"711",
			"seveneleven",
			"outsideseveneleven"
		],
		str_name = "Outside the 7-11",
		str_desc = "The darkened derelict 7-11 stands as it always has, a steadfast pillar of NLACakaNM culture. On its dirty exterior walls are spraypainted messages about \"patch notes\", \"github\", and other unparseable nonsense.\n\nExits into Poudrin Alley.",
		channel = channel_711,
		role = "7-11",
		coord = (19, 25),
		pvp = False,
		vendors = [
			vendor_vendingmachine
		],
		is_subzone = True,
		mother_district = poi_id_poudrinalley
	),
	EwPoi( # the-labs
		id_poi = poi_id_slimeoidlab,
		alias = [
			"lab",
			"labs",
			"laboratory",
			"slimecorpslimeoidlaboratory",
			"slimecorpslimeoidlab",
			"slimecorplab",
			"slimecorplabs",
			"slimeoidlaboratory",
			"slimeoidlab",
			"slimeoidlabs",
			"slab",
			"sl",
			"slimeoid"
		],
		str_name = "SlimeCorp Slimeoid Laboratory",
		str_desc = "A nondescript building containing mysterious SlimeCorp industrial equipment. Large glass tubes and metallic vats seem to be designed to serve as incubators. There is a notice from SlimeCorp on the entranceway explaining the use of its equipment. Use !instructions to read it.\n\nExits into Brawlden.",
		channel = channel_slimeoidlab,
		role = "Slimeoid Lab",
		coord = (28, 1),
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_brawlden
	),
	EwPoi( # the-mines
		id_poi = poi_id_mine,
		alias = [
			"mines",
			"mine",
			"m",
			"tm",
			"jrm"
		],
		str_name = "The Mines",
		str_desc = "A veritable slime-mine of slime, rejuvinated by the revival of ENDLESS WAR.\n\nExits into Juvie's Row.",
		coord = (34, 18),
		channel = channel_mines,
		role = "Mines",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_juviesrow
	),
	EwPoi( # the-casino
		id_poi = poi_id_thecasino,
		alias = [
			"casino",
			"slimecasino",
			"theslimecasino",
			"tc",  # the casino
			"cas",
			"c"
		],
		str_name = "The Casino",
		str_desc = "The casino is filled with tables and machines for playing games of chance, and garishly decorated wall-to-wall. Lights which normally flash constantly cover everything, but now they all sit unlit.\n\nExits into Green Light District.",
		coord = (28, 15),
		channel = channel_casino,
		role = "Casino",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_greenlightdistrict
	),
	EwPoi(  # cratersville mines
		id_poi = poi_id_cv_mines,
		alias = [
			"mines2",
			"cvmines",
			"cmines",
			"cvm",
			"cm",
			"cratersvillemine",
			"cratersvillem"
		],
		str_name = "The Cratersville Mines",
		str_desc = "A veritable slime-mine of slime, rejuvenated by the revival of ENDLESS WAR.\n\nExits into Cratersville.",
		coord = (19, 30),
		channel = channel_cv_mines,
		role = "Cratersville Mines",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_cratersville
	),
	EwPoi(  # toxington mines
		id_poi = poi_id_tt_mines,
		alias = [
			"mines3",
			"ttmines",
			"ttm",
			"toxm",
			"toxingtonmine",
			"toxingtonm"
		],
		str_name = "The Toxington Mines",
		str_desc = "A veritable slime-mine of slime, rejuvinated by the revival of ENDLESS WAR.\n\nExits into Toxington.",
		coord = (9, 2),
		channel = channel_tt_mines,
		role = "Toxington Mines",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_toxington
	),
	EwPoi( # smokers-cough
		id_poi = poi_id_diner,
		alias = [
			"diner",
			"smokers",
			"cough",
			"smc",
			"sc",
			"rf", #rowdy food
			"sm",
			#"k0ff"
		],
		str_name = "The Smoker's Cough",
		str_desc = "A quaint hole-in-the-wall vintage diner. The wallpaper may be peeling and the ‘80s paint job might be faded, but you’ll be damned if this place didn’t make an aesthetic stomping grounds for cheapskate juveniles like yourself. All the staff know you by name, they’ve memorized your order, and frankly they love you. You’re like a ninth son to the inbred owner and his many, many wives. It’s a cramped space, only fitting about 20 people maximum. The fluorescent lighting from the ceiling lamps invade every nook and cranny of the cyan and purple diner, even when the natural daylight could easily illuminate it just as well. You think you can see some mold on certain corners of the floor. Oh man, so cool.\n\nExits into Wreckington.",
		coord = (25, 24),
		channel = channel_diner,
		role = "Smoker's Cough",
		pvp = False,
		vendors = [
			vendor_diner
		],
		is_subzone = True,
		mother_district = poi_id_wreckington
	),
	EwPoi( # Red Mobster
		id_poi = poi_id_seafood,
		alias = [
			"seafood",
			"redmobster",
			"red",
			"mobster",
			"rm",
			"mob",
			"kf" #killer food
		],
		str_name = "Red Mobster Seafood",
		str_desc = "The last bastion of sophistication in this godforsaken city. A dimly lit, atmospheric fine dining restaurant with waiters and tables and archaic stuff like that. Upper crust juveniles and older fugitives make up the majority of the patrons, making you stick out like a sore thumb. Quiet, respectable murmurs pollute the air alongside the scrapping of silverware and the occasional hoity toity laugh. Everything about this place makes you sick.\n\nExits into Astatine Heights.",
		coord = (17, 1),
		channel = channel_seafood,
		role = "Red Mobster Seafood",
		pvp = False,
		vendors = [
			vendor_seafood
		],
		is_subzone = True,
		mother_district = poi_id_astatineheights
	),
	EwPoi( # JR Farm
		id_poi = poi_id_jr_farms,
		alias = [
			"jrf", #juviesrow farms
			"jrp", #juviesrow plantation
			"jrfarms",
			"jrfarm",
			"jrplantation",
			"jrplant",
			"juviesrowf",
			"juviesrowfarm"
		],
		str_name = "The Juvie's Row Farms",
		str_desc = "An array of haphazardly placed farms dot the already dense, crowded areas between mining shaft entrances and impoverished juvenile housing. Pollution is rampant here, with the numerous trash heaps and sludge refineries enjoying the majority of earth under the smoke-smuggered stars. It’s soil is irradiated and barely arable, but it will do. It has to.\n\nExits into Juvie's Row.",
		coord = (32, 20),
		channel = channel_jr_farms,
		role = "Juvie's Row Farms",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_juviesrow
	),
	EwPoi( # OG Farm
		id_poi = poi_id_og_farms,
		alias = [
			"ogf",  # OozeGardens farms
			"ogp",  # OozeGardens plantation
			"ogfarms",
			"ogfarm",
			"ogplantation",
			"ogplant",
			"oozegardenfarms",
			"oozegardenfarm",
			"oozegardensf",
			"oozegardensfarm"
		],
		str_name = "The Ooze Gardens Farms",
		str_desc = "An impressive host of unique and exotic flora are grown here. Originally on private property, the expansive greenhouses were the weekly meeting place for the city’s botanical society. They have since been seized by imminent domain and are now a public park. It’s type of soil is vast and varied depending on where you choose to plant. Surely, anything can grow here.\n\nExits into Ooze Gardens.",
		coord = (14, 27),
		channel = channel_og_farms,
		role = "Ooze Gardens Farms",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_oozegardens
	),
	EwPoi( # AB Farm
		id_poi = poi_id_ab_farms,
		alias = [
			"abf", #ArsonBrook farms
			"abp", #ArsonBrook plantation
			"abfarms",
			"abfarm",
			"abplantation",
			"abplant",
			"arsonbrookf",
			"arsonbrookfarm"
		],
		str_name = "The Arsonbrook Farms",
		str_desc = "A series of reedy creeks interspersed with quiet farms and burnt, black trees. It’s overcast skies make the embers from frequent forest fires glow even brighter by comparison. It’s soil is fertile with copious amounts of soot and accompanying nutrients.\n\nExits into Arsonbrook.",
		coord = (21, 1),
		channel = channel_ab_farms,
		role = "Arsonbrook Farms",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_arsonbrook
	),
	EwPoi(  # Neo Milwaukee State
		id_poi = poi_id_neomilwaukeestate,
		alias = [
			"neomilwaukee",
			"state",
			"college",
			"nms",
		],
		str_name = "Neo Milwaukee State",
		str_desc = "An abysmally funded public college, with a student body of high school has-beens and future gas station attendants. With nearly a 100% acceptance rate, it’s needless to say that the riff raff is not kept out of this seedy establishment. People are here to stumble through their meaningless lives, chasing normality and appeasing their poor parent’s ideas of success by enrolling in the first college they get accepted to and walking out four years later with thousands of dollars of debt and a BA in English. No one here is excited to learn, no one is excited to teach, no one is excited for anything here. They all just want to die, and thankfully they will someday.\n\nExits into North Sleezeborough. ",
		coord = (12, 19),
		channel = channel_neomilwaukeestate,
		role = "Neo Milwaukee State",
		pvp = False,
		is_subzone = True,
		mother_district = poi_id_northsleezeborough
	),
	EwPoi(  # Assault Flats Beach Resort
		id_poi = poi_id_beachresort,
		alias = [
			"resort",
			"br",
			"r",
		],
		str_name = "The Resort",
		str_desc = "The interior is lavishly decorated with all manner of tropically-inspired furnishings, all beautifully maintained with nary a speck of grime staining it’s pristine off-white walls. Exotic potted plants and natural lighting fill the hallways, which all smell like the inside of a women’s body wash bottle. Palm trees seemingly occupy half of the outside land on the complex, averaging about 2 feet apart from one another at most to your calculations. Imported red sand of the beach stretches toward the horizon, lapped by gentle waves of slime. Couples enjoy slima coladas and tanning by the slime pool. This place fucking disgusts you. Is… is that a stegosaurus in the distance?\n\nExits into Assault Flats Beach.",
		coord = (42, 6),
		channel = channel_beachresort,
		role = "Beach Resort",
		pvp = False,
		vendors = [
			vendor_beachresort
		],
		is_subzone = True,
		mother_district = poi_id_assaultflatsbeach
	),
	EwPoi(  # Dreadford Country Club
		id_poi = poi_id_countryclub,
		alias = [
			"country",
			"club",
			"cc",
		],
		str_name = "The Country Club",
		str_desc = "On top of a grassy hill, behind several wired/eletric fences, lies Dreadford’s famous country club. The lodge itself is a huge, old wooden lodge from the 1800s, with hundreds of knick-knacks, hunting trophies and historic photos hung up on the wall, and tacky rugs and furniture around a roaring fire in it’s center. Sprawling out from the club itself is the complex’s signature golf course, where all the pompous rich assholes go to waste their time and chit-chat with each other about cheating on their wives.\n\nExits into Dreadford.",
		coord = (3, 25),
		channel = channel_countryclub,
		role = "Country Club",
		pvp = False,
		vendors = [
			vendor_countryclub
		],
		is_subzone = True,
		mother_district = poi_id_dreadford
	),
	EwPoi( # Slime Sea
		id_poi = poi_id_slimesea,
		str_name = "The Slime Sea",
		str_desc = "Slime as far as the eye can see.",
		channel = channel_slimesea,
		role = "Slime Sea",
		pvp = True
	),
	EwPoi(  # Wreckington Ferry Port
		id_poi = poi_id_wt_port,
		alias = [
			"wreckingtonport",
			"wtport",
			"wreckingtonferry",
			"wtferry",
			"wtp",
			"wtfp",
			"wf"
		],
		str_name = "The Wreckington Ferry Port",
		str_desc = "Caddy corner to Wreckington’s iconic junkyard lies its less famous shipyard, filled mostly with dozens upon dozens of different garbage barges dumping off metric tons of trash every day but also hosting this very terminal! The ferry takes you from here to Vagrant’s Corner, so just head there like you would any other district and you’ll hop on the ferry. Nifty!\n\nExits into Wreckington.",
		coord = (29, 24),
		channel = channel_wt_port,
		role = "Wreckington Port",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_wreckington,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Vagrant's Corner Ferry Port
		id_poi = poi_id_vc_port,
		alias = [
			"vagrantscornerport",
			"vagrantsport",
			"vcport",
			"vagrantscornerferry",
			"vcferry",
			"vcp",
			"vcfp",
			"vf"
		],
		str_name = "The Vagrant's Corner Ferry Port",
		str_desc = "Down one of hundreds of piers on the crowded Vagrant’s Corner wharf sits this dingy dinghy terminal. The ferry takes you from here to Wreckington, so just head there like you would any other district and you’ll hop on the ferry. Nifty!\n\nExits into Vagrant's Corner.",
		coord = (41, 11),
		channel = channel_vc_port,
		role = "Vagrant's Corner Port",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_vagrantscorner,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Toxington Subway Station
		id_poi = poi_id_tt_subway_station,
		alias = [
			"toxingtonsubway",
			"toxingtonsub",
			"toxingtonstation",
			"toxsubwaystation",
			"toxsubway",
			"toxsub",
			"toxstation",
			"ttsubwaystation",
			"ttsubway",
			"ttsub",
			"ttstation",
			"toxs",
			"tts"
		],
		str_name = "The Toxington Subway Station",
                str_desc = str_red_subway_station_description + "\n\nExits into Toxington.",
		coord = (9, 6),
		channel = channel_tt_subway_station,
		role = "Toxington Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_toxington,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Astatine Heights Subway Station
		id_poi = poi_id_ah_subway_station,
		alias = [
			"astatineheightssubway",
			"astatineheightssub",
			"astatineheightsstation",
			"astatinesubwaystation",
			"astatinesubway",
			"astatinesub",
			"astatinestation",
			"ahsubwaystation",
			"ahsubway",
			"ahsub",
			"ahstation",
			"astatines",
			"ahs"
		],
		str_name = "The Astatine Heights Subway Station",
		str_desc = str_red_subway_station_description + "\n\nExits into Astatine Heights.",
		coord = (15, 3),
		channel = channel_ah_subway_station,
		role = "Astatine Heights Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_astatineheights,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Gatlingsdale Subway Station
		id_poi = poi_id_gd_subway_station,
		alias = [
			"gatlingsdalesubway",
			"gatlingsdalesub",
			"gatlingsdalestation",
			"gatlingssubwaystation",
			"gatlingssubway",
			"gatlingssub",
			"gatlingsstation",
			"gdsubwaystation",
			"gdsubway",
			"gdsub",
			"gdstation",
			"gatlingss",
			"gds"
		],
		str_name = "The Gatlingsdale Subway Station",
		str_desc = str_red_subway_station_description + "\n\nExits into Gatlingsdale.",
		coord = (15, 11),
		channel = channel_gd_subway_station,
		role = "Gatlingsdale Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_gatlingsdale,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Arsonbrook Subway Station
		id_poi = poi_id_ab_subway_station,
		alias = [
			"arsonbrooksubway",
			"arsonbrooksub",
			"arsonbrookstation",
			"arsonsubwaystation",
			"arsonsubway",
			"arsonsub",
			"arsonstation",
			"absubwaystation",
			"absubway",
			"absub",
			"abstation",
			"arsons",
			"abs"
		],
		str_name = "The Arsonbrook Subway Station",
		str_desc = str_yellow_subway_station_description + "\n\nExits into Arsonbrook.",
		coord = (23, 1),
		channel = channel_ab_subway_station,
		role = "Arsonbrook Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_arsonbrook,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Cop Killtown Subway Station
		id_poi = poi_id_ck_subway_station,
		alias = [
			"copkilltownsubway",
			"copkilltownsub",
			"copkilltownstation",
			"copkillsubwaystation",
			"copkillsubway",
			"copkillsub",
			"copkillstation",
			"cksubwaystation",
			"cksubway",
			"cksub",
			"ckstation",
			"copkills",
			"cks",
			"cs"
		],
		str_name = "The Cop Killtown Subway Station",
		str_desc = str_red_subway_station_description + "\n\nExits into Cop Killtown.",
		coord = (17, 15),
		channel = channel_ck_subway_station,
		role = "Cop Killtown Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_copkilltown,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Smogsburg Subway Station
		id_poi = poi_id_sb_subway_station,
		alias = [
			"smogsburgsubway",
			"smogsburgsub",
			"smogsburgstation",
			"smogssubwaystation",
			"smogssubway",
			"smogssub",
			"smogsstation",
			"sbsubwaystation",
			"sbsubway",
			"sbsub",
			"sbstation",
			"smogss",
			"sbs"
		],
		str_name = "The Smogsburg Subway Station",
		str_desc = str_green_subway_station_description + \
                        "\n\n" + str_subway_connecting_sentence.format("yellow") + \
                        "\n\n" + str_yellow_subway_station_description \
			+ "\n\nExits into Smogsburg.",
		coord = (25, 9),
		channel = channel_sb_subway_station,
		role = "Smogsburg Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_smogsburg,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Downtown Subway Station
		id_poi = poi_id_dt_subway_station,
		alias = [
			"downtownsubway",
			"downtownsub",
			"downtownstation",
			"dtsubwaystation",
			"dtsubway",
			"dtsub",
			"dtstation",
			"dts"
		],
		str_name = "The Downtown NLACakaNM Subway Station",
		str_desc = str_downtown_station_description,
		coord = (23, 20),
		channel = channel_dt_subway_station,
		role = "Downtown Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_downtown,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Krak Bay Subway Station
		id_poi = poi_id_kb_subway_station,
		alias = [
			"krakbaysubway",
			"krakbaysub",
			"krakbaystation",
			"kraksubwaystation",
			"kraksubway",
			"kraksub",
			"krakstation",
			"kbsubwaystation",
			"kbsubway",
			"kbsub",
			"kbstation",
			"kraks",
			"kbs"
		],
		str_name = "The Krak Bay Subway Station",
		str_desc = str_green_subway_station_description + \
                        "\n\n" + str_subway_connecting_sentence.format("yellow") + \
                        "\n\n" + str_yellow_subway_station_description + \
			"\n\nExits into Krak Bay.",
		coord = (18, 17),
		channel = channel_kb_subway_station,
		role = "Krak Bay Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_krakbay,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Glocksbury Subway Station
		id_poi = poi_id_gb_subway_station,
		alias = [
			"glocksburysubway",
			"glocksburysub",
			"glocksburystation",
			"glockssubwaystation",
			"glockssubway",
			"glockssub",
			"glocksstation",
			"gbsubwaystation",
			"gbsubway",
			"gbsub",
			"gbstation",
			"glockss",
			"gbs"
		],
		str_name = "The Glocksbury Subway Station",
		str_desc = str_green_subway_station_description + "\n\nExits into Glocksbury.",
		coord = (6, 18),
		channel = channel_gb_subway_station,
		role = "Glocksbury Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_glocksbury,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # West Glocksbury Subway Station
		id_poi = poi_id_wgb_subway_station,
		alias = [
			"westglocksburysubway",
			"westglocksburysub",
			"westglocksburystation",
			"westglockssubwaystation",
			"westglockssubway",
			"westglockssub",
			"westglocksstation",
			"wgbsubwaystation",
			"wgbsubway",
			"wgbsub",
			"wgbstation",
			"westglockss",
			"wgbs"
		],
		str_name = "The West Glocksbury Subway Station",
		str_desc = str_green_subway_station_description + "\n\nExits into West Glocksbury.",
		coord = (2, 14),
		channel = channel_wgb_subway_station,
		role = "West Glocksbury Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_westglocksbury,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Jaywalker Plain Subway Station
		id_poi = poi_id_jp_subway_station,
		alias = [
			"jaywalkerplainsubway",
			"jaywalkerplainsub",
			"jaywalkerplainstation",
			"jaywalkersubwaystation",
			"jaywalkersubway",
			"jaywalkersub",
			"jaywalkerstation",
			"jpsubwaystation",
			"jpsubway",
			"jpsub",
			"jpstation",
			"jaywalkers",
			"jps"
		],
		str_name = "The Jaywalker Plain Subway Station",
		str_desc = str_green_subway_station_description + "\n\nExits into Jaywalker Plain.",
		coord = (2, 19),
		channel = channel_jp_subway_station,
		role = "Jaywalker Plain Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_jaywalkerplain,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # North Sleezeborough Subway Station
		id_poi = poi_id_nsb_subway_station,
		alias = [
			"northsleezeboroughsubwaystation",
			"northsleezeboroughsubway",
			"northsleezeboroughsub",
			"northsleezeboroughstation",
			"northsleezesubwaystation",
			"northsleezesubway",
			"northsleezesub",
			"northsleezestation",
			"nsbsubwaystation",
			"nsbsubway",
			"nsbsub",
			"nsbstation",
			"northsleezes",
			"nsbs"
		],
		str_name = "The North Sleezeborough Subway Station",
		str_desc = str_green_subway_station_description + "\n\nExits into North Sleezeborough.",
		coord = (10, 23),
		channel = channel_nsb_subway_station,
		role = "North Sleezeborough Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_northsleezeborough,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # South Sleezeborough Subway Station
		id_poi = poi_id_ssb_subway_station,
		alias = [
			"southsleezeboroughsubwaystation",
			"southsleezeboroughsubway",
			"southsleezeboroughsub",
			"southsleezeboroughstation",
			"southsleezesubwaystation",
			"southsleezesubway",
			"southsleezesub",
			"southsleezestation",
			"ssbsubwaystation",
			"ssbsubway",
			"ssbsub",
			"ssbstation",
			"southsleezes",
			"ssbs"
		],
		str_name = "The South Sleezeborough Subway Station",
		str_desc = str_yellow_subway_station_description + "\n\nExits into South Sleezeborough.",
		coord = (10, 27),
		channel = channel_ssb_subway_station,
		role = "South Sleezeborough Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_southsleezeborough,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Cratersville Subway Station
		id_poi = poi_id_cv_subway_station,
		alias = [
			"cratersvillesubway",
			"cratersvillesub",
			"cratersvillestation",
			"craterssubwaystation",
			"craterssubway",
			"craterssub",
			"cratersstation",
			"cvsubwaystation",
			"cvsubway",
			"cvsub",
			"cvstation",
			"craterss",
			"cvs"
		],
		str_name = "The Cratersville Subway Station",
		str_desc = str_red_subway_station_description + "\n\nExits into Cratersville.",
		coord = (21, 30),
		channel = channel_cv_subway_station,
		role = "Cratersville Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_cratersville,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Wreckington Subway Station
		id_poi = poi_id_wt_subway_station,
		alias = [
			"wreckingtonsubway",
			"wreckingtonsub",
			"wreckingtonstation",
			"wrecksubwaystation",
			"wrecksubway",
			"wrecksub",
			"wreckstation",
			"wtsubwaystation",
			"wtsubway",
			"wtsub",
			"wtstation",
			"wrecks",
			"wts"
		],
		str_name = "The Wreckington Subway Station",
		str_desc = str_red_subway_station_description + "\n\nExits into Wreckington.",
		coord = (25, 26),
		channel = channel_wt_subway_station,
		role = "Wreckington Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_wreckington,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Rowdy Roughhouse Subway Station
		id_poi = poi_id_rr_subway_station,
		alias = [
			"rowdyroughhousesubway",
			"rowdyroughhousesub",
			"rowdyroughhousestation",
			"rowdysubwaystation",
			"rowdysubway",
			"rowdysub",
			"rowdystation",
			"rrsubwaystation",
			"rrsubway",
			"rrsub",
			"rrstation",
			"rrs"
		],
		str_name = "The Rowdy Roughhouse Subway Station",
		str_desc = str_red_subway_station_description + "\n\nExits into Rowdy Roughhouse.",
		coord = (29, 21),
		channel = channel_rr_subway_station,
		role = "Rowdy Roughhouse Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_rowdyroughhouse,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Green Light District Subway Station
		id_poi = poi_id_gld_subway_station,
		alias = [
			"greenlightdistrictsubwaystation",
			"greenlightdistrictsubway",
			"greenlightdistrictsub",
			"greenlightdistrictstation",
			"greenlightsubwaystation",
			"greenlightsubway",
			"greenlightsub",
			"greenlightstation",
			"gldsubwaystation",
			"gldsubway",
			"gldsub",
			"gldstation",
			"greenlights",
			"glds"
		],
		str_name = "The Green Light District Subway Station",
		str_desc = str_blue_subway_station_description + "\n\nExits into Green Light District.",
		coord = (30, 15),
		channel = channel_gld_subway_station,
		role = "Green Light District Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_greenlightdistrict,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Juvie's Row Subway Station
		id_poi = poi_id_jr_subway_station,
		alias = [
			"juviesrowsubway",
			"juviesrowsub",
			"juviesrowstation",
			"juviessubwaystation",
			"juviessubway",
			"juviessub",
			"juviesstation",
			"jrsubwaystation",
			"jrsubway",
			"jrsub",
			"jrstation",
			"juviess",
			"jrs"
		],
		str_name = "The Juvie's Row Subway Station",
		str_desc = str_blue_subway_station_description + "\n\nExits into Juvie's Row.",
		coord = (30, 18),
		channel = channel_jr_subway_station,
		role = "Juvie's Row Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_juviesrow,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Vagrant's Corner Subway Station
		id_poi = poi_id_vc_subway_station,
		alias = [
			"vagrantscornersubway",
			"vagrantscornersub",
			"vagrantscornerstation",
			"vagrantssubwaystation",
			"vagrantssubway",
			"vagrantssub",
			"vagrantsstation",
			"vcsubwaystation",
			"vcsubway",
			"vcsub",
			"vcstation",
			"vagrantss",
			"vcs"
		],
		str_name = "The Vagrant's Corner Subway Station",
		str_desc = str_blue_subway_station_description + "\n\nExits into Vagrant's Corner.",
		coord = (41, 9),
		channel = channel_vc_subway_station,
		role = "Vagrant's Corner Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_vagrantscorner,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Assault Flats Beach Subway Station
		id_poi = poi_id_afb_subway_station,
		alias = [
			"assaultflatsbeachsubwaystation",
			"assaultflatsbeachsubway",
			"assaultflatsbeachsub",
			"assaultflatsbeachstation",
			"assaultflatssubwaystation",
			"assaultflatssubway",
			"assaultflatssub",
			"assaultflatsstation",
			"beachsubwaystation",
			"beachsubway",
			"beachsub",
			"beachstation",
			"afbsubwaystation",
			"afbsubway",
			"afbsub",
			"afbstation",
			"assaultflatss",
			"afbs"
		],
		str_name = "The Assault Flats Beach Subway Station",
		str_desc = str_blue_subway_station_description + "\n\nExits into Assault Flats Beach.",
		coord = (42, 4),
		channel = channel_afb_subway_station,
		role = "Assault Flats Beach Subway Station",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_assaultflatsbeach,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Dreadford Blimp Tower
		id_poi = poi_id_df_blimp_tower,
		alias = [
			"dreadfordblimptower",
			"dreadfordhblimp",
			"dreadfordtower",
			"dreadblimptower",
			"dreadblimp",
			"dreadtower",
			"dfblimptower",
			"dfblimp",
			"dftower"
		],
		str_name = "The Dreadford Blimp Tower",
		str_desc = str_blimp_tower_description + "\n\nExits into Dreadford.",
		coord = (1, 23),
		channel = channel_df_blimp_tower,
		role = "Dreadford Blimp Tower",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_dreadford,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Assault Flats Beach Blimp Tower
		id_poi = poi_id_afb_blimp_tower,
		alias = [
			"assaultflatsbeachblimptower",
			"assaultflatsbeachblimp",
			"assaultflatsbeachtower",
			"assaultflatsblimptower",
			"assaultflatsblimp",
			"assaultflatstower",
			"beachblimptower",
			"beachblimp",
			"beachtower",
			"afbblimptower",
			"afbblimp",
			"afbtower"
		],
		str_name = "The Assault Flats Beach Blimp Tower",
		str_desc = str_blimp_tower_description + "\n\nExits into Assault Flats Beach.",
		coord = (40, 2),
		channel = channel_afb_blimp_tower,
		role = "Assault Flats Beach Blimp Tower",
		pvp = True,
		is_subzone = True,
		mother_district = poi_id_assaultflatsbeach,
		is_transport_stop = True,
		transport_lines = set()
	),
	EwPoi(  # Ferry
		id_poi = poi_id_ferry,
		alias = [
			"boat",
			"f"
		],
		str_name = "The Ferry",
		str_desc = "A modest two-story passenger ferry, built probably 80 years ago. Its faded paint is starting to crack and its creaky wood benches aren’t exactly comfortable. Though it’s not much to look at, you still love riding it. Out here, all you have to think about is the cool wind in your hair, the bright green glow of the Slime Sea searing your eyes, and the New Los Angeles City aka Neo Milwaukee skyline in the distance. You plug in earbuds to drown out the sea captain’s embarrassing Jungle Cruise-tier commentary over the microphone. Good times.",
		channel = channel_ferry,
		role = "Ferry",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_ferry,
		default_line = transport_line_ferry_wt_to_vc,
		default_stop = poi_id_wt_port
	),
	EwPoi(  # Subway train on the red line
		id_poi = poi_id_subway_red01,
		str_name = "A Red Line Subway Train",
		str_desc = str_red_subway_description,
		channel = channel_subway_red01,
		role = "Subway Train R-01",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_red_northbound,
		default_stop = poi_id_cv_subway_station
	),
	EwPoi(  # Subway train on the red line
		id_poi = poi_id_subway_red02,
		str_name = "A Red Line Subway Train",
		str_desc = str_red_subway_description,
		channel = channel_subway_red02,
		role = "Subway Train R-02",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_red_southbound,
		default_stop = poi_id_tt_subway_station
	),
	EwPoi(  # Subway train on the yellow line
		id_poi = poi_id_subway_yellow01,
		str_name = "A Yellow Line Subway Train",
		str_desc = str_yellow_subway_description,
		channel = channel_subway_yellow01,
		role = "Subway Train Y-01",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_yellow_northbound,
		default_stop = poi_id_ssb_subway_station
	),
	EwPoi(  # Subway train on the yellow line
		id_poi = poi_id_subway_yellow02,
		str_name = "A Yellow Line Subway Train",
		str_desc = str_yellow_subway_description,
		channel = channel_subway_yellow02,
		role = "Subway Train Y-02",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_yellow_southbound,
		default_stop = poi_id_ab_subway_station
	),
	EwPoi(  # Subway train on the green line
		id_poi = poi_id_subway_green01,
		str_name = "A Green Line Subway Train",
		str_desc = str_green_subway_description,
		channel = channel_subway_green01,
		role = "Subway Train G-01",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_green_eastbound,
		default_stop = poi_id_wgb_subway_station
	),
	EwPoi(  # Subway train on the green line
		id_poi = poi_id_subway_green02,
		str_name = "A Green Line Subway Train",
		str_desc = str_green_subway_description,
		channel = channel_subway_green02,
		role = "Subway Train G-02",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_green_westbound,
		default_stop = poi_id_sb_subway_station
	),
	EwPoi(  # Subway train on the blue line
		id_poi = poi_id_subway_blue01,
		str_name = "A Blue Line Subway Train",
		str_desc = str_blue_subway_description,
		channel = channel_subway_blue01,
		role = "Subway Train B-01",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_blue_eastbound,
		default_stop = poi_id_dt_subway_station
	),
	EwPoi(  # Subway train on the blue line
		id_poi = poi_id_subway_blue02,
		str_name = "A Blue Line Subway Train",
		str_desc = str_blue_subway_description,
		channel = channel_subway_blue02,
		role = "Subway Train B-02",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_subway,
		default_line = transport_line_subway_blue_westbound,
		default_stop = poi_id_afb_subway_station
	),
	#EwPoi(  # Subway train on the white line
	#	id_poi = poi_id_subway_white01,
	#	str_name = "A Subway Train",
	#	str_desc = generic_subway_description, # TODO: add description
	#	channel = channel_subway_white01,
	#	role = "Subway Train W-01",
	#	pvp = True,
	#	is_transport = True,
	#	transport_type = transport_type_subway,
	#	default_line = transport_line_subway_white_eastbound,
	#	default_stop = poi_id_dt_subway_station
	#),
	EwPoi(  # Blimp
		id_poi = poi_id_blimp,
		alias = [
			"zeppelin",
			"airship"
		],
		str_name = "The Blimp",
		str_desc = str_blimp_description,
		channel = channel_blimp,
		role = "Blimp",
		pvp = True,
		is_transport = True,
		transport_type = transport_type_blimp,
		default_line = transport_line_blimp_df_to_afb,
		default_stop = poi_id_df_blimp_tower
	)
]

id_to_poi = {}
coord_to_poi = {}
alias_to_coord = {}
capturable_districts = []
transports = []
transport_stops = []

for poi in poi_list:
	if poi.coord != None:
		# Populate the map of coordinates to their point of interest, for looking up from the map.
		coord_to_poi[poi.coord] = poi

		# Populate the map of coordinate aliases to the main coordinate.
		for coord_alias in poi.coord_alias:
			alias_to_coord[coord_alias] = poi.coord
			coord_to_poi[coord_alias] = poi

	# Populate the map of point of interest names/aliases to the POI.
	id_to_poi[poi.id_poi] = poi
	for alias in poi.alias:
		id_to_poi[alias] = poi

	# if it's a district and not RR, CK, or JR, add it to a list of capturable districts
	if poi.is_capturable:
		capturable_districts.append(poi.id_poi)

	if poi.is_transport:
		transports.append(poi.id_poi)

	if poi.is_transport_stop:
		transport_stops.append(poi.id_poi)

# maps districts to their immediate neighbors
poi_neighbors = {}

transport_lines = [
	EwTransportLine( # ferry line from wreckington to vagrant's corner
		id_line = transport_line_ferry_wt_to_vc,
		alias = [
			"vagrantscornerferry",
			"vagrantsferry",
			"vcferry",
			"ferrytovagrantscorner",
			"ferrytovagrants",
			"ferrytovc"
		    ],
		first_stop = poi_id_wt_port,
		last_stop = poi_id_vc_port,
		next_line = transport_line_ferry_vc_to_wt,
		str_name = "The ferry line towards Vagrant's Corner",
		schedule = {
			poi_id_wt_port : [60, poi_id_slimesea],
			poi_id_slimesea : [120, poi_id_vc_port]
		    }

		),
	EwTransportLine( # ferry line from vagrant's corner to wreckington
		id_line = transport_line_ferry_vc_to_wt,
		alias = [
			"wreckingtonferry",
			"wreckferry",
			"wtferry",
			"ferrytowreckington",
			"ferrytowreck",
			"ferrytowt"
		    ],
		first_stop = poi_id_vc_port,
		last_stop = poi_id_wt_port,
		next_line = transport_line_ferry_wt_to_vc,
		str_name = "The ferry line towards Wreckington",
		schedule = {
			poi_id_vc_port : [60, poi_id_slimesea],
			poi_id_slimesea : [120, poi_id_wt_port]
		    }

		),
	EwTransportLine( # yellow subway line from south sleezeborough to arsonbrook
		id_line = transport_line_subway_yellow_northbound,
		alias = [
			"northyellowline",
			"northyellow",
			"yellownorth",
			"yellowtoarsonbrook",
			"yellowtoarson",
			"yellowtoab"
		    ],
		first_stop = poi_id_ssb_subway_station,
		last_stop = poi_id_ab_subway_station,
		next_line = transport_line_subway_yellow_southbound,
		str_name = "The yellow subway line towards Arsonbrook",
		schedule = {
			poi_id_ssb_subway_station : [20, poi_id_kb_subway_station],
			poi_id_kb_subway_station : [20, poi_id_dt_subway_station],
			poi_id_dt_subway_station : [20, poi_id_sb_subway_station],
			poi_id_sb_subway_station : [20, poi_id_ab_subway_station]
		    }

		),
	EwTransportLine( # yellow subway line from arsonbrook to south sleezeborough
		id_line = transport_line_subway_yellow_southbound,
		alias = [
			"southyellowline",
			"southyellow",
			"yellowsouth",
			"yellowtosouthsleezeborough",
			"yellowtosouthsleeze",
			"yellowtossb"
		    ],
		first_stop = poi_id_ab_subway_station,
		last_stop = poi_id_ssb_subway_station,
		next_line = transport_line_subway_yellow_northbound,
		str_name = "The yellow subway line towards South Sleezeborough",
		schedule = {
			poi_id_ab_subway_station : [20, poi_id_sb_subway_station],
			poi_id_sb_subway_station : [20, poi_id_dt_subway_station],
			poi_id_dt_subway_station : [20, poi_id_kb_subway_station],
			poi_id_kb_subway_station : [20, poi_id_ssb_subway_station]
		    }

		),
	EwTransportLine( # red subway line from cratersville to toxington
		id_line = transport_line_subway_red_northbound,
		alias = [
			"northredline",
			"northred",
			"rednorth",
			"redtotoxington",
			"redtotox",
			"redtott"
		    ],
		first_stop = poi_id_cv_subway_station,
		last_stop = poi_id_tt_subway_station,
		next_line = transport_line_subway_red_southbound,
		str_name = "The red subway line towards Toxington",
		schedule = {
			poi_id_cv_subway_station : [20, poi_id_wt_subway_station],
			poi_id_wt_subway_station : [20, poi_id_rr_subway_station],
			poi_id_rr_subway_station : [20, poi_id_dt_subway_station],
			poi_id_dt_subway_station : [20, poi_id_ck_subway_station],
			poi_id_ck_subway_station : [20, poi_id_gd_subway_station],
			poi_id_gd_subway_station : [20, poi_id_ah_subway_station],
			poi_id_ah_subway_station : [20, poi_id_tt_subway_station]
		    }

		),
	EwTransportLine( # red subway line from toxington to cratersville
		id_line = transport_line_subway_red_southbound,
		alias = [
			"southredline",
			"southred",
			"redsouth",
			"redtocratersville",
			"redtocraters",
			"redtocv"
		    ],
		first_stop = poi_id_tt_subway_station,
		last_stop = poi_id_cv_subway_station,
		next_line = transport_line_subway_red_northbound,
		str_name = "The red subway line towards Cratersville",
		schedule = {
			poi_id_tt_subway_station : [20, poi_id_ah_subway_station],
			poi_id_ah_subway_station : [20, poi_id_gd_subway_station],
			poi_id_gd_subway_station : [20, poi_id_ck_subway_station],
			poi_id_ck_subway_station : [20, poi_id_dt_subway_station],
			poi_id_dt_subway_station : [20, poi_id_rr_subway_station],
			poi_id_rr_subway_station : [20, poi_id_wt_subway_station],
			poi_id_wt_subway_station : [20, poi_id_cv_subway_station]
		    }

		),
	EwTransportLine( # green subway line from smogsburg to west glocksbury
		id_line = transport_line_subway_green_eastbound,
		alias = [
			"greeneastline",
			"greeneast",
			"eastgreen",
			"greentosmogsburg",
			"greentosmogs",
			"greentosb"
		    ],
		first_stop = poi_id_wgb_subway_station,
		last_stop = poi_id_sb_subway_station,
		next_line = transport_line_subway_green_westbound,
		str_name = "The green subway line towards Smogsburg",
		schedule = {
			poi_id_wgb_subway_station : [20, poi_id_jp_subway_station],
			poi_id_jp_subway_station : [20, poi_id_nsb_subway_station],
			poi_id_nsb_subway_station : [20, poi_id_kb_subway_station],
			poi_id_kb_subway_station : [20, poi_id_dt_subway_station],
			poi_id_dt_subway_station : [20, poi_id_sb_subway_station]
		    }

		),
	EwTransportLine( # green subway line from west glocksbury to smogsburg
		id_line = transport_line_subway_green_westbound,
		alias = [
			"greenwestline",
			"greenwest",
			"westgreen",
			"greentowestglocksbury",
			"greentowestglocks",
			"greentowgb"
		    ],
		first_stop = poi_id_sb_subway_station,
		last_stop = poi_id_wgb_subway_station,
		next_line = transport_line_subway_green_eastbound,
		str_name = "The green subway line towards West Glocksbury",
		schedule = {
			poi_id_sb_subway_station : [20, poi_id_dt_subway_station],
			poi_id_dt_subway_station : [20, poi_id_kb_subway_station],
			poi_id_kb_subway_station : [20, poi_id_gb_subway_station],
			poi_id_gb_subway_station : [20, poi_id_wgb_subway_station]
		    }

		),
	EwTransportLine( # blue subway line from downtown to assault flats beach
		id_line = transport_line_subway_blue_eastbound,
		alias = [
			"blueeastline",
			"blueeast",
			"eastblue",
			"bluetoassaultflatsbeach",
			"bluetoassaultflats",
			"bluetobeach",
			"bluetoafb"
		    ],
		first_stop = poi_id_dt_subway_station,
		last_stop = poi_id_afb_subway_station,
		next_line = transport_line_subway_blue_westbound,
		str_name = "The blue subway line towards Assault Flats Beach",
		schedule = {
			poi_id_dt_subway_station : [20, poi_id_gld_subway_station],
			poi_id_gld_subway_station : [20, poi_id_jr_subway_station],
			poi_id_jr_subway_station : [20, poi_id_vc_subway_station],
			poi_id_vc_subway_station : [20, poi_id_afb_subway_station]
		    }

		),
	EwTransportLine( # blue subway line from assault flats beach to downtown
		id_line = transport_line_subway_blue_westbound,
		alias = [
			"bluewestline",
			"bluewest",
			"westblue",
			"bluetodowntown",
			"bluetodt"
		    ],
		first_stop = poi_id_afb_subway_station,
		last_stop = poi_id_dt_subway_station,
		next_line = transport_line_subway_blue_eastbound,
		str_name = "The blue subway line towards Downtown NLACakaNM",
		schedule = {
			poi_id_afb_subway_station : [20, poi_id_vc_subway_station],
			poi_id_vc_subway_station : [20, poi_id_jr_subway_station],
			poi_id_jr_subway_station : [20, poi_id_gld_subway_station],
			poi_id_gld_subway_station : [20, poi_id_dt_subway_station]
		    }

		),
	#EwTransportLine( # white subway line from downtown to juvies row
	#	id_line = transport_line_subway_white_eastbound,
	#	alias = [
	#		"whiteeastline",
	#		"whiteeast",
	#		"eastwhite",
	#		"whitetojuviesrow",
	#		"whitetojuvies",
	#		"whitetojr"
	#	    ],
	#	first_stop = poi_id_dt_subway_station,
	#	last_stop = poi_id_jr_subway_station,
	#	next_line = transport_line_subway_white_westbound,
	#	str_name = "The white subway line towards Juvie's Row",
	#	schedule = {
	#		poi_id_dt_subway_station : [20, poi_id_rr_subway_station],
	#		poi_id_rr_subway_station : [20, poi_id_jr_subway_station]
	#	    }
	#	),
	#EwTransportLine( # white subway line from juvies row to downtown
	#	id_line = transport_line_subway_white_westbound,
	#	alias = [
	#		"whitewestline",
	#		"whitewest",
	#		"westwhite",
	#		"whitetodowntown",
	#		"whitetodt"
	#	    ],
	#	first_stop = poi_id_jr_subway_station,
	#	last_stop = poi_id_dt_subway_station,
	#	next_line = transport_line_subway_white_eastbound,
	#	str_name = "The white subway line towards Downtown NLACakaNM",
	#	schedule = {
	#		poi_id_jr_subway_station : [20, poi_id_rr_subway_station],
	#		poi_id_rr_subway_station : [20, poi_id_dt_subway_station]
	#	    }
	#	),
	EwTransportLine( # blimp line from dreadford to assault flats beach
		id_line = transport_line_blimp_df_to_afb,
		alias = [
			"assaultflatsbeachblimp",
			"assaultflatsblimp",
			"beachblimp",
			"afbblimp",
			"blimptoassaultflatsbeach",
			"blimptoassaultflats",
			"blimptobeach",
			"blimptoafb"
		    ],
		first_stop = poi_id_df_blimp_tower,
		last_stop = poi_id_afb_blimp_tower,
		next_line = transport_line_blimp_afb_to_df,
		str_name = "The blimp line towards Assault Flats Beach",
		schedule = {
			poi_id_df_blimp_tower : [60, poi_id_jaywalkerplain],
			poi_id_jaywalkerplain : [40, poi_id_northsleezeborough],
			poi_id_northsleezeborough : [40, poi_id_krakbay],
			poi_id_krakbay : [40, poi_id_downtown],
			poi_id_downtown : [40, poi_id_greenlightdistrict],
			poi_id_greenlightdistrict : [40, poi_id_vagrantscorner],
			poi_id_vagrantscorner : [40, poi_id_afb_blimp_tower]
		    }

		),
	EwTransportLine( # blimp line from assault flats beach to dreadford
		id_line = transport_line_blimp_afb_to_df,
		alias = [
			"dreadfordblimp",
			"dreadblimp",
			"dfblimp",
			"blimptodreadford",
			"blimptodread",
			"blimptodf"
		    ],
		first_stop = poi_id_afb_blimp_tower,
		last_stop = poi_id_df_blimp_tower,
		next_line = transport_line_blimp_df_to_afb,
		str_name = "The blimp line towards Dreadford",
		schedule = {
			poi_id_afb_blimp_tower : [60, poi_id_vagrantscorner],
			poi_id_vagrantscorner : [40, poi_id_greenlightdistrict],
			poi_id_greenlightdistrict : [40, poi_id_downtown],
			poi_id_downtown : [40, poi_id_krakbay],
			poi_id_krakbay : [40, poi_id_northsleezeborough],
			poi_id_northsleezeborough : [40, poi_id_jaywalkerplain],
			poi_id_jaywalkerplain : [40, poi_id_df_blimp_tower]
		    }

		)
]

id_to_transport_line = {}

for line in transport_lines:
	id_to_transport_line[line.id_line] = line
	for alias in line.alias:
		id_to_transport_line[alias] = line

	for poi in transport_stops:
		poi_data = id_to_poi.get(poi)
		if (poi in line.schedule.keys()) or (poi == line.last_stop):
			poi_data.transport_lines.add(line.id_line)


cosmetic_items_list = [
	EwCosmeticItem(
		id_cosmetic = "propellerhat",
		str_name = "propeller hat",
		str_desc = "A simple multi-color striped hat with a propeller on top. A staple of every juvenile’s youth.",
		rarity = rarity_plebeian,
	),
	EwCosmeticItem(
		id_cosmetic = "mininghelmet",
		str_name = "mining helmet",
		str_desc = "A typical construction hard hat with a head lamp strapped onto it.",
		rarity = rarity_plebeian,
	),
	EwCosmeticItem(
		id_cosmetic = "pickelhaube",
		str_name = "pickelhaube",
		str_desc = "A traditional Prussian spiked helmet from the nineteenth century.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "fedora",
		str_name = "fedora",
		str_desc = "A soft brimmed hat with a pinched crown. A classic piece of vintage Americana and a staple of film noir. Not to be confused with the trilby, the fedora is a hat befitting the hardboiled men of it’s time.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "baseballcap",
		str_name = "baseball cap",
		str_desc = "A classic baseball cap. A staple of American culture and subsequently freedom from tyranny. If you don’t own at least one of these hats you might as well have hopped the fence from Tijuana last night. Yeah, I’m racist, that going to be a problem for you??",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "backwardsbaseballcap",
		str_name = "backwards baseball cap",
		str_desc = "A classic baseball cap… with an urban twist! Heh, 'sup dawg? Nothing much, man. You know me, just mining some goddamn slime. Word 'n shit. Hell yeah.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "piratehat",
		str_name = "pirate hat",
		str_desc = "A swashbuckling buccaneer’s tricorne, stylized with a jolly roger on the front.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "eyepatch",
		str_name = "eyepatch",
		str_desc = "A black eyepatch. A striking accessory for the particularly swashbuckling, chauvinistic, or generally hardboiled of you. Genuine lack of two eyes optional and not recommended.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "cigarette",
		str_name = "cigarette",
		str_desc = "A single cigarette sticking out of your mouth. You huff these things down in seconds but you’re never seen without one. Everyone thinks you’re really, really cool.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "headband",
		str_name = "headband",
		str_desc = "A headband wrapped tightly around your forehead with long, flowing ends.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "handkerchief",
		str_name = "handkerchief",
		str_desc = "A bandanna tied on your head, creating a simple cap.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "bandanna",
		str_name = "bandanna",
		str_desc = "A handkerchief tied around your neck and covering your lower face.",
		rarity = rarity_plebeian,
	),
	EwCosmeticItem(
		id_cosmetic = "pairofsunglasses",
		str_name = "pair of sunglasses",
		str_desc = "An iconic pair of black sunglasses. Widely recognized as the coolest thing you can wear.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "pairofglasses",
		str_name = "pair of glasses",
		str_desc = "A simple pair of eyeglasses. You have perfectly serviceable eyesight, but you are a sucker for the bookworm aesthetic. People with actual issues with sight hate you.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "birthdayhat",
		str_name = "birthday hat",
		str_desc = "A striped, multi-color birthday hat. ",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "scarf",
		str_name = "scarf",
		str_desc = "A very thick striped wool scarf, in case 110° degrees is too nippy for you.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		str_name = "witch hat",
		id_cosmetic = "witchhat",
		str_desc = "A pointy, cone-shaped hat with a wide brim. It exudes a spooky essence.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "bomberhat",
		str_name = "bomber hat",
		str_desc = "A thick fur and leather aviator’s hat.",
		rarity = rarity_plebeian,
	),
	EwCosmeticItem(
		id_cosmetic = "tuxedo",
		str_name = "tuxedo",
		str_desc = "A classy, semi-formal suit for dashing rogues you can’t help but love. Instant charisma granted upon each !adorn.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "beanie",
		str_name = "beanie",
		str_desc = "A simple beanie with a pointed top and a slip stitch brim.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "jestershat",
		str_name = "jester's hat",
		str_desc = "A ridiculous, multi-colored hat with four bells dangling from protruding sleeves.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "pairof3dglasses",
		str_name = "pair of 3D glasses",
		str_desc = "A pair of totally tubular, ridiculously radical 3D glasses. Straight up stereoscopic, dude!",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "necktie",
		str_name = "necktie",
		str_desc = "A vintage necktie, reeking of coffee, college, and shaving cream.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "vikinghelmet",
		str_name = "viking helmet",
		str_desc = "A pointy bronze helmet with two sharp horns jutting out of the base.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "pairofflipflops",
		str_name = "pair of flip flops",
		str_desc = "A pair of loud, obnoxious flip flops. The price of your comfort is higher than you could ever know.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "fez",
		str_name = "fez",
		str_desc = "A short fez with a tassel attached to the top. Fezzes are cool. Or, are bowties cool? You forget, and frankly you’re embarrassed you remember either one of them.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "bowtie",
		str_name = "bowtie",
		str_desc = "A quite dapper, neatly tied butterfly bowtie. Bowties are cool. Or, are fezzes cool? You forget, and frankly you’re embarrassed you remember either one of them.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "cowboyhat",
		str_name = "cowboy hat",
		str_desc = "An essential piece of Wild West memorabilia, a bonafide ten gallon Stetson. Befitting the individualistic individuals that made them famous. Yeehaw, and all that stuff.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "kepi",
		str_name = "kepi",
		str_desc = "A short kepi with a sunken top and an insignia on the front.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "tamoshanter",
		str_name = "tam o' shanter",
		str_desc = "A traditional Scottish wool bonnet with a plaid pattern.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "ushanka",
		str_name = "ushanka",
		str_desc = "A traditional Russian fur cap with thick wool ear flaps.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "karategi",
		str_name = "karategi",
		str_desc = "A traditional Japanese karateka’s outfiit, complete with a belt with extended ends that easily flow in the wind for dramatic effect.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "turban",
		str_name = "turban",
		str_desc = "A traditional Arabian headdress, lavishly decorated with a single large jewel and protruding peacock feather.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "nemes",
		str_name = "nemes",
		str_desc = "The traditional ancient Egyptian pharaoh's striped head cloth.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "varsityjacket",
		str_name = "varsity jacket",
		str_desc = "An American baseball jacket, with a large insignia on the left side of the chest.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "sombrero",
		str_name = "sombrero",
		str_desc = "A traditional Mexican sombrero, with an extra-wide brim to protect you from the blistering Arizonian sun.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "hawaiianshirt",
		str_name = "hawaiian shirt",
		str_desc = "A brightly colored Hawaiian shirt with a floral pattern. It reeks of slima colada and the complementary shampoo from the resort in Assault Flats Beach.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "fursuit",
		str_name = "fursuit",
		str_desc = "A fursuit. Custom-made and complete with high quality faux fur, padded digitigrade legs, follow-me eyes, adjustable facial expressions, and a fan in the head. It is modeled off your original character, also known as your fursona. Some would call its character design “ugly” or “embarrassing,” but you think it's perfect.",
		rarity = rarity_patrician
	),
	EwCosmeticItem(
		id_cosmetic = "diadem",
		str_name = "diadem",
		str_desc = "The traditional Greco-Roman laurel wreath symbolizing sovereignty and power. Be careful about wearing this around in public, you might just wake up with 23 stab wounds.",
		rarity = rarity_patrician
	),
	EwCosmeticItem(
		id_cosmetic = "billshat",
		str_name = "Bill's Hat",
		str_desc = "A military beret with a shield insignia on the front.",
		rarity = rarity_patrician
	),
	EwCosmeticItem(
		id_cosmetic = "weddingring",
		str_name = "wedding ring",
		str_desc = "A silver ring with a decently large diamond on top. For the person you love most in the entire world. <3",
		rarity = rarity_patrician
	),
	EwCosmeticItem(
		id_cosmetic = "earbuds",
		str_name = "earbuds",
		str_desc = "A pair of white standard iPod earbuds. Who knows what sort of tasty jams you must be listening to while walking down the street?",
		rarity = rarity_patrician
	),
	EwCosmeticItem(
		id_cosmetic = "nursesoutfit",
		str_name = "nurse's outfit",
		str_desc = "A disturbingly revealing nurse’s outfit that shows off your lumpy, fleshy visage. No one likes that you wear this. Theming bonus for responding to people’s crackpot ideas in the nurse’s office, though.",
		rarity = rarity_plebeian
	),
	EwCosmeticItem(
		id_cosmetic = "heartboxers",
		str_name = "heart boxers",
		str_desc = "A staple of comedy. A pair of white boxers with stylized cartoon hearts tiled all over it. Sure hope your pants aren’t hilariously ripped or unadorned while you’re wearing these, how embarrassing! Hahaha! We like to have fun here.",
		rarity = rarity_plebeian,
	),
	EwCosmeticItem(
		id_cosmetic = "captainshat",
		str_name = "Captain's Hat",
		str_desc = "The perfect hat for sailing across the Slime Sea, commanding a navy fleet, or prematurely ending your lucrative My Little Pony review series in favor of starting a shitty Pokemon Nuzlocke series. For shame.",
		ingredients = "poketuber",
	),
	EwCosmeticItem(
		id_cosmetic = "juveolantern",
		str_name = "Juve-O'-Lantern",
		str_desc = "Hand-carved with a hole just barely big enough to fit your head in, this Juve O' Lantern severely hinders your combat ability. But, you look fucking sick while wearing it, so who cares.",
		ingredients = "pulpgourds",
	),
	EwCosmeticItem(
		id_cosmetic = "bowlerhat",
		str_name = "Bowler Hat",
		str_desc = "A simply traditional billyock. You’re gonna be the talk of the toy box with this dashing felt cosmetic! Now you just have to work on the moustache.",
		ingredients = "sourpotatoes",
	),
	EwCosmeticItem(
		id_cosmetic = "cabbagetreehat",
		str_name = "Cabbage Tree Hat",
		str_desc = "An unmistakably Australian hat, with a wide brim and a high crown.",
		ingredients = "bloodcabbages",
	),
	EwCosmeticItem(
		id_cosmetic = "braces",
		str_name = "Braces",
		str_desc = "An old fashioned orthodontic headgear. Elaborate metal wires and braces hold your nearly eroded, crooked teeth together in what can genously be called a mouth. You are in agony, and so is everyone that looks at you.",
		ingredients = "joybeans",
	),
	EwCosmeticItem(
		id_cosmetic = "hoodie",
		str_name = "Hoodie",
		str_desc = "Perfect for keeping warm in the middle of the blisteringly hot Arizonian desert! Heatstroke or bust!",
		ingredients = "purplekilliflower",
	),
	EwCosmeticItem(
		id_cosmetic = "copbadge",
		str_name = "Cop Badge",
		str_desc = "What the fuck are you doing with this thing? Are you TRYING to make the sewers your permanent residence? Acquaint yourself with the !drop command and FAST, before you don’t have a body to wear the badge on.",
		ingredients = "razornuts",
	),
	EwCosmeticItem(
		id_cosmetic = "strawhat",
		str_name = "Straw Hat",
		str_desc = "A wide-brimmed straw hat, the perfect hat for farming.",
		ingredients = "pawpaw",
	),
	EwCosmeticItem(
		id_cosmetic = "cosplayhorns",
		str_name = "Cosplay Horns",
		str_desc = "You’re not entirely sure what these things are, but they sort of look like brightly painted, candy corn colored, paper mache horns that are hot glued onto a black headband. Their purpose is mysterious, but for some reason you are inclined to adorn them… perhaps you understood their importance in a past life.",
		ingredients = "sludgeberries",
	),
	EwCosmeticItem(
		id_cosmetic = "youfavoritehat",
		str_name = "***Your Favorite Hat***",
		str_desc = "***It fits perfectly, and it’s just your style! You love wearing this cosmetic far more than any other, it’s simply the best.***",
		ingredients = "suganmanuts",
	),
	EwCosmeticItem(
		id_cosmetic = "pajamaonesie",
		str_name = "Pajama Onesie",
		str_desc = "A soft jumpsuit with an audacious, repeating design printed over the entire cosmetic. You feel like getting a little bit fucking rowdy wearing this outrageous onesie. ",
		ingredients = "pinkrowddishes",
	),
	EwCosmeticItem(
		id_cosmetic = "pairofcircularsunglasses",
		str_name = "Pair of Circular Sunglasses",
		str_desc = "Sunglasses, but in a circle! Genius! You can't wait to show the world your hot takes on television shows for girls.",
		ingredients = "dankwheat",
	),
	EwCosmeticItem(
		id_cosmetic = "flowercrown",
		str_name = "Flower Crown",
		str_desc = "A lovingly handcrafted crown of flowers, connected by a string. You’re gonna be famous on Pinterest with a look like this!",
		ingredients = "brightshade",
	),
	EwCosmeticItem(
		id_cosmetic = "spikedbracelets",
		str_name = "Spiked Bracelets",
		str_desc = "Hilariously unrealistic spiked bracelets, ala Bowser, King of the Koopas. You’re hyper aware of these fashion disasters whenever you’re walking, making sure to swing them as far away from your body as possible.",
		ingredients = "blacklimes",
	),
	EwCosmeticItem(
		id_cosmetic = "slimecorppin",
		str_name = "SlimeCorp Pin",
		str_desc = "An enamel pin of the SlimeCorp logo, a badge of loyalty to your favorite charismatic megacorporation. Dude, like, *”Follow He Who Turns The Wheels”*, bro!!",
		ingredients = "phosphorpoppies",
	),
	EwCosmeticItem(
		id_cosmetic = "overalls",
		str_name = "Overalls",
		str_desc = "Simple, humble denim overalls, for a simple, humble farmer such as yourself.",
		ingredients = "direapples",
	),
]

# Slimeoid attributes.

# All body attributes in the game.
body_list = [
	EwBody( # body 1
		id_body = "teardrop",
		alias = [
			"tear",
			"drop",
			"oblong",
			"a"
		],
		str_create = "You press a button on the body console labelled 'A'. Through the observation port, you see the rapidly congealing proto-Slimeoid take on a roughly teardrop-shaped form.",
		str_body = "It is teardrop-shaped.",
		str_observe = "{slimeoid_name} is bobbing its top-heavy body back and forth."
	),
	EwBody( # body 2
		id_body = "wormlike",
		alias = [
			"long",
			"serpent",
			"serpentine",
			"b"
		],
		str_create = "You press a button on the body console labelled 'B'. Through the observation port, you see the rapidly congealing proto-Slimeoid begin to stretch into an elongated form.",
		str_body = "It is long and wormlike.",
		str_observe = "{slimeoid_name} is twisting itself around, practicing tying its knots."
	),
	EwBody( # body 3
		id_body = "spherical",
		alias = [
			"sphere",
			"orb",
			"ball",
			"c"
		],
		str_create = "You press a button on the body console labelled 'C'. Through the observation port, you see the rapidly congealing proto-Slimeoid take on a roughly spherical form.",
		str_body = "It is generally orb-shaped.",
		str_observe = "{slimeoid_name} flops over onto one side of its round body."
	),
	EwBody( # body 4
		id_body = "humanoid",
		alias = [
			"biped",
			"human",
			"d"
		],
		str_create = "You press a button on the body console labelled 'D'. Through the observation port, you see the rapidly congealing proto-Slimeoid curl into a foetal, vaguely humanoid form.",
		str_body = "It is vaguely humanoid.",
		str_observe = "{slimeoid_name} is scraping at something on the ground with its arms."
	),
	EwBody( # body 5
		id_body = "tentacled",
		alias = [
			"squid",
			"squidlike",
			"tentacle",
			"tentacles",
			"e"
		],
		str_create = "You press a button on the body console labelled 'E'. Through the observation port, you see the rapidly congealing proto-Slimeoid begin to sprout long tendrils from its nucleus.",
		str_body = "It is a mass of tendrils.",
		str_observe = "{slimeoid_name} is moving its tentacles around, running them over one another."
	),
	EwBody( # body 6
		id_body = "amorphous",
		alias = [
			"none",
			"formless",
			"f"
		],
		str_create = "You press a button on the body console labelled 'F'. Through the observation port, you see the rapidly congealing proto-Slimeoid accreting itself together with no distinct shape to speak of.",
		str_body = "It has no defined shape.",
		str_observe = "{slimeoid_name}'s body is spread out on the floor like a kind of living puddle."
	),
	EwBody( # body 7
		id_body = "quadruped",
		alias = [
			"animal",
			"g"
		],
		str_create = "You press a button on the body console labelled 'G'. Through the observation port, you see the rapidly congealing proto-Slimeoid beginning to grow bones and vertebrae as it starts to resemble some kind of quadruped.",
		str_body = "It has a body shape vaguely reminiscent of a quadruped.",
		str_observe = "{slimeoid_name} has its hindquarters lowered in a sort of sitting position."
	)
]

# A map of id_body to EwBody objects.
body_map = {}

# A list of body names
body_names = []

# Populate body map, including all aliases.
for body in body_list:
	body_map[body.id_body] = body
	body_names.append(body.id_body)

	for alias in body.alias:
		body_map[alias] = body

# All head attributes in the game.
head_list = [
	EwHead( # head 1
		id_head = "eye",
		alias = [
			"cyclops",
			"a"
		],
		str_create = "You press a button on the head console labelled 'A'. Through the observation port, you see a dark cluster within the proto-Slimeoid begin to form into what looks like a large eye.",
		str_head = "Its face is a single huge eye.",
		str_feed = "",
		str_fetch = "You toss a ball for {slimeoid_name} to fetch. {slimeoid_name}'s huge eye follows the ball's arc, and it makes a leap to catch it!!\n\n...only to get socked right in the eye, sending it to the floor in pain. Depth perception... it's truly a gift."
	),
	EwHead( # head 2
		id_head = "maw",
		alias = [
			"mouth",
			"b"
		],
		str_create = "You press a button on the head console labelled 'B'. Through the observation port, you see an opening form in what you think is the proto-Slimeoid's face, which begins to sprout large pointed teeth.",
		str_head = "Its face is a huge toothy mouth.",
		str_feed = "",
		str_fetch = "You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} slavers and drools as it awaits the throw, and when it sees the ball start to fly, it lunges to grab it out of the air in its huge toothy maw, slicing it to shreds with its teeth in seconds."
	),
	EwHead( # head 3
		id_head = "void",
		alias = [
			"hole",
			"c"
		],
		str_create = "You press a button on the head console labelled 'C'. Through the observation port, you see what you thought was the proto-Slimeoid's face suddenly sucked down into its body, as though by a black hole.",
		str_head = "Its face is an empty black void.",
		str_feed = "",
		str_fetch = "You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} positions itself to catch the ball in it's... face? The ball falls into the empty void of {slimeoid_name}'s face, then just keeps falling, falling, falling, down into the depths, falling so far it dissapears forever."
	),
	EwHead( # head 4
		id_head = "beast",
		alias = [
			"animal",
			"dragon",
			"d"
		],
		str_create = "You press a button on the head console labelled 'D'. Through the observation port, you see the beginnings of an animal-like face forming on your proto-Slimeoid, with what might be eyes, a nose, teeth... maybe.",
		str_head = "Its face is that of a vicious beast.",
		str_feed = "",
		str_fetch = "You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} focuses its eyes and bares its teeth, then makes a flying leap, snapping the ball clean out of the air in its jaws! It comes back to you and drops the ball at your feet. Good boy!"
	),
	EwHead( # head 5
		id_head = "insect",
		alias = [
			"bug",
			"insectoid",
			"e"
		],
		str_create = "You press a button on the head console labelled 'E'. Through the observation port, you see the proto-Slimeoid suddenly bulge with a series of hard orbs which congeal into what appear to be large compound eyes.",
		str_head = "It has bulging insectoid eyes and mandibles.",
		str_feed = "",
		str_fetch = "You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} stands motionless, presumably watching the ball with its large compound eyes, before darting toward it as it sails through the air, snapping its mandibles around the ball and slicing it cleanly in two."
	),
	EwHead( # head 6
		id_head = "skull",
		alias = [
			"skeleton",
			"f"
		],
		str_create = "You press a button on the head console labelled 'F'. Through the observation port, you see the proto-Slimeoid's frontal features twist into a ghastly death's-head.",
		str_head = "Its face resembles a skull.",
		str_feed = "",
		str_fetch = "You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} moves as quickly as it can to make the catch, making it just before the ball lands! With a thunk, the ball lodges itself in {slimeoid_name}'s open eye socket. {slimeoid_name} yanks it out and tosses the ball back to you. Euughh."
	),
	EwHead( # head 7
		id_head = "none",
		alias = [
			"g"
		],
		str_create = "You press a button on the head console labelled 'G'. Through the observation port, you see the proto-Slimeoid's front end melt into an indistinct mass.",
		str_head = "It has no discernable head.",
		str_feed = "",
		str_fetch = "You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} moves under the ball as it flies through the air, but makes no attempt to catch it in its mouth on account of having none. The ball lands next to {slimeoid_name}, who merely looks on. Actually, you can't tell where it's looking."
	)
]

# A map of id_head to EwBody objects.
head_map = {}

# A list of head names
head_names = []

# Populate head map, including all aliases.
for head in head_list:
	head_map[head.id_head] = head
	head_names.append(head.id_head)

	for alias in head.alias:
		head_map[alias] = head

# All mobility attributes in the game.
mobility_list = [
	EwMobility( # mobility 1
		id_mobility = "legs",
		alias = [
			"animal",
			"quadruped",
			"biped",
			"jointed",
			"limbs",
			"a"
		],
		str_advance = "{active} barrels toward {inactive}!",
		str_retreat = "{active} leaps away from {inactive}!",
		str_advance_weak = "{active} limps toward {inactive}!",
		str_retreat_weak = "{active} limps away from {inactive}!",
		str_create = "You press a button on the mobility console labelled 'A'. Through the observation port, you see jointed limbs begin to sprout from the proto-Slimeoid's underside.",
		str_mobility = "It walks on legs.",
		str_defeat = "{slimeoid_name}'s knees buckle under it as it collapses to the ground, defeated!",
		str_walk = "{slimeoid_name} walks along beside you."
	),
	EwMobility( # mobility 2
		id_mobility = "rolling",
		alias = [
			"roll",
			"b"
		],
		str_advance = "{active} rolls itself toward {inactive}!",
		str_retreat = "{active} rolls away from {inactive}!",
		str_advance_weak = "{active} rolls itself unsteadily towards {inactive}!",
		str_retreat_weak = "{active} rolls unsteadily away from {inactive}!",
		str_create = "You press a button on the mobility console labelled 'B'. Through the observation port, you see the proto-Slimeoid becoming smoother and rounder.",
		str_mobility = "It moves by rolling its body around.",
		str_defeat = "{slimeoid_name} rolls itself over before collapsing on the ground, defeated!",
		str_walk = "{slimeoid_name} rolls itself along the ground behind you."
	),
	EwMobility( # mobility 3
		id_mobility = "flagella",
		alias = [
			"flagella",
			"tendrils",
			"tentacles",
			"c"
		],
		str_advance = "{active} slithers toward {inactive}!",
		str_retreat = "{active} slithers away from {inactive}!",
		str_advance_weak = "{active} drags itself toward {inactive}!",
		str_retreat_weak = "{active} drags itself away from {inactive}!",
		str_create = "You press a button on the mobility console labelled 'C'. Through the observation port, you see masses of writhing flagella begin to protrude from the proto-Slimeoid's extremities.",
		str_mobility = "It moves by pulling itself around with its flagella.",
		str_defeat = "{slimeoid_name}'s flagella go limp as it collapses to the ground, defeated!",
		str_walk = "{slimeoid_name} writhes its way along the ground on its flagella next to you."
	),
	EwMobility( # mobility 4
		id_mobility = "jets",
		alias = [
			"fluid",
			"jet",
			"d"
		],
		str_advance = "{active} propels itself toward {inactive}!",
		str_retreat = "{active} propels itself away from {inactive}!",
		str_advance_weak = "{active} sputters towards {inactive}!",
		str_retreat_weak = "{active} sputters away from {inactive}!",
		str_create = "You press a button on the mobility console labelled 'D'. Through the observation port, you see openings forming in the proto-Slimeoid's body, which begin to vent fluid.",
		str_mobility = "It moves via jet-propulsion by squirting fluids.",
		str_defeat = "{slimeoid_name} fires its fluid jets wildly in a panic until it completely deflates and collapses, defeated!",
		str_walk = "{slimeoid_name} tries to keep pace with you, spurting jets of fluid to propel itself along behind you."
	),
	EwMobility( # mobility 5
		id_mobility = "slug",
		alias = [
			"undulate",
			"e"
		],
		str_advance = "{active} undulates its way toward {inactive}!",
		str_retreat = "{active} undulates itself away from {inactive}!",
		str_advance_weak = "{active} heaves itself slowly toward {inactive}!",
		str_retreat_weak = "{active} heaves itself slowly away from {inactive}!",
		str_create = "You press a button on the mobility console labelled 'E'. Through the observation port, you see the base of the proto-Slimeoid's body widen and flatten out.",
		str_mobility = "It moves like a slug, undulating its underside along the ground.",
		str_defeat = "{slimeoid_name} stops moving entirely and collapses to the ground, defeated!",
		str_walk = "{slimeoid_name} glacially drags its way along behind you in its slug-like way. Your walk ends up taking fucking forever."
	),
	EwMobility( # mobility 5
		id_mobility = "float",
		alias = [
			"gas",
			"f"
		],
		str_advance = "{active} floats toward {inactive}!",
		str_retreat = "{active} floats away from {inactive}!",
		str_advance_weak = "{active} bobs unsteadily through the air towards {inactive}!",
		str_retreat_weak = "{active} bobs unsteadily away from {inactive}!",
		str_create = "You press a button on the mobility console labelled 'F'. Through the observation port, you see the of the proto-Slimeoid's body start to inflate itself.",
		str_mobility = "It floats in the air with the use of super-low-density gas bladders.",
		str_defeat = "{slimeoid_name} spins wildly in the air before careening to the ground, defeated!",
		str_walk = "{slimeoid_name} bobs along next to you on its leash like a balloon."
	),
	EwMobility( # mobility 5
		id_mobility = "wings",
		alias = [
			"fly",
			"g"
		],
		str_advance = "{active} darts through the air toward {inactive}!",
		str_retreat = "{active} flaps away from {inactive}!",
		str_advance_weak = "{active} flaps its way doggedly towards {inactive}!",
		str_retreat_weak = "{active} flaps doggedly away from {inactive}!",
		str_create = "You press a button on the mobility console labelled 'G'. Through the observation port, you see the proto-slimeoid start to sprout wide, flat, thin appendages.",
		str_mobility = "It moves by making short flights through the air with its wings.",
		str_defeat = "{slimeoid_name} flaps helplessly as it spins out and crashes into the ground, defeated!",
		str_walk = "{slimeoid_name} flaps along through the air next to you, occasionally perching in trees or windowsills along the route."
	)
]

# A map of id_mobility to EwBody objects.
mobility_map = {}

# A list of mobility names
mobility_names = []

# Populate mobility map, including all aliases.
for mobility in mobility_list:
	mobility_map[mobility.id_mobility] = mobility
	mobility_names.append(mobility.id_mobility)

	for alias in mobility.alias:
		mobility_map[alias] = mobility

# All offense attributes in the game.
offense_list = [
	EwOffense( # offense 1
		id_offense = "blades",
		alias = [
			"edged",
			"edges",
			"edgy",
			"bladed",
			"blade",
			"a"
		],
		str_attack = "{active} slashes {inactive} with its blades!",
		str_attack_weak = "{active} desperately swipes at {inactive} with its blades!",
		str_attack_coup = "{active} slices deep into {inactive}! Green goo splatters onto the ground from the wound!!",
		str_create = "You press a button on the weapon console labelled 'A'. Through the observation port, you see long, sharp protrusions begin to form on the proto-Slimeoid's extremities.",
		str_offense = "It slices foes with retractible blades.",
		str_observe = "{slimeoid_name} is sharpening its retractible blades on a stone nearby."
	),
	EwOffense( # offense 2
		id_offense = "teeth",
		alias = [
			"bite",
			"biting",
			"crunch",
			"crunching",
			"b"
		],
		str_attack = "{active} sinks its teeth into {inactive}!",
		str_attack_weak = "{active} gnashes its teeth, biting {inactive} wherever it can!",
		str_attack_coup = "{active} bites hard into {inactive}, tearing off a piece and chewing it hungrily!",
		str_create = "You press a button on the weapon console labelled 'B'. Through the observation port, you see large bony structures resembling teeth forming in the proto-Slimeoid's... mouth?",
		str_offense = "It can bite foes with deadly fangs.",
		str_observe = "{slimeoid_name} is idly picking its sharp teeth."
	),
	EwOffense( # offense 3
		id_offense = "grip",
		alias = [
			"squeeze",
			"grab",
			"squeezing",
			"grabbing",
			"gripping",
			"constrict",
			"constriction",
			"c"
		],
		str_attack = "{active} grabs {inactive} and squeezes hard!",
		str_attack_weak = "{active} grabs at {inactive}, trying to fend it off!",
		str_attack_coup = "{active} grips {inactive} like a vice, squeezing until you hear a sickening pop!",
		str_create = "You press a button on the weapon console labelled 'C'. Through the observation port, you see the proto-Slimeoid's limbs becoming thicker and stronger, beginning to twist and writhe, seeking something to grip onto.",
		str_offense = "It can grab and crush its foes with its limbs.",
		str_observe = "{slimeoid_name} picks up a rock off the ground and squeezes it like a stress ball."
	),
	EwOffense( # offense 4
		id_offense = "bludgeon",
		alias = [
			"strike",
			"striking",
			"smash",
			"smashing",
			"bash",
			"bashing",
			"crush",
			"crushing",
			"d"
		],
		str_attack = "{active} bashes {inactive} with its limbs!",
		str_attack_weak = "{active} flails its limbs to strike back at {inactive}!",
		str_attack_coup = "{active} winds back and smashes {inactive}, dealing a knockout blow!",
		str_create = "You press a button on the weapon console labelled 'D'. Through the observation port, you see the ends of the proto-Slimeoid's limbs becoming harder and heavier.",
		str_offense = "It can smash foes with one or more of its limbs.",
		str_observe = "{slimeoid_name} spots an insect on the ground nearby and smashes it."
	),
	EwOffense( # offense 5
		id_offense = "spikes",
		alias = [
			"puncture",
			"spear",
			"e"
		],
		str_attack = "{active} skewers {inactive} with its spikes!",
		str_attack_weak = "{active} tries to defend itself from {inactive} with its spikes!",
		str_attack_coup = "{active} punctures {inactive} with its spikes, opening a hole that oozes green fluid all over the ground!",
		str_create = "You press a button on the weapon console labelled 'E'. Through the observation port, you see hard spikes forming out of the congealing slime biomatter.",
		str_offense = "It can puncture its enemies with the spikes on its body.",
		str_observe = "{slimeoid_name} carefully adjusts its position so as not to prick itself with its own spikes."
	),
	EwOffense( # offense 6
		id_offense = "electricity",
		alias = [
			"strike",
			"f"
		],
		str_attack = "{active} unleashes a pent-up electrical discharge into {inactive}!",
		str_attack_weak = "{active} sparks and flickers with electricity, shocking {inactive}!",
		str_attack_coup = "{active} charges up and sends a bolt of electricity through {inactive}, making it sizzle!",
		str_create = "You press a button on the weapon console labelled 'F'. Through the observation port, you see the proto-Slimeoid begin to spark with small electrical discharges.",
		str_offense = "It crackles with stored electrical energy.",
		str_observe = "A fly flies a little too near {slimeoid_name} and is zapped with a tiny bolt of electricity, killing it instantly."
	),
	EwOffense( # offense 7
		id_offense = "slam",
		alias = [
			"bodyslam",
			"g"
		],
		str_attack = "{active} slams its entire body into {inactive}!",
		str_attack_weak = "{active} flails itself back against {inactive}'s onslaught!",
		str_attack_coup = "{active} hurls its whole weight into {inactive}, crushing it to the ground!",
		str_create = "You press a button on the weapon console labelled 'G'. Through the observation port, you see the ends of the proto-Slimeoid's congealing body condense, becoming heavier and more robust.",
		str_offense = "It can slam its body into its foes with tremendous force.",
		str_observe = "{slimeoid_name} shifts its weight back and forth before settling down in a kind of sumo-squat position."
	)
]

# A map of id_offense to EwBody objects.
offense_map = {}

# A list of offense names
offense_names = []

# Populate offense map, including all aliases.
for offense in offense_list:
	offense_map[offense.id_offense] = offense
	offense_names.append(offense.id_offense)

	for alias in offense.alias:
		offense_map[alias] = offense

# All defense attributes in the game.
defense_list = [
	EwDefense( # defense 1
		id_defense = "scales",
		alias = [
			"scale",
			"scaled",
			"scaly",
			"a"
		],
		str_defense = "",
		str_pet = "You carefully run your hand over {slimeoid_name}'s hide, making sure to go with the grain so as not to slice your fingers open on its sharp scales.",
		str_create = "You press a button on the armor console labelled 'A'. Through the observation port, you see the proto-Slimeoid's skin begin to glint as it sprouts roughly-edged scales.",
		str_armor = "It is covered in scales."
	),
	EwDefense( # defense 2
		id_defense = "boneplates",
		alias = [
			"bone",
			"bony",
			"bones",
			"plate",
			"plates",
			"armor",
			"plating",
			"b"
		],
		str_defense = "",
		str_pet = "You pat one of the hard, bony plates covering {slimeoid_name}'s skin.",
		str_create = "You press a button on the armor console labelled 'B'. Through the observation port, you see hard bony plates begin to congeal on the proto-Slimeoid's surface.",
		str_armor = "It is covered in bony plates."
	),
	EwDefense( # defense 3
		id_defense = "quantumfield",
		alias = [
			"quantum",
			"field",
			"energy",
			"c"
		],
		str_defense = "",
		str_pet = "You pat {slimeoid_name}, and your hand tingles as it passes through the quantum field that surrounds its body.",
		str_create = "You press a button on the armor console labelled 'C'. Through the observation port, start to notice the proto-Slimeoid begin to flicker, and you hear a strange humming sound.",
		str_armor = "It is enveloped in a field of quantum uncertainty."
	),
	EwDefense( # defense 4
		id_defense = "formless",
		alias = [
			"amorphous",
			"shapeless",
			"squishy",
			"d"
		],
		str_defense = "",
		str_pet = "You pat {slimeoid_name}, its fluid, shapeless body squishing and deforming in response to even slight pressure.",
		str_create = "You press a button on the armor console labelled 'D'. Through the observation port, you see the proto-Slimeoid suddenly begin to twist itself, stretching and contracting as its shape rapidly shifts.",
		str_armor = "It is malleable and can absorb blows with ease."
	),
	EwDefense( # defense 5
		id_defense = "regeneration",
		alias = [
			"healing",
			"regen",
			"e"
		],
		str_defense = "",
		str_pet = "You pat {slimeoid_name}. Its skin is hot, and you can feel it pulsing rhythmically.",
		str_create = "You press a button on the armor console labelled 'E'. Through the observation port, you see the proto-Slimeoid begin to pulse, almost like a beating heart.",
		str_armor = "It can regenerate damage to its body rapidly."
	),
	EwDefense( # defense 6
		id_defense = "stench",
		alias = [
			"stink",
			"smell",
			"f"
		],
		str_defense = "",
		str_pet = "You pat {slimeoid_name}, taking care not to inhale through your nose, as one whiff of its odor has been known to make people lose their lunch.",
		str_create = "You press a button on the armor console labelled 'F'. Through the observation port, you see the proto-Slimeoid suddenly begin to twist itself, stretching and contracting as its shape rapidly shifts.",
		str_armor = "It exudes a horrible stench."
	),
	EwDefense( # defense 7
		id_defense = "oil",
		alias = [
			"slick",
			"g"
		],
		str_defense = "",
		str_pet = "You pat {slimeoid_name}'s slick wet skin, and your hand comes away coated in a viscous, slippery oil.",
		str_create = "You press a button on the armor console labelled 'G'. Through the observation port, you see the surface of the proto-Slimeoid become shiny with some kind of oily fluid.",
		str_armor = "It is covered in a coating of slippery oil."
	)
]

# A map of id_defense to EwBody objects.
defense_map = {}

# A list of defense names
defense_names = []

# Populate defense map, including all aliases.
for defense in defense_list:
	defense_map[defense.id_defense] = defense
	defense_names.append(defense.id_defense)

	for alias in defense.alias:
		defense_map[alias] = defense

# All special attributes in the game.
special_list = [
	EwSpecial( # special 1
		id_special = "spit",
		alias = [
			"spitting",
			"spray",
			"squirt",
			"spraying",
			"squirting",
			"liquid",
			"fluid",
			"acid",
			"acidic",
			"toxic",
			"poison",
			"a"
		],
		str_special_attack = "{active} spits acidic ooze onto {inactive}!",
		str_special_attack_weak = "{active} coughs and spurts up a sputtering spray of acid at {inactive}!",
		str_special_attack_coup = "{active} vomits a torrent of acid onto {inactive}, deteriorating it to the point that it can no longer fight!",
		str_create = "You press a button on the special attack console labelled 'A'. Through the observation port, you see the proto-Slimeoid's body begin to excrete a foul, toxic ooze.",
		str_special = "It can spit acidic ooze.",
		str_observe = "A bit of acidic fluid drips from {slimeoid_name} onto the ground, where it smokes and sizzles."
	),
	EwSpecial( # special 2
		id_special = "laser",
		alias = [
			"beam",
			"energy",
			"radiation",
			"b"
		],
		str_special_attack = "{active} sears {inactive} with a blast of radiation!",
		str_special_attack_weak = "{active} starts to flicker before firing an unsteady beam of light at {inactive}!",
		str_special_attack_coup = "{active} blasts {inactive} with a beam of green energy, searing it all over its body!",
		str_create = "You press a button on the special attack console labelled 'B'. Through the observation port, you see the proto-Slimeoid's body begin to glow with energy as the gestation vat's built-in Geiger Counter begins to click frantically.",
		str_special = "It can fire beams of radiation.",
		str_observe = "{slimeoid_name} suddenly glows with radioactive energy. Best not to look directly at it until it settles down..."
	),
	EwSpecial( # special 3
		id_special = "spines",
		alias = [
			"spikes",
			"spiky",
			"spiny",
			"quills",
			"c"
		],
		str_special_attack = "{active} fires a volley of quills into {inactive}!",
		str_special_attack_weak = "{active} desperately fires a few of its last quills into {inactive}!",
		str_special_attack_coup = "{active} fires a rapid burst of sharp quills into {inactive}, filling it like a pincushion!",
		str_create = "You press a button on the special attack console labelled 'C'. Through the observation port, you see the proto-Slimeoid's congealing body suddenly protruding with long, pointed spines, which quickly retract back into it.",
		str_special = "It can fire sharp quills.",
		str_observe = "{slimeoid_name} shudders and ejects a few old quills onto the ground. You can see new ones already growing in to replace them."
	),
	EwSpecial( # special 4
		id_special = "throw",
		alias = [
			"throwing",
			"hurling",
			"hurl",
			"d"
		],
		str_special_attack = "{active} picks up a nearby {object} and hurls it into {inactive}!",
		str_special_attack_weak = "{active} unsteadily hefts a nearby {object} before throwing it into {inactive}!",
		str_special_attack_coup = "{active} hurls a {object}, which smashes square into {inactive}, knocking it to the ground! A direct hit!",
		str_create = "You press a button on the special attack console labelled 'D'. Through the observation port, you see the proto-Slimeoid's limbs become more articulate.",
		str_special = "It can hurl objects at foes.",
		str_observe = "{slimeoid_name} is idly picking up stones and seeing how far it can toss them."
	),
	EwSpecial( # special 5
		id_special = "TK",
		alias = [
			"telekinesis",
			"psychic",
			"e"
		],
		str_special_attack = "{active} focuses on {inactive}... {inactive} convulses in pain!",
		str_special_attack_weak = "{active}'s cranium bulges and throbs! {inactive} convulses!",
		str_special_attack_coup = "{active} emanates a strange static sound as {inactive} is inexplicably rendered completely unconscious!",
		str_create = "You press a button on the special attack console labelled 'E'. You momentarily experience an uncomfortable sensation, sort of like the feeling you get when you know there's a TV on in the room even though you can't see it.",
		str_special = "It can generate harmful frequencies with its brainwaves.",
		str_observe = "You momentarily black out. When you come to, your nose is bleeding. {slimeoid_name} tries to look innocent."
	),
	EwSpecial( # special 6
		id_special = "fire",
		alias = [
			"chemical",
			"breath",
			"breathe",
			"f"
		],
		str_special_attack = "{active} ejects a stream of fluid which ignites in the air, burning {inactive}!",
		str_special_attack_weak = "{active} fires an unsteady, sputtering stream of fluid that ignites and singes {inactive}!",
		str_special_attack_coup = "{active} empties its fluid bladders in a final burst of liquid! {inactive} is completely engulfed in the conflagration!",
		str_create = "You press a button on the special attack console labelled 'F'. Through the observation port, you see fluid bladders forming deep under the still-forming proto-Slimeoid's translucent skin.",
		str_special = "It can fire a stream of pyrophoric fluid at its foes.",
		str_observe = "A bit of fluid drips from {slimeoid_name} onto the floor and ignites, but you manage to smother the small flame quickly before it spreads."
	),
	EwSpecial( # special 7
		id_special = "webs",
		alias = [
			"webbing",
			"web",
			"g"
		],
		str_special_attack = "{active} fires a stream of sticky webbing onto {inactive}!",
		str_special_attack_weak = "{active} is running out of webbing! It shoots as much as it can onto {inactive}!",
		str_special_attack_coup = "{active} gathers itself up before spurting a blast of webbing that coats {inactive}'s body, completely ensnaring it!",
		str_create = "You press a button on the special attack console labelled 'G'. Through the observation port, you see large glands forming near the surface of the still-forming proto-Slimeoid's translucent skin.",
		str_special = "It can spin webs and shoot webbing fluid to capture prey.",
		str_observe = "{slimeoid_name} is over in the corner, building itself a web to catch prey in."
	)
]

# A map of id_special to EwBody objects.
special_map = {}

# A list of special names
special_names = []

# Populate special map, including all aliases.
for special in special_list:
	special_map[special.id_special] = special
	special_names.append(special.id_special)

	for alias in special.alias:
		special_map[alias] = special

# All brain attributes in the game.
brain_list = [
	EwBrain( # brain 1
		id_brain = "a",
		alias = [
			"typea",
			"type a"
		],
		str_create = "You press a button on the brain console labelled 'A'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid begins to move, thrashing about as if in frustration.",
		str_brain = "It is extremely irritable.",
		str_observe = "{slimeoid_name} is snarling. You're not sure if it's angry at you, or at the world in general.",
		str_pet = "{slimeoid_name} hisses at you.",
		str_walk = "You wrestle {slimeoid_name} down and force a leash onto it, as it angrily snarls and hisses at you in protest.",
		str_kill = "{slimeoid_name} howls with savage delight at the bloodshed!!",
		str_death = "{slimeoid_name} howls in fury at its master's death! It tears away in a blind rage!",
		str_victory = "{slimeoid_name} roars in triumph!!",
		str_battlecry = "{slimeoid_name} roars with bloodlust!! ",
		str_battlecry_weak = "{slimeoid_name} is too breathless to roar, but is still filled with bloodlust!! ",
		str_movecry = "{slimeoid_name} snarls at its prey! " ,
		str_movecry_weak = "{slimeoid_name}  hisses with frustrated rage! ",
		str_revive = "{slimeoid_name} howls at your return, annoyed to have been kept waiting.",
		str_spawn = "{slimeoid_name} shakes itself off to get rid of some excess gestation fluid, then starts to hiss at you. Seems like a real firecracker, this one.",
		str_dissolve = "{slimeoid_name} hisses and spits with fury as you hold it over the SlimeCorp Dissolution Vats. Come on, get in there...\n{slimeoid_name} claws at you, clutching at the edge of the vat, screeching with rage even as you hold its head under the surface and wait for the chemical soup to do its work. At last, it stops fighting.\n\n{slimeoid_name} is no more."
	),
	EwBrain( # brain 2
		id_brain = "b",
		alias = [
			"typeb",
			"type b"
		],
		str_create = "You press a button on the brain console labelled 'B'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid begins to move about its gestation tank, exploring its surroundings.",
		str_brain = "It is enthusiastic about almost everything.",
		str_observe = "{slimeoid_name} notices you looking at it and seems delighted!",
		str_pet = "{slimeoid_name} purrs happily.",
		str_walk = "{slimeoid_name} is so excited for its walk, it can barely hold still enough to let you put the leash on it!",
		str_kill = "{slimeoid_name} gives a bestial woop of excitement for your victory!",
		str_death = "{slimeoid_name} gives a wail of grief at its master's death, streaking away from the scene.",
		str_victory = "{slimeoid_name} woops with delight at its victory!",
		str_battlecry = "{slimeoid_name} lets out a loud war woop! " ,
		str_battlecry_weak = "{slimeoid_name} is determined not to lose! ",
		str_movecry = "{slimeoid_name} is thrilled by the battle! " ,
		str_movecry_weak = "{slimeoid_name} seems a little less thrilled now... ",
		str_revive = "{slimeoid_name} is waiting patiently downtown when you return from your time as a corpse. It knew you'd be back!",
		str_spawn = "{slimeoid_name} gets up off the ground slowly at first, but then it notices you and leaps into your arms. It sure seems glad to see you!",
		str_dissolve = "You order {slimeoid_name} into the Dissolution Vats. It's initially confused, but realization of what you're asking slowly crawks across its features.\nIt doesn't want to go, but after enough stern commanding, it finally pitches itself into the toxic sludge, seemingly too heartbroken to fear death.\n\n{slimeoid_name} is no more."
	),
	EwBrain( # brain 3
		id_brain = "c",
		alias = [
			"typec",
			"type c"
		],
		str_create = "You press a button on the brain console labelled 'C'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid draws its congealing body together, as if trying to gather its strength.",
		str_brain = "It is quiet and withdrawn.",
		str_observe = "{slimeoid_name} seems to be resting, possibly deep in thought.",
		str_pet = "{slimeoid_name} doesn't react.",
		str_walk = "{slimeoid_name} holds still as you place the leash on it. It regards the leash, seemingly pontificating.",
		str_kill = "{slimeoid_name} regards the corpse of your former adversary with an unknowable expression.",
		str_death = "{slimeoid_name} stares at the killer, memorizing their face before fleeing the scene.",
		str_victory = "{slimeoid_name} silently turns away from its defeated opponent.",
		str_battlecry = "{slimeoid_name} carefully regards its opponent. ",
		str_battlecry_weak = "{slimeoid_name} tries to steady itself. ",
		str_movecry = "{slimeoid_name} seems to be getting impatient. " ,
		str_movecry_weak = "{slimeoid_name} is losing its composure just a little! ",
		str_revive = "{slimeoid_name} is downtown when you return from the sewers. You find it staring silently up at ENDLESS WAR.",
		str_spawn = "{slimeoid_name} regards you silently from the floor. You can't tell if it likes you or not, but it starts to follow you regardless.",
		str_dissolve = "You pick up {slimeoid_name} and hurl it into the SlimeCorp Dissolution Vats before it starts to suspect anything. It slowly sinks into the chemical soup, kind of like Arnold at the end of Terminator 2, only instead of giving you a thumbs-up, it stares at you with an unreadable expression. Betrayal? Confusion? Hatred? Yeah, probably.\n\n{slimeoid_name} is no more."
	),
	EwBrain( # brain 4
		id_brain = "d",
		alias = [
			"typed",
			"type d"
		],
		str_create = "You press a button on the brain console labelled 'D'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid lazily turns over in its gestation vat, floating and doing little else.",
		str_brain = "It is usually staring off into space.",
		str_observe = "{slimeoid_name} stares off into the distance. Who knows if it's actually looking at anything in particular.",
		str_pet = "{slimeoid_name} is startled out of a stupor by your touch.",
		str_walk = "{slimeoid_name} hardly seems to notice you fastening it with a leash.",
		str_kill = "{slimeoid_name} wasn't paying attention and missed the action.",
		str_death = "{slimeoid_name} is startled to realize its master has died. It blinks in confusion before fleeing.",
		str_victory = "{slimeoid_name} keeps attacking for a moment before realizing it's already won.",
		str_battlecry = "{slimeoid_name} is weighing its options! ",
		str_battlecry_weak = "{slimeoid_name} is desperately trying to come up with a plan! ",
		str_movecry = "{slimeoid_name} Isn't really feeling this. " ,
		str_movecry_weak = "{slimeoid_name} tries to buy itself some time to think! ",
		str_revive = "{slimeoid_name} is exactly where you left it when you died.",
		str_spawn = "{slimeoid_name} flops over on the floor and stares up at you. Its gaze wanders around the room for a while before it finally picks itself up to follow you.",
		str_dissolve = "You lead {slimeoid_name} up to the edge of the Dissolution Vats and give a quick 'Hey, look, a distraction!'. {slimeoid_name} is immediately distracted and you shove it over the edge. Landing in the vat with a sickening *gloop* sound, it sinks quickly under the fluid surface, flailing madly in confusion and desperation.\n\n{slimeoid_name} is no more."
	),
	EwBrain( # brain 5
		id_brain = "e",
		alias = [
			"typee",
			"type e"
		],
		str_create = "You press a button on the brain console labelled 'E'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid starts to sporadically twitch and shiver.",
		str_brain = "It is extremely skittish and jumpy.",
		str_observe = "{slimeoid_name} is glancing around furtively, seemingly scanning for threats.",
		str_pet = "{slimeoid_name} flinches nervously at your touch.",
		str_walk = "{slimeoid_name} shivers in place as you're fastening the leash, then starts to pull and tug at it, seemingly perturbed.",
		str_kill = "{slimeoid_name} peers out from behind its master, hoping the violence is over.",
		str_death = "{slimeoid_name} is overcome with terror, skittering away from the killer in a mad panic!",
		str_victory = "{slimeoid_name} is deeply relieved that the battle is over.",
		str_battlecry = "{slimeoid_name} chitters fearfully! ",
		str_battlecry_weak = "{slimeoid_name} squeals in abject terror! ",
		str_movecry = "{slimeoid_name} makes a break for it! " ,
		str_movecry_weak = "{slimeoid_name} is in a full-blown panic! ",
		str_revive = "{slimeoid_name} peeks out from behind some trash cans before rejoining you. It seems relieved to have you back.",
		str_spawn = "{slimeoid_name}'s eyes dart frantically around the room. Seeing you, it darts behind you, as if for cover from an unknown threat.",
		str_dissolve = "{slimeoid_name} is looking around the lab nervously, obviously unnerved by the Slimeoid technology. Its preoccupation makes it all too easy to lead it to the Dissolution Vats and kick its legs out from under it, knocking it in. As it falls and hits the solvent chemicals, it wails and screeches in shock and terror, but the noise eventually quiets as it dissolves into a soft lump, then disintegrates altogether.\n\n{slimeoid_name} is no more."
	),
	EwBrain( # brain 6
		id_brain = "f",
		alias = [
			"typef",
			"type f"
		],
		str_create = "You press a button on the brain console labelled 'F'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid darts to the opposite side of the gestation vat. You're not sure, but you feel like it's watching you.",
		str_brain = "It acts secretive, as though it's up to something.",
		str_observe = "{slimeoid_name} is moving around, apparently searching for... something.",
		str_pet = "{slimeoid_name} seems nonplussed, but doesn't object.",
		str_walk = "{slimeoid_name} exasperatedly lets you fit it with a leash for a walk.",
		str_kill = "{slimeoid_name} rifles through your victim's pockets for food.",
		str_death = "{slimeoid_name} rifles through its dead master's pockets for whatever it can find before slinking away.",
		str_victory = "{slimeoid_name} shakes itself off after the battle.",
		str_battlecry = "{slimeoid_name} makes its move! ",
		str_battlecry_weak = "{slimeoid_name}, backed into a corner, tries to counterattack! ",
		str_movecry = "{slimeoid_name} decides on a tactical repositioning. " ,
		str_movecry_weak = "{slimeoid_name} thinks it'd better try something else, and fast! ",
		str_revive = "{slimeoid_name} starts following you around again not long after you have returned from the dead.",
		str_spawn = "{slimeoid_name} picks itself up off the floor and regards you coolly. It seems as if it's gauging your usefulness.",
		str_dissolve = "{slimeoid_name} eyes you suspiciously as you approach the Dissolution Vats. It's on to you. Before it has a chance to bolt, you grab it, hoist it up over your head, and hurl it into the chemical soup. {slimeoid_name} screeches in protest, sputtering and hissing as it thrashes around in the vat, but the chemicals work quickly and it soon dissolves into nothing.\n\n{slimeoid_name} is no more."
	),
	EwBrain( # brain 7
		id_brain = "g",
		alias = [
			"typeg",
			"type g"
		],
		str_create = "You press a button on the brain console labelled 'G'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid begins to flit around the gestation vat, seemingly unsure where to go.",
		str_brain = "It seems to have no idea what it's doing.",
		str_observe = "{slimeoid_name} seems unsure of whether it wants to wander around or just stay put.",
		str_pet = "{slimeoid_name} seems confused about how to react.",
		str_walk = "{slimeoid_name} lets you put its leash on it, but immediately starts to trip over it and get tangled in it.",
		str_kill = "{slimeoid_name} seems unsure of whether to celebrate the victory or to mourn the decline of your civilization into rampant youth violence.",
		str_death = "{slimeoid_name} starts to approach its master's body, then changes its mind and starts to run away. It trips over itself and falls on its way out.",
		str_victory = "{slimeoid_name} looks around, apparently shocked that it somehow won.",
		str_battlecry = "{slimeoid_name} decides to actually do something for once! ",
		str_battlecry_weak = "{slimeoid_name} decides to actually do something for once, now that it's probably too late.",
		str_movecry = "{slimeoid_name} is moving around aimlessly! " ,
		str_movecry_weak = "{slimeoid_name} is limping around aimlessly! ",
		str_revive = "{slimeoid_name} wanders by, seemingly by accident, but thinks it probably ought to start following you again.",
		str_spawn = "{slimeoid_name} starts to pick itself up off the floor, then changes its mind and lies back down. Then it gets up again. Lies down again. Up. Down. Up. Ok, this time it stays up.",
		str_dissolve = "{slimeoid_name} is perplexed by the laboratory machinery. Taking advantage of its confusion, you point it towards the Dissolution Vats, and it gormlessly meanders up the ramp and over the edge. You hear a gloopy SPLOOSH sound, then nothing. You approach the vats and peer over the edge, but see no trace of your former companion.\n\n{slimeoid_name} is no more."
	)
]

# A map of id_brain to EwBrain objects.
brain_map = {}

# A list of brain names
brain_names = []

# Populate brain map, including all aliases.
for brain in brain_list:
	brain_map[brain.id_brain] = brain
	brain_names.append(brain.id_brain)

	for alias in brain.alias:
		brain_map[alias] = brain

hue_analogous = -1
hue_neutral = 0
hue_atk_complementary = 1
hue_special_complementary = 2
hue_full_complementary = 3

# All color attributes in the game.
hue_list = [
	EwHue(
		id_hue = "white",
		alias = [
			"whitedye",
			"poketuber"
		],
		str_saturate = "It begins to glow a ghostly white!",
		str_name = "White",
		str_desc = "Its pale white body and slight luminescence give it a supernatural vibe."
	),
	EwHue(
		id_hue = "yellow",
		alias = [
			"yellowdye",
			"pulpgourds"
		],
		str_saturate = "It begins to shine a bright yellow!",
		str_name = "Yellow",
		str_desc = "Its bright yellow hue is delightfully radiant.",
		effectiveness = {
			"orange": hue_analogous,
			"lime": hue_analogous,
			"purple": hue_atk_complementary,
			"cobalt": hue_special_complementary,
			"rainbow": hue_full_complementary
		}
	),
	EwHue(
		id_hue = "orange",
		alias = [
			"orangedye",
			"sourpotatoes"
		],
		str_saturate = "It turns a warm orange!",
		str_name= "Orange",
		str_desc = "Its warm orange hue makes you want to cuddle up beside it with a nice book.",
		effectiveness = {
			"red": hue_analogous,
			"yellow": hue_analogous,
			"blue": hue_atk_complementary,
			"cyan": hue_special_complementary,
			"rainbow": hue_full_complementary
		}
	),
	EwHue(
		id_hue = "red",
		alias = [
			"blood"
			"cabbage"
		],
		str_saturate = "It darkens a deep shade of crimson red!",
		str_name = "Red",
		str_desc = "Its deep burgundy hue reminds you of a rare steak’s leaked myoglobin.",
		effectiveness = {
			"pink": hue_analogous,
			"orange": hue_analogous,
			"cobalt": hue_atk_complementary,
			"teal": hue_special_complementary,
			"rainbow": hue_full_complementary
		}
	),
	EwHue(
		id_hue = "magenta",
		alias = [
			"magentadye",
			"joybeans"
		],
		str_saturate = "It turns a vivid magenta!",
		str_name = "Magenta",
		str_desc = "It’s vivid magenta that fills you with energy and excitement every time you see it.",
		effectiveness = {
			"pink": hue_analogous,
			"purple": hue_analogous,
			"teal": hue_atk_complementary,
			"lime": hue_special_complementary,
			"rainbow": hue_full_complementary
		}
	),
	EwHue(
		id_hue = "purple",
		alias = [
			"purpledye",
			"purplekilliflower",
			"killer"
		],
		str_saturate = "It turns a dark purple!",
		str_name = "Purple",
		str_desc = "Its dark purple hue gives it a brooding, edgy appearance. It will huff and groan when given orders, like a teenage rebelling against his mom in the most flaccid way possible.",
		effectiveness = {
			"blue": hue_analogous,
			"magenta": hue_analogous,
			"green": hue_atk_complementary,
			"yellow": hue_special_complementary,
			"rainbow": hue_full_complementary
		}
	),
	EwHue(
		id_hue = "blue",
		alias = [
			"bluedye",
			"razornuts"
		],
		str_saturate = "It turns a deep blue!",
		str_name = "Blue",
		str_desc = "Its deep blue hue reminds you of those “ocean” things you’ve heard so much of in the movies and video games that have washed ashore the coast of the Slime Sea.",
		effectiveness = {
			"cobalt": hue_analogous,
			"purple": hue_analogous,
			"lime": hue_atk_complementary,
			"orange": hue_special_complementary,
			"rainbow": hue_full_complementary
		}
	),
	EwHue(
		id_hue = "green",
		alias = [
			"greendye",
			"pawpaw",
			"juvie"
		],
		str_saturate = "It turns a shade of green that barely distinguishes itself from a Slimeoid’s standard hue.",
		str_name = "Green",
		str_desc = "Its unimpressive green hue does nothing to separate itself from the swathes of the undyed Slimeoids of the working class.",
		effectiveness = {
			"lime": hue_analogous,
			"teal": hue_analogous,
			"pink": hue_atk_complementary,
			"purple": hue_special_complementary,
			"rainbow": hue_full_complementary
		}

	),
	EwHue(
		id_hue = "teal",
		alias = [
			"tealdye",
			"sludgeberries"
		],
		str_saturate = "It looks so purdy now!",
		str_name = "Teal",
		str_desc = "Its caliginous teal hue gives you a sudden lust for prosecuting criminals in the legal system, before coming to your senses and realizing there is no legal system here.",
		effectiveness = {
			"green": hue_analogous,
			"cyan": hue_analogous,
			"red": hue_atk_complementary,
			"magenta": hue_special_complementary,
			"rainbow": hue_full_complementary
		}

	),
	EwHue(
		id_hue = "rainbow",
		alias = [
			"rainbowdye",
			"suganmanuts"
		],
		str_saturate = "It turns a fantastic shade of... well, everything!!",
		str_name = "***Rainbow***",
		str_desc = "Its ***Rainbow*** hue dazzles and amazes you. It comprises the whole color spectrum in an crude, Photoshop-tier gradient. It’s so obnoxious… and yet, decadent!"
	),
	EwHue(
		id_hue = "pink",
		alias = [
			"pinkdye",
			"pinkrowddishes"
		],
		str_saturate = "It turns a vibrant shade of  pink!",
		str_name = "Pink",
		str_desc = "Its vibrant pink hue imbues the Slimeoid with an uncontrollable lust for destruction. You will often see it flailing about happily, before knocking down a mailbox or kicking some adult in the shin.",
		effectiveness = {
			"magenta": hue_analogous,
			"red": hue_analogous,
			"cyan": hue_atk_complementary,
			"green": hue_special_complementary,
			"rainbow": hue_full_complementary
		}

	),
	EwHue(
		id_hue = "grey",
		alias = [
			"greydye",
			"dankwheat"
		],
		str_saturate = "It turns a dull, somber grey.",
		str_name = "Grey",
		str_desc = "Its dull grey hue depresses you, lulling you into inaction and complacency. "
	),
	EwHue(
		id_hue = "cobalt",
		alias = [
			"cobaltdye",
			"brightshade"
		],
		str_saturate = "It turns a shimmering cobalt!",
		str_name = "Cobalt",
		str_desc = "Its shimmering cobalt hue can reflect images if properly polished.",
		effectiveness = {
			"cyan": hue_analogous,
			"blue": hue_analogous,
			"yellow": hue_atk_complementary,
			"red": hue_special_complementary,
			"rainbow": hue_full_complementary
		}

	),
	EwHue(
		id_hue = "black",
		alias = [
			"blackdye",
			"blacklimes"
		],
		str_saturate = "It turns pitch black!",
		str_name = "Black",
		str_desc = "Its pitch black, nearly vantablack hue absorbs all the light around it, making this Slimeoid appear as though a hole was ripped right out of reality."
	),
	EwHue(
		id_hue = "lime",
		alias = [
			"limedye",
			"phosphorpoppies"
		],
		str_saturate = "It turns a heavily saturated lime!",
		str_name = "Lime",
		str_desc = "Its heavily saturated lime hue assaults your eyes in a way not unlike the Slime Sea. That is to say, painfully.",
		effectiveness = {
			"yellow": hue_analogous,
			"green": hue_analogous,
			"magenta": hue_atk_complementary,
			"blue": hue_special_complementary,
			"rainbow": hue_full_complementary
		}

	),
	EwHue(
		id_hue = "cyan",
		alias = [
			"cyandye",
			"direapples"
		],
		str_saturate = "It turned a light cyan!",
		str_name = "Cyan",
		str_desc = "Its light cyan hue imbues it with a slightly anxious demeanor, it is sure to avoid sewer manholes when walking down the street.",
		effectiveness = {
			"teal": hue_analogous,
			"cobalt": hue_analogous,
			"orange": hue_atk_complementary,
			"pink": hue_special_complementary,
			"rainbow": hue_full_complementary
		}

	),
]

# A map of id_hue to EwHue objects.
hue_map = {}

# A list of hue names
hue_names = []

# Populate hue map, including all aliases.
for hue in hue_list:
	hue_map[hue.id_hue] = hue
	hue_names.append(hue.id_hue)

	for alias in hue.alias:
		hue_map[alias] = hue

# Things a slimeoid might throw
thrownobjects_list = [
	"sewer cap",
	"boulder",
	"chunk of broken asphalt",
	"broken fire hydrant",
	"SlimeCorp-Brand Slime Containment Vessel (tm)",
	"piece of sheet metal",
	"burning tire",
	"hapless bystander",
	"completely normal small mammal",
	"heap of broken glass",
	"stereotypical nautical anchor",
	"piece of an iron girder",
	"pile of lumber",
	"pile of bricks",
	"unrecognizably decayed animal carcass",
	"very fortuitously abandoned javelin",
	"large rock",
	"small motor vehicle",
	"chunk of broken concrete",
	"piece of rusted scrap metal",
	"box overflowing with KFC branded bbq sauce",
	"Nokia 3310"
]

quadrant_flushed = "flushed"
quadrant_pale = "pale"
quadrant_caliginous = "caliginous"
quadrant_ashen = "ashen"

quadrant_ids = [
	quadrant_flushed,
	quadrant_pale,
	quadrant_caliginous,
	quadrant_ashen
	]

quadrants_map = {}

quadrants = [
	EwQuadrantFlavor(
		id_quadrant = quadrant_flushed,

		aliases = ["heart", "hearts", "matesprit", "matespritship"],

		resp_add_onesided = "You have developed flushed feelings for {}.",

		resp_add_relationship = "You have entered into a matespritship with {}.",

		resp_view_onesided = "{} has a one-sided red crush on {}.",

		resp_view_onesided_self = "You have a one-sided red crush on {}.",

		resp_view_relationship = "{} is in a matespritship with {}. " + emote_hearts,

		resp_view_relationship_self = "You are in a matespritship with {}. " + emote_hearts
		),

	EwQuadrantFlavor(
		id_quadrant = quadrant_pale,

		aliases = ["diamond", "diamonds", "moirail", "moiraillegiance"],

		resp_add_onesided = "You have developed pale feelings for {}.",

		resp_add_relationship = "You have entered into a moiraillegiance with {}.",

		resp_view_onesided = "{} has a one-sided pale crush on {}.",

		resp_view_onesided_self = "You have a one-sided pale crush on {}.",

		resp_view_relationship = "{} is in a moiraillegiance with {}. " + emote_diamonds,

		resp_view_relationship_self = "You are in a moiraillegiance with {}. " + emote_diamonds
		),

	EwQuadrantFlavor(
		id_quadrant = quadrant_caliginous,

		aliases = ["spade", "spades", "kismesis", "kismesissitude"],

		resp_add_onesided = "You have developed caliginous feelings for {}.",

		resp_add_relationship = "You have entered into a kismesissitude with {}.",

		resp_view_onesided = "{} has a one-sided black crush on {}.",

		resp_view_onesided_self = "You have a one-sided black crush on {}.",

		resp_view_relationship = "{} is in a kismesissitude with {}. " + emote_spades,

		resp_view_relationship_self = "You are in a kismesissitude with {}. " + emote_spades
		),

	EwQuadrantFlavor(
		id_quadrant = quadrant_ashen,

		aliases = ["club", "clubs", "auspistice", "auspisticism"],

		resp_add_onesided = "You have developed ashen feelings for {}.",

		resp_add_relationship = "You have entered into an auspisticism with {}.",

		resp_view_onesided = "{} has a one-sided ashen crush on {}.",

		resp_view_onesided_self = "You have a one-sided ashen crush on {}.",

		resp_view_relationship = "{} is in an auspisticism with {}. " + emote_clubs,

		resp_view_relationship_self = "You are in an auspisticism with {}. " + emote_clubs
		)

	]

for quadrant in quadrants:
	quadrants_map[quadrant.id_quadrant] = quadrant
	for alias in quadrant.aliases:
		quadrants_map[alias] = quadrant

quadrants_comments_onesided = [
		"Adorable~",
		"GAY!",
		"Disgusting.",
		"How embarrassing!",
		"Epic.",
		"Have you no shame...?",
		"As if you'd ever have a shot with them."
	]

quadrants_comments_relationship = [
		"Adorable~",
		"GAY!",
		"Disgusting.",
		"How embarrassing!",
		"Epic.",
		"Have you no shame...?",
		"Lke that's gonna last."
	]

# list of stock ids
stocks = [
	stock_kfc,
	stock_pizzahut,
	stock_tacobell,
]

# Stock names
stock_names = {
	stock_kfc : "Kentucky Fried Chicken",
	stock_pizzahut : "Pizza Hut",
	stock_tacobell : "Taco Bell",
}

#  Stock emotes
stock_emotes = {
    stock_kfc : emote_kfc,
    stock_pizzahut : emote_pizzahut,
    stock_tacobell : emote_tacobell
}

# List of items you can obtain via milling.
mill_results = []

# gather all items that can be the result of milling.
for m in item_list:
	if m.ingredients != None:
		mill_results.append(m)
	else:
		pass

for m in food_list:
	if m.ingredients != None:
		mill_results.append(m)
	else:
		pass

for m in cosmetic_items_list:
	if m.ingredients != None:
		mill_results.append(m)
	else:
		pass



# Dict of all help responses linked to their associated topics
help_responses = {
	"mining":"Mining is the primary way to gain slime in **ENDLESS WAR**. When you type one **'!mine'** command, you raise your hunger by about 0.5%. The more slime you mine for, the higher your level gets, and the higher your level gets, the more slime you gain with every '!mine' command, resulting in exponential gains. Mining will sometimes endow you with hardened crystals of slime called **slime poudrins**, which can be used for farming and annointing your weapon. **JUVENILES** can mine any time they like, but **ROWDYS** and **KILLERS** are restricted to mining during the day (8AM-6PM) and night (8PM-6AM), respectively.",
	"food":"Food lowers your hunger by a set amount, and can be ordered from various **restaurants** within the city. Generally speaking, the more expensive food is, the more hunger it sates. You can **'!order'** food and eat it at the same time, or add **'togo'** (or just 't') at the end of your order to place it in your inventory (example: !order pizza togo). Ordering it togo **doubles** the price, however, and you can only carry a certain amount of food depending on your level. Three popular restauraunts close by various gang bases include **THE SPEAKEASY** (juveniles), **THE SMOKER'S COUGH** (rowdys), and **RED MOBSTER SEAFOOD** (killers), though there are other places to order food as well, such as the **Food Court**.",
	"capturing":"Capturing districts is the primary objective of **ENDLESS WAR**. If you reach **level 10** (done by gaining at least 10,000 slime), you are able to capture districts and generate slime for your team's **Kingpin**. The rate at which you capture a district is determined by various factors. If more **people** are capturing a district, that district will take **less** time to capture. The **property class** (which can range from S at the highest to C at the lowest) of that district will also increase capture time, with S class districts taking more time to capture than C class districts. Districts will take **less** time to capture if they are nearby **friendly** districts, and **more** time to capture if they are nearby **enemy** districts. Districts will have their capture progress **decay** over time, but if a captured district is **fully surrounded** by friendly districts (example: Assault Flats Beach is surrounded by Vagrant's Corner and New New Yonkers), then it will **not** decay. Inversely, districts will decay **faster** if they are next to **enemy** districts. **DECAPTURING** (lowering an enemy's capture progress on districts they control) and **RENEWING** (increasing capture progress on districts your team currently controls) can also be done, but only if that district is **not** fully surrounded. **JUVIE'S ROW**, **ROWDY ROUGHHOUSE**, and **COP KILLTOWN** are gang bases, and thus cannot be captured, nor do they decay. To check the capture progress of a district, use **'!progress'**. To view the status of the map itself and check what property class each district has, use **'!map'**.",
	"dojo":"The Dojo is where you acquire weapons to fight and kill other players with. To purchase a weapon, use **'!arm [weapon]'**. There are many weapons you can choose from, and they all perform differently from one another. Once you've purchased a weapon, you can use **'!equip [weapon]'** to equip it, provided that you're enlisted in a gang beforehand. You can also name your weapon by spending a poudrin on it with **'!annoint [name]'**. Furthermore, annointing will increase your mastery over that weapon, but it's much more efficient to do so through **sparring**. Sparring can be done between two players using **'!spar [player]'**. Sparring, provided that both players spar with the same weapon type and are not at full hunger, will increase both of your mastery **LEVEL**, which is a hidden value, by one. The publicly displayed value, mastery **RANK** (which is just your mastery level minus 4), is what's actually important. Once you reach mastery rank 1 (Again, this would be level 5), the damage you do with that weapon type is increased, and when you next revive, you will now **permanently** be at level 3 for that weapon type. Essentially, this means you would only have to '!spar' or '!annoint twice to get back up to rank 1. Once you reach **rank 6**, you can no longer spar or annoint your weapon rank any higher, and must instead kill other players (that are higher in slime level than you) to do so. You can only spar up to someone else's mastery rank, minus 1 (example: Sparring with a rank 15 master of the katana would, at most, allow you to get to rank 14). Sparring has a five minute cooldown and raises your hunger by about 15%, so make sure to bring some food with you beforehand. Once you reach rank 8, you may also **'!marry'** your weapon, resulting in a matrimonial ceremony that increases your rank by two.",
	"bleeding":"When you get hit by someone using a '!kill' command, certain things happen to your slime. Let's say you take 20,000 points of damage. **50%** of that slime, in this case 10,000, immediately becomes scavengeable. However, the other 50%, provided that you didn't die instantly, will undergo the **bleeding** process. 25% of that slime, in this case 5,000, is immediately added to a 'bleed pool', causing it to slowly trickle out of your body and onto the ground for it to be scavenged. The remaining 25% of that slime will **slowly** be added to the 'bleed pool', where it will then bleed, just as previously stated. Upon dying, your 'bleed pool' is immediately dumped onto the ground, ready to be scavenged. Think of it like the 'rolling HP' system from the game *EarthBound*. When you get hit, you don't take all your damage upfront, it instead slowly trickles down.",
	"scavenging":"Scavenging allows you to collect slime that is **stored** in districts. When someone in a district gets hurt or dies, their slime **splatters** onto the ground, allowing you to use **'!scavenge'** and collect it, similarly to mining. Scavenging, however, raises your hunger by about 0.8% per use of the '!scavenge' command, so it's often more efficient to do a '!scavenge' command **every 30 seconds** or so, resulting in the highest potential collection of slime at the lowest cost of hunger. You can still spam it, just as you would with '!mine', but you'll gain less and less slime if you don't wait for the 30 second cool-down. To check how much slime you can scavenge, use **'!look'** while in a district channel.",
	"farming":"**Farming** is an alternative way to gain slime, accessible only by **JUVENILES**. Currently, it is done by planting poudrins on a farm with the **'!sow'** command. You can only '!sow' one poudrin per farm. After about 12 in-game hours (3 hours in real life), you can use **'!reap'** to gain 160,000 slime, with a 1/3 chance to gain a poudrin. If you do gain a poudrin, you also have 1/3 chance to gain a second poudrin. If your poudrin plant is left alone for too long (around 2 in-game days), it will **die out**. In addition to slime, farming also provides you with various **crops**. Current farms within the city include **JUVIE'S ROW FARMS** (within Juvie's Row), **OOZE GARDENS FARMS** (close by Rowdy Roughhouse), and **ARSONBROOK FARMS** (close by Cop Killtown).",
	"slimeoids":"**SLIMEOIDS** are sentient masses of slime that you can keep as **pets**. To learn how to make one for yourself, visit **The Slimeoid Laboratory** in Brawlden and check the enclosed **'!instructions'**. After you've made one, you can also battle it out with other slimeoids in **The Arena**, located in Vandal Park.",
	"transportation":"There are various methods of transportation within the city, the quickest and most efficient of them being **The Subway System**. Trains can be boarded with **'!board'** or **'!embark'**, and to board specific trains, you can add your destination to the command. For example, to board the red line to Cratersville, you would use '!board redtocv'. **'!disembark'** can be used to exit a train. **The Ferry** and **The Blimp** can also be used as methods of transportation, though they take longer to arrive at their destinations than the trains do.",
	"scouting":"Scouting is a way for you to check how many **players** might be in a district that's close by. You can do just **'!scout'** to check the district you're already in, or **'!scout [district]'** to scout out that specific district. For example, if you were in Vagrant's Corner, you could use '!scout gld' to see how many players might be in Green Light District. Scouting will show both **friendly and enemy** gang members, as well as juveniles and even ghosts. Scouting will list all players above your own level, as well as players below your level, but at a certain **cutoff point**. If you can't scout someone, it's safe to assume they have around **1/10th** the amount of slime that you do, or less.",
	"offline":"Given that ENDLESS WAR is a **Discord** game, there are a few peculiarities surrounding it and how it interacts with Discord itself. When you set your status to **'Offline'**, you can still move between districts if you typed a '!goto' command beforehand. You won't show up on the sidebar in that district's channel, but people can still scout for you, and see the '[player] has entered [district]' message when you do enter the district they're in. Furthermore, you **can't** use commands while offline, and can only use commands **10 seconds** after coming online again. Often times, you may find yourself using '!scout' or '!look' on a district, only to find that **no one** is there besides yourself. This is likely because they're in that district, just with their status set to offline."
}

# lists of all the discord server objects served by bot, identified by the server id
server_list = {}

"""
	store a server in a dictionary
"""
def update_server_list(server):
	server_list[server.id] = server


client_ref = None

def get_client():
	global client_ref
	return client_ref;

"""
	save the discord client of this bot
"""
def set_client(cl):
	global client_ref
	client_ref = cl

	return client_ref
