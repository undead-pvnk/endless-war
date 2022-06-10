import asyncio
import random
import time

from . import core as ewutils
from ..backend import core as bknd_core
from ..backend.user import EwUserBase as EwUser
from ..backend.market import EwMarket
from ..backend.player import EwPlayer
from ..backend.slimeoid import EwSlimeoidBase
from ..static import cfg as ewcfg
from ..static import hue as hue_static
from ..static import poi as poi_static
from ..static import slimeoid as sl_static

""" Slimeoid data model for database persistence """


class EwSlimeoid(EwSlimeoidBase):

    def die(self):
        self.life_state = ewcfg.slimeoid_state_dead
        self.id_user = ""

    def eat(self, food_item):
        if food_item.item_props.get('context') != ewcfg.context_slimeoidfood:
            return False

        if food_item.item_props.get('decrease') == ewcfg.slimeoid_stat_moxie:
            if self.atk < 1:
                return False

            self.atk -= 1
        elif food_item.item_props.get('decrease') == ewcfg.slimeoid_stat_grit:
            if self.defense < 1:
                return False

            self.defense -= 1
        elif food_item.item_props.get('decrease') == ewcfg.slimeoid_stat_chutzpah:
            if self.intel < 1:
                return False

            self.intel -= 1
        if food_item.item_props.get('increase') == ewcfg.slimeoid_stat_moxie:
            self.atk += 1
        elif food_item.item_props.get('increase') == ewcfg.slimeoid_stat_grit:
            self.defense += 1
        elif food_item.item_props.get('increase') == ewcfg.slimeoid_stat_chutzpah:
            self.intel += 1

        return True


def get_slimeoid_look_string(user_id = None, server_id = None):
    if user_id != None and server_id != None:
        finalString = ""
        slimeoid_data = EwSlimeoid(id_user=user_id, id_server=server_id)

        if slimeoid_data:

            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                sql = "SELECT {} FROM slimeoids WHERE {} = %s"
                cursor.execute(sql.format(ewcfg.col_name, ewcfg.col_id_user), [user_id])
                if cursor.rowcount > 0:
                    iterate = 0
                    finalString += "\n\nIn the freezer, you hear "
                    for sloid in cursor:
                        if iterate > 0:
                            finalString += ", "
                        if iterate >= cursor.rowcount - 1 and cursor.rowcount > 1:
                            finalString += "and "
                        finalString += sloid[0]
                        iterate += 1
                    finalString += " cooing to themselves."


            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

                return finalString


"""
	Describe the specified slimeoid. Used for the !slimeoid command and while it's being created.
"""


def slimeoid_describe(slimeoid):
    response = ""

    body = sl_static.body_map.get(slimeoid.body)
    if body != None:
        response += " {}".format(body.str_body)

    head = sl_static.head_map.get(slimeoid.head)
    if head != None:
        response += " {}".format(head.str_head)

    mobility = sl_static.mobility_map.get(slimeoid.legs)
    if mobility != None:
        response += " {}".format(mobility.str_mobility)

    offense = sl_static.offense_map.get(slimeoid.weapon)
    if offense != None:
        response += " {}".format(offense.str_offense)

    defense = sl_static.defense_map.get(slimeoid.armor)
    if defense != None:
        response += " {}".format(defense.str_armor)

    special = sl_static.special_map.get(slimeoid.special)
    if special != None:
        response += " {}".format(special.str_special)

    brain = sl_static.brain_map.get(slimeoid.ai)
    if brain != None:
        response += " {}".format(brain.str_brain)

    hue = hue_static.hue_map.get(slimeoid.hue)
    if hue != None:
        response += " {}".format(hue.str_desc)

    # coating = hue_static.hue_map.get(slimeoid.coating)
    # if coating != None:
    # 	response += " {}".format(coating.str_desc)

    stat_desc = []

    stat = slimeoid.atk
    if stat == 0:
        statlevel = "almost no"
    if stat == 1:
        statlevel = "just a little bit of"
    if stat == 2:
        statlevel = "a decent amount of"
    if stat == 3:
        statlevel = "quite a bit of"
    if stat == 4:
        statlevel = "a whole lot of"
    if stat == 5:
        statlevel = "loads of"
    if stat == 6:
        statlevel = "massive amounts of"
    if stat == 7:
        statlevel = "seemingly inexhaustible stores of"
    if stat >= 8:
        statlevel = "truly godlike levels of"
    stat_desc.append("{} moxie".format(statlevel))

    stat = slimeoid.defense
    if stat == 0:
        statlevel = "almost no"
    if stat == 1:
        statlevel = "just a little bit of"
    if stat == 2:
        statlevel = "a decent amount of"
    if stat == 3:
        statlevel = "quite a bit of"
    if stat == 4:
        statlevel = "a whole lot of"
    if stat == 5:
        statlevel = "loads of"
    if stat == 6:
        statlevel = "massive amounts of"
    if stat == 7:
        statlevel = "seemingly inexhaustible stores of"
    if stat >= 8:
        statlevel = "truly godlike levels of"
    stat_desc.append("{} grit".format(statlevel))

    stat = slimeoid.intel
    if stat == 0:
        statlevel = "almost no"
    if stat == 1:
        statlevel = "just a little bit of"
    if stat == 2:
        statlevel = "a decent amount of"
    if stat == 3:
        statlevel = "quite a bit of"
    if stat == 4:
        statlevel = "a whole lot of"
    if stat == 5:
        statlevel = "loads of"
    if stat == 6:
        statlevel = "massive amounts of"
    if stat == 7:
        statlevel = "seemingly inexhaustible stores of"
    if stat >= 8:
        statlevel = "truly godlike levels of"
    stat_desc.append("{} chutzpah".format(statlevel))

    response += " It has {}.".format(ewutils.formatNiceList(names=stat_desc))

    clout = slimeoid.clout
    if slimeoid.sltype != ewcfg.sltype_nega:
        if clout >= 50:
            response += " A **LIVING LEGEND** on the arena."
        elif clout >= 30:
            response += " A **BRUTAL CHAMPION** on the arena."
        elif clout >= 15:
            response += " This slimeoid has proven itself on the arena."
        elif clout >= 1:
            response += " This slimeoid has some clout, but has not yet realized its potential."
        elif clout == 0:
            response += " A pitiable baby, this slimeoid has no clout whatsoever."
    else:
        response += " Onlookers shriek in terror at the sight of it."

    if (int(time.time()) - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response += " It is currently incapacitated after being defeated."

    return response


def find_slimeoid(slimeoid_search = None, id_user = None, id_server = None):
    slimeoid_sought = None

    # search for an ID instead of a name
    slimeoid_list = []
    try:
        conn_info = bknd_core.databaseConnect()
        conn = conn_info.get('conn')
        cursor = conn.cursor()

        cursor.execute("SELECT {} FROM slimeoids WHERE {} = %s AND {} = %s".format(
            ewcfg.col_name,
            ewcfg.col_id_user,
            ewcfg.col_id_server
        ), (
            id_user,
            id_server))
        # print (sql)

        slimeoid_sought = None
        for row in cursor:
            slimeoid_name = row[0]
            slimeboy = EwSlimeoid(slimeoid_name=slimeoid_name, id_server=id_server, id_user=id_user)
            if ewutils.flattenTokenListToString(slimeoid_search) in ewutils.flattenTokenListToString(slimeboy.name):
                slimeoid_sought = slimeboy.id_slimeoid
                break

    finally:
        cursor.close()
        bknd_core.databaseClose(conn_info)

    return slimeoid_sought

def generate_slimeoid(id_owner = None, id_server = None, name = None, hue = None, level = None, persist = False, force_hue = False):
    new_slimeoid = EwSlimeoid()
    
    if id_owner:
        new_slimeoid.id_user = id_owner
    
    if id_server:
        new_slimeoid.id_server = id_server
    
    if name:
        new_slimeoid.name = name
    else:
        while new_slimeoid.name == "" or len(new_slimeoid.name) >= 32:
            sl_name_prefix = [
                "Dr. ", "Mr. ", "Mrs. ", "King ", "Queen ", "Sir ", "Xx_", "Lil' ", "Xr. ",
                "Wet ", "Dry ", "Spicy ", "Sweet ", "Bitter ", "Sour ", "Savoury ", "Lord "
            ]
            sl_name_suffix = [
                " the Destroyer", " the Wise", " III", " II", " IV", "_xX",
            ]
            new_name = random.choice(ewcfg.captcha_dict).capitalize()
            if random.randint(0, 10) <= 2:
                new_name = new_name + "-" + random.choice(ewcfg.captcha_dict).capitalize()
            if random.randint(0, 10) <= 5:
                new_name = random.choice(sl_name_prefix) + new_name
            if random.randint(0, 10) >= 5:
                new_name = new_name + random.choice(sl_name_suffix)
            
            new_slimeoid.name = new_name
    if hue:
        new_slimeoid.hue = hue
    else:    
        if random.randint(0, 2) == 0 or force_hue:
            new_slimeoid.hue = random.choice(hue_static.hue_list).id_hue
    if level:
        new_slimeoid.level = level
    else:
        new_slimeoid.level = random.randint(1, 10)

    for lvl in range(new_slimeoid.level):
        choice = random.randint(0, 2)
        if choice == 0:
            new_slimeoid.atk += 1
        elif choice == 1:
            new_slimeoid.defense += 1
        elif choice == 2:
            new_slimeoid.intel += 1

    # Generate all the body parts
    new_slimeoid.body = random.choice(sl_static.body_names)
    new_slimeoid.head = random.choice(sl_static.head_names)
    new_slimeoid.legs = random.choice(sl_static.mobility_names)
    new_slimeoid.armor = random.choice(sl_static.defense_names)
    new_slimeoid.weapon = random.choice(sl_static.offense_names)
    new_slimeoid.special = random.choice(sl_static.special_names)
    new_slimeoid.ai = random.choice(sl_static.brain_names)

    new_slimeoid.life_state = 2 # Finally, bring your creation to life!

    if persist:
        new_slimeoid.persist()

    return new_slimeoid
    