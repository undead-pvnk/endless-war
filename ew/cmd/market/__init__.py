from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Display the progress towards the current Quarterly Goal.
    # ewcfg.cmd_quarterlyreport: cmds.quarterlyreport,

    # Transfer slimecoin between players. Shares a cooldown with investments.
    ewcfg.cmd_transfer: cmds.xfer,
    ewcfg.cmd_transfer_alt1: cmds.xfer,

    # Redeem slime with SlimeCoin
    # ewcfg.cmd_redeem: cmds.redeem,

    # Donate your slime to SlimeCorp in exchange for SlimeCoin.
    ewcfg.cmd_donate: cmds.donate,

    # Invest slimecoin into a stock
    ewcfg.cmd_invest: cmds.invest,

    # Withdraw slimecoin from your shares
    ewcfg.cmd_withdraw: cmds.withdraw,

    # show the exchange rate of a given stock
    ewcfg.cmd_exchangerate: cmds.rate,
    ewcfg.cmd_exchangerate_alt1: cmds.rate,
    ewcfg.cmd_exchangerate_alt2: cmds.rate,
    ewcfg.cmd_exchangerate_alt3: cmds.rate,
    ewcfg.cmd_exchangerate_alt4: cmds.rate,

    # check available stocks
    ewcfg.cmd_stocks: cmds.stocks,

    # trading
    ewcfg.cmd_trade: cmds.trade,
    ewcfg.cmd_offer: cmds.offer_item,
    ewcfg.cmd_remove_offer: cmds.remove_offer,
    ewcfg.cmd_completetrade: cmds.complete_trade,
    ewcfg.cmd_canceltrade: cmds.cancel_trade,

}