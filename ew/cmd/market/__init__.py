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

    # Show the player's slime coin.
    # Feel like this should be in cmd with !slime and !data
    ewcfg.cmd_slimecoin: cmds.slimecoin,
    ewcfg.cmd_slimecoin_alt1: cmds.slimecoin,
    ewcfg.cmd_slimecoin_alt2: cmds.slimecoin,
    ewcfg.cmd_slimecoin_alt3: cmds.slimecoin,

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

    # show player's current shares in a company
    # Again feel like this could definitely be with !slime in cmd
    ewcfg.cmd_shares: cmds.shares,
    ewcfg.cmd_shares_alt1: cmds.shares,

    # check available stocks
    ewcfg.cmd_stocks: cmds.stocks,

    # trading
    ewcfg.cmd_trade: cmds.trade,
    ewcfg.cmd_offer: cmds.offer_item,
    ewcfg.cmd_remove_offer: cmds.remove_offer,
    ewcfg.cmd_completetrade: cmds.complete_trade,
    ewcfg.cmd_canceltrade: cmds.cancel_trade,

}

apt_dm_cmd_map = {

    # Show the player's slime coin.
    ewcfg.cmd_slimecoin: cmds.slimecoin,
    ewcfg.cmd_slimecoin_alt1: cmds.slimecoin,
    ewcfg.cmd_slimecoin_alt2: cmds.slimecoin,
    ewcfg.cmd_slimecoin_alt3: cmds.slimecoin,

}
