import asyncio

from ew.backend import item as bknd_item
from ew.backend.apt import EwApartment
from ew.backend.item import EwItem
from ew.backend.market import EwStock
from ew.cmd import move as ewmap
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser


# This is quite literally not used anywhere
def check(str):
    if str.content == ewcfg.cmd_sign or str.content == ewcfg.cmd_rip:
        return True


# async def bazaar_update(cmd): ##DEBUG COMMAND. DO NOT RELEASE WITH THIS.
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

# while market_data.bazaar_wares.get('cosmetic3') is None or market_data.bazaar_wares.get('cosmetic3') == \
#	   market_data.bazaar_wares['cosmetic1'] or market_data.bazaar_wares.get('cosmetic3') == \
#	  market_data.bazaar_wares['cosmetic2']:
# market_data.bazaar_wares['cosmetic3'] = random.choice(bazaar_cosmetics)

# market_data.bazaar_wares['furniture1'] = random.choice(bazaar_furniture)


# market_data.persist()


async def usekey(cmd, owner_user):
    user_data = EwUser(member=cmd.message.author)
    poi = poi_static.id_to_poi.get(user_data.poi)
    poi_dest = poi_static.id_to_poi.get(ewcfg.poi_id_apt + owner_user.apt_zone)  # there isn't an easy way to change this, apologies for being a little hacky
    inv = bknd_item.inventory(id_user=cmd.message.author.id, id_server=cmd.guild.id)
    apartment = EwApartment(id_server=cmd.guild.id, id_user=owner_user.id_user)

    key = None
    for item_inv in inv:
        if "key to" in item_inv.get('name'):
            item_key_check = EwItem(id_item=item_inv.get('id_item'))
            if item_key_check.item_props.get("houseID") == str(owner_user.id_user):
                key = item_key_check

    if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You must enter an apartment in a zone's channel.".format(cmd.tokens[0])))
    elif key == None:
        response = "You don't have a key for their apartment."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif apartment.apt_class == ewcfg.property_class_c or (apartment.apt_class in [ewcfg.property_class_a, ewcfg.property_class_b] and key.id_item == apartment.key_2):
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Your key's not working at this new flat. Your roomates must've forgotten to upgrade apartments. Congratulations on the homelessness by the way.".format(cmd.tokens[0])))
    elif owner_user.apt_zone != poi.id_poi:
        response = "Your key doesn't match an apartment here."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        ewmap.move_counter += 1
        move_current = ewutils.moves_active[cmd.message.author.id] = ewmap.move_counter
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You start walking toward the apartment."))

        await asyncio.sleep(20)

        if move_current == ewutils.moves_active[cmd.message.author.id]:
            user_data = EwUser(member=cmd.message.author)
            user_data.poi = poi_dest.id_poi
            user_data.visiting = owner_user.id_user
            user_data.persist()
            await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
            response = "You're in the apartment."

            try:
                await fe_utils.send_message(cmd.client, cmd.message.author, response)
            except:
                await fe_utils.send_message(cmd.client, fe_utils.get_channel(cmd.guild, poi_dest.channel), fe_utils.formatMessage(cmd.message.author, response))


# returns a price based on the stock with the biggest change
def getPriceBase(cmd):
    # based on stock success
    user_data = EwUser(member=cmd.message.author)  # market rates average to 1000. This fomula calculates prices to specification based on that amount.
    kfc = EwStock(stock='kfc', id_server=user_data.id_server)
    tcb = EwStock(stock='tacobell', id_server=user_data.id_server)
    hut = EwStock(stock='pizzahut', id_server=user_data.id_server)
    if abs(kfc.market_rate - 1000) > abs(tcb.market_rate - 1000) and abs(kfc.market_rate - 1000) > abs(hut.market_rate - 1000):
        return kfc.market_rate * 201
    elif abs(tcb.market_rate - 1000) > abs(hut.market_rate - 1000):
        return tcb.market_rate * 201
    else:
        return hut.market_rate * 201


def letter_up(letter = None):
    if letter == ewcfg.property_class_a:
        return ewcfg.property_class_s
    elif letter == ewcfg.property_class_b:
        return ewcfg.property_class_a
    elif letter == ewcfg.property_class_c:
        return ewcfg.property_class_b


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
