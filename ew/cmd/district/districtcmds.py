import asyncio

from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict
from ew.backend.dungeons import EwGamestate
from ew.backend.item import EwItem
from ew.backend import item as bknd_item
try:
    from ew.cmd import debug as ewdebug
except:
    from ew.cmd import debug_dummy as ewdebug

"""
	Informs the player about their current zone's capture progress
"""


async def capture_progress(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""

    poi = poi_static.id_to_poi.get(user_data.poi)
    response += "**{}**: ".format(poi.str_name)

    if not user_data.poi in poi_static.capturable_districts:
        response += "This zone cannot be captured."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    district_data = EwDistrict(id_server=user_data.id_server, district=user_data.poi)

    if district_data.controlling_faction != "":
        response += "{} control this district. ".format(district_data.controlling_faction.capitalize())
    elif district_data.capturing_faction != "" and district_data.cap_side != district_data.capturing_faction:
        response += "{} are de-capturing this district. ".format(district_data.capturing_faction.capitalize())
    elif district_data.capturing_faction != "":
        response += "{} are capturing this district. ".format(district_data.capturing_faction.capitalize())
    else:
        response += "Nobody has staked a claim to this district yet."

    response += "\n\n**Current influence: {:,}**\nMaximum influence: {:,}\nPercentage to maximum influence: {:,}%".format(abs(district_data.capture_points), int(ewcfg.max_capture_points[district_data.property_class]),
                                                                                                                                                   round((abs(district_data.capture_points) * 100 / (ewcfg.max_capture_points[district_data.property_class])), 1))

    # if district_data.time_unlock > 0:

    # response += "\nThis district cannot be captured currently. It will unlock in {}.".format(ewutils.formatNiceTime(seconds = district_data.time_unlock, round_to_minutes = True))
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# Old capping CMD
"""async def annex(cmd):
	user_data = EwUser(member = cmd.message.author)
	if user_data.life_state == ewcfg.life_state_shambler:
		response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	response = ""
	resp_cont = ewutils.EwResponseContainer(id_server = cmd.guild.id)
	time_now = int(time.time())

	poi = poi_static.id_to_poi.get(user_data.poi)

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "You ineffectively try shaking your can of spraypaint to whip up some sick graffiti. Alas, you’re all outta slime. " \
                   "They should really make these things compatible with ectoplasm."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	if not (len(user_data.faction) > 0 and user_data.life_state == ewcfg.life_state_enlisted):
		response = "Juveniles are too chickenshit to make graffiti and risk getting busted by the cops. Fuckin’ losers."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	if user_data.poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown]:
		response = "There’s no point, the rest of your gang has already covered this place in spraypaint. Focus on exporting your graffiti instead."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	if user_data.poi == ewcfg.poi_id_juviesrow:
		response = "Nah, the Rowdys and Killers have both agreed this is neutral ground. You don’t want to start a diplomatic crisis, " \
                   "just stick to spraying down sick graffiti and splattering your rival gang across the pavement in the other districts."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	if not user_data.poi in poi_static.capturable_districts:
		response = "This zone cannot be captured."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	district_data = EwDistrict(id_server = user_data.id_server, district = user_data.poi)


	if district_data.is_degraded():
		response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
	if district_data.time_unlock > 0:
		response = "You can’t spray graffiti here yet, it’s too soon after your rival gang extended their own cultural dominance over it. Try again in {}.".format(ewutils.formatNiceTime(seconds = district_data.time_unlock, round_to_minutes = True))
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	if district_data.all_neighbors_friendly():
		response = "What the hell are you doing, dude? You can’t put down any graffiti here, it’s been completely overrun by your rival gang. " \
                   "You can only spray districts that have at least one unfriendly neighbor, duh!"
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	users_in_district = district_data.get_players_in_district(
		life_states = [ewcfg.life_state_enlisted],
		ignore_offline = True,
		pvp_only = True
	)

	allies_in_district = district_data.get_players_in_district(
		factions = [user_data.faction],
		life_states = [ewcfg.life_state_enlisted],
		ignore_offline = True,
		pvp_only = True
	)

	if len(users_in_district) > len(allies_in_district):
		response = "Holy shit, deal with your rival gangsters first! You can’t spray graffiti while they’re on the prowl!"
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	mutations = user_data.get_mutations()

	slimes_spent = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)
	capture_discount = 1

	if ewcfg.mutation_id_lonewolf in mutations:
		if user_data.time_expirpvp > time_now:
			if len(users_in_district) == 1:
				capture_discount *= 0.8
		else:
			if len(users_in_district) == 0:
				capture_discount *= 0.8

	if ewcfg.mutation_id_patriot in mutations:
		capture_discount *= 0.8

	if slimes_spent == None:
		response = "How much slime do you want to spend on spraying graffiti in this district?"
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	if slimes_spent < 0:
		slimes_spent = user_data.slimes

	if slimes_spent > user_data.slimes:
		response = "You don't have that much slime, retard."
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

	num_lock = len(allies_in_district)
	if user_data.time_expirpvp < time_now:
		num_lock += 1

	if (district_data.controlling_faction not in ["", user_data.faction]) or (district_data.capturing_faction not in ["", user_data.faction]):
		slimes_decap = min(district_data.capture_points, int(slimes_spent / capture_discount))
		decap_resp = district_data.change_capture_points(
			progress = -slimes_decap,
			actor = user_data.faction,
			num_lock = num_lock
		)
		resp_cont.add_response_container(decap_resp)

		user_data.change_slimes(n = -slimes_decap * capture_discount, source = ewcfg.source_spending)
		slimes_spent -= slimes_decap * capture_discount

	slimes_cap = min(district_data.max_capture_points - district_data.capture_points, int(slimes_spent / capture_discount))
	cap_resp = district_data.change_capture_points(
		progress = slimes_cap,
		actor = user_data.faction,
		num_lock = num_lock
	)
	resp_cont.add_response_container(cap_resp)

	user_data.change_slimes(n = -slimes_cap * capture_discount, source = ewcfg.source_spending)

	# Flag the user for PvP
	# user_data.time_expirpvp = ewutils.calculatePvpTimer(user_data.time_expirpvp, ewcfg.time_pvp_annex, True)

	user_data.persist()
	district_data.persist()
	await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

	return await resp_cont.post()
"""


async def change_spray(cmd):
    user_data = EwUser(member=cmd.message.author)
    newspray = cmd.message.content[(len(ewcfg.cmd_changespray)):].strip()

    if newspray == "":
        response = "You need to add an image link to change your spray."
    elif len(newspray) > 400:
        response = "Fucking christ, are you painting the Sistine Chapel? Use a shorter link."
    else:
        response = "Got it. Spray set."
        user_data.spray = newspray
        user_data.persist()

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def tag(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state in (ewcfg.life_state_enlisted, ewcfg.life_state_kingpin):
        response = user_data.spray
    else:
        response = "Save the spraying for the gangsters. You're either too gay or dead to participate in this sort of thing."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


"""
    GVS COMMANDS
"""


async def shamble(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state != ewcfg.life_state_shambler and user_data.poi != ewcfg.poi_id_assaultflatsbeach:
        response = "You have too many higher brain functions left to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif user_data.life_state in [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted] and user_data.poi == ewcfg.poi_id_assaultflatsbeach:
        response = "You feel an overwhelming sympathy for the plight of the Shamblers and decide to join their ranks."
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        await asyncio.sleep(5)

        user_data = EwUser(member=cmd.message.author)
        user_data.life_state = ewcfg.life_state_shambler
        user_data.degradation = 100

        ewutils.moves_active[user_data.id_user] = 0

        user_data.poi = ewcfg.poi_id_nuclear_beach_edge
        user_data.persist()

        member = cmd.message.author

        base_poi_channel = fe_utils.get_channel(cmd.message.guild, 'nuclear-beach-edge')

        response = 'You arrive inside the facility and are injected with a unique strain of the Modelovirus. Not long after, a voice on the intercom chimes in.\n**"Welcome, {}. Welcome to Downpour Laboratories. It\'s safer here. Please treat all machines and facilities with respect, they are precious to our cause."**'.format(member.display_name)

        await ewrolemgr.updateRoles(client=cmd.client, member=member)
        return await fe_utils.send_message(cmd.client, base_poi_channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        pass


# Rest in fucking pieces

# if poi is None:
# 	return
# elif not poi.is_district:
# 	response = "This doesn't seem like an important place to be shambling. Try a district zone instead."
# 	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
# elif poi.id_poi == ewcfg.poi_id_oozegardens:
# 	response = "The entire district is covered in Brightshades! You have no business shambling this part of town!"
# 	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
#
# in_operation, op_poi = ewutils.gvs_check_if_in_operation(user_data)
# if in_operation:
# 	if op_poi != user_data.poi:
# 		response = "You aren't allowed to !shamble this district, per Dr. Downpour's orders.\n(**!goto {}**)".format(op_poi)
# 		return await fe_utils.send_message(cmd.client, cmd.message.channel,  fe_utils.formatMessage(cmd.message.author, response))
# else:
# 	response = "You aren't even in a Graveyard Op yet!\n(**!joinops [tombstone]**)"
# 	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
#
# if (time_now - user_data.time_lasthaunt) < ewcfg.cd_shambler_shamble:
# 	response = "You know, you really just don't have the energy to shamble this place right now. Try again in {} seconds.".format(int(ewcfg.cd_shambler_shamble-(time_now-user_data.time_lasthaunt)))
# 	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
#
# district_data = EwDistrict(district = poi.id_poi, id_server = cmd.guild.id)
#
# if district_data.degradation < poi.max_degradation:
# 	district_data.degradation += 1
# 	# user_data.degradation += 1
# 	user_data.time_lasthaunt = time_now
# 	district_data.persist()
# 	user_data.persist()
#
# 	response = "You shamble {}.".format(poi.str_name)
# 	await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
#
# 	if district_data.degradation == poi.max_degradation:
# 		response = ewcfg.str_zone_degraded.format(poi = poi.str_name)
# 		await fe_utils.send_message(cmd.client, cmd.message.channel, response)


async def rejuvenate(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.life_state == ewcfg.life_state_shambler and user_data.poi != ewcfg.poi_id_oozegardens:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif user_data.life_state == ewcfg.life_state_shambler and user_data.poi == ewcfg.poi_id_oozegardens:
        response = "You decide to change your ways and become one of the Garden Gankers in order to overthrow your old master."
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        await asyncio.sleep(5)

        user_data = EwUser(member=cmd.message.author)
        user_data.life_state = ewcfg.life_state_juvenile
        user_data.degradation = 0
        # user_data.gvs_currency = 0

        ewutils.moves_active[user_data.id_user] = 0

        user_data.poi = ewcfg.poi_id_og_farms
        user_data.persist()

        client = ewutils.get_client()
        server = client.get_guild(user_data.id_server)
        member = server.get_member(user_data.id_user)

        base_poi_channel = fe_utils.get_channel(cmd.message.guild, ewcfg.channel_og_farms)

        response = "You enter into Atomic Forest inside the farms of Ooze Gardens and are sterilized of the Modelovirus. Hortisolis gives you a big hug and says he's glad you've overcome your desire for vengeance in pursuit of deposing Downpour."

        await ewrolemgr.updateRoles(client=cmd.client, member=member)
        return await fe_utils.send_message(cmd.client, base_poi_channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        pass

async def ufo_observe(cmd):
    user_data = EwUser(member = cmd.message.author)

    cosmetics = bknd_item.inventory(id_user=user_data.id_user, id_server=cmd.guild.id, item_type_filter=ewcfg.it_cosmetic)

    protected = False
    for cosmetic in cosmetics:
        cosmetic_data = EwItem(id_item=cosmetic.get('id_item'))
        if cosmetic_data.item_props.get('id_cosmetic') == 'skinsuit':
            if cosmetic_data.item_props.get('adorned') == 'true':
                protected = True

    shipstate = EwGamestate(id_state='shipstate', id_server=cmd.guild.id)

    if user_data.poi != 'ufoufo':
        return await ewdebug.scrutinize(cmd=cmd)
    elif not protected:
        response = "Those aliens would probably ass-probe the fuck out of you if you messed with their equipment. Better not."
    elif shipstate.bit == 1:
        response = "The ship is grounded. Can't see much from here."
    elif cmd.tokens_count <= 1:
        response = "Observe what?"
    elif not ewcfg.dh_active or ewcfg.dh_stage < 3:
        response = "Wait, your alien espionage is waaaay out of season."
    else:
        poi_seek = ewutils.flattenTokenListToString(cmd.tokens[1:])
        poi_sought = poi_static.id_to_poi.get(poi_seek)
        if poi_sought is None:
            response = "The aliens know all the district names. You don't have to make up weird shit."
        elif poi_sought.id_poi == 'ufoufo':
            return await ewdebug.scrutinize(cmd=cmd)
        elif poi_sought.is_street:
            response = "You try to zoom in on a specific street, but you're a little too high up to get that level of detail."
        elif poi_sought.id_poi == 'blackpond' or (not poi_sought.is_district and not poi_sought.is_outskirts and not poi_sought.is_pier and poi_sought not in [ewcfg.poi_id_slimesendcliffs, ewcfg.poi_id_ferry, ewcfg.poi_id_sodafountain, ewcfg.poi_id_stockexchange, ewcfg.poi_id_ab_farms, ewcfg.poi_id_og_farms, ewcfg.poi_id_jr_farms]):
            response = "The X-ray vision on this viewport sucks. You can't really see indoors."
        elif poi_sought.id_poi in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown]:
            response = "Do you want to blow your cover, dumbass? Stop acting like a gangster. The gang bases are mostly indoors anyway."
        else:
            new_permissions = {"ufo-ufo": ["read", "send", "connect"]}
            new_permissions[poi_sought.channel] = ["read"]
            current_poi = poi_static.id_to_poi.get('ufoufo')
            response = ""
            if current_poi is not None:
                response = 'You point the observation reticle over at {}.'.format(poi_sought.str_name)
                district_data = EwDistrict(id_server=cmd.guild.id, district='ufoufo')
                poi_static.id_to_poi['ufoufo'].permissions = new_permissions
                players_in_district = district_data.get_players_in_district(min_slimes=0, life_states=[ewcfg.life_state_enlisted, ewcfg.life_state_corpse, ewcfg.life_state_juvenile, ewcfg.life_state_shambler], ignore_offline=True)
                server = ewcfg.server_list[cmd.guild.id]
                for playerid in players_in_district:
                    member_object = server.get_member(playerid)
                    await ewrolemgr.updateRoles(client=cmd.client, member=member_object)
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def launch(cmd):
    user_data = EwUser(member=cmd.message.author)
    protected = False
    cosmetics = bknd_item.inventory(id_user=user_data.id_user, id_server=cmd.guild.id, item_type_filter=ewcfg.it_cosmetic)
    for cosmetic in cosmetics:
        cosmetic_data = EwItem(id_item=cosmetic.get('id_item'))
        if cosmetic_data.item_props.get('id_cosmetic') == 'skinsuit':
            if cosmetic_data.item_props.get('adorned') == 'true':
                protected = True

    if user_data.poi != 'ufoufo':
        response = "Launch what, dumbass? My patience?"
    elif not protected:
        response = "The aliens aren't gonna let you start the ship. You're basically their captive now."
    elif not ewcfg.dh_active or ewcfg.dh_stage < 3:
        response = "Wait, your alien espionage is waaaay out of season."
    else:
        launchstate = EwGamestate(id_state='shipstate', id_server=cmd.guild.id)
        if launchstate.bit == 1:
            response = "PCHOOOOOOOOOO! Weird bleeps and bloops begin to increase in frequency as the ship rises back into the air!"
            launchstate.bit = 0
            launchstate.persist()
        else:
            response = "WHOOOOOOOO -CRASH! Your poor piloting crashes the ship back down. Your fellow alien crew seems excited, like you just chugged a whole bottle of their galactic lager or something. Good thing the hull is so shock resistant or you wouldn't be able to joyride again."
            launchstate.bit = 1
            launchstate.persist()
    return await fe_utils.send_message(cmd.client, cmd.message.channel,fe_utils.formatMessage(cmd.message.author, response))


async def abduct(cmd):
    user_data = EwUser(member=cmd.message.author)
    item_sought = bknd_item.find_item(item_search='alienbattery', id_user=cmd.message.author.id, id_server=cmd.guild.id)

    protected = False
    cosmetics = bknd_item.inventory(id_user=user_data.id_user, id_server=cmd.guild.id,
                                    item_type_filter=ewcfg.it_cosmetic)
    for cosmetic in cosmetics:
        cosmetic_data = EwItem(id_item=cosmetic.get('id_item'))
        if cosmetic_data.item_props.get('id_cosmetic') == 'skinsuit':
            if cosmetic_data.item_props.get('adorned') == 'true':
                protected = True

    shipstate = EwGamestate(id_server=user_data.id_server, id_state='shipstate')

    if user_data.poi != 'ufoufo':
        response = "Launch what, dumbass? My patience?"
    elif not protected:
        response = "The aliens aren't gonna let you start the ship. You're basically their captive now."
    elif not ewcfg.dh_active or ewcfg.dh_stage < 3:
        response = "Wait, your alien espionage is waaaay out of season."
    elif cmd.mentions_count == 0:
        response = "Abduct who?"
    elif cmd.mentions_count > 1:
        response = "One victim at a time, please."
    elif shipstate.bit == 1:
        response = 'The ship\'s on the ground right now, it can\'t reach you.'
    else:
        if item_sought:
            target_data = EwUser(member = cmd.mentions[0])
            target_poi = poi_static.id_to_poi.get(target_data.poi)
            target_channel = fe_utils.get_channel(cmd.message.guild, target_poi.channel)

            bknd_item.item_delete(id_item=item_sought.get('id_item'))
            response = 'You plug in your battery pack and begin to abduct {} They\'re 20 seconds away.'
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            await fe_utils.send_message(cmd.client, target_channel, fe_utils.formatMessage(cmd.mentions[0], "You are being abducted by aliens. The ship is 20 seconds away."))
            ewutils.active_restrictions[user_data.id_user] = 2
            await asyncio.sleep(20)

            ewutils.moves_active[cmd.message.author.id] = 0
            target_data.poi = 'ufoufo'
            user_data.persist()
            target_data.persist()

            await ewrolemgr.updateRoles(client=ewutils.get_client(), member=cmd.mentions[0])
            await target_data.move_inhabitants(id_poi='ufoufo')


        else:
            response = "The going energy cost for abduction is pretty expensive these days. You better have a battery pack before you do something like that."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def beam_me_up(cmd):
    user_data = EwUser(member=cmd.message.author)
    protected = False
    cosmetics = bknd_item.inventory(id_user=user_data.id_user, id_server=cmd.guild.id,
                                    item_type_filter=ewcfg.it_cosmetic)
    for cosmetic in cosmetics:
        cosmetic_data = EwItem(id_item=cosmetic.get('id_item'))

        print(cosmetic_data.item_props)
        if cosmetic_data.item_props.get('id_cosmetic') == 'skinsuit':
            if cosmetic_data.item_props.get('adorned') == 'true':
                protected = True

    poi_sought = poi_static.id_to_poi.get(user_data.poi)

    shipstate = EwGamestate(id_server=user_data.id_server, id_state='shipstate')

    if not protected:
        response = "Why would aliens abduct you? What makes you so special?"
    elif poi_sought.id_poi == 'ufoufo':
        response = 'You\'re already in here.'
    elif poi_sought.id_poi != ewcfg.poi_id_west_outskirts:
        response = "Hey, get a bit closer. The ship's in the West Outskirts. Beam up power doesn't grow on trees, you know."
    elif shipstate.bit == 1:
        response = 'The ship\'s on the ground right now, it can\'t beam shit.'
    else:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You are being abducted by aliens. The ship is 20 seconds away."))
        ewutils.active_restrictions[user_data.id_user] = 2
        await asyncio.sleep(20)

        ewutils.moves_active[cmd.message.author.id] = 0
        user_data.poi = 'ufoufo'
        user_data.persist()

        await ewrolemgr.updateRoles(client=ewutils.get_client(), member=cmd.message.author)
        await user_data.move_inhabitants(id_poi='ufoufo')

    return await fe_utils.send_message(cmd.client, cmd.message.channel,fe_utils.formatMessage(cmd.message.author, response))
