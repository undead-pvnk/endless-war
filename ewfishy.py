import random
import asyncio
import ewcfg
import ewutils
import ewitem

from ewmarket import EwMarket
from ew import EwUser
from ewcfg import fish_list

class EwFisher:
    fishing = False
    bite = False
    current_fish = ""

fishers = {}

# A map of id_fish to EwFish objects.
fish_map = {}

# A list of fish names
fish_names = []

# Populate fish map.
for fish in fish_list:
    fish_map[fish.id_fish] = fish
    fish_names.append(fish.id_fish)

# Randomly generates a fish
def gen_fish(x):
    all_fish = fish_names
    market_data = x
    if market_data.clock < 20 or market_data.clock > 5:
        for fish in all_fish:
            if fish_map[fish].catch_time == "n":
                all_fish.remove(fish)
    if market_data.clock < 8 or market_data.clock > 17:
        for fish in all_fish:
            if fish_map[fish].catch_time == "d":
                all_fish.remove(fish)
    fish_number = random.randint(0, 99)
    if fish_number >= 0 and fish_number < 5:
        fish = "loot"
        return fish
    elif fish_number >= 5 and fish_number < 10:
        for fish in all_fish:
            if fish_map[fish].str_size != "m":
                all_fish.remove(fish)
        fish = random.choice(all_fish)
        return fish
    elif fish_number >= 10 and fish_number < 30:
        for fish in all_fish:
            if fish_map[fish].str_size != "s":
                all_fish.remove(fish)
        fish = random.choice(all_fish)
        return fish
    elif fish_number >= 30 and fish_number < 74:
        for fish in all_fish:
            if fish_map[fish].str_size != "a":
                all_fish.remove(fish)
        fish = random.choice(all_fish)
        return fish
    elif fish_number >= 74 and fish_number < 89:
        for fish in all_fish:
            if fish_map[fish].str_size != "b":
                all_fish.remove(fish)
        fish = random.choice(all_fish)
        return fish
    elif fish_number >= 89 and fish_number < 99:
        for fish in all_fish:
            if fish_map[fish].str_size != "h":
                all_fish.remove(fish)
        fish = random.choice(all_fish)
        return fish
    else:
        for fish in all_fish:
            if fish_map[fish].str_size != "c":
                all_fish.remove(fish)
        fish = random.choice(all_fish)
        return fish

# Generates text for when a fish bites based on the size class.

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

    # Enlisted players only fish at certain times.
    if user_data.life_state == ewcfg.life_state_enlisted:
        if user_data.faction == ewcfg.faction_rowdys and (market_data.clock < 8 or market_data.clock > 17):
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                     "Rowdies only fish in the daytime. Wait for full daylight at 8am.".format(
                                                                                                         ewcfg.cmd_revive)))

        if user_data.faction == ewcfg.faction_killers and (market_data.clock < 20 and market_data.clock > 5):
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                     "Killers only fish under cover of darkness. Wait for nightfall at 8pm.".format(
                                                                                                         ewcfg.cmd_revive)))

    # Only fish at The Pier
    if cmd.message.channel.name in ewcfg.channel_thepier:
        if user_data.hunger >= ewutils.hunger_max_bylevel(user_data.slimelevel):
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                     "You've exhausted yourself from fishing. You'll need some refreshment before getting back to work."))
        else:
            fisher.current_fish = gen_fish(market_data)
            if fisher.current_fish == "loot":
                text = "You feel a distinctly inanimate tug at your fishing pole!"
            elif fish_map[fisher.current_fish].str_size == "m":
                text = "You feel a wimpy tug at your fishing pole!"
            elif fish_map[fisher.current_fish].str_size == "s":
                text = "You feel a mediocre tug at your fishing pole!"
            elif fish_map[fisher.current_fish].str_size == "a":
                text = "You feel a modest tug at your fishing pole!"
            elif fish_map[fisher.current_fish].str_size == "b":
                text = "You feel a mildly threatening tug at your fishing pole!"
            elif fish_map[fisher.current_fish].str_size == "h":
                text = "You feel a startlingly strong tug at your fishing pole!"
            else:
                text = "You feel a tug at your fishing pole so intense that you nearly get swept off your feet!"
            bite_text = text
            bite_text += " **!REEL NOW!!!!!**"
            fisher.fishing = True
            await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                     "You cast your fishing line into the vast Slime Sea."))

            while True:
                if user_data.poi != "thepier":
                    fisher.fishing = False
                    return
                if fisher.fishing == False:
                    return
                await asyncio.sleep(60)
                if 1 != random.randint(1,10):
                    await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, random.choice(nobite_text)))
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
                return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                  "The fish got away..."))

    else:
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                 "You can't fish here. Go to The Pier."))

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
    # Enlisted players only fish at certain times.
    if user_data.life_state == ewcfg.life_state_enlisted:
        if user_data.faction == ewcfg.faction_rowdys and (market_data.clock < 8 or market_data.clock > 17):
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                     "Rowdies only fish in the daytime. Wait for full daylight at 8am."))

        if user_data.faction == ewcfg.faction_killers and (market_data.clock < 20 and market_data.clock > 5):
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                     "Killers only fish under cover of darkness. Wait for nightfall at 8pm."))
    if cmd.message.channel.name in ewcfg.channel_thepier:
        # Players who haven't cast a line cannot reel.
        if fisher.fishing == False:
            return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                         "You haven't cast your hook yet. Try !cast."))
        # If a fish isn't biting, then a player reels in nothing.
        elif fisher.bite == False and fisher.fishing == True:
            fisher.current_fish=""
            fisher.fishing = False
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
            user_data.persist()
    else:
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author,
                                                                                                 "You can't fish here. Go to The Pier."))