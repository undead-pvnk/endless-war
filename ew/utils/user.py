import time

from . import core as ewutils
from ..backend.market import EwMarket
from ..static import cfg as ewcfg


def get_move_speed(user_data):
    time_now = int(time.time())
    mutations = user_data.get_mutations()
    statuses = user_data.getStatusEffects()
    market_data = EwMarket(id_server=user_data.id_server)
    # trauma = se_static.trauma_map.get(user_data.trauma)
    # disabled until held items update
    # move_speed = 1 + (user_data.speed / 50)
    move_speed = 1

    if ewcfg.mutation_id_organicfursuit in mutations and ewutils.check_moon_phase(market_data) == ewcfg.moon_full:
        move_speed *= 2
    if (ewcfg.mutation_id_lightasafeather in mutations or ewcfg.mutation_id_airlock in mutations) and market_data.weather == "windy":
        move_speed *= 2
    if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() < 0.4:
        move_speed *= 1.33

    if user_data.life_state == ewcfg.life_state_corpse and ewcfg.dh_active:
        move_speed *= 2

    move_speed = max(0.1, move_speed)
    if ewutils.DEBUG == True:
        move_speed *= 2
        #move_speed = 12


    return move_speed
