import asyncio
import random

from ew.static import poi as poi_static
from ew.utils import dungeons as dungeon_utils
from ew.utils import frontend as fe_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser
from . import utils


async def tutorial_cmd(cmd):
    user_data = EwUser(member=cmd.message.author)
    client = cmd.client

    if user_data.poi not in poi_static.tutorial_pois:
        return

    if user_data.id_user not in utils.user_to_tutorial_state:
        return await dungeon_utils.begin_tutorial(cmd.message.author)

    tutorial_state = utils.user_to_tutorial_state.get(user_data.id_user)

    tutorial_scene = poi_static.dungeon_tutorial[tutorial_state]

    cmd_content = cmd.message.content[1:].lower()

    # Administrators can skip the tutorial
    if cmd_content == "skiptutorial" and cmd.message.author.guild_permissions.administrator:
        new_state = 20
        utils.user_to_tutorial_state[user_data.id_user] = new_state

        scene = poi_static.dungeon_tutorial[new_state]

        if scene.poi != None:
            user_data.poi = scene.poi

        if scene.life_state != None:
            user_data.life_state = scene.life_state

        user_data.persist()

        await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

        response = dungeon_utils.format_tutorial_response(scene)

        poi_def = poi_static.id_to_poi.get(user_data.poi)
        channels = [poi_def.channel]
        return await fe_utils.post_in_channels(cmd.guild.id, fe_utils.formatMessage(cmd.message.author, response), channels)

    if cmd_content in tutorial_scene.options:
        new_state = tutorial_scene.options.get(cmd_content)
        utils.user_to_tutorial_state[user_data.id_user] = new_state

        scene = poi_static.dungeon_tutorial[new_state]

        if scene.poi != None:
            user_data.poi = scene.poi

        if scene.life_state != None:
            user_data.life_state = scene.life_state

        user_data.persist()

        await ewrolemgr.updateRoles(client=cmd.client, member=cmd.message.author)

        response = dungeon_utils.format_tutorial_response(scene)

        poi_def = poi_static.id_to_poi.get(user_data.poi)
        channels = [poi_def.channel]
        return await fe_utils.post_in_channels(cmd.guild.id, fe_utils.formatMessage(cmd.message.author, response), channels)


    else:
        """ couldn't process the command. bail out!! """
        """ bot rule 0: be cute """
        randint = random.randint(1, 3)
        msg_mistake = "ENDLESS WAR is growing frustrated."
        if randint == 2:
            msg_mistake = "ENDLESS WAR denies you his favor."
        elif randint == 3:
            msg_mistake = "ENDLESS WAR pays you no mind."

        msg = await fe_utils.send_message(client, cmd.message.channel, msg_mistake)
        await asyncio.sleep(2)
        try:
            await msg.delete()
            pass
        except:
            pass

        # response = dungeon_utils.format_tutorial_response(tutorial_scene)
        # return await fe_utils.send_message(client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        return
