import random
import time

from . import core as bknd_core
from ..static import cfg as ewcfg
from ..static import status as se_static


class EwStatusEffect:
    id_server = -1
    id_user = -1
    id_status = ""

    time_expire = -1
    value = 0
    source = ""
    id_target = -1

    def __init__(
            self,
            id_status = None,
            user_data = None,
            time_expire = 0,
            value = 0,
            source = "",
            id_user = None,
            id_server = None,
            id_target = -1,
    ):
        if user_data != None:
            id_user = user_data.id_user
            id_server = user_data.id_server

        if id_status != None and id_user != None and id_server != None:
            self.id_server = id_server
            self.id_user = id_user
            self.id_status = id_status
            self.time_expire = time_expire
            self.value = value
            self.source = source
            self.id_target = id_target
            time_now = int(time.time())

            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                # Retrieve object
                cursor.execute("SELECT {time_expire}, {value}, {source}, {id_target} FROM status_effects WHERE {id_status} = %s and {id_server} = %s and {id_user} = %s".format(
                    time_expire=ewcfg.col_time_expir,
                    id_status=ewcfg.col_id_status,
                    id_server=ewcfg.col_id_server,
                    id_user=ewcfg.col_id_user,
                    value=ewcfg.col_value,
                    source=ewcfg.col_source,
                    id_target=ewcfg.col_status_target,
                ), (
                    self.id_status,
                    self.id_server,
                    self.id_user
                ))
                result = cursor.fetchone()

                if result != None:
                    self.time_expire = result[0]
                    self.value = result[1]
                    self.source = result[2]

                else:
                    # Save the object.
                    cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
                        ewcfg.col_id_server,
                        ewcfg.col_id_user,
                        ewcfg.col_id_status,
                        ewcfg.col_time_expir,
                        ewcfg.col_value,
                        ewcfg.col_source,
                        ewcfg.col_status_target,
                    ), (
                        self.id_server,
                        self.id_user,
                        self.id_status,
                        (self.time_expire + time_now) if self.time_expire > 0 else self.time_expire,
                        self.value,
                        self.source,
                        self.id_target,
                    ))

                    self.time_expire = (self.time_expire + time_now) if self.time_expire > 0 else self.time_expire

                    conn.commit()

            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

    """ Save item data object to the database. """

    def persist(self):
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Save the object.
            cursor.execute("REPLACE INTO status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
                ewcfg.col_id_server,
                ewcfg.col_id_user,
                ewcfg.col_id_status,
                ewcfg.col_time_expir,
                ewcfg.col_value,
                ewcfg.col_source,
                ewcfg.col_status_target,
            ), (
                self.id_server,
                self.id_user,
                self.id_status,
                self.time_expire,
                self.value,
                self.source,
                self.id_target,
            ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


class EwEnemyStatusEffect:
    id_server = -1
    id_enemy = -1
    id_status = ""

    time_expire = -1
    value = 0
    source = ""
    id_target = -1

    def __init__(
            self,
            id_status = None,
            enemy_data = None,
            time_expire = 0,
            value = 0,
            source = "",
            id_enemy = None,
            id_server = None,
            id_target = -1,
    ):
        if enemy_data != None:
            id_enemy = enemy_data.id_enemy
            id_server = enemy_data.id_server

        if id_status != None and id_enemy != None and id_server != None:
            self.id_server = id_server
            self.id_enemy = id_enemy
            self.id_status = id_status
            self.time_expire = time_expire
            self.value = value
            self.source = source
            self.id_target = id_target
            time_now = int(time.time())

            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                # Retrieve object
                cursor.execute("SELECT {time_expire}, {value}, {source}, {id_target} FROM enemy_status_effects WHERE {id_status} = %s and {id_server} = %s and {id_enemy} = %s".format(
                    time_expire=ewcfg.col_time_expir,
                    id_status=ewcfg.col_id_status,
                    id_server=ewcfg.col_id_server,
                    id_enemy=ewcfg.col_id_enemy,
                    value=ewcfg.col_value,
                    source=ewcfg.col_source,
                    id_target=ewcfg.col_status_target,
                ), (
                    self.id_status,
                    self.id_server,
                    self.id_enemy
                ))
                result = cursor.fetchone()

                if result != None:
                    self.time_expire = result[0]
                    self.value = result[1]
                    self.source = result[2]

                else:
                    # Save the object.
                    cursor.execute("REPLACE INTO enemy_status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
                        ewcfg.col_id_server,
                        ewcfg.col_id_enemy,
                        ewcfg.col_id_status,
                        ewcfg.col_time_expir,
                        ewcfg.col_value,
                        ewcfg.col_source,
                        ewcfg.col_status_target,
                    ), (
                        self.id_server,
                        self.id_enemy,
                        self.id_status,
                        (self.time_expire + time_now) if self.time_expire > 0 else self.time_expire,
                        self.value,
                        self.source,
                        self.id_target,
                    ))

                    self.time_expire = (self.time_expire + time_now) if self.time_expire > 0 else self.time_expire

                    conn.commit()

            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

    """ Save item data object to the database. """

    def persist(self):
        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Save the object.
            cursor.execute("REPLACE INTO enemy_status_effects({}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
                ewcfg.col_id_server,
                ewcfg.col_id_enemy,
                ewcfg.col_id_status,
                ewcfg.col_time_expir,
                ewcfg.col_value,
                ewcfg.col_source,
                ewcfg.col_status_target,
            ), (
                self.id_server,
                self.id_enemy,
                self.id_status,
                self.time_expire,
                self.value,
                self.source,
                self.id_target,
            ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)


def applyStatus(user_data, id_status = None, value = 0, source = "", multiplier = 1, id_target = -1):
    response = ""
    if id_status != None:
        status = None

        status = se_static.status_effects_def_map.get(id_status)
        time_expire = status.time_expire * multiplier

        if status != None:
            statuses = user_data.getStatusEffects()

            status_effect = EwStatusEffect(id_status=id_status, user_data=user_data, time_expire=time_expire, value=value, source=source, id_target=id_target)

            if id_status in statuses:
                status_effect.value = value

                if status.time_expire > 0 and id_status in ewcfg.stackable_status_effects:
                    status_effect.time_expire += time_expire
                    response = status.str_acquire

                status_effect.persist()
            else:
                response = status.str_acquire

    return response


def apply_injury(user_data, id_injury, severity, source):
    statuses = user_data.getStatusEffects()

    if id_injury in statuses:
        status_data = EwStatusEffect(id_status=id_injury, user_data=user_data)

        try:
            value_int = int(status_data.value)

            if value_int > severity:
                if random.randrange(value_int) < severity:
                    status_data.value = value_int + 1
            else:
                status_data.value = severity
        except:
            status_data.value = severity

        status_data.source = source

        status_data.persist()

    else:
        user_data.applyStatus(id_status=id_injury, value=severity, source=source)
