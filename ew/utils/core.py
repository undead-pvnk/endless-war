import datetime
import math
import random
import re
import string
import time

from sys import getsizeof, stderr
from itertools import chain

from ..backend import core as bknd_core
from ..static import cfg as ewcfg
from ..static import mutations as static_mutations
from ..static import poi as poi_static
from ..static import weather as weather_static

TERMINATE = False
DEBUG = False

DEBUG_OPTIONS = {
    'no_race_cooldown': False,
}

# Map of user IDs to their course ID.
moves_active = {}

food_multiplier = {}

# Contains who players are trading with and the state of the trades
active_trades = {}
# Contains the items being offered by players
trading_offers = {}

# Map of users to their target. This includes apartments, potential Russian Roulette players, potential Slimeoid Battle players, etc.
active_target_map = {}
# Map of users to their restriction level, typically in a mini-game. This prevents people from moving, teleporting, boarding, retiring, or suiciding in Russian Roulette/Duels
active_restrictions = {}

# Map of users that have their butthole clenched
clenched = {}

# When using SSOD, adjusted paths are listed here.
path_ssod = {}

active_slimeoidbattles = {}


class EwVector2D:
    vector = [0, 0]

    def __init__(self, vector):
        self.vector = vector

    def scalar_product(self, other_vector):
        result = 0

        for i in range(2):
            result += self.vector[i] * other_vector.vector[i]

        return result

    def add(self, other_vector):
        result = []

        for i in range(2):
            result.append(self.vector[i] + other_vector.vector[i])

        return EwVector2D(result)

    def subtract(self, other_vector):
        result = []

        for i in range(2):
            result.append(self.vector[i] - other_vector.vector[i])

        return EwVector2D(result)

    def norm(self):
        result = self.scalar_product(self)
        result = result ** 0.5
        return result

    def normalize(self):
        result = []

        norm = self.norm()

        if norm == 0:
            return EwVector2D([0, 0])

        for i in range(2):
            result.append(round(self.vector[i] / norm, 3))

        return EwVector2D(result)


""" Write the string to stdout with a timestamp. """


def logMsg(string):
    print("[{}] {}".format(datetime.datetime.now(), string))

    return string


""" read a file named fname and return its contents as a string """


def getValueFromFileContents(fname):
    token = ""

    try:
        f_token = open(fname, "r")
        f_token_lines = f_token.readlines()

        for line in f_token_lines:
            line = line.rstrip()
            if len(line) > 0:
                token = line
    except IOError:
        token = ""
        print("Could not read {} file.".format(fname))
    finally:
        f_token.close()

    return token


""" get the Discord API token from the config file on disk """


def getToken():
    return getValueFromFileContents("token")


""" get the Twitch client ID from the config file on disk """


def getTwitchClientId():
    return getValueFromFileContents("twitch_client_id")


""" print a list of strings with nice comma-and grammar """


def formatNiceList(names = [], conjunction = "and"):
    l = len(names)

    if l == 0:
        return ''

    if l == 1:
        return names[0]

    return ', '.join(names[0:-1]) + '{comma} {conj} '.format(comma=(',' if l > 2 else ''), conj=conjunction) + names[-1]


def formatNiceTime(seconds = 0, round_to_minutes = False, round_to_hours = False):
    try:
        seconds = int(seconds)
    except:
        seconds = 0

    if round_to_minutes:
        minutes = round(seconds / 60)
    else:
        minutes = int(seconds / 60)

    if round_to_hours:
        hours = round(minutes / 60)
    else:
        hours = int(minutes / 60)

    minutes = minutes % 60
    seconds = seconds % 60
    time_tokens = []
    if hours > 0:
        if hours == 1:
            token_hours = "1 hour"
        else:
            token_hours = "{} hours".format(hours)
        time_tokens.append(token_hours)

    if round_to_hours:
        if len(time_tokens) == 0:
            time_tokens.append("0 hours")
        return formatNiceList(names=time_tokens, conjunction="and")

    if minutes > 0:
        if minutes == 1:
            token_mins = "1 minute"
        else:
            token_mins = "{} minutes".format(minutes)
        time_tokens.append(token_mins)

    if round_to_minutes:
        if len(time_tokens) == 0:
            time_tokens.append("0 minutes")
        return formatNiceList(names=time_tokens, conjunction="and")

    if seconds > 0:
        if seconds == 1:
            token_secs = "1 second"
        else:
            token_secs = "{} seconds".format(seconds)
        time_tokens.append(token_secs)

    if len(time_tokens) == 0:
        time_tokens.append("0 seconds")
    return formatNiceList(names=time_tokens, conjunction="and")


""" weighted choice. takes a dict of element -> weight and returns a random element """


def weightedChoice(weight_map):
    weight_sum = 0
    elem_list = []
    weight_sums = []
    for elem in weight_map:
        weight_sum += weight_map.get(elem)
        elem_list.append(elem)
        weight_sums.append(weight_sum)

    rand = random.random() * weight_sum

    for i in range(len(weight_sums)):
        weight = weight_sums[i]
        if rand < weight:
            return elem_list[i]


""" turn a list of Users into a list of their respective names """


def userListToNameString(list_user):
    names = []

    for user in list_user:
        names.append(user.display_name)

    return formatNiceList(names)


""" turn a list of Roles into a map of name = >Role """


def getRoleMap(roles):
    roles_map = {}

    for role in roles:
        roles_map[mapRoleName(role.name)] = role

    return roles_map


""" turn a list of Roles into a map of id = >Role """


def getRoleIdMap(roles):
    roles_map = {}

    for role in roles:
        roles_map[mapRoleName(role.id)] = role

    return roles_map


""" canonical lowercase no space name for a role """


def mapRoleName(roleName):
    if type(roleName) == int:
        return roleName
    return roleName.replace(" ", "").lower()


""" Parse a list of tokens and return an integer value. If allow_all, return -1 if the word 'all' is present. """


def getIntToken(tokens = [], allow_all = False, negate = False):
    value = None

    for token in tokens[1:]:
        try:
            value = int(token.replace(",", ""))
            if value < 0 and not negate:
                value = None
            elif value > 0 and negate:
                value = None
            elif negate:
                value = -value
            break
        except:
            if allow_all and ("{}".format(token)).lower() == 'all':
                return -1
            else:
                value = None

    return value


""" Get the map of weapon skills for the specified player. """


def weaponskills_get(id_server = None, id_user = None, member = None):
    weaponskills = {}

    if member != None:
        id_server = member.guild.id
        id_user = member.id

    if id_server != None and id_user != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("SELECT {weapon}, {weaponskill} FROM weaponskills WHERE {id_server} = %s AND {id_user} = %s".format(
                weapon=ewcfg.col_weapon,
                weaponskill=ewcfg.col_weaponskill,
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user
            ), (
                id_server,
                id_user
            ))

            data = cursor.fetchall()
            if data != None:
                for row in data:
                    weaponskills[row[0]] = row[1]
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)

    return weaponskills


""" Set an individual weapon skill value for a player. """


def weaponskills_set(id_server = None, id_user = None, member = None, weapon = None, weaponskill = 0):
    if member != None:
        id_server = member.guild.id
        id_user = member.id

    if id_server != None and id_user != None and weapon != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            cursor.execute("REPLACE INTO weaponskills({id_server}, {id_user}, {weapon}, {weaponskill}) VALUES(%s, %s, %s, %s)".format(
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user,
                weapon=ewcfg.col_weapon,
                weaponskill=ewcfg.col_weaponskill
            ), (
                id_server,
                id_user,
                weapon,
                weaponskill
            ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


""" Clear all weapon skills for a player (probably called on death). """


def weaponskills_clear(id_server = None, id_user = None, member = None, weaponskill = None):
    if member != None:
        id_server = member.guild.id
        id_user = member.id

    if id_server != None and id_user != None:
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Clear any records that might exist.
            cursor.execute("UPDATE weaponskills SET {weaponskill} = %s WHERE {weaponskill} > %s AND {id_server} = %s AND {id_user} = %s".format(
                weaponskill=ewcfg.col_weaponskill,
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user
            ), (
                weaponskill,
                weaponskill,
                id_server,
                id_user
            ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


re_flattener = re.compile("[ '\"!@#$%^&*().,/?{}\[\];:]")

"""
	Turn an array of tokens into a single word (no spaces or punctuation) with all lowercase letters.
"""


def flattenTokenListToString(tokens):
    global re_flattener
    target_name = ""

    if type(tokens) == list:
        for token in tokens:
            if token.startswith('<@') == False:
                target_name += re_flattener.sub("", token.lower())
    elif tokens.startswith('<@') == False:
        target_name = re_flattener.sub("", tokens.lower())

    return target_name


"""
	Return the role name of a user's faction. Takes user data object or life_state and faction tag
"""


def get_faction(user_data = None, life_state = 0, faction = ""):
    life_state = life_state
    faction = faction
    if user_data != None:
        life_state = user_data.life_state
        faction = user_data.faction

    faction_role = ewcfg.role_corpse

    if life_state == ewcfg.life_state_juvenile:
        faction_role = ewcfg.role_juvenile

    elif life_state == ewcfg.life_state_enlisted:
        if faction == ewcfg.faction_killers:
            faction_role = ewcfg.role_copkillers

        elif faction == ewcfg.faction_rowdys:
            faction_role = ewcfg.role_rowdyfuckers

        elif faction == ewcfg.faction_slimecorp:
            faction_role = ewcfg.role_slimecorp

        else:
            faction_role = ewcfg.role_juvenile

    elif life_state == ewcfg.life_state_kingpin:
        faction_role = ewcfg.role_kingpin

    elif life_state == ewcfg.life_state_grandfoe:
        faction_role = ewcfg.role_grandfoe

    elif life_state == ewcfg.life_state_executive:
        faction_role = ewcfg.role_executive

    elif life_state == ewcfg.life_state_lucky:
        faction_role = ewcfg.role_executive

    elif life_state == ewcfg.life_state_shambler:
        faction_role = ewcfg.role_shambler

    return faction_role


def get_faction_symbol(faction = "", faction_raw = ""):
    result = None

    if faction == ewcfg.role_kingpin:
        if faction_raw == ewcfg.faction_rowdys:
            result = ewcfg.emote_rowdyfucker
        elif faction_raw == ewcfg.faction_killers:
            result = ewcfg.emote_copkiller

    if result == None:
        if faction == ewcfg.role_corpse:
            result = ewcfg.emote_ghost
        elif faction == ewcfg.role_juvenile:
            result = ewcfg.emote_slime3
        elif faction == ewcfg.role_copkillers:
            result = ewcfg.emote_ck
        elif faction == ewcfg.role_rowdyfuckers:
            result = ewcfg.emote_rf
        elif faction == ewcfg.role_shambler:
            result = ewcfg.emote_slimeskull
        elif faction == ewcfg.role_slimecorp:
            result = ewcfg.emote_slimecorp
        else:
            result = ewcfg.emote_blank

    return result


"""
	Calculate the slime amount needed to reach a certain level
"""


def slime_bylevel(slimelevel):
    return int(slimelevel ** 4)


"""
	Calculate what level the player should be at, given their slime amount
"""


def level_byslime(slime):
    return int(abs(slime) ** 0.25)


"""
	Calculate the maximum sap amount a player can have at their given slime level
"""


def sap_max_bylevel(slimelevel):
    return int(1.6 * slimelevel ** 0.75)


"""
	Calculate the maximum hunger level at the player's slimelevel
"""


def hunger_max_bylevel(slimelevel, has_bottomless_appetite = 0):
    # note that when you change this formula, you'll also have to adjust its sql equivalent in pushupServerHunger
    mult = 1
    if has_bottomless_appetite == 1:
        mult = 2
    return max(ewcfg.min_stamina, slimelevel ** 2) * mult


"""
	Calculate how much more stamina activities should cost
"""


def hunger_cost_mod(slimelevel):
    return hunger_max_bylevel(slimelevel) / 200


"""
	Calculate how much food the player can carry
"""


def food_carry_capacity_bylevel(slimelevel):
    return math.ceil(slimelevel / ewcfg.max_food_in_inv_mod)


"""
	Calculate how many weapons the player can carry
"""


def weapon_carry_capacity_bylevel(slimelevel):
    return math.floor(slimelevel / ewcfg.max_weapon_mod) + 1


def max_adornspace_bylevel(slimelevel):
    if slimelevel < 4:
        adorn_space = 0
    else:
        adorn_space = math.floor(math.sqrt(slimelevel - 2) - 0.40)

    return adorn_space


"""
	gets the discord client the bot is running on
"""


def get_client():
    return ewcfg.get_client()


"""
	Returns a list of slimeoid ids in the district
"""


def get_slimeoids_in_poi(id_server = None, poi = None, sltype = None):
    slimeoids = []
    if id_server is None:
        return slimeoids

    query = "SELECT {id_slimeoid} FROM slimeoids WHERE {id_server} = %s".format(
        id_slimeoid=ewcfg.col_id_slimeoid,
        id_server=ewcfg.col_id_server
    )

    if sltype is not None:
        query += " AND {} = '{}'".format(ewcfg.col_type, sltype)

    if poi is not None:
        query += " AND {} = '{}'".format(ewcfg.col_poi, poi)

    data = bknd_core.execute_sql_query(query, (
        id_server,
    ))

    for row in data:
        slimeoids.append(row[0])

    return slimeoids


def number_civilians(id_server):
    query = bknd_core.execute_sql_query("SELECT COUNT(*) from enemies where enemytype in ('civilian', 'innocent') and id_server = id_server")
    for counts in query:
        if counts[0] < 20:
            return 1
        else:
            return 0


def is_otp(user_data):
    poi = poi_static.id_to_poi.get(user_data.poi)
    return user_data.poi not in [ewcfg.poi_id_thesewers, ewcfg.poi_id_juviesrow, ewcfg.poi_id_copkilltown, ewcfg.poi_id_rowdyroughhouse] and (not poi.is_apartment)


def check_accept_or_refuse(string):
    if string.content.lower() == ewcfg.cmd_accept or string.content.lower() == ewcfg.cmd_refuse:
        return True


def check_confirm_or_cancel(string):
    if string.content.lower() == ewcfg.cmd_confirm or string.content.lower() == ewcfg.cmd_cancel:
        return True


def check_trick_or_treat(string):
    if string.content.lower() == ewcfg.cmd_treat or string.content.lower() == ewcfg.cmd_trick:
        return True


def check_is_command(string):
    if string.content.startswith(ewcfg.cmd_prefix):
        return True


def end_trade(id_user):
    # Cancel an ongoing trade
    if active_trades.get(id_user) != None and len(active_trades.get(id_user)) > 0:
        trader = active_trades.get(id_user).get("trader")

        active_trades[id_user] = {}
        active_trades[trader] = {}

        trading_offers[trader] = []
        trading_offers[id_user] = []


def text_to_regional_indicator(text):
    #  note that inside the quotes below is a zero-width space,
    # used to prevent the regional indicators from turning into flags
    # also note that this only works for digits and english letters

    ###return "‎".join([chr(0x1F1E6 + string.ascii_uppercase.index(c)) for c in text.upper()])
    return "‎".join([c + '\ufe0f\u20e3' if c.isdigit() else chr(0x1F1E6 + string.ascii_uppercase.index(c)) for c in text.upper()])


def generate_captcha_random(length = 4):
    return "".join([random.choice(ewcfg.alphabet) for _ in range(length)]).upper()


def generate_captcha(length = 4, user_data = None):
    length_final = length
    if user_data is not None:
        mutations = user_data.get_mutations()
        if ewcfg.mutation_id_dyslexia in mutations:
            length_final = max(1, length_final - 1)
    try:
        return random.choice([captcha for captcha in ewcfg.captcha_dict if len(captcha) == length_final])
    except:
        return generate_captcha_random(length=length_final)


def check_fursuit_active(market_data):
    if (market_data.day % 31 == 0 and market_data.clock >= 20
            or market_data.day % 31 == 1 and market_data.clock < 6):
        return True
    else:
        return False


# Get the current kingpin of slimernalia
def get_slimernalia_kingpin(server):
    data = bknd_core.execute_sql_query("SELECT {id_user} FROM users WHERE {id_server} = %s AND {slimernalia_kingpin} = true".format(
        id_user=ewcfg.col_id_user,
        id_server=ewcfg.col_id_server,
        slimernalia_kingpin=ewcfg.col_slimernalia_kingpin
    ), (
        server.id,
    ))

    if len(data) > 0:
        return data[0][0]

    return None


# Get the player with the most festivity
def get_most_festive(server):
    data = bknd_core.execute_sql_query(
        "SELECT users.{id_user}, FLOOR({festivity}) + COALESCE(sigillaria, 0) + FLOOR({festivity_from_slimecoin}) as total_festivity FROM users " \
        "LEFT JOIN (SELECT {id_user}, {id_server}, COUNT(*) * 1000 as sigillaria FROM items INNER JOIN items_prop ON items.{id_item} = items_prop.{id_item} WHERE {name} = %s AND {value} = %s GROUP BY items.{id_user}, items.{id_server}) f on users.{id_user} = f.{id_user} AND users.{id_server} = f.{id_server} " \
        "WHERE users.{id_server} = %s ORDER BY total_festivity DESC LIMIT 1".format(
            id_user=ewcfg.col_id_user,
            id_server=ewcfg.col_id_server,
            festivity=ewcfg.col_festivity,
            festivity_from_slimecoin=ewcfg.col_festivity_from_slimecoin,
            name=ewcfg.col_name,
            value=ewcfg.col_value,
            id_item=ewcfg.col_id_item,
        ), (
            "id_furniture",
            ewcfg.item_id_sigillaria,
            server.id,
        ))

    return data[0][0]


""" Returns the latest value, so that short PvP timer actions don't shorten remaining PvP time. """


def calculatePvpTimer(current_time_expirpvp, timer, enlisted = False):
    if enlisted:
        timer *= 1
    # timer *= 4

    desired_time_expirpvp = int(time.time()) + timer

    if desired_time_expirpvp > current_time_expirpvp:
        return desired_time_expirpvp

    return current_time_expirpvp


"""
	Returns true if the specified name is used by any POI.
"""


def channel_name_is_poi(channel_name):
    if channel_name != None:
        return channel_name in poi_static.chname_to_poi

    return False


def mention_type(cmd, ew_id):
    if cmd.client_id.user == ew_id.user:
        return "ew"
    elif cmd.author_id.user == ew_id.user:
        return "self"
    else:
        return "other"


def get_mutation_alias(name):
    if static_mutations.mutations_map.get(name) != None:
        return name
    else:

        for mutation in static_mutations.mutations_map:
            for alias in static_mutations.mutations_map.get(mutation).alias:
                if name == alias:
                    return mutation
        return 0


def messagesplit(stringIn, whitespace = '\n'):
    currentMessage = stringIn
    messagearray = []
    while len(currentMessage) > 1500:
        index = currentMessage.rfind(whitespace, 0, 1500)
        messagearray.append(currentMessage[:index])
        currentMessage = currentMessage[index:]

    messagearray.append(currentMessage)
    return messagearray


"""
	Return true if inventory has associated User table entry
	and a member object from selected server.
	Member ensures they are present in game.
"""


def is_player_inventory(id_inventory, id_server):
    if id_server == None or id_inventory == None:
        return False

    if isinstance(id_inventory, int):
        pass
    elif not id_inventory.isdigit():
        return False

    # Grab the Discord Client
    client = get_client()
    discord_result = client.get_guild(id_server).get_member(id_inventory)

    # Access DB
    conn_info = bknd_core.databaseConnect()
    conn = conn_info.get('conn')
    cursor = conn.cursor()
    db_result = None

    # Try to grab a value from a user with given id
    try:
        cursor.execute("SELECT {} FROM users WHERE id_user = %s AND id_server = %s".format(
            ewcfg.col_rand_seed
        ), (
            id_inventory,
            id_server
        ))
        db_result = cursor.fetchone()
    finally:
        cursor.close()
        bknd_core.databaseClose(conn_info)

    if db_result != None and discord_result != None:
        return True
    else:
        return False


def weather_txt(market_data):
    response = ""
    time_current = market_data.clock
    displaytime = str(time_current)
    ampm = ''

    if time_current <= 12:
        ampm = 'AM'
    if time_current > 12:
        displaytime = str(time_current - 12)
        ampm = 'PM'

    if time_current == 0:
        displaytime = 'midnight'
        ampm = ''
    if time_current == 12:
        displaytime = 'high noon'
        ampm = ''

    flair = ''
    weather_data = weather_static.weather_map.get(market_data.weather)
    if weather_data != None:
        if time_current >= 6 and time_current <= 7:
            flair = weather_data.str_sunrise
        if time_current >= 8 and time_current <= 17:
            flair = weather_data.str_day
        if time_current >= 18 and time_current <= 19:
            flair = weather_data.str_sunset
        if time_current >= 20 or time_current <= 5:
            flair = weather_data.str_night

    response += "It is currently {}{} in NLACakaNM.{}".format(displaytime, ampm, (' ' + flair))
    return response



def total_size(o, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.
    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, dict, set and frozenset.
    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)
