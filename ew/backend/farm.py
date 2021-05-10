import asyncio
import random
import time

from . import core as bknd_core
from ..static import cfg as ewcfg
from ..static import farm as farm_static
from ..utils import core as ewutils


class EwFarm:
	id_server = -1
	id_user = -1
	name = ""
	time_lastsow = 0
	phase = 0
	time_lastphase = 0
	slimes_onreap = 0
	action_required = 0
	crop = ""
	# player's life state at sow
	sow_life_state = 0

	def __init__(
		self,
		id_server = None,
		id_user = None,
		farm = None
	):
		if id_server is not None and id_user is not None and farm is not None:
			self.id_server = id_server
			self.id_user = id_user
			self.name = farm

			data = bknd_core.execute_sql_query(
				"SELECT {time_lastsow}, {phase}, {time_lastphase}, {slimes_onreap}, {action_required}, {crop}, {life_state} FROM farms WHERE id_server = %s AND id_user = %s AND {col_farm} = %s".format(
					time_lastsow = ewcfg.col_time_lastsow,
					col_farm = ewcfg.col_farm,
					phase = ewcfg.col_phase,
					time_lastphase = ewcfg.col_time_lastphase,
					slimes_onreap = ewcfg.col_slimes_onreap,
					action_required = ewcfg.col_action_required,
					crop = ewcfg.col_crop,
					life_state = ewcfg.col_sow_life_state,
				), (
					id_server,
					id_user,
					farm
				)
			)

			if len(data) > 0:  # if data is not empty, i.e. it found an entry
				# data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
				self.time_lastsow = data[0][0]
				self.phase = data[0][1]
				self.time_lastphase = data[0][2]
				self.slimes_onreap = data[0][3]
				self.action_required = data[0][4]
				self.crop = data[0][5]
				self.sow_life_state = data[0][6]

			else:  # create new entry
				bknd_core.execute_sql_query(
					"REPLACE INTO farms (id_server, id_user, {col_farm}) VALUES (%s, %s, %s)".format(
						col_farm = ewcfg.col_farm
					), (
						id_server,
						id_user,
						farm
					)
				)

	def persist(self):
		bknd_core.execute_sql_query(
			"REPLACE INTO farms(id_server, id_user, {farm}, {time_lastsow}, {phase}, {time_lastphase}, {slimes_onreap}, {action_required}, {crop}, {life_state}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
				farm = ewcfg.col_farm,
				time_lastsow = ewcfg.col_time_lastsow,
				phase = ewcfg.col_phase,
				time_lastphase = ewcfg.col_time_lastphase,
				slimes_onreap = ewcfg.col_slimes_onreap,
				action_required = ewcfg.col_action_required,
				crop = ewcfg.col_crop,
				life_state = ewcfg.col_sow_life_state,
			), (
				self.id_server,
				self.id_user,
				self.name,
				self.time_lastsow,
				self.phase,
				self.time_lastphase,
				self.slimes_onreap,
				self.action_required,
				self.crop,
				self.sow_life_state,
			)
		)

async def farm_tick_loop(id_server):
	while not ewutils.TERMINATE:
		await asyncio.sleep(ewcfg.farm_tick_length)
		farm_tick(id_server)


def farm_tick(id_server):
	time_now = int(time.time())
	farms = bknd_core.execute_sql_query("SELECT {id_user}, {farm} FROM farms WHERE id_server = %s AND {time_lastsow} > 0 AND {phase} < %s".format(
		id_user = ewcfg.col_id_user,
		farm = ewcfg.col_farm,
		time_lastsow = ewcfg.col_time_lastsow,
		phase = ewcfg.col_phase,
	),(
		id_server,
		ewcfg.farm_phase_reap,
	))

	for row in farms:
		farm_data = EwFarm(id_server = id_server, id_user = row[0], farm = row[1])

		time_nextphase = ewcfg.time_nextphase

		# gvs - juvie's last farming phase lasts 10 minutes
		if farm_data.sow_life_state in [ewcfg.life_state_juvenile, ewcfg.farm_life_state_juviethumb] and farm_data.phase == (ewcfg.farm_phase_reap_juvie - 1):
			time_nextphase = ewcfg.time_lastphase_juvie

		if farm_data.sow_life_state in [ewcfg.farm_life_state_juviethumb, ewcfg.farm_life_state_thumb]:
			time_nextphase /= 1.5


		if time_now >= farm_data.time_lastphase + time_nextphase:
			farm_data.phase += 1
			farm_data.time_lastphase = time_now

			# gvs - juvies only have 5 farming phases
			if farm_data.sow_life_state in [ewcfg.life_state_juvenile, ewcfg.farm_life_state_juviethumb] and farm_data.phase == ewcfg.farm_phase_reap_juvie:
				farm_data.phase = ewcfg.farm_phase_reap
				
			if farm_data.phase < ewcfg.farm_phase_reap:
				farm_data.action_required = random.choice(farm_static.farm_action_ids)
			else:
				farm_data.action_required = ewcfg.farm_action_none
			farm_data.persist()
