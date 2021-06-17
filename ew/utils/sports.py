import asyncio

from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils.frontend import EwResponseContainer

sb_games = {}


async def slimeball_tick_loop(id_server):
    global sb_games
    while not ewutils.TERMINATE:
        await slimeball_tick(id_server)
        await asyncio.sleep(ewcfg.slimeball_tick_length)


async def slimeball_tick(id_server):
    resp_cont = EwResponseContainer(id_server=id_server)

    for id_game in sb_games:
        game = sb_games.get(id_game)
        if game == None:
            continue
        if game.id_server == id_server:
            if len(game.players) > 0:
                for player in game.players:
                    resp_cont.add_response_container(player.move())

                resp_cont.add_response_container(game.move_ball())

            else:
                poi_data = poi_static.id_to_poi.get(game.poi)
                response = "Slimeball game ended with score purple {} : {} pink.".format(game.score_purple, game.score_pink)
                resp_cont.add_channel_response(poi_data.channel, response)

                game.kill()

    await resp_cont.post()
