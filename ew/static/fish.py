import json
import os
from re import M

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

common_fish = []
uncommon_fish = []
rare_fish = []
promo_fish = []

rainy_fish = []
night_fish = []
day_fish = []

size_to_reward = {
    "miniscule": 1,
    "small": 2,
    "average": 3,
    "big": 4,
    "huge": 5,
    "colossal": 6
}

rarity_to_reward = {
    "common": 1,
    "uncommon": 2,
    "rare": 3,
    "promo": 4
}

rarity_to_list = {
    "common": common_fish,
    "uncommon": uncommon_fish,
    "rare": rare_fish,
    "promo": promo_fish
}

# A list of fish names.
fish_names = []

# Populate fish map, including all aliases.
for fish in fish_list:
    fish_map[fish.id_fish] = fish
    fish_names.append(fish.id_fish)
    # Categorize fish into their rarities
    rarity_to_list[fish.rarity].append(fish.id_fish)
    if fish.catch_weather == "rainy":
        rainy_fish.append(fish.id_fish)
    if fish.catch_time == "night":
        night_fish.append(fish.id_fish)
    elif fish.catch_time == "day":
        day_fish.append(fish.id_fish)
    for alias in fish.alias:
        fish_map[alias] = fish
