import ewcfg
import ewutils
from ew import EwUser

# Returns a user's life state/gang color as a discord.Colour object
def get_tweet_color(user_data):
    if user_data.life_state < 2:
        color = ewcfg.tweet_color_by_lifestate.get(user_data.life_state)
    else:
        color = ewcfg.tweet_color_by_faction.get(user_data.faction)

    if color is None:   
        color = ewutils.discord.Embed.Empty
    else:
        color = ewutils.discord.Colour(int(color, 16))

    return color

async def tweet(cmd):
    
    user_data = EwUser(id_user=cmd.message.author.id, id_server=cmd.guild.id)
    
    if user_data.has_gellphone():

        if cmd.tokens_count < 2:
            response = "Tweet what?"
            return await ewutils.send_response(response, cmd)

        tweet_content = ' '.join("`{}`".format(token) if token.startswith("#") else token for token in cmd.tokens[1:])
        # embed limits
        if len(tweet_content) > 280:
            response = "Alright there bud, slow down a bit. No one's gonna read all that ({}/280).".format(len(tweet_content))
            return await ewutils.send_response(response, cmd)

        tweet = ewutils.discord.Embed()

        tweet.set_thumbnail(url = cmd.message.author.avatar_url)
        # we use the description to set the author since members cannot be mentioned from the author field
        tweet.description="<@!{}>".format(cmd.message.author.id)
        tweet.color = get_tweet_color(user_data)

        # \u200b is a whitespace character, since we cannot leave field names empty
        tweet.add_field(name='\u200b', value = tweet_content)

        # works as long as the first attachment is an image
        # other file types are ignored
        if len(cmd.message.attachments) > 0:
            tweet.set_image(url=cmd.message.attachments[0].url)

        channel = ewutils.get_channel(server=cmd.guild, channel_name=ewcfg.channel_slimetwitter)

        await ewutils.send_message(cmd.client, channel, embed=tweet)

    else:
        response = "You need to have a gellphone to !tweet."
        return await ewutils.send_response(response, cmd)