import math
import time

import discord

from . import core as ewutils
from . import frontend as fe_utils
from . import poi as poi_utils
from .frontend import EwResponseContainer
from ..backend import core as bknd_core
from ..backend.district import EwDistrictBase
from ..static import cfg as ewcfg
from ..static import poi as poi_static

"""
	district data model for database persistence
"""


class EwDistrict(EwDistrictBase):
    def get_number_of_friendly_neighbors(self):
        if self.controlling_faction == "":
            return 0
        neighbors = poi_static.poi_neighbors[self.name]
        friendly_neighbors = 0

        for neighbor_id in neighbors:
            neighbor_data = EwDistrict(id_server=self.id_server, district=neighbor_id)
            if neighbor_data.controlling_faction == self.controlling_faction:
                friendly_neighbors += 1
        return friendly_neighbors

    def all_neighbors_friendly(self):
        rival_gang_poi = "none"
        if self.controlling_faction == "":
            return False
        elif self.controlling_faction == ewcfg.faction_killers:
            rival_gang_poi = ewcfg.poi_id_rowdyroughhouse
        elif self.controlling_faction == ewcfg.faction_rowdys:
            rival_gang_poi = ewcfg.poi_id_copkilltown

        neighbors = poi_static.poi_neighbors[self.name]
        for neighbor_id in neighbors:
            neighbor_poi = poi_static.id_to_poi.get(neighbor_id)
            neighbor_data = EwDistrict(id_server=self.id_server, district=neighbor_id)
            if neighbor_data.controlling_faction != self.controlling_faction and not neighbor_poi.is_subzone and not neighbor_poi.is_outskirts or neighbor_poi.id_poi == rival_gang_poi:
                return False
            elif neighbor_poi.id_poi == ewcfg.poi_id_juviesrow:
                return False
        return True

    def all_streets_taken(self):
        street_name_list = poi_utils.get_street_list(self.name)

        if self.name == ewcfg.poi_id_rowdyroughhouse:
            return ewcfg.faction_rowdys
        elif self.name == ewcfg.poi_id_copkilltown:
            return ewcfg.faction_killers

        faction_list = []
        for name in street_name_list:
            district_data = EwDistrict(id_server=self.id_server, district=name)
            faction_list.append(district_data.controlling_faction)

        if len(faction_list) > 0 and all(faction == faction_list[0] for faction in faction_list):
            return faction_list[0]
        else:
            return ""

    def get_players_in_district(self,
                                min_level = 0,
                                max_level = math.inf,
                                life_states = [],
                                factions = [],
                                min_slimes = -math.inf,
                                max_slimes = math.inf,
                                ignore_offline = False,
                                pvp_only = False
                                ):
        client = ewutils.get_client()
        server = client.get_guild(self.id_server)
        if server == None:
            ewutils.logMsg("error: couldn't find server with id {}".format(self.id_server))
            return []
        time_now = int(time.time())

        players = bknd_core.execute_sql_query("SELECT {id_user}, {slimes}, {slimelevel}, {faction}, {life_state} FROM users WHERE id_server = %s AND {poi} = %s".format(
            id_user=ewcfg.col_id_user,
            slimes=ewcfg.col_slimes,
            slimelevel=ewcfg.col_slimelevel,
            faction=ewcfg.col_faction,
            life_state=ewcfg.col_life_state,
            poi=ewcfg.col_poi
        ), (
            self.id_server,
            self.name
        ))

        filtered_players = []
        for player in players:
            id_user = player[0]
            slimes = player[1]
            slimelevel = player[2]
            faction = player[3]
            life_state = player[4]

            member = server.get_member(id_user)

            if member != None:
                if max_level >= slimelevel >= min_level \
                        and max_slimes >= slimes >= min_slimes \
                        and (len(life_states) == 0 or life_state in life_states) \
                        and (len(factions) == 0 or faction in factions) \
                        and not (ignore_offline and member.status == discord.Status.offline):  # \
                    # and not (pvp_only and life_state == ewcfg.life_state_juvenile and slimelevel <= ewcfg.max_safe_level):
                    filtered_players.append(id_user)

        return filtered_players

    def get_enemies_in_district(self,
                                min_level = 0,
                                max_level = math.inf,
                                min_slimes = -math.inf,
                                max_slimes = math.inf,
                                scout_used = False,
                                classes = None,
                                ):

        client = ewutils.get_client()
        server = client.get_guild(self.id_server)
        if server == None:
            ewutils.logMsg("error: couldn't find server with id {}".format(self.id_server))
            return []

        enemies = bknd_core.execute_sql_query("SELECT {id_enemy}, {slimes}, {level}, {enemytype}, {enemyclass} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1".format(
            id_enemy=ewcfg.col_id_enemy,
            slimes=ewcfg.col_enemy_slimes,
            level=ewcfg.col_enemy_level,
            enemytype=ewcfg.col_enemy_type,
            enemyclass=ewcfg.col_enemy_class,
            poi=ewcfg.col_enemy_poi,
            life_state=ewcfg.col_enemy_life_state
        ), (
            self.id_server,
            self.name
        ))

        filtered_enemies = []
        for enemy_data_column in enemies:

            fetched_id_enemy = enemy_data_column[0]  # data from id_enemy column in enemies table
            fetched_slimes = enemy_data_column[1]  # data from slimes column in enemies table
            fetched_level = enemy_data_column[2]  # data from level column in enemies table
            fetched_type = enemy_data_column[3]  # data from enemytype column in enemies table
            fetched_class = enemy_data_column[4]  # data from enemyclass column in enemies table

            # Append the enemy to the list if it meets the requirements
            if max_level >= fetched_level >= min_level \
                    and max_slimes >= fetched_slimes >= min_slimes:
                if classes != None:
                    if fetched_class in classes:
                        filtered_enemies.append(fetched_id_enemy)
                else:
                    filtered_enemies.append(fetched_id_enemy)

            # Don't show sandbags on !scout
            if scout_used and fetched_type == ewcfg.enemy_type_sandbag:
                filtered_enemies.remove(fetched_id_enemy)

        return filtered_enemies

    # Check if a type of enemy is in a district, e.g. if a Mammoslime is in Downtown. Returns bool.

    def enemy_type_in_district(self,
                               search_type = ""):
        answer = False

        enemies = bknd_core.execute_sql_query("SELECT {enemy_type} FROM enemies WHERE id_server = %s AND {poi} = %s AND {life_state} = 1".format(
            enemy_type=ewcfg.col_enemy_type,
            poi=ewcfg.col_enemy_poi,
            life_state=ewcfg.col_enemy_life_state
        ), (
            self.id_server,
            self.name
        ))

        if search_type != "":
            for enemy_type_column in enemies:
                enemy_type = enemy_type_column[0]
                if search_type == enemy_type:
                    answer = True
        return answer

    def decay_capture_points(self):
        resp_cont_decay = EwResponseContainer(client=ewutils.get_client(), id_server=self.id_server)
        if self.capture_points > 0:
            # and self.time_unlock == 0:

            neighbors = poi_static.poi_neighbors[self.name]
            all_neighbors_friendly = self.all_neighbors_friendly()

            decay = -math.ceil(ewcfg.max_capture_points_a / (ewcfg.ticks_per_day * ewcfg.decay_modifier))
            # decay = -math.ceil(ewcfg.max_capture_points_a / (ewcfg.ticks_per_day * ewcfg.decay_modifier))

            slimeoids = ewutils.get_slimeoids_in_poi(poi=self.name, id_server=self.id_server, sltype=ewcfg.sltype_nega)

            nega_present = len(slimeoids) > 0

            poi = poi_static.id_to_poi.get(self.name)

            if nega_present:
                decay *= 1.5
            if self.capture_points + (decay * 3) > (ewcfg.max_capture_points[poi.property_class]):
                decay *= 3

            # if self.controlling_faction == "" or (not self.all_neighbors_friendly() and self.capture_points > ewcfg.max_capture_points[poi.property_class]) or nega_present:  # don't decay if the district is completely surrounded by districts controlled by the same faction
            if nega_present or not self.all_neighbors_friendly():
                # reduces the capture progress at a rate with which it arrives at 0 after 1 in-game day
                # if (self.capture_points + int(decay) < ewcfg.min_influence[self.property_class] and self.capture_points >= ewcfg.min_influence[self.property_class]) and not nega_present and self.controlling_faction != "":
                #	responses = self.change_capture_points(self.capture_points - ewcfg.min_influence[self.property_class], ewcfg.actor_decay)
                # else:
                responses = self.change_capture_points(int(decay), ewcfg.actor_decay)
                resp_cont_decay.add_response_container(responses)

        # if self.capture_points < 0:
        #	self.capture_points = 0

        if self.capture_points <= 0:
            if self.controlling_faction != "":  # if it was owned by a faction

                message = "The {faction} have lost control over {district} because of sheer negligence.".format(
                    faction=self.controlling_faction,
                    district=poi_static.id_to_poi[self.name].str_name
                )
                channels = [poi_static.id_to_poi[self.name].channel] + ewcfg.hideout_channels
                for ch in channels:
                    resp_cont_decay.add_channel_response(channel=ch, response=message)
            responses = self.change_ownership("", ewcfg.actor_decay)
            resp_cont_decay.add_response_container(responses)
            self.capturing_faction = ""
        return resp_cont_decay

    def change_capture_lock(self, progress):
        resp_cont = EwResponseContainer(id_server=self.id_server)

        progress_before = self.time_unlock

        self.time_unlock += progress

        if self.time_unlock < 0:
            self.time_unlock = 0

        progress_after = self.time_unlock

        if (progress_after // ewcfg.capture_lock_milestone) != (progress_before // ewcfg.capture_lock_milestone):
            time_mins = ewutils.formatNiceTime(seconds=progress_after, round_to_minutes=True)
            if progress < 0:
                if progress_before >= 15 * 60 >= progress_after:
                    message = "{district} will unlock for capture in {time}.".format(
                        district=poi_static.id_to_poi[self.name].str_name,
                        time=time_mins
                    )
                    channels = ewcfg.hideout_channels

                    for ch in channels:
                        resp_cont.add_channel_response(channel=ch, response=message)

                elif progress_before >= 5 * 60 >= progress_after:
                    message = "{district} will unlock for capture in {time}.".format(
                        district=poi_static.id_to_poi[self.name].str_name,
                        time=time_mins
                    )
                    channels = ewcfg.hideout_channels

                    for ch in channels:
                        resp_cont.add_channel_response(channel=ch, response=message)

                message = "{district} will unlock for capture in {time}.".format(
                    district=poi_static.id_to_poi[self.name].str_name,
                    time=time_mins
                )

                channels = [poi_static.id_to_poi[self.name].channel]

                for ch in channels:
                    resp_cont.add_channel_response(channel=ch, response=message)

        if self.time_unlock == 0 and progress < 0:
            chip_cont = self.change_capture_points(progress=-1, actor=ewcfg.actor_decay)
            resp_cont.add_response_container(chip_cont)

        return resp_cont

    def change_capture_points(self, progress, actor, nothing = None):
        #ewutils.logMsg("Points in {} changing by {}".format(self.name, progress))
        ccp_resp_ctn = EwResponseContainer(client=ewutils.get_client(), id_server=self.id_server)
        previous_owners, previous_cappers = self.controlling_faction, self.capturing_faction
        poi_data = poi_static.id_to_poi.get(self.name)
        percent_progress_start = int(self.capture_points / self.max_capture_points * 100)

        self.capture_points += progress

        # if points have been subtracted past 0
        if self.capture_points <= 0:
            # allow progress for decapping to be maintained for recapping, but hold at 0 if decaying
            self.capture_points *= -1 if actor != ewcfg.actor_decay else 0

            # if the district is now neutral mark it, otherwise mark that it is being taken
            self.capturing_faction = "" if self.capture_points == 0 else actor

            # if it was previously owned, remove ownership and alert the owners to their loss
            if self.controlling_faction != "":
                # only call it negligence if they lost it to decay
                if actor == ewcfg.actor_decay:
                    message = "The {owners} have lost control over {district} because of sheer negligence."
                    for ch in ewcfg.hideout_channels + [poi_data.channel]:
                        ccp_resp_ctn.add_channel_response(channel=ch, response=message)

                ccp_resp_ctn.add_response_container(self.change_ownership("", actor, client=ewutils.get_client()))

        # Assign after value limiting, reassign if it has to be limited at max
        percent_progress_after = int(self.capture_points / self.max_capture_points * 100)

        # if it has reached the ownership threshhold
        if self.capture_points >= self.max_capture_points:
            # Block overcapping
            self.capture_points = self.max_capture_points
            percent_progress_after = int(self.capture_points / self.max_capture_points * 100)

            # If it was not already owned
            if self.controlling_faction == "":
                # set the new owner
                ccp_resp_ctn.add_response_container(self.change_ownership(actor, actor, client=ewutils.get_client()))

        # if it wasn't captured, send progress alerts when being de/capped by non decay forces
        else:
            previous_milestone = percent_progress_start // ewcfg.capture_milestone
            new_milestone = percent_progress_after // ewcfg.capture_milestone

            # only announce if a new milestone was reached
            if previous_milestone != new_milestone:
                # Different responses for de/capping
                if progress > 0 and actor != ewcfg.actor_decay:
                    # When the first milestone is hit, send a special starting message
                    if new_milestone == 1:
                        message = "{actors} have started capturing {district}. Current progress: {progress}%"
                        ccp_resp_ctn.add_channel_response(channel=poi_data.channel, response=message)

                    # otherwise, create the generic progress message, and possibly alert for significant progress
                    else:
                        # Just hit/passed 30%. Alert gangbases. first 30% is free tho
                        if 30 <= percent_progress_after < (30 + ewcfg.capture_milestone):
                            message = "{actors} are capturing {district}."

                            for ch in ewcfg.hideout_channels:
                                ccp_resp_ctn.add_channel_response(channel=ch, response=message)

                        # Reinforcing captured territory
                        if self.controlling_faction == actor:
                            message = "{actors} are renewing their grasp on {district}. Current control level: {progress}%"
                            ccp_resp_ctn.add_channel_response(channel=poi_data.channel, response=message)

                        # Capturing uncontrolled territory
                        else:
                            message = "{actors} continue to capture {district}. Current progress: {progress}%"
                            ccp_resp_ctn.add_channel_response(channel=poi_data.channel, response=message)

                # District is being decapped from an owned state
                elif self.controlling_faction != "":
                    # alert gangbases to decapturing
                    if percent_progress_after < 75 <= percent_progress_start and actor != ewcfg.actor_decay:
                        message = "{actors} are de-capturing {district}."

                        for ch in ewcfg.hideout_channels:
                            ccp_resp_ctn.add_channel_response(channel=ch, response=message)

                    # alert gangbases as they approach loss of territory
                    elif percent_progress_after < 50 <= percent_progress_start:
                        message = "{owners}' control of {district} is slipping."

                        for ch in ewcfg.hideout_channels:
                            ccp_resp_ctn.add_channel_response(channel=ch, response=message)

                    # Mark progress for decappers
                    message = "{owners}' control of {district} has decreased. Remaining control level: {progress}%"
                    ccp_resp_ctn.add_channel_response(channel=poi_data.channel, response=message)

                # Opposing progress is being removed from an uncontrolled district
                else:
                    message = "{owners}' capture progress of {district} has decreased. Remaining progress: {progress}%"
                    ccp_resp_ctn.add_channel_response(channel=poi_data.channel, response=message)

        # Format messages
        for channel, unformatted_list in ccp_resp_ctn.channel_responses.items():
            formatted_list = []
            for msg in unformatted_list:
                newmsg = msg.format(
                    owners=(previous_owners if previous_owners != "" else previous_cappers).capitalize(),
                    actors=actor.capitalize(),
                    district=poi_data.str_name,
                    progress=percent_progress_after
                )

                formatted_list.append(newmsg)

            ccp_resp_ctn.channel_responses[channel] = formatted_list

        return ccp_resp_ctn

    """
        Change who controls the district. Can be used to update the channel topic by passing the already controlling faction as an arg.
    """

    def change_ownership(self, new_owner, actor, client = None):  # actor can either be a faction, "decay", or "init"
        resp_cont_owner = EwResponseContainer(client=ewutils.get_client(), id_server=self.id_server)

        factions = ["", ewcfg.faction_killers, ewcfg.faction_rowdys]

        if new_owner in factions:
            server = ewcfg.server_list[self.id_server]
            channel_str = poi_static.id_to_poi[self.name].channel
            channel = fe_utils.get_channel(server=server, channel_name=channel_str)

            if channel is not None and channel.topic:  # tests if the topic is neither None nor empty
                initialized = False

                # initialize channel topic control statuses
                for faction in factions:
                    if ewcfg.control_topics[faction] in channel.topic:
                        initialized = True

                if not initialized:
                    new_topic = channel.topic + " " + ewcfg.control_topics[new_owner]

                # replace the the string of the previously controlling faction with that of the new one.
                else:
                    new_topic = channel.topic.replace(ewcfg.control_topics[self.controlling_faction], ewcfg.control_topics[new_owner])

                if client is None:
                    client = ewutils.get_client()

                if client is not None:
                    resp_cont_owner.add_channel_topic(channel=channel_str, topic=new_topic)

            if self.controlling_faction != new_owner:  # if the controlling faction actually changed
                if new_owner != "":  # if it was captured by a faction instead of being de-captured or decayed
                    countdown_message = ""
                    if self.time_unlock > 0:
                        countdown_message = "It will unlock for capture again in {}.".format(ewutils.formatNiceTime(seconds=self.time_unlock, round_to_minutes=True))
                    message = "{faction} just captured {district}. {countdown}".format(
                        faction=self.capturing_faction.capitalize(),
                        district=poi_static.id_to_poi[self.name].str_name,
                        countdown=countdown_message
                    )
                    channels = [poi_static.id_to_poi[self.name].channel] + ewcfg.hideout_channels

                    for ch in channels:
                        resp_cont_owner.add_channel_response(channel=ch, response=message)
                else:  # successful de-capture or full decay
                    if actor != ewcfg.actor_decay:
                        message = "{faction} just wrested control over {district} from the {other_faction}.".format(
                            faction=actor.capitalize(),
                            district=poi_static.id_to_poi[self.name].str_name,
                            other_faction=self.controlling_faction  # the faction that just lost control
                        )
                        channels = [poi_static.id_to_poi[self.name].channel] + ewcfg.hideout_channels

                        for ch in channels:
                            resp_cont_owner.add_channel_response(channel=ch, response=message)

                self.controlling_faction = new_owner

        return resp_cont_owner

    """ add or remove slime """

    def change_slimes(self, n = 0, source = None):
        change = int(n)
        self.slimes += change

    """ wether the district is still functional """

    def is_degraded(self):
        checked_poi = poi_static.id_to_poi.get(self.name)
        if checked_poi is None:
            return True

        poi = None

        # In the Gankers Vs. Shamblers event, importance is placed on districts
        # As a result, if a district is degraded, then all of its subzones/streets are also now degraded
        if checked_poi.is_district:
            poi = checked_poi
        elif checked_poi.is_street:
            poi = poi_static.id_to_poi.get(checked_poi.father_district)
        elif checked_poi.is_subzone:
            # Subzones are a more complicated affair to check for degradation.
            # Look to see if its mother district is a district or a street, then check for degradation of the appropriate district.
            for mother_poi_id in checked_poi.mother_districts:
                mother_poi = poi_static.id_to_poi.get(mother_poi_id)

                if mother_poi.is_district:
                    # First mother POI found is a district. Break here and check for its degradation.
                    poi = mother_poi
                    break
                elif mother_poi.is_street:
                    # First mother POI found is a street. Break here and check for its father district's degradation.
                    poi = poi_static.id_to_poi.get(mother_poi.father_district)
                    break
        else:
            poi = checked_poi

        # print('poi checked was {}. looking for {} degradation.'.format(self.name, poi.id_poi))
        poi_district_data = EwDistrict(district=poi.id_poi, id_server=self.id_server)
        return poi_district_data.degradation >= poi.max_degradation

