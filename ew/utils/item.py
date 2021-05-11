
import collections
import random
import time

from . import core as ewutils
from . import frontend as fe_utils
from . import stats as ewstats
from ..backend import core as bknd_core
from ..backend import item as bknd_item
from ..backend.item import EwItem
from ..backend.user import EwUserBase as EwUser
from ..static import cfg as ewcfg
from ..static import hue as hue_static
from ..static import items as static_items
from ..static import weapons as static_weapons

"""
    Drop some of a player's non-soulbound items into their district.
"""
def item_dropsome(id_server = None, id_user = None, item_type_filter = None, fraction = None, rigor = False):
    #try:
    user_data = EwUser(id_server = id_server, id_user = id_user)
    items = bknd_item.inventory(id_user = id_user, id_server = id_server, item_type_filter = item_type_filter)
    mutations = user_data.get_mutations()

    drop_candidates = []
    #safe_items = [ewcfg.item_id_gameguide]

    # Filter out Soulbound items.
    for item in items:
        item_obj = EwItem(id_item = item.get('id_item'))
        if item_obj.item_props.get('context') in ["corpse", "droppable"]:
            bknd_item.give_item(id_user=user_data.poi, id_server=id_server, id_item=item_obj.id_item)
        if item.get('soulbound') == False and not (rigor == True and item_obj.item_props.get('preserved') ==  user_data.id_user) and item_obj.item_props.get('context') != 'gellphone':
            drop_candidates.append(item)


    filtered_items = []

    if item_type_filter == ewcfg.it_item or item_type_filter == ewcfg.it_food:
        filtered_items = drop_candidates
    if item_type_filter == ewcfg.it_cosmetic:
        for item in drop_candidates:
            cosmetic_id = item.get('id_item')
            cosmetic_item = EwItem(id_item = cosmetic_id)
            if cosmetic_item.item_props.get('adorned') != "true" and cosmetic_item.item_props.get('slimeoid') != "true":
                filtered_items.append(item)

    if item_type_filter == ewcfg.it_weapon:
        for item in drop_candidates:
            if item.get('id_item') != user_data.weapon and item.get('id_item') != user_data.sidearm:
                filtered_items.append(item)
            else:
                pass

    number_of_filtered_items = len(filtered_items)

    number_of_items_to_drop = int(number_of_filtered_items / fraction)

    if number_of_items_to_drop >= 2:
        random.shuffle(filtered_items)
        for drop in range(number_of_items_to_drop):
            for item in filtered_items:
                id_item = item.get('id_item')
                bknd_item.give_item(id_user = user_data.poi, id_server = id_server, id_item = id_item)
                filtered_items.pop(0)
                break
    #except:
    #	ewutils.logMsg('Failed to drop items for user with id {}'.format(id_user))


def get_fingernail_item(cmd):
	item = static_weapons.weapon_map.get(ewcfg.weapon_id_fingernails)
	item_props = gen_item_props(item)
	id_item = bknd_item.item_create(
		item_type=ewcfg.it_weapon,
		id_user=cmd.message.author.id,
		id_server=cmd.guild.id,
		stack_max=-1,
		stack_size=0,
		item_props=item_props
	)

	return id_item


def get_cosmetic_abilities(id_user, id_server):
	active_abilities = []

	cosmetic_items = bknd_item.inventory(
		id_user = id_user,
		id_server = id_server,
		item_type_filter = ewcfg.it_cosmetic
	)

	for item in cosmetic_items:
		i = item.get('item_props')
		if i['adorned'] == "true" and i['ability'] is not None:
			active_abilities.append(i['ability'])
		else:
			pass

	return active_abilities

def get_outfit_info(id_user, id_server, wanted_info = None):
	cosmetic_items = bknd_item.inventory(
		id_user = id_user,
		id_server = id_server,
		item_type_filter = ewcfg.it_cosmetic
	)

	adorned_cosmetics = []
	adorned_ids = []

	adorned_styles = []
	dominant_style = None

	adorned_hues = []

	total_freshness = 0

	for cosmetic in cosmetic_items:
		item_props = cosmetic.get('item_props')

		if item_props['adorned'] == 'true':
			adorned_styles.append(item_props.get('fashion_style'))

			hue = hue_static.hue_map.get(item_props.get('hue'))
			adorned_hues.append(item_props.get('hue'))

			if item_props['id_cosmetic'] not in adorned_ids:
				total_freshness += int(item_props.get('freshness'))

			adorned_ids.append(item_props['id_cosmetic'])
			adorned_cosmetics.append((hue.str_name + " " if hue != None else "") + cosmetic.get('name'))

	if len(adorned_cosmetics) != 0:
		# Assess if there's a cohesive style
		if len(adorned_styles) != 0:
			counted_styles = collections.Counter(adorned_styles)
			dominant_style = max(counted_styles, key = counted_styles.get)

			relative_style_amount = round(int(counted_styles.get(dominant_style) / len(adorned_cosmetics) * 100))
			# If the outfit has a dominant style
			if relative_style_amount >= 60:
				total_freshness *= int(relative_style_amount / 10) # If relative amount is 60 --> multiply by 6. 70 --> 7, 80 --> 8, etc. Rounds down, so 69 --> 6.

	if wanted_info is not None and wanted_info == "dominant_style" and dominant_style is not None:
		return dominant_style
	elif wanted_info is not None and wanted_info == "total_freshness":
		return total_freshness
	else:
		outfit_map = {
			'dominant_style': dominant_style,
			'total_freshness': total_freshness
		}
		return outfit_map

def get_style_freshness_rating(user_data, dominant_style = None):
	if dominant_style == None:
		dominant_style = "fresh"

	if user_data.freshness < ewcfg.freshnesslevel_1:
		response = "Your outfit is starting to look pretty fresh, but you’ve got a long way to go if you wanna be NLACakaNM’s next top model."
	else:
		if user_data.freshness < ewcfg.freshnesslevel_2:
			response = "Your outfit is low-key on point, not gonna lie. You’re goin’ places, kid."
		elif user_data.freshness < ewcfg.freshnesslevel_3:
			response = "Your outfit is lookin’ fresh as hell, goddamn! You shop so much you can probably speak Italian."
		elif user_data.freshness < ewcfg.freshnesslevel_4:
			response = "Your outfit is straight up **GOALS!** Like, honestly. I’m being, like, totally sincere right now. Your Instragrime has attracted a small following."
		else:
			response = "Holy shit! Your outfit is downright, positively, without a doubt, 100% **ON FLEEK!!** You’ve blown up on Instragrime, and you’ve got modeling gigs with fashion labels all across the city."

		if dominant_style == ewcfg.style_cool:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re lookin’ wicked cool, dude. Like, straight up radical, man. For real, like, ta-haaa, seriously? Damn, bro. Sick."
			else:
				response += " Hey, kids, the world just got cooler. You’re the swingingest thing from coast-to-coast, and that ain’t no boast. You’re every slimegirl’s dream, you know what I mean? You’re where it’s at, and a far-out-happenin’ cat to boot. Man, it must hurt to be this hip."
		elif dominant_style == ewcfg.style_tough:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re lookin’ tough as hell. Juveniles of all affiliations are starting to act nervous around you."
			else:
				response += " You’re just about the toughest-lookin' juveniledelinquent in the whole detention center. Ain’t nobody gonna pick a fight with you anymore, goddamn."
		elif dominant_style == ewcfg.style_smart:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re starting to look like a real hipster, wearing all these smartypants garments. You love it, the people around you hate it."
			else:
				response += " You know extensive facts about bands that are so underground they’ve released their albums through long-since-expired Vocaroo links. You’re a leading hashtag warrior on various internet forums, and your opinions are well known by everyone who has spoken to you for more than five minutes. Everyone wants to knock your lights out, but… you’re just too fresh. "
		elif dominant_style == ewcfg.style_beautiful:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " You’re looking extremely handsome in all of those beautiful garments. If only this refined, elegant reflected in your manners when cracking into a Arizonian Kingpin Crab."
			else:
				response += " You’re the belle of the ball at every ball you attend, which has never happened. But, if you *were* to ever attend one, your beautiful outfit would surely distinguish you from the crowd. Who knows, you might even find TRUE LOVE because of it and get MARRIED. That is, if you weren’t already married to slime."
		elif dominant_style == ewcfg.style_cute:
			if user_data.freshness < ewcfg.freshnesslevel_4:
				response += " Awwwhhh, look at you! You’re sooo cute~, oh my gosh. I could just eat you up, and then vomit you back up after I read back the previous line I’ve just written."
			else:
				response += " It is almost kowai how kawaii you are right now. Your legions of fans slobber all over each new post on Instragrime and leave very strange comments. You’re stopped for autographs in public now, and there hasn’t been a selfie taken with you that hasn’t featured a hover hand."

	return response


def gen_item_props(item):
    item_props = {}
    if not hasattr(item, "item_type"):
        return item_props
    if item.acquisition == ewcfg.acquisition_fishing and item.item_type == ewcfg.it_food:
        item_props = {
            'id_food': item.id_fish,
            'food_name': item.str_name,
            'food_desc': item.str_desc,
            'recover_hunger': 20,
            'str_eat': ewcfg.str_eat_raw_material.format(item.str_name),
            'time_expir': int(time.time()) + ewcfg.std_food_expir,
            'time_fridged': 0,
            'perishable': item.perishable,
            'acquisition': ewcfg.acquisition_fishing,
        }
    elif item.item_type == ewcfg.it_food:
        item_props = {
            'id_food': item.id_food,
            'food_name': item.str_name,
            'food_desc': item.str_desc,
            'recover_hunger': item.recover_hunger,
            'inebriation': item.inebriation,
            'str_eat': item.str_eat,
            'time_expir': int(time.time()) + item.time_expir,
            'time_fridged': item.time_fridged,
            'perishable': item.perishable,
        }
    elif item.item_type == ewcfg.it_relic:
        item_props = {
            'id_relic': item.id_relic,
            'relic_name': item.str_name,
            'relic_desc': item.str_desc,
            'acquisition': item.acquisition
        }
    elif item.item_type == ewcfg.it_item:
        item_props = {
            'id_item': item.id_item,
            'context': item.context,
            'item_name': item.str_name,
            'item_desc': item.str_desc,
            'ingredients': item.ingredients if type(item.ingredients) == str else item.ingredients[0],
            'acquisition': item.acquisition,
        }
        if item.context == ewcfg.context_slimeoidfood:
            item_props["increase"] = item.increase
            item_props["decrease"] = item.decrease
        if item.context == ewcfg.context_prankitem:
            item_props["prank_type"] = item.prank_type
            item_props["prank_desc"] = item.prank_desc
            item_props["rarity"] = item.rarity
            item_props["gambit"] = item.gambit
            # Response items
            item_props["response_command"] = item.response_command
            item_props["response_desc_1"] = item.response_desc_1
            item_props["response_desc_2"] = item.response_desc_2
            item_props["response_desc_3"] = item.response_desc_3
            item_props["response_desc_4"] = item.response_desc_4
            # Trap items
            item_props["trap_chance"] = item.trap_chance
            item_props["trap_stored_credence"] = item.trap_stored_credence
            item_props["trap_user_id"] = item.trap_user_id
            # Some prank items have nifty side effects
            item_props["side_effect"] = item.side_effect
        if item.context == ewcfg.context_seedpacket:
            item_props["cooldown"] = item.cooldown
            item_props["cost"] = item.cost
            item_props["time_nextuse"] = item.time_nextuse
            item_props["enemytype"] = item.enemytype
        if item.context == ewcfg.context_tombstone:
            item_props["brainpower"] = item.brainpower
            item_props["cost"] = item.cost
            item_props["stock"] = item.stock
            item_props["enemytype"] = item.enemytype

        try:
            item_props["durability"] = item.durability
        except:
            pass


    elif item.item_type == ewcfg.it_weapon:
        captcha = ""
        if ewcfg.weapon_class_captcha in item.classes:
            captcha = ewutils.generate_captcha(length = item.captcha_length)

        item_props = {
            "weapon_type": item.id_weapon,
            "weapon_name": "",
            "weapon_desc": item.str_description,
            "married": "",
            "ammo": item.clip_size,
            "captcha": captcha,
            "is_tool" : item.is_tool
        }

    elif item.item_type == ewcfg.it_cosmetic:
        item_props = {
            'id_cosmetic': item.id_cosmetic,
            'cosmetic_name': item.str_name,
            'cosmetic_desc': item.str_desc,
            'str_onadorn': item.str_onadorn if item.str_onadorn else ewcfg.str_generic_onadorn,
            'str_unadorn': item.str_unadorn if item.str_unadorn else ewcfg.str_generic_unadorn,
            'str_onbreak': item.str_onbreak if item.str_onbreak else ewcfg.str_generic_onbreak,
            'rarity': item.rarity if item.rarity else ewcfg.rarity_plebeian,
            'attack': item.stats[ewcfg.stat_attack] if ewcfg.stat_attack in item.stats.keys() else 0,
            'defense': item.stats[ewcfg.stat_defense] if ewcfg.stat_defense in item.stats.keys() else 0,
            'speed': item.stats[ewcfg.stat_speed] if ewcfg.stat_speed in item.stats.keys() else 0,
            'ability': item.ability if item.ability else None,
            'durability': item.durability if item.durability else ewcfg.base_durability,
            'size': item.size if item.size else 1,
            'fashion_style': item.style if item.style else ewcfg.style_cool,
            'freshness': item.freshness if item.freshness else 5,
            'adorned': 'false',
            'hue': ""
        }
    elif item.item_type == ewcfg.it_furniture:
        item_props = {
            'id_furniture': item.id_furniture,
            'furniture_name': item.str_name,
            'furniture_desc': item.str_desc,
            'rarity': item.rarity,
            'furniture_place_desc': item.furniture_place_desc,
            'furniture_look_desc': item.furniture_look_desc,
            'acquisition': item.acquisition
        }

    return item_props

# SWILLDERMUK
async def perform_prank_item_side_effect(side_effect, cmd=None, member=None):
    response = ""

    if side_effect == "bungisbeam_effect":

        target_member = cmd.mentions[0]
        client = cmd.client

        current_nickname = target_member.display_name
        new_nickname = current_nickname + ' (Bungis)'

        if len(new_nickname) > 32:
            # new nickname is too long, cut out some parts of original nickname
            new_nickname = current_nickname[:20]
            new_nickname += '... (Bungis)'

        await target_member.edit(nick=new_nickname)

        response = "\n\nYou are now known as {}!".format(target_member.display_name)

    elif side_effect == "cumjar_effect":

        target_member = cmd.mentions[0]
        target_data = EwUser(member=target_member)

        if random.randrange(2) == 0:

            figurine_id = random.choice(static_items.furniture_pony)

            #print(figurine_id)
            item = static_items.furniture_map.get(figurine_id)

            item_props = gen_item_props(item)

            #print(item_props)

            bknd_item.item_create(
                id_user=target_data.id_user,
                id_server=target_data.id_server,
                item_type=ewcfg.it_furniture,
                item_props=item_props,
            )

            response = "\n\n*{}*: What's this? It looks like a pony figurine was inside the Cum Jar all along! You stash it in your inventory quickly.".format(target_member.display_name)

    elif side_effect == "bensaintsign_effect":

        target_member = member
        client = ewutils.get_client()

        new_nickname = 'Ben Saint'

        await target_member.edit(nick=new_nickname)

        response = "\n\nYou are now Ben Saint.".format(target_member.display_name)

    elif side_effect == "bodynotifier_effect":
        target_member = cmd.mentions[0]

        direct_message = "You are now manually breathing.\nYou are now manually blinking.\nYour tounge is now uncomfortable inside your mouth.\nYou just lost THE GAME."
        try:
            await fe_utils.send_message(cmd.client, target_member, direct_message)
        except:
            await fe_utils.send_message(cmd.client, fe_utils.get_channel(cmd.guild, cmd.message.channel), fe_utils.formatMessage(target_member, direct_message))

    return response


"""
    Transfer a random item from district inventory to player inventory
"""
def item_lootrandom(user_data):
    response = ""

    try:

        items_in_poi = bknd_core.execute_sql_query("SELECT {id_item} FROM items WHERE {id_owner} = %s AND {id_server} = %s".format(
                id_item = ewcfg.col_id_item,
                id_owner = ewcfg.col_id_user,
                id_server = ewcfg.col_id_server
            ),(
                user_data.poi,
                user_data.id_server
            ))

        if len(items_in_poi) > 0:
            id_item = random.choice(items_in_poi)[0]

            item_sought = bknd_item.find_item(item_search = str(id_item), id_user = user_data.poi, id_server = user_data.id_server)

            response += "You found a {}!".format(item_sought.get('name'))

            if bknd_item.check_inv_capacity(user_data = user_data, item_type = item_sought.get('item_type')):
                if item_sought.get('name') == "Slime Poudrin":
                    ewstats.change_stat(
                        id_server=user_data.id_server,
                        id_user=user_data.id_user,
                        metric=ewcfg.stat_poudrins_looted,
                        n=1
                    )
                bknd_item.give_item(id_user=user_data.id_user, id_server=user_data.id_server, id_item=id_item)
            else:
                response += " But you couldn't carry any more {}s, so you tossed it back.".format(item_sought.get('item_type'))

        else:
            response += "You found a... oh, nevermind, it's just a piece of trash."

    except:
        ewutils.logMsg("Failed to loot random item")

    finally:
        return response



