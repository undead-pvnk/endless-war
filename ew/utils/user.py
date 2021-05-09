import time

from ew.utils import core as ewutils
from ew.static import cfg as ewcfg

from ew.backend.market import EwMarket



def get_move_speed(user_data):
	time_now = int(time.time())
	mutations = user_data.get_mutations()
	statuses = user_data.getStatusEffects()
	market_data = EwMarket(id_server=user_data.id_server)
	# trauma = se_static.trauma_map.get(user_data.trauma)
	# disabled until held items update
	# move_speed = 1 + (user_data.speed / 50)
	move_speed = 1

	if user_data.life_state == ewcfg.life_state_shambler:
		if market_data.weather == ewcfg.weather_bicarbonaterain:
			move_speed *= 2
		else:
			move_speed *= 0.5

	# if ewcfg.status_injury_legs_id in statuses:
	#	status_data = EwStatusEffect(id_status = ewcfg.status_injury_legs_id, user_data = user_data)
	#	try:
	#		move_speed *= max(0, (1 - 0.2 * int(status_data.value) / 10))
	#	except:
	#		ewutils.logMsg("failed int conversion while getting move speed for user {}".format(user_data.id_user))

	# if (trauma != None) and (trauma.trauma_class == ewcfg.trauma_class_movespeed):
	#	move_speed *= max(0, (1 - 0.5 * user_data.degradation / 100))

	if ewcfg.mutation_id_organicfursuit in mutations and ewutils.check_fursuit_active(market_data):
		move_speed *= 2
	if (
			ewcfg.mutation_id_lightasafeather in mutations or ewcfg.mutation_id_airlock) in mutations and market_data.weather == "windy":
		move_speed *= 2
	if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() < 0.4:
		move_speed *= 1.33

	# TODO remove after double halloween
	# if user_data.life_state == ewcfg.life_state_corpse:
	#	move_speed *= 2

	move_speed = max(0.1, move_speed)

	return move_speed
