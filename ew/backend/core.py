import time
import traceback
from copy import copy, deepcopy

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

obj_type_to_identifiers = {
    "EwItem": [{"id_item", "id_entry"}],
    "EwPlayer": [{"id_user", "id_entry"}],
    #"EwUser": ["id_user", "id_server"],
}

obj_type_to_nested_props = {
    "EwItem": ["item_props"],
    #"EwEnemy": ["enemy_props"],
}

class ObjCache():
    entry_type = None

    identifiers = []
    nested_props = []
    entries = {}

    def __init__(self, ew_obj_type = None):
        """ Takes the string representing the class type. Found with `type(instance).__name__` """

        # Track the object type stored in the cache
        self.entry_type = ew_obj_type

        # If this isn't done all instances use the same dict
        self.entries = {}

        # Check if it has been given an identifying column
        if ew_obj_type in obj_type_to_identifiers.keys():
            # declare the unique columns
            self.identifiers = obj_type_to_identifiers.get(ew_obj_type)

        # Find any nested properties so copying will work right
        if ew_obj_type in obj_type_to_nested_props.keys():
            self.nested_props = obj_type_to_nested_props.get(ew_obj_type)

    def get_data_id(self, data):
        """ Takes a dictionary of all identifier names and values, and converts to a string """

        # Set Up
        return_id = None

        # Iterate through all identifying properties
        for prop_type in self.identifiers:
            # Allow for entry_id to be recognized as user_id or item_id etc.
            shared_names = [name for name in data.keys() if name in prop_type]

            # Handle the value if it exists
            if shared_names:
                prop_val = data.get(shared_names[0])
                # Format the value based on whether it's the first, and add to the final id
                return_id = str(prop_val) if (return_id is None) else "{}~{}".format(return_id, prop_val)
            else:
                # Data is missing a necessary identifier
                return False

        # Return the made identifier
        if return_id is not None:
            return return_id
        elif len(self.identifiers) == 0:
            # If the type has no identifiers, then simple number the entries as they come in.
            # Everything from the DB should have a unique column or pair of, this shouldn't ever be used
            return str(len(self.entries) + 1)

    def copy_entry(self, data):
        # Run a surface level copy
        ret_dat = copy(data)

        # Since the caches are being typed, we know what values will be too deep to copy. So Get those replaced
        for prop in self.nested_props:
            # Ensure the data has the prop, then copy and replace
            if prop in ret_dat.keys():
                # Ensure the pointing entry is removed
                ret_dat.pop(prop)

                # And replaced with the copy
                prop_cop = copy(data.get(prop))
                ret_dat.update({prop: prop_cop})

            else:
                # Data was incompatible, make it known
                return False

        return ret_dat

    def set_entry(self, data):
        # Attempt to get unique ID for the data
        entry_id = self.get_data_id(data)
        # Ensure saved data is separated from active use data
        unique_data = self.copy_entry(data)

        # Save it if it's real, if it's missing a property it should have, one of these should return false
        if (entry_id is not False) and (unique_data is not False):
            self.entries.update({entry_id: unique_data})
            return True
        else:
            print("Cache for {}s was passed incompatible or incomplete data. \nData Passed: {}".format(self.entry_type, data))
            return False

    def get_entry(self, unique_vals = None):
        # Convert identifiers to a string of consistent order and format
        id_str = self.get_data_id(unique_vals)
        #print("Searching {} cache for id {}".format(self.entry_type, id_str))

        # Find the target data and copy it so nothing receives a pointer to the cache
        return self.copy_entry(self.entries.get(id_str)) if (id_str in self.entries.keys()) else False

    def delete_entry(self, unique_vals = None):
        # Convert identifiers to a string of consistent order and format
        id_str = self.get_data_id(unique_vals)

        if id_str in self.entries.keys():
            # Delete the entry if it exists
            self.entries.pop(id_str)

    def find_entries(self, criteria = None):
        copied_matches = []

        # iterate through all entered data
        for data in self.entries.values():

            # Check against all given criteria
            meets = True
            for key, value in criteria.items():

                # Stop and mark if it isn't a match
                if not ((key in data.keys()) and (str(value) == str(data.get(key)))):
                    meets = False
                    break

            # track data if it matches
            if meets:
                copied_matches.append(self.copy_entry(data))

        return copied_matches


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


def get_cache_result(obj_type = None, id_server = None, id_entry = None):
    #print("Obj Type {} with id {} attempting retrieval".format(obj_type, id_entry))
    # Setup, and grab the cache if it exists
    obj_cache = cached_db.get(obj_type) if obj_type in cached_db.keys() else False
    result = False

    # if the cache exists, try to grab the item
    if obj_cache is not False:
        ids_dict = {
            "id_server": id_server,
            "id_entry": id_entry,
        }
        result = obj_cache.get_entry(unique_vals=ids_dict)

    #print("Found result: \n{}".format(result))
    return result


""" Add a row to the cached database """
def cache_data(obj_type = None, data = None):
    if obj_type not in cached_db.keys():
        # Initialize a cache for the given object type if it doesnt exist
        cached_db.update({obj_type: ObjCache(ew_obj_type=obj_type)})

    #print("Caching as {}:\n{}".format(obj_type, data))
    # Grab the cache and send it the data
    cached_db.get(obj_type).set_entry(data)


""" Removes an entry, from the cache """
def remove_entry(obj_type = None, id_server = None, id_entry = None):
    # Organize potential identifiers
    identifiers = {
        "id_server": id_server,
        "id_entry": id_entry,
    }

    # Remove if it exists
    if obj_type in cached_db.keys():
        cached_db.get(obj_type).delete_entry(unique_vals = identifiers)
