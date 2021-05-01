from . import core as bknd_core

from ..static import cfg as ewcfg
from .. import utils as ewutils

class EwGamestate():
	#server id, duh
	id_server = -1

	#name of the state
	id_state = ""

	#setting of the state, on or off
	bit = True

	#additional value for unique states
	value = ""

	def __init__(
			self,
			 id_state = None,
			 id_server = None
			):

		if id_server is not None and id_state is not None:
			self.id_server = id_server
			self.id_state = id_state
			try:
				data = bknd_core.execute_sql_query("SELECT {col_bit}, {col_value} FROM gamestates WHERE {id_server} = %s AND {id_state} = %s".format(

						id_state = ewcfg.col_id_state,
						id_server = ewcfg.col_id_server,
						col_bit = ewcfg.col_bit,
						col_value = ewcfg.col_value
					),(
						self.id_server,
						self.id_state
					))
				# Retrieve data if the object was found
				if len(data) > 0:
					self.id_state = id_state
					self.bit = data[0][0]
					self.value = data[0][1]
				else:
					self.bit = None

			except:
				ewutils.logMsg("Failed to retrieve gamestate {} from database.".format(self.id_state))
	def persist(self):
		bknd_core.execute_sql_query(
			"REPLACE INTO gamestates ({id_server}, {id_state},  {col_bit}, {col_value}) VALUES (%s, %s, %s, %s)".format(
				id_server=ewcfg.col_id_server,
				id_state = ewcfg.col_id_state,
				col_bit=ewcfg.col_bit,
				col_value=ewcfg.col_value
			), (
				self.id_server,
				self.id_state,
				self.bit,
				self.value
			))


