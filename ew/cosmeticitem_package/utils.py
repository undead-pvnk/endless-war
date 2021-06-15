from ..backend import core as bknd_core
from ..backend.item import EwItem
from ..static import cfg as ewcfg
from ..static import hue as hue_static
from ..utils import core as ewutils

def dedorn_all_costumes():
    costumes = bknd_core.execute_sql_query("SELECT id_item FROM items_prop WHERE name = 'context' AND value = 'costume' AND id_item IN (SELECT id_item FROM items_prop WHERE (name = 'adorned' OR name = 'slimeoid') AND value = 'true')")
    costume_count = 0

    for costume_id in costumes:
        costume_item = EwItem(id_item=costume_id)

        costume_item.item_props['adorned'] = 'false'
        costume_item.item_props['slimeoid'] = 'false'

        costume_item.persist()

        costume_count += 1

    ewutils.logMsg("Dedorned {} costumes after full moon ended.".format(costume_count))


def update_hues():
    for hue in hue_static.hue_list:

        hue_props = {
            ewcfg.col_hue_analogous_1: '',
            ewcfg.col_hue_analogous_2: '',
            ewcfg.col_hue_splitcomp_1: '',
            ewcfg.col_hue_splitcomp_2: '',
            ewcfg.col_hue_fullcomp_1: '',
            ewcfg.col_hue_fullcomp_2: '',
        }

        for h in hue.effectiveness:
            effect = hue.effectiveness.get(h)

            if effect == ewcfg.hue_analogous:

                if hue_props.get(ewcfg.col_hue_analogous_1) == '':
                    hue_props[ewcfg.col_hue_analogous_1] = h

                elif hue_props.get(ewcfg.col_hue_analogous_2) == '':
                    hue_props[ewcfg.col_hue_analogous_2] = h

            elif effect == ewcfg.hue_atk_complementary:

                if hue_props.get(ewcfg.col_hue_splitcomp_1) == '':
                    hue_props[ewcfg.col_hue_splitcomp_1] = h

            elif effect == ewcfg.hue_special_complementary:

                if hue_props.get(ewcfg.col_hue_splitcomp_2) == '':
                    hue_props[ewcfg.col_hue_splitcomp_2] = h

            elif effect == ewcfg.hue_full_complementary:

                if hue_props.get(ewcfg.col_hue_fullcomp_1) == '':
                    hue_props[ewcfg.col_hue_fullcomp_1] = h

                elif hue_props.get(ewcfg.col_hue_fullcomp_2) == '':
                    hue_props[ewcfg.col_hue_fullcomp_2] = h

        bknd_core.execute_sql_query("REPLACE INTO hues ({}, {}, {}, {}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(
            ewcfg.col_id_hue,
            ewcfg.col_is_neutral,
            ewcfg.col_hue_analogous_1,
            ewcfg.col_hue_analogous_2,
            ewcfg.col_hue_splitcomp_1,
            ewcfg.col_hue_splitcomp_2,
            ewcfg.col_hue_fullcomp_1,
            ewcfg.col_hue_fullcomp_2,
        ), (
            hue.id_hue,
            1 if hue.is_neutral else 0,
            hue_props.get(ewcfg.col_hue_analogous_1),
            hue_props.get(ewcfg.col_hue_analogous_2),
            hue_props.get(ewcfg.col_hue_splitcomp_1),
            hue_props.get(ewcfg.col_hue_splitcomp_2),
            hue_props.get(ewcfg.col_hue_fullcomp_1),
            hue_props.get(ewcfg.col_hue_fullcomp_2),
        ))
