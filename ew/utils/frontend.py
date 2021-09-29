import asyncio
import sys
import traceback

import discord

from . import core as ewutils
from . import rolemgr as ewrolemgr
from ..backend import core as bknd_core
from ..backend.hunting import EwEnemyBase as EwEnemy
from ..backend.item import EwItem
from ..backend.player import EwPlayer
from ..backend.user import EwUserBase as EwUser
from ..static import cfg as ewcfg
from ..static import hunting as hunt_static
from ..static import poi as poi_static
from ..static import weapons as static_weapons


class Message:
    # Send the message to this exact channel by name.
    channel = None

    # Send the message to the channel associated with this point of interest.
    id_poi = None

    # Should this message echo to adjacent points of interest?
    reverb = None
    message = ""

    def __init__(
            self,
            channel = None,
            reverb = False,
            message = "",
            id_poi = None
    ):
        self.channel = channel
        self.reverb = reverb
        self.message = message
        self.id_poi = id_poi


"""
	Class for storing, passing, editing and posting channel responses and topics
"""


class EwResponseContainer:
    client = None
    id_server = -1
    channel_responses = {}
    channel_topics = {}
    members_to_update = []

    def __init__(self, client = None, id_server = None):
        self.client = client
        self.id_server = id_server
        self.channel_responses = {}
        self.channel_topics = {}
        self.members_to_update = []

    def add_channel_response(self, channel, response):
        if channel in self.channel_responses:
            self.channel_responses[channel].append(response)
        else:
            self.channel_responses[channel] = [response]

    def add_channel_topic(self, channel, topic):
        self.channel_topics[channel] = topic

    def add_member_to_update(self, member):
        for update_member in self.members_to_update:
            if update_member.id == member.id:
                return

        self.members_to_update.append(member)

    def add_response_container(self, resp_cont):
        for ch in resp_cont.channel_responses:
            responses = resp_cont.channel_responses[ch]
            for r in responses:
                self.add_channel_response(ch, r)

        for ch in resp_cont.channel_topics:
            self.add_channel_topic(ch, resp_cont.channel_topics[ch])

        for member in resp_cont.members_to_update:
            self.add_member_to_update(member)

    def format_channel_response(self, channel, member):
        if channel in self.channel_responses:
            for i in range(len(self.channel_responses[channel])):
                self.channel_responses[channel][i] = formatMessage(member, self.channel_responses[channel][i])

    async def post(self, channel = None, delete_after = None):
        self.client = ewutils.get_client()
        messages = []

        if self.client == None:
            ewutils.logMsg("Couldn't find client")
            return messages

        server = self.client.get_guild(int(self.id_server))
        if server == None:
            ewutils.logMsg("Couldn't find server with id {}".format(self.id_server))
            return messages

        for member in self.members_to_update:
            await ewrolemgr.updateRoles(client=self.client, member=member)

        for ch in self.channel_responses:
            if channel == None:
                current_channel = get_channel(server=server, channel_name=ch)
                if current_channel == None:
                    current_channel = ch
            else:
                current_channel = channel
            try:
                response = ""
                while len(self.channel_responses[ch]) > 0:
                    if len(self.channel_responses[ch][0]) > ewcfg.discord_message_length_limit:
                        response += "\n" + self.channel_responses[ch].pop(0)
                        length = len(response)
                        #client, channel, text = None, embed = None, delete_after = None, filter_everyone = True
                        split_list = [(response[i:i + 2000]) for i in range(0, length, 2000)]
                        for blurb in split_list:
                            message = await send_message(client = self.client, channel=current_channel, text = blurb, delete_after=delete_after)
                            messages.append(message)
                        response = ""
                    elif len(response) == 0 or len("{}\n{}".format(response, self.channel_responses[ch][0])) < ewcfg.discord_message_length_limit:
                        response += "\n" + self.channel_responses[ch].pop(0)
                    else:
                        message = await send_message(client = self.client, channel=current_channel, text =response, delete_after=delete_after)
                        messages.append(message)
                        response = ""
                message = await send_message(client = self.client, channel=current_channel, text = response, delete_after=delete_after)
                messages.append(message)
            except:
                ewutils.logMsg('Failed to send message to channel {}: {}'.format(ch, self.channel_responses[ch]))

        # for ch in self.channel_topics:
        # 	channel = get_channel(server = server, channel_name = ch)
        # 	try:
        # 		await channel.edit(topic = self.channel_topics[ch])
        # 	except:
        # 		ewutils.logMsg('Failed to set channel topic for {} to {}'.format(ch, self.channel_topics[ch]))

        return messages


def readMessage(fname):
    msg = Message()

    try:
        f = open(fname, "r")
        f_lines = f.readlines()

        count = 0
        for line in f_lines:
            line = line.rstrip()
            count += 1
            if len(line) == 0:
                break

            args = line.split('=')
            if len(args) == 2:
                field = args[0].strip().lower()
                value = args[1].strip()

                if field == "channel":
                    msg.channel = value.lower()
                elif field == "poi":
                    msg.poi = value.lower()
                elif field == "reverb":
                    msg.reverb = True if (value.lower() == "true") else False
            else:
                count -= 1
                break

        for line in f_lines[count:]:
            msg.message += (line.rstrip() + "\n")
    except:
        ewutils.logMsg('failed to parse message.')
        traceback.print_exc(file=sys.stdout)
    finally:
        f.close()

    return msg


""" format responses with the username: """


def formatMessage(user_target, message):
    # If the display name belongs to an unactivated raid boss, hide its name while it's counting down.

    try:
        if user_target.life_state == ewcfg.enemy_lifestate_alive:

            if user_target.enemyclass == ewcfg.enemy_class_gaiaslimeoid:
                return "**{} ({}):** {}".format(user_target.display_name, user_target.gvs_coord, message)
            else:
                # Send messages for normal enemies, and allow mentioning with @
                if user_target.identifier != '' and user_target.enemyclass == ewcfg.enemy_class_shambler:
                    return "**{} [{}] ({}):** {}".format(user_target.display_name, user_target.identifier, user_target.gvs_coord, message)
                elif user_target.identifier != '':
                    return "*{} [{}]* {}".format(user_target.display_name, user_target.identifier, message)
                else:
                    return "*{}:* {}".format(user_target.display_name, message)


        elif user_target.display_name in ewcfg.raid_boss_names and user_target.life_state == ewcfg.enemy_lifestate_unactivated:
            return "{}".format(message)

    # If user_target isn't an enemy, catch the exception.
    except:
        if hasattr(user_target, "id_user") and hasattr(user_target, "id_server"):
            user_obj = EwUser(id_server=user_target.id_server, id_user=user_target.id_user)
        else:
            user_obj = EwUser(member=user_target)
        mutations = user_obj.get_mutations()
        if ewcfg.mutation_id_amnesia in mutations:
            display_name = '?????'
        else:
            display_name = user_target.display_name

        return "*{}:* {}".format(display_name, message).replace("{", "\{").replace("@", "{at}")


"""
	Send a message to multiple chat channels at once. "channels" can be either a list of discord channel objects or strings
"""


async def post_in_channels(id_server, message, channels = None):
    client = ewutils.get_client()
    server = client.get_guild(id=id_server)

    if channels is None and server is not None:
        channels = server.channels

    for channel in channels:
        if type(channel) is str:  # if the channels are passed as strings instead of discord channel objects
            channel = get_channel(server, channel)
        if channel is not None and channel.type == discord.ChannelType.text:
            await channel.send(content=message)
    return


"""
	Find a chat channel by name in a server.
"""


def get_channel(server = None, channel_name = ""):
    channel = None

    for chan in server.channels:
        if chan.name == channel_name:
            channel = chan

    if channel == None and not ewutils.DEBUG:
        ewutils.logMsg('Error: In get_channel(), could not find channel using channel_name "{}"'.format(channel_name))

    return channel


"""
	Returns an EwUser object of the selected kingpin
"""


def find_kingpin(id_server, kingpin_role):
    data = bknd_core.execute_sql_query("SELECT id_user FROM users WHERE id_server = %s AND {life_state} = %s AND {faction} = %s".format(
        life_state=ewcfg.col_life_state,
        faction=ewcfg.col_faction
    ), (
        id_server,
        ewcfg.life_state_kingpin,
        ewcfg.faction_rowdys if kingpin_role == ewcfg.role_rowdyfucker else ewcfg.faction_killers
    ))

    kingpin = None

    if len(data) > 0:
        id_kingpin = data[0][0]
        kingpin = EwUser(id_server=id_server, id_user=id_kingpin)

    return kingpin


"""
	Posts a message both in CK and RR.
"""


async def post_in_hideouts(id_server, message):
    await post_in_channels(
        id_server=id_server,
        message=message,
        channels=[ewcfg.channel_copkilltown, ewcfg.channel_rowdyroughhouse]
    )


"""
	Proxy to discord.py channel.send with exception handling.
"""


async def send_message(client, channel, text = None, embed = None, delete_after = None, filter_everyone = True):
    # catch any future @everyone exploits
    if filter_everyone and text is not None:
        text = text.replace("@everyone", "{at}everyone")

    try:
        if text is not None:
            return await channel.send(content=text, delete_after=delete_after)
        if embed is not None:
            return await channel.send(embed=embed)
    except discord.errors.Forbidden:
        ewutils.logMsg('Could not message user: {}\n{}'.format(channel, text))
        raise
    except:
        ewutils.logMsg('Failed to send message to channel: {}\n{}'.format(channel, text))


""" Simpler to use version of send_message that formats message by default """


async def send_response(response_text, cmd = None, delete_after = None, name = None, channel = None, format_name = True, format_ats = True, allow_everyone = False):
    user_data = EwUser(member=cmd.message.author)
    user_mutations = user_data.get_mutations()

    if cmd == None and channel == None:
        raise Exception("No channel to send message to")

    if channel == None:
        channel = cmd.message.channel

    if name == None and cmd != None:
        name = cmd.author_id.display_name
        if ewcfg.mutation_id_amnesia in user_mutations:
            name = '?????'

    if format_name and name != None:
        response_text = "*{}:* {}".format(name, response_text)

    if ewutils.DEBUG:  # to see when the bot uses send_response vs send_message in --debug mode
        response_text = "--{}".format(response_text)

    if format_ats:
        response_text = response_text.replace("@", "{at}")

    allowed_mentions = discord.AllowedMentions(everyone=allow_everyone, users=False, roles=False)

    try:
        # TODO: experiment with allow_mentions argument. Might get rid of the need to filter "@"s
        return await channel.send(content=response_text, delete_after=delete_after, allowed_mentions=allowed_mentions)
    except discord.errors.Forbidden:
        ewutils.logMsg('Could not message user: {}\n{}'.format(channel, response_text))
        raise
    except:
        ewutils.logMsg('Failed to send message to channel: {}\n{}'.format(channel, response_text))


"""
	Proxy to discord.py message.edit() with exception handling.
"""


async def edit_message(client, message, text):
    try:
        return await message.edit(content=str(text))
    except:
        ewutils.logMsg('Failed to edit message. Updated text would have been:\n{}'.format(text))


async def delete_last_message(client, last_messages, tick_length):
    if len(last_messages) == 0:
        return
    await asyncio.sleep(tick_length)
    try:
        msg = last_messages[-1]
        await msg.delete()
        pass
    except:
        ewutils.logMsg("failed to delete last message")


def create_death_report(cause = None, user_data = None):
    client = ewutils.get_client()
    server = client.get_guild(user_data.id_server)

    # User display name is used repeatedly later, grab now
    user_member = server.get_member(user_data.id_user)
    user_player = EwPlayer(id_user=user_data.id_user)
    user_nick = user_player.display_name

    deathreport = "You arrive among the dead. {}".format(ewcfg.emote_slimeskull)
    deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

    report_requires_killer = [ewcfg.cause_killing, ewcfg.cause_busted, ewcfg.cause_burning, ewcfg.cause_killing_enemy]
    if (cause in report_requires_killer):  # Only deal with enemy data if necessary
        killer_isUser = cause in [ewcfg.cause_killing, ewcfg.cause_busted, ewcfg.cause_burning]
        killer_isEnemy = cause in [ewcfg.cause_killing_enemy]
        if (killer_isUser):  # Generate responses for dying to another player
            # Grab user data
            killer_data = EwUser(id_user=user_data.id_killer, id_server=user_data.id_server)
            player_data = EwPlayer(id_user=user_data.id_killer)

            # Get killer weapon
            weapon_item = EwItem(id_item=killer_data.weapon)
            weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))

            killer_nick = player_data.display_name

            if (cause == ewcfg.cause_killing) and (weapon != None):  # Response for dying to another player
                deathreport = "You were {} by {}. {}".format(weapon.str_killdescriptor, killer_nick, ewcfg.emote_slimeskull)
                deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

            if (cause == ewcfg.cause_busted):  # Response for being busted
                deathreport = "Your ghost has been busted by {}. {}".format(killer_nick, ewcfg.emote_bustin)
                deathreport = "{} ".format(ewcfg.emote_bustin) + formatMessage(user_player, deathreport)

            if (cause == ewcfg.cause_burning):  # Response for burning to death
                deathreport = "You were {} by {}. {}".format(static_weapons.weapon_map.get(ewcfg.weapon_id_molotov).str_killdescriptor, killer_nick, ewcfg.emote_slimeskull)
                deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

        if (killer_isEnemy):  # Generate responses for being killed by enemy
            # Grab enemy data
            killer_data = EwEnemy(id_enemy=user_data.id_killer, id_server=user_data.id_server)

            if killer_data.attacktype != ewcfg.enemy_attacktype_unarmed:
                used_attacktype = hunt_static.attack_type_map.get(killer_data.attacktype)
            else:
                used_attacktype = ewcfg.enemy_attacktype_unarmed
            if (cause == ewcfg.cause_killing_enemy):  # Response for dying to enemy attack
                # Get attack kill description
                kill_descriptor = "beaten to death"
                if used_attacktype != ewcfg.enemy_attacktype_unarmed:
                    kill_descriptor = used_attacktype.str_killdescriptor

                # Format report
                deathreport = "You were {} by {}. {}".format(kill_descriptor, killer_data.display_name, ewcfg.emote_slimeskull)
                deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

    if (cause == ewcfg.cause_donation):  # Response for overdonation
        deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, "You have died in a medical mishap. {}".format(ewcfg.emote_slimeskull))

    if (cause == ewcfg.cause_suicide):  # Response for !suicide
        deathreport = "You arrive among the dead by your own volition. {}".format(ewcfg.emote_slimeskull)
        deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

    if (cause == ewcfg.cause_drowning):  # Response for disembarking into the slime sea
        deathreport = "You have drowned in the slime sea. {}".format(ewcfg.emote_slimeskull)
        deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

    if (cause == ewcfg.cause_falling):  # Response for disembarking blimp over the city
        deathreport = "You have fallen to your death. {}".format(ewcfg.emote_slimeskull)
        deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

    if (cause == ewcfg.cause_bleeding):  # Response for bleed death
        deathreport = "{skull} *{uname}*: You have succumbed to your wounds. {skull}".format(skull=ewcfg.emote_slimeskull, uname=user_nick)

    if (cause == ewcfg.cause_weather):  # Response for death by bicarbonate rain
        deathreport = "{skull} *{uname}*: You have been cleansed by the bicarbonate rain. {skull}".format(skull=ewcfg.emote_slimeskull, uname=user_nick)

    if (cause == ewcfg.cause_cliff):  # Response for falling or being pushed off cliff
        deathreport = "You fell off a cliff. {}".format(ewcfg.emote_slimeskull)
        deathreport = "{} ".format(ewcfg.emote_slimeskull) + formatMessage(user_player, deathreport)

    if (cause == ewcfg.cause_backfire):  # Response for death by self backfire
        weapon_item = EwItem(id_item=user_data.weapon)
        weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
        deathreport = "{} killed themselves with their own {}. Dumbass.".format(user_nick, weapon.str_name)

    if (cause == ewcfg.cause_praying):  # Response for praying
        deathreport = formatMessage(user_member, "{} owww yer frickin bones man {}".format(ewcfg.emote_slimeskull, ewcfg.emote_slimeskull))

    return (deathreport)


async def update_slimernalia_kingpin(client, server):
    # Depose current slimernalia kingpin
    old_kingpin_id = ewutils.get_slimernalia_kingpin(server)
    if old_kingpin_id != None:
        old_kingpin = EwUser(id_user=old_kingpin_id, id_server=server.id)
        old_kingpin.slimernalia_kingpin = False
        old_kingpin.persist()
        try:
            old_kingpin_member = server.get_member(old_kingpin.id_user)
            await ewrolemgr.updateRoles(client=client, member=old_kingpin_member)
        except:
            ewutils.logMsg("Error removing kingpin of slimernalia role from {} in server {}.".format(old_kingpin.id_user, server.id))

    # Update the new kingpin of slimernalia
    new_kingpin = EwUser(id_user=ewutils.get_most_festive(server), id_server=server.id)
    new_kingpin.slimernalia_kingpin = True
    new_kingpin.persist()
    try:
        new_kingpin_member = server.get_member(new_kingpin.id_user)
        await ewrolemgr.updateRoles(client=client, member=new_kingpin_member)
    except:
        ewutils.logMsg("Error adding kingpin of slimernalia role to user {} in server {}.".format(new_kingpin.id_user, server.id))


def check_user_has_role(server, member, checked_role_name):
    checked_role = discord.utils.get(server.roles, name=checked_role_name)
    if checked_role not in member.roles:
        return False
    else:
        return True


def return_server_role(server, role_name):
    return discord.utils.get(server.roles, name=role_name)


""" add the PvP flag role to a member """


async def add_pvp_role(cmd = None):
    member = cmd.message.author
    roles_map_user = ewutils.getRoleMap(member.roles)

    if ewcfg.role_copkillers in roles_map_user and ewcfg.role_copkillers_pvp not in roles_map_user:
        await member.add_roles(cmd.roles_map[ewcfg.role_copkillers_pvp])
    elif ewcfg.role_rowdyfuckers in roles_map_user and ewcfg.role_rowdyfuckers_pvp not in roles_map_user:
        await member.add_roles(cmd.roles_map[ewcfg.role_rowdyfuckers_pvp])
    elif ewcfg.role_juvenile in roles_map_user and ewcfg.role_juvenile_pvp not in roles_map_user:
        await member.add_roles(cmd.roles_map[ewcfg.role_juvenile_pvp])


async def collect_topics(cmd):
    if not cmd.message.author.guild_permissions.administrator:
        return

    client = ewutils.get_client()
    server = client.get_guild(cmd.guild.id)
    topic_count = 0

    for channel in server.channels:

        if channel.type != discord.ChannelType.text:
            continue
        elif channel.topic == None or channel.topic == '':
            continue
        elif channel.topic == '(Closed indefinitely) Currently controlled by no one.':
            continue

        found_poi = False
        for poi in poi_static.poi_list:
            if channel.name == poi.channel:
                found_poi = True
                break

        if found_poi:
            topic_count += 1
            print('\n{}\n=================\n{}'.format(channel.name, channel.topic))

    print('POI topics found: {}'.format(topic_count))


async def sync_topics(cmd):
    if not cmd.message.author.guild_permissions.administrator:
        return

    for poi in poi_static.poi_list:

        poi_has_blank_topic = False
        if poi.topic == None or poi.topic == '':
            poi_has_blank_topic = True

        channel = get_channel(cmd.guild, poi.channel)

        if channel == None:
            ewutils.logMsg('Failed to get channel for {}'.format(poi.id_poi))
            continue

        if channel.topic == poi.topic:
            continue

        if (poi_has_blank_topic and channel.topic == None) or (poi_has_blank_topic and channel.topic == ''):
            continue

        if poi_has_blank_topic:
            new_topic = ''
            debug_info = 'be a blank topic.'
        else:
            new_topic = poi.topic
            debug_info = poi.topic

        try:
            await asyncio.sleep(2)
            await channel.edit(topic=new_topic)
            ewutils.logMsg('Changed channel topic for {} to {}'.format(channel, debug_info))
        except:
            ewutils.logMsg('Failed to set channel topic for {} to {}'.format(channel, debug_info))

    ewutils.logMsg('Finished syncing topics.')
