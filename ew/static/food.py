import os
import json

from . import cfg as ewcfg

from ..model.food import EwFood

food_list = []
with open(os.path.join('json', 'food.json')) as f:
	foods = json.load(f)
	for i in foods:
		i = foods[i]
		food_list.append(
			EwFood(
				id_food = i['id_food'],						
				alias = i['alias'],							
				recover_hunger = i['recover_hunger'],		
				price = i['price'],							
				inebriation = i['inebriation'],				
				str_name = i['str_name'],					
				vendors = i['vendors'],						
				str_eat = i['str_eat'],						
				str_desc = i['str_desc'],					
				time_expir =  i['time_expir'],
				time_fridged =  i['time_fridged'],
				ingredients =  i['ingredients'],
				acquisition =  i['acquisition'],
				perishable =  i['perishable'],
			))						
		

# A map of id_food to EwFood objects.
food_map = {}

# A list of food names
food_names = []

# Populate food map, including all aliases.
for food in food_list:
	food_map[food.id_food] = food
	food_names.append(food.id_food)
	
	for alias in food.alias:
		food_map[alias] = food

# list of crops you're able to !reap
vegetable_list = []

# map of vegetables to their associated cosmetic material
vegetable_to_cosmetic_material = {}

# seperate the crops from the normal foods
for v in food_list:

	if ewcfg.vendor_farm not in v.vendors:
		pass
	else:
		if v.id_food in [ewcfg.item_id_direapples, ewcfg.item_id_brightshade, ewcfg.item_id_razornuts, ewcfg.item_id_steelbeans]:
			vegetable_to_cosmetic_material[v.id_food] = ewcfg.item_id_cool_material
		elif v.id_food in [ewcfg.item_id_pinkrowddishes, ewcfg.item_id_joybeans, ewcfg.item_id_purplekilliflower, ewcfg.item_id_suganmanuts]:
			vegetable_to_cosmetic_material[v.id_food] = ewcfg.item_id_cute_material
		elif v.id_food in [ewcfg.item_id_poketubers, ewcfg.item_id_dankwheat, ewcfg.item_id_blacklimes, ewcfg.item_id_aushucks]:
			vegetable_to_cosmetic_material[v.id_food] = ewcfg.item_id_beautiful_material
		elif v.id_food in [ewcfg.item_id_phosphorpoppies, ewcfg.item_id_pawpaw, ewcfg.item_id_sludgeberries, ewcfg.item_id_rustealeaves]:
			vegetable_to_cosmetic_material[v.id_food] = ewcfg.item_id_smart_material
		elif v.id_food in [ewcfg.item_id_sourpotatoes, ewcfg.item_id_bloodcabbages, ewcfg.item_id_pulpgourds, ewcfg.item_id_metallicaps]:
			vegetable_to_cosmetic_material[v.id_food] = ewcfg.item_id_tough_material

		vegetable_list.append(v)

candy_ids_list = []
for c in food_list:
	if c.acquisition == ewcfg.acquisition_trickortreating:
		candy_ids_list.append(c.id_food)
		

# Gather all the items that can be the result of trick-or-treating.
trickortreat_results = []

for t in food_list:
	if t.acquisition == ewcfg.acquisition_trickortreating:
		trickortreat_results.append(t)

# Shitty bait that always yields Plebefish while fishing.
plebe_bait = []

# Gather all shitty bait.
for bait in food_list:
	if bait.price == None or bait.price <= 1000:
		plebe_bait.append(bait.id_food)

