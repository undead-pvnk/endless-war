import random

from ew.backend import item as bknd_item
from ew.backend.market import EwMarket

#does this have anything to do with markets? yes. how do you think wall street gets its nutrients when there are no nearby food stands?
#by eating the bricks in the trade center of course.
#look i need to use markets and don't want to deal with any circular imports fuck you

def brickeat(item_obj):
	id_item = item_obj.id_item
	market = EwMarket(id_server=item_obj.id_server)
	pushedclock = ((market.clock + random.randint(6, 12)) % 24)+1
	item_obj.item_props['furniture_name'] = 'brick{:02d}'.format(pushedclock)
	digestion = '{}brickshit'.format(item_obj.id_owner)
	print(digestion)
	item_obj.persist()
	bknd_item.give_item(id_item=id_item, id_user=digestion, id_server=item_obj.id_server)
