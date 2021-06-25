from . import core as bknd_core
from ..static import cfg as ewcfg


class EwPrankIndex:
    id_server = -1
    id_user_pranker = -1
    id_user_pranked = -1
    prank_count = 0  # How many times has user 1 (pranker) pranked user 2 (pranked)?

    def __init__(
            self,
            id_server = -1,
            id_user_pranker = -1,
            id_user_pranked = -1,
            prank_count = 0,
    ):
        self.id_server = id_server
        self.id_user_pranker = id_user_pranker
        self.id_user_pranked = id_user_pranked
        self.prank_count = prank_count

        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Retrieve object
            cursor.execute("SELECT {count} FROM swilldermuk_prank_index WHERE {id_user_pranker} = %s AND {id_user_pranked} = %s AND {id_server} = %s".format(
                count=ewcfg.col_prank_count,
                id_user_pranker=ewcfg.col_id_user_pranker,
                id_user_pranked=ewcfg.col_id_user_pranked,
                id_server=ewcfg.col_id_server,
            ), (
                self.id_user_pranker,
                self.id_user_pranked,
                self.id_server,
            ))
            result = cursor.fetchone()

            if result != None:
                # Record found: apply the data to this object.
                self.prank_count = result[0]

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
                "REPLACE INTO swilldermuk_prank_index({}, {}, {}, {}) VALUES(%s, %s, %s, %s)".format(
                    ewcfg.col_id_server,
                    ewcfg.col_id_user_pranker,
                    ewcfg.col_id_user_pranked,
                    ewcfg.col_prank_count,
                ), (
                    self.id_server,
                    self.id_user_pranker,
                    self.id_user_pranked,
                    self.prank_count,
                ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)
