from . import cmds
from .utils import *

cmd_map = {

    # exchanging souls
    ewcfg.cmd_betsoul: cmds.betsoul,
    ewcfg.cmd_buysoul: cmds.buysoul,

    # Play slime pachinko!
    ewcfg.cmd_slimepachinko: cmds.pachinko,
    ewcfg.cmd_slimepachinko_alt1: cmds.pachinko,

    # Toss the dice at slime craps!
    ewcfg.cmd_slimecraps: cmds.craps,
    ewcfg.cmd_slimecraps_alt1: cmds.craps,

    # Pull the lever on a slot machine!
    ewcfg.cmd_slimeslots: cmds.slots,
    ewcfg.cmd_slimeslots_alt1: cmds.slots,

    # Play slime roulette!
    ewcfg.cmd_slimeroulette: cmds.roulette,
    ewcfg.cmd_slimeroulette_alt1: cmds.roulette,

    # Play slime baccarat!
    ewcfg.cmd_slimebaccarat: cmds.baccarat,
    ewcfg.cmd_slimebaccarat_alt1: cmds.baccarat,

    # Play slime skat!
    ewcfg.cmd_slimeskat: cmds.skat,
    ewcfg.cmd_slimeskat_alt1: cmds.skat,
    ewcfg.cmd_slimeskat_join: cmds.skat_play,
    ewcfg.cmd_slimeskat_decline: cmds.skat_play,
    ewcfg.cmd_slimeskat_bid: cmds.skat_play,
    ewcfg.cmd_slimeskat_call: cmds.skat_play,
    ewcfg.cmd_slimeskat_pass: cmds.skat_play,
    ewcfg.cmd_slimeskat_play: cmds.skat_play,
    ewcfg.cmd_slimeskat_hearts: cmds.skat_play,
    ewcfg.cmd_slimeskat_slugs: cmds.skat_play,
    ewcfg.cmd_slimeskat_hats: cmds.skat_play,
    ewcfg.cmd_slimeskat_shields: cmds.skat_play,
    ewcfg.cmd_slimeskat_grand: cmds.skat_play,
    ewcfg.cmd_slimeskat_null: cmds.skat_play,
    ewcfg.cmd_slimeskat_take: cmds.skat_play,
    ewcfg.cmd_slimeskat_hand: cmds.skat_play,
    ewcfg.cmd_slimeskat_choose: cmds.skat_play,

    # Russian Roulette
    ewcfg.cmd_russian: cmds.russian_roulette,

    # Dueling
    # This isn't done in the casino. maybe move to wep
    ewcfg.cmd_duel: cmds.duel,

}
