import time

from .utils import format_ad_response
from ew.backend import ads as bknd_ads
from ew.backend.ads import EwAd
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict


async def advertise(cmd):
    time_now = int(time.time())
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.poi != ewcfg.poi_id_slimecorphq:
        response = "To buy ad space, you'll need to go SlimeCorp HQ."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    cost = ewcfg.slimecoin_toadvertise

    if user_data.slimecoin < cost:
        response = "Your don't have enough slimecoin to advertise. ({:,}/{:,})".format(user_data.slimecoin, cost)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    ads = bknd_ads.get_ads(cmd.guild.id)

    if len(ads) >= ewcfg.max_concurrent_ads:
        first_ad = EwAd(id_ad=ads[0])
        first_expire = first_ad.time_expir

        secs_to_expire = int(first_expire - time_now)
        mins_to_expire = int(secs_to_expire / 60)
        hours_to_expire = int(mins_to_expire / 60)
        days_to_expire = int(hours_to_expire / 24)

        expire_list = []
        if hours_to_expire > 0:
            expire_list.append("{} days".format(days_to_expire))
        if hours_to_expire > 0:
            expire_list.append("{} hours".format(hours_to_expire % 24))
        if mins_to_expire > 0:
            expire_list.append("{} minutes".format(mins_to_expire % 60))
        else:
            expire_list.append("{} seconds".format(secs_to_expire % 60))

        time_to_expire = ewutils.formatNiceList(names=expire_list, conjunction="and")

        response = "Sorry, but all of our ad space is currently in use. The next vacancy will be in {}.".format(time_to_expire)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.tokens_count < 2:
        response = "Please specify the content of your ad."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    content = cmd.message.content[len(cmd.tokens[0]):].strip()

    if len(content) > ewcfg.max_length_ads:
        response = "Your ad is too long, we can't fit that on a billboard. ({:,}/{:,})".format(len(content), ewcfg.max_length_ads)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    sponsor_disclaimer = "Paid for by {}".format(cmd.message.author.display_name)

    response = "This is what your ad is going to look like."
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    response = "{}\n\n*{}*".format(content, sponsor_disclaimer)
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    response = "It will cost {:,} slimecoin to stay up for 4 weeks. Is this fine? {} or {}".format(cost, ewcfg.cmd_confirm, ewcfg.cmd_cancel)
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    accepted = False
    try:
        msg = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == cmd.message.author and
                                                                                     message.content.lower() in [ewcfg.cmd_confirm, ewcfg.cmd_cancel])

        if msg != None:
            if msg.content.lower() == ewcfg.cmd_confirm:
                accepted = True
    except:
        accepted = False

    if accepted:
        bknd_ads.create_ad(
            id_server=cmd.guild.id,
            id_sponsor=cmd.message.author.id,
            content=content,
            time_expir=time_now + ewcfg.uptime_ads,
        )

        user_data.change_slimecoin(n=-cost, coinsource=ewcfg.coinsource_spending)

        user_data.persist()

        response = "Your ad will be put up immediately. Thank you for your business."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        response = "Good luck raising awareness by word of mouth."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def ads_look(cmd):
    user_data = EwUser(member=cmd.message.author)
    poi = poi_static.id_to_poi.get(user_data.poi)

    response = "You look around for ads. God, you love being advertised to...\n"

    ads = bknd_ads.get_ads(id_server=cmd.guild.id)

    if poi.has_ads and len(ads) > 0:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        for id_ad in ads:
            ad_data = EwAd(id_ad=id_ad)
            ad_resp = format_ad_response(ad_data)
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, ad_resp))

    else:
        response += "\nBut you couldn't find any. Bummer."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
