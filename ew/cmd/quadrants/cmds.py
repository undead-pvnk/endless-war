import random

from .utils import get_quadrant
from ew.backend.quadrants import EwQuadrant
from ew.static import cfg as ewcfg
from ew.static import quadrants as quad_static
from ew.utils import frontend as fe_utils
from ew.utils.combat import EwUser


async def add_quadrant(cmd):
    response = ""
    author = cmd.message.author
    quadrant = None
    user_data = EwUser(id_user=author.id, id_server=author.guild.id)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    for token in cmd.tokens[1:]:
        if token.lower() in quad_static.quadrants_map:
            quadrant = quad_static.quadrants_map[token.lower()]
        if quadrant is not None:
            break

    if quadrant is None:
        response = "Please select a quadrant for your romantic feelings."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count == 0:
        response = "Please select a target for your romantic feelings."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.has_soul == 0:
        response = "A soulless juvie can only desperately reach for companionship, they will never find it."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    target = cmd.mentions[0].id
    target2 = None
    if quadrant.id_quadrant == ewcfg.quadrant_policitous and cmd.mentions_count > 1:
        target2 = cmd.mentions[1].id

    quadrant_data = EwQuadrant(id_server=author.guild.id, id_user=author.id, quadrant=quadrant.id_quadrant, id_target=target, id_target2=target2)

    onesided = quadrant_data.check_if_onesided()

    if onesided:
        comment = random.choice(ewcfg.quadrants_comments_onesided)
        resp_add = quadrant.resp_add_onesided

    else:
        comment = random.choice(ewcfg.quadrants_comments_relationship)
        resp_add = quadrant.resp_add_relationship

    if target2 is None:
        resp_add = resp_add.format(cmd.mentions[0].display_name)
    else:
        resp_add = resp_add.format("{} and {}".format(cmd.mentions[0].display_name, cmd.mentions[1].display_name))
    response = "{} {}".format(resp_add, comment)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def clear_quadrant(cmd):
    response = ""
    author = cmd.message.author
    quadrant = None
    user_data = EwUser(id_user=author.id, id_server=author.guild.id)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    for token in cmd.tokens[1:]:
        if token.lower() in quad_static.quadrants_map:
            quadrant = quad_static.quadrants_map[token.lower()]
        if quadrant is not None:
            break

    if quadrant is None:
        response = "Please select a quadrant for your romantic feelings."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    quadrant_data = EwQuadrant(id_server=author.guild.id, id_user=author.id, quadrant=quadrant.id_quadrant)

    if quadrant_data.id_target != -1:
        target_member_data = cmd.guild.get_member(quadrant_data.id_target)
        target_member_data_2 = None

        if quadrant_data.id_target2 != -1:
            target_member_data_2 = cmd.guild.get_member(quadrant_data.id_target)

        quadrant_data = EwQuadrant(id_server=author.guild.id, id_user=author.id, quadrant=quadrant.id_quadrant, id_target=-1, id_target2=-1)
        quadrant_data.persist()

        response = "You break up with {}. Maybe it's for the best...".format(target_member_data.display_name)
        if target_member_data_2 != None:
            response = "You break up with {} and {}. Maybe it's for the best...".format(target_member_data.display_name, target_member_data_2.display_name)

    else:
        response = "You haven't filled out that quadrant, bitch."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def get_quadrants(cmd):
    response = ""
    author = cmd.message.author
    if cmd.mentions_count > 0:
        member = cmd.mentions[0]
    else:
        member = author
    for quadrant in ewcfg.quadrant_ids:
        quadrant_data = EwQuadrant(id_server=cmd.guild.id, id_user=member.id, quadrant=quadrant)
        if quadrant_data.id_target != -1:
            response += "\n"
            response += get_quadrant(cmd, quadrant)

    if response == "":
        response = "{} quadrants are completely empty. " + ewcfg.emote_broken_heart

        if cmd.mentions_count > 0:
            response = response.format("Their")
        else:
            response = response.format("Your")

    user_data = EwUser(id_user=member.id, id_server=member.guild.id)
    if user_data.has_soul == 0:
        response = "{} can't truly form any bonds without {} soul."
        if cmd.mentions_count > 0:
            response = response.format("They", "their")
        else:
            response = response.format("You", "your")

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def get_sloshed(cmd):
    response = get_quadrant(cmd, ewcfg.quadrant_sloshed)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def get_roseate(cmd):
    response = get_quadrant(cmd, ewcfg.quadrant_roseate)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def get_violacious(cmd):
    response = get_quadrant(cmd, ewcfg.quadrant_violacious)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def get_policitous(cmd):
    response = get_quadrant(cmd, ewcfg.quadrant_policitous)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))