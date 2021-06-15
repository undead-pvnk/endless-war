import time

from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import frontend as fe_utils
from ew.utils import hunting as hunt_utils
from ew.utils.combat import EwUser

# Debug command. Could be used for events, perhaps?
async def summonenemy(cmd):
    author = cmd.message.author

    if not author.guild_permissions.administrator:
        return

    time_now = int(time.time())
    response = ""
    user_data = EwUser(member=cmd.message.author)
    data_level = 0

    enemytype = None
    enemy_location = None
    enemy_coord = None
    poi = None
    enemy_slimes = None
    enemy_displayname = None
    enemy_level = None

    resp_cont = None

    if len(cmd.tokens) >= 3:

        enemytype = cmd.tokens[1]
        enemy_location = cmd.tokens[2]

        if len(cmd.tokens) >= 6:
            enemy_slimes = cmd.tokens[3]
            enemy_level = cmd.tokens[4]
            enemy_coord = cmd.tokens[5]
            enemy_displayname = " ".join(cmd.tokens[6:])

        poi = poi_static.id_to_poi.get(enemy_location)

    if enemytype != None and poi != None:

        data_level = 1

        if enemy_slimes != None and enemy_displayname != None and enemy_level != None and enemy_coord != None:
            data_level = 2

        if data_level == 1:
            resp_cont = hunt_utils.spawn_enemy(id_server=cmd.message.guild.id, pre_chosen_type=enemytype, pre_chosen_poi=poi.id_poi, manual_spawn=True)
        elif data_level == 2:

            resp_cont = hunt_utils.spawn_enemy(
                id_server=cmd.message.guild.id,
                pre_chosen_type=enemytype,
                pre_chosen_poi=poi.id_poi,
                pre_chosen_level=enemy_level,
                pre_chosen_slimes=enemy_slimes,
                pre_chosen_initialslimes=enemy_slimes,
                pre_chosen_coord=enemy_coord,
                pre_chosen_displayname=enemy_displayname,
                pre_chosen_weather=ewcfg.enemy_weathertype_normal,
                manual_spawn=True,
            )

        await resp_cont.post()

    else:
        response = "**DEBUG**: PLEASE RE-SUMMON WITH APPLICABLE TYPING / LOCATION. ADDITIONAL OPTIONS ARE SLIME / LEVEL / COORD / DISPLAYNAME"
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def summongvsenemy(cmd):
    author = cmd.message.author

    if not author.guild_permissions.administrator:
        return

    time_now = int(time.time())
    response = ""
    user_data = EwUser(member=cmd.message.author)

    poi = None
    enemytype = None
    coord = None
    joybean_status = None

    if cmd.tokens_count == 4:
        enemytype = cmd.tokens[1]
        coord = cmd.tokens[2]
        joybean_status = cmd.tokens[3]
        poi = poi_static.id_to_poi.get(user_data.poi)
    else:
        response = "Correct usage: !summongvsenemy [type] [coord] [joybean status ('yes', otherwise false)]"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if enemytype != None and poi != None and joybean_status != None and coord != None:
        props = None
        try:
            props = ewcfg.enemy_data_table[enemytype]["props"]

            if joybean_status.lower() == 'yes':
                props['joybean'] = 'true'

        except:
            pass

        resp_cont = hunt_utils.spawn_enemy(
            id_server=cmd.message.guild.id,
            pre_chosen_type=enemytype,
            pre_chosen_poi=poi.id_poi,
            pre_chosen_coord=coord.upper(),
            pre_chosen_props=props,
            pre_chosen_weather=ewcfg.enemy_weathertype_normal,
            manual_spawn=True,
        )

        await resp_cont.post()