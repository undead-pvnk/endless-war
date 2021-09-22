import time

from . import core as bknd_core
from ..static import cfg as ewcfg


class EwOffer:
    id_server = -1
    id_user = -1
    offer_give = 0
    offer_receive = ""
    time_sinceoffer = 0

    def __init__(
            self,
            id_server = None,
            id_user = None,
            offer_give = None,

    ):
        if id_server is not None and id_user is not None and offer_give is not None:
            self.id_server = id_server
            self.id_user = id_user
            self.offer_give = offer_give

            data = bknd_core.execute_sql_query(
                "SELECT {time_sinceoffer} FROM offers WHERE id_server = %s AND id_user = %s AND {col_offer_give} = %s".format(
                    time_sinceoffer=ewcfg.col_time_sinceoffer,
                    col_offer_give=ewcfg.col_offer_give,
                ), (
                    id_server,
                    id_user,
                    offer_give,
                )
            )

            if len(data) > 0:  # if data is not empty, i.e. it found an entry
                # data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
                self.time_sinceoffer = data[0][0]

            data = bknd_core.execute_sql_query(
                "SELECT {col_offer_receive} FROM offers WHERE id_server = %s AND id_user = %s AND {col_offer_give} = %s".format(
                    col_offer_receive=ewcfg.col_offer_receive,
                    col_offer_give=ewcfg.col_offer_give,
                ), (
                    id_server,
                    id_user,
                    offer_give,
                )
            )

            if len(data) > 0:  # if data is not empty, i.e. it found an entry
                # data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
                self.offer_receive = data[0][0]

            else:  # create new entry
                bknd_core.execute_sql_query(
                    "REPLACE INTO offers(id_server, id_user, {col_offer_give}) VALUES (%s, %s, %s)".format(
                        col_offer_give=ewcfg.col_offer_give,
                    ), (
                        id_server,
                        id_user,
                        offer_give,
                    )
                )

    def persist(self):
        bknd_core.execute_sql_query(
            "REPLACE INTO offers(id_server, id_user, {col_offer_give}, {col_offer_receive}, {col_time_sinceoffer}) VALUES (%s, %s, %s, %s, %s)".format(
                col_offer_give=ewcfg.col_offer_give,
                col_offer_receive=ewcfg.col_offer_receive,
                col_time_sinceoffer=ewcfg.col_time_sinceoffer
            ), (
                self.id_server,
                self.id_user,
                self.offer_give,
                self.offer_receive,
                self.time_sinceoffer
            )
        )

    def deal(self):
        bknd_core.execute_sql_query("DELETE FROM offers WHERE {id_user} = %s AND {id_server} = %s AND {col_offer_give} = %s".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            col_offer_give=ewcfg.col_offer_give,
        ), (
            self.id_user,
            self.id_server,
            self.offer_give
        ))



class EwRecord:
    # ID of the server
    id_server = -1

    # ID of the record holder
    id_user = -1

    # The item length being set
    record_type = ""

    # The length/record amount
    record_amount = 0.0

    # whether the submission is legal or not
    legality = 1

    # the ID of the post in the server
    id_post = ""

    #an associated image with the work
    id_image = "-...-"

    def __init__(
            self,
            id_server=None,
            record_type=None
    ):
        if (record_type != None) and (id_server != None):
            self.id_server = id_server
            self.record_type = record_type

            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                # Retrieve object

                print("SELECT {}, {}, {}, {}, {} FROM records WHERE record_type = %s AND id_server = %s".format(
                        ewcfg.col_id_user,
                        ewcfg.col_record_amount,
                        ewcfg.col_legality,
                        ewcfg.col_id_post,
                        ewcfg.col_id_image
                    ),(
                        self.record_type,
                        self.id_server
                    ))

                cursor.execute(
                    "SELECT {}, {}, {}, {}, {} FROM records WHERE record_type = %s AND id_server = %s".format(
                        ewcfg.col_id_user,
                        ewcfg.col_record_amount,
                        ewcfg.col_legality,
                        ewcfg.col_id_post,
                        ewcfg.col_id_image
                    ),(
                        self.record_type,
                        self.id_server
                    ))
                result = cursor.fetchone()

                if result != None:
                    # Record found: apply the data to this object.
                    self.id_user = result[0]
                    self.record_amount = result[1]
                    self.legality = result[2]
                    self.id_post = result[3]
                    self.id_image = result[4]
            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

    def persist(self):
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Save the object.
            cursor.execute(
                "REPLACE INTO records({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
                    ewcfg.col_id_server,
                    ewcfg.col_record_type,
                    ewcfg.col_record_amount,
                    ewcfg.col_id_user,
                    ewcfg.col_legality,
                    ewcfg.col_id_post,
                    ewcfg.col_id_image,
                ), (
                    self.id_server,
                    self.record_type,
                    self.record_amount,
                    self.id_user,
                    self.legality,
                    self.id_post,
                    self.id_image
                ))
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)

def kill_dead_offers(id_server):
    time_now = int(time.time() / 60)
    bknd_core.execute_sql_query("DELETE FROM offers WHERE {id_server} = %s AND {time_sinceoffer} < %s".format(
        id_server=ewcfg.col_id_server,
        time_sinceoffer=ewcfg.col_time_sinceoffer,
    ), (
        id_server,
        time_now - ewcfg.fish_offer_timeout,
    ))

