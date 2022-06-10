from ew.backend import core as bknd_core
from ew.backend.item import EwItem
from ew.static import cfg as ewcfg
from ew.static import hue as hue_static
from ew.utils import core as ewutils


async def dedorn_all_costumes():
    costume_count = 0
    # Grab costumes from the cache if enabled
    item_cache = bknd_core.get_cache(obj_type = "EwItem")
    if item_cache is not False:
        # separate search criteria for adorned or slimeoided
        p1 = {"context": "costume", "adorned": "true"}
        p2 = {"context": "costume", "slimeoid": "true"}
        # compile both results
        costumes_data = item_cache.find_entries(criteria={"item_props": p1})
        costumes_data += item_cache.find_entries(criteria={"item_props": p2})

        # Build a list that'll be handled in the same way
        costumes = list(map(lambda dat: dat.get("id_item"), costumes_data))
    else:
        costumes = bknd_core.execute_sql_query("SELECT id_item FROM items_prop WHERE name = 'context' AND value = 'costume' AND id_item IN (SELECT id_item FROM items_prop WHERE (name = 'adorned' OR name = 'slimeoid') AND value = 'true')")

    for costume_id in costumes:
        costume_item = EwItem(id_item=costume_id)

        costume_item.item_props['adorned'] = 'false'
        costume_item.item_props['slimeoid'] = 'false'

        costume_item.persist()

        costume_count += 1

    ewutils.logMsg("Dedorned {} costumes after full moon ended.".format(costume_count))