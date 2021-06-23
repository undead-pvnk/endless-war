from . import core as bknd_core
from ..static import cfg as ewcfg
from ..static import poi as poi_static
from ..utils import core as ewutils


class EwTransportBase:
    # server id
    id_server = -1

    # id of the EwPoi object for this transport
    poi = ""

    # string describing the kind of vehicle it is
    transport_type = ""

    # which line the vehicle follows. see EwTransportLine object
    current_line = ""

    # connection to the world map
    current_stop = ""

    """ Retrieve object from database, or initialize it, if it doesn't exist yet """

    def __init__(self, id_server = None, poi = None):
        if id_server is not None and poi is not None:
            self.id_server = id_server
            self.poi = poi
            try:
                data = bknd_core.execute_sql_query("SELECT {transport_type}, {current_line}, {current_stop} FROM transports WHERE {id_server} = %s AND {poi} = %s".format(
                    transport_type=ewcfg.col_transport_type,
                    current_line=ewcfg.col_current_line,
                    current_stop=ewcfg.col_current_stop,
                    id_server=ewcfg.col_id_server,
                    poi=ewcfg.col_poi
                ), (
                    self.id_server,
                    self.poi
                ))
                # Retrieve data if the object was found
                if len(data) > 0:
                    self.transport_type = data[0][0]
                    self.current_line = data[0][1]
                    self.current_stop = data[0][2]
                # initialize it per the Poi default otherwise
                else:
                    poi_data = poi_static.id_to_poi.get(self.poi)
                    if poi_data is not None:
                        self.transport_type = poi_data.transport_type
                        self.current_line = poi_data.default_line
                        self.current_stop = poi_data.default_stop

                        self.persist()
            except:
                ewutils.logMsg("Failed to retrieve transport {} from database.".format(self.poi))

    """ Write object to database """

    def persist(self):

        try:
            bknd_core.execute_sql_query("REPLACE INTO transports ({id_server}, {poi}, {transport_type}, {current_line}, {current_stop}) VALUES (%s, %s, %s, %s, %s)".format(
                id_server=ewcfg.col_id_server,
                poi=ewcfg.col_poi,
                transport_type=ewcfg.col_transport_type,
                current_line=ewcfg.col_current_line,
                current_stop=ewcfg.col_current_stop
            ), (
                self.id_server,
                self.poi,
                self.transport_type,
                self.current_line,
                self.current_stop
            ))
        except:
            ewutils.logMsg("Failed to write transport {} to database.".format(self.poi))
