
import time

from ..static import cfg as ewcfg
from ..static import poi as poi_static

from ..backend import core as bknd_core

from .. import move as ewmap

from . import core as ewutils

from ..backend.district import EwDistrict
from ..backend.market import EwMarket
from ..backend.dungeons import EwGamestate

def get_subzone_controlling_faction(subzone_id, id_server):
	
	subzone = poi_static.id_to_poi.get(subzone_id)
	
	if subzone == None:
		return
	else:
		if not subzone.is_subzone:
			return
	
	mother_pois = subzone.mother_districts

	# Get all the mother pois of a subzone in order to find the father poi, which is either one of the mother pois or the father poi of the mother poi
	# Subzones such as the food court will have both a district poi and a street poi as one of their mother pois
	district_data = None

	for mother_poi in mother_pois:
		
		mother_poi_data = poi_static.id_to_poi.get(mother_poi)
		
		if mother_poi_data.is_district:
			# One of the mother pois was a district, get its controlling faction
			district_data = EwDistrict(district=mother_poi, id_server=id_server)
			break
		else:
			# One of the mother pois was a street, get the father district of that street and its controlling faction
			father_poi = mother_poi_data.father_district
			district_data = EwDistrict(district=father_poi, id_server=id_server)
			break

	if district_data != None:
		faction = district_data.controlling_faction
		return faction

def get_street_list(str_poi):
	poi = poi_static.id_to_poi.get(str_poi)
	neighbor_list = poi.neighbors
	poi_list = []
	if poi.is_district == False:
		return poi_list
	else:
		for neighbor in neighbor_list.keys():
			neighbor_poi = poi_static.id_to_poi.get(neighbor)
			if neighbor_poi.is_street == True:
				poi_list.append(neighbor)
		return poi_list
	
def get_move_speed(user_data):
	time_now = int(time.time())
	mutations = user_data.get_mutations()
	statuses = user_data.getStatusEffects()
	market_data = EwMarket(id_server = user_data.id_server)
	#trauma = se_static.trauma_map.get(user_data.trauma)
	# disabled until held items update
	# move_speed = 1 + (user_data.speed / 50)
	move_speed = 1

	if user_data.life_state == ewcfg.life_state_shambler:
		if market_data.weather == ewcfg.weather_bicarbonaterain:
			move_speed *= 2
		else:
			move_speed *= 0.5

	#if ewcfg.status_injury_legs_id in statuses:
	#	status_data = EwStatusEffect(id_status = ewcfg.status_injury_legs_id, user_data = user_data)
	#	try:
	#		move_speed *= max(0, (1 - 0.2 * int(status_data.value) / 10))
	#	except:
	#		ewutils.logMsg("failed int conversion while getting move speed for user {}".format(user_data.id_user))

	#if (trauma != None) and (trauma.trauma_class == ewcfg.trauma_class_movespeed):
	#	move_speed *= max(0, (1 - 0.5 * user_data.degradation / 100))

	if ewcfg.mutation_id_organicfursuit in mutations and ewutils.check_fursuit_active(market_data):
		move_speed *= 2
	if (ewcfg.mutation_id_lightasafeather in mutations or ewcfg.mutation_id_airlock) in mutations and market_data.weather == "windy":
		move_speed *= 2
	if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() < 0.4:
		move_speed *= 1.33
		
	#TODO remove after double halloween
	#if user_data.life_state == ewcfg.life_state_corpse:
	#	move_speed *= 2

	move_speed = max(0.1, move_speed)

	return move_speed


def inaccessible(user_data = None, poi = None):

    if poi == None or user_data == None:
        return True

    if user_data.life_state == ewcfg.life_state_observer:
        return False

    if user_data.life_state == ewcfg.life_state_shambler and poi.id_poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown, ewcfg.poi_id_juviesrow]:
        return True


    elevatorstop = EwGamestate(id_server=user_data.id_server, id_state='elevator')

    for lock in ewcfg.lock_states:
        if poi in ewcfg.lock_states.get(lock) and user_data.poi in ewcfg.lock_states.get(lock):
            print(lock)
            gamestate = EwGamestate(id_server=user_data.id_server, id_state=lock)
            if gamestate.bit == 0 or elevatorstop.value not in ewcfg.lock_states.get(lock):
                return True

    bans = user_data.get_bans()
    vouchers = user_data.get_vouchers()

    locked_districts_list = ewmap.retrieve_locked_districts(user_data.id_server)

    if(
        len(poi.factions) > 0 and
        (set(vouchers).isdisjoint(set(poi.factions)) or user_data.faction != "") and
        user_data.faction not in poi.factions
    ) or (
        len(poi.life_states) > 0 and
        user_data.life_state not in poi.life_states
    ):
        return True
    elif(
        len(poi.factions) > 0 and
        len(bans) > 0 and
        set(poi.factions).issubset(set(bans))
    ):
        return True
    elif poi.id_poi in locked_districts_list and user_data.life_state not in [ewcfg.life_state_executive, ewcfg.life_state_lucky]:
        return True
    else:
        return False



async def degrade_districts(cmd):
	
	if not cmd.message.author.guild_permissions.administrator:
		return

	gvs_districts = []

	for poi in poi_static.poi_list:
		if poi.is_district and not poi.id_poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown, ewcfg.poi_id_juviesrow, ewcfg.poi_id_oozegardens, ewcfg.poi_id_thevoid]:
			gvs_districts.append(poi.id_poi)

	bknd_core.execute_sql_query("UPDATE districts SET degradation = 0")
	bknd_core.execute_sql_query("UPDATE districts SET time_unlock = 0")
	bknd_core.execute_sql_query("UPDATE districts SET degradation = 10000 WHERE district IN {}".format(tuple(gvs_districts)))
	ewutils.logMsg('Set proper degradation values.')


