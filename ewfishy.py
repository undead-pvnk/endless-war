import random
import asyncio
import time
import ewcfg
import ewutils
import ewitem


from ewmarket import EwMarket
from ew import EwUser
from ewitem import EwItem

class EwFisher:
    fishing = False
    bite = False
    current_fish = ""
    pier = ""
    bait = False

fishers = {}

class EwFish:
    # A unique name for the fish. This is used in the database and typed by
    # users, so it should be one word, all lowercase letters.
    id_fish = ""

    # Name of fish.
    str_name = ""

    # Size of fish.
    str_size = ""

    # When it can be caught.
    catch_time = None

    # Flavor text upon catch.
    flavor = ""

    # What type of slimewater it resides in (None means either).
    slime = None

    def __init__(
            self,
            id_fish = "",
            str_name = "",
            str_size = "",
            catch_time = None,
            flavor = "",
            slime = None
    ):
        self.id_fish = id_fish
        self.str_name = str_name
        self.str_size = str_size
        self.catch_time = catch_time
        self.flavor = flavor
        self.slime = slime

# All the fish, baby!
fish_list = [
    EwFish(
        id_fish="neoneel",
        str_name="Neon Eel",
        str_size="a",
        catch_time=None,
        flavor="Its slippery body is bathed in a bright green glow.",
        slime="s"
    ),
    EwFish(
        id_fish="fantaray",
        str_name="Fanta Ray",
        str_size="h",
        catch_time=None,
        flavor="Wait a minute, wasn't this the thing that killed that famous guy? Better be careful!",
        slime="s"
    ),
    EwFish(
        id_fish="thalamuscaranx",
        str_name="Thalamus Caranx",
        str_size="s",
        catch_time="n",
        flavor="Finally, a worthy fish emerges.",
        slime="f"
    ),
    EwFish(
        id_fish="fuckshark",
        str_name="Fuck Shark",
        str_size="b",
        catch_time=None,
        flavor="You recall reading that this thing has the same nutritional value as SUPER WATER FUCK ENERGY.",
        slime="s"
    ),
    EwFish(
        id_fish="sourfish",
        str_name="Sourfish",
        str_size="m",
        catch_time=None,
        flavor="It gives you an oddly cynical gaze."
    ),
    EwFish(
        id_fish="snakeheadtrout",
        str_name="Snakehead Trout",
        str_size="a",
        catch_time="n",
        flavor="It has the body of a trout and the head of a snake. Heavy fuckin' metal.",
        slime="f"
    ),
    EwFish(
        id_fish="gar",
        str_name="Gar",
        str_size="b",
        catch_time=None,
        flavor="You have the strange urge to wrestle this fish into submission. You almost resist it."
    ),
    EwFish(
        id_fish="clownfish",
        str_name="Clownfish",
        str_size="m",
        catch_time="d",
        flavor="Its face kinda looks like a clown if you squint.",
        slime="s"
    ),
    EwFish(
        id_fish="seasaint",
        str_name="Seasaint",
        str_size="m",
        catch_time="n",
        flavor="It has a beanie on.",
        slime="s"
    ),
    EwFish(
        id_fish="holykrakerel",
        str_name="Holy Krakerel",
        str_size="s",
        catch_time="n",
        flavor="It looks bovine-adjacent."
    ),
    EwFish(
        id_fish="seajuggalo",
        str_name="Sea Juggalo",
        str_size="b",
        catch_time="d",
        flavor="This motherfucker definitely has some sick fuckin' musical taste."
    ),
    EwFish(
        id_fish="plebefish",
        str_name="Plebefish",
        str_size="m",
        catch_time=None,
        flavor="God. This fucking retard. It just doesn't fucking GET it."
    ),
    EwFish(
        id_fish="bufferfish",
        str_name="Bufferfish",
        str_size="s",
        catch_time=None,
        flavor="This fish has the ability to lag out predators in order to get away."
    ),
    EwFish(
        id_fish="slimesquid",
        str_name="Slime Squid",
        str_size="a",
        catch_time=None,
        flavor="It's just a green squid.",
        slime="s"
    ),
    EwFish(
        id_fish="jellyturkeyfish",
        str_name="Jelly Turkeyfish",
        str_size="a",
        catch_time=None,
        flavor="You nearly prick your finger on one of the many of the venomous spines on its back.",
        slime="f"
    ),
    EwFish(
        id_fish="iridescentsnapper",
        str_name="Iridescent Snapper",
        str_size="b",
        catch_time=None,
        flavor="Its scales change color if you shake it. Fun.",
        slime="f"
    ),
    EwFish(
        id_fish="barredkatanajaw",
        str_name="Barred Katanajaw",
        str_size="b",
        catch_time=None,
        flavor="Its stripes make it look vaguely Japanese.",
        slime="f"
    ),
    EwFish(
        id_fish="doublestuffedflounder",
        str_name="Double-Stuffed Flounder",
        str_size="c",
        catch_time=None,
        flavor="No one out-Flounders this fish."
    ),
    EwFish(
        id_fish="seacolonel",
        str_name="Sea Colonel",
        str_size="c",
        catch_time=None,
        flavor="This fish definitely looks like its dropped out of high school."
    ),
    EwFish(
        id_fish="marlinsupreme",
        str_name="Marlin Supreme",
        str_size="c",
        catch_time=None,
        flavor="Live mas."
    ),
    EwFish(
        id_fish="relicanth",
        str_name="Relicanth",
        str_size="h",
        catch_time="r",
        flavor="It doesn't have teeth.",
        slime="s"
    ),
    EwFish(
        id_fish="stunfisk",
        str_name="h",
        str_size="Stunfisk",
        catch_time="r",
        flavor="Its hide is so tough it can be stepped on by Connor without being injured.",
        slime="f"
    ),
    EwFish(
        id_fish="bathyphysaheadshark",
        str_name="Bathyphysahead Shark",
        str_size="c",
        catch_time=None,
        flavor="This one looks fucking terrifying. I'm serious, search for 'bathyphysa' on Google.",
        slime="s"
    ),
    EwFish(
        id_fish="anglershark",
        str_name="Angler Shark",
        str_size="h",
        catch_time="n",
        flavor="It has a little poudrin on its head.",
        slime="s"
    ),
    EwFish(
        id_fish="bigtopoctopus",
        str_name="Big Top Octopus",
        str_size="h",
        catch_time="d",
        flavor="It kinda looks like a circus tent."
    ),
    EwFish(
        id_fish="souroctopus",
        str_name="Sour Octopus",
        str_size="b",
        catch_time=None,
        flavor="It would rather be in a jar.",
        slime="f"
    ),
    EwFish(
        id_fish="octohuss",
        str_name="Octohuss",
        str_size="c",
        catch_time=None,
        flavor="Don't let it near a horse. Or a drawing tablet.",
        slime="s"
    ),
    EwFish(
        id_fish="jarocephalopod",
        str_name="Jar O' Cephalopod",
        str_size="a",
        catch_time=None,
        flavor="It looks content in there."
    ),
    EwFish(
        id_fish="dab",
        str_name="Dab",
        str_size="a",
        catch_time="n",
        flavor="Pretty Killercore.",
        slime="f"
    ),
    EwFish(
        id_fish="thrash",
        str_name="Thrash",
        str_size="a",
        catch_time="d",
        flavor="Pretty Rowdycore.",
        slime="f"
    ),
    EwFish(
        id_fish="arsonfish",
        str_name="Arsonfish",
        str_size="a",
        catch_time=None,
        flavor="Its scales are so hot, you continuously toss the fish upwards to avoid getting burned."
    ),
    EwFish(
        id_fish="cruna",
        str_name="Cruna",
        str_size="a",
        catch_time=None,
        flavor="It's just a green tuna fish."

    ),
    EwFish(
        id_fish="modelopole",
        str_name="Modelopole",
        str_size="a",
        catch_time=None,
        flavor="UH-OH, IT'S MODELOPOLE TIME!",
        slime="f"
    ),
    EwFish(
        id_fish="universefrog",
        str_name="Universe Frog",
        str_size="c",
        catch_time=None,
        flavor="It's a huge fuckin' color-changing frog."
    ),
    EwFish(
        id_fish="galaxyfrog",
        str_name="Galaxy Frog",
        str_size="h",
        catch_time=None,
        flavor="It's a big fuckin' color-changing frog."
    ),
    EwFish(
        id_fish="solarfrog",
        str_name="Solar Frog",
        str_size="h",
        catch_time="d",
        flavor="Don't stare at it!"
    ),
    EwFish(
        id_fish="lunarfrog",
        str_name="Lunar Frog",
        str_size="h",
        catch_time="n",
        flavor="It's said to control the waves of the Slime Sea."
    ),
    EwFish(
        id_fish="killifish",
        str_name="Killifish",
        str_size="a",
        catch_time="n",
        flavor="Apparently there are 1270 different species of Killifish."
    ),
    EwFish(
        id_fish="lee",
        str_name="Lee",
        str_size="s",
        catch_time=None,
        flavor="Oh shit, it's Lee!"
    ),
    EwFish(
        id_fish="palemunch",
        str_name="Pale Munch",
        str_size="a",
        catch_time="d",
        flavor="This fish looks like it needs some sleep."
    ),
    EwFish(
        id_fish="moldfish",
        str_name="Moldfish",
        str_size="a",
        catch_time=None,
        flavor="It's said to have the memory capacity of 16 GB."
    ),
    EwFish(
        id_fish="neonjuvie",
        str_name="Neon Juvie",
        str_size="a",
        catch_time=None,
        flavor="Pretty Juviecore."
    ),
    EwFish(
        id_fish="greengill",
        str_name="Greengill",
        str_size="s",
        catch_time=None,
        flavor="Its gills are green."
    ),
    EwFish(
        id_fish="corpsecarp",
        str_name="Corpse Carp",
        str_size="a",
        catch_time=None,
        flavor="It smells like a rotting fish.",
        slime="f"
    ),
    EwFish(
        id_fish="slimewatergoby",
        str_name="Slimewater Goby",
        str_size="m",
        catch_time=None,
        flavor="This little fucko hates fun.",
        slime="s"
    ),
    EwFish(
        id_fish="nibblefish",
        str_name="Nibblefish",
        str_size="m",
        catch_time=None,
        flavor="It looks hungry."
    ),
    EwFish(
        id_fish="piranhoid",
        str_name="Piranhoid",
        str_size="s",
        catch_time=None,
        flavor="This fish is said to occasionally jump out of the water and bite unsuspecting slimeoids."
    ),
    EwFish(
        id_fish="torrentfish",
        str_name="Torrentfish",
        str_size="b",
        catch_time=None,
        flavor="This fish looks like it doesn't pay for ANY of its anime."
    ),
    EwFish(
        id_fish="barbeln8",
        str_name="Barbel N8",
        str_size="a",
        catch_time="n",
        flavor="It looks like it could run a shady corporation."
    ),
    EwFish(
        id_fish="mace",
        str_name="Mace",
        str_size="s",
        catch_time=None,
        flavor="These fish are called Mud Carps in Nu Hong Kong.",
        slime="f"
    ),
    EwFish(
        id_fish="blacklimesalmon",
        str_name="Black Lime Salmon",
        str_size="h",
        catch_time=None,
        flavor="Kinda smells like Black Limes."
    ),
    EwFish(
        id_fish="char",
        str_name="Char",
        str_size="s",
        catch_time=None,
        flavor="These fish migrated south after the North Pole was nuked."
    ),
    EwFish(
        id_fish="arijuana",
        str_name="Arijuana",
        str_size="s",
        catch_time=None,
        flavor="These fish are banned from the USA."
    ),
    EwFish(
        id_fish="thebassedgod",
        str_name="The Bassed God",
        str_size="c",
        catch_time=None,
        flavor="This is The Bassed God. He's gonna fuck your bitch.",
        slime="s"
    ),
    EwFish(
        id_fish="flarp",
        str_name="Flarp",
        str_size="s",
        catch_time=None,
        flavor="It's a carp thats really flexible."
    ),
    EwFish(
        id_fish="clouttrout",
        str_name="Clout Trout",
        str_size="a",
        catch_time=None,
        flavor="This fish has the eyes of a winner."
    ),
    EwFish(
        id_fish="slimekoi",
        str_name="Slimekoi",
        str_size="a",
        catch_time=None,
        flavor="Slimekoi is a level 3 slimeboi."
    ),
    EwFish(
        id_fish="deadkoi",
        str_name="Deadkoi",
        str_size="a",
        catch_time=None,
        flavor="Deadkoi is a level 3 deadboi."
    ),
    EwFish(
        id_fish="magicksdorado",
        str_name="magicksDorado",
        str_size="b",
        catch_time="n",
        flavor="No relation."
    ),
    EwFish(
        id_fish="straubling",
        str_name="Straubling",
        str_size="b",
        catch_time="d",
        flavor="No relation."
    ),
    EwFish(
        id_fish="croach",
        str_name="Croach",
        str_size="s",
        catch_time=None,
        flavor="It's very uncommon in North America.",
        slime="f"
    ),
    EwFish(
        id_fish="slimesmelt",
        str_name="Slime Smelt",
        str_size="a",
        catch_time=None,
        flavor="It could sure use a bath."
    ),
    EwFish(
        id_fish="neomilwaukianmittencrab",
        str_name="Neo-Milwaukian Mitten Crab",
        str_size="b",
        catch_time=None,
        flavor="Known for their furry claws, Mitten Crabs were considered an invasive species, but eventually people stopped caring about that because they had bigger fish to fry (metaphorically, of course)."
    ),
    EwFish(
        id_fish="yellowslash",
        str_name="Yellow Slash",
        str_size="s",
        catch_time=None,
        flavor="This fish is the successor to Classic Milwaukee's Yellow Perch."
    ),
    EwFish(
        id_fish="sweetfish",
        str_name="sweet fish",
        str_size="m",
        catch_time="d",
        flavor="Also known as Gillanaks."
    ),
    EwFish(
        id_fish="hardboiledturtle",
        str_name="Hard Boiled Turtle",
        str_size="a",
        catch_time=None,
        flavor="This radical dude doesn't take shit from anyone."
    ),
    EwFish(
        id_fish="oozesalmon",
        str_name="Ooze Salmon",
        str_size="a",
        catch_time=None,
        flavor="You wonder how good it would taste on a bagel."
    ),
    EwFish(
        id_fish="toxicpike",
        str_name="Toxic Pike",
        str_size="a",
        catch_time=None,
        flavor="Don't let it bite you."
    ),
    EwFish(
        id_fish="kingpincrab",
        str_name="Kingpin Crab",
        str_size="h",
        catch_time=None,
        flavor="It reminds you of your last meal at Red Mobster.",
        slime="s"
    ),
    EwFish(
        id_fish="regiarapaima",
        str_name="Regiarapaima",
        str_size="c",
        catch_time=None,
        flavor="Regigas sends its regards."
    ),
    EwFish(
        id_fish="kinkfish",
        str_name="Kinkfish",
        str_size="h",
        catch_time=None,
        flavor="This fish looks like it's down to get wacky."
    ),
    EwFish(
        id_fish="nuclearbream",
        str_name="Nuclear Bream",
        str_size="s",
        catch_time=None,
        flavor="Not to be confused with BREEAM, although this fish looks like its in the mood for assessing shit."
    ),
    EwFish(
        id_fish="killercod",
        str_name="Killer Cod",
        str_size="a",
        catch_time="n",
        flavor="Quite Killercore."
    ),
    EwFish(
        id_fish="pinksnapper",
        str_name="Pink Snapper",
        str_size="a",
        catch_time="d",
        flavor="Quite Rowdycore."
    ),
    EwFish(
        id_fish="angerfish",
        str_name="Angerfish",
        str_size="h",
        catch_time=None,
        flavor="It doesn't look very happy to be here."
    ),
    EwFish(
        id_fish="flopfish",
        str_name="Flop Fish",
        str_size="b",
        catch_time=None,
        flavor="It's floppin'."
    ),
    EwFish(
        id_fish="cardboardcrab",
        str_name="Cardboard Crab",
        str_size="b",
        catch_time=None,
        flavor="It originated when Shigeru Miyamoto decided to splice crab DNA with Nintendo Labo Piano."
    ),
    EwFish(
        id_fish="easysardines",
        str_name="Easy Sardines",
        str_size="m",
        catch_time=None,
        flavor="In terms of difficulty, this little bitch looks real low on the rungs."
    ),
    EwFish(
        id_fish="largebonedlionfish",
        str_name="Large-Boned Lionfish",
        str_size="a",
        catch_time=None,
        flavor="It's not fat."
    ),
    EwFish(
        id_fish="paradoxcrocodile",
        str_name="Paradox Crocodile",
        str_size="c",
        catch_time=None,
        flavor="It has no arms and a blue bandana.",
        slime="f"
    )
]

# A map of id_fish to EwFish objects.
fish_map = {}

# A list of fish names
fish_names = []

# Populate fish map.
for fish in fish_list:
    fish_map[fish.id_fish] = fish
    fish_names.append(fish.id_fish)

# Randomly generates a fish
def gen_fish(x, cmd):
    all_fish = []
    fish_number = random.randint(0, 99)
    if fish_number >= 0 and fish_number < 5:
        fish = "loot"
        return fish
    elif fish_number >= 5 and fish_number < 10:
        for fish in fish_names:
            if fish_map[fish].str_size == "m":
                all_fish.append(fish)
    elif fish_number >= 10 and fish_number < 30:
        for fish in fish_names:
            if fish_map[fish].str_size == "s":
                all_fish.append(fish)
    elif fish_number >= 30 and fish_number < 74:
        for fish in fish_names:
            if fish_map[fish].str_size == "a":
                all_fish.append(fish)
    elif fish_number >= 74 and fish_number < 89:
        for fish in fish_names:
            if fish_map[fish].str_size == "b":
                all_fish.append(fish)
    elif fish_number >= 89 and fish_number < 99:
        for fish in fish_names:
            if fish_map[fish].str_size == "h":
                all_fish.append(fish)
    else:
        for fish in fish_names:
            if fish_map[fish].str_size == "c":
                all_fish.append(fish)
    market_data = x
    if market_data.clock < 20 or market_data.clock > 5:
        for fish in all_fish:
            if fish_map[fish].catch_time == "n":
                all_fish.remove(fish)
    elif market_data.clock < 8 or market_data.clock > 17:
        for fish in all_fish:
            if fish_map[fish].catch_time == "d":
                all_fish.remove(fish)
    else:
        for fish in all_fish:
            if fish_map[fish].catch_time != None:
                all_fish.remove(fish)
    if cmd.message.channel.name in ["slimes-end-pier", "ferry"]:
        for fish in all_fish:
            if fish_map[fish].slime == "f":
                all_fish.remove(fish)
    elif cmd.message.channel.name in ["jaywalker-plain-pier", "little-chernobyl-pier"]:
        for fish in all_fish:
            if fish_map[fish].slime == "s":
                all_fish.remove(fish)
    fish = random.choice(all_fish)
    return fish

# Determines bite text
def gen_bite_text(fish):
    if fish == "loot":
        text = "You feel a distinctly inanimate tug at your fishing pole!"
    elif fish_map[fish].str_size == "m":
        text = "You feel a wimpy tug at your fishing pole!"
    elif fish_map[fish].str_size == "s":
        text = "You feel a mediocre tug at your fishing pole!"
    elif fish_map[fish].str_size == "a":
        text = "You feel a modest tug at your fishing pole!"
    elif fish_map[fish].str_size == "b":
        text = "You feel a mildly threatening tug at your fishing pole!"
    elif fish_map[fish].str_size == "h":
        text = "You feel a startlingly strong tug at your fishing pole!"
    else:
        text = "You feel a tug at your fishing pole so intense that you nearly get swept off your feet!"
    text += " **!REEL NOW!!!!!**"
    return text

# If a fish doesn't bite, send one of these.
nobite_text = [
    "You patiently wait...",
    "You look towards the green Slime Sea horizon...",
    "This is so fucking boring...",
    "You watch your hook bob...",
    "You grow impatient and kick the rotted wooden guard rails...",
    "AUUUUUGH JUST BITE THE FUCKING HOOK ALREADY...",
    "You begin to zone-out a bit..."
]

# Shitty bait that always yields Plebefish
plebe_bait = ['slimentonic', 'slimacolada', 'slimekashot', 'slimynipple', 'slimeonthebeach', 'goobalibre', 'slimymary',
              'water', 'breadsticks', 'taco', 'nachocheesetaco', 'coolranchtaco', 'coleslaw', 'biscuitngravy', 'barbecuesauce',
              'mtndew', 'bajablast', 'codered', 'pitchblack', 'whiteout', 'livewire', 'sparklingwater', 'homefries',
              'friedeggs', 'orangejuice', 'milk', 'sludgeberries', 'pulpgourds', 'joybeans', 'brightshade',
              'direapples', 'razornuts', 'poketubers', 'suganmanuts', 'dankwheat',
              'phosphorpoppies', 'sourpotatoes', 'bloodcabbages', 'pawpaw', 'sludgeberrypancakes',
              'pulpgourdpie', 'joybeanpastemochi', 'brightshadeseeds', 'direapplejuice',
              'razornutbutter', 'jellyfilleddoughnut', 'yourfavoritefood', 'dankwheattoast', 'phosphorpoppiesmuffin',
              'sourpotatofrenchfries', 'bloodcabbagecoleslaw', 'pawpawfood']

""" Casts a line into the Slime Sea """
async def cast(cmd):
    market_data = EwMarket(id_server=cmd.message.author.server.id)
    user_data = EwUser(member=cmd.message.author)
    if cmd.message.author.id not in fishers.keys():
        fishers[cmd.message.author.id] = EwFisher()
    fisher = fishers[cmd.message.author.id]

    # Ghosts cannot fish.
    if user_data.life_state == ewcfg.life_state_corpse:
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                 "You can't fish while you're dead. Try {}.".format(
                                                                                                     ewcfg.cmd_revive)))

    # Players who are already cast a line cannot cast another one.
    if fisher.fishing == True:
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                 "You've already cast a line."))
    # Only fish at The Pier
    if cmd.message.channel.name in [ewcfg.channel_se_pier, ewcfg.channel_jp_pier, ewcfg.channel_lc_pier, ewcfg.channel_ferry]:
        if user_data.hunger >= ewutils.hunger_max_bylevel(user_data.slimelevel):
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                     "You've exhausted yourself from fishing. You'll need some refreshment before getting back to work."))
        else:
            fisher.current_fish = gen_fish(market_data, cmd)
            fisher.fishing = True
            fisher.bait = False
            fisher.pier = user_data.poi
            item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
            author = cmd.message.author
            server = cmd.message.server

            item_sought = ewitem.find_item(item_search=item_search, id_user=author.id, id_server=server.id)

            if item_sought:
                item = EwItem(id_item=item_sought.get('id_item'))
                name = item_sought.get('name')
                if item.item_type == ewcfg.it_food:
                    fisher.bait = True
                    if name in plebe_bait:
                        fisher.current_fish = "plebefish"
                    elif name == "double Original Stuffed Crust® pizza":
                        if random.randrange(5) == 3:
                            fisher.current_fish = "doublestuffedflounder"
                    elif name in ["8-piece bucket of fried chicken", "KFC Family Meal"]:
                        if random.randrange(5) == 3:
                            fisher.current_fish = "seacolonel"
                    elif name in ["SteakVolcanoQuesoMachoRito", "Nacho Supreme"]:
                        if random.randrange(5) == 3:
                            fisher.current_fish = "marlinsupreme"
                    elif name in ["Black Limes", "Black Lime Sour"]:
                        if random.randrange(1) == 1:
                            fisher.current_fish = "blacklimesalmon"
                    elif name in ["Pink Rowddishes", "Pink Rowdatouille"]:
                        if random.randrange(1) == 1:
                            fisher.current_fish = "thrash"
                    elif name in ["Purple Killiflower Crust Pizza", "Purple Killiflower"]:
                        if random.randrange(1) == 1:
                            fisher.current_fish = "dab"
                    elif name == "an Arizonian Kingpin Crab":
                        if random.randrange(5) == 1:
                            fisher.current_fish = "kingpincrab"
                    elif float(item.time_expir if item.time_expir is not None else 0) < time.time():
                        if random.randrange(1) == 1:
                            fisher.current_fish = "plebefish"
                    ewitem.item_delete(item_sought.get('id_item'))
            if fisher.bait == False:
                await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                  "You cast your fishing line into the vast Slime Sea."))
            else:
                await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                  "You attach your {} to the hook as bait and then cast your fishing line into the vast Slime Sea.".format(name)))
            bite_text = gen_bite_text(fisher.current_fish)
            fun = 99
            if fisher.bait == True:
                fun = 69
            bun = 0
            while True:
                damp = random.randrange(fun)
                timer = 0
                while timer <= 60:
                    await asyncio.sleep(1)
                    if user_data.poi != fisher.pier:
                        fisher.fishing = False
                        return
                    if user_data.life_state == ewcfg.life_state_corpse:
                        fisher.fishing = False
                        return
                    if fisher.fishing == False:
                        return
                    timer += 1
                if damp != 1 and damp != 2 and damp != 3 and damp != 4 and damp != 5 and damp != 6 and damp != 7 and damp != 8 and damp != 9 and damp != 10:
                    await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, random.choice(nobite_text)))
                    fun -= 2
                    bun += 1
                    if bun >= 5:
                        fun -= 1
                    if bun >= 15:
                        fun -= 1
                    continue
                else:
                    break
            await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, bite_text))
            fisher.bite = True
            await asyncio.sleep(6)
            if fisher.bite != False:
                fisher.fishing = False
                fisher.bite = False
                fisher.current_fish = ""
                fisher.bait = False
                return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                  "The fish got away..."))

    else:
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                 "You can't fish here. Go to a pier."))

""" Reels in the fishing line. """
async def reel(cmd):
    market_data = EwMarket(id_server=cmd.message.author.server.id)
    user_data = EwUser(member=cmd.message.author)
    if cmd.message.author.id not in fishers.keys():
        fishers[cmd.message.author.id] = EwFisher()
    fisher = fishers[cmd.message.author.id]

    # Ghosts cannot fish.
    if user_data.life_state == ewcfg.life_state_corpse:
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                 "You can't fish while you're dead. Try {}.".format(
                                                                                                     ewcfg.cmd_revive)))
    if cmd.message.channel.name in [ewcfg.channel_se_pier, ewcfg.channel_jp_pier, ewcfg.channel_lc_pier, ewcfg.channel_ferry]:
        # Players who haven't cast a line cannot reel.
        if fisher.fishing == False:
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                         "You haven't cast your hook yet. Try !cast."))
        # If a fish isn't biting, then a player reels in nothing.
        elif fisher.bite == False and fisher.fishing == True:
            fisher.current_fish=""
            fisher.fishing = False
            fisher.pier = ""
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                         "You reeled in too early! Nothing was caught."))
        # On successful reel.
        else:
            if fisher.current_fish == "loot":
                poudrinamount = 1 if random.randint(1, 3) != 1 else 2  # 33% chance of extra drop

                # Create and give slime poudrins
                for pcreate in range(poudrinamount):
                    ewitem.item_create(
                        id_user=cmd.message.author.id,
                        id_server=cmd.message.server.id,
                        item_type=ewcfg.it_slimepoudrin,
                    )
                fisher.fishing = False
                fisher.bite = False
                fisher.current_fish = ""
                fisher.pier = ""
                user_data.hunger += ewcfg.hunger_perfish * ewutils.hunger_cost_mod(user_data.slimelevel)
                user_data.persist()
                if poudrinamount == 1:
                    return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                         "You reeled in a poudrin!"))
                else:
                    return await ewutils.send_message(cmd.client, cmd.message.channel,ewutils.formatMessage(cmd.message.author,
                                                                                                            "You reeled in two poudrins!"))
            size_class = fish_map[fisher.current_fish].str_size
            fish_gain = ewcfg.fish_gain
            if size_class == "m":
                slime_gain = fish_gain * 1
            elif size_class == "s":
                slime_gain = fish_gain * 2
            elif size_class == "a":
                slime_gain = fish_gain * 3
            elif size_class == "b":
                slime_gain = fish_gain * 4
            elif size_class == "h":
                slime_gain = fish_gain * 5
            else:
                slime_gain = fish_gain * 6
            await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                         "You caught a fish! It's a {fish}! {flavor} You absorb it into your slimestream for {slime} slime.".format(
                                                                                                             fish=fish_map[fisher.current_fish].str_name, flavor=fish_map[fisher.current_fish].flavor, slime=str(slime_gain))))
            user_data.change_slimes(n=slime_gain, source=ewcfg.source_fishing)
            user_data.hunger += ewcfg.hunger_perfish * ewutils.hunger_cost_mod(user_data.slimelevel)
            fisher.fishing = False
            fisher.bite = False
            fisher.current_fish = ""
            fisher.pier = ""
            user_data.persist()
    else:
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                 "You can't fish here. Go to The Pier."))
