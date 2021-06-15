from . import cmds
from .utils import *
from ew.static import cfg as ewcfg

cmd_map = {

    # Show the current slime score of a player.
    ewcfg.cmd_score: cmds.score,
    ewcfg.cmd_score_alt1: cmds.score,
    ewcfg.cmd_score_alt2: cmds.score,
    ewcfg.cmd_score_alt3: cmds.score,

    # Show a player's combat data.
    ewcfg.cmd_data: cmds.data,

    # Show a player's mutations.
    ewcfg.cmd_mutations: cmds.mutations,
    ewcfg.cmd_mutations_alt_1: cmds.mutations,

    # Check how hungry you are.
    ewcfg.cmd_hunger: cmds.hunger,

    # check what time it is, and the weather
    ewcfg.cmd_time: cmds.weather,
    ewcfg.cmd_clock: cmds.weather,
    ewcfg.cmd_weather: cmds.weather,

    # Rowdys thrash and Killers dab.
    ewcfg.cmd_thrash: cmds.thrash,
    ewcfg.cmd_dab: cmds.dab,

    # Ghosts can BOO
    ewcfg.cmd_boo: cmds.boo,

    # TODO remove after double halloween
    # ewcfg.cmd_spook: cmds.spook,

    # Juvies can dance
    ewcfg.cmd_dance: cmds.dance,
    ewcfg.cmd_dance_alt: cmds.dance,

    # Terezi Gang can flip coins
    ewcfg.cmd_coinflip: cmds.coinflip,

    # Show the total of positive slime in the world.
    ewcfg.cmd_endlesswar: cmds.endlesswar,

    # Slimefest
    ewcfg.cmd_slimefest: cmds.slimefest,

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # up till this point it was    #
    # a good spread of general     #
    # purpose cmds. RIP            #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    # Show the number of swears in the global swear jar.
    # ewcfg.cmd_swear_jar: cmds.swearjar,

    # throw an item off the cliff
    ewcfg.cmd_toss: cmds.toss_off_cliff,

    # throw yourself off the cliff
    ewcfg.cmd_jump: cmds.jump,
    ewcfg.cmd_jump_alt1: cmds.jump,

    # throw someone else off the cliff
    ewcfg.cmd_push: cmds.push,
    ewcfg.cmd_push_alt_1: cmds.push,
    ewcfg.cmd_push_alt_2: cmds.push,

    # drink from the fountain
    ewcfg.cmd_purify: cmds.purify,

    # stow/snag
    ewcfg.cmd_store: cmds.store_item,
    ewcfg.cmd_take: cmds.remove_item,

    # look at the flag
    ewcfg.cmd_checkflag: cmds.check_flag,

    # for russianroulette apparently. I think every package has a copy of these
    ewcfg.cmd_accept: cmds.accept,
    ewcfg.cmd_refuse: cmds.refuse,

    # More confirmation cmds, but for ads
    ewcfg.cmd_confirm: cmds.confirm,
    ewcfg.cmd_cancel: cmds.cancel,

    # TODO - Create a universal accept system
    # implement checks on everything that awaits
    # acceptance to make sure queues dont stack
    # Cause I am fortelling of bugs with all these

    # link to the world map
    ewcfg.cmd_map: cmds.map,
    ewcfg.cmd_transportmap: cmds.transportmap,

    # Check your fashion ratings
    # debatably could go in cosmetic
    # but it fits with hunger/data/slime
    ewcfg.cmd_fashion: cmds.fashion,
    ewcfg.cmd_fashion_alt1: cmds.fashion,

    # admins manipulate/make items. Feels like these should be in
    # the item_package with the prop editor
    ewcfg.cmd_forgemasterpoudrin: cmds.forge_master_poudrin,
    ewcfg.cmd_createitem: cmds.create_item,
    ewcfg.cmd_manualsoulbind: cmds.manual_soulbind,
    ewcfg.cmd_balance_cosmetics: cmds.balance_cosmetics,

    # more debug commands. feel wrong here
    ewcfg.cmd_setslime: cmds.set_slime,
    ewcfg.cmd_checkstats: cmds.check_stats,
    ewcfg.cmd_makebp: cmds.make_bp,
    ewcfg.cmd_ping_me: cmds.ping_me,
    ewcfg.cmd_addstatuseffect: cmds.assign_status_effect,

    # force print the leaderboard
    ewcfg.cmd_post_leaderboard: cmds.post_leaderboard,

    # Ban/pardon from gameplay
    ewcfg.cmd_arrest: cmds.arrest,
    ewcfg.cmd_release: cmds.release,
    ewcfg.cmd_release_alt1: cmds.release,

    ewcfg.cmd_manual_unban: cmds.unban_manual,

    # grant slimecorp executive status
    ewcfg.cmd_promote: cmds.promote,

    # recycle your trash at the slimecorp recycling plant
    ewcfg.cmd_recycle: cmds.recycle,
    ewcfg.cmd_recycle_alt1: cmds.recycle,

    # Show guide pages or available commands
    ewcfg.cmd_help: cmds.help,
    ewcfg.cmd_help_alt3: cmds.help,
    ewcfg.cmd_commands: cmds.commands,
    ewcfg.cmd_commands_alt1: cmds.commands,

    # Misc (this whole map is misc)
    ewcfg.cmd_howl: cmds.cmd_howl,
    ewcfg.cmd_howl_alt1: cmds.cmd_howl,
    ewcfg.cmd_moan: cmds.cmd_moan,
    ewcfg.cmd_harvest: cmds.harvest,
    ewcfg.cmd_salute: cmds.salute,
    ewcfg.cmd_unsalute: cmds.unsalute,
    ewcfg.cmd_hurl: cmds.hurl,
    ewcfg.cmd_news: cmds.patchnotes,
    ewcfg.cmd_patchnotes: cmds.patchnotes,
    ewcfg.cmd_wiki: cmds.wiki,
    ewcfg.cmd_booru: cmds.booru,
    ewcfg.cmd_bandcamp: cmds.bandcamp,
    ewcfg.cmd_tutorial: cmds.tutorial,
    ewcfg.cmd_leaderboard: cmds.leaderboard,
    ewcfg.cmd_leaderboard_alt1: cmds.leaderboard,

    # WHY ARE THE MUTATION COMMANDS EVERYWHERE BUT EW/MUTATIONS
    ewcfg.cmd_piss: cmds.piss,
    ewcfg.cmd_fursuit: cmds.fursuit,

    # LOL
    ewcfg.cmd_lol: cmds.lol,

    # Shuts down the bot with sys.exit()
    # or kills non admins
    ewcfg.cmd_shutdownbot: cmds.shut_down_bot,

    # Checks the status of ewutils.TERMINATE
    ewcfg.cmd_checkbot: cmds.check_bot,

    # for the filth
    ewcfg.cmd_paycheck: cmds.paycheck,
    ewcfg.cmd_payday: cmds.payday,

    # Praying at the base of ENDLESS WAR.
    ewcfg.cmd_pray: cmds.pray,

    # Slimernalia
    # Check your current festivity
    # ewcfg.cmd_festivity: cmds.festivity,
    # Wrap a gift -- ewitem maybe?
    # ewcfg.cmd_wrap: cmds.wrap,
    # Unwrap a gift -- ewitem maybe?
    ewcfg.cmd_unwrap: cmds.unwrap,
    # Yo, Slimernalia
    # ewcfg.cmd_yoslimernalia: cmds.yoslimernalia,

    # Swilldermuk
    # ewcfg.cmd_gambit: cmds.gambit,
    # ewcfg.cmd_credence: cmds.credence, #debug
    # ewcfg.cmd_get_credence: cmds.get_credence, #debug
    # ewcfg.cmd_reset_prank_stats: cmds.reset_prank_stats, #debug
    # ewcfg.cmd_set_gambit: cmds.set_gambit, #debug
    # ewcfg.cmd_pointandlaugh: cmds.point_and_laugh,
    ewcfg.cmd_prank: cmds.prank,

    # Gankers Vs. Shamblers
    # Maybe shoulda had its own file
    # ewcfg.cmd_gvs_printgrid: cmds.gvs_print_grid,
    # ewcfg.cmd_gvs_printgrid_alt1: cmds.gvs_print_grid,
    # ewcfg.cmd_gvs_printlane: cmds.gvs_print_lane,
    # ewcfg.cmd_gvs_incubategaiaslimeoid: cmds.gvs_incubate_gaiaslimeoid,
    # ewcfg.cmd_gvs_fabricatetombstone: cmds.gvs_fabricate_tombstone,
    # ewcfg.cmd_gvs_joinoperation: cmds.gvs_join_operation,
    # ewcfg.cmd_gvs_leaveoperation: cmds.gvs_leave_operation,
    # ewcfg.cmd_gvs_checkoperation: cmds.gvs_check_operations,
    # ewcfg.cmd_gvs_plantgaiaslimeoid: cmds.gvs_plant_gaiaslimeoid,
    ewcfg.cmd_gvs_almanac: cmds.almanac,
    # ewcfg.cmd_gvs_searchforbrainz: cmds.gvs_searchforbrainz,
    # ewcfg.cmd_gvs_grabbrainz: cmds.gvs_grabbrainz,
    # ewcfg.cmd_gvs_dive: cmds.gvs_dive,
    # ewcfg.cmd_gvs_resurface: cmds.gvs_resurface,
    # ewcfg.cmd_gvs_sellgaiaslimeoid: cmds.gvs_sell_gaiaslimeoid,
    # ewcfg.cmd_gvs_sellgaiaslimeoid_alt: cmds.gvs_sell_gaiaslimeoid,
    # ewcfg.cmd_gvs_dig: cmds.dig,
    # ewcfg.cmd_gvs_progress: cmds.gvs_progress,
    # ewcfg.cmd_gvs_gaiaslime: cmds.gvs_gaiaslime,
    # ewcfg.cmd_gvs_gaiaslime_alt1: cmds.gvs_gaiaslime,
    # ewcfg.cmd_gvs_brainz: cmds.gvs_brainz,

    # Check your weapon masteries
    ewcfg.cmd_mastery: cmds.check_mastery,
    ewcfg.cmd_getattire: cmds.get_attire,

    # SlimeCorp security officers can post propaganda
    # ewcfg.cmd_propaganda: ewcmd.propaganda,

}

dm_cmd_map = {

	# !help
	ewcfg.cmd_help: cmds.help,
	ewcfg.cmd_help_alt3: cmds.help,

    # !commands
    ewcfg.cmd_commands_alt1: cmds.commands,
    ewcfg.cmd_commands: cmds.commands,

}

apt_dm_cmd_map = {

    # !howl
    ewcfg.cmd_howl: cmds.cmd_howl,
    ewcfg.cmd_howl_alt1: cmds.cmd_howl,

    # !moan
    ewcfg.cmd_moan: cmds.cmd_moan,

    # Show a player's combat data.
    ewcfg.cmd_data: cmds.data,

    # Check how hungry you are.
    ewcfg.cmd_hunger: cmds.hunger,

    # Show the current slime score of a player.
    ewcfg.cmd_score: cmds.score,
    ewcfg.cmd_score_alt1: cmds.score,
    ewcfg.cmd_score_alt2: cmds.score,
    ewcfg.cmd_score_alt3: cmds.score,

    # !booru
    ewcfg.cmd_booru: cmds.booru,

    # !wiki
    ewcfg.cmd_wiki: cmds.wiki,

    # !unsalute
    ewcfg.cmd_unsalute: cmds.unsalute,

    # !salute
    ewcfg.cmd_salute: cmds.salute,

    # vomit
    ewcfg.cmd_hurl: cmds.hurl,

    # link to the world map
    ewcfg.cmd_map: cmds.map,

    # check what time it is, and the weather
    ewcfg.cmd_time: cmds.weather,
    ewcfg.cmd_clock: cmds.weather,
    ewcfg.cmd_weather: cmds.weather,

    # Check patchnotes
    ewcfg.cmd_news: cmds.patchnotes,
    ewcfg.cmd_patchnotes: cmds.patchnotes,

    # gives +10Gigaslime
    ewcfg.cmd_harvest: cmds.harvest,

    # show what commands are currently available
    ewcfg.cmd_commands_alt1: cmds.commands,
    ewcfg.cmd_commands: cmds.commands,

    # I will cry and piss my pants about this
    # put the mutation commands in ewmutaion
    # I am literally begging
    ewcfg.cmd_piss: cmds.piss,

}