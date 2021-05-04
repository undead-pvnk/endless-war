import os
import json

from ..model.item import EwCosmeticItem

cosmetic_items_list = []

# A map of id_cosmetic to EwCosmeticItem objects.
cosmetic_map = {}

# A list of cosmetic names.
cosmetic_names = []

with open(os.path.join('json', 'cosmetic_items.json')) as f:
	cosmetic_items = json.load(f)
	for i in cosmetic_items:
		i = cosmetic_items[i]
		cosmetic_items_list.append(
			EwCosmeticItem(
			id_cosmetic = i['id_cosmetic'],
			str_name = i['str_name'],
			str_desc = i['str_desc'],
			str_onadorn = i['str_onadorn'],
			str_unadorn = i['str_unadorn'],
			str_onbreak = i['str_onbreak'],
			rarity = i['rarity'],
			ability = i['ability'],
			durability = i['durability'],
			size = i['size'],
			style = i['style'],
			freshness = i['freshness'],
			ingredients = i['ingredients'],
			acquisition = i['acquisition'],
			price = i['price'],
			vendors = i['vendors'],
			is_hat = i['is_hat'],
		))

# Populate cosmetic map.
for cosmetic in cosmetic_items_list:
	cosmetic_map[cosmetic.id_cosmetic] = cosmetic
	cosmetic_names.append(cosmetic.id_cosmetic)
