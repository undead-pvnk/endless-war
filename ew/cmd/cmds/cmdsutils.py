import random

from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.backend.market import EwStock
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import frontend as fe_utils
from ew.utils import market as market_utils
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict


def gen_score_text(ew_id, slime_alias):
    user_data = EwUser(ew_id=ew_id)

    items = bknd_item.inventory(id_user=user_data.id_user, id_server=user_data.id_server, item_type_filter=ewcfg.it_item)

    poudrin_amount = bknd_item.find_poudrin(id_user=user_data.id_user, id_server=user_data.id_server)

    if user_data.life_state == ewcfg.life_state_grandfoe:
        # Can't see a raid boss's slime score.
        response = "{}'s power is beyond your understanding.".format(ew_id.display_name)
    else:
        # return somebody's score
        response = "{} currently has {:,} {}{}.".format(ew_id.display_name, user_data.slimes, slime_alias, (" and {} {} poudrin{}".format(poudrin_amount, slime_alias, ("" if poudrin_amount == 1 else "s")) if poudrin_amount > 0 else ""))

    return response


def item_off(id_item, id_server, item_name = "", is_pushed_off = False):
    item_obj = EwItem(id_item=id_item)
    districtmodel = EwDistrict(id_server=id_server, district=ewcfg.poi_id_slimesendcliffs)
    slimetotal = 0

    if item_obj.item_props.get('id_furniture') == 'sord':
        response = "You toss the sord off the cliff, but for whatever reason, the damn thing won't go down. It just keeps going up and up, as though gravity itself blocked this piece of shit jpeg artifact on Twitter. It eventually goes out of sight, where you assume it flies into the sun."
        bknd_item.item_delete(id_item=id_item)
    elif random.randrange(500) < 125 or item_obj.item_type in([ewcfg.it_questitem, item_obj.item_type == ewcfg.it_medal, ewcfg.it_relic])  or item_obj.item_props.get('rarity') == ewcfg.rarity_princeps or item_obj.item_props.get('id_cosmetic') == "soul" or item_obj.item_props.get('id_furniture') == "propstand" :
        response = "You toss the {} off the cliff. It sinks into the ooze disappointingly.".format(item_name)
        bknd_item.give_item(id_item=id_item, id_server=id_server, id_user=ewcfg.poi_id_slimesea)

    elif random.randrange(500) < 498:
        response = "You toss the {} off the cliff. A nearby kraken swoops in and chomps it down with the cephalapod's equivalent of a smile. Your new friend kicks up some sea slime for you. Sick!".format(item_name)
        slimetotal = 2000 + random.randrange(10000)
        bknd_item.item_delete(id_item=id_item)

    else:
        response = "{} Oh fuck. FEEDING FRENZY!!! Sea monsters lurch down on the spoils like it's fucking christmas, and a ridiculous level of slime debris covers the ground. {}".format(ewcfg.emote_slime1, ewcfg.emote_slime1)
        slimetotal = 100000 + random.randrange(900000)

        bknd_item.item_delete(id_item=id_item)

    districtmodel.change_slimes(n=slimetotal)
    districtmodel.persist()
    return response


async def exec_mutations(cmd):
    user_data = EwUser(member=cmd.message.author)

    if cmd.mentions_count == 1:
        user_data = EwUser(member=cmd.mentions[0])

    status = user_data.getStatusEffects()

    if ewcfg.status_n1 in status:
        response = "They fight without expending themselves due to **Perfection**. They're precise even without a target due to **Indiscriminate Rage**. They're hard to fell and cut deep due to **Monolith Body**. They are immaculate and unaging due to **Immortality**."
    elif ewcfg.status_n2 in status:
        response = "They have unparalleled coordination, speed and reaction time due to **Fucked Out**. They prioritize best-in-breed productivity and physical enhancement synergy due to **Market Efficiency**. They can take the heat due to **Kevlar Attire**."
    elif ewcfg.status_n4 in status:
        response = "They are capable of murder by machine due to **Napalm Hacker**. Their hiding spot evades you due to **Super Amnesia**."
    elif ewcfg.status_n8 in status:
        response = "They take advantage of your moments of weakness due to **Opportunist**. They prioritize best-in-breed productivity and physical enhancement synergy due to **Market Efficiency**. They can take the heat due to **Kevlar Attire**."
    elif ewcfg.status_n11 in status:
        response = "They command a crowd through fear and punishment due to **Unnatural Intimidation**. They take advantage of your moments of weakness due to **Opportunist**. They prioritize best-in-breed productivity and physical enhancement synergy due to **Market Efficiency**. They can take the heat due to **Kevlar Attire**."
    elif ewcfg.status_n12 in status:
        response = "Their body holds untold numbers of quirks and perks due to **Full Aberrant**. They take advantage of your moments of weakness due to **Opportunist**. They prioritize best-in-breed productivity and physical enhancement synergy due to **Market Efficiency**. They can take the heat due to **Kevlar Attire**."
    elif ewcfg.status_n13 in status:
        response = "They are prone to explosive entries due to **Tantrum**. They take advantage of your moments of weakness due to **Opportunist**. They prioritize best-in-breed productivity and physical enhancement synergy due to **Market Efficiency**. They can take the heat due to **Kevlar Attire**."
    elif user_data.life_state == ewcfg.life_state_lucky:
        response = "They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. They are extremely fortunate due to **Lucky**. "
    else:
        response = "Slimecorp hasn't issued them mutations in their current position."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


def location_commands(cmd, search_poi = None):
    user_data = EwUser(member=cmd.message.author)
    if search_poi is not None:
        poi = search_poi
    else:
        poi = user_data.poi
    poi_obj = poi_static.id_to_poi.get(poi)
    response = "\n**THIS LOCATION:**\n"
    if poi in [ewcfg.poi_id_mine, ewcfg.poi_id_mine_sweeper, ewcfg.poi_id_mine_bubble, ewcfg.poi_id_tt_mines,
               ewcfg.poi_id_tt_mines_sweeper, ewcfg.poi_id_tt_mines_bubble, ewcfg.poi_id_cv_mines,
               ewcfg.poi_id_cv_mines_sweeper, ewcfg.poi_id_cv_mines_bubble]:
        response += ewcfg.mine_commands
    if poi_obj.is_pier == True:
        response += ewcfg.pier_commands
    if poi_obj.is_transport_stop == True or poi_obj.is_transport == True:
        response += ewcfg.transport_commands
    if poi_obj.is_apartment:
        response += ewcfg.apartment_commands
    if poi in [ewcfg.poi_id_greencakecafe, ewcfg.poi_id_nlacu, ewcfg.poi_id_neomilwaukeestate,
               ewcfg.poi_id_glocksburycomics]:
        response += ewcfg.zine_writing_places_commands
    if poi in [ewcfg.poi_id_ab_farms, ewcfg.poi_id_og_farms, ewcfg.poi_id_jr_farms]:
        response += ewcfg.farm_commands
    if poi in [ewcfg.poi_id_nlacu, ewcfg.poi_id_neomilwaukeestate]:
        response += "\n" + ewcfg.universities_commands
    if len(poi_obj.vendors) != 0:
        response += "\n" + ewcfg.shop_commands
    if ewcfg.district_unique_commands.get(poi) is not None:
        response += "\n" + ewcfg.district_unique_commands.get(poi)
    if response != "\n**THIS LOCATION:**\n":
        return response
    else:
        return ""


def mutation_commands(cmd):
    response = "\n**CURRENT MUTATIONS:**"
    user_data = EwUser(member=cmd.message.author)
    mutations = user_data.get_mutations()
    for mutation in mutations:
        if ewcfg.mutation_unique_commands.get(mutation) is not None:
            response += "\n" + ewcfg.mutation_unique_commands.get(mutation)

    if response != "\n**CURRENT MUTATIONS:**":
        return response
    else:
        return ""


def item_commands(cmd):
    response = "\n**IN YOUR INVENTORY:**"
    items_to_find = ewcfg.item_unique_commands.keys()
    user_data = EwUser(member=cmd.message.author)

    for lookup in items_to_find:
        item_sought = bknd_item.find_item(item_search=lookup, id_user=user_data.id_user, id_server=user_data.id_server)
        if item_sought:
            response += "\n" + ewcfg.item_unique_commands.get(lookup)
    if response != "\n**IN YOUR INVENTORY:**":
        return response
    else:
        return ""


""" used for !shares """


def get_user_shares_str(id_server = None, stock = None, id_user = None):
    response = ""
    if id_server != None and stock != None and id_user != None:
        user_data = EwUser(id_server=id_server, id_user=id_user)
        stock = EwStock(id_server=id_server, stock=stock)
        shares = market_utils.getUserTotalShares(id_server=user_data.id_server, stock=stock.id_stock, id_user=user_data.id_user)
        shares_value = round(shares * (stock.exchange_rate / 1000.0))

        response = "You have {shares:,} shares in {stock}".format(shares=shares, stock=ewcfg.stock_names.get(stock.id_stock))

        # if user_data.poi == ewcfg.poi_id_downtown:
        response += ", currently valued at {coin:,} SlimeCoin.".format(coin=shares_value)
        # else:
        #	response += "."

    return response

def get_crime_level(num, forYou = 1):
    if forYou == 0:
        pronounThey = 'they'
        pronounThem = 'them'
        pronounTheir = 'their'
    else:
        pronounThey = 'you'
        pronounThem = 'you'
        pronounTheir = 'your'

    for level in ewcfg.crime_status.keys():
        if num <= level:
            response = ewcfg.crime_status.get(level).format(they=pronounThey, them=pronounThem, their=pronounTheir)
            return response.capitalize()
    return ewcfg.crime_status.get(1000000)