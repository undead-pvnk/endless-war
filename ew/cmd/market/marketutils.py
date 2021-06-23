from ew.backend import core as bknd_core
from ew.static import cfg as ewcfg

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
