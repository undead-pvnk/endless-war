from ew.static import cfg as ewcfg
from ew.utils import frontend as fe_utils


# Returns a user's life state/gang color as a discord.Colour object
def get_tweet_color(user_data):
    if user_data.life_state < 2:
        color = ewcfg.tweet_color_by_lifestate.get(user_data.life_state)
    else:
        color = ewcfg.tweet_color_by_faction.get(user_data.faction)

    if color is None:
        color = fe_utils.discord.Embed.Empty
    else:
        color = fe_utils.discord.Colour(int(color, 16))

    return color
