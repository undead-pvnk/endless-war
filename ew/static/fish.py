import json
import os

from ..model.fish import EwFish

# All the fish, baby!
fish_list = []
with open(os.path.join('json', 'fish.json')) as f:
    fish = json.load(f)
    for i in fish:
        i = fish[i]
        fish_list.append(
            EwFish(
                id_fish=i['id_fish'],
                str_name=i['str_name'],
                size=i['size'],
                rarity=i['rarity'],
                catch_time=i['catch_time'],
                catch_weather=i['catch_weather'],
                str_desc=i['str_desc'],
                slime=i['slime'],
                vendors=i['vendors']
            ))

# A map of id_fish to EwFish objects.
fish_map = {}

# A list of fish names.
fish_names = []

# Populate fish map, including all aliases.
for fish in fish_list:
    fish_map[fish.id_fish] = fish
    fish_names.append(fish.id_fish)

    for alias in fish.alias:
        fish_map[alias] = fish
