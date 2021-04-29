from . import cfg as ewcfg
from . import cosmetics
from . import items as static_items

# A map of vendor names to their items.
vendor_inv = {}

# Populate item map, including all aliases.
for item in static_items.item_list:
	# Add item to its vendors' lists.
	for vendor in item.vendors:
		vendor_list = vendor_inv.get(vendor)

		if vendor_list == None:
			vendor_list = []
			vendor_inv[vendor] = vendor_list

		vendor_list.append(item.id_item)

# Populate food map, including all aliases.
for food in ewcfg.food_list:
	ewcfg.food_map[food.id_food] = food
	ewcfg.food_names.append(food.id_food)

	# Add food to its vendors' lists.
	for vendor in food.vendors:
		vendor_list = vendor_inv.get(vendor)

		if vendor_list == None:
			vendor_list = []
			vendor_inv[vendor] = vendor_list

		vendor_list.append(food.id_food)

	for alias in food.alias:
		ewcfg.food_map[alias] = food

# Populate fish map, including all aliases.
for fish in ewcfg.fish_list:
	ewcfg.fish_map[fish.id_fish] = fish
	ewcfg.fish_names.append(fish.id_fish)

	# Add fish to its vendors' lists.
	for vendor in fish.vendors:
		vendor_list = vendor_inv.get(vendor)

		if vendor_list == None:
			vendor_list = []
			vendor_inv[vendor] = vendor_list

		vendor_list.append(fish.id_fish)

	for alias in fish.alias:
		ewcfg.fish_map[alias] = fish

# Populate cosmetic map.
for cosmetic in cosmetics.cosmetic_items_list:

	# Add cosmetics to its vendors' lists.
	for vendor in cosmetic.vendors:
		vendor_list = vendor_inv.get(vendor)

		if vendor_list == None:
			vendor_list = []
			vendor_inv[vendor] = vendor_list

		vendor_list.append(cosmetic.id_cosmetic)


for furniture in ewcfg.furniture_list:
	ewcfg.furniture_map[furniture.id_furniture] = furniture
	ewcfg.furniture_names.append(furniture.id_furniture)
	if furniture.furn_set == "haunted":
		ewcfg.furniture_haunted.append(furniture.id_furniture)
	elif furniture.furn_set == "high class":
		ewcfg.furniture_highclass.append(furniture.id_furniture)
	elif furniture.furn_set == "lgbt":
		ewcfg.furniture_lgbt.append(furniture.id_furniture)
	elif furniture.furn_set == "leather":
		ewcfg.furniture_leather.append(furniture.id_furniture)
	elif furniture.furn_set == "church":
		ewcfg.furniture_church.append(furniture.id_furniture)
	elif furniture.furn_set == "pony":
		ewcfg.furniture_pony.append(furniture.id_furniture)
	elif furniture.furn_set == "blackvelvet":
		ewcfg.furniture_blackvelvet.append(furniture.id_furniture)
	elif furniture.furn_set == "seventies":
		ewcfg.furniture_seventies.append(furniture.id_furniture)
	elif furniture.furn_set == "slimecorp":
		ewcfg.furniture_slimecorp.append(furniture.id_furniture)
	elif furniture.furn_set == "shitty":
		ewcfg.furniture_shitty.append(furniture.id_furniture)
	elif furniture.furn_set == "instrument":
		ewcfg.furniture_instrument.append(furniture.id_furniture)
	elif furniture.furn_set == "specialhue":
		ewcfg.furniture_specialhue.append(furniture.id_furniture)


	for vendor in furniture.vendors:
		vendor_list = vendor_inv.get(vendor)
		if vendor_list == None:
			vendor_list = []
			vendor_inv[vendor] = vendor_list
		vendor_list.append(furniture.id_furniture)


# Populate weapon map, including all aliases.
for weapon in ewcfg.weapon_list:
	ewcfg.weapon_map[weapon.id_weapon] = weapon
	ewcfg.weapon_names.append(weapon.id_weapon)

	for vendor in weapon.vendors:
		vendor_list = vendor_inv.get(vendor)

		if vendor_list == None:
			vendor_list = []
			vendor_inv[vendor] = vendor_list

		vendor_list.append(weapon.id_weapon)

	for alias in weapon.alias:
		ewcfg.weapon_map[alias] = weapon

# List of items you can obtain via milling.
mill_results = []

# Gather all items that can be the result of milling.
for m in static_items.item_list:
	if m.acquisition == ewcfg.acquisition_milling:
		mill_results.append(m)
	else:
		pass

for m in ewcfg.food_list:
	if m.acquisition == ewcfg.acquisition_milling:
		mill_results.append(m)
	else:
		pass

for m in cosmetics.cosmetic_items_list:
	if m.acquisition == ewcfg.acquisition_milling:
		mill_results.append(m)
	else:
		pass

# List of items you can obtain via appraisal.
appraise_results = []

# Gather all items that can be the result of bartering.
for a in static_items.item_list:
	if a.acquisition == ewcfg.acquisition_bartering:
		appraise_results.append(a)
	else:
		pass

for a in ewcfg.food_list:
	if a.acquisition == ewcfg.acquisition_bartering:
		appraise_results.append(a)
	else:
		pass

for a in cosmetics.cosmetic_items_list:
	if a.acquisition == ewcfg.acquisition_bartering:
		appraise_results.append(a)
	else:
		pass

# List of items you can obtain via smelting.
smelt_results = []

# Gather all items that can be the result of smelting.
for s in static_items.item_list:
	if s.acquisition == ewcfg.acquisition_smelting:
		smelt_results.append(s)
	# So poudrins can be smelted with 2 royalty poudrins (this is obviously half-assed but i can't think of a better solution)
	elif s.id_item == ewcfg.item_id_slimepoudrin:
		smelt_results.append(s)
	else:
		pass

for s in ewcfg.food_list:
	if s.acquisition == ewcfg.acquisition_smelting:
		smelt_results.append(s)
	else:
		pass

for s in cosmetics.cosmetic_items_list:
	if s.acquisition == ewcfg.acquisition_smelting:
		smelt_results.append(s)
	else:
		pass

for s in ewcfg.weapon_list:
	if s.acquisition == ewcfg.acquisition_smelting:
		smelt_results.append(s)
	else:
		pass

for s in ewcfg.furniture_list:
	if s.acquisition == ewcfg.acquisition_smelting:
		smelt_results.append(s)
	else:
		pass

# List of items you can obtain via mining.
mine_results = []

# Gather all items that can be the result of mining.
for m in static_items.item_list:
	if m.acquisition == ewcfg.acquisition_mining:
		mine_results.append(m)
	else:
		pass

for m in ewcfg.food_list:
	if m.acquisition == ewcfg.acquisition_mining:
		mine_results.append(m)
	else:
		pass

for m in cosmetics.cosmetic_items_list:
	if m.acquisition == ewcfg.acquisition_mining:
		mine_results.append(m)
	else:
		pass
