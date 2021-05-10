import time

import MySQLdb

from ..static import cfg as ewcfg

db_pool = {}
db_pool_id = 0

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
		'conn': MySQLdb.connect(host = "localhost", user = "rfck-bot", passwd = "rfck" , db = ewcfg.database, charset = "utf8mb4"),
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

