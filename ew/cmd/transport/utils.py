import asyncio

from ew.backend import core as bknd_core
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils.transport import EwTransport

""" Starts movement of all transports. Called once at client startup """
async def init_transports(id_server = None):
	if id_server is not None:
		for poi in poi_static.transports:
			transport_data = EwTransport(id_server = id_server, poi = poi)
			asyncio.ensure_future(transport_data.move_loop())

""" Returns a list of Poi IDs """
def get_transports_at_stop(id_server, stop):
	result = []
	try:
		data = bknd_core.execute_sql_query("SELECT {poi} FROM transports WHERE {id_server} = %s AND {current_stop} = %s".format(
				poi = ewcfg.col_poi,
				id_server = ewcfg.col_id_server,
				current_stop = ewcfg.col_current_stop
			),(
				id_server,
				stop
			))
		for row in data:
			result.append(row[0])

	except:
		ewutils.logMsg("Failed to retrieve transports at stop {}.".format(stop))
	finally:
		return result
