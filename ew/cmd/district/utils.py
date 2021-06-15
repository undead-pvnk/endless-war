import asyncio
import time
import discord

from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import stats as ewstats
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict
from ew.utils.frontend import EwResponseContainer


"""
	Updates/Increments the capture_points values of all districts every time it's called
"""
async def capture_tick(id_server):
    # the variables might apparently be accessed before assignment if i didn't declare them here
    cursor = None
    conn_info = None

    resp_cont_capture_tick = EwResponseContainer(client=ewutils.get_client(), id_server=id_server)

    all_districts = poi_static.capturable_districts

    if len(all_districts) > 0:  # if all_districts isn't empty
        server = ewcfg.server_list[id_server]
        time_old = time.time()

        for district in all_districts:
            district_name = district
            dist = EwDistrict(id_server=id_server, district=district_name)

            if dist.time_unlock > 0 and not dist.all_neighbors_friendly():
                responses = dist.change_capture_lock(progress=-ewcfg.capture_tick_length)
                resp_cont_capture_tick.add_response_container(responses)
                dist.persist()

            if dist.time_unlock > 0:
                continue

            # no more automatic capping
            continue

            controlling_faction = dist.controlling_faction

            gangsters_in_district = dist.get_players_in_district(min_slimes=ewcfg.min_slime_to_cap, life_states=[ewcfg.life_state_enlisted], ignore_offline=True)

            slimeoids = ewutils.get_slimeoids_in_poi(poi=district_name, id_server=id_server, sltype=ewcfg.sltype_nega)

            nega_present = len(slimeoids) > 0
            #			if nega_present:
            #				continue

            # the faction that's actively capturing the district this tick
            # if no players are present, it's None, if only players of one faction (ignoring juvies and ghosts) are,
            # it's the faction's name, i.e. 'rowdys' or 'killers', and if both are present, it's 'both'
            faction_capture = None

            # how much progress will be made. is higher the more people of one faction are in a district, and is 0 if both teams are present
            capture_speed = 0

            # number of players actively capturing
            num_capturers = 0

            dc_stat_increase_list = []

            # checks if any players are in the district and if there are only players of the same faction, i.e. progress can happen
            for player in gangsters_in_district:
                player_id = player
                user_data = EwUser(id_user=player_id, id_server=id_server)
                player_faction = user_data.faction

                mutations = user_data.get_mutations()

                try:
                    player_online = server.get_member(player_id).status != discord.Status.offline
                except:
                    player_online = False

                # ewutils.logMsg("Online status checked. Time elapsed: %f" % (time.time() - time_old) + " Server: %s" % id_server + " Player: %s" % player_id + " Status: %s" % ("online" if player_online else "offline"))

                if player_online:
                    if faction_capture not in [None, player_faction]:  # if someone of the opposite faction is in the district
                        faction_capture = 'both'  # standstill, gang violence has to happen
                        capture_speed = 0
                        num_capturers = 0
                        dc_stat_increase_list.clear()

                    else:  # if the district isn't already controlled by the player's faction and the capture isn't halted by an enemy
                        faction_capture = player_faction
                        player_capture_speed = 1
                        if ewcfg.mutation_id_lonewolf in mutations and len(gangsters_in_district) == 1:
                            player_capture_speed *= 2
                        if ewcfg.mutation_id_patriot in mutations:
                            player_capture_speed *= 2

                        capture_speed += player_capture_speed
                        num_capturers += 1
                        dc_stat_increase_list.append(player_id)

            if faction_capture not in ['both', None]:  # if only members of one faction is present
                if district_name in poi_static.capturable_districts:
                    friendly_neighbors = dist.get_number_of_friendly_neighbors()
                    if dist.all_neighbors_friendly():
                        capture_speed = 0
                    elif dist.controlling_faction == faction_capture:
                        capture_speed *= 1 + 0.1 * friendly_neighbors
                    else:
                        capture_speed /= 1 + 0.1 * friendly_neighbors

                    capture_progress = dist.capture_points

                    if faction_capture != dist.capturing_faction:
                        capture_progress *= -1

                    capture_speed *= ewcfg.baseline_capture_speed

                    if dist.capture_points < dist.max_capture_points:
                        for stat_recipient in dc_stat_increase_list:
                            ewstats.change_stat(
                                id_server=id_server,
                                id_user=stat_recipient,
                                metric=ewcfg.stat_capture_points_contributed,
                                n=ewcfg.capture_tick_length * capture_speed
                            )

                    if faction_capture == dist.capturing_faction:  # if the faction is already in the process of capturing, continue
                        responses = dist.change_capture_points(ewcfg.capture_tick_length * capture_speed, faction_capture, num_capturers)
                        resp_cont_capture_tick.add_response_container(responses)

                    elif dist.capture_points == 0 and dist.controlling_faction == "":  # if it's neutral, start the capture
                        responses = dist.change_capture_points(ewcfg.capture_tick_length * capture_speed, faction_capture, num_capturers)
                        resp_cont_capture_tick.add_response_container(responses)

                        dist.capturing_faction = faction_capture

                    # lower the enemy faction's progress to revert it to neutral (or potentially get it onto your side without becoming neutral first)
                    else:  # if the (de-)capturing faction is not in control
                        responses = dist.change_capture_points(-(ewcfg.capture_tick_length * capture_speed * ewcfg.decapture_speed_multiplier), faction_capture)
                        resp_cont_capture_tick.add_response_container(responses)

                    dist.persist()
# await resp_cont_capture_tick.post()


"""
	Coroutine that continually calls capture_tick; is called once per server, and not just once globally
"""
async def capture_tick_loop(id_server):
    interval = ewcfg.capture_tick_length
    # causes a capture tick to happen exactly every 10 seconds (the "elapsed" thing might be unnecessary, depending on how long capture_tick ends up taking on average)
    while not ewutils.TERMINATE:
        await capture_tick(id_server=id_server)
        # ewutils.logMsg("Capture tick happened on server %s." % id_server + " Timestamp: %d" % int(time.time()))

        await asyncio.sleep(interval)


"""
	Gives both kingpins the appropriate amount of slime for how many districts they own and lowers the capture_points property of each district by a certain amount, turning them neutral after a while
"""
async def give_kingpins_slime_and_decay_capture_points(id_server):
    resp_cont_decay_loop = EwResponseContainer(client=ewutils.get_client(), id_server=id_server)

    for kingpin_role in [ewcfg.role_rowdyfucker, ewcfg.role_copkiller]:
        kingpin = fe_utils.find_kingpin(id_server=id_server, kingpin_role=kingpin_role)
        if kingpin is not None:
            kingpin = EwUser(id_server=id_server, id_user=kingpin.id_user)
            total_slimegain = 0
            for id_district in poi_static.capturable_districts:

                district = EwDistrict(id_server=id_server, district=id_district)

                # if the kingpin is controlling this district give the kingpin slime based on the district's property class
                if district.controlling_faction == (ewcfg.faction_killers if kingpin.faction == ewcfg.faction_killers else ewcfg.faction_rowdys):
                    poi = poi_static.id_to_poi.get(id_district)

                    slimegain = ewcfg.district_control_slime_yields[poi.property_class]

                    # increase slimeyields by 10 percent per friendly neighbor
                    friendly_mod = 1 + 0.1 * district.get_number_of_friendly_neighbors()
                    total_slimegain += slimegain * friendly_mod

            kingpin.change_slimes(n=total_slimegain)
            kingpin.persist()

            ewutils.logMsg(kingpin_role + " just received %d" % total_slimegain + " slime for their captured districts.")

    # Decay capture points.
    for id_district in poi_static.capturable_districts:
        district = EwDistrict(id_server=id_server, district=id_district)

        responses = district.decay_capture_points()
        resp_cont_decay_loop.add_response_container(responses)
        district.persist()
# await resp_cont_decay_loop.post()
