import json
import os
from re import M

from ..model.fish import EwFish

# All the fish, baby!
fish_list = [
    EwFish(
        id_fish = "neoneel",
        str_name = "Neon Eel",
        rarity = "common",
        str_desc = "Its slippery body is bathed in a bright green glow.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "fantaray",
        str_name = "Fanta Ray",
        rarity = "rare",
        str_desc = "Wait a minute, wasn't this the thing that killed that famous guy? Better be careful!",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "thalamuscaranx",
        str_name = "Thalamus Caranx",
        rarity = "uncommon",
        catch_time = "night",
        str_desc = "Finally, a worthy fish emerges.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "fuckshark",
        str_name = "Fuck Shark",
        rarity = "uncommon",
        str_desc = "You recall reading that this thing has the same nutritional value as SUPER WATER FUCK ENERGY.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "sourfish",
        str_name = "Sourfish",
        rarity = "rare",
        str_desc = "It gives you an oddly cynical gaze.",
    ),
    EwFish(
        id_fish = "snakeheadtrout",
        str_name = "Snakehead Trout",
        rarity = "common",
        catch_time = "night",
        str_desc = "It has the body of a trout and the head of a snake. Heavy fuckin' metal.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "gar",
        str_name = "Gar",
        rarity = "uncommon",
        str_desc = "You have the strange urge to wrestle this fish into submission. You almost resist it.",
    ),
    EwFish(
        id_fish = "clownfish",
        str_name = "Clownfish",
        rarity = "rare",
        catch_time = "day",
        str_desc = "Its face kinda looks like a clown if you squint.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "seasaint",
        str_name = "Seasaint",
        rarity = "rare",
        catch_time = "night",
        str_desc = "It has a beanie on.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "holykrakerel",
        str_name = "Holy Krakerel",
        rarity = "uncommon",
        catch_time = "night",
        str_desc = "It looks bovine-adjacent.",
    ),
    EwFish(
        id_fish = "seajuggalo",
        str_name = "Sea Juggalo",
        rarity = "uncommon",
        catch_time = "day",
        str_desc = "This motherfucker definitely has some sick fuckin' musical taste.",
    ),
    EwFish(
        id_fish = "plebefish",
        str_name = "Plebefish",
        rarity = "rare",
        str_desc = "God. This fucking retard. It just doesn't fucking GET it.",
    ),
    EwFish(
        id_fish = "bufferfish",
        str_name = "Bufferfish",
        rarity = "uncommon",
        str_desc = "This fish has the ability to lag out predators in order to get away.",
    ),
    EwFish(
        id_fish = "slimesquid",
        str_name = "Slime Squid",
        rarity = "common",
        str_desc = "It's just a green squid.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "jellyturkeyfish",
        str_name = "Jelly Turkeyfish",
        rarity = "common",
        str_desc = "You nearly prick your finger on one of the many of the venomous spines on its back.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "iridescentsnapper",
        str_name = "Iridescent Snapper",
        rarity = "uncommon",
        str_desc = "Its scales change color if you shake it. Fun.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "barredkatanajaw",
        str_name = "Barred Katanajaw",
        rarity = "uncommon",
        str_desc = "Its stripes make it look vaguely Japanese.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "doublestuffedflounder",
        str_name = "Double-Stuffed Flounder",
        rarity = "promo",
        str_desc = "No one out-Flounders this fish.",
    ),
    EwFish(
        id_fish = "seacolonel",
        str_name = "Sea Colonel",
        rarity = "promo",
        str_desc = "This fish definitely looks like its dropped out of high school.",
    ),
    EwFish(
        id_fish = "marlinsupreme",
        str_name = "Marlin Supreme",
        rarity = "promo",
        str_desc = "Live mas.",
    ),
    EwFish(
        id_fish = "relicanth",
        str_name = "Relicanth",
        rarity = "rare",
        catch_weather = "rain",
        str_desc = "It doesn't have teeth.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "stunfisk",
        str_name = "Stunfisk",
        rarity = "rare",
        catch_weather = "rain",
        str_desc = "Its hide is so tough it can be stepped on by Pink Whale without being injured.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "bathyphysaheadshark",
        str_name = "Bathyphysahead Shark",
        rarity = "promo",
        str_desc = "This one looks fucking terrifying. I'm serious, search for 'bathyphysa' on Google.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "anglershark",
        str_name = "Angler Shark",
        rarity = "rare",
        catch_time = "night",
        str_desc = "It has a little poudrin on its head.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "bigtopoctopus",
        str_name = "Big Top Octopus",
        rarity = "rare",
        catch_time = "day",
        str_desc = "It kinda looks like a circus tent.",
    ),
    EwFish(
        id_fish = "souroctopus",
        str_name = "Sour Octopus",
        rarity = "uncommon",
        str_desc = "It would rather be in a jar.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "octohuss",
        str_name = "Octohuss",
        rarity = "promo",
        str_desc = "Don't let it near a horse. Or a drawing tablet.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "jarocephalopod",
        str_name = "Jar O' Cephalopod",
        rarity = "common",
        str_desc = "It looks content in there.",
    ),
    EwFish(
        id_fish = "dab",
        str_name = "Dab",
        rarity = "common",
        catch_time = "night",
        str_desc = "Pretty Killercore.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "thrash",
        str_name = "Thrash",
        rarity = "common",
        catch_time = "day",
        str_desc = "Pretty Rowdycore.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "arsonfish",
        str_name = "Arsonfish",
        rarity = "common",
        str_desc = "Its scales are so hot, you continuously toss the fish upwards to avoid getting burned.",
    ),
    EwFish(
        id_fish = "cruna",
        str_name = "Cruna",
        rarity = "common",
        str_desc = "It's just a green tuna fish.",
    ),
    EwFish(
        id_fish = "modelopole",
        str_name = "Modelopole",
        rarity = "common",
        str_desc = "UH-OH, IT'S MODELOPOLE TIME!",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "universefrog",
        str_name = "Universe Frog",
        rarity = "promo",
        str_desc = "It's a huge fuckin' color-changing frog.",
    ),
    EwFish(
        id_fish = "galaxyfrog",
        str_name = "Galaxy Frog",
        rarity = "rare",
        str_desc = "It's a big fuckin' color-changing frog.",
    ),
    EwFish(
        id_fish = "solarfrog",
        str_name = "Solar Frog",
        rarity = "rare",
        catch_time = "day",
        str_desc = "Don't stare at it!",
    ),
    EwFish(
        id_fish = "lunarfrog",
        str_name = "Lunar Frog",
        rarity = "rare",
        catch_time = "night",
        str_desc = "It's said to control the waves of the Slime Sea.",
    ),
    EwFish(
        id_fish = "killifish",
        str_name = "Killifish",
        rarity = "common",
        catch_time = "night",
        str_desc = "Apparently there are 1270 different species of Killifish.",
    ),
    EwFish(
        id_fish = "lee",
        str_name = "Lee",
        rarity = "uncommon",
        str_desc = "Oh shit, it's Lee!",
    ),
    EwFish(
        id_fish = "palemunch",
        str_name = "Pale Munch",
        rarity = "common",
        catch_time = "day",
        str_desc = "This fish looks like it needs some sleep.",
    ),
    EwFish(
        id_fish = "moldfish",
        str_name = "Moldfish",
        rarity = "common",
        str_desc = "It's said to have the memory capacity of 16 GB.",
    ),
    EwFish(
        id_fish = "neonjuvie",
        str_name = "Neon Juvie",
        rarity = "common",
        str_desc = "Pretty Juviecore.",
    ),
    EwFish(
        id_fish = "greengill",
        str_name = "Greengill",
        rarity = "uncommon",
        str_desc = "Its gills are green.",
    ),
    EwFish(
        id_fish = "corpsecarp",
        str_name = "Corpse Carp",
        rarity = "common",
        str_desc = "It smells like a rotting fish.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "slimewatergoby",
        str_name = "Slimewater Goby",
        rarity = "rare",
        str_desc = "This little fucko hates fun.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "nibblefish",
        str_name = "Nibblefish",
        rarity = "rare",
        str_desc = "It looks hungry.",
    ),
    EwFish(
        id_fish = "piranhoid",
        str_name = "Piranhoid",
        rarity = "uncommon",
        str_desc = "This fish is said to occasionally jump out of the water and bite unsuspecting slimeoids.",
    ),
    EwFish(
        id_fish = "torrentfish",
        str_name = "Torrentfish",
        rarity = "uncommon",
        str_desc = "This fish looks like it doesn't pay for ANY of its anime.",
    ),
    EwFish(
        id_fish = "barbeln8",
        str_name = "Barbel N8",
        rarity = "common",
        catch_time = "night",
        str_desc = "It looks like it could run a shady corporation.",
    ),
    EwFish(
        id_fish = "mace",
        str_name = "Mace",
        rarity = "uncommon",
        str_desc = "These fish are called Mud Carps in Nu Hong Kong.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "blacklimesalmon",
        str_name = "Black Lime Salmon",
        rarity = "rare",
        str_desc = "Kinda smells like Black Limes.",
    ),
    EwFish(
        id_fish = "char",
        str_name = "Char",
        rarity = "uncommon",
        str_desc = "These fish migrated south after the North Pole was nuked.",
    ),
    EwFish(
        id_fish = "arijuana",
        str_name = "Arijuana",
        rarity = "uncommon",
        str_desc = "These fish are banned from the USA.",
    ),
    EwFish(
        id_fish = "thebassedgod",
        str_name = "The Bassed God",
        rarity = "promo",
        str_desc = "This is The Bassed God. He's gonna fuck your bitch.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "flarp",
        str_name = "Flarp",
        rarity = "uncommon",
        str_desc = "It's a carp thats really flexible.",
    ),
    EwFish(
        id_fish = "clouttrout",
        str_name = "Clout Trout",
        rarity = "common",
        str_desc = "This fish has the eyes of a winner.",
    ),
    EwFish(
        id_fish = "slimekoi",
        str_name = "Slimekoi",
        rarity = "common",
        str_desc = "Slimekoi is a level 3 slimeboi.",
    ),
    EwFish(
        id_fish = "deadkoi",
        str_name = "Deadkoi",
        rarity = "common",
        str_desc = "Deadkoi is a level 3 deadboi.",
    ),
    EwFish(
        id_fish = "magicksdorado",
        str_name = "magicksDorado",
        rarity = "uncommon",
        catch_time = "night",
        str_desc = "No relation.",
    ),
    EwFish(
        id_fish = "straubling",
        str_name = "Straubling",
        rarity = "uncommon",
        catch_time = "day",
        str_desc = "No relation.",
    ),
    EwFish(
        id_fish = "croach",
        str_name = "Croach",
        rarity = "uncommon",
        str_desc = "It's very uncommon in North America.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "slimesmelt",
        str_name = "Slime Smelt",
        rarity = "common",
        str_desc = "It could sure use a bath.",
    ),
    EwFish(
        id_fish = "neomilwaukianmittencrab",
        str_name = "Neo-Milwaukian Mitten Crab",
        rarity = "uncommon",
        str_desc = "Known for their furry claws, Mitten Crabs were considered an invasive species, but eventually people stopped caring about that because they had bigger fish to fry (metaphorically, of course).",
    ),
    EwFish(
        id_fish = "yellowslash",
        str_name = "Yellow Slash",
        rarity = "uncommon",
        str_desc = "This fish is the successor to Classic Milwaukee's Yellow Perch.",
    ),
    EwFish(
        id_fish = "sweetfish",
        str_name = "Sweet Fish",
        rarity = "rare",
        catch_time = "day",
        str_desc = "Also known as Gillanaks.",
    ),
    EwFish(
        id_fish = "hardboiledturtle",
        str_name = "Hard Boiled Turtle",
        rarity = "common",
        str_desc = "This radical dude doesn't take shit from anyone.",
    ),
    EwFish(
        id_fish = "oozesalmon",
        str_name = "Ooze Salmon",
        rarity = "common",
        str_desc = "You wonder how good it would taste on a bagel.",
    ),
    EwFish(
        id_fish = "toxicpike",
        str_name = "Toxic Pike",
        rarity = "common",
        str_desc = "Don't let it bite you.",
    ),
    EwFish(
        id_fish = "uncookedkingpincrab",
        str_name = "Kingpin Crab",
        rarity = "rare",
        str_desc = "It reminds you of your last meal at Red Mobster.",
        slime = "saltwater",
    ),
    EwFish(
        id_fish = "regiarapaima",
        str_name = "Regiarapaima",
        rarity = "promo",
        str_desc = "Regigas sends its regards.",
    ),
    EwFish(
        id_fish = "kinkfish",
        str_name = "Kinkfish",
        rarity = "rare",
        str_desc = "This fish looks like it's down to get wacky.",
    ),
    EwFish(
        id_fish = "nuclearbream",
        str_name = "Nuclear Bream",
        rarity = "uncommon",
        str_desc = "Not to be confused with BREEAM, although this fish looks like its in the mood for assessing shit.",
    ),
    EwFish(
        id_fish = "killercod",
        str_name = "Killer Cod",
        rarity = "common",
        catch_time = "night",
        str_desc = "Quite Killercore.",
    ),
    EwFish(
        id_fish = "pinksnapper",
        str_name = "Pink Snapper",
        rarity = "common",
        catch_time = "day",
        str_desc = "Quite Rowdycore.",
    ),
    EwFish(
        id_fish = "angerfish",
        str_name = "Angerfish",
        rarity = "rare",
        str_desc = "It doesn't look very happy to be here.",
    ),
    EwFish(
        id_fish = "flopfish",
        str_name = "Flop Fish",
        rarity = "uncommon",
        str_desc = "It's floppin'.",
    ),
    EwFish(
        id_fish = "cardboardcrab",
        str_name = "Cardboard Crab",
        rarity = "uncommon",
        str_desc = "It originated when Shigeru Miyamoto decided to splice crab DNA with a Nintendo Labo Piano.",
    ),
    EwFish(
        id_fish = "easysardines",
        str_name = "Easy Sardines",
        rarity = "rare",
        str_desc = "In terms of difficulty, this little bitch looks real low on the rungs.",
    ),
    EwFish(
        id_fish = "largebonedlionfish",
        str_name = "Large-Boned Lionfish",
        rarity = "common",
        str_desc = "It's not fat.",
    ),
    EwFish(
        id_fish = "paradoxcrocodile",
        str_name = "Paradox Crocodile",
        rarity = "promo",
        str_desc = "It has no arms and a blue bandana.",
        slime = "freshwater",
    ),
    EwFish(
        id_fish = "mertwink",
        str_name = "Mertwink",
        rarity = "rare",
        catch_weather = "rain",
        str_desc = "Rejoice, horndogs.",
    ),
    EwFish(
        id_fish = "negaslimesquid",
        str_name = "Negaslime Squid",
        rarity = "common",
        str_desc = "It's just a black squid, but spooky.",
        slime = "void",
    ),
    EwFish(
        id_fish = "voidfish",
        str_name = "Void Fish",
        rarity = "common",
        str_desc = "Translucent and quiet, it weighs less than nothing.",
        slime = "void",
    ),
    EwFish(
        id_fish = "corpsefish",
        str_name = "Corpse Fish",
        rarity = "common",
        str_desc = "It's just laying there.",
        slime = "void",
    ),
    EwFish(
        id_fish = "bonedoctopus",
        str_name = "Boned Octopus",
        rarity = "common",
        str_desc = "Its tentacles crack while wriggling.",
        slime = "void",
    ),
    EwFish(
        id_fish = "kaleidoscuttle",
        str_name = "Kaleidoscuttle",
        rarity = "uncommon",
        str_desc = "Whoa, dude.",
        slime = "void",
    ),
    EwFish(
        id_fish = "deathfish",
        str_name = "Death Fish",
        rarity = "uncommon",
        str_desc = "It is the beast it worships.",
        slime = "void",
    ),
    EwFish(
        id_fish = "artifish",
        str_name = "Artifish",
        rarity = "uncommon",
        str_desc = "It's chromatically abhorrent.",
        slime = "void",
    ),
    EwFish(
        id_fish = "ghostfish",
        str_name = "Ghost Fish",
        rarity = "uncommon",
        str_desc = "You remind yourself not to dip it in coleslaw.",
        slime = "void",
    ),
    EwFish(
        id_fish = "boxcrab",
        str_name = "Box Crab",
        rarity = "rare",
        str_desc = "Hiding in its own little fort.",
        slime = "void",
    ),
    EwFish(
        id_fish = "bluejelly",
        str_name = "Blue Jelly",
        rarity = "rare",
        str_desc = "Its tentacles look like a mop head.",
        slime = "void",
    ),
    EwFish(
        id_fish = "lichfish",
        str_name = "Lich Fish",
        rarity = "rare",
        str_desc = "What you didn't reel is its phylactery.",
        slime = "void",
    ),
    EwFish(
        id_fish = "logfish",
        str_name = "Logfish",
        rarity = "promo",
        str_desc = "WOODEN AND HORRIFYING.",
        slime = "void",
    ),
    EwFish(
        id_fish = "highmonkfish",
        str_name = "High Monkfish",
        rarity = "promo",
        str_desc = "First of its creed.",
        slime = "void",
    ),
]


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
