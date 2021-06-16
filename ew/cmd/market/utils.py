from ew.backend import core as bknd_core
from ew.backend.market import EwStock
from ew.static import cfg as ewcfg
from ew.utils import market as market_utils
from ew.utils.combat import EwUser

""" Returns an array of the most recent counts of all invested slime coin, from newest at 0 to oldest. """


# Unused
def getRecentTotalShares(id_server = None, stock = None, count = 2):
    if id_server != None and stock != None:

        values = []

        try:

            count = round(count)
            data = bknd_core.execute_sql_query("SELECT {total_shares} FROM stocks WHERE {id_server} = %s AND {stock} = %s ORDER BY {timestamp} DESC LIMIT %s".format(
                stock=ewcfg.col_stock,
                total_shares=ewcfg.col_total_shares,
                id_server=ewcfg.col_id_server,
                timestamp=ewcfg.col_timestamp,
            ), (
                id_server,
                stock,
                (count if (count > 0) else 2)
            ))

            for row in data:
                values.append(row[0])

            # Make sure we return at least one value.
            if len(values) == 0:
                values.append(0)

            # If we don't have enough data, pad out to count with the last value in the array.
            value_last = values[-1]
            while len(values) < count:
                values.append(value_last)
        except:
            pass
        finally:
            return values


""" used for !shares """


def get_user_shares_str(id_server = None, stock = None, id_user = None):
    response = ""
    if id_server != None and stock != None and id_user != None:
        user_data = EwUser(id_server=id_server, id_user=id_user)
        stock = EwStock(id_server=id_server, stock=stock)
        shares = market_utils.getUserTotalShares(id_server=user_data.id_server, stock=stock.id_stock, id_user=user_data.id_user)
        shares_value = round(shares * (stock.exchange_rate / 1000.0))

        response = "You have {shares:,} shares in {stock}".format(shares=shares, stock=ewcfg.stock_names.get(stock.id_stock))

        # if user_data.poi == ewcfg.poi_id_downtown:
        response += ", currently valued at {coin:,} SlimeCoin.".format(coin=shares_value)
        # else:
        #	response += "."

    return response
