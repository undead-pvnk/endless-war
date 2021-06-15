import time
from copy import deepcopy

from .utils import getUserTotalShares
from .utils import updateUserTotalShares
from .utils import get_user_shares_str
from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.market import EwStock
from ew.backend.player import EwPlayer
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict

""" transfer slimecoin between players """
async def xfer(cmd):
    time_now = round(time.time())
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


    if cmd.message.channel.name != ewcfg.channel_stockexchange:
        # Only allowed in the stock exchange.
        response = ewcfg.str_exchange_channelreq.format(currency = "SlimeCoin", action = "transfer")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count != 1:
        # Must have exactly one target to send to.
        response = "Mention the player you want to send SlimeCoin to."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.time_lastinvest + ewcfg.cd_invest > time_now:
        # Limit frequency of transfers
        response = ewcfg.str_exchange_busy.format(action = "transfer slimecoin")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_corpse:
        # Disallow transfers from ghosts.
        response = "Your slimebroker can't confirm your identity while you're dead."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    member = cmd.mentions[0]
    target_data = EwUser(member = member)

    if target_data.life_state == ewcfg.life_state_kingpin:
        # Disallow transfers to RF and CK kingpins.
        response = "You can't transfer SlimeCoin to a known criminal warlord."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    market_data = EwMarket(id_server = cmd.message.author.guild.id)

    if cmd.message.author.id == member.id:

        slimes_total = user_data.slimes
        slimes_drained = int(slimes_total * 0.1)
        slimes_todistrict = slimes_total - slimes_drained

        sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=user_data.id_server)
        sewer_data.change_slimes(n=slimes_drained)
        sewer_data.persist()

        district_data = EwDistrict(district=user_data.poi, id_server=cmd.guild.id)
        district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)
        district_data.persist()

        # Set the id_killer to the player himself, remove his slime and slime poudrins.
        user_data.id_killer = cmd.message.author.id
        user_data.visiting = ewcfg.location_id_empty
        user_data.trauma = ewcfg.trauma_id_environment

        user_data.die(cause = ewcfg.cause_suicide)
        user_data.persist()

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Gaming the slimeconomy is punishable by death. SlimeCorp soldiers execute you immediately."))
        await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
        return

    # Parse the slime value to send.
    value = None
    if cmd.tokens_count > 1:
        value = ewutils.getIntToken(tokens = cmd.tokens)

    if value != None:
        if value < 0:
            value = user_data.slimes
        if value <= 0:
            value = None

    if value != None:
        # Cost including the transfer fee.
        cost_total = round(value * 1.1)

        if user_data.slimecoin < cost_total:
            response = "You don't have enough SlimeCoin. ({:,}/{:,})".format(user_data.slimecoin, cost_total)
        else:
            # Do the transfer if the player can afford it.
            target_data.change_slimecoin(n = value, coinsource = ewcfg.coinsource_transfer)
            user_data.change_slimecoin(n = -cost_total, coinsource = ewcfg.coinsource_transfer)
            user_data.time_lastinvest = time_now

            # Persist changes
            response = "You transfer {slime:,} SlimeCoin to {target_name}. Your slimebroker takes his nominal fee of {fee:,} SlimeCoin.".format(slime = value, target_name = member.display_name, fee = (cost_total - value))

            target_data.persist()
            user_data.persist()
    else:
        response = ewcfg.str_exchange_specify.format(currency = "SlimeCoin", action = "transfer")

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" player turns slimecoin into slime """
async def redeem(cmd):
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    time_now = round(time.time())
    market_data = EwMarket(id_server = cmd.message.author.guild.id)

    if market_data.clock < 6 or market_data.clock >= 20:
        response = ewcfg.str_exchange_closed
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.time_lastinvest + ewcfg.cd_invest > time_now:
        response = ewcfg.str_exchange_busy.format(action = "redeem")

    if cmd.message.channel.name != ewcfg.channel_stockexchange:  #or user_data.poi != ewcfg.poi_id_downtown:
        # Only allowed in the stock exchange.
        response = ewcfg.str_exchange_channelreq.format(currency = "SlimeCoin", action = "redeem")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_corpse:
        # Disallow withdraws from ghosts.
        response = "Your slimebroker can't confirm your identity while you're dead."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        slimecoin_exchange_rate = 25000000000000 # 25 trillion slime

        redeem_value = round(user_data.slimecoin / slimecoin_exchange_rate)

        if redeem_value <= 0:
            response = "Sadly, you haven't made enough Slimecoin to reedeem any slime!"

        else:
            response = ""

            if user_data.life_state == ewcfg.life_state_enlisted:
                response = "After you dot all the i’s and cross all the t’s, you immediately send your Kingpin half of your earnings."
                role_boss = (ewcfg.role_copkiller if user_data.faction == ewcfg.faction_killers else ewcfg.role_rowdyfucker)
                kingpin = fe_utils.find_kingpin(id_server = cmd.guild.id, kingpin_role = role_boss)
                kingpin = EwUser(id_server=cmd.guild.id, id_user=kingpin.id_user)
                if kingpin:
                    kingpin.change_slimes(n = int(redeem_value / 2))
                    kingpin.persist()

            else:
                response = "Your slimebroker pulls a fast one on you and gets you to sign a waiver that lets SlimeCorp keep half of your supposedly redeemed slime. Damn."

            response += "You walk out with {:,}.".format(int(redeem_value / 2))
            user_data.slimes += int(redeem_value / 2)
            user_data.slimecoin = round(user_data.slimecoin % slimecoin_exchange_rate)
            user_data.persist()

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" show player's slimecoin balance """
async def slimecoin(cmd):
    if cmd.mentions_count == 0:
        user_data = EwUser(member = cmd.message.author)
        coins = user_data.slimecoin
        credits = user_data.salary_credits
        response = "You have {:,} SlimeCoin".format(coins)

        if credits != 0:
            response += " and {:,} SlimeCorp Salary Credits.".format(credits)
        else:
            response += "."

    else:
        member = cmd.mentions[0]
        user_data = EwUser(member = member)
        coins = user_data.slimecoin
        credits = user_data.salary_credits
        response = "{} has {:,} SlimeCoin".format(member.display_name, coins)

        if credits != 0:
            response += " and {:,} SlimeCorp Salary Credits.".format(credits)
        else:
            response += "."

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" donate slime to slimecorp in exchange for slimecoin """
async def donate(cmd):
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    market_data = EwMarket(id_server = user_data.id_server)

    time_now = round(time.time())

    if user_data.poi == ewcfg.poi_id_slimecorphq:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        value = None
        if cmd.tokens_count > 1:
            value = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)

        if value != None:
            if value < 0:
                value = user_data.slimes
            if value <= 0:
                value = None

        if value != None and value < ewcfg.slimecoin_exchangerate:
            response = "You must volunteer to donate at least %d slime to receive compensation." % ewcfg.slimecoin_exchangerate

        elif value != None:
            # Amount of slime invested.
            cost_total = round(value)
            coin_total = round(value / ewcfg.slimecoin_exchangerate)

            if user_data.slimes < cost_total:
                response = "Acid-green flashes of light and bloodcurdling screams emanate from small window of SlimeCorp HQ. Unfortunately, you did not survive the procedure. Your body is dumped down a disposal chute to the sewers."
                market_data.donated_slimes += user_data.slimes
                market_data.persist()
                user_data.trauma = ewcfg.trauma_id_environment
                die_resp = user_data.die(cause = ewcfg.cause_donation)
                user_data.persist()
                # Assign the corpse role to the player. He dead.
                await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
                await die_resp.post()
            else:
                # Do the transfer if the player can afford it.
                market_data.donated_slimes += cost_total
                market_data.persist()
                user_data.change_slimes(n = -cost_total, source = ewcfg.source_spending)
                user_data.change_slimecoin(n = coin_total, coinsource = ewcfg.coinsource_donation)
                user_data.slime_donations += cost_total

                # Persist changes
                user_data.persist()

                response = "You stumble out of a Slimecorp HQ vault room in a stupor. You don't remember what happened in there, but your body hurts and you've got {slimecoin:,} shiny new SlimeCoin in your pocket.".format(slimecoin = coin_total)

        else:
            response = ewcfg.str_exchange_specify.format(currency = "slime", action = "donate")

    elif user_data.poi == ewcfg.poi_id_slimeoidlab:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        poudrins = bknd_item.find_item(item_search = "slimepoudrin", id_user = cmd.message.author.id, id_server = cmd.guild.id if cmd.guild is not None else None, item_type_filter = ewcfg.it_item)

        if poudrins == None:
            response = "You have to own a poudrin in order to donate a poudrin. Duh."

        else:
            bknd_item.item_delete(id_item = poudrins.get('id_item'))  # Remove Poudrins
            market_data.donated_poudrins += 1
            market_data.persist()
            user_data.poudrin_donations += 1
            user_data.persist()

            response = "You hand off one of your hard-earned poudrins to the front desk receptionist, who is all too happy to collect it. Pretty uneventful, but at the very least you’re glad donating isn’t physically painful anymore."

    else:
        response = "To donate slime, go to the SlimeCorp HQ in Downtown. To donate poudrins, go to the N.L.A.C.U. Lab in Brawlden."

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" player invests slimecoin in the market """
async def invest(cmd):
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    time_now = round(time.time())
    market_data = EwMarket(id_server = cmd.message.author.guild.id)

    if cmd.message.channel.name != ewcfg.channel_stockexchange: # or user_data.poi != ewcfg.poi_id_downtown:
        # Only allowed in the stock exchange.
        response = ewcfg.str_exchange_channelreq.format(currency = "SlimeCoin", action = "invest")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if market_data.clock < 6 or market_data.clock >= 20:
        response = ewcfg.str_exchange_closed
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.time_lastinvest + ewcfg.cd_invest > time_now:
        # Limit frequency of investments.
        response = ewcfg.str_exchange_busy.format(action = "invest")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_corpse:
        # Disallow invests from ghosts.
        response = "Your slimebroker can't confirm your identity while you're dead."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_kingpin:
        # Disallow investments by RF and CK kingpins.
        response = "You need that money to buy more videogames."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        value = None
        stock = None

        if cmd.tokens_count > 1:
            value = ewutils.getIntToken(cmd.tokens, allow_all = True)

            for token in cmd.tokens[1:]:
                if token.lower() in ewcfg.stocks:
                    stock = token.lower()
                    break


        if value != None:
            if value < 0:
                value = user_data.slimecoin
            if value <= 0:
                value = None

        if value != None:
            if stock != None:

                stock = EwStock(id_server = cmd.guild.id, stock = stock)
                # basic exchange rate / 1000 = 1 share
                exchange_rate = (stock.exchange_rate / 1000.0)

                cost_total = round(value * 1.05)

                # gets the highest value possible where the player can still pay the fee
                if value == user_data.slimecoin:
                    while cost_total > user_data.slimecoin:
                        value -= cost_total - value
                        cost_total = round(value * 1.05)

                # The user can only buy a whole number of shares, so adjust their cost based on the actual number of shares purchased.
                net_shares = round(value / exchange_rate)

                if user_data.slimecoin < cost_total:
                    response = "You don't have enough SlimeCoin. ({:,}/{:,})".format(user_data.slimecoin, cost_total)

                elif value > user_data.slimecoin:
                    response = "You don't have that much SlimeCoin to invest."

                elif net_shares == 0:
                    response = "You don't have enough SlimeCoin to buy a share in {stock}".format(stock = ewcfg.stock_names.get(stock.id_stock))

                else:
                    user_data.change_slimecoin(n = -cost_total, coinsource = ewcfg.coinsource_invest)
                    shares = getUserTotalShares(id_server = user_data.id_server, stock = stock.id_stock, id_user = user_data.id_user)
                    shares += net_shares
                    updateUserTotalShares(id_server = user_data.id_server, stock = stock.id_stock, id_user = user_data.id_user, shares = shares)
                    user_data.time_lastinvest = time_now

                    stock.total_shares += net_shares
                    response = "You invest {coin:,} SlimeCoin and receive {shares:,} shares in {stock}. Your slimebroker takes his nominal fee of {fee:,} SlimeCoin.".format(coin = value, shares = net_shares, stock = ewcfg.stock_names.get(stock.id_stock), fee = (cost_total - value))

                    user_data.persist()
                    stock.timestamp = round(time.time())
                    stock.persist()

            else:
                response = "That's not a valid stock name, please use a proper one, you cunt: {}".format(ewutils.formatNiceList(names = ewcfg.stocks))

        else:
            response = ewcfg.str_exchange_specify.format(currency = "SlimeCoin", action = "invest")

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" player withdraws slimecoin from the market """
async def withdraw(cmd):
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    time_now = round(time.time())
    market_data = EwMarket(id_server = cmd.message.author.guild.id)

    if market_data.clock < 6 or market_data.clock >= 20:
        response = ewcfg.str_exchange_closed
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.message.channel.name != ewcfg.channel_stockexchange:  #or user_data.poi != ewcfg.poi_id_downtown:
        # Only allowed in the stock exchange.
        response = ewcfg.str_exchange_channelreq.format(currency = "SlimeCoin", action = "withdraw")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_corpse:
        # Disallow withdraws from ghosts.
        response = "Your slimebroker can't confirm your identity while you're dead."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        value = None
        stock = None

        if cmd.tokens_count > 1:
            value = ewutils.getIntToken(cmd.tokens[1:], allow_all = True)

            for token in cmd.tokens[1:]:
                if token.lower() in ewcfg.stocks:
                    stock = token.lower()
                    break


        if stock != None:
            stock = EwStock(id_server = cmd.guild.id, stock = stock)

            total_shares = getUserTotalShares(id_server = user_data.id_server, stock = stock.id_stock, id_user = user_data.id_user)

            if value != None:
                if value < 0:
                    value = total_shares
                if value <= 0:
                    value = None

            if value != None:

                if value <= total_shares:
                    exchange_rate = (stock.exchange_rate / 1000.0)

                    shares = value
                    slimecoin = round(value * exchange_rate)

                    if user_data.time_lastinvest + ewcfg.cd_invest > time_now:
                        # Limit frequency of withdrawals
                        response = ewcfg.str_exchange_busy.format(action = "withdraw")
                    else:
                        user_data.change_slimecoin(n = slimecoin, coinsource = ewcfg.coinsource_withdraw)
                        total_shares -= shares
                        user_data.time_lastinvest = time_now
                        stock.total_shares -= shares

                        response = "You exchange {shares:,} shares in {stock} for {coins:,} SlimeCoin.".format(coins = slimecoin, shares = shares, stock = ewcfg.stock_names.get(stock.id_stock))
                        user_data.persist()
                        stock.timestamp = round(time.time())
                        stock.persist()
                        updateUserTotalShares(id_server = user_data.id_server, stock = stock.id_stock, id_user = user_data.id_user, shares = total_shares)
                else:
                    response = "You don't have that many shares in {stock} to exchange.".format(stock = ewcfg.stock_names.get(stock.id_stock))
            else:
                response = ewcfg.str_exchange_specify.format(currency = "SlimeCoin", action = "withdraw")
        else:
            response = "That's not a valid stock name, please use a proper one, you cunt: {}".format(ewutils.formatNiceList(names = ewcfg.stocks))


    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" show the current market exchange rate """
async def rate(cmd):
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    response = ""

    if cmd.message.channel.name != ewcfg.channel_stockexchange:
        # Only allowed in the stock exchange.
        response = "You must go to the Slime Stock Exchange to check the current stock exchange rates ."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        stock = ""

        if cmd.tokens_count > 0:
            stock = ewutils.flattenTokenListToString(cmd.tokens[1:])

        if stock in ewcfg.stocks:
            stock = EwStock(id_server = cmd.guild.id, stock = stock)
            response = "The current value of {stock} stocks is {cred:,} SlimeCoin per 1000 Shares.".format(stock = ewcfg.stock_names.get(stock.id_stock), cred = stock.exchange_rate)
        elif stock == "":
            for stock in ewcfg.stocks:
                stock = EwStock(id_server = cmd.guild.id, stock = stock)
                response += "\nThe current value of {stock} stocks is {cred:,} SlimeCoin per 1000 Shares.".format(stock = ewcfg.stock_names.get(stock.id_stock), cred = stock.exchange_rate)

        else:
            response = "That's not a valid stock name, please use a proper one, you cunt: {}".format(ewutils.formatNiceList(ewcfg.stocks))

        # Send the response to the player.
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" show player's shares in a stock """
async def shares(cmd):
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    stock = ""
    response = ""

    if cmd.tokens_count > 0:
        stock = ewutils.flattenTokenListToString(cmd.tokens[1:])

    if stock in ewcfg.stocks:
        response = get_user_shares_str(id_server = user_data.id_server, id_user = user_data.id_user, stock = stock)

    elif stock == "":
        for stock in ewcfg.stocks:
            response += "\n"
            response += get_user_shares_str(id_server = user_data.id_server, id_user = user_data.id_user, stock = stock)

    else:
        response = "That's not a valid stock name, please use a proper one, you cunt: {}".format(ewutils.formatNiceList(ewcfg.stocks))

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" show all interactable stocks in the market """
async def stocks(cmd):
    user_data = EwUser(member = cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


    if cmd.message.channel.name != ewcfg.channel_stockexchange:
        # Only allowed in the stock exchange.
        response = "You must go to the Slime Stock Exchange to check the currently available stocks."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district = poi.id_poi, id_server = user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        response = "Here are the currently available stocks: {}".format(ewutils.formatNiceList(ewcfg.stocks))

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

""" Trading commands """
async def trade(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    user_trade = ewutils.active_trades.get(user_data.id_user)

    if user_trade != None and len(user_trade) > 0:
        if user_trade.get("state") > ewcfg.trade_state_proposed:

            stacking = True if 'stack' in ewutils.flattenTokenListToString(cmd.tokens[1:]).lower() else False
            sort_by_name = True if 'name' in ewutils.flattenTokenListToString(cmd.tokens[1:]).lower() else False

            stacked_item_map = {}

            # print info about the current trade
            trade_partner = EwPlayer(id_user=user_trade.get("trader"), id_server=user_data.id_server)

            #print player's offers
            response = "Your offers:\n"
            items = ewutils.trading_offers.get(user_data.id_user) if not sort_by_name else sorted(ewutils.trading_offers.get(user_data.id_user), key=lambda item: item.get("name").lower)
            for item in items:
                if not stacking:
                    response_part = "{id_item}: {name} {quantity}\n".format(id_item=item.get("id_item"), name=item.get("name"), quantity=(" x{:,}".format(item.get("quantity")) if (item.get("quantity") > 1) else ""))

                    if len(response) + len(response_part) > 1492:
                        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        response = ""

                    response += response_part

                else:
                    if item.get("name") in stacked_item_map:
                        stacked_item = stacked_item_map.get(item.get("name"))
                        stacked_item["quantity"] += item.get("quantity")
                    else:
                        stacked_item_map[item.get("name")] = deepcopy(item)

            if stacking:
                item_names = stacked_item_map.keys() if not sort_by_name else sorted(stacked_item_map.keys())

                for item_name in item_names:
                    item = stacked_item_map.get(item_name)
                    quantity = item.get('quantity')
                    response_part = "{soulbound_style}{name}{soulbound_style}{quantity}\n".format(
                        name=item.get('name'),
                        soulbound_style=("**" if item.get('soulbound') else ""),
                        quantity=(" **x{:,}**".format(quantity) if (quantity > 0) else "")
                    )

                    if len(response) + len(response_part) > 1492:
                        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        response = ""

                    response += response_part

            if user_trade.get("state") == ewcfg.trade_state_complete:
                response_part = "**You are ready to complete the trade.**"

                if len(response) + len(response_part) > 1492:
                    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                    response = ""

                response += response_part

            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            #print partner's offers
            stacked_item_map = {}

            response = trade_partner.display_name + "'s offers:\n"
            items = ewutils.trading_offers.get(trade_partner.id_user) if not sort_by_name else sorted(ewutils.trading_offers.get(trade_partner.id_user), key=lambda item: item.get("name").lower)
            for item in items:
                if not stacking:
                    response_part = "{id_item}: {name} {quantity}\n".format(id_item=item.get("id_item"), name=item.get("name"), quantity=(" x{:,}".format(item.get("quantity")) if (item.get("quantity") > 1) else ""))

                    if len(response) + len(response_part) > 1492:
                        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        response = ""

                    response += response_part

                else:
                    if item.get("name") in stacked_item_map:
                        stacked_item = stacked_item_map.get(item.get("name"))
                        stacked_item["quantity"] += item.get("quantity")
                    else:
                        stacked_item_map[item.get("name")] = deepcopy(item)

            if stacking:
                item_names = stacked_item_map.keys() if not sort_by_name else sorted(stacked_item_map.keys())

                for item_name in item_names:
                    item = stacked_item_map.get(item_name)
                    quantity = item.get('quantity')
                    response_part = "{soulbound_style}{name}{soulbound_style}{quantity}\n".format(
                        name=item.get('name'),
                        soulbound_style=("**" if item.get('soulbound') else ""),
                        quantity=(" **x{:,}**".format(quantity) if (quantity > 0) else "")
                    )

                    if len(response) + len(response_part) > 1492:
                        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        response = ""

                    response += response_part

            if ewutils.active_trades.get(trade_partner.id_user).get("state") == ewcfg.trade_state_complete:
                response_part = '**They are ready to complete the trade.**'

                if len(response) + len(response_part) > 1492:
                    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                    response = ""

                response += response_part

            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        if cmd.mentions_count == 0:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Who do you want to trade with?"))

        if cmd.mentions_count > 1:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You can only trade with one person at a time."))

        trade_partner = EwUser(member=cmd.mentions[0])

        if user_data.id_user == trade_partner.id_user:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Huh?"))

        if user_data.poi != trade_partner.poi:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You must be in the same location as someone to trade with them."))

        if ewutils.active_trades.get(trade_partner.id_user) != None and len(ewutils.active_trades.get(trade_partner.id_user)) > 0:
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Wait for them to finish their business before trying to trade with them."))

        ewutils.active_trades[user_data.id_user] = {"state": ewcfg.trade_state_proposed, "trader": trade_partner.id_user}
        ewutils.active_trades[trade_partner.id_user] = {"state": ewcfg.trade_state_proposed, "trader": user_data.id_user}

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.mentions[0], "{user} wants to trade with you. Do you {accept} or {refuse}?".format(user=cmd.message.author.display_name, accept=ewcfg.cmd_accept, refuse=ewcfg.cmd_refuse)))

        accepted = False

        try:
            member = cmd.mentions[0]
            msg = await cmd.client.wait_for('message', timeout = 30, check=lambda message: message.author == member and
                                                    message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

            if msg != None and msg.content.lower() == ewcfg.cmd_accept:
                accepted = True
        except:
            accepted = False

        if accepted:
            ewutils.active_trades[user_data.id_user] = {"state": ewcfg.trade_state_ongoing, "trader": trade_partner.id_user}
            ewutils.active_trades[trade_partner.id_user] = {"state": ewcfg.trade_state_ongoing, "trader": user_data.id_user}

            ewutils.trading_offers[user_data.id_user] = []

            ewutils.trading_offers[trade_partner.id_user] = []

            response = "You both head into a shady alleyway nearby to conduct your business."

        else:
            ewutils.active_trades[user_data.id_user] = {}
            ewutils.active_trades[trade_partner.id_user] = {}
            response = "They didn't respond in time."

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

async def offer_item(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    user_trade = ewutils.active_trades.get(user_data.id_user)

    if user_trade != None and len(user_trade) > 0 and user_trade.get("state") > ewcfg.trade_state_proposed:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_search)
        except:
            item_id_int = None

        if item_search != None and len(item_search) > 0:
            item_sought = None

            inventory = bknd_item.inventory(
                id_user=user_data.id_user,
                id_server=user_data.id_server
            )

            for item in inventory:
                if (item.get('id_item') == item_id_int or item_search in ewutils.flattenTokenListToString(item.get('name'))) \
                    and item not in ewutils.trading_offers.get(user_data.id_user):
                    item_sought = item

            if item_sought:
                item = EwItem(id_item=item_sought.get("id_item"))

                if not item.soulbound or EwItem(id_item = item_sought.get('id_item')).item_props.get("context") == "housekey":

                    if item.id_item == user_data.weapon and user_data.weaponmarried:
                        response = "Unfortunately for you, the contract you signed before won't let you trade your partner away. You'll have to get your cuckoldry fix from somewhere else."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    ewutils.trading_offers[user_data.id_user].append(item_sought)
                    response = "You add a {} to your offers.".format(item_sought.get("name"))

                    user_trade["state"] = ewcfg.trade_state_ongoing
                    ewutils.active_trades.get(user_trade.get("trader"))["state"] = ewcfg.trade_state_ongoing

                else:
                    response = "You can't trade soulbound items."
            else:
                if item_search:
                    response = "You don't have one."
        else:
            response = "Offer which item? (check **!inventory**)"
    else:
        response = "You need to be trading with someone to offer an item."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

async def remove_offer(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    user_trade = ewutils.active_trades.get(user_data.id_user)

    if user_trade != None and len(user_trade) > 0 and user_trade.get("state") > ewcfg.trade_state_proposed:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_search)
        except:
            item_id_int = None

        if item_search != None and len(item_search) > 0:
            item_sought = None

            inventory = bknd_item.inventory(
                id_user=user_data.id_user,
                id_server=user_data.id_server
            )

            for item in inventory:
                if (item.get('id_item') == item_id_int or item_search in ewutils.flattenTokenListToString(item.get('name'))) \
                    and item in ewutils.trading_offers.get(user_data.id_user):
                    item_sought = item

            if item_sought:
                item = EwItem(id_item=item_sought.get("id_item"))

                ewutils.trading_offers[user_data.id_user].remove(item_sought)
                response = "You remove {} from your offers.".format(item_sought.get("name"))

                user_trade["state"] = ewcfg.trade_state_ongoing
                ewutils.active_trades.get(user_trade.get("trader"))["state"] = ewcfg.trade_state_ongoing

            else:
                if item_search:
                    response = "You don't have one."
        else:
            response = "Remove which offer? (check **!trade**)"
    else:
        response = "You need to be trading with someone to remove an offer."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

async def complete_trade(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    user_trade = ewutils.active_trades.get(user_data.id_user)

    if user_trade != None and len(user_trade) > 0 and user_trade.get("state") > ewcfg.trade_state_proposed:
        user_trade["state"] = ewcfg.trade_state_complete

        trader_id = user_trade.get("trader")
        if ewutils.active_trades.get(trader_id).get("state") != ewcfg.trade_state_complete:
            partner_player = EwPlayer(id_user=trader_id, id_server=user_data.id_server)
            response = "You tell {} that you're ready to finish the trade.".format(partner_player.display_name)

        else:
            trade_partner = EwUser(id_user=trader_id, id_server=user_data.id_server)

            #items this player is offering
            items_offered = {}

            #items the other player is offering
            trader_items_offered = {}

            for item in ewutils.trading_offers.get(user_data.id_user):
                if items_offered.get(item.get("item_type")) != None:
                    items_offered[item.get("item_type")] += 1
                else:
                    items_offered[item.get("item_type")] = 1

            for item in ewutils.trading_offers.get(trade_partner.id_user):
                if trader_items_offered.get(item.get("item_type")) != None:
                    trader_items_offered[item.get("item_type")] += 1
                else:
                    trader_items_offered[item.get("item_type")] = 1

            # check items currently held + items being given to the player - items the player is giving
            # check other user's inventory capacity
            for item_type in items_offered:
                it_held = bknd_item.inventory(
                    id_user = trade_partner.id_user,
                    id_server = trade_partner.id_server,
                    item_type_filter = item_type
                )

                if item_type == ewcfg.it_food:
                    if (len(it_held) + items_offered[ewcfg.it_food] - trader_items_offered.get(ewcfg.it_food, 0)) > trade_partner.get_food_capacity():
                        response = "They can't carry any more food items."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                elif item_type == ewcfg.it_weapon:
                    if (len(it_held) + items_offered[ewcfg.it_weapon] - trader_items_offered.get(ewcfg.it_weapon, 0)) > trade_partner.get_weapon_capacity():
                        response = "They can't carry any more weapon items."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                else:
                    if (len(it_held) + items_offered[item_type] - trader_items_offered.get(item_type, 0)) > ewcfg.generic_inv_limit:
                        response = "They can't carry any more {}s.".format(item_type)
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            # check own user's inventory capacity
            for item_type in trader_items_offered:
                it_held = bknd_item.inventory(
                    id_user = user_data.id_user,
                    id_server = user_data.id_server,
                    item_type_filter = item_type
                )

                if item_type == ewcfg.it_food:
                    if (len(it_held) + trader_items_offered[ewcfg.it_food] - items_offered.get(ewcfg.it_food, 0)) > user_data.get_food_capacity():
                        response = "You can't carry any more food items."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                elif item_type == ewcfg.it_weapon:
                    if (len(it_held) + trader_items_offered[ewcfg.it_weapon] - items_offered.get(ewcfg.it_weapon, 0)) > user_data.get_weapon_capacity():
                        response = "You can't carry any more weapon items."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                else:
                    if (len(it_held) + trader_items_offered.get(item_type) - items_offered.get(item_type, 0)) > ewcfg.generic_inv_limit:
                        response = "You can't carry any more {}s.".format(item_type)
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            for item in list(ewutils.trading_offers.get(user_data.id_user)):
                if item.get("id_item") == user_data.weapon:
                    user_data.weapon = -1
                    user_data.persist()
                elif item.get("id_item") == user_data.sidearm:
                    user_data.sidearm = -1
                    user_data.persist()
                elif item.get("item_type") == ewcfg.it_cosmetic:
                    cosmetic = EwItem(id_item=item.get("id_item"))
                    cosmetic.item_props["adorned"] = 'false'
                    cosmetic.item_props["slimeoid"] = 'false'
                    cosmetic.persist()

                bknd_item.give_item(id_item=item.get("id_item"), id_user=trade_partner.id_user, id_server=trade_partner.id_server)

            for item in list(ewutils.trading_offers.get(trade_partner.id_user)):
                if item.get("id_item") == trade_partner.weapon:
                    trade_partner.weapon = -1
                    trade_partner.persist()
                elif item.get("id_item") == trade_partner.sidearm:
                    trade_partner.sidearm = -1
                    user_data.persist()
                elif item.get("item_type") == ewcfg.it_cosmetic:
                    cosmetic = EwItem(id_item=item.get("id_item"))
                    cosmetic.item_props["adorned"] = 'false'
                    cosmetic.item_props["slimeoid"] = 'false'
                    cosmetic.persist()

                bknd_item.give_item(id_item=item.get("id_item"), id_user=user_data.id_user, id_server=user_data.id_server)

            ewutils.active_trades[user_data.id_user] = {}
            ewutils.active_trades[trade_partner.id_user] = {}

            ewutils.trading_offers[user_data.id_user] = []
            ewutils.trading_offers[trade_partner.id_user] = []

            response = "You shake hands to commemorate another successful deal. That is their hand, right?"
    else:
        response = "You're not trading with anyone right now."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

async def cancel_trade(cmd):
    user_trade = ewutils.active_trades.get(cmd.message.author.id)

    #if user_data.life_state == ewcfg.life_state_shambler:
    #	response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
    #	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


    if user_trade != None and len(user_trade) > 0 and user_trade.get("state") > ewcfg.trade_state_proposed:
        ewutils.end_trade(cmd.message.author.id)
        response = "With your finely attuned business senses you realize they're trying to scam you and immediately call off the deal."
    else:
        response = "You're not trading with anyone right now."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
