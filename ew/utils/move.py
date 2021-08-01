import asyncio
import heapq
import math
import random
import time
from copy import deepcopy

from ew.backend import core as bknd_core
from ew.backend.dungeons import EwGamestate
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import poi as poi_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict

move_counter = 0

map_world = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 0
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 1
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 120, -3, -3, -3, -3, -2, 120, 0, 0, 0, 0, 0, 0, 0, 0, 120, -3, -3, -3, -3, -2, 120, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 2
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 60, -1, 60, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 60, -1, 60, -1, 60, -1, -1, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 3
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1],  # 4
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 120, -1, -1, -1, -1, -1, -1, -1],  # 5
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 60, -1, -1, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 0, 0, 0, -1, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1],  # 6
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -2, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -3, -1, -1, -1, -1, -1, -1, -1],  # 7
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -2, 30, 0, 0, 0, 0, 30, -2, 30, 0, 0, 0, 0, -1, -1, 60, -1, -1, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1],  # 8
    [-1, -1, -1, 120, -1, -1, -1, -1, -1, -1, -1, 0, 0, 30, -2, 30, 0, 0, 0, 0, 0, -1, 0, -1, -1, -1, 30, -1, -1, -1, 0, -1, -1, 30, -1, -1, -1, -1, 0, 0, 30, -2, 30, 0, 0, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1],  # 9
    [-1, -1, -1, -2, 60, 0, 0, 0, 0, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 60, -1, 0, 0, 0, 0, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, 30, -1, 0, -1, -1, -1, -1, -1, -1, -1],  # 10
    [-1, -1, -1, -3, -1, -1, -1, -1, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 30, -2, 30, 0, -1, -1, 0, -1, -1, 30, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -2, 60, 0, -1, -1, -1, -1, -1, -1, -1],  # 11
    [-1, -1, -1, -3, 60, 0, 0, 0, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, 0, 0, 0, -1, 30, -1, -1, -1, -1, 0, -1, -1, -2, 30, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 12
    [-1, -1, -1, -3, -1, -1, -1, 0, -1, 0, -1, 30, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, 0, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 13
    [-1, -1, -1, -3, 60, 0, -1, 0, -1, 0, 60, -2, 30, 0, 0, 0, 0, 30, -2, -1, -1, -1, 0, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, 0, 0, 30, -2, 30, 0, 0, 0, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 14
    [-1, -1, -1, 120, -1, 0, -1, 0, -1, -1, -1, 30, -1, -1, -1, 0, -1, -1, 30, -1, -1, -1, 0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, 30, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 15
    [-1, -1, -1, 0, -1, 0, -1, 0, -1, -1, -1, 0, -1, -1, -1, 30, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0, 0, 30, -2, 30, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 30, -2, 30, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 16
    [-1, -1, -1, 0, -1, 0, -1, 0, -1, 0, 0, 0, 0, 0, 30, -2, -1, -1, 0, -1, -1, -1, 30, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 17
    [-1, -1, -1, 0, -1, 0, -1, 0, -1, 30, -1, -1, -1, -1, -1, 30, -1, -1, 0, 0, 0, 30, -2, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 18
    [-1, -1, -1, 0, -1, 0, -1, 0, 60, -2, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, 0, -1, 0, 0, 0, 30, -2, 30, 0, 0, 0, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 19
    [-1, -1, -1, 0, -1, 0, -1, -1, -1, 30, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, 30, -1, 30, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 20
    [-1, -1, -1, 0, -1, 0, -1, -1, -1, 0, 0, 0, 0, 30, -2, 30, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0, 0, 30, -2, -3, -3, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, 0, 0, 30, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 21
    [-1, -1, -1, 0, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, 30, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 30, -1, -3, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 22
    [-1, -1, -1, 0, -1, 0, -1, -1, -1, 0, -1, -1, -1, -1, 0, -1, 30, -1, -1, 0, -1, -1, -1, -1, 0, 0, 0, 0, 0, -1, -3, -1, -1, -1, -1, -1, 30, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 23
    [-1, -1, -1, 0, -1, 0, -1, -1, -1, 30, 30, 0, 0, 0, 0, 30, -2, -1, -1, 0, 30, -2, 30, 0, 0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 24
    [-1, -1, -1, 0, -1, 0, 0, 0, 60, -2, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, 30, -1, -1, 0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 25
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, 30, 0, 0, 0, 30, -2, 30, 0, 30, -1, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -2, 30, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 26
    [-1, -1, -1, 0, -1, -1, -1, -1, -1, -1, 30, -1, -1, -1, 60, -1, -1, -2, 30, 0, 0, 0, -1, -1, 30, -1, 0, 0, 0, 0, 30, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 27
    [-1, -1, -1, 0, -1, -1, 0, 0, 0, 60, -2, -1, -1, -1, 0, -1, -1, 60, -1, 0, -1, -1, 0, 30, -2, 30, 0, -1, -1, -1, -1, -1, 30, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 28
    [-1, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, 0, -1, 30, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, 60, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 29
    [-1, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, 0, -1, -2, 30, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 30, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 30
    [-1, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, 0, -1, 60, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 31
    [-1, -1, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, 0, -1, 0, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 32
    [-1, -1, -1, 0, -1, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0, -1, 0, -1, -1, 0, 30, -2, 30, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 33
    [-1, -1, -1, 0, -1, -1, 0, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, 0, -1, -1, -1, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 34
    [-1, -1, -1, 0, -1, -1, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 35
    [-1, -1, -1, 0, -1, -1, 60, -1, 60, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, 60, -1, 60, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 36
    [-1, -1, -1, 0, 0, 120, -2, -3, -3, -3, -3, 120, 0, 0, 0, 0, 0, 0, 120, -2, -3, -3, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 37
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 38
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2],  # 39
]
map_width = len(map_world[0])
map_height = len(map_world)

sem_wall = -1
sem_city = -2
sem_city_alias = -3

landmarks = {}

"""
    Returns true if the specified point of interest is a PvP zone.
"""


def poi_is_pvp(poi_name = None):
    poi = poi_static.id_to_poi.get(poi_name)

    if poi != None:
        return poi.pvp

    return False


"""
    Directions and cost from coord to arrive at a destination.
"""


class EwPath:
    visited = None
    steps = None
    cost = 0
    iters = 0
    pois_visited = None

    def __init__(
            self,
            path_from = None,
            steps = [],
            cost = 0,
            visited = {},
            pois_visited = None
    ):
        if path_from != None:
            self.steps = deepcopy(path_from.steps)
            self.cost = path_from.cost
            self.visited = deepcopy(path_from.visited)
            self.pois_visited = deepcopy(path_from.pois_visited)
        else:
            self.steps = steps
            self.cost = cost
            self.visited = visited
            if pois_visited == None:
                self.pois_visited = set()
            else:
                self.pois_visited = pois_visited


"""
    Add coord_next to the path.
"""


def path_step(path, poi_next, cost_next, user_data, poi_end, landmark_mode = False):
    next_poi = poi_next

    if inaccessible(user_data=user_data, poi=next_poi):
        return False
    else:
        # check if we already got the movement bonus/malus for this district
        if not poi_next.id_poi in path.pois_visited:
            path.pois_visited.add(next_poi.id_poi)
            if len(user_data.faction) > 0 and next_poi.id_poi != poi_end.id_poi and next_poi.id_poi != path.steps[0].id_poi:
                district = EwDistrict(
                    id_server=user_data.id_server,
                    district=next_poi.id_poi
                )

                if district != None and len(district.controlling_faction) > 0:
                    if user_data.faction == district.controlling_faction:
                        cost_next -= ewcfg.territory_time_gain
                    else:
                        cost_next += ewcfg.territory_time_gain
                # Slimecorp gets a bonus in unclaimed territory
                elif user_data.faction == ewcfg.faction_slimecorp:
                    cost_next -= ewcfg.territory_time_gain

    path.steps.append(poi_next)

    if landmark_mode and cost_next > ewcfg.territory_time_gain:
        cost_next -= ewcfg.territory_time_gain

    path.cost += cost_next

    return True


"""
    Returns a new path including all of path_base, with the next step coord_next.
"""


def path_branch(path_base, poi_next, cost_next, user_data, poi_end, landmark_mode = False):
    path_next = EwPath(path_from=path_base)

    if path_step(path_next, poi_next, cost_next, user_data, poi_end, landmark_mode) == False:
        return None

    return path_next


def score_map_from(
        poi_start = None,
        user_data = None,
        landmark_mode = False
):
    score_golf = math.inf
    score_map = {}
    for poi in poi_static.poi_list:
        score_map[poi.id_poi] = score_golf

    paths_finished = []
    paths_walking = []

    poi_start = poi_static.id_to_poi.get(poi_start)
    poi_end = None
    poi_end = None

    path_base = EwPath(
        steps=[poi_start],
        cost=0,
        pois_visited={poi_start.id_poi},
    )

    paths_walking.append(path_base)

    count_iter = 0
    while len(paths_walking) > 0:
        count_iter += 1

        paths_walking_new = []

        for path in paths_walking:
            step_last = path.steps[-1]
            score_current = score_map.get(step_last.id_poi)
            if path.cost >= score_current:
                continue

            score_map[step_last.id_poi] = path.cost

            step_penult = path.steps[-2] if len(path.steps) >= 2 else None

            path_base = path
            neighs = list(step_last.neighbors.keys())

            if step_penult != None and step_penult.id_poi in neighs:
                neighs.remove(step_penult.id_poi)

            num_neighbors = len(neighs)
            for i in range(num_neighbors):

                neigh = poi_static.id_to_poi.get(neighs[i])
                neigh_cost = step_last.neighbors.get(neigh.id_poi)

                if neigh_cost == None:
                    continue

                if i < num_neighbors - 1:
                    branch = path_branch(path_base, neigh, neigh_cost, user_data, poi_end, landmark_mode)
                    if branch != None:
                        paths_walking_new.append(branch)

                else:
                    if path_step(path_base, neigh, neigh_cost, user_data, poi_end, landmark_mode):
                        paths_walking_new.append(path_base)

        paths_walking = paths_walking_new

    return score_map


def path_to(
        poi_start = None,
        poi_end = None,
        user_data = None
):
    # ewutils.logMsg("beginning pathfinding")
    score_golf = math.inf
    score_map = {}
    for poi in poi_static.poi_list:
        score_map[poi.id_poi] = math.inf

    paths_finished = []
    paths_walking = []

    pois_adjacent = []

    poi_start = poi_static.id_to_poi.get(poi_start)
    poi_end = poi_static.id_to_poi.get(poi_end)

    path_base = EwPath(
        steps=[poi_start],
        cost=0,
        pois_visited={poi_start.id_poi},
    )

    path_id = 0
    heapq.heappush(paths_walking, (path_base.cost + landmark_heuristic(path_base, poi_end), path_id, path_base))
    path_id += 1

    count_iter = 0
    while len(paths_walking) > 0:
        count_iter += 1

        path_tuple = heapq.heappop(paths_walking)

        path = path_tuple[-1]

        if path is not None:
            step_last = path.steps[-1]
            score_current = score_map.get(step_last.id_poi)
            if poi_end is not None and not poi_start.is_outskirts and not poi_end.is_outskirts and step_last.is_outskirts and poi_end.id_poi != 'temple':
                # do not go through outskirts if the start and destination aren't part of them
                continue
            if path.cost >= score_current:
                continue
            if user_data.life_state != ewcfg.life_state_corpse and (poi_end and poi_end.id_poi != step_last.id_poi == ewcfg.poi_id_thesewers):
                # can't route through the sewers unless you're dead
                continue

            score_map[step_last.id_poi] = path.cost
            # ewutils.logMsg("visiting " + str(step_last))

            step_penult = path.steps[-2] if len(path.steps) >= 2 else None

            if poi_end != None:
                # Arrived at the actual destination?
                if step_last.id_poi == poi_end.id_poi:
                    path_final = path
                    if path_final.cost < score_golf:
                        score_golf = path_final.cost
                        paths_finished = []
                    if path_final.cost <= score_golf:
                        paths_finished.append(path_final)
                    break

            else:
                # Looking for adjacent points of interest.
                poi_adjacent = step_last

                if poi_adjacent.id_poi != poi_start.id_poi:
                    pois_adjacent.append(poi_adjacent)
                    continue

            path_base = path
            neighs = list(step_last.neighbors.keys())

            if step_penult != None and step_penult.id_poi in neighs:
                neighs.remove(step_penult.id_poi)

            num_neighbors = len(neighs)
            i = 0
            for i in range(num_neighbors):

                neigh = poi_static.id_to_poi.get(neighs[i])
                neigh_cost = step_last.neighbors.get(neigh.id_poi)

                if neigh_cost == None:
                    continue

                if i < num_neighbors - 1:
                    branch = path_branch(path_base, neigh, neigh_cost, user_data, poi_end)
                    if branch != None:
                        heapq.heappush(paths_walking, (branch.cost + landmark_heuristic(branch, poi_end), path_id, branch))
                        path_id += 1
                else:
                    if path_step(path_base, neigh, neigh_cost, user_data, poi_end):
                        heapq.heappush(paths_walking, (path_base.cost + landmark_heuristic(path_base, poi_end), path_id, path_base))
                        path_id += 1

    # ewutils.logMsg("finished pathfinding")

    if poi_end != None:
        path_true = None
        if len(paths_finished) > 0:
            path_true = paths_finished[0]
            path_true.iters = count_iter
        if path_true is None:
            ewutils.logMsg("Could not find a path.")
        return path_true
    else:
        return pois_adjacent


def landmark_heuristic(path, poi_end):
    if len(landmarks) == 0 or poi_end is None:
        return 0
    else:
        last_step = path.steps[-1]
        scores = []
        for lm in landmarks:
            score_map = landmarks.get(lm)
            score_path = score_map.get(last_step.id_poi)
            score_goal = score_map.get(poi_end.id_poi)
            scores.append(abs(score_path - score_goal))

        return max(scores)


"""
    Debug method to draw the map, optionally with a path/route on it.
"""


def map_draw(path = None, coord = None):
    y = 0
    for row in map_world:
        outstr = ""
        x = 0

        for col in row:
            if col == sem_wall:
                col = "  "
            elif col == sem_city:
                col = "CT"
            elif col == sem_city_alias:
                col = "ct"
            elif col == 0:
                col = "██"
            elif col == 30:
                col = "[]"
            elif col == 20:
                col = "••"
            elif col == 60:
                col = "<>"
            elif col == 120:
                col = "=="

            if path != None:
                visited_set_y = path.visited.get(x)
                if visited_set_y != None and visited_set_y.get(y) != None:
                    col = "." + col[-1]

            if coord != None and coord == (x, y):
                col = "O" + col[-1]

            outstr += "{}".format(col)
            x += 1

        print(outstr)
        y += 1


def inaccessible(user_data = None, poi = None):
    if poi == None or user_data == None:
        return True

    if user_data.life_state == ewcfg.life_state_observer:
        return False

    if user_data.life_state == ewcfg.life_state_shambler and poi.id_poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown, ewcfg.poi_id_juviesrow]:
        return True

    source_poi = poi_static.id_to_poi.get(user_data.poi)

    # locks that inhibit a POI
    for lock in ewcfg.region_lock_states:
        if poi.id_poi == lock:
            for state in ewcfg.region_lock_states.get(lock):
                gamestate = EwGamestate(id_server=user_data.id_server, id_state=state)
                if gamestate.bit == 0:
                    return True

    bans = user_data.get_bans()
    vouchers = user_data.get_vouchers()

    locked_districts_list = poi_utils.retrieve_locked_districts(user_data.id_server)

    if (
            len(poi.factions) > 0 and
            (set(vouchers).isdisjoint(set(poi.factions)) or user_data.faction != "") and
            user_data.faction not in poi.factions
    ) or (
            len(poi.life_states) > 0 and
            user_data.life_state not in poi.life_states
    ):
        return True
    elif (
            len(poi.factions) > 0 and
            len(bans) > 0 and
            set(poi.factions).issubset(set(bans))
    ):
        return True
    elif poi.id_poi in locked_districts_list and user_data.life_state not in [ewcfg.life_state_executive, ewcfg.life_state_lucky]:
        return True
    else:
        return False


"""
    Kicks idle players from subzones. Called every 15 minutes.
"""


async def kick(id_server):
    # Gets data for all living players from the database
    all_living_players = bknd_core.execute_sql_query("SELECT {poi}, {id_user} FROM users WHERE id_server = %s AND {life_state} > 0 AND {time_last_action} < %s".format(
        poi=ewcfg.col_poi,
        id_user=ewcfg.col_id_user,
        time_last_action=ewcfg.col_time_last_action,
        life_state=ewcfg.col_life_state
    ), (
        id_server,
        (int(time.time()) - ewcfg.time_kickout)
    ))

    client = ewutils.get_client()

    for player in all_living_players:
        try:
            poi = poi_static.id_to_poi[player[0]]
            id_user = player[1]
            user_data = EwUser(id_user=id_user, id_server=id_server)

            # checks if the player should be kicked from the subzone and kicks them if they should.
            if poi.is_subzone and poi.id_poi not in [ewcfg.poi_id_thesphere, ewcfg.poi_id_thebreakroom]:

                # Some subzones could potentially have multiple mother districts.
                # Make sure to get one that's accessible before attempting a proper kickout.
                mother_district_chosen = random.choice(poi.mother_districts)

                if inaccessible(user_data=user_data, poi=poi_static.id_to_poi.get(mother_district_chosen)):
                    # If the randomly chosen mother district is inaccessible, make one more attempt.
                    mother_district_chosen = random.choice(poi.mother_districts)
                else:
                    pass

                if not inaccessible(user_data=user_data, poi=poi_static.id_to_poi.get(mother_district_chosen)):

                    if user_data.life_state not in [ewcfg.life_state_kingpin, ewcfg.life_state_lucky, ewcfg.life_state_executive] and user_data.id_user != 799933061080416266:
                        server = ewcfg.server_list[id_server]
                        member_object = server.get_member(id_user)

                        user_data.poi = mother_district_chosen
                        user_data.time_lastenter = int(time.time())
                        user_data.persist()
                        await ewrolemgr.updateRoles(client=client, member=member_object)
                        await user_data.move_inhabitants(id_poi=mother_district_chosen)
                        mother_district_channel = fe_utils.get_channel(server, poi_static.id_to_poi[mother_district_chosen].channel)
                        response = "You have been kicked out for loitering! You can only stay in a sub-zone and twiddle your thumbs for 1 hour at a time."
                        await fe_utils.send_message(client, mother_district_channel, fe_utils.formatMessage(member_object, response))
        except:
            ewutils.logMsg('failed to move inactive player out of subzone with poi {}: {}'.format(player[0], player[1]))


async def send_gangbase_messages(server_id, clock):
    # this can be added onto for events and such
    lucky_lucy = 0
    casino_response = "**Lucky Lucy has arrived!** Now's the time to make your fortune!"
    casino_end = "Aww, Lucy left."

    response = ""
    if clock == 3:
        response = "The police are probably asleep, the lazy fucks. It's a good time for painting the town!"
    elif clock == 11:
        response = "Spray time's over, looks like the cops are back out. Fuck those guys."
    if random.randint(1, 50) == 2:
        lucky_lucy = 1

    client = ewutils.get_client()
    server = client.get_guild(server_id)
    channels = ewcfg.hideout_channels
    casino_channel = fe_utils.get_channel(server=server, channel_name=ewcfg.channel_casino)

    if response != "":
        for channel in channels:
            post_channel = fe_utils.get_channel(server, channel)
            await fe_utils.send_message(client, post_channel, response)
    if lucky_lucy == 1:
        await fe_utils.send_message(client, casino_channel, casino_response)
        await asyncio.sleep(300)
        await fe_utils.send_message(client, casino_channel, casino_end)


"""
    Find the cost to move through ortho-adjacent cells.
"""


# unused
def neighbors(coord):
    neigh = []

    if coord[1] > 0 and map_world[coord[1] - 1][coord[0]] != sem_wall:
        neigh.append((coord[0], coord[1] - 1))
    if coord[1] < (map_height - 1) and map_world[coord[1] + 1][coord[0]] != sem_wall:
        neigh.append((coord[0], coord[1] + 1))

    if coord[0] > 0 and map_world[coord[1]][coord[0] - 1] != sem_wall:
        neigh.append((coord[0] - 1, coord[1]))
    if coord[0] < (map_width - 1) and map_world[coord[1]][coord[0] + 1] != sem_wall:
        neigh.append((coord[0] + 1, coord[1]))

    return neigh
