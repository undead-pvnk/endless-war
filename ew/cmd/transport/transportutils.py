from ew.backend import core as bknd_core
from ew.static import cfg as ewcfg
from ew.utils import core as ewutils

""" Returns a list of Poi IDs """


def get_transports_at_stop(id_server, stop):
    result = []
    try:
        data = bknd_core.execute_sql_query("SELECT {poi} FROM transports WHERE {id_server} = %s AND {current_stop} = %s".format(
            poi=ewcfg.col_poi,
            id_server=ewcfg.col_id_server,
            current_stop=ewcfg.col_current_stop
        ), (
            id_server,
            stop
        ))
        for row in data:
            result.append(row[0])

    except:
        ewutils.logMsg("Failed to retrieve transports at stop {}.".format(stop))
    finally:
        return result
