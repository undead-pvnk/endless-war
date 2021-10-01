import math
import random

from ew.backend import core as bknd_core, item as bknd_item
from ew.backend.item import EwItem
from ew.backend.mutation import EwMutation
from ew.backend.player import EwPlayer
from ew.backend.worldevent import get_void_connection_pois
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils.combat import EwEnemy
from ew.utils.slimeoid import EwSlimeoid

"""
    Returns data for POI if it isn't on the map.
"""


# Unused
def fetch_poi_if_coordless(channel_name):
    if channel_name != None:
        poi = poi_static.chname_to_poi.get(channel_name)

        if poi != None and poi.coord is None:
            return poi

    return None


"""
    Returns the fancy display name of the specified POI.
"""


# Unused
def poi_id_to_display_name(poi_name = None):
    poi = poi_static.id_to_poi.get(poi_name)

    if poi != None:
        return poi.str_name

    return "the city"

    #  0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54


# Unused
def pairToString(pair):
    return "({},{})".format("{}".format(pair[0]).rjust(2), "{}".format(pair[1]).ljust(2))


# Unused
def replace_with_inf(n):
    return math.inf


def get_slimes_resp(district_data):
    # get information about slime levels in the district

    slimes_resp = ""

    slimes = district_data.slimes
    if slimes < 10000:
        slimes_resp += "There are a few specks of slime splattered across the city streets."
    elif slimes < 100000:
        slimes_resp += "There are sparse puddles of slime filling potholes in the cracked city streets."
    elif slimes < 1000000:
        slimes_resp += "There are good amounts of slime pooling around storm drains and craters in the rundown city streets."
    else:
        slimes_resp += "There are large heaps of slime shoveled into piles to clear the way for cars and pedestrians on the slime-soaked city streets."

    return slimes_resp


def get_players_look_resp(user_data, district_data):
    # get information about players in the district

    # don't show low level players
    min_level = math.ceil((1 / 10) ** 0.25 * user_data.slimelevel)

    life_states = [ewcfg.life_state_corpse, ewcfg.life_state_juvenile, ewcfg.life_state_enlisted]

    players_in_district = district_data.get_players_in_district(min_level=min_level, life_states=life_states)
    if user_data.id_user in players_in_district:
        players_in_district.remove(user_data.id_user)

    num_players = len(players_in_district)
    players_resp = "\n\n"
    if num_players == 0:
        players_resp += "You don’t notice any activity from this district."
    elif num_players == 1:
        players_resp += "You can hear the occasional spray of a spray can from a gangster in this district."
    elif num_players <= 5:
        players_resp += "You can make out a distant conversation between a few gangsters in this district."
    elif num_players <= 10:
        players_resp += "You can hear shouting and frequent gunshots from a group of gangsters in this district."
    else:
        players_resp += "You feel the ground rumble from a stampeding horde of gangsters in this district."

    return players_resp


def get_enemies_look_resp(user_data, district_data):
    # lists off enemies in district

    # identifiers are converted into lowercase, then into emoticons for visual clarity.
    # server emoticons are also used for clarity

    enemies_in_district = district_data.get_enemies_in_district(classes=[ewcfg.enemy_class_normal, ewcfg.enemy_class_shambler])

    num_enemies = len(enemies_in_district)

    enemies_resp = "\n\n"

    if num_enemies == 0:
        enemies_resp = ""
    # enemies_resp += "You don't find any enemies in this district."
    elif num_enemies == 1:
        found_enemy_data = EwEnemy(id_enemy=enemies_in_district[0])

        if found_enemy_data.identifier != '':
            identifier_text = " {}".format(":regional_indicator_{}:".format(found_enemy_data.identifier.lower()))
        else:
            identifier_text = ""

        if found_enemy_data.ai == ewcfg.enemy_ai_coward or found_enemy_data.ai == ewcfg.enemy_ai_sandbag or found_enemy_data.ai == ewcfg.enemy_ai_carrottop or (found_enemy_data.ai == ewcfg.enemy_ai_defender and found_enemy_data.id_target != user_data.id_user) or (found_enemy_data.enemyclass == ewcfg.enemy_class_shambler and user_data.life_state == ewcfg.life_state_shambler) or (
                found_enemy_data.enemyclass == ewcfg.enemy_class_gaiaslimeoid and user_data.life_state != ewcfg.life_state_shambler):
            threat_emote = ewcfg.emote_slimeheart
        else:
            threat_emote = ewcfg.emote_slimeskull

        enemies_resp += ("You look around and find a\n{} **{}" + identifier_text + "**\nin this location.").format(threat_emote, found_enemy_data.display_name)
    else:
        enemies_resp += "You notice several enemies in this district, such as\n"
        for i in range(len(enemies_in_district) - 1):
            found_enemy_data = EwEnemy(id_enemy=enemies_in_district[i])

            if found_enemy_data.identifier != '':
                if not ewcfg.gvs_active:
                    identifier_text = " {}".format(":regional_indicator_{}:".format(found_enemy_data.identifier.lower()))
                else:
                    identifier_text = " {}, ({})".format(":regional_indicator_{}:".format(found_enemy_data.identifier.lower()), found_enemy_data.gvs_coord)
            else:
                identifier_text = ""

            # remove after event - Carrot Top's funny
            if found_enemy_data.ai == ewcfg.enemy_ai_coward or found_enemy_data.ai == ewcfg.enemy_ai_sandbag or found_enemy_data.ai == ewcfg.enemy_ai_carrottop or (
                    found_enemy_data.ai == ewcfg.enemy_ai_defender and found_enemy_data.id_target != user_data.id_user):
                threat_emote = ewcfg.emote_slimeheart
            else:
                threat_emote = ewcfg.emote_slimeskull

            enemies_resp += ("{} **{}" + identifier_text + "**\n").format(threat_emote, found_enemy_data.display_name)

        final_enemy_data = EwEnemy(id_enemy=enemies_in_district[num_enemies - 1])

        if final_enemy_data.identifier != '':
            if not ewcfg.gvs_active:
                identifier_text = " {}".format(":regional_indicator_{}:".format(final_enemy_data.identifier.lower()))
            else:
                identifier_text = " {}, ({})".format(":regional_indicator_{}:".format(final_enemy_data.identifier.lower()), final_enemy_data.gvs_coord)
        else:
            identifier_text = ""

        if final_enemy_data.ai == ewcfg.enemy_ai_coward or final_enemy_data.ai == ewcfg.enemy_ai_sandbag or final_enemy_data.ai == ewcfg.enemy_ai_carrottop or(final_enemy_data.ai == ewcfg.enemy_ai_defender and final_enemy_data.id_target != user_data.id_user):
            threat_emote = ewcfg.emote_slimeheart
        else:
            threat_emote = ewcfg.emote_slimeskull

        enemies_resp += ("{} **{}" + identifier_text + "**").format(threat_emote, final_enemy_data.display_name)

    return enemies_resp


def get_slimeoids_resp(id_server, poi):
    slimeoids_resp = ""

    slimeoids_in_district = ewutils.get_slimeoids_in_poi(id_server=id_server, poi=poi.id_poi)

    for id_slimeoid in slimeoids_in_district:
        slimeoid_data = EwSlimeoid(id_slimeoid=id_slimeoid)
        if slimeoid_data.sltype == ewcfg.sltype_nega:
            slimeoids_resp += "\n{} is here.".format(slimeoid_data.name)

    return slimeoids_resp


# SWILLDERMUK - Unused
def get_random_prank_item(user_data, district_data):
    response = ""

    items_in_poi = bknd_item.inventory(id_user=user_data.poi, id_server=district_data.id_server)

    prank_items = []

    for item in items_in_poi:
        id_item = item.get("id_item")
        possible_prank_item = EwItem(id_item=id_item)

        context = possible_prank_item.item_props.get('context')
        food_item_id = possible_prank_item.item_props.get('id_food')

        if (context == ewcfg.context_prankitem or food_item_id == "defectivecreampie"):
            prank_items.append(id_item)

    if len(prank_items) > 0:
        id_item = random.choice(prank_items)

        prank_item = EwItem(id_item=id_item)

        item_name = prank_item.item_props.get('item_name')
        if item_name == None:
            item_name = prank_item.item_props.get('food_name')

        response = "\n\nYou think you can spot a {} lying on the ground somewhere...".format(item_name)

    return response


def get_void_connections_resp(poi, id_server):
    response = ""
    void_connections = get_void_connection_pois(id_server)
    if poi == ewcfg.poi_id_thevoid:
        connected_poi_names = [poi_static.id_to_poi.get(poi_id).str_name for poi_id in void_connections]
        response = "\nThe street sign in the intersection points to {}, and {}".format(", ".join(connected_poi_names), poi_static.id_to_poi.get(ewcfg.poi_id_thesewers).str_name)
    elif poi in void_connections:
        response = "There's also a well lit staircase leading underground, but it looks too clean to be an entrance to the subway."
    return response


async def one_eye_dm(id_user = None, id_server = None, poi = None):
    poi_obj = poi_static.id_to_poi.get(poi)
    client = ewutils.get_client()
    server = client.get_guild(id_server)

    server = client.get_guild(str(id_server))

    server = client.get_guild(int(id_server))

    id_player = EwPlayer(id_user=id_user, id_server=id_server)

    if poi_obj.pvp:
        try:
            recipients = bknd_core.execute_sql_query(
                "SELECT {id_user} FROM mutations WHERE {id_server} = %s AND {mutation} = %s and {data} = %s".format(
                    data=ewcfg.col_mutation_data,
                    id_server=ewcfg.col_id_server,
                    id_user=ewcfg.col_id_user,
                    mutation=ewcfg.col_id_mutation,
                ), (
                    id_server,
                    ewcfg.mutation_id_oneeyeopen,
                    str(id_user),
                ))
            for recipient in recipients:
                member = server.get_member(int(recipient[0]))
                mutation = EwMutation(id_server=id_server, id_user=recipient[0], id_mutation=ewcfg.mutation_id_oneeyeopen)
                mutation.data = ""
                mutation.persist()
                await fe_utils.send_message(client, member, fe_utils.formatMessage(member, "{} is stirring...".format(id_player.display_name)))

        except:
            ewutils.logMsg("Failed to do OEO notificaitons for {}.".format(id_user))


async def send_arrival_response(cmd, poi, channel):
    response = "You {} {}.".format(poi.str_enter, poi.str_name)
    if poi.id_poi in get_void_connection_pois(cmd.guild.id):
        response += "\nYou notice an underground passage that wasn't there last time you came here."

    return await fe_utils.send_message(cmd.client,
                                       channel,
                                       fe_utils.formatMessage(
                                           cmd.message.author,
                                           response
                                       )
                                       )
