import random

from .. import item_package as ewitem
from .. import slimeoid as ewslimeoid
from ..backend import core as bknd_core
from ..backend import item as bknd_item
from ..backend.apt import EwApartment
from ..backend.item import EwItem
from ..backend.market import EwMarket
from ..backend.player import EwPlayer
from ..static import cfg as ewcfg
from ..static import cosmetics
from ..static import hue as hue_static
from ..static import items as static_items
from ..static import poi as poi_static
from ..utils import core as ewutils
from ..utils import frontend as fe_utils
from ..utils import rolemgr as ewrolemgr
from ..utils.combat import EwUser
from ..utils.frontend import EwResponseContainer

from .abstractions import toss_squatters
from .abstractions import toss_items

async def rent_time(id_server = None):

	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()
		client = ewutils.get_client()
		if id_server != None:
			#get all players with apartments. If a player is evicted, thir rent is 0, so this will not affect any bystanders.
			cursor.execute("SELECT apartment.rent, users.id_user FROM users INNER JOIN apartment ON users.id_user=apartment.id_user WHERE users.id_server = %s AND apartment.id_server = %s AND apartment.rent > 0".format(

			), (
				id_server,
				id_server,
			))

			landowners = cursor.fetchall()

			for landowner in landowners:
				owner_id_user = int(landowner[1])
				owner_rent_price = landowner[0]

				user_data = EwUser(id_user=owner_id_user, id_server=id_server)
				user_poi = poi_static.id_to_poi.get(user_data.poi)
				poi = poi_static.id_to_poi.get(user_data.apt_zone)

				if owner_rent_price > user_data.slimecoin:

					if(user_poi.is_apartment and user_data.visiting == ewcfg.location_id_empty):
						user_data.poi = user_data.apt_zone #toss out player
						user_data.persist()
						server = ewcfg.server_list[user_data.id_server]
						member_object = server.get_member(owner_id_user)

						await ewrolemgr.updateRoles(client = client, member=member_object)
						player = EwPlayer(id_user = owner_id_user)
						response = "{} just got evicted. Point and laugh, everyone.".format(player.display_name)
						await fe_utils.send_message(client, fe_utils.get_channel(server, poi.channel), response)


					user_data = EwUser(id_user=owner_id_user, id_server=id_server)
					user_apt = EwApartment(id_user=owner_id_user, id_server=id_server)
					poi = poi_static.id_to_poi.get(user_data.apt_zone)

					toss_items(id_user=str(user_data.id_user) + 'closet', id_server=user_data.id_server, poi = poi)
					toss_items(id_user=str(user_data.id_user) + 'fridge', id_server=user_data.id_server, poi = poi)
					toss_items(id_user=str(user_data.id_user) + 'decorate', id_server=user_data.id_server, poi = poi)

					user_data.apt_zone = ewcfg.location_id_empty
					user_data.persist()
					user_apt.rent = 0
					user_apt.poi = " "
					user_apt.persist()

					await toss_squatters(user_id=user_data.id_user, server_id=id_server)

				else:
					user_data.change_slimecoin(n=-owner_rent_price, coinsource=ewcfg.coinsource_spending)
					user_data.persist()
	finally:
		cursor.close()
		bknd_core.databaseClose(conn_info)

async def apt_look(cmd):
	playermodel = EwPlayer(id_user=cmd.message.author.id)
	usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
	apt_model = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
	poi = poi_static.id_to_poi.get(apt_model.poi)
	lookObject = str(cmd.message.author.id)
	isVisiting = False
	resp_cont = EwResponseContainer(id_server=playermodel.id_server)

	if usermodel.visiting != ewcfg.location_id_empty:
		apt_model = EwApartment(id_user=usermodel.visiting, id_server=playermodel.id_server)
		poi = poi_static.id_to_poi.get(apt_model.poi)
		lookObject = str(usermodel.visiting)
		isVisiting = True

	response = "You stand in {}, your flat in {}.\n\n{}\n\n".format(apt_model.name, poi.str_name, apt_model.description)

	if isVisiting:
		response = response.replace("your", "a")

	resp_cont.add_channel_response(cmd.message.channel, response)

	furns = bknd_item.inventory(id_user= lookObject+ewcfg.compartment_id_decorate, id_server= playermodel.id_server, item_type_filter=ewcfg.it_furniture)

	has_hat_stand = False

	furniture_id_list = []
	furn_response = ""
	for furn in furns:
		i = EwItem(furn.get('id_item'))

		furn_response += "{} ".format(i.item_props['furniture_look_desc'])

		furniture_id_list.append(i.item_props['id_furniture'])
		if i.item_props.get('id_furniture') == "hatstand":
			has_hat_stand = True


		hue = hue_static.hue_map.get(i.item_props.get('hue'))
		if hue != None and i.item_props.get('id_furniture') not in static_items.furniture_specialhue:
			furn_response += " It's {}. ".format(hue.str_name)
		elif i.item_props.get('id_furniture') in static_items.furniture_specialhue:
			if hue != None:
				furn_response = furn_response.replace("-*HUE*-", hue.str_name)
			else:
				furn_response = furn_response.replace("-*HUE*-", "white")

	furn_response += "\n\n"

	if all(elem in furniture_id_list for elem in static_items.furniture_lgbt):
		furn_response += "This is the most homosexual room you could possibly imagine. Everything is painted rainbow. A sign on your bedroom door reads \"FORNICATION ZONE\". There's so much love in the air that some dust mites set up a gay bar in your closet. It's amazing.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_haunted):
		furn_response += "One day, on a whim, you decided to say \"Levy Jevy\" 3 times into the mirror. Big mistake. Not only did it summon several staydeads, but they're so enamored with your decoration that they've been squatting here ever since.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_highclass):
		furn_response += "This place is loaded. Marble fountains, fully stocked champagne fridges, complementary expensive meats made of bizarre unethical ingredients, it's a treat for the senses. You wonder if there's any higher this place can go. Kind of depressing, really.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_leather):
		furn_response += "34 innocent lives. 34 lives were taken to build the feng shui in this one room. Are you remorseful about that? Obsessed? Nobody has the base antipathy needed to peer into your mind and pick at your decisions. The leather finish admittedly does look fantastic, however. Nice work.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_church):
		furn_response += random.choice(ewcfg.bible_verses) + "\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_pony):
		furn_response += "When the Mane 6 combine their powers, kindness, generosity, loyalty, honesty, magic, and the other one, they combine to form the most powerful force known to creation: friendship. Except for slime. That's still stronger.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_blackvelvet):
		furn_response += "Looking around just makes you want to loosen your tie a bit and pull out an expensive cigar. Nobody in this city of drowned rats and slimeless rubes can stop you now. You commit homicide...in style. Dark, velvety smooth style.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_seventies):
		furn_response += "Look at all this vintage furniture. Didn't the counterculture that created all this shit advocate for 'peace and love'? Yuck. I hope you didn't theme your bachelor pad around that kind of shit and just bought everything for its retro aesthetic.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_shitty):
		furn_response += "You're never gonna make it. Look at all this furniture you messed up, do you think someday you can escape this? You're never gonna have sculptures like Stradivarius, or paintings as good as that one German guy. You're deluded and sitting on splinters. Grow up. \n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_instrument):
		furn_response += "You assembled the instruments. Now all you have to do is form a soopa groop and play loudly over other people acts next Slimechella. It's high time the garage bands of this city take over, with fresh homemade shredding and murders most foul. The world's your oyster. As soon as you can trust them with all this expensive equipment.\n\n"
	if all(elem in furniture_id_list for elem in static_items.furniture_slimecorp):
		furn_response = "SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP.\n\n"


	market_data = EwMarket(id_server = playermodel.id_server)
	clock_data = ewutils.weather_txt(market_data)
	clock_data = clock_data[16:20]
	furn_response = furn_response.format(time = clock_data)
	resp_cont.add_channel_response(cmd.message.channel, furn_response)

	response = ""
	iterate = 0
	frids = bknd_item.inventory(id_user=lookObject + ewcfg.compartment_id_fridge, id_server=playermodel.id_server)

	if(len(frids) > 0):
		response += "\n\nThe fridge contains: "
		fridge_pile = []
		for frid in frids:
			fridge_pile.append(frid.get('name'))
		response += ewutils.formatNiceList(fridge_pile)
		response = response + '.'
	closets = bknd_item.inventory(id_user=lookObject + ewcfg.compartment_id_closet, id_server=playermodel.id_server)

	resp_cont.add_channel_response(cmd.message.channel, response)
	response = ""

	if (len(closets) > 0):
		closet_pile = []
		hatstand_pile = []
		for closet in closets:
			closet_obj = EwItem(id_item=closet.get('id_item'))
			map_obj = cosmetics.cosmetic_map.get(closet_obj.item_props.get('id_cosmetic'))
			if has_hat_stand and map_obj and map_obj.is_hat == True:
				hatstand_pile.append(closet.get('name'))
			else:
				closet_pile.append(closet.get('name'))
		if len(closet_pile) > 0:
			response += "\n\nThe closet contains: "
			response += ewutils.formatNiceList(closet_pile)
			response = response + '.'
			resp_cont.add_channel_response(cmd.message.channel, response)

		if len(hatstand_pile) > 0:
			response = "\n\nThe hat stand holds: "
			response += ewutils.formatNiceList(hatstand_pile)
			response = response + '.'
			resp_cont.add_channel_response(cmd.message.channel, response)



	shelves = bknd_item.inventory(id_user=lookObject + ewcfg.compartment_id_bookshelf, id_server=playermodel.id_server)

	response = ""
	if (len(shelves) > 0):
		response += "\n\nThe bookshelf holds: "
		shelf_pile = []
		for shelf in shelves:
			shelf_pile.append(shelf.get('name'))
		response += ewutils.formatNiceList(shelf_pile)
		response = response + '.'

	resp_cont.add_channel_response(cmd.message.channel, response)

	freezeList = ewslimeoid.get_slimeoid_look_string(user_id=lookObject+'freeze', server_id = playermodel.id_server)

	resp_cont.add_channel_response(cmd.message.channel, freezeList)
	return await resp_cont.post(channel=cmd.message.channel)

# This is quite literally not used anywhere
def check(str):
	if str.content == ewcfg.cmd_sign or str.content == ewcfg.cmd_rip:
		return True
	#async def bazaar_update(cmd): ##DEBUG COMMAND. DO NOT RELEASE WITH THIS.
	#   playermodel = EwPlayer(id_user=cmd.message.author.id)
	#  market_data = EwMarket(playermodel.id_server)
	#   market_data.bazaar_wares.clear()

	#  bazaar_foods = []
	#  bazaar_cosmetics = []
	#  bazaar_general_items = []
	#  bazaar_furniture = []

	# for item in vendors.vendor_inv.get(ewcfg.vendor_bazaar):
	#	 if item in static_items.item_names:
	#		bazaar_general_items.append(item)
	#
	#	   elif item in static_food.food_names:
	#		  bazaar_foods.append(item)
	#	 elif item in cosmetics.cosmetic_names:
	#		  bazaar_cosmetics.append(item)
	#
	#	   elif item in static_items.furniture_names:
	#		  bazaar_furniture.append(item)
	#
	#   market_data.bazaar_wares['generalitem'] = random.choice(bazaar_general_items)

	#   market_data.bazaar_wares['food1'] = random.choice(bazaar_foods)
	# Don't add repeated foods
	#  while market_data.bazaar_wares.get('food2') is None or market_data.bazaar_wares.get('food2') == \
	#		 market_data.bazaar_wares['food1']:
	#	market_data.bazaar_wares['food2'] = random.choice(bazaar_foods)

	# market_data.bazaar_wares['cosmetic1'] = random.choice(bazaar_cosmetics)
	# Don't add repeated cosmetics
	# while market_data.bazaar_wares.get('cosmetic2') is None or market_data.bazaar_wares.get('cosmetic2') == \
	#		market_data.bazaar_wares['cosmetic1']:
	#   market_data.bazaar_wares['cosmetic2'] = random.choice(bazaar_cosmetics)

	#while market_data.bazaar_wares.get('cosmetic3') is None or market_data.bazaar_wares.get('cosmetic3') == \
	#	   market_data.bazaar_wares['cosmetic1'] or market_data.bazaar_wares.get('cosmetic3') == \
	#	  market_data.bazaar_wares['cosmetic2']:
	# market_data.bazaar_wares['cosmetic3'] = random.choice(bazaar_cosmetics)

	#market_data.bazaar_wares['furniture1'] = random.choice(bazaar_furniture)


	#market_data.persist()

async def setOffAlarms(id_server = None):
	ewutils.logMsg('Setting off alarms...')

	if id_server != None:
		client = ewutils.get_client()
		server = client.get_guild(id_server)
		time_current = EwMarket(id_server=id_server).clock
		if time_current <= 12:
			displaytime = str(time_current)
			ampm = 'am'
		if time_current > 12:
			displaytime = str(time_current - 12)
			ampm = 'pm'

		if time_current == 24:
			ampm = "am"
		elif time_current == 12:
			ampm = "pm"

		item_search = "alarm clock set to {}{}".format(displaytime, ampm)
		item_search_brick = "brick{:02d}".format(time_current)
		clockinv = ewitem.find_item_all(item_search="alarmclock", id_server=id_server, item_type_filter=ewcfg.it_furniture)
		brickinv = ewitem.find_item_all(item_search=item_search_brick, id_server=id_server, item_type_filter=ewcfg.it_furniture, search_names=True)

		for clock in clockinv:
			isFurnished = False
			clock_obj = EwItem(id_item=clock.get('id_item'))

			if clock_obj.item_props.get('furniture_name') == item_search:
				if "decorate" in clock_obj.id_owner:
					isFurnished = True
				clock_user = clock_obj.id_owner.replace("decorate", "")
				clock_member = server.get_member(user_id=clock_user)
				if clock_member != None:
					clock_player = EwUser(member=clock_member)
					if (isFurnished == False or ("apt" in clock_player.poi and clock_player.visiting == "empty")) and clock_member:
						try:
							await fe_utils.send_message(client, clock_member, fe_utils.formatMessage(clock_member, "BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP BLAAAP"))
						except:
							ewutils.logMsg("failed to send alarm to user {}".format(clock_member.id))

		for brick in brickinv:
			brick_obj = EwItem(id_item=brick.get('id_item'))
			id_user = brick_obj.id_owner.replace("brickshit", "")
			print(id_user)
			brick_user = EwUser(id_server=id_server, id_user=id_user)
			brick_member = server.get_member(user_id=int(id_user))
			poi = poi_static.id_to_poi.get(brick_user.poi)
			channel_brick = fe_utils.get_channel(server, poi.channel)
			print('pass1')
			if brick_member != None:
				print('pass2')
				if brick_member:
					print('pass3')
					try:
						await fe_utils.send_message(client, channel_brick, fe_utils.formatMessage(brick_member, "UUUUUUUUUUGGGGGGGGGGGGHHHHHHHHHHH... OOOOOOOOOOOOOOOOOAAAAAAAAAAAAAAAHHHHH th-tunk. You just shit a brick. Congratulations?"))
						brick_obj.id_owner = poi.id_poi
						brick_obj.item_props['furniture_name'] = 'brick'
						brick_obj.persist()
					except:
						ewutils.logMsg("failed to shit brick on user {}".format(brick_member.id))

"""
	Apartments were originally intended to be read-only channels
	with all interaction being in the dms only. Someone apparently
	forgot maps existed and created this behemoth to parse the 
	proper commands from dms. DM command parsing will be redone
	with the same update that releases this package so this is 
	entirely nonsensical to keep around.
	
async def aptCommands(cmd):
	tokens_count = len(cmd.tokens)
	cmd_text = cmd.tokens[0].lower() if tokens_count >= 1 else ""
	player = EwPlayer(id_user=cmd.message.author.id)
	user_data = EwUser(id_user=cmd.message.author.id, id_server=player.id_server)

	if cmd_text == ewcfg.cmd_depart or cmd_text == ewcfg.cmd_retire:
		return await depart(cmd)
	elif cmd_text == ewcfg.cmd_fridge:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_fridge)
	elif cmd_text == ewcfg.cmd_store:
		return await store_item(cmd=cmd, dest="store")
	elif cmd_text == ewcfg.cmd_closet:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_closet)
	elif cmd_text == ewcfg.cmd_take:
		return await remove_item(cmd=cmd, dest="apartment")
	elif cmd_text == ewcfg.cmd_uncloset:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_closet)
	elif cmd_text == ewcfg.cmd_unfridge:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_fridge)
	elif cmd_text == ewcfg.cmd_decorate:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_decorate)
	elif cmd_text == ewcfg.cmd_undecorate:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_decorate)
	elif cmd_text in [ewcfg.cmd_shelve, ewcfg.cmd_shelve_alt_1]:
		return await store_item(cmd=cmd, dest=ewcfg.compartment_id_bookshelf)
	elif cmd_text in [ewcfg.cmd_unshelve, ewcfg.cmd_unshelve_alt_1]:
		return await remove_item(cmd=cmd, dest=ewcfg.compartment_id_bookshelf)
	elif cmd_text == ewcfg.cmd_upgrade:
		return await upgrade(cmd = cmd)
	elif cmd_text == ewcfg.cmd_breaklease:
		return await cancel(cmd=cmd)
	elif cmd_text == ewcfg.cmd_look:
		return await apt_look(cmd)
	elif cmd_text == ewcfg.cmd_freeze:
		return await freeze(cmd=cmd)
	elif cmd_text == ewcfg.cmd_unfreeze:
		return await unfreeze(cmd=cmd)
	elif cmd_text == ewcfg.cmd_aptname:
		return await customize(cmd=cmd)
	elif cmd_text == ewcfg.cmd_aptdesc:
		return await customize(cmd=cmd, isDesc=True)
	elif cmd_text == ewcfg.cmd_move or cmd_text == ewcfg.cmd_move_alt1 or cmd_text == ewcfg.cmd_move_alt2 or cmd_text == ewcfg.cmd_move_alt3 or cmd_text == ewcfg.cmd_move_alt4 or cmd_text == ewcfg.cmd_move_alt5:
		return await ewmap.move(cmd=cmd, isApt = True)
	elif cmd_text == ewcfg.cmd_knock:
		return await knock(cmd=cmd)
	elif cmd_text == ewcfg.cmd_trickortreat:
		return await trickortreat(cmd=cmd)
	elif cmd_text == ewcfg.cmd_wash:
		return await wash(cmd=cmd)
	elif cmd_text == ewcfg.cmd_browse:
		return await browse(cmd=cmd)
	# from here, all commands are prebuilt and just set to work in DMs

	if cmd_text == ewcfg.cmd_use:
		return await ewitem.item_use(cmd=cmd)
	elif cmd_text == ewcfg.cmd_pot:
		return await flowerpot(cmd=cmd)
	elif cmd_text == ewcfg.cmd_unpot:
		return await unpot(cmd=cmd)
	elif cmd_text == ewcfg.cmd_extractsoul:
		return await ewitem.soulextract(cmd=cmd)
	elif cmd_text == ewcfg.cmd_returnsoul:
		return await ewitem.returnsoul(cmd=cmd)
	elif cmd_text == ewcfg.cmd_releaseprop:
		return await releaseprop(cmd=cmd)
	elif cmd_text == ewcfg.cmd_releasefish:
		return await releasefish(cmd=cmd)
	elif cmd_text == ewcfg.cmd_halt or cmd_text == ewcfg.cmd_halt_alt1:
		return await ewmap.halt(cmd=cmd)
	elif cmd_text == ewcfg.cmd_aquarium:
		return await aquarium(cmd=cmd)
	elif cmd_text == ewcfg.cmd_propstand:
		return await propstand(cmd=cmd)
	elif cmd_text == ewcfg.cmd_howl or cmd_text == ewcfg.cmd_howl_alt1:
		return await ewcmd.cmd_howl(cmd=cmd)
	elif cmd_text == ewcfg.cmd_moan:
		return await ewcmd.cmd_moan(cmd=cmd)
	elif cmd_text == ewcfg.cmd_data:
		return await ewcmd.data(cmd=cmd)
	elif cmd_text == ewcfg.cmd_hunger:
		return await ewcmd.hunger(cmd=cmd)
	elif cmd_text == ewcfg.cmd_slimecoin or cmd_text == ewcfg.cmd_slimecoin_alt1 or cmd_text == ewcfg.cmd_slimecoin_alt2 or cmd_text == ewcfg.cmd_slimecoin_alt3:
		return await ewmarket.slimecoin(cmd=cmd)
	elif cmd_text == ewcfg.cmd_score or cmd_text == ewcfg.cmd_score_alt1:
		return await ewcmd.score(cmd=cmd)
	elif cmd_text == ewcfg.cmd_slimeoid:
		return await ewslimeoid.slimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_adorn:
		return await ewcosmeticitem.adorn(cmd=cmd)
	elif cmd_text in [ewcfg.cmd_dedorn, ewcfg.cmd_dedorn_alt1]:
		return await ewcosmeticitem.dedorn(cmd=cmd)
	elif cmd_text == ewcfg.cmd_smelt:
		return await ewsmelting.smelt(cmd=cmd)
	elif cmd_text == ewcfg.cmd_dress_slimeoid or cmd_text == ewcfg.cmd_dress_slimeoid_alt1:
		return await ewslimeoid.dress_slimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_annoint or cmd_text == ewcfg.cmd_annoint_alt1:
		return await ewwep.annoint(cmd=cmd)
	elif cmd_text == ewcfg.cmd_petslimeoid:
		return await ewslimeoid.petslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_abuseslimeoid:
		return await ewslimeoid.abuseslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_playfetch:
		return await ewslimeoid.playfetch(cmd=cmd)
	elif cmd_text == ewcfg.cmd_observeslimeoid:
		return await ewslimeoid.observeslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_walkslimeoid:
		return await ewslimeoid.walkslimeoid(cmd=cmd)
	elif cmd_text == ewcfg.cmd_wiki:
		return await ewcmd.wiki(cmd=cmd)
	elif cmd_text == ewcfg.cmd_unsalute:
		return await ewcmd.unsalute(cmd=cmd)
	elif cmd_text == ewcfg.cmd_time or cmd_text == ewcfg.cmd_clock or cmd_text == ewcfg.cmd_weather:
		return await ewcmd.weather(cmd=cmd)
	elif cmd_text == ewcfg.cmd_add_quadrant:
		return await ewquadrants.add_quadrant(cmd=cmd)
	elif cmd_text == ewcfg.cmd_clear_quadrant:
		return await ewquadrants.clear_quadrant(cmd=cmd)
	elif cmd_text == ewcfg.cmd_apartment:
		return await apartment(cmd=cmd)
	elif cmd_text == ewcfg.cmd_booru:
		return await ewcmd.booru(cmd=cmd)
	elif cmd_text == ewcfg.cmd_dyecosmetic or ewcfg.cmd_dyecosmetic_alt1 == cmd_text or ewcfg.cmd_dyecosmetic_alt2 == cmd_text or ewcfg.cmd_dyecosmetic_alt3 == cmd_text:
		return await ewcosmeticitem.dye(cmd=cmd)
	elif cmd_text == ewcfg.cmd_equip == cmd_text:
		return await ewwep.equip(cmd=cmd)
	elif ewcfg.cmd_give == cmd_text:
		return await ewitem.give(cmd=cmd)
	elif ewcfg.cmd_hurl == cmd_text:
		return await ewcmd.hurl(cmd=cmd)
	elif ewcfg.cmd_map == cmd_text:
		return await ewcmd.map(cmd=cmd)
	elif ewcfg.cmd_news == cmd_text or ewcfg.cmd_patchnotes == cmd_text:
		return await ewcmd.patchnotes(cmd=cmd)
	elif ewcfg.cmd_petslimeoid == cmd_text:
		return await ewslimeoid.petslimeoid(cmd=cmd)
	#elif ewcfg.cmd_quarterlyreport == cmd_text:
	#	return await ewmarket.quarterlyreport(cmd=cmd)
	elif ewcfg.cmd_salute == cmd_text:
		return await ewcmd.salute(cmd=cmd)
	elif ewcfg.cmd_get_policitous == cmd_text or ewcfg.cmd_get_policitous_alt1 == cmd_text:
		return await ewquadrants.get_policitous(cmd=cmd)
	elif ewcfg.cmd_get_violacious == cmd_text or ewcfg.cmd_get_violacious_alt1 == cmd_text:
		return await ewquadrants.get_violacious(cmd=cmd)
	elif ewcfg.cmd_get_sloshed == cmd_text or ewcfg.cmd_get_sloshed_alt1 == cmd_text:
		return await ewquadrants.get_sloshed(cmd=cmd)
	elif ewcfg.cmd_get_roseate == cmd_text or ewcfg.cmd_get_roseate_alt1 == cmd_text:
		return await ewquadrants.get_roseate(cmd=cmd)
	elif ewcfg.cmd_get_quadrants == cmd_text:
		return await ewquadrants.get_quadrants(cmd=cmd)
	elif ewcfg.cmd_harvest == cmd_text:
		return await ewcmd.harvest(cmd=cmd)
	elif ewcfg.cmd_check_farm == cmd_text:
		return await ewfarm.check_farm(cmd=cmd)
	elif ewcfg.cmd_bottleslimeoid == cmd_text:
		return await ewslimeoid.bottleslimeoid(cmd=cmd)
	elif ewcfg.cmd_unbottleslimeoid == cmd_text:
		return await ewslimeoid.unbottleslimeoid(cmd = cmd)
	elif ewcfg.cmd_piss == cmd_text:
		return await ewcmd.piss(cmd=cmd)
	elif ewcfg.cmd_scout == cmd_text:
		return await ewmap.scout(cmd=cmd)
	elif ewcfg.cmd_smoke == cmd_text:
		return await ewcosmeticitem.smoke(cmd=cmd)
	elif ewcfg.cmd_squeeze == cmd_text:
		return await ewitem.squeeze(cmd=cmd)
	elif ewcfg.cmd_watch == cmd_text:
		return await watch(cmd=cmd)
	elif ewcfg.cmd_setalarm == cmd_text:
		return await set_alarm(cmd=cmd)
	elif ewcfg.cmd_bootall == cmd_text:
		return await bootall(cmd=cmd)
	#elif cmd_text == "~bazaarupdate":
	 #   return await bazaar_update(cmd)
	elif cmd_text == ewcfg.cmd_help or  cmd_text == ewcfg.cmd_help_alt3:
		return await apt_help(cmd)
	elif cmd_text == ewcfg.cmd_commands or  cmd_text == ewcfg.cmd_commands_alt1:
		return await ewcmd.commands(cmd)
	elif cmd_text == ewcfg.cmd_accept or cmd_text == ewcfg.cmd_refuse:
		pass
	elif cmd_text == ewcfg.cmd_switch or cmd_text == ewcfg.cmd_switch_alt_1:
		return await ewwep.switch_weapon(cmd=cmd)
	elif cmd_text == ewcfg.cmd_changespray or cmd_text == ewcfg.cmd_changespray_alt1:
		return await ewdistrict.change_spray(cmd=cmd)
	elif cmd_text == ewcfg.cmd_tag:
		return await ewdistrict.tag(cmd=cmd)
	elif cmd_text == ewcfg.cmd_sidearm:
		return await ewwep.sidearm(cmd=cmd)
	elif cmd_text == ewcfg.cmd_stink:
		return await ewmutation.waft(cmd=cmd)
	elif cmd_text == ewcfg.cmd_bleedout:
		return await ewmutation.bleedout(cmd=cmd)
	elif cmd_text == ewcfg.cmd_thirdeye:
		return await ewmap.tracker(cmd=cmd)
	elif cmd_text == ewcfg.cmd_track:
		return await ewmutation.track_oneeyeopen(cmd=cmd)
	elif cmd_text == ewcfg.cmd_preserve:
		return await ewmutation.preserve(cmd=cmd)
	elif cmd_text == ewcfg.cmd_clench:
		return await ewmutation.clench(cmd=cmd)
	elif cmd_text == ewcfg.cmd_longdrop:
		return await ewitem.longdrop(cmd=cmd)
	elif cmd_text == ewcfg.cmd_trick or cmd_text == ewcfg.cmd_treat:
		pass
	elif cmd_text[0]==ewcfg.cmd_prefix: #faliure text
		randint = random.randint(1, 3)
		msg_mistake = "ENDLESS WAR is growing frustrated."
		if randint == 2:
			msg_mistake = "ENDLESS WAR denies you his favor."
		elif randint == 3:
			msg_mistake = "ENDLESS WAR pays you no mind."

		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, msg_mistake), 2)
"""
