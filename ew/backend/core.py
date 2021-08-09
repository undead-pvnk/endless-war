import time

import MySQLdb

from ..static import cfg as ewcfg

db_pool = {}
db_pool_id = 0

cached_db = {
    #'table-name': {
    #   'idserverasnumber~entryidasnumber': {
    #       ewcfg.col_id: entry
    #   }
    # },
    #'inventories': {
    #   '169282450621595648': [2, 6, 9, 25],
    #   'owner_id': [all item id's belonging to them]
    #}
}

""" connect to the database """

def databaseConnect():
    conn_info = None

    conn_id_todelete = []

    global db_pool
    global db_pool_id

    # Iterate through open connections and find the currently active one.
    for pool_id in db_pool:
        conn_info_iter = db_pool.get(pool_id)

        if conn_info_iter['closed'] == True:
            if conn_info_iter['count'] <= 0:
                conn_id_todelete.append(pool_id)
        else:
            conn_info = conn_info_iter

    # Close and remove dead connections.
    if len(conn_id_todelete) > 0:
        for pool_id in conn_id_todelete:
            conn_info_iter = db_pool[pool_id]
            conn_info_iter['conn'].close()

            del db_pool[pool_id]

    # Create a new connection.
    if conn_info == None:
        db_pool_id += 1
        conn_info = {
            'conn': MySQLdb.connect(host="localhost", user="rfck-bot", passwd="rfck", db=ewcfg.database, charset="utf8mb4"),
            'created': int(time.time()),
            'count': 1,
            'closed': False
        }
        db_pool[db_pool_id] = conn_info
    else:
        conn_info['count'] += 1

    return conn_info


""" close (maybe) the active database connection """


def databaseClose(conn_info):
    conn_info['count'] -= 1

    # Expire old database connections.
    if (conn_info['created'] + 60) < int(time.time()):
        conn_info['closed'] = True


"""
	Execute a given sql_query. (the purpose of this function is to minimize repeated code and keep functions readable)
"""


def execute_sql_query(sql_query = None, sql_replacements = None):
    data = None

    try:
        conn_info = databaseConnect()
        conn = conn_info.get('conn')
        cursor = conn.cursor()
        cursor.execute(sql_query, sql_replacements)
        if sql_query.lower().startswith("select"):
            data = cursor.fetchall()
        conn.commit()
    finally:
        # Clean up the database handles.
        cursor.close()
        databaseClose(conn_info)

    return data


""" Check the cached_db for data, return the data like a sql query if found, otherwise return false"""


def get_cache_result(table = None, id_server = None, id_entry = None):
    # Check inputs
    if table != None and id_entry != None:
        # See if table is cached
        cached_table = cached_db.get(table)
        if cached_table is not None:
            # Attempt to grab the entry
            if id_server != None:
                entry_key = "{}~{}".format(id_server, id_entry)
            else:
                entry_key = str(id_entry)
            entry = cached_table.get(entry_key)
            # Return if entry found
            if entry is not None:
                return entry

    return False


""" Add a row to the cached database """
def cache_data(table = None, id_server = None, id_entry = None, data = None):
    # Create entry
    if id_server is not None:
        entry = {
            "{}~{}".format(id_server, id_entry): data
        }
    else:
        entry = {
            str(id_entry): data
        }

    # Check for table
    if cached_db.__contains__(table):
        cached_db.get(table).update(entry)
    else:
        cached_db.update({table: entry})


""" Removes an entry, from the cache """
def remove_entry(table = None, id_server = None, id_entry = None):
    # Determine Identifier
    entry = "{}~{}".format(id_server, id_entry) if id_server is not None else str(id_entry)

    # Remove if it exists
    if cached_db.__contains__(table) and cached_db.get(table).__contains__(entry):
        cached_db.get(table).pop(entry)
