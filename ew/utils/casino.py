def slimecorp_collectfee(winnings):
    slimecorp_fee = int(winnings * 0.2)
    new_winnings = int(winnings * 0.8)

    return slimecorp_fee, new_winnings
