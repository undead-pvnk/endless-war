import time

from . import core as bknd_core
from ..static import cfg as ewcfg


class EwAd:
    id_ad = -1

    id_server = -1
    id_sponsor = ""

    content = ""
    time_expir = 0

    def __init__(
            self,
            id_ad = None
    ):
        if id_ad != None:
            self.id_ad = id_ad
            data = bknd_core.execute_sql_query("SELECT {id_server}, {id_sponsor}, {content}, {time_expir} FROM ads WHERE {id_ad} = %s".format(
                id_server=ewcfg.col_id_server,
                id_sponsor=ewcfg.col_id_sponsor,
                content=ewcfg.col_ad_content,
                time_expir=ewcfg.col_time_expir,
                id_ad=ewcfg.col_id_ad,
            ), (
                self.id_ad,
            ))

            if len(data) > 0:
                result = data[0]

                self.id_server = result[0]
                self.id_sponsor = result[1]
                self.content = result[2]
                self.time_expir = result[3]
            else:
                self.id_ad = -1

    def persist(self):
        bknd_core.execute_sql_query("REPLACE INTO ads ({}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s)".format(
            ewcfg.col_id_ad,
            ewcfg.col_id_server,
            ewcfg.col_id_sponsor,
            ewcfg.col_ad_content,
            ewcfg.col_time_expir,
        ), (
            self.id_ad,
            self.id_server,
            self.id_sponsor,
            self.content,
            self.time_expir
        ))


def create_ad(id_server, id_sponsor, content, time_expir):
    bknd_core.execute_sql_query("INSERT INTO ads ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)".format(
        ewcfg.col_id_server,
        ewcfg.col_id_sponsor,
        ewcfg.col_ad_content,
        ewcfg.col_time_expir,
    ), (
        id_server,
        id_sponsor,
        content,
        time_expir,
    ))


def get_ads(id_server):
    time_now = int(time.time())
    ad_ids = []
    data = bknd_core.execute_sql_query("SELECT {id_ad} FROM ads WHERE {id_server} = %s AND {time_expir} > %s ORDER BY {time_expir} ASC".format(
        id_ad=ewcfg.col_id_ad,
        id_server=ewcfg.col_id_server,
        time_expir=ewcfg.col_time_expir,
    ), (
        id_server,
        time_now
    ))

    for result in data:
        ad_ids.append(result[0])

    return ad_ids


def delete_expired_ads(id_server):
    time_now = int(time.time())
    data = bknd_core.execute_sql_query("DELETE FROM ads WHERE {id_server} = %s AND {time_expir} < %s".format(
        id_server=ewcfg.col_id_server,
        time_expir=ewcfg.col_time_expir,
    ), (
        id_server,
        time_now
    ))
