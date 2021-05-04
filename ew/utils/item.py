
import collections

from ..static import cfg as ewcfg
from ..static import weapons as static_weapons
from ..static import hue as hue_static

from ..backend import item as bknd_item

from .. import item as ewitem

from . import core as ewutils

def get_fingernail_item(cmd):
	item = static_weapons.weapon_map.get(ewcfg.weapon_id_fingernails)
	item_props = ewitem.gen_item_props(item)
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

