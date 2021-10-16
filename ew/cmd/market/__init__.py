from ew.static import cfg as ewcfg
from . import marketcmds

cmd_map = {

    # Display the progress towards the current Quarterly Goal.
    # ewcfg.cmd_quarterlyreport: cmds.quarterlyreport,

    # Transfer slimecoin between players. Shares a cooldown with investments.
    ewcfg.cmd_transfer: marketcmds.xfer,
    ewcfg.cmd_transfer_alt1: marketcmds.xfer,

    # Redeem slime with SlimeCoin
    # ewcfg.cmd_redeem: cmds.redeem,

    # Donate your slime to SlimeCorp in exchange for SlimeCoin.
    ewcfg.cmd_donate: marketcmds.donate,

    # Invest slimecoin into a stock
    ewcfg.cmd_invest: marketcmds.invest,

    # Withdraw slimecoin from your shares
    ewcfg.cmd_withdraw: marketcmds.withdraw,

    # show the exchange rate of a given stock
    ewcfg.cmd_exchangerate: marketcmds.rate,
    ewcfg.cmd_exchangerate_alt1: marketcmds.rate,
    ewcfg.cmd_exchangerate_alt2: marketcmds.rate,
    ewcfg.cmd_exchangerate_alt3: marketcmds.rate,
    ewcfg.cmd_exchangerate_alt4: marketcmds.rate,

    # check available stocks
    ewcfg.cmd_stocks: marketcmds.stocks,

    # trading
    ewcfg.cmd_trade: marketcmds.trade,
    ewcfg.cmd_offer: marketcmds.offer_item,
    ewcfg.cmd_remove_offer: marketcmds.remove_offer,
    ewcfg.cmd_completetrade: marketcmds.complete_trade,
    ewcfg.cmd_canceltrade: marketcmds.cancel_trade,
    ewcfg.cmd_cockdraw:marketcmds.cockdraw,
    ewcfg.cmd_measurecock:marketcmds.cockdraw


}
