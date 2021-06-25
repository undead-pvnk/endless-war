from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser

# maps users to where they are in the tutorial
user_to_tutorial_state = {}


def format_tutorial_response(scene):
    response = scene.text
    if scene.dungeon_state:
        response += "\n\nWhat do you do?\n\n**>options: "
        options = []
        for path in scene.options.keys():
            options.append("{}{}".format(ewcfg.cmd_prefix, path))
        response += ewutils.formatNiceList(names=options, conjunction="or")
        response += "**"

    return response


async def begin_tutorial(member):
    user_data = EwUser(member=member)
    user_to_tutorial_state[user_data.id_user] = 0

    scene = poi_static.dungeon_tutorial[0]

    if scene.poi != None:
        user_data.poi = scene.poi
    if scene.life_state != None:
        user_data.life_state = scene.life_state

    user_data.persist()

    await ewrolemgr.updateRoles(client=ewutils.get_client(), member=member)

    response = format_tutorial_response(scene)
    poi_def = poi_static.id_to_poi.get(user_data.poi)
    channels = [poi_def.channel]
    return await fe_utils.post_in_channels(member.guild.id, fe_utils.formatMessage(member, response), channels)
