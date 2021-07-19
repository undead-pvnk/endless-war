import random
import time

from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.static import cfg as ewcfg
from ew.static import fish as static_fish
from ew.static import status as se_static
from ew.static import vendors
from ew.static import weapons as static_weapons
from ew.static import weather as weather_static
from ew.utils import item as itm_utils
from ew.utils import poi as poi_utils
from ew.utils.combat import EwUser


class EwFisher:
    fishing = False
    bite = False
    current_fish = ""
    current_size = ""
    pier = ""
    bait = False
    bait_id = 0
    high = False
    fishing_id = 0
    inhabitant_id = None
    fleshling_reeled = False
    ghost_reeled = False

    def stop(self):
        self.fishing = False
        self.bite = False
        self.current_fish = ""
        self.current_size = ""
        self.pier = ""
        if self.bait == True and self.bait_id != 0:
            bknd_item.item_delete(self.bait_id)
        self.bait = False
        self.bait_id = 0
        self.high = False
        self.fishing_id = 0
        self.inhabitant_id = None
        self.fleshling_reeled = False
        self.ghost_reeled = False


fishers = {}
fishing_counter = 0


# Randomly generates a fish.
def gen_fish(market_data, fisher, has_fishingrod = False, rarity = None, secret_unlocked = False):
    fish_pool = []

    rarity_number = random.randint(0, 100)

    # TODO: reimplement chance to get items in black pond using negapoudrin
    # fragments when any of that shit has any use beyond making staves.
    # just ctrl+f the variable below and remove anything to do with it
    voidfishing = fisher.pier.pier_type == ewcfg.fish_slime_void
    if rarity is None:
        if has_fishingrod:
            if rarity_number >= 0 and rarity_number < 21 and not voidfishing:  # 20%
                rarity = "item"

            elif rarity_number >= 21 and rarity_number < 31:  # 10%
                rarity = "common"

            elif rarity_number >= 31 and rarity_number < 71:  # 40%
                rarity = "uncommon"

            elif rarity_number >= 71 and rarity_number < 91:  # 20%
                rarity = "rare"

            else:  # 10%
                rarity = "promo"

        else:
            if rarity_number >= 0 and rarity_number < 11 and not voidfishing:  # 10%
                rarity = "item"

            elif rarity_number >= 11 and rarity_number < 61:  # 50%
                rarity = "common"

            elif rarity_number >= 61 and rarity_number < 91:  # 30%
                rarity = "uncommon"

            elif rarity_number >= 91 and rarity_number < 100:  # 9%
                rarity = "rare"

            else:  # 1%
                rarity = "promo"
    
    if rarity == "item":
        fish = "item"
        return fish
    else:
        fish_pool.extend(static_fish.rarity_to_list[rarity])

    # Weather exclusive fish
    if market_data.weather != "rainy":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.rainy_fish]
    if market_data.weather != "sunny":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.sunny_fish]
    if market_data.weather != "foggy":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.foggy_fish]
    if market_data.weather != "snow":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.snow_fish]

    # Time exclusive fish
    if 5 < market_data.clock < 20:
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.night_fish]
    elif market_data.clock < 8 or market_data.clock > 17:
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.day_fish]
    else:
        for fish in fish_pool:
            if static_fish.fish_map[fish].catch_time != None:
                fish_pool.remove(fish)

    # Pier type exclusive fish
    if fisher.pier.pier_type == "freshwater":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.salt_fish and fish not in static_fish.void_fish]
    elif fisher.pier.pier_type == "saltwater":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.fresh_fish and fish not in static_fish.void_fish]
    elif fisher.pier.pier_type == "void":
        fish_pool = [fish for fish in fish_pool if fish in static_fish.void_fish]

    fish = random.choice(fish_pool)

    # Get fucked
    if fisher.pier.id_poi == ewcfg.poi_id_juviesrow_pier:
        fish = 'plebefish'

    #TODO you can unlock the secret fish by catching all the other ones
    # secret fish
    if secret_unlocked and random.randint(0, 1000) == 69:
        fish = 'mermaid'

    return fish


# Determines the size of the fish
def gen_fish_size(mastery_bonus = 0):
    size_number = random.randint(mastery_bonus * 5, 100)

    if size_number >= 0 and size_number < 6:  # 5%
        size = ewcfg.fish_size_miniscule
    elif size_number >= 6 and size_number < 21:  # 15%
        size = ewcfg.fish_size_small
    elif size_number >= 21 and size_number < 71:  # 50%
        size = ewcfg.fish_size_average
    elif size_number >= 71 and size_number < 86:  # 15%
        size = ewcfg.fish_size_big
    elif size_number >= 86 and size_number < 100:  # 4
        size = ewcfg.fish_size_huge
    else:  # 1%
        size = ewcfg.fish_size_colossal

    return size


# Determines bite text
def gen_bite_text(size):
    if size == "item":
        text = "You feel a distinctly inanimate tug at your fishing pole!"

    elif size == ewcfg.fish_size_miniscule:
        text = "You feel a wimpy tug at your fishing pole!"
    elif size == ewcfg.fish_size_small:
        text = "You feel a mediocre tug at your fishing pole!"
    elif size == ewcfg.fish_size_average:
        text = "You feel a modest tug at your fishing pole!"
    elif size == ewcfg.fish_size_big:
        text = "You feel a mildly threatening tug at your fishing pole!"
    elif size == ewcfg.fish_size_huge:
        text = "You feel a startlingly strong tug at your fishing pole!"
    else:
        text = "You feel a tug at your fishing pole so intense that you nearly get swept off your feet!"

    text += " **!REEL NOW!!!!!**"
    return text


async def award_fish(fisher, cmd, user_data):
    response = ""

    actual_fisherman = None
    actual_fisherman_data = user_data
    if fisher.inhabitant_id:
        actual_fisherman = user_data.get_possession()[1]
        actual_fisherman_data = EwUser(id_user=actual_fisherman, id_server=cmd.guild.id)

    if fisher.current_fish in ["item", "seaitem"]:
        slimesea_inventory = bknd_item.inventory(id_server=cmd.guild.id, id_user=ewcfg.poi_id_slimesea)

        if (fisher.pier.pier_type != ewcfg.fish_slime_saltwater or len(slimesea_inventory) == 0 or random.random() < 0.2) and fisher.current_fish == "item":

            item = random.choice(vendors.mine_results)

            # if actual_fisherman_data.juviemode:
            #	unearthed_item_amount = 1
            # else:
            unearthed_item_amount = (random.randrange(5) + 8)  # anywhere from 8-12 drops

            item_props = itm_utils.gen_item_props(item)

            # Ensure item limits are enforced, including food since this isn't the fish section
            if bknd_item.check_inv_capacity(user_data=actual_fisherman_data, item_type=item.item_type):
                for creation in range(unearthed_item_amount):
                    bknd_item.item_create(
                        item_type=item.item_type,
                        id_user=actual_fisherman or cmd.message.author.id,
                        id_server=cmd.guild.id,
                        item_props=item_props
                    )

                response = "You reel in {} {}s! ".format(unearthed_item_amount, item.str_name)
            else:
                response = "You woulda reeled in some {}s, but your back gave out under the weight of the rest of your {}s.".format(item.str_name, item.item_type)

        else:
            item = random.choice(slimesea_inventory)

            if bknd_item.give_item(id_item=item.get('id_item'), member=cmd.message.author):
                response = "You reel in a {}!".format(item.get('name'))
            else:
                response = "You woulda reeled in a {}, but your back gave out under the weight of the rest of your {}s.".format(item.str_name, item.item_type)

        fisher.stop()
        user_data.persist()

    else:
        user_initial_level = user_data.slimelevel

        gang_bonus = False

        has_fishingrod = False

        if user_data.weapon >= 0:
            weapon_item = EwItem(id_item=user_data.weapon)
            weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
            if weapon.id_weapon == "fishingrod":
                has_fishingrod = True

        value = 0

        # Rewards from the fish's size
        slime_gain = ewcfg.fish_gain * static_fish.size_to_reward[fisher.current_size]
        value += 10 * static_fish.size_to_reward[fisher.current_size]

        # Rewards from the fish's rarity
        value += 10 * static_fish.rarity_to_reward[static_fish.fish_map[fisher.current_fish].rarity]

        if user_data.life_state == 2:
            if fisher.current_fish in static_fish.day_fish and user_data.faction == ewcfg.faction_rowdys:
                gang_bonus = True
                slime_gain = slime_gain * 1.5
                value += 20

            if fisher.current_fish in static_fish.night_fish and user_data.faction == ewcfg.faction_killers:
                gang_bonus = True
                slime_gain = slime_gain * 1.5
                value += 20

        # Disabled while I try out the new mastery fishing
        #if has_fishingrod == True:
        #    slime_gain = slime_gain * 2

        # trauma = se_static.trauma_map.get(user_data.trauma)
        # if trauma != None and trauma.trauma_class == ewcfg.trauma_class_slimegain:
        #	slime_gain *= (1 - 0.5 * user_data.degradation / 100)

        if fisher.pier.pier_type == ewcfg.fish_slime_void:
            slime_gain = slime_gain * 1.5
            value += 30

        if fisher.current_fish == "plebefish":
            slime_gain = ewcfg.fish_gain * .5
            value = 10

        controlling_faction = poi_utils.get_subzone_controlling_faction(user_data.poi, user_data.id_server)

        if controlling_faction != "" and controlling_faction == user_data.faction:
            slime_gain *= 2

        if user_data.poi == ewcfg.poi_id_juviesrow_pier:
            slime_gain = int(slime_gain / 4)

        trauma = se_static.trauma_map.get(user_data.trauma)
        if trauma != None and trauma.trauma_class == ewcfg.trauma_class_slimegain:
            slime_gain *= (1 - 0.5 * user_data.degradation / 100)

        slime_gain = max(0, round(slime_gain))

        bknd_item.item_create(
            id_user=actual_fisherman or cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type=ewcfg.it_food,
            item_props={
                'id_food': static_fish.fish_map[fisher.current_fish].id_fish,
                'food_name': static_fish.fish_map[fisher.current_fish].str_name,
                'food_desc': static_fish.fish_map[fisher.current_fish].str_desc,
                'recover_hunger': 20,
                'str_eat': ewcfg.str_eat_raw_material.format(static_fish.fish_map[fisher.current_fish].str_name),
                'rarity': static_fish.fish_map[fisher.current_fish].rarity,
                'size': fisher.current_size,
                'time_expir': time.time() + ewcfg.std_food_expir,
                'time_fridged': 0,
                'acquisition': ewcfg.acquisition_fishing,
                'value': value,
                'noslime': 'false'  # if not actual_fisherman_data.juviemode else 'true'
            }
        )

        if fisher.inhabitant_id:
            server = cmd.guild
            inhabitant_member = server.get_member(fisher.inhabitant_id)
            inhabitant_name = inhabitant_member.display_name
            inhabitant_data = EwUser(id_user=fisher.inhabitant_id, id_server=user_data.id_server)
            inhabitee_name = server.get_member(actual_fisherman).display_name

            slime_gain = int(0.25 * slime_gain)

            response = "The two of you together manage to reel in a {fish}! {flavor} {ghost} haunts {slime:,} slime away from the fish before placing it on {fleshling}'s hands." \
                .format(
                fish=static_fish.fish_map[fisher.current_fish].str_name,
                flavor=static_fish.fish_map[fisher.current_fish].str_desc,
                ghost=inhabitant_name,
                fleshling=inhabitee_name,
                slime=slime_gain,
            )

            inhabitant_data.change_slimes(n=-slime_gain)
            inhabitant_data.persist()
            fisher.stop()
        else:
            response = "You reel in a {fish}! {flavor} You grab hold and wring {slime:,} slime from it. " \
                .format(fish=static_fish.fish_map[fisher.current_fish].str_name, flavor=static_fish.fish_map[fisher.current_fish].str_desc, slime=slime_gain)
            if gang_bonus == True:
                if user_data.faction == ewcfg.faction_rowdys:
                    response += "The Rowdy-pride this fish is showing gave you more slime than usual. "
                elif user_data.faction == ewcfg.faction_killers:
                    response += "The Killer-pride this fish is showing gave you more slime than usual. "

            levelup_response = user_data.change_slimes(n=slime_gain, source=ewcfg.source_fishing)
            was_levelup = True if user_initial_level < user_data.slimelevel else False
            # Tell the player their slime level increased.
            if was_levelup:
                response += levelup_response

        fisher.stop()

        user_data.persist()
    return response


def cancel_rod_possession(fisher, user_data):
    response = ''
    if fisher.inhabitant_id:
        user_data.cancel_possession()
        response += '\n'
        if fisher.fleshling_reeled:
            response += "Fucking ghosts, can't rely on them for anything."
        elif fisher.ghost_reeled:
            response += "You can't trust the living even for the simplest shit, I guess."
        else:
            response += "Are you two even trying?"
        response += ' Your contract is dissolved.'
    return response
