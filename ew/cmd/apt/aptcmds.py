import asyncio
import random
import time

from ew.backend import item as bknd_item
from ew.backend.apt import EwApartment
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.player import EwPlayer
from ew.static import cfg as ewcfg
from ew.static import cosmetics
from ew.static import food as static_food
from ew.static import hue as hue_static
from ew.static import items as static_items
from ew.static import poi as poi_static
from ew.utils import apt as apt_utils
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import hunting as hunt_utils
from ew.utils import item as itm_utils
from ew.utils import move as move_utils
from ew.utils import prank as prank_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils import slimeoid as slimeoid_utils
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict
from ew.utils.frontend import EwResponseContainer
from ew.utils.slimeoid import EwSlimeoid, get_slimeoid_look_string
from .aptutils import getPriceBase, letter_up, usekey


async def nothing(cmd):  # for an accept, refuse, sign or rip
    return 0


async def retire(cmd = None, isGoto = False, movecurrent = None):
    user_data = EwUser(member=cmd.message.author)
    poi = poi_static.id_to_poi.get(user_data.poi)
    poi_dest = poi_static.id_to_poi.get(ewcfg.poi_id_apt + user_data.apt_zone)  # there isn't an easy way to change this, apologies for being a little hacky

    owner_user = None
    if cmd.mentions_count == 0 and cmd.tokens_count > 1 and isGoto == False:
        server = cmd.guild
        member_object = server.get_member(ewutils.getIntToken(cmd.tokens))
        owner_user = EwUser(member=member_object)
    elif cmd.mentions_count == 1:
        owner_user = EwUser(member=cmd.mentions[0])

    if owner_user:
        return await usekey(cmd, owner_user)
    if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))
    elif ewutils.active_restrictions.get(user_data.id_user) != None and ewutils.active_restrictions.get(user_data.id_user) > 0:
        response = "You can't do that right now."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif user_data.apt_zone != poi.id_poi:
        response = "You don't own an apartment here."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        if isGoto:
            move_current = movecurrent
        else:
            move_utils.move_counter += 1
            move_current = ewutils.moves_active[cmd.message.author.id] = move_utils.move_counter
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You start walking toward your apartment."))
        await asyncio.sleep(20)

        if move_current == ewutils.moves_active[cmd.message.author.id]:
            user_data = EwUser(member=cmd.message.author)
            user_data.poi = poi_dest.id_poi
            user_data.persist()
            await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
            response = "You're in your apartment."

            try:
                await fe_utils.send_message(cmd.client, cmd.message.author, response)
            except:
                await fe_utils.send_message(cmd.client, fe_utils.get_channel(cmd.guild, poi_dest.channel), fe_utils.formatMessage(cmd.message.author, response))


async def depart(cmd = None, isGoto = False, movecurrent = None):
    player = EwPlayer(id_user=cmd.message.author.id)
    user_data = EwUser(id_user=player.id_user, id_server=player.id_server)
    poi_source = poi_static.id_to_poi.get(user_data.poi)
    poi_dest = poi_static.id_to_poi.get(poi_source.mother_districts[0])

    # isgoto checks if this is part of a goto command.

    client = ewutils.get_client()
    server = ewcfg.server_list[user_data.id_server]
    member_object = server.get_member(user_data.id_user)

    if not poi_source.is_apartment:
        response = "You're not in an apartment."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        if isGoto:
            move_current = movecurrent
        else:
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You exit the apartment."))
            move_utils.move_counter += 1
            move_current = ewutils.moves_active[cmd.message.author.id] = move_utils.move_counter
        await asyncio.sleep(20)
        if move_current == ewutils.moves_active[cmd.message.author.id]:
            user_data = EwUser(id_user=player.id_user, id_server=player.id_server)
            user_data.poi = poi_dest.id_poi
            user_data.visiting = ewcfg.location_id_empty
            user_data.time_lastenter = int(time.time())
            ewutils.active_target_map[user_data.id_user] = ""
            user_data.persist()

            ewutils.end_trade(user_data.id_user)
            await user_data.move_inhabitants(id_poi=poi_dest.id_poi)

            await ewrolemgr.updateRoles(client=client, member=member_object)

            if isGoto:
                response = "You arrive in {}.".format(poi_dest.str_name)

            else:
                response = "Here we are. The outside world."

            await fe_utils.send_message(cmd.client, fe_utils.get_channel(server, poi_dest.channel), fe_utils.formatMessage(cmd.message.author, response))

            # SWILLDERMUK
            await prank_utils.activate_trap_items(poi_dest.id_poi, user_data.id_server, user_data.id_user)

            return


async def consult(cmd):
    target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
    # to check the descriptions, look for consult_responses in ewcfg

    if target_name == None or len(target_name) == 0:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "What region would you like to look at?"))

    user_data = EwUser(member=cmd.message.author)
    response = ""

    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.poi != ewcfg.poi_id_realestate:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You have to !consult at the Real Estate Agency in Old New Yonkers."))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(target_name)

    if poi == None:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "That place doesn't exist. The stupidity of the question drives the realtor to down another bottle."))

    elif poi.id_poi in poi_static.transports:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "As much as the realtor would like to charge you for being homeless, you can't pay rent for sleeping on public transport."))

    elif poi.id_poi == ewcfg.poi_id_rowdyroughhouse or poi.id_poi == ewcfg.poi_id_copkilltown or poi.id_poi == ewcfg.poi_id_juviesrow:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "\"We don't have apartments in such...urban places,\" your consultant mutters under his breath."))


    elif poi.is_subzone:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You don't find it on the list of properties. Try something that isn't a subzone."))

    elif poi.id_poi == ewcfg.poi_id_assaultflatsbeach or poi.id_poi == ewcfg.poi_id_dreadford:  # check for DT and other S districts separately, otherwise rank by class
        multiplier = ewcfg.apartment_s_multiplier

    elif poi.id_poi == ewcfg.poi_id_downtown:
        multiplier = ewcfg.apartment_dt_multiplier

    elif poi.property_class == ewcfg.property_class_c:
        multiplier = 1

    elif poi.property_class == ewcfg.property_class_b:
        multiplier = ewcfg.apartment_b_multiplier

    elif poi.property_class == ewcfg.property_class_a:
        multiplier = ewcfg.apartment_a_multiplier

    else:
        response = "Not for sale."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    if ewcfg.consult_responses[poi.id_poi]:
        response = "You ask the realtor what he thinks of {}.\n\n\"".format(poi.str_name) + ewcfg.consult_responses[poi.id_poi] + "\"\n\n"
        response += "The cost per month is {:,} SC. \n\n The down payment is four times that, {:,} SC.".format(multiplier * getPriceBase(cmd=cmd), multiplier * 4 * getPriceBase(cmd=cmd))
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def signlease(cmd):
    target_name = ewutils.flattenTokenListToString(cmd.tokens[1:])
    if target_name == None or len(target_name) == 0:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "What region would you like to rent?"))

    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.poi != ewcfg.poi_id_realestate:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You have to !signlease at the Real Estate Agency in Old New Yonkers."))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(target_name)

    if poi == None:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "That place doesn't exist. The consultant behind the counter is aroused by your stupidity."))

    elif poi == ewcfg.poi_id_rowdyroughhouse or poi == ewcfg.poi_id_copkilltown or poi == ewcfg.poi_id_juviesrow:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "\"We don't have apartments in such...urban places,\" your consultant mutters under his breath."))

    elif poi.id_poi in poi_static.transports:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "As much as the realtor would like to charge you for being homeless, you can't pay rent for sleeping on public transport."))

    elif poi.is_subzone:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You don't find it on the list of properties. Try something that isn't a subzone."))
    # these prices are based on prices in the design doc.
    elif poi.id_poi == ewcfg.poi_id_assaultflatsbeach or poi.id_poi == ewcfg.poi_id_dreadford:
        base_cost = ewcfg.apartment_s_multiplier * getPriceBase(cmd=cmd)

    elif poi.id_poi == ewcfg.poi_id_downtown:
        base_cost = ewcfg.apartment_dt_multiplier * getPriceBase(cmd=cmd)

    elif poi.property_class == ewcfg.property_class_c:
        base_cost = getPriceBase(cmd=cmd)

    elif poi.property_class == ewcfg.property_class_b:
        base_cost = ewcfg.apartment_b_multiplier * getPriceBase(cmd=cmd)

    elif poi.property_class == ewcfg.property_class_a:
        base_cost = ewcfg.apartment_a_multiplier * getPriceBase(cmd=cmd)

    else:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "Not for sale."))

    if (user_data.slimecoin < base_cost * 4):
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You can't afford it."))

    response = "The receptionist slides you a contract. It reads:\n\n THE TENANT, {},  WILL HERETO SUBMIT {:,} SLIMECOIN EACH MONTH UNTIL THEY INEVITABLY HIT ROCK BOTTOM. THEY MUST ALSO PROVIDE A DOWN PAYMENT OF {:,} TO INSURE THE PROPERTY FROM THEIR GREASY JUVENILE HANDS. LANDLORD(S) ARE NOT RESPONSIBLE FOR ANY INJURY OR PROPERTY DAMAGE THAT MAY OCCUR ON THE PREMISES. THEY'RE ALSO NOT RESPONSIBLE IN GENERAL. YOU ARE. BITCH. \n\nDo you !sign the document, or do you !rip it into a million pieces?".format(
        cmd.message.author.display_name, base_cost, base_cost * 4)
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    try:
        message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and
                                                                                         message.content.lower() in [ewcfg.cmd_sign, ewcfg.cmd_rip])

        if message != None:
            if message.content.lower() == ewcfg.cmd_sign:
                accepted = True
            if message.content.lower() == ewcfg.cmd_rip:
                accepted = False

    except Exception as e:
        print(e)
        accepted = False

    if not accepted:
        response = "You dirty the agency's floor with your wanton ripping of contracts. Ah. How satisfying."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:

        user_data = EwUser(member=cmd.message.author)
        user_apt = EwApartment(id_user=user_data.id_user, id_server=user_data.id_server)

        if (user_data.apt_zone != ewcfg.location_id_empty):
            had_old_place = True
        else:
            had_old_place = False

        user_data.change_slimecoin(n=-base_cost * 4, coinsource=ewcfg.coinsource_spending)
        user_data.apt_zone = poi.id_poi
        user_data.persist()

        # if user_apt.key_1 != 0:
        # bknd_item.item_delete(user_apt.key_1)
        # user_apt.key_1 = 0
        # user_apt.rent = user_apt.rent/1.5
        # if user_apt.key_2 != 0:
        # bknd_item.item_delete(user_apt.key_2)
        # user_apt.key_2 = 0
        # user_apt.rent = user_apt.rent / 1.5
        user_apt.num_keys = 0

        user_apt.name = "{}'s Apartment".format(cmd.message.author.display_name)
        user_apt.apt_class = poi.property_class
        user_apt.description = "This new flat is fucking cash, bro.".format(cmd.message.author.display_name)
        user_apt.poi = poi.id_poi
        user_apt.rent = base_cost
        user_apt.persist()

        response = "You signed the lease for an apartment in {} for {:,} SlimeCoin a month.".format(poi.str_name, base_cost)

        if had_old_place:
            response += " The receptionist calls up a moving crew, who quickly move your stuff to your new place. "
        else:
            # FUCK ENERGY stock has plummeted, so the real estate agency can't afford to give out so many!
            value = random.choice(ewcfg.fuck_energies)
            item = static_food.food_map.get(value)
            item_props = itm_utils.gen_item_props(item)
            item_props["time_fridged"] = str(int(time.time()))
            id_item = bknd_item.item_create(
                item_type=ewcfg.it_food,
                id_user='{}{}'.format(cmd.message.author.id, 'fridge'),
                id_server=cmd.guild.id,
                stack_max=-1,
                stack_size=0,
                item_props=item_props
            )

        await apt_utils.toss_squatters(user_data.id_user, user_data.id_server)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def apartment(cmd):
    usermodel = EwUser(member=cmd.message.author)
    apartmentmodel = EwApartment(id_user=usermodel.id_user, id_server=usermodel.id_server)
    if usermodel.apt_zone == ewcfg.location_id_empty:
        response = "You don't have an apartment."

    else:
        poi = poi_static.id_to_poi.get(usermodel.apt_zone)
        response = "Your apartment is in {}. This {} rank apartment costs {:,} SlimeCoin a month.".format(poi.str_name, apartmentmodel.apt_class.upper(), apartmentmodel.rent)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def upgrade(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
    apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)

    if usermodel.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if usermodel.apt_zone == ewcfg.location_id_empty:
        response = "You don't have an apartment."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    elif usermodel.poi != ewcfg.poi_id_realestate:
        response = "Upgrade your home at the apartment agency."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    elif (apt_model.apt_class == ewcfg.property_class_s):
        response = "Fucking hell, man. You're loaded, and we're not upgrading you."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    elif (usermodel.slimecoin < apt_model.rent * 8):
        response = "You can't even afford the down payment. We're not entrusting an upgrade to a 99%er like you."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        poi = poi_static.id_to_poi.get(usermodel.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=usermodel.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        response = "Are you sure? The upgrade cost is {:,} SC, and rent goes up to {:,} SC per month. To you !accept the deal, or do you !refuse it?".format(apt_model.rent * 8, apt_model.rent * 2)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        accepted = False

        try:
            message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and
                                                                                             message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

            if message != None:
                if message.content.lower() == ewcfg.cmd_accept:
                    accepted = True
                if message.content.lower() == ewcfg.cmd_refuse:
                    accepted = False
        except:
            accepted = False

        if not accepted:
            response = "Eh. Your loss."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
            apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)

            usermodel.change_slimecoin(n=apt_model.rent * -8, coinsource=ewcfg.coinsource_spending)

            apt_model.rent *= 2
            apt_model.apt_class = letter_up(letter=apt_model.apt_class)

            usermodel.persist()
            apt_model.persist()
            response = "The deed is done. Back at your apartment, a builder nearly has a stroke trying to speed-renovate. You're now rank {}.".format(apt_model.apt_class)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def knock(cmd = None):
    user_data = EwUser(member=cmd.message.author)
    poi = poi_static.id_to_poi.get(user_data.poi)

    target_data = None
    if cmd.mentions_count == 0 and cmd.tokens_count > 1:
        server = ewcfg.server_list[user_data.id_server]
        target = server.get_member(cmd.tokens[1])
        target_data = EwUser(member=target)
    elif cmd.mentions_count == 1:
        target = cmd.mentions[0]
        target_data = EwUser(member=cmd.mentions[0])

    if target_data:
        target_poi = poi_static.id_to_poi.get(target_data.poi)
        if poi.is_apartment:
            response = "You're already in an apartment."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.apt_zone != user_data.poi:
            response = "You're not anywhere near their apartment."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif (not target_poi.is_apartment) or target_data.visiting != ewcfg.location_id_empty:
            response = "You knock, but nobody's home."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            response = "{} is knocking at your door. Do you !accept their arrival, or !refuse entry?".format(cmd.message.author.display_name)
            try:
                await fe_utils.send_message(cmd.client, target, fe_utils.formatMessage(target, response))
            except:
                response = "They aren't taking in any visitors right now."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            try:
                accepted = False
                if ewutils.active_target_map.get(user_data.id_user) == target_data.apt_zone:
                    return  # returns if the user is spam knocking. However, the person in the apt still gets each of the DMs above.
                else:
                    user_data = EwUser(member=cmd.message.author)
                    ewutils.active_target_map[user_data.id_user] = target_data.apt_zone
                    message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == target and
                                                                                                     message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                    if message != None:
                        if message.content.lower() == ewcfg.cmd_accept:
                            accepted = True
                        if message.content.lower() == ewcfg.cmd_refuse:
                            accepted = False

                            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "They don't want your company, and have tipped off the authorities."))
                    else:
                        pass
            # user_data = EwUser(member=cmd.message.author)
            # if ewutils.active_target_map.get(user_data.id_user) != "": #checks if a user is knocking, records the recipient and removes it when done
            #	user_data.persist()
            except:
                accepted = False
            user_data = EwUser(member=cmd.message.author)
            if accepted:
                user_data.poi = target_poi.id_poi
                user_data.visiting = target_data.id_user
                ewutils.active_target_map[user_data.id_user] = ""
                user_data.persist()
                await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)
                response = "You arrive in the abode of {}.".format(target.display_name)
                await fe_utils.send_message(cmd.client, cmd.message.author, fe_utils.formatMessage(cmd.message.author, response))
                response = "{} enters your home.".format(cmd.message.author.display_name)
                return await fe_utils.send_message(cmd.client, target, fe_utils.formatMessage(target, response))
            else:
                if ewutils.active_target_map.get(user_data.id_user) != "":
                    ewutils.active_target_map[user_data.id_user] = ""
    elif cmd.mentions_count == 0:
        response = "Whose door are you knocking?"
        return await fe_utils.send_message(cmd.client, cmd.message.author, fe_utils.formatMessage(cmd.message.author, response))
    else:
        response = "One door at a time, please."
        return await fe_utils.send_message(cmd.client, cmd.message.author, fe_utils.formatMessage(cmd.message.author, response))


async def trickortreat(cmd = None):
    user_data = EwUser(member=cmd.message.author)

    if ewutils.channel_name_is_poi(cmd.message.channel.name) == False:
        response = "There will be neither trick nor treat found in these parts."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "The undead are too wicked and impure for such acts. Seems you can't have your cake and !haunt it too on Double Halloween."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.hunger >= user_data.get_hunger_max():
        response = "You're too hungry to trick-or-treat right now."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    reject = False

    items = bknd_item.inventory(
        id_user=cmd.message.author.id,
        id_server=cmd.guild.id,
        item_type_filter=ewcfg.it_cosmetic
    )

    costumes = 0
    for it in items:
        i = EwItem(it.get('id_item'))
        id_cosmetic = i.item_props.get('id_cosmetic')
        adorned = i.item_props.get('adorned')
        if (id_cosmetic == 'dhcostume' or id_cosmetic == 'costume') and adorned == 'true':
            costumes += 1

    if costumes == 0:
        response = "How are you gonna go trick-or-treating without a costume on?"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count == 1:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)
        target_poi = poi_static.id_to_poi.get(target_data.poi)
        if poi.is_apartment:
            response = "You're already in an apartment."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.apt_zone != user_data.poi:
            response = "You're not anywhere near their apartment."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif (not target_poi.is_apartment) or target_data.visiting != ewcfg.location_id_empty:
            response = "You knock, but nobody's home."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            response = "{} is all dressed up for Double Halloween, waiting at your doorstep. Do you pull a !trick on them, or !treat them to a piece of candy?".format(cmd.message.author.display_name)

            try:
                await fe_utils.send_message(cmd.client, target, fe_utils.formatMessage(target, response))
            except:
                response = "They aren't taking in any visitors right now."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            try:
                treat = False
                if ewutils.active_target_map.get(user_data.id_user) == target_data.apt_zone:
                    # For Double Halloween spam knocking isn't really an issue. Just clear up their slot in the active target map for now.
                    # print('DEBUG: Spam knock in trickortreat command.')
                    ewutils.active_target_map[user_data.id_user] = ""
                    return  # returns if the user is spam knocking. However, the person in the apt still gets each of the DMs above.
                else:
                    user_data = EwUser(member=cmd.message.author)
                    ewutils.active_target_map[user_data.id_user] = target_data.apt_zone
                    message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == target and
                                                                                                     message.content.lower() in [ewcfg.cmd_trick, ewcfg.cmd_treat])

                    if message != None:
                        if message.content.lower() == ewcfg.cmd_treat:
                            treat = True
                        if message.content.lower() == ewcfg.cmd_trick:
                            treat = False
                    else:
                        reject = True
                    # user_data = EwUser(member=cmd.message.author)
                    # if ewutils.active_target_map.get(user_data.id_user) != "": #checks if a user is knocking, records the recipient and removes it when done
                    #	user_data.persist()
            except:
                reject = True
            user_data = EwUser(member=cmd.message.author)

            if reject:
                response = "No response. Maybe they're busy?"
                await fe_utils.send_message(cmd.client, cmd.message.author, fe_utils.formatMessage(cmd.message.channel, response))
                response = "You just sort of wait in your apartment until they go away."
                return await fe_utils.send_message(cmd.client, target, fe_utils.formatMessage(target, response))

            hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
            user_data.hunger += ewcfg.hunger_pertrickortreat * int(hunger_cost_mod)
            user_data.persist()

            if treat:
                ewutils.active_target_map[user_data.id_user] = ""

                item = random.choice(static_food.trickortreat_results)
                item_props = itm_utils.gen_item_props(item)
                if item is not None:
                    bknd_item.item_create(
                        item_type=item.item_type,
                        id_user=cmd.message.author.id,
                        id_server=cmd.guild.id,
                        item_props=item_props
                    )
                item_name = item_props.get('food_name')

                response = "{} gives you a {}. You thank them, and go about your business.".format(target.display_name, item_name)
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                response = "You give {} a {}. Happy Double Halloween, you knucklehead!".format(cmd.message.author.display_name, item_name)
                return await fe_utils.send_message(cmd.client, target, fe_utils.formatMessage(target, response))
            else:
                slime_loss = random.randrange(10000) + 1

                if slime_loss <= 10:
                    trick_index = 0
                elif slime_loss <= 100:
                    trick_index = 1
                elif slime_loss <= 1000:
                    trick_index = 2
                else:
                    trick_index = 3

                if ewutils.active_target_map.get(user_data.id_user) != None and ewutils.active_target_map.get(user_data.id_user) != "":
                    ewutils.active_target_map[user_data.id_user] = ""
                user_data.change_slimes(n=-slime_loss, source=ewcfg.source_damage)
                if user_data.slimes <= 0:
                    client = ewutils.get_client()
                    server = client.get_guild(user_data.id_server)
                    user_poi = poi_static.id_to_poi.get(user_data.poi)

                    resp_cont = EwResponseContainer(id_server=user_data.id_server)
                    player_data = EwPlayer(id_user=user_data.id_user, id_server=user_data.id_server)

                    user_data.trauma = ewcfg.trauma_id_environment
                    user_data.die(cause=ewcfg.cause_killing)
                    deathreport = "{skull} *{uname}*: You were tricked to death. {skull}".format(skull=ewcfg.emote_slimeskull, uname=player_data.display_name)

                    resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)
                    resp_cont.add_channel_response(user_poi.channel, deathreport)

                    await resp_cont.post()
                    await ewrolemgr.updateRoles(client=client, member=server.get_member(user_data.id_user))

                user_data.persist()
                response = ewcfg.halloween_tricks_trickee[trick_index].format(target.display_name, slime_loss)
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                response = ewcfg.halloween_tricks_tricker[trick_index].format(cmd.message.author.display_name, slime_loss)
                return await fe_utils.send_message(cmd.client, target, fe_utils.formatMessage(target, response))


    elif cmd.mentions_count == 0:
        user_poi = poi_static.id_to_poi.get(user_data.poi)

        if user_poi.is_capturable:
            hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
            user_data.hunger += ewcfg.hunger_pertrickortreat * int(hunger_cost_mod)
            user_data.persist()

            trick_chance = 10

            lowtrick = 10
            mediumtrick = 7
            hightrick = 4
            extremetrick = 3

            property_class = user_poi.property_class

            if property_class == ewcfg.property_class_c:
                trick_chance = lowtrick
            elif property_class == ewcfg.property_class_b:
                trick_chance = mediumtrick
            elif property_class == ewcfg.property_class_a:
                trick_chance = hightrick
            elif property_class == ewcfg.property_class_s:
                trick_chance = extremetrick

            class_based_treats = []
            for treat in static_food.trickortreat_results:
                if trick_chance == lowtrick and treat.price == 100:
                    class_based_treats.append(treat)
                elif trick_chance == mediumtrick and treat.price == 1000:
                    class_based_treats.append(treat)
                elif trick_chance == hightrick and treat.price == 10000:
                    class_based_treats.append(treat)
                elif trick_chance == extremetrick and treat.price == 100000:
                    class_based_treats.append(treat)

            response = "You try and go trick-or-treating around various houses in {}.\n".format(user_poi.str_name)

            if random.randrange(trick_chance) == 0:
                treat = False
            else:
                treat = True

            if treat:
                item = random.choice(class_based_treats)
                item_props = itm_utils.gen_item_props(item)
                if item is not None:
                    bknd_item.item_create(
                        item_type=item.item_type,
                        id_user=cmd.message.author.id,
                        id_server=cmd.guild.id,
                        item_props=item_props
                    )
                item_name = item_props.get('food_name')

                response += "A kind resident gives you a {}. You thank them, and go about your business.".format(item_name)
            else:
                slime_loss = random.randrange(10000) + 1

                if slime_loss <= 10:
                    trick_index = 0
                elif slime_loss <= 100:
                    trick_index = 1
                elif slime_loss <= 1000:
                    trick_index = 2
                else:
                    trick_index = 3

                user_data.change_slimes(n=-slime_loss, source=ewcfg.source_damage)
                if user_data.slimes <= 0:
                    client = ewutils.get_client()
                    server = client.get_guild(user_data.id_server)
                    user_poi = poi_static.id_to_poi.get(user_data.poi)

                    resp_cont = EwResponseContainer(id_server=user_data.id_server)
                    player_data = EwPlayer(id_user=user_data.id_user, id_server=user_data.id_server)

                    user_data.trauma = ewcfg.trauma_id_environment
                    user_data.die(cause=ewcfg.cause_killing)
                    deathreport = "{skull} *{uname}*: You were tricked to death. {skull}".format(skull=ewcfg.emote_slimeskull, uname=player_data.display_name)

                    resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)
                    resp_cont.add_channel_response(user_poi.channel, deathreport)

                    await resp_cont.post()
                    await ewrolemgr.updateRoles(client=client, member=server.get_member(user_data.id_user))
                user_data.persist()
                response += ewcfg.halloween_tricks_trickee[trick_index].format("A pranksterous resident", slime_loss)

            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            response = "Whose door are you knocking?"
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        response = "One door at a time, please."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def cancel(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
    aptmodel = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    if usermodel.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if usermodel.poi != ewcfg.poi_id_realestate:
        response = "You can only null your lease at the Real Estate Agency."
    elif usermodel.apt_zone == ewcfg.location_id_empty:
        response = "You don't have an apartment."
    elif aptmodel.rent * 4 > usermodel.slimecoin:
        response = "You can't afford the lease separation. Time to take your eviction like a champ."
    else:
        poi = poi_static.id_to_poi.get(usermodel.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=usermodel.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        poi = poi_static.id_to_poi.get(usermodel.apt_zone)
        response = "The separation will cost {:,} SlimeCoin. Do you !accept the termination, or !refuse it?".format(aptmodel.rent * 4)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        try:
            accepted = False
            message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and
                                                                                             message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

            if message != None:
                if message.content.lower() == ewcfg.cmd_accept:
                    accepted = True
                if message.content.lower() == ewcfg.cmd_refuse:
                    accepted = False
        except:
            accepted = False
        if not accepted:
            response = "Ahahaha. Of course you don't."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)
            aptmodel = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)

            response = "You cancel your {} apartment for {:,} SlimeCoin.".format(poi.str_name, aptmodel.rent * 4)
            inv_toss_closet = bknd_item.inventory(id_user=str(usermodel.id_user) + ewcfg.compartment_id_closet, id_server=playermodel.id_server)

            apt_utils.toss_items(id_user=str(usermodel.id_user) + ewcfg.compartment_id_closet, id_server=playermodel.id_server, poi=poi)
            apt_utils.toss_items(id_user=str(usermodel.id_user) + ewcfg.compartment_id_fridge, id_server=playermodel.id_server, poi=poi)
            apt_utils.toss_items(id_user=str(usermodel.id_user) + ewcfg.compartment_id_decorate, id_server=playermodel.id_server, poi=poi)

            usermodel.apt_zone = ewcfg.location_id_empty
            usermodel.change_slimecoin(n=aptmodel.rent * -4, coinsource=ewcfg.coinsource_spending)
            aptmodel.rent = 0
            aptmodel.poi = ""
            aptmodel.apt_class = ewcfg.property_class_c
            usermodel.persist()
            aptmodel.persist()

            await apt_utils.toss_squatters(cmd.message.author.id, cmd.guild.id)
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def frame(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    namechange = cmd.message.content[(len(ewcfg.cmd_frame)):].strip()

    if bknd_item.find_item(item_search="pictureframe", id_user=usermodel.id_user, id_server=playermodel.id_server, item_type_filter=ewcfg.it_furniture) and len(namechange) >= 3:
        item_sought = bknd_item.find_item(item_search="pictureframe", id_user=usermodel.id_user, id_server=playermodel.id_server, item_type_filter=ewcfg.it_furniture)
        item = EwItem(id_item=item_sought.get('id_item'))
        item.item_props['furniture_desc'] = namechange
        item.persist()
        response = "You slip the photo into a frame."
    elif len(namechange) < 3:
        response = "You try to put the nothing you have into the frame, but then you realize that's fucking stupid. Put an image link in there"
    else:
        response = "You don't have a frame."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def dyefurniture(cmd):
    first_id = ewutils.flattenTokenListToString(cmd.tokens[1:2])
    second_id = ewutils.flattenTokenListToString(cmd.tokens[2:])

    try:
        first_id_int = int(first_id)
        second_id_int = int(second_id)
    except:
        first_id_int = None
        second_id_int = None

    if first_id != None and len(first_id) > 0 and second_id != None and len(second_id) > 0:
        response = "You don't have one."

        items = bknd_item.inventory(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
        )

        furniture = None
        dye = None
        for item in items:
            if item.get('id_item') in [first_id_int, second_id_int] or first_id in ewutils.flattenTokenListToString(
                    item.get('name')) or second_id in ewutils.flattenTokenListToString(item.get('name')):
                if item.get('item_type') == ewcfg.it_furniture and furniture is None:
                    furniture = item

                if item.get('item_type') == ewcfg.it_item and item.get('name') in static_items.dye_map and dye is None:
                    dye = item

                if furniture != None and dye != None:
                    break

        if furniture != None:
            if dye != None:
                user_data = EwUser(member=cmd.message.author)

                furniture_item = EwItem(id_item=furniture.get("id_item"))
                dye_item = EwItem(id_item=dye.get("id_item"))

                hue = hue_static.hue_map.get(dye_item.item_props.get('id_item'))

                response = "You dye your {} in {} paint!".format(furniture_item.item_props.get('furniture_name'), hue.str_name)
                furniture_item.item_props['hue'] = hue.id_hue

                furniture_item.persist()
                bknd_item.item_delete(id_item=dye.get('id_item'))
            else:
                response = 'Use which dye? Check your **!inventory**.'
        else:
            response = 'Dye which furniture? Check your **!inventory**.'

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, 'You need to specify which furniture you want to paint and which dye you want to use! Check your **!inventory**.'))


async def add_key(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    apartment_data = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
    if user_data.poi != ewcfg.poi_id_realestate:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You need to request a housekey at the Real Estate Agency."))
    elif user_data.apt_zone == ewcfg.location_id_empty:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You don't have an apartment."))
    elif apartment_data.apt_class == ewcfg.property_class_c:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You're practically homeless yourself with that slumhouse you've leased out. Upgrade your house to get a roommate!"))
    elif (apartment_data.apt_class == ewcfg.property_class_b or apartment_data.apt_class == ewcfg.property_class_a) and apartment_data.num_keys >= 1:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You already have a roommate. If we let you guys create hippie communes like you're trying we'd go out of business."))
    elif apartment_data.apt_class == ewcfg.property_class_s and apartment_data.num_keys >= 2:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "2 roommates is enough. You upgraded the apartment, and we upgraded its fragile load bearing capacity. But not by much."))
    elif user_data.slimecoin < apartment_data.rent:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You need to pay base rent in order to receive a new housekey. It sadly appears as though you can't even afford a new friend."))
    else:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        response = "Adding a key will change your rent to {:,} SlimeCoin. It will cost {:,}, as a down payment. Do you !accept or !refuse?".format(int(apartment_data.rent * 1.5), apartment_data.rent)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        try:
            accepted = False
            message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and
                                                                                             message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse, ewcfg.cmd_addkey])

            if message != None:
                if message.content.lower() == ewcfg.cmd_accept:
                    accepted = True
                if message.content.lower() == ewcfg.cmd_refuse:
                    accepted = False
                if message.content.lower() == ewcfg.cmd_addkey: # If this isn't here, !addkey can spammed to get past 2 keys. No multiple keys, posers.
                    accepted = False
        except:
            accepted = False
        if not accepted:
            response = "Ok, sure. Live alone forever. See if I care."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
            user_data.change_slimecoin(n=-apartment_data.rent, coinsource=ewcfg.coinsource_spending)
            user_data.persist()

            new_item_id = bknd_item.item_create(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type=ewcfg.it_item,
                item_props={
                    'item_name': "key to {}'s house".format(playermodel.display_name),
                    'id_item': "housekey",
                    'item_desc': "A key to {}'s house. They must trust you a lot.".format(playermodel.display_name),
                    'rarity': ewcfg.rarity_plebeian,
                    'houseID': "{}".format(cmd.message.author.id),
                    'context': "housekey"
                }
            )
            new_item = EwItem(id_item=new_item_id)
            new_item.soulbound = True
            new_item.persist()

            apartment_data.num_keys += 1
            apartment_data.rent = apartment_data.rent * 1.5
            if apartment_data.key_1 == 0:
                apartment_data.key_1 = new_item_id
            else:
                apartment_data.key_2 = new_item_id
            apartment_data.persist()
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "The realtor examines your profile for a bit before opening his filing cabinet and pulling out a key from the massive pile. 'You two lovebirds enjoy yourselves', he sleepily remarks before tossing it onto the desk. Sweet, new key!"))


async def manual_changelocks(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    apartment_data = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
    if user_data.poi != ewcfg.poi_id_realestate:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You need to request a housekey at the Real Estate Agency."))
    elif user_data.apt_zone == ewcfg.location_id_empty:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You don't have an apartment."))
    elif apartment_data.num_keys <= 0:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You don't have any roommates. You live alone."))
    elif user_data.slimecoin < apartment_data.rent * 0.5:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You need to pay half of base rent in order to change the locks around. Whatever scourge you set loose on your property, you'll just have to live with them."))
    else:
        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        response = "Changing the locks will revert your rent back to before you added keys. It will cost {:,}, though. Do you !accept or !refuse?".format(apartment_data.rent / 2)
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        try:
            accepted = False
            message = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and
                                                                                             message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

            if message != None:
                if message.content.lower() == ewcfg.cmd_accept:
                    accepted = True
                if message.content.lower() == ewcfg.cmd_refuse:
                    accepted = False
        except:
            accepted = False
        if not accepted:
            response = "Ahahaha. Of course you don't."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            user_data = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)
            user_data.change_slimecoin(n=-(apartment_data.rent / 2), coinsource=ewcfg.coinsource_spending)
            user_data.persist()

            apartment_data = EwApartment(id_user=cmd.message.author.id, id_server=playermodel.id_server)
            if apartment_data.key_1 != 0:
                bknd_item.item_delete(apartment_data.key_1)
                apartment_data.key_1 = 0
                apartment_data.rent = apartment_data.rent / 1.5
            if apartment_data.key_2 != 0:
                bknd_item.item_delete(apartment_data.key_2)
                apartment_data.key_2 = 0
                apartment_data.rent = apartment_data.rent / 1.5
            apartment_data.num_keys = 0
            apartment_data.persist()

            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "The realtor makes a couple of shady sounding phone calls and informs you the keys have been permanently destroyed."))


async def set_alarm(cmd):
    player_data = EwPlayer(id_user=cmd.message.author.id)
    user_data = EwUser(id_user=cmd.message.author.id, id_server=player_data.id_server)
    item_search = ewutils.flattenTokenListToString(cmd.tokens[2:])
    time_set = ewutils.flattenTokenListToString(cmd.tokens[1:2])

    if ((not time_set[:-2].isnumeric()) or not (time_set[-2:] == "am" or time_set[-2:] == "pm")) and time_set != "off":
        response = "You're setting it wrong, dumbass. See, I knew you were bad at this."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    item_sought = bknd_item.find_item(item_search=item_search, id_user=user_data.id_user, id_server=player_data.id_server)
    if item_sought:
        item = EwItem(id_item=item_sought.get('id_item'))
        if "alarmclock" == item.item_props.get('id_furniture'):
            item.item_props['furniture_name'] = "alarm clock set to {}".format(time_set)
            item.persist()
            response = "You set the clock to {}.".format(time_set)
        else:
            response = "That's not an alarm clock. Be less delusional next time."
    else:
        response = "You don't have an item like that."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


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

    furns = bknd_item.inventory(id_user=lookObject + ewcfg.compartment_id_decorate, id_server=playermodel.id_server, item_type_filter=ewcfg.it_furniture)

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
        furn_response += "SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP. SUBMIT TO SLIMECORP.\n\n"

    market_data = EwMarket(id_server=playermodel.id_server)
    clock_data = ewutils.weather_txt(market_data)
    clock_data = clock_data[16:20]
    furn_response = furn_response.format(time=clock_data)
    resp_cont.add_channel_response(cmd.message.channel, furn_response)

    response = ""
    iterate = 0
    frids = bknd_item.inventory(id_user=lookObject + ewcfg.compartment_id_fridge, id_server=playermodel.id_server)

    if (len(frids) > 0):
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

    freezeList = get_slimeoid_look_string(user_id=lookObject + 'freeze', server_id=playermodel.id_server)

    resp_cont.add_channel_response(cmd.message.channel, freezeList)
    return await resp_cont.post(channel=cmd.message.channel)


async def wash(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)
    slimeoid_search = slimeoid_utils.find_slimeoid(slimeoid_search=item_search, id_server=playermodel.id_server, id_user=playermodel.id_user)
    slimeoid = EwSlimeoid(id_slimeoid=slimeoid_search, id_server=playermodel.id_server, id_user=playermodel.id_user)
    if usermodel.visiting != ewcfg.location_id_empty:
        usermodel = EwUser(id_user=usermodel.visiting, id_server=playermodel.id_server)

    if bknd_item.find_item(item_search="washingmachine", id_user=str(usermodel.id_user) + ewcfg.compartment_id_decorate, id_server=playermodel.id_server, item_type_filter=ewcfg.it_furniture):
        if item_sought:
            item = EwItem(id_item=item_sought.get('id_item'))
            if item.item_type == ewcfg.it_cosmetic:
                if item.item_props.get('hue') is None or item.item_props.get('hue') == "":
                    response = "You jam your dirty laundry into the machine. It's so loud you can't hear the gunshots outside anymore, but you're sure the neighbors won't mind. Some time later, your {} pops out, freshly cleaned and full of static.".format(item.item_props.get('cosmetic_name'))
                else:
                    item.item_props['hue'] = ""
                    item.persist()
                    response = "You toss the {} into the washing machine. The thing shakes and sputters like a juvie begging for its life, but after a few minutes your {} comes out undyed.".format(item.item_props.get('cosmetic_name'), item.item_props.get('cosmetic_name'))
                if item.item_props.get('adorned') == 'true':
                    response += " You readorn the {}. Man, this feels comfy.".format(item.item_props.get('cosmetic_name'))
            else:
                response = "Don't put a {} in the washing machine. You'll break it. Christ, you spent like 1.6 mega on that fucking thing.".format(item_sought.get('name'))
        elif slimeoid_search and slimeoid.life_state == ewcfg.slimeoid_state_active:
            if (slimeoid.hue == "" or slimeoid.hue is None) and (slimeoid.coating == "" or slimeoid.coating is None):
                response = "You tell {} that there's a poudrin for it in the washer. D'aww. It's so trusting. The moment it enters, you close the lid and crank the spin cycle. You laugh for awhile, but quickly realize you don't know how to pause it and let {} out. Guess you'll have to wait the full 20 minutes. Time passes, and your slimeoid stumbles out, nearly unconscious. Sorry, little buddy.".format(
                    slimeoid.name, slimeoid.name)
            else:
                response = "You toss your colored slimeoid in the washing machine and press start. Not only is {} now tumbling around and getting constantly scalded by the water, it's also suddenly insecure about how you wanted to rid it of its racial identity. After about 20 minutes {} steps out, demoralized, exhausted, and green as an ogre. Nice. Nice.".format(slimeoid.name, slimeoid.name)
                slimeoid.hue = ""
                slimeoid.coating = ""
                slimeoid.persist()
        elif item_search == "":
            response = "There's nothing to wash. You start the machine anyway, riding it like a fucking bucking bronco. This thing really was a great investment."
        elif item_search == "brain":
            response = "You learn the cult-like ideology that all washing machines share. Truly, this new philosophy will change the future of humanity, and you'll be the one it all starts with. You'll follow this washing machine through thick and thin, through cover-ups and mass suicide plots. The religion will be called: LAUNDRONISM. \n\nActually, you know what? This is fucking stupid. ENDLESS WAR is way better at brainwashing than this rusty old thing."
        else:
            response = "There's no item or slimeoid with that name. "
    else:
        response = "You don't have a washing machine."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def browse(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    if bknd_item.find_item(item_search="laptopcomputer", id_user=str(usermodel.id_user) + ewcfg.compartment_id_decorate, id_server=playermodel.id_server):
        response = random.choice(ewcfg.browse_list)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        await apt_look(cmd=cmd)


async def store_item(cmd):
    cmd_text = cmd.tokens[0].lower() if len(cmd.tokens) >= 1 else ""

    # Consider moving this map to ewcfg, though its inconsequential
    text_to_dest = {
        ewcfg.cmd_fridge: ewcfg.compartment_id_fridge,
        ewcfg.cmd_store: "store",
        ewcfg.cmd_closet: ewcfg.compartment_id_closet,
        ewcfg.cmd_decorate: ewcfg.compartment_id_decorate,
        ewcfg.cmd_shelve: ewcfg.compartment_id_bookshelf,
        ewcfg.cmd_shelve_alt_1: ewcfg.compartment_id_bookshelf
    }

    dest = text_to_dest[cmd_text]

    destination = dest  # used to separate the compartment keyword from the string displayed to the user.
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    user_mutations = usermodel.get_mutations()
    apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=playermodel.id_server)

    if usermodel.visiting != ewcfg.location_id_empty:
        recipient = str(usermodel.visiting)
        apt_model = EwApartment(id_server=playermodel.id_server, id_user=usermodel.visiting)

    else:
        recipient = str(cmd.message.author.id)

    if item_sought:
        item = EwItem(id_item=item_sought.get('id_item'))
        if item_sought.get('soulbound') and EwItem(id_item=item_sought.get('id_item')).item_props.get("context") != "housekey":
            response = "You can't just put away soulbound items. You have to keep them in your pants at least until the Rapture hits."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif item_sought.get('item_type') == ewcfg.it_furniture and (dest != ewcfg.compartment_id_decorate and dest != "store"):
            response = "The fridge and closet don't have huge spaces for furniture storage. Try !decorate or !stow instead."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif item_sought.get('item_type') != ewcfg.it_furniture and (dest == ewcfg.compartment_id_decorate):
            response = "Are you going to just drop items on the ground like a ruffian? Store them in your fridge or closet instead."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        if destination == "store":
            if item_sought.get('item_type') == ewcfg.it_food:
                destination = ewcfg.compartment_id_fridge

            elif item_sought.get('item_type') == ewcfg.it_furniture:
                destination = ewcfg.compartment_id_decorate

            elif item_sought.get('item_type') == ewcfg.it_book:
                destination = ewcfg.compartment_id_bookshelf

            else:
                destination = ewcfg.compartment_id_closet

        storage_limit_base = 8
        if apt_model.apt_class == ewcfg.property_class_b:
            storage_limit_base *= 2

        elif apt_model.apt_class == ewcfg.property_class_a:
            storage_limit_base *= 4

        elif apt_model.apt_class == ewcfg.property_class_s:
            storage_limit_base *= 8

        if ewcfg.mutation_id_packrat in user_mutations:
            storage_limit_base *= 2

        name_string = item_sought.get('name')

        items_stored = bknd_item.inventory(id_user=recipient + destination, id_server=playermodel.id_server)

        if len(items_stored) >= storage_limit_base * 2 and destination == ewcfg.compartment_id_closet:
            response = "The closet is bursting at the seams. Fearing the consequences of opening the door, you decide to hold on to the {}.".format(name_string)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif len(items_stored) >= storage_limit_base and destination == ewcfg.compartment_id_fridge:
            response = "The fridge is so full it's half open, leaking 80's era CFCs into the flat. You decide to hold on to the {}.".format(name_string)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif len(items_stored) >= int(storage_limit_base * 1.5) and destination == ewcfg.compartment_id_decorate:
            response = "You have a lot of furniture here already. Hoarding is unladylike, so you decide to hold on to the {}.".format(name_string)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        elif len(items_stored) >= int(storage_limit_base * 3) and destination == ewcfg.compartment_id_bookshelf:
            response = "Quite frankly, you doubt you wield the physical ability to cram another zine onto your bookshelf, so you decided to hold on to the {}.".format(name_string)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        if item.item_type == ewcfg.it_food and destination == ewcfg.compartment_id_fridge:
            item.item_props["time_fridged"] = time.time()
            item.persist()

        elif item.item_type == ewcfg.it_weapon:
            if usermodel.weapon == item.id_item:
                if usermodel.weaponmarried:
                    response = "If only it were that easy. But you can't just shove your lover in a {}.".format(destination)
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                usermodel.weapon = -1
                usermodel.persist()
            elif usermodel.sidearm == item.id_item:
                usermodel.sidearm = -1
                usermodel.persist()

        elif item.item_type == ewcfg.it_cosmetic:
            item.item_props["adorned"] = 'false'
            item.item_props["slimeoid"] = 'false'
            item.persist()

        bknd_item.give_item(id_item=item.id_item, id_server=playermodel.id_server, id_user=recipient + destination)

        if (destination == ewcfg.compartment_id_decorate):
            response = item.item_props['furniture_place_desc']

        else:
            response = "You store the {} in the {}.".format(name_string, destination)
            hatrack = bknd_item.find_item(id_server=playermodel.id_server, id_user=str(playermodel.id_user) + "decorate", item_search="hatstand")
            if destination == "closet" and item_sought.get('item_type') == ewcfg.it_cosmetic:
                map_obj = cosmetics.cosmetic_map.get(item.item_props.get('id_cosmetic'))
                if map_obj != None:
                    if map_obj.is_hat == True and hatrack:
                        response = "You hang the {} on the rack.".format(name_string)

    else:
        response = "Are you sure you have that item?"

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def remove_item(cmd):
    cmd_text = cmd.tokens[0].lower() if len(cmd.tokens) >= 1 else ""

    # Consider moving this map to ewcfg, though its inconsequential
    text_to_dest = {
        ewcfg.cmd_take: "apartment",
        ewcfg.cmd_uncloset: ewcfg.compartment_id_closet,
        ewcfg.cmd_unfridge: ewcfg.compartment_id_fridge,
        ewcfg.cmd_undecorate: ewcfg.compartment_id_decorate,
        ewcfg.cmd_unshelve: ewcfg.compartment_id_bookshelf,
        ewcfg.cmd_unshelve_alt_1: ewcfg.compartment_id_bookshelf
    }
    dest = text_to_dest[cmd_text]
    destination = dest  # used to separate the compartment keyword from the string displayed to the user.

    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    if usermodel.visiting != ewcfg.location_id_empty:
        recipient = str(usermodel.visiting)

    else:
        recipient = str(cmd.message.author.id)
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

    aptmodel = EwApartment(id_user=recipient, id_server=playermodel.id_server)
    key_1 = EwItem(id_item=aptmodel.key_1)
    key_2 = EwItem(id_item=aptmodel.key_2)

    if key_1.id_owner != str(usermodel.id_user) and key_2.id_owner != str(usermodel.id_user) and usermodel.visiting != ewcfg.location_id_empty:
        response = "Burglary takes finesse. You are but a lowly gangster, who takes money the old fashioned way."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # if the command is "take", we need to determine where the item might be
    if dest == "apartment":
        item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_bookshelf, id_server=playermodel.id_server)
        if not item_sought:
            item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_fridge, id_server=playermodel.id_server)
            if not item_sought:
                item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_closet, id_server=playermodel.id_server)
                if not item_sought:
                    item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_decorate, id_server=playermodel.id_server)
                else:
                    destination = ewcfg.compartment_id_closet
            else:
                destination = ewcfg.compartment_id_fridge
        else:
            destination = ewcfg.compartment_id_bookshelf

    elif dest == ewcfg.compartment_id_fridge:
        item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_fridge, id_server=playermodel.id_server)

    elif dest == ewcfg.compartment_id_closet:
        item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_closet, id_server=playermodel.id_server)

    elif dest == ewcfg.compartment_id_decorate:
        item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_decorate, id_server=playermodel.id_server)
        destination = "apartment"

    elif dest == ewcfg.compartment_id_bookshelf:
        item_sought = bknd_item.find_item(item_search=item_search, id_user=recipient + ewcfg.compartment_id_bookshelf, id_server=playermodel.id_server)

    if item_sought:
        name_string = item_sought.get('name')
        item = EwItem(id_item=item_sought.get('id_item'))

        if item_sought.get('item_type') == ewcfg.it_food:
            food_items = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=playermodel.id_server,
                item_type_filter=ewcfg.it_food
            )
            if len(food_items) >= usermodel.get_food_capacity():
                del food_items
                response = "You can't carry any more food."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif item_sought.get('item_type') == ewcfg.it_weapon:
            wep_items = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=playermodel.id_server,
                item_type_filter=ewcfg.it_weapon
            )
            if len(wep_items) >= usermodel.get_weapon_capacity():
                del wep_items
                response = "You can't carry any more weapons."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            other_items = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=playermodel.id_server,
                item_type_filter=item_sought.get('item_type')
            )
            if len(other_items) >= ewcfg.generic_inv_limit:
                del other_items
                response = ewcfg.str_generic_inv_limit.format(item_sought.get('item_type'))
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        if item_sought.get('item_type') == ewcfg.it_food and destination == ewcfg.compartment_id_fridge:
            # the formula is: expire time = expire time + current time - time frozen
            if int(float(item.item_props.get('time_fridged'))) != 0:
                item.item_props['time_expir'] = str(int(float(item.item_props.get('time_expir'))) + (int(time.time()) - int(float(item.item_props.get('time_fridged')))))
            else:
                item.item_props['time_expir'] = str(int(float(item.item_props.get('time_fridged'))) + 43200)
            item.time_expir = int(float(item.item_props.get('time_expir')))
            item.item_props['time_fridged'] = '0'
            item.persist()

        bknd_item.give_item(id_item=item.id_item, id_server=playermodel.id_server, id_user=cmd.message.author.id)

        response = "You take the {} from the {}.".format(name_string, destination)

        hatrack = bknd_item.find_item(id_server=playermodel.id_server, id_user=str(playermodel.id_user) + "decorate", item_search="hatstand")
        if destination == "closet" and item_sought.get('item_type') == ewcfg.it_cosmetic:
            map_obj = cosmetics.cosmetic_map.get(item.item_props.get('id_cosmetic'))
            if map_obj != None:
                if map_obj.is_hat == True and hatrack:
                    response = "You take the {} off the rack.".format(name_string)

        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        response = "Are you sure you have that item?"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def watch(cmd):
    player_model = EwPlayer(id_user=cmd.message.author.id)
    user_model = EwUser(id_user=cmd.message.author.id, id_server=player_model.id_server)

    check_poi = poi_static.id_to_poi.get(user_model.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    poi = user_model.poi

    if user_model.visiting != ewcfg.location_id_empty:
        user_id = user_model.visiting
    else:
        user_id = cmd.message.author.id
    apartment_model = EwApartment(id_server=cmd.guild.id, id_user=user_id)
    apartment_model.persist()

    poi_object = poi_static.id_to_poi.get(poi)
    item_sought = bknd_item.find_item(id_user=str(user_id) + ewcfg.compartment_id_decorate, id_server=player_model.id_server, item_search="television")
    if item_sought:
        item_obj = EwItem(id_item=item_sought.get('id_item'))
    else:
        item_obj = None

    if not poi_object.is_apartment:
        response = "Watching TV in public sounds like a good idea on paper, but when you're 3 hours in, braindead and drooling your fucking tonsils out your yapper you won't want the masses taking pictures."
    elif not item_sought:
        response = "There's no TV here. Give it up and go back to killing people."
    elif item_obj and "television" not in item_obj.item_props.get('id_furniture'):
        response = "Get your counterfeit TVs out of here before you start watching the real deal."
    else:
        user_model.persist()
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You begin watching TV."))
        for x in range(0, 62):
            await asyncio.sleep(300)
            # await asyncio.sleep(1)
            user_model = EwUser(id_user=cmd.message.author.id, id_server=player_model.id_server)
            item_sought = bknd_item.find_item(id_user=str(user_id) + ewcfg.compartment_id_decorate, id_server=player_model.id_server, item_search="television")
            if user_model.poi == poi and user_model.time_last_action > (int(time.time()) - ewcfg.time_kickout) and item_sought:
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, random.choice(ewcfg.tv_lines)))
            else:
                if user_model.time_last_action <= (int(time.time()) - ewcfg.time_kickout):
                    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You fell asleep watching TV."))
                else:
                    return
        # await asyncio.sleep(1)
        await asyncio.sleep(300)
        for lyric in ewcfg.the_slime_lyrics:
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, lyric))
            await asyncio.sleep(8)

        poi = poi_static.id_to_poi.get(user_model.poi)

        await hunt_utils.spawn_enemy(id_server=player_model.id_server, pre_chosen_type=ewcfg.enemy_type_megaslime, pre_chosen_poi=poi.mother_districts[0], pre_chosen_slimes=ewcfg.tv_set_slime, pre_chosen_level=ewcfg.tv_set_level, pre_chosen_displayname="The Slime")
        response = ""

    user_model = EwUser(id_user=cmd.message.author.id, id_server=player_model.id_server)
    ewutils.active_target_map[user_model.id_user] = ""
    user_model.persist()
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# slimeoid storage works just like regular item storage. Just add "freeze" to the owner's name to store it.
async def freeze(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    ew_slime_model = EwSlimeoid(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    if usermodel.visiting != ewcfg.location_id_empty and ew_slime_model.name != "":
        response = "Your slimeoid, sensing you're trying to abandon them in someone else's freezer, begins to pout. Dammit, you can't refuse a face like that."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    elif usermodel.visiting != ewcfg.location_id_empty:
        response = "You don't have a slimeoid on you."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if ew_slime_model.name != "":
        ew_slime_model.id_user += "freeze"
        ew_slime_model.life_state = ewcfg.slimeoid_state_stored
        ew_slime_model.persist()
        usermodel.active_slimeoid = -1
        usermodel.persist()
        response = "You pick up your slimeoid. {} wonders what is going on, but trusts you implicitly. You open the freezer. {} begins to panic. However, you overpower them, shove them in the icebox, and quickly close the door. Whew. You wonder if this is ethical.".format(ew_slime_model.name, ew_slime_model.name)

    else:
        response = "You don't have a slimeoid for that."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def unfreeze(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_server=playermodel.id_server, id_user=cmd.message.author.id)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    firstCheck = True
    slimeoid_search = ""

    for token in cmd.tokens:  # check for first occurrence in comma separated list
        if firstCheck:
            firstCheck = False

        else:
            slimeoid_search += token + " "

    slimeoid_search = slimeoid_search[:-1]
    id_slimeoid = slimeoid_utils.find_slimeoid(id_user=str(cmd.message.author.id) + "freeze", id_server=playermodel.id_server, slimeoid_search=slimeoid_search)
    if id_slimeoid != None:
        ew_slime_model = EwSlimeoid(id_user=str(cmd.message.author.id) + "freeze", id_slimeoid=id_slimeoid, id_server=playermodel.id_server)
    else:
        ew_slime_model = EwSlimeoid(id_user=str(cmd.message.author.id) + "freeze", slimeoid_name=slimeoid_search, id_server=playermodel.id_server)
    yourslimeoid = EwSlimeoid(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    if usermodel.visiting != ewcfg.location_id_empty:
        response = "The freezer's stuck! Well you're a guest, anyhow. You probably shouldn't steal any slimeoids."

    elif yourslimeoid.name != "":
        response = "You already have a slimeoid on you. !freeze it first."

    elif slimeoid_search == None or len(slimeoid_search) == 0:
        response = "You need to specify your slimeoid's name."

    elif ew_slime_model.name == None or len(ew_slime_model.name) == 0:
        response = "You don't have anyone like that in the fridge."

    else:
        ew_slime_model.id_user = cmd.message.author.id
        ew_slime_model.life_state = ewcfg.slimeoid_state_active
        ew_slime_model.persist()
        usermodel.active_slimeoid = ew_slime_model.id_slimeoid
        usermodel.persist()
        response = "You open the freezer. Your slimeoid stumbles out, desperately gasping for air. {} isn't sure what it did to deserve cryostasis, but it gives you an apologetic yap in order to earn your forgiveness. \n\n {} is now your slimeoid.".format(ew_slime_model.name, ew_slime_model.name, ew_slime_model.name)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def customize(cmd):
    cmd_text = cmd.tokens[0].lower() if len(cmd.tokens) >= 1 else ""
    isDesc = True if cmd_text == ewcfg.cmd_aptdesc else False

    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    apt_model = EwApartment(id_server=playermodel.id_server, id_user=cmd.message.author.id)

    # dual function for changing apt info

    if not isDesc:  # check for description function or name function
        property_type = "name"
        namechange = cmd.message.content[(len(ewcfg.cmd_aptname)):].strip()
    else:
        property_type = "description"
        namechange = cmd.message.content[(len(ewcfg.cmd_aptdesc)):].strip()

    if usermodel.visiting != ewcfg.location_id_empty:
        response = "This apartment isn't yours."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if property_type == "name":
        apt_model.name = namechange

    elif property_type == "description":
        apt_model.description = namechange

    response = "You changed the {}.".format(property_type)

    if len(namechange) < 2:
        response = "You didn't enter a proper {}.".format(property_type)

    else:
        apt_model.persist()

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def bootall(cmd):
    playermodel = EwPlayer(id_user=cmd.message.author.id)
    usermodel = EwUser(id_user=cmd.message.author.id, id_server=playermodel.id_server)

    check_poi = poi_static.id_to_poi.get(usermodel.poi)
    if not (check_poi.is_apartment and (cmd.message.guild is None or check_poi.channel == cmd.message.channel.name)):
        return await apt_utils.lobbywarning(cmd)

    await apt_utils.toss_squatters(user_id=usermodel.id_user, server_id=usermodel.id_server, keepKeys=True)

    response = "You throw a furious tantrum and shoo all the undesirables out. It's only you and your roommates now."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
