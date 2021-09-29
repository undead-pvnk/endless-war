from ew.static import cfg as ewcfg
from . import casinocmds

cmd_map = {

    # exchanging souls
    ewcfg.cmd_betsoul: casinocmds.betsoul,
    ewcfg.cmd_buysoul: casinocmds.buysoul,

    # Play slime pachinko!
    ewcfg.cmd_slimepachinko: casinocmds.pachinko,
    ewcfg.cmd_slimepachinko_alt1: casinocmds.pachinko,

    # Toss the dice at slime craps!
    ewcfg.cmd_slimecraps: casinocmds.craps,
    ewcfg.cmd_slimecraps_alt1: casinocmds.craps,

    # Pull the lever on a slot machine!
    ewcfg.cmd_slimeslots: casinocmds.slots,
    ewcfg.cmd_slimeslots_alt1: casinocmds.slots,

    # Play slime roulette!
    ewcfg.cmd_slimeroulette: casinocmds.roulette,
    ewcfg.cmd_slimeroulette_alt1: casinocmds.roulette,

    # Play slime baccarat!
    ewcfg.cmd_slimebaccarat: casinocmds.baccarat,
    ewcfg.cmd_slimebaccarat_alt1: casinocmds.baccarat,

    # Play slime skat!
    ewcfg.cmd_slimeskat: casinocmds.skat,
    ewcfg.cmd_slimeskat_alt1: casinocmds.skat,
    ewcfg.cmd_slimeskat_join: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_decline: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_bid: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_call: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_pass: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_play: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_hearts: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_slugs: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_hats: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_shields: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_grand: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_null: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_take: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_hand: casinocmds.skat_play,
    ewcfg.cmd_slimeskat_choose: casinocmds.skat_play,

    # Russian Roulette
    ewcfg.cmd_russian: casinocmds.russian_roulette,

}
