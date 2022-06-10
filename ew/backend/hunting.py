import time

from . import core as bknd_core
from ..static import cfg as ewcfg
from ..utils import core as ewutils
from ew.utils.slimeoid import EwSlimeoid

""" Enemy data model for database persistence """


class EwEnemyBase:
    id_enemy = 0
    id_server = -1

    combatant_type = "enemy"

    # The amount of slime an enemy has
    slimes = 0

    # The total amount of damage an enemy has sustained throughout its lifetime
    totaldamage = 0

    # The type of AI the enemy uses to select which players to attack
    ai = ""

    # The name of enemy shown in responses
    display_name = ""

    # Used to help identify enemies of the same type in a district
    identifier = ""

    # An enemy's level, which determines how much damage it does
    level = 0

    # An enemy's location
    poi = ""

    # Life state 0 = Dead, pending for deletion when it tries its next attack / action
    # Life state 1 = Alive / Activated raid boss
    # Life state 2 = Raid boss pending activation
    life_state = 0

    # Used to determine how much slime an enemy gets, what AI it uses, as well as what weapon it uses.
    enemytype = ""

    # The 'weapon' of an enemy
    attacktype = ""

    # An enemy's bleed storage
    bleed_storage = 0

    # Used for determining when a raid boss should be able to move between districts
    time_lastenter = 0

    # Used to determine how much slime an enemy started out with to create a 'health bar' ( current slime / initial slime )
    initialslimes = 0

    # Enemies despawn when this value is less than int(time.time())
    expiration_date = 0

    # Used by the 'defender' AI to determine who it should retaliate against
    id_target = -1

    # Used by raid bosses to determine when they should activate
    raidtimer = 0

    # Determines if an enemy should use its rare variant or not
    rare_status = 0

    # What kind of weather the enemy is suited to
    weathertype = 0

    # Sap armor
    # hardened_sap = 0

    # What faction the enemy belongs to
    faction = ""

    # What class the enemy belongs to
    enemyclass = ""

    # Tracks which user is associated with the enemy
    owner = -1

    # Various properties different enemies might have
    enemy_props = ""

    """ Load the enemy data from the database. """

    def __init__(self, id_enemy = None, id_server = None, enemytype = None):
        self.combatant_type = ewcfg.combatant_type_enemy
        self.enemy_props = {}

        query_suffix = ""

        if id_enemy != None:
            query_suffix = " WHERE id_enemy = '{}'".format(id_enemy)
        else:

            if id_server != None:
                query_suffix = " WHERE id_server = '{}'".format(id_server)
                if enemytype != None:
                    query_suffix += " AND enemytype = '{}'".format(enemytype)

        if query_suffix != "":
            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                # Retrieve object
                cursor.execute(
                    "SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM enemies{}".format(
                        ewcfg.col_id_enemy,
                        ewcfg.col_id_server,
                        ewcfg.col_enemy_slimes,
                        ewcfg.col_enemy_totaldamage,
                        ewcfg.col_enemy_ai,
                        ewcfg.col_enemy_type,
                        ewcfg.col_enemy_attacktype,
                        ewcfg.col_enemy_display_name,
                        ewcfg.col_enemy_identifier,
                        ewcfg.col_enemy_level,
                        ewcfg.col_enemy_poi,
                        ewcfg.col_enemy_life_state,
                        ewcfg.col_enemy_bleed_storage,
                        ewcfg.col_enemy_time_lastenter,
                        ewcfg.col_enemy_initialslimes,
                        ewcfg.col_enemy_expiration_date,
                        ewcfg.col_enemy_id_target,
                        ewcfg.col_enemy_raidtimer,
                        ewcfg.col_enemy_rare_status,
                        ewcfg.col_enemy_weathertype,
                        ewcfg.col_faction,
                        ewcfg.col_enemy_class,
                        ewcfg.col_enemy_owner,
                        query_suffix
                    ))
                result = cursor.fetchone()

                if result != None:
                    # Record found: apply the data to this object.
                    self.id_enemy = result[0]
                    self.id_server = result[1]
                    self.slimes = result[2]
                    self.totaldamage = result[3]
                    self.ai = result[4]
                    self.enemytype = result[5]
                    self.attacktype = result[6]
                    self.display_name = result[7]
                    self.identifier = result[8]
                    self.level = result[9]
                    self.poi = result[10]
                    self.life_state = result[11]
                    self.bleed_storage = result[12]
                    self.time_lastenter = result[13]
                    self.initialslimes = result[14]
                    self.expiration_date = result[15]
                    self.id_target = result[16]
                    self.raidtimer = result[17]
                    self.rare_status = result[18]
                    self.weathertype = result[19]
                    self.faction = result[20]
                    self.enemyclass = result[21]
                    self.owner = result[22]

                    # Retrieve additional properties
                    cursor.execute("SELECT {}, {} FROM enemies_prop WHERE id_enemy = %s".format(
                        ewcfg.col_name,
                        ewcfg.col_value
                    ), (
                        self.id_enemy,
                    ))

                    for row in cursor:
                        # this try catch is only necessary as long as extraneous props exist in the table
                        try:
                            self.enemy_props[row[0]] = row[1]
                        except:
                            ewutils.logMsg("extraneous enemies_prop row detected.")

            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

    """ Save enemy data object to the database. """

    def persist(self):
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Save the object.
            cursor.execute(
                "REPLACE INTO enemies({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
                    ewcfg.col_id_enemy,
                    ewcfg.col_id_server,
                    ewcfg.col_enemy_slimes,
                    ewcfg.col_enemy_totaldamage,
                    ewcfg.col_enemy_ai,
                    ewcfg.col_enemy_type,
                    ewcfg.col_enemy_attacktype,
                    ewcfg.col_enemy_display_name,
                    ewcfg.col_enemy_identifier,
                    ewcfg.col_enemy_level,
                    ewcfg.col_enemy_poi,
                    ewcfg.col_enemy_life_state,
                    ewcfg.col_enemy_bleed_storage,
                    ewcfg.col_enemy_time_lastenter,
                    ewcfg.col_enemy_initialslimes,
                    ewcfg.col_enemy_expiration_date,
                    ewcfg.col_enemy_id_target,
                    ewcfg.col_enemy_raidtimer,
                    ewcfg.col_enemy_rare_status,
                    # ewcfg.col_enemy_hardened_sap,
                    ewcfg.col_enemy_weathertype,
                    ewcfg.col_faction,
                    ewcfg.col_enemy_class,
                    ewcfg.col_enemy_owner,
                ), (
                    self.id_enemy,
                    self.id_server,
                    self.slimes,
                    self.totaldamage,
                    self.ai,
                    self.enemytype,
                    self.attacktype,
                    self.display_name,
                    self.identifier,
                    self.level,
                    self.poi,
                    self.life_state,
                    self.bleed_storage,
                    self.time_lastenter,
                    self.initialslimes,
                    self.expiration_date,
                    self.id_target,
                    self.raidtimer,
                    self.rare_status,
                    # self.hardened_sap,
                    self.weathertype,
                    self.faction,
                    self.enemyclass,
                    self.owner,
                ))

            # If the enemy doesn't have an ID assigned yet, have the cursor give us the proper ID.
            if self.id_enemy == 0:
                used_enemy_id = cursor.lastrowid
                self.id_enemy = used_enemy_id
            # print('used new enemy id')
            else:
                used_enemy_id = self.id_enemy
            # print('used existing enemy id')

            # Remove all existing property rows.
            cursor.execute("DELETE FROM enemies_prop WHERE {} = %s".format(
                ewcfg.col_id_enemy
            ), (
                used_enemy_id,
            ))

            if self.enemy_props != None:
                for name in self.enemy_props:
                    cursor.execute("INSERT INTO enemies_prop({}, {}, {}) VALUES(%s, %s, %s)".format(
                        ewcfg.col_id_enemy,
                        ewcfg.col_name,
                        ewcfg.col_value
                    ), (
                        used_enemy_id,
                        name,
                        self.enemy_props[name]
                    ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


async def delete_all_enemies(cmd = None, query_suffix = "", id_server_sent = ""):
    if cmd != None:
        author = cmd.message.author

        if not author.guild_permissions.administrator:
            return

        id_server = cmd.message.guild.id

        bknd_core.execute_sql_query("DELETE FROM enemies WHERE id_server = {id_server}".format(
            id_server=id_server
        ))

        ewutils.logMsg("Deleted all enemies from database connected to server {}".format(id_server))

    else:
        id_server = id_server_sent

        bknd_core.execute_sql_query("DELETE FROM enemies WHERE id_server = {} {}".format(
            id_server,
            query_suffix
        ))

        ewutils.logMsg(
            "Deleted all enemies from database connected to server {}. Query suffix was '{}'".format(id_server,
                                                                                                     query_suffix))


# Check if raidboss is ready to attack / be attacked
def check_raidboss_countdown(enemy_data):
    time_now = int(time.time())

    # Wait for raid bosses
    if enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.raidtimer <= time_now - ewcfg.time_raidcountdown:
        # Raid boss has activated!
        return True
    elif enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.raidtimer > time_now - ewcfg.time_raidcountdown:
        # Raid boss hasn't activated.
        return False


# Check if an enemy is dead. Implemented to prevent enemy data from being recreated when not necessary.
def check_death(enemy_data):
    if enemy_data.slimes <= 0 or enemy_data.life_state == ewcfg.enemy_lifestate_dead:
        # delete_enemy(enemy_data)
        return True
    else:
        return False


# Deletes an enemy the database.
def delete_enemy(enemy_data):
    # print("DEBUG - {} - {} DELETED".format(enemy_data.id_enemy, enemy_data.display_name))
    enemy_data.clear_allstatuses()
    
    # If the enemy is a Slimeoid Trainer, delete its slimeoid.
    if enemy_data.enemytype in ewcfg.slimeoid_trainers:
        trainer_slimeoid = EwSlimeoid(id_user=enemy_data.id_enemy, id_server=enemy_data.id_server)
        trainer_slimeoid.delete()
    
    bknd_core.execute_sql_query("DELETE FROM enemies WHERE {id_enemy} = %s".format(
        id_enemy=ewcfg.col_id_enemy
    ), (
        enemy_data.id_enemy,
    ))




