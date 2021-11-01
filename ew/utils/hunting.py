import random
import time

from . import core as ewutils
from . import frontend as fe_utils
from . import slimeoid as slimeoid_utils
from .district import EwDistrict
from .frontend import EwResponseContainer
from ..backend import core as bknd_core
from ..backend import hunting as bknd_hunt
from ..backend.hunting import EwEnemyBase as EwEnemy
from ..backend.hunting import EwOperationData
from ..backend.market import EwMarket
from ..static import cfg as ewcfg
from ..static import items as static_items
from ..static import poi as poi_static


def gvs_create_gaia_grid_mapping(user_data):
    grid_map = {}

    # Grid print mapping and shambler targeting use different priority lists. Don't get these mixed up
    printgrid_low_priority = [ewcfg.enemy_type_gaia_rustealeaves]
    printgrid_mid_priority = [ewcfg.enemy_type_gaia_steelbeans]
    printgrid_high_priority = []
    for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
        if enemy_id not in printgrid_low_priority and enemy_id not in printgrid_mid_priority:
            printgrid_high_priority.append(enemy_id)

    gaias = bknd_core.execute_sql_query(
        "SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1 AND {enemyclass} = %s".format(
            id_enemy=ewcfg.col_id_enemy,
            enemytype=ewcfg.col_enemy_type,
            poi=ewcfg.col_enemy_poi,
            life_state=ewcfg.col_enemy_life_state,
            gvs_coord=ewcfg.col_enemy_gvs_coord,
            enemyclass=ewcfg.col_enemy_class,
        ), (
            user_data.id_server,
            user_data.poi,
            ewcfg.enemy_class_gaiaslimeoid
        ))

    grid_conditions = bknd_core.execute_sql_query(
        "SELECT coord, grid_condition FROM gvs_grid_conditions WHERE district = %s".format(
        ), (
            user_data.poi,
        ))

    for condition in grid_conditions:
        grid_map[condition[0]] = condition[1]

    for gaia in gaias:
        try:
            gaia_in_coord = grid_map[gaia[2]]
            # No key error: Gaia is in coord already, check for priority
            is_filled = True
        except KeyError:
            gaia_in_coord = ''
            # Key error: Gaia was not in coord
            is_filled = False

        if is_filled:
            if gaia_in_coord in printgrid_low_priority and (gaia[1] in printgrid_mid_priority or gaia[1] in printgrid_high_priority):
                grid_map[gaia[2]] = gaia[1]
            if gaia_in_coord in printgrid_mid_priority and gaia[1] in printgrid_high_priority:
                grid_map[gaia[2]] = gaia[1]
        else:
            grid_map[gaia[2]] = gaia[1]

    return grid_map


def gvs_create_gaia_lane_mapping(user_data, row_used):
    # Grid print mapping and shambler targeting use different priority lists. Don't get these mixed up
    printlane_low_priority = [ewcfg.enemy_type_gaia_rustealeaves]
    printlane_mid_priority = []
    printlane_high_priority = [ewcfg.enemy_type_gaia_steelbeans]
    for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
        if enemy_id not in printlane_low_priority and enemy_id not in printlane_high_priority:
            printlane_mid_priority.append(enemy_id)

    gaias = bknd_core.execute_sql_query(
        "SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} IN %s".format(
            id_enemy=ewcfg.col_id_enemy,
            enemytype=ewcfg.col_enemy_type,
            poi=ewcfg.col_enemy_poi,
            life_state=ewcfg.col_enemy_life_state,
            gvs_coord=ewcfg.col_enemy_gvs_coord,
            enemyclass=ewcfg.col_enemy_class,
        ), (
            user_data.id_server,
            user_data.poi,
            ewcfg.enemy_class_gaiaslimeoid,
            tuple(row_used)
        ))

    grid_conditions = bknd_core.execute_sql_query(
        "SELECT coord, grid_condition FROM gvs_grid_conditions WHERE district = %s AND coord IN %s".format(
        ), (
            user_data.poi,
            tuple(row_used)
        ))

    coord_sets = []

    for coord in row_used:
        current_coord_set = []
        for enemy in printlane_low_priority:
            for gaia in gaias:
                if gaia[1] == enemy and gaia[2] == coord:
                    current_coord_set.append(gaia[0])

        for enemy in printlane_mid_priority:
            for gaia in gaias:
                if gaia[1] == enemy and gaia[2] == coord:
                    current_coord_set.append(gaia[0])

        for enemy in printlane_high_priority:
            for gaia in gaias:
                if gaia[1] == enemy and gaia[2] == coord:
                    current_coord_set.append(gaia[0])

        for condition in grid_conditions:
            if condition[0] == coord:
                if condition[1] == 'frozen':
                    current_coord_set.append('frozen')

        coord_sets.append(current_coord_set)

    return coord_sets


def gvs_check_gaia_protected(enemy_data):
    is_protected = False

    low_attack_priority = [ewcfg.enemy_type_gaia_rustealeaves]
    high_attack_priority = [ewcfg.enemy_type_gaia_steelbeans]
    mid_attack_priority = []
    for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
        if enemy_id not in low_attack_priority and enemy_id not in high_attack_priority:
            mid_attack_priority.append(enemy_id)

    checked_coords = []
    enemy_coord = enemy_data.gvs_coord
    for row in ewcfg.gvs_valid_coords_gaia:
        if enemy_coord in row:
            index = row.index(enemy_coord)
            row_length = len(ewcfg.gvs_valid_coords_gaia)
            for i in range(index + 1, row_length):
                checked_coords.append(ewcfg.gvs_valid_coords_gaia[i])

    gaias_in_front_coords = bknd_core.execute_sql_query(
        "SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} IN %s".format(
            id_enemy=ewcfg.col_id_enemy,
            enemytype=ewcfg.col_enemy_type,
            life_state=ewcfg.col_enemy_life_state,
            gvs_coord=ewcfg.col_enemy_gvs_coord,
            enemyclass=ewcfg.col_enemy_class,
        ), (
            ewcfg.enemy_class_gaiaslimeoid,
            tuple(checked_coords)
        ))

    if len(gaias_in_front_coords) > 0:
        is_protected = True
    else:
        gaias_in_same_coord = bknd_core.execute_sql_query(
            "SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE {life_state} = 1 AND {enemyclass} = %s AND {gvs_coord} = %s".format(
                id_enemy=ewcfg.col_id_enemy,
                enemytype=ewcfg.col_enemy_type,
                life_state=ewcfg.col_enemy_life_state,
                gvs_coord=ewcfg.col_enemy_gvs_coord,
                enemyclass=ewcfg.col_enemy_class,
            ), (
                ewcfg.enemy_class_gaiaslimeoid,
                enemy_coord
            ))
        if len(gaias_in_same_coord) > 1:
            same_coord_gaias_types = []
            for gaia in gaias_in_same_coord:
                same_coord_gaias_types.append(gaia[1])

            for type in same_coord_gaias_types:
                if enemy_data.enemy_type in high_attack_priority:
                    is_protected = False
                    break
                elif enemy_data.enemy_type in mid_attack_priority and type in high_attack_priority:
                    is_protected = True
                    break
                elif enemy_data.enemy_type in low_attack_priority and (type in mid_attack_priority or type in high_attack_priority):
                    is_protected = True
                    break

        else:
            is_protected = False

    return is_protected


def gvs_check_operation_duplicate(id_user, district, enemytype, faction):
    entry = None

    if faction == ewcfg.psuedo_faction_gankers:
        entry = bknd_core.execute_sql_query(
            "SELECT * FROM gvs_ops_choices WHERE id_user = %s AND district = %s AND enemytype = %s AND faction = %s".format(
            ), (
                id_user,
                district,
                enemytype,
                faction
            ))
    elif faction == ewcfg.psuedo_faction_shamblers:
        entry = bknd_core.execute_sql_query(
            "SELECT * FROM gvs_ops_choices WHERE district = %s AND enemytype = %s AND faction = %s".format(
            ), (
                district,
                enemytype,
                faction
            ))

    if len(entry) > 0:
        return True
    else:
        return False


def gvs_check_operation_limit(id_user, district, enemytype, faction):
    limit_hit = False
    tombstone_limit = 0

    if faction == ewcfg.psuedo_faction_gankers:
        data = bknd_core.execute_sql_query(
            "SELECT id_user FROM gvs_ops_choices WHERE id_user = %s AND district = %s AND faction = %s".format(
            ), (
                id_user,
                district,
                faction
            ))

        if len(data) >= 6:
            limit_hit = True
        else:
            limit_hit = False

    elif faction == ewcfg.psuedo_faction_shamblers:
        sh_data = bknd_core.execute_sql_query(
            "SELECT enemytype FROM gvs_ops_choices WHERE district = %s AND faction = %s".format(
            ), (
                district,
                faction
            ))

        gg_data = bknd_core.execute_sql_query(
            "SELECT id_user FROM gvs_ops_choices WHERE district = %s AND faction = %s".format(
            ), (
                district,
                enemytype,
            ))

        gg_id_list = []
        for gg in gg_data:
            gg_id_list.append(gg[0])

        gg_id_set = set(gg_id_list)  # Remove duplicate user IDs

        if len(gg_id_set) == 0:
            tombstone_limit = 3
        elif len(gg_id_set) <= 3:
            tombstone_limit = 6
        elif len(gg_id_set) <= 6:
            tombstone_limit = 10
        else:
            tombstone_limit = 12

        if len(sh_data) >= tombstone_limit:
            limit_hit = True
        else:
            limit_hit = False

    return limit_hit, tombstone_limit


def gvs_check_if_in_operation(user_data):
    op_data = bknd_core.execute_sql_query(
        "SELECT id_user, district FROM gvs_ops_choices WHERE id_user = %s".format(
        ), (
            user_data.id_user,
        ))

    if len(op_data) > 0:
        return True, op_data[0][1]
    else:
        return False, None


def gvs_get_gaias_from_coord(poi, checked_coord):
    gaias = bknd_core.execute_sql_query(
        "SELECT id_enemy, enemytype FROM enemies WHERE poi = %s AND gvs_coord = %s".format(
        ), (
            poi,
            checked_coord
        ))

    gaias_id_to_type_map = {}

    for gaia in gaias:
        if gaia[1] in ewcfg.gvs_enemies_gaiaslimeoids:
            gaias_id_to_type_map[gaia[0]] = gaia[1]

    return gaias_id_to_type_map


# If there are no player operations, spawn in ones that the bot uses
def gvs_insert_bot_ops(id_server, district, enemyfaction):
    bot_id = 56709

    if enemyfaction == ewcfg.psuedo_faction_gankers:
        possible_bot_types = [
            ewcfg.enemy_type_gaia_pinkrowddishes,
            ewcfg.enemy_type_gaia_purplekilliflower,
            ewcfg.enemy_type_gaia_poketubers,
            ewcfg.enemy_type_gaia_razornuts
        ]
        for type in possible_bot_types:
            bknd_core.execute_sql_query("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
                ewcfg.col_id_user,
                ewcfg.col_district,
                ewcfg.col_enemy_type,
                ewcfg.col_faction,
                ewcfg.col_id_item,
                ewcfg.col_shambler_stock,
            ), (
                bot_id,
                district,
                type,
                enemyfaction,
                -1,
                0,
            ))

            # To increase the challenge, a column of suganmanuts is placed down.
            for coord in ['A6', 'B6', 'C6', 'D6', 'E6']:
                spawn_enemy(
                    id_server=id_server,
                    pre_chosen_type=ewcfg.enemy_type_gaia_suganmanuts,
                    pre_chosen_level=50,
                    pre_chosen_poi=district,
                    pre_chosen_identifier='',
                    pre_chosen_faction=ewcfg.psuedo_faction_gankers,
                    pre_chosen_owner=bot_id,
                    pre_chosen_coord=coord,
                    manual_spawn=True,
                )

    elif enemyfaction == ewcfg.psuedo_faction_shamblers:
        possible_bot_types = [
            ewcfg.enemy_type_defaultshambler,
            ewcfg.enemy_type_bucketshambler,
        ]
        for type in possible_bot_types:
            bknd_core.execute_sql_query("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
                ewcfg.col_id_user,
                ewcfg.col_district,
                ewcfg.col_enemy_type,
                ewcfg.col_faction,
                ewcfg.col_id_item,
                ewcfg.col_shambler_stock,
            ), (
                bot_id,
                district,
                type,
                enemyfaction,
                -1,
                20,
            ))


# This function takes care of all win conditions within Gankers Vs. Shamblers.
# It also handles turn counters, including gaiaslime generation, as well as spawning in shamblers
async def gvs_update_gamestate(id_server):
    op_districts = bknd_core.execute_sql_query("SELECT district FROM gvs_ops_choices GROUP BY district")
    for op_district in op_districts:
        district = op_district[0]

        graveyard_ops = bknd_core.execute_sql_query(
            "SELECT id_user, enemytype, shambler_stock FROM gvs_ops_choices WHERE faction = 'shamblers' AND district = '{}' AND shambler_stock > 0".format(
                district))
        bot_garden_ops = bknd_core.execute_sql_query(
            "SELECT id_user, enemytype FROM gvs_ops_choices WHERE faction = 'gankers' AND district = '{}' AND id_user = 56709".format(
                district))
        op_district_data = EwDistrict(district=district, id_server=id_server)

        # Generate Gaiaslime passively over time, but in small amounts
        op_district_data.gaiaslime += 5
        op_district_data.persist()

        victor = None
        time_now = int(time.time())

        op_poi = poi_static.id_to_poi.get(district)
        client = ewutils.get_client()
        server = client.get_guild(id_server)
        channel = fe_utils.get_channel(server, op_poi.channel)

        if len(bot_garden_ops) > 0:
            if random.randrange(25) == 0:

                # random_op = random.choice(bot_garden_ops)
                # random_op_data = EwOperationData(id_user=random_op[0], district=district, enemytype=random_op[1])

                possible_bot_types = [
                    ewcfg.enemy_type_gaia_suganmanuts,
                    ewcfg.enemy_type_gaia_pinkrowddishes,
                    ewcfg.enemy_type_gaia_purplekilliflower,
                    ewcfg.enemy_type_gaia_poketubers,
                    ewcfg.enemy_type_gaia_razornuts
                ]

                possible_bot_coords = [
                    'A1', 'A2', 'A3', 'A4', 'A5',
                    'B1', 'B2', 'B3', 'B4', 'B5',
                    'C1', 'C2', 'C3', 'C4', 'C5',
                    'D1', 'D2', 'D3', 'D4', 'D5',
                    'E1', 'E2', 'E3', 'E4', 'E5'
                ]

                for i in range(5):
                    chosen_type = random.choice(possible_bot_types)
                    chosen_coord = random.choice(possible_bot_coords)

                    existing_gaias = gvs_get_gaias_from_coord(district, chosen_coord)

                    # If the coordinate is completely empty, spawn a gaiaslimeoid there.
                    # Otherwise, make up to 5 attempts when choosing random coordinates
                    if len(existing_gaias) == 0:
                        resp_cont = spawn_enemy(
                            id_server=id_server,
                            pre_chosen_type=chosen_type,
                            pre_chosen_level=50,
                            pre_chosen_poi=district,
                            pre_chosen_identifier='',
                            pre_chosen_faction=ewcfg.psuedo_faction_gankers,
                            pre_chosen_owner=56709,
                            pre_chosen_coord=chosen_coord,
                            manual_spawn=True,
                        )
                        await resp_cont.post()

                        break

        if len(graveyard_ops) > 0:

            # The chance for a shambler to spawn is inversely proportional to the amount of shamblers left in stock
            # The less shamblers there are left, the more likely they are to spawn
            current_stock = 0
            full_stock = 0

            for op in graveyard_ops:
                current_stock += op[2]
                full_stock += static_items.tombstone_fullstock_map[op[1]]

            # Example: If full_stock is 50, and current_stock is 20, then the spawn chance is 70%
            # ((1 - (20 / 50)) * 100) + 10 = 70

            shambler_spawn_chance = int(((1 - (current_stock / full_stock)) * 100) + 10)
            if random.randrange(100) + 1 < shambler_spawn_chance:

                random_op = random.choice(graveyard_ops)
                random_op_data = EwOperationData(id_user=random_op[0], district=district, enemytype=random_op[1])

                # Don't spawn if there aren't available identifiers
                if len(op_district_data.get_enemies_in_district(classes=[ewcfg.enemy_class_shambler])) < 26:
                    resp_cont = spawn_enemy(
                        id_server=id_server,
                        pre_chosen_type=random_op_data.enemytype,
                        pre_chosen_level=50,
                        pre_chosen_poi=district,
                        pre_chosen_faction=ewcfg.psuedo_faction_shamblers,
                        pre_chosen_owner=random_op_data.id_user,
                        pre_chosen_coord=random.choice(ewcfg.gvs_coords_start),
                        manual_spawn=True
                    )

                    random_op_data.shambler_stock -= 1
                    random_op_data.persist()

                    if random_op_data.shambler_stock == 0:
                        breakdown_response = "The tombstone spawning in {}s breaks down and collapses!".format(
                            random_op_data.enemytype.capitalize())
                        resp_cont.add_channel_response(channel, breakdown_response)
                    else:
                        random_op_data.persist()

                    await resp_cont.post()
        else:
            shamblers = bknd_core.execute_sql_query(
                "SELECT id_enemy FROM enemies WHERE enemyclass = '{}' AND poi = '{}'".format(ewcfg.enemy_class_shambler,
                                                                                             district))
            if len(shamblers) == 0:
                # No more stocked tombstones, and no more enemy shamblers. Garden Gankers win!
                victor = ewcfg.psuedo_faction_gankers

        op_juvies = bknd_core.execute_sql_query(
            "SELECT id_user FROM gvs_ops_choices WHERE faction = 'gankers' AND district = '{}' AND id_user != 56709 GROUP BY id_user".format(
                district))

        # No more Garden Gankers left. Shamblers win?
        if len(op_juvies) == 0:

            # Check if the shamblers are fighting against the bot.
            # If they are, they can only win if at least one shambler has reached the back.
            if len(bot_garden_ops) > 0:
                back_shamblers = bknd_core.execute_sql_query(
                    "SELECT id_enemy FROM enemies WHERE gvs_coord IN {}".format(tuple(ewcfg.gvs_coords_end)))
                if len(back_shamblers) > 0:
                    # Shambler reached the back while no juveniles were around to help the bot. Shamblers win!
                    victor = ewcfg.psuedo_faction_shamblers
            else:
                # No juveniles left in the district, and there were no bot operations. Shamblers win!
                victor = ewcfg.psuedo_faction_shamblers

        all_garden_ops = bknd_core.execute_sql_query(
            "SELECT id_user FROM gvs_ops_choices WHERE faction = 'gankers' AND district = '{}'".format(district))
        # No garden ops at all. Shamblers win!
        if len(all_garden_ops) == 0:
            victor = ewcfg.psuedo_faction_shamblers

        if victor != None:
            if victor == ewcfg.psuedo_faction_gankers:
                response = "***All tombstones have been emptied out! The Garden Gankers take victory!\nThe district is rejuvenated completely!!***"

                for juvie in op_juvies:
                    ewutils.active_restrictions[juvie[0]] = 0

                op_district_data.gaiaslime = 0
                op_district_data.degradation = 0
                op_district_data.time_unlock = time_now + 3600
                op_district_data.persist()
            else:
                response = "***The shamblers have eaten the brainz of the Garden Gankers and take control of the district!\nIt's shambled completely!!***"
                op_district_data.gaiaslime = 0
                op_district_data.degradation = ewcfg.district_max_degradation
                op_district_data.time_unlock = time_now + 3600
                op_district_data.persist()

            bknd_core.execute_sql_query("DELETE FROM gvs_ops_choices WHERE district = '{}'".format(district))
            await bknd_hunt.delete_all_enemies(cmd=None, query_suffix="AND poi = '{}'".format(district), id_server_sent=id_server)
            return await fe_utils.send_message(client, channel, response)


# Certain conditions may prevent a shambler from acting.
def check_enemy_can_act(enemy_data):
    enemy_props = enemy_data.enemy_props

    turn_countdown = enemy_props.get('turncountdown')
    dank_countdown = enemy_props.get('dankcountdown')
    sludge_countdown = enemy_props.get('sludgecountdown')
    hardened_sludge_countdown = enemy_props.get('hardsludgecountdown')

    waiting = False
    stoned = False
    sludged = False
    hardened = False

    if turn_countdown != None:
        if int(turn_countdown) > 0:
            waiting = True
            enemy_props['turncountdown'] -= 1
        else:
            waiting = False

    if dank_countdown != None:
        if int(dank_countdown) > 0:
            # If the countdown number is even, they can act. Otherwise, they cannot.
            if dank_countdown % 2 == 0:
                stoned = False
            else:
                stoned = True

            enemy_props['dankcountdown'] -= 1
        else:
            stoned = False

    # Regular sludge only slows a shambler down every other turn. Hardened sludge immobilizes them completely.
    if sludge_countdown != None:
        if int(sludge_countdown) > 0:
            # If the countdown number is even, they can act. Otherwise, they cannot.
            if sludge_countdown % 2 == 0:
                sludged = False
            else:
                sludged = True

            enemy_props['sludgecountdown'] -= 1
        else:
            sludged = False

    if hardened_sludge_countdown != None:
        if int(hardened_sludge_countdown) > 0:
            hardened = True
            enemy_props['hardsludgecountdown'] -= 1
        else:
            hardened = False

    enemy_data.persist()

    if not waiting and not stoned and not sludged and not hardened:
        return True
    else:
        return False


def handle_turn_timers(enemy_data):
    response = ""

    # Handle specific turn counters of all GvS enemies.
    if enemy_data.enemytype == ewcfg.enemy_type_gaia_brightshade:
        countdown = enemy_data.enemy_props.get('gaiaslimecountdown')

        if countdown != None:
            int_countdown = int(countdown)

            if int_countdown == 0:

                gaiaslime_amount = 0

                enemy_data.enemy_props['gaiaslimecountdown'] = 2
                district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)

                if enemy_data.enemy_props.get('joybean') != None:
                    if enemy_data.enemy_props.get('joybean') == 'true':
                        gaiaslime_amount = 50
                    else:
                        gaiaslime_amount = 25
                else:
                    gaiaslime_amount = 25

                district_data.gaiaslime += gaiaslime_amount
                district_data.persist()

                response = "{} ({}) produced {} gaiaslime!".format(enemy_data.display_name, enemy_data.gvs_coord,
                                                                   gaiaslime_amount)

            else:
                enemy_data.enemy_props['gaiaslimecountdown'] = int_countdown - 1

            enemy_data.persist()
            return response

    elif enemy_data.enemytype == ewcfg.enemy_type_gaia_poketubers:

        countdown = enemy_data.enemy_props.get('primecountdown')

        if countdown != None:
            int_countdown = int(countdown)

            if enemy_data.enemy_props.get('primed') != 'true':

                if int_countdown == 0:
                    enemy_data.enemy_props['primed'] = 'true'

                    response = "{} ({}) is primed and ready.".format(enemy_data.display_name, enemy_data.gvs_coord)

                else:
                    enemy_data.enemy_props['primecountdown'] = int_countdown - 1

                enemy_data.persist()
                return response


async def sh_move(enemy_data):
    current_coord = enemy_data.gvs_coord
    has_moved = False
    index = None
    row = None
    new_coord = None

    if current_coord in ewcfg.gvs_coords_start and enemy_data.enemytype == ewcfg.enemy_type_juvieshambler:
        bknd_hunt.delete_enemy(enemy_data)

    if current_coord not in ewcfg.gvs_coords_end:
        for row in ewcfg.gvs_valid_coords_shambler:

            if current_coord in row:
                index = row.index(current_coord)
                new_coord = row[index - 1]
                # print(new_coord)
                break

        if new_coord == None:
            return

        enemy_data.gvs_coord = new_coord
        enemy_data.persist()

        for gaia_row in ewcfg.gvs_valid_coords_gaia:
            if new_coord in gaia_row and index != None and row != None:
                poi_channel = poi_static.id_to_poi.get(enemy_data.poi).channel

                try:
                    previous_gaia_coord = row[index - 2]
                except:
                    break

                response = "The {} moved from {} to {}!".format(enemy_data.display_name, new_coord, previous_gaia_coord)
                client = ewutils.get_client()
                server = client.get_guild(enemy_data.id_server)
                channel = fe_utils.get_channel(server, poi_channel)

                await fe_utils.send_message(client, channel, response)

    # print('shambler moved from {} to {} in {}.'.format(current_coord, new_coord, enemy_data.poi))

    return has_moved


# Spawns an enemy in a randomized outskirt district. If a district is full, it will try again, up to 5 times.
def spawn_enemy(
        id_server,
        pre_chosen_type = None,
        pre_chosen_level = None,
        pre_chosen_slimes = None,
        pre_chosen_displayname = None,
        pre_chosen_expiration = None,
        pre_chosen_initialslimes = None,
        pre_chosen_poi = None,
        pre_chosen_identifier = None,
        # pre_chosen_hardened_sap = None,
        pre_chosen_weather = None,
        pre_chosen_faction = None,
        pre_chosen_owner = None,
        pre_chosen_coord = None,
        pre_chosen_rarity = None,
        pre_chosen_props = None,
        manual_spawn = False,
):
    time_now = int(time.time())
    response = ""
    ch_name = ""
    resp_cont = EwResponseContainer(id_server=id_server)
    chosen_poi = ""
    potential_chosen_poi = ""
    threat_level = ""
    boss_choices = []

    enemies_count = ewcfg.max_enemies
    try_count = 0

    rarity_choice = random.randrange(10000)

    if rarity_choice <= 5200:
        # common enemies
        enemytype = random.choice(ewcfg.common_enemies)
    elif rarity_choice <= 8000:
        # uncommon enemies
        enemytype = random.choice(ewcfg.uncommon_enemies)
    elif rarity_choice <= 9700:
        # rare enemies
        enemytype = random.choice(ewcfg.rare_enemies)
    else:
        # raid bosses
        threat_level_choice = random.randrange(1000)

        if threat_level_choice <= 450:
            threat_level = "micro"
        elif threat_level_choice <= 720:
            threat_level = "monstrous"
        elif threat_level_choice <= 900:
            threat_level = "mega"
        else:
            threat_level = "mega"
        # threat_level = "nega"

        boss_choices = ewcfg.raid_boss_tiers[threat_level]
        enemytype = random.choice(boss_choices)

    if pre_chosen_type is not None:
        enemytype = pre_chosen_type

    if not manual_spawn:

        while enemies_count >= ewcfg.max_enemies and try_count < 5:

            # Sand bags only spawn in the dojo
            if enemytype == ewcfg.enemy_type_sandbag:
                potential_chosen_poi = ewcfg.poi_id_dojo
            # Slimeoid Trainers only spawn in the Arena
            elif enemytype == ewcfg.enemy_type_slimeoidtrainer:
                potential_chosen_poi = ewcfg.poi_id_arena
            # Underground Trainers only spawn in the Subway, Ferry, or Blimp
            elif enemytype == ewcfg.enemy_type_ug_slimeoidtrainer:
                potential_chosen_poi = random.choice(poi_static.transports)
            # Everything else spawns in the outskrits TODO: Make this code not shit
            else:
                potential_chosen_poi = random.choice(poi_static.outskirts)

            potential_chosen_district = EwDistrict(district=potential_chosen_poi, id_server=id_server)
            enemies_list = potential_chosen_district.get_enemies_in_district()
            enemies_count = len(enemies_list)

            if enemies_count < ewcfg.max_enemies:
                chosen_poi = potential_chosen_poi
                try_count = 5
            else:
                # Enemy couldn't spawn in that district, try again
                try_count += 1

        # If it couldn't find a district in 5 tries or less, back out of spawning that enemy.
        if chosen_poi == "":
            return resp_cont

        if enemytype == 'titanoslime':
            potential_chosen_poi = 'downtown'

        # If an enemy spawns in the Nuclear Beach, it should be remade as a 'pre-historic' enemy.
        if potential_chosen_poi in [ewcfg.poi_id_nuclear_beach_edge, ewcfg.poi_id_nuclear_beach,
                                    ewcfg.poi_id_nuclear_beach_depths]:
            enemytype = random.choice(ewcfg.pre_historic_enemies)
            # If the enemy is a raid boss, re-roll it once to make things fair
            if enemytype in ewcfg.raid_bosses:
                enemytype = random.choice(ewcfg.pre_historic_enemies)
    else:
        if pre_chosen_poi == None:
            return

    if pre_chosen_poi != None:
        chosen_poi = pre_chosen_poi

    if enemytype != None:
        enemy = get_enemy_data(enemytype)

        # Assign enemy attributes that weren't assigned in get_enemy_data
        enemy.id_server = id_server
        enemy.slimes = enemy.slimes if pre_chosen_slimes is None else pre_chosen_slimes
        enemy.display_name = enemy.display_name if pre_chosen_displayname is None else pre_chosen_displayname
        enemy.level = level_byslime(enemy.slimes) if pre_chosen_level is None else pre_chosen_level
        enemy.expiration_date = time_now + ewcfg.time_despawn if pre_chosen_expiration is None else pre_chosen_expiration
        enemy.initialslimes = enemy.slimes if pre_chosen_initialslimes is None else pre_chosen_initialslimes
        enemy.poi = chosen_poi
        enemy.identifier = set_identifier(chosen_poi,
                                          id_server) if pre_chosen_identifier is None else pre_chosen_identifier
        # enemy.hardened_sap = int(enemy.level / 2) if pre_chosen_hardened_sap is None else pre_chosen_hardened_sap
        enemy.weathertype = ewcfg.enemy_weathertype_normal if pre_chosen_weather is None else pre_chosen_weather
        enemy.faction = '' if pre_chosen_faction is None else pre_chosen_faction
        enemy.owner = -1 if pre_chosen_owner is None else pre_chosen_owner
        enemy.gvs_coord = '' if pre_chosen_coord is None else pre_chosen_coord
        enemy.rare_status = enemy.rare_status if pre_chosen_rarity is None else pre_chosen_rarity

        if pre_chosen_weather != ewcfg.enemy_weathertype_normal:
            if pre_chosen_weather == ewcfg.enemy_weathertype_rainresist:
                enemy.display_name = "Bicarbonate {}".format(enemy.display_name)
                enemy.slimes *= 2

        # TODO delete after double halloween
        market_data = EwMarket(id_server=id_server)
        if (
                enemytype == ewcfg.enemy_type_doubleheadlessdoublehorseman or enemytype == ewcfg.enemy_type_doublehorse) and market_data.horseman_deaths >= 1:
            enemy.slimes *= 1.5

        props = None
        try:
            props = ewcfg.enemy_data_table[enemytype]["props"]
        except:
            pass

        enemy.enemy_props = props if pre_chosen_props is None else pre_chosen_props

        enemy.persist()

        # Recursively spawn enemies that belong to groups.
        if enemytype in ewcfg.enemy_group_leaders:
            sub_enemies_list = ewcfg.enemy_spawn_groups[enemytype]
            sub_enemies_list_item_max = len(sub_enemies_list)
            sub_enemy_list_item_count = 0

            while sub_enemy_list_item_count < sub_enemies_list_item_max:
                sub_enemy_type = sub_enemies_list[0]
                sub_enemy_spawning_max = sub_enemies_list[1]
                sub_enemy_spawning_count = 0

                sub_enemy_list_item_count += 1
                while sub_enemy_spawning_count < sub_enemy_spawning_max:
                    sub_enemy_spawning_count += 1

                    sub_resp_cont = spawn_enemy(id_server=id_server, pre_chosen_type=sub_enemy_type,
                                                pre_chosen_poi=chosen_poi, manual_spawn=True)

                    resp_cont.add_response_container(sub_resp_cont)

        if enemytype in ewcfg.slimeoid_trainers:
            sl_level = 1
            spawn_hue = False
            if enemy.rare_status:
                sl_level = random.randint(7, 10)
            else:
                sl_level = random.randint(1, 6)
            new_sl = slimeoid_utils.generate_slimeoid(id_owner=enemy.id_enemy, id_server=id_server, level=sl_level, persist=True)

        if enemytype not in ewcfg.raid_bosses:

            if enemytype in ewcfg.gvs_enemies_gaiaslimeoids:
                response = "**A {} has been planted in {}!!**".format(enemy.display_name, enemy.gvs_coord)
            elif enemytype in ewcfg.gvs_enemies_shamblers:
                response = "**A {} creeps forward!!** It spawned in {}!".format(enemy.display_name, enemy.gvs_coord)
            elif enemytype == ewcfg.enemy_type_doubleheadlessdoublehorseman:
                response = "***BEHOLD!!!***  The {} has arrived to challenge thee! He is of {} slime, and {} in level. Happy Double Halloween, you knuckleheads!".format(
                    enemy.display_name, enemy.slimes, enemy.level)

                if market_data.horseman_deaths >= 1:
                    response += "\n***BACK SO SOON, MORTALS? I'M JUST GETTING WARMED UP, BAHAHAHAHAHAHA!!!***"

            elif enemytype == ewcfg.enemy_type_doublehorse:
                response = "***HARK!!!***  Clopping echoes throughout the cave! The {} has arrived with {} slime, and {} levels. And on top of him rides...".format(
                    enemy.display_name, enemy.slimes, enemy.level)
            
            elif enemytype == ewcfg.enemy_type_sandbag:
                    response = "A new {} just got sent in. It's level {}, and has {} slime.\n*'Don't hold back!'*, the Dojo Master cries out from afar.".format(
                        enemy.display_name, enemy.level, enemy.slimes)
            
            elif enemytype in ewcfg.slimeoid_trainers:
                response = "A {} is looking for a challenge! They are accompanied by {}, a {}-foot tall {}Slimeoid.".format(
                    enemy.display_name, new_sl.name, new_sl.level, "" if new_sl.hue == "" else new_sl.hue + " ")
            else:
                print('made it to response')
                response = "**An enemy draws near!!** It's a level {} {}, and has {} slime.".format(enemy.level,
                                                                                                    enemy.display_name,
                                                                                                    enemy.slimes)
                

        ch_name = poi_static.id_to_poi.get(enemy.poi).channel

    if len(response) > 0 and len(ch_name) > 0:
        resp_cont.add_channel_response(ch_name, response)

    return resp_cont


# Determines what level an enemy is based on their slime count.
def level_byslime(slime):
    return int(abs(slime) ** 0.25)


# Assigns enemies most of their necessary attributes based on their type.
def get_enemy_data(enemy_type):
    enemy = EwEnemy()

    rare_status = 0
    if random.randrange(5) == 0 and enemy_type not in ewcfg.overkill_enemies and enemy_type not in ewcfg.gvs_enemies:
        rare_status = 1

    enemy.id_server = -1
    enemy.slimes = 0
    enemy.totaldamage = 0
    enemy.level = 0
    enemy.life_state = ewcfg.enemy_lifestate_alive
    enemy.enemytype = enemy_type
    enemy.bleed_storage = 0
    enemy.time_lastenter = 0
    enemy.initialslimes = 0
    enemy.id_target = -1
    enemy.raidtimer = 0
    enemy.rare_status = rare_status

    if enemy_type in ewcfg.raid_bosses:
        enemy.life_state = ewcfg.enemy_lifestate_unactivated
        enemy.raidtimer = int(time.time())

    slimetable = ewcfg.enemy_data_table[enemy_type]["slimerange"]
    minslime = slimetable[0]
    maxslime = slimetable[1]

    slime = random.randrange(minslime, (maxslime + 1))

    enemy.slimes = slime
    enemy.ai = ewcfg.enemy_data_table[enemy_type]["ai"]
    enemy.display_name = ewcfg.enemy_data_table[enemy_type]["displayname"]
    enemy.attacktype = ewcfg.enemy_data_table[enemy_type]["attacktype"]

    try:
        enemy.enemyclass = ewcfg.enemy_data_table[enemy_type]["class"]
    except:
        enemy.enemyclass = ewcfg.enemy_class_normal

    if rare_status == 1:
        enemy.display_name = ewcfg.enemy_data_table[enemy_type]["raredisplayname"]
        enemy.slimes *= 2

    return enemy


# Gives enemy an identifier so it's easier to pick out in a crowd of enemies
def set_identifier(poi, id_server):
    district = EwDistrict(district=poi, id_server=id_server)
    enemies_list = district.get_enemies_in_district()

    # A list of identifiers from enemies in a district
    enemy_identifiers = []

    new_identifier = ewcfg.identifier_letters[0]

    if len(enemies_list) > 0:
        for enemy_id in enemies_list:
            enemy = EwEnemy(id_enemy=enemy_id)
            enemy_identifiers.append(enemy.identifier)

        # Sort the list of identifiers alphabetically
        enemy_identifiers.sort()

        for checked_enemy_identifier in enemy_identifiers:
            # If the new identifier matches one from the list of enemy identifiers, give it the next applicable letter
            # Repeat until a unique identifier is given
            if new_identifier == checked_enemy_identifier:
                next_letter = (ewcfg.identifier_letters.index(checked_enemy_identifier) + 1)
                new_identifier = ewcfg.identifier_letters[next_letter]
            else:
                continue

    return new_identifier
