import random
import time

from ew.static import cfg as ewcfg
from ew.backend import item as bknd_item
from ew.backend import worldevent as bknd_event
from ew.backend.market import EwMarket

# does this have anything to do with markets? yes. how do you think wall street gets its nutrients when there are no nearby food stands?
# by eating the bricks in the trade center of course.
# look i need to use markets and don't want to deal with any circular imports fuck you

def brickeat(item_obj):
    id_server = item_obj.id_server
    market = EwMarket(id_server)
    pushedclock = ((market.clock + random.randint(6, 12)) % 24) + 1
    stomach = '{}stomach'.format(item_obj.id_owner)
    props = {"time": pushedclock, "brick_id": item_obj.id_item}
    bknd_event.create_world_event(id_server, ewcfg.event_type_brickshit, time.time(), time.time() + 86400, props)
    bknd_item.give_item(id_item=item_obj.id_item, id_user=stomach, id_server=item_obj.id_server)
