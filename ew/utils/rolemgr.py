import asyncio
import time

import discord

from . import core as ewutils
from . import frontend as fe_utils
from ..backend.role import EwRole
from ..backend.user import EwUserBase as EwUser
from ..static import cfg as ewcfg
from ..static import poi as poi_static

"""
	Find relevant roles and save them to the database.
"""


def setupRoles(client = None, id_server = -1):
    roles_map = ewutils.getRoleMap(client.get_guild(id_server).roles)
    for poi in poi_static.poi_list:
        if poi.role in roles_map:
            try:
                role_data = EwRole(id_server=id_server, name=poi.role)
                role_data.id_role = roles_map[poi.role].id
                role_data.persist()
            except:
                ewutils.logMsg('Failed to set up role {}'.format(poi.role))

        if poi.major_role in roles_map:
            try:
                role_data = EwRole(id_server=id_server, name=poi.major_role)
                role_data.id_role = roles_map[poi.major_role].id
                role_data.persist()
            except:
                ewutils.logMsg('Failed to set up major role {}'.format(poi.major_role))

        if poi.minor_role in roles_map:
            try:
                role_data = EwRole(id_server=id_server, name=poi.minor_role)
                role_data.id_role = roles_map[poi.minor_role].id
                role_data.persist()
            except:
                ewutils.logMsg('Failed to set up minor role {}'.format(poi.minor_role))

    for faction_role in ewcfg.faction_roles:
        if faction_role in roles_map:
            try:
                role_data = EwRole(id_server=id_server, name=faction_role)
                role_data.id_role = roles_map[faction_role].id
                role_data.persist()
            except:
                ewutils.logMsg('Failed to set up role {}'.format(faction_role))

    for misc_role in ewcfg.misc_roles:
        if misc_role in roles_map:
            try:
                role_data = EwRole(id_server=id_server, name=misc_role)
                role_data.id_role = roles_map[misc_role].id
                role_data.persist()
            except:
                ewutils.logMsg('Failed to set up role {}'.format(misc_role))


"""
	Hide the names of poi roles behind a uniform alias
"""


async def hideRoleNames(cmd):
    id_server = cmd.guild.id
    client = ewutils.get_client()

    server = client.get_guild(id_server)
    roles_map = ewutils.getRoleMap(server.roles)

    role_counter = 0

    ewutils.logMsg('Attempting to hide all role names...')

    for poi in poi_static.poi_list:

        if poi.is_street:
            pass
        elif poi.is_district:
            pass
        elif poi.id_poi in [ewcfg.poi_id_mine, ewcfg.poi_id_cv_mines, ewcfg.poi_id_tt_mines]:
            pass
        else:
            continue

        # Slow down just a bit every 20 Role change attempts
        if role_counter >= 20:
            role_counter = 0
            await asyncio.sleep(5)

        try:
            if poi.role in roles_map:
                role = roles_map[poi.role]
                if role.name != ewcfg.generic_role_name:
                    role_counter += 1
                    await role.edit(name=ewcfg.generic_role_name)
        except:
            ewutils.logMsg('Failed to hide role name for {}'.format(poi.role))

        try:
            if poi.major_role in roles_map:
                major_role = roles_map[poi.major_role]
                if major_role.name != ewcfg.generic_role_name:
                    role_counter += 1
                    await major_role.edit(name=ewcfg.generic_role_name)
        except:
            ewutils.logMsg('Failed to hide role name for {}'.format(poi.major_role))

        try:
            if poi.minor_role in roles_map:
                minor_role = roles_map[poi.minor_role]
                if minor_role.name != ewcfg.generic_role_name:
                    role_counter += 1
                    await minor_role.edit(name=ewcfg.generic_role_name)
        except:
            ewutils.logMsg('Failed to hide role name for {}'.format(poi.minor_role))

    ewutils.logMsg('Finished hiding roles!')



"""
	Restore poi roles to their original names
"""


async def restoreRoleNames(cmd):
    member = cmd.message.author

    if not member.guild_permissions.administrator:
        return

    client = cmd.client
    server = member.guild

    role_counter = 0

    ewutils.logMsg('Attempting to restore all role names...')

    for poi in poi_static.poi_list:

        # Slow down just a bit every 20 Role change attempts
        if role_counter >= 20:
            role_counter = 0
            await asyncio.sleep(5)

        try:
            role_data = EwRole(id_server=server.id, name=poi.role)
            for role in server.roles:
                if role.id == int(role_data.id_role):
                    role_counter += 1
                    await role.edit(name=role_data.name)
        except:
            ewutils.logMsg('Failed to restore role name for {}'.format(poi.role))

        try:
            major_role_data = EwRole(id_server=server.id, name=poi.major_role)
            for role in server.roles:
                if role.id == int(major_role_data.id_role):
                    role_counter += 1
                    await role.edit(name=major_role_data.name)
        except:
            ewutils.logMsg('Failed to restore role name for {}'.format(poi.major_role))

        try:
            minor_role_data = EwRole(id_server=server.id, name=poi.minor_role)
            for role in server.roles:
                if role.id == int(minor_role_data.id_role):
                    role_counter += 1
                    await role.edit(name=minor_role_data.name)
        except:
            ewutils.logMsg('Failed to restore role name for {}'.format(poi.minor_role))

    ewutils.logMsg('Finished restoring roles!')


"""
	Creates all POI roles from scratch. Ideally, this is only used in test servers.
"""


async def recreateRoles(cmd):
    member = cmd.message.author

    if not member.guild_permissions.administrator:
        return

    client = cmd.client
    server = client.get_guild(cmd.guild.id)

    server_role_names = []

    for role in server.roles:
        server_role_names.append(role.name)

    # print(server_role_names)
    roles_created = 0

    for poi in poi_static.poi_list:

        # if poi.role != None:
        #
        # 	if poi.role not in server_role_names:
        # 		await server.create_role(name=poi.role)
        # 		ewutils.logMsg('created role {} for poi {}'.format(poi.role, poi.id_poi))
        #
        # 		roles_created += 1

        if poi.major_role != None and poi.major_role != ewcfg.role_null_major_role:

            if poi.major_role not in server_role_names:

                if poi.is_district:
                    # print(poi.major_role)
                    await server.create_role(name=poi.major_role)
                    ewutils.logMsg('created major role {} for poi {}'.format(poi.major_role, poi.id_poi))

                    roles_created += 1

        if poi.minor_role != None and poi.minor_role != ewcfg.role_null_minor_role:

            if poi.minor_role not in server_role_names:

                if poi.is_district or poi.is_street:
                    await server.create_role(name=poi.minor_role)
                    ewutils.logMsg('created minor role {} for poi {}'.format(poi.minor_role, poi.id_poi))

                    roles_created += 1

    print('{} roles were created in recreateRoles.'.format(roles_created))


"""
	Deletes all POI roles of a desired type. Ideally, this is only used in test servers.
"""


async def deleteRoles(cmd):
    member = cmd.message.author

    if not member.guild_permissions.administrator:
        return

    client = cmd.client
    server = client.get_guild(cmd.guild.id)

    delete_target = ""

    if cmd.tokens_count > 1:
        if cmd.tokens[1].lower() == 'roles':
            delete_target = 'roles'
        elif cmd.tokens[1].lower() == 'minorroles':
            delete_target = 'minorroles'
        elif cmd.tokens[1].lower() == 'majorroles':
            delete_target = 'majorroles'
        elif cmd.tokens[1].lower() == 'hiddrenroles':
            delete_target = 'hiddenroles'
        else:
            return
    else:
        return

    roles_map = ewutils.getRoleMap(server.roles)

    server_role_names = []

    for role in server.roles:
        server_role_names.append(role.name)

    roles_deleted = 0

    if delete_target == 'roles':
        for poi in poi_static.poi_list:
            if poi.role in server_role_names:
                await roles_map[poi.role].delete()
                roles_deleted += 1

    elif delete_target == 'majorroles':
        for poi in poi_static.poi_list:
            if poi.is_district:
                if poi.major_role in server_role_names:
                    await roles_map[poi.major_role].delete()
                    roles_deleted += 1

    elif delete_target == 'minorroles':
        for poi in poi_static.poi_list:
            if poi.is_district or poi.is_street:
                if poi.minor_role in server_role_names:
                    await roles_map[poi.minor_role].delete()
                    roles_deleted += 1

    elif delete_target == 'hiddenroles':
        for generic_role in server.roles:
            if generic_role.name == ewcfg.generic_role_name:
                await generic_role.delete()
                roles_deleted += 1

    print('{} roles were deleted in deleteRoles.'.format(roles_deleted))


"""
	Fix the Discord roles assigned to this member.
"""


async def updateRoles(
        client = None,
        member = None,
        server_default = None,
        refresh_perms = True,
        remove_or_apply_flag = None
):
    time_now = int(time.time())

    if server_default != None:
        user_data = EwUser(id_user=member.id, id_server=server_default)
    else:
        user_data = EwUser(member=member)

    id_server = user_data.id_server

    if member == None:
        return ewutils.logMsg("error: member was not supplied for updateRoles")

    # roles_map = ewutils.getRoleMap(member.guild.roles)
    roles_map_user = ewutils.getRoleIdMap(member.roles)

    user_poi = poi_static.id_to_poi.get(user_data.poi)

    if user_data.life_state != ewcfg.life_state_kingpin and ewcfg.role_kingpin in roles_map_user:
        # Fix the life_state of kingpins, if somehow it wasn't set.
        user_data.life_state = ewcfg.life_state_kingpin
        user_data.persist()

    elif user_data.life_state != ewcfg.life_state_grandfoe and ewcfg.role_grandfoe in roles_map_user:
        # Fix the life_state of a grand foe.
        user_data.life_state = ewcfg.life_state_grandfoe
        user_data.persist()

    faction_roles_remove = [
        ewcfg.role_juvenile,
        ewcfg.role_juvenile_active,
        ewcfg.role_juvenile_pvp,
        ewcfg.role_rowdyfuckers,
        ewcfg.role_rowdyfuckers_pvp,
        ewcfg.role_rowdyfuckers_active,
        ewcfg.role_slimecorp,
        ewcfg.role_slimecorp_pvp,
        ewcfg.role_slimecorp_active,
        ewcfg.role_copkillers,
        ewcfg.role_copkillers_pvp,
        ewcfg.role_copkillers_active,
        ewcfg.role_corpse,
        ewcfg.role_corpse_pvp,
        ewcfg.role_corpse_active,
        ewcfg.role_kingpin,
        ewcfg.role_grandfoe,
        ewcfg.role_executive,
        ewcfg.role_tutorial,
        ewcfg.role_shambler,
    ]

    # Manage faction roles.
    faction_role = ewutils.get_faction(user_data=user_data)

    faction_roles_remove.remove(faction_role)

    non_wanted_pois = [
        ewcfg.poi_id_copkilltown,
        ewcfg.poi_id_rowdyroughhouse,
        ewcfg.poi_id_juviesrow,
        ewcfg.poi_id_thebreakroom,
        ewcfg.poi_id_mine,
        ewcfg.poi_id_mine_bubble,
        ewcfg.poi_id_mine_sweeper,
        ewcfg.poi_id_juviesrow_pier,
        ewcfg.poi_id_jr_farms
    ]

    pvp_role = None
    active_role = None
    #  If faction has an associated PVP role
    if faction_role in ewcfg.role_to_pvp_role:

        if not user_poi.is_apartment and \
                user_poi.id_poi not in non_wanted_pois:  # and \
            # (user_data.life_state != ewcfg.life_state_juvenile or user_data.slimelevel > ewcfg.max_safe_level):
            pvp_role = ewcfg.role_to_pvp_role.get(faction_role)
            faction_roles_remove.remove(pvp_role)

    # if ewutils.is_otp(user_data):
    # 	active_role = ewcfg.role_to_active_role.get(faction_role)
    # 	faction_roles_remove.remove(active_role)

    tutorial_role = None
    if user_data.poi in poi_static.tutorial_pois:
        tutorial_role = ewcfg.role_tutorial
        faction_roles_remove.remove(tutorial_role)

    # Manage location roles.
    if user_poi != None:
        # poi_role = user_poi.role
        poi_major_role = user_poi.major_role
        poi_minor_role = user_poi.minor_role
        poi_permissions = user_poi.permissions
    else:
        # poi_role = None
        poi_major_role = None
        poi_minor_role = None
        poi_permissions = None

    poi_permissions_remove = []
    for poi in poi_static.poi_list:
        if poi.permissions != None and poi.permissions != poi_permissions:
            poi_permissions_remove.append(poi.id_poi)

    poi_roles_remove = []
    for poi in poi_static.poi_list:
        if poi.major_role != None and poi.major_role != poi_major_role:
            poi_roles_remove.append(poi.major_role)
        # if poi.minor_role != None and poi.minor_role != poi_minor_role:
        poi_roles_remove.append(poi.minor_role)

    misc_roles_remove = [
        ewcfg.role_gellphone,
        ewcfg.role_slimernalia
    ]

    # Remove user's gellphone role if they don't have a phone
    role_gellphone = None

    if user_data.has_gellphone():
        role_gellphone = ewcfg.role_gellphone
        misc_roles_remove.remove(ewcfg.role_gellphone)

    role_slimernalia = None
    if user_data.slimernalia_kingpin == True:
        role_slimernalia = ewcfg.role_slimernalia
        misc_roles_remove.remove(ewcfg.role_slimernalia)

    role_ids = []
    for role_id in roles_map_user:

        try:
            role_data = EwRole(id_server=id_server, id_role=role_id)
            roleName = role_data.name
            if roleName != None and roleName not in faction_roles_remove and roleName not in misc_roles_remove and roleName not in poi_roles_remove and role_data.id_role != '':
                role_ids.append(int(role_data.id_role))
        except:
            ewutils.logMsg('error: couldn\'t find role with id {}'.format(role_id))

    try:
        role_data = EwRole(id_server=id_server, name=faction_role)
        if not role_data.id_role in role_ids and role_data.id_role != '':
            role_ids.append(int(role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    except:
        ewutils.logMsg('error: couldn\'t find faction role {}'.format(faction_role))

    try:
        role_data = EwRole(id_server=id_server, name=pvp_role)
        if not role_data.id_role in role_ids and role_data.id_role != '':
            role_ids.append(int(role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    except:
        ewutils.logMsg('error: couldn\'t find pvp role {}'.format(pvp_role))

    try:
        role_data = EwRole(id_server=id_server, name=active_role)
        if not role_data.id_role in role_ids and role_data.id_role != '':
            role_ids.append(int(role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    except:
        ewutils.logMsg('error: couldn\'t find active role {}'.format(active_role))

    try:
        role_data = EwRole(id_server=id_server, name=tutorial_role)
        if not role_data.id_role in role_ids and role_data.id_role != '':
            role_ids.append(int(role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    except:
        ewutils.logMsg('error: couldn\'t find tutorial role {}'.format(tutorial_role))

    # poi roles are disabled
    # try:
    #	major_role_data = EwRole(id_server = id_server, name = poi_major_role)
    #	if not major_role_data.id_role in role_ids and major_role_data.id_role != '':
    #		role_ids.append(int(major_role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    # except:
    #	ewutils.logMsg('error: couldn\'t find major role {}'.format(poi_major_role))

    # try:
    #	minor_role_data = EwRole(id_server = id_server, name = poi_minor_role)
    #	if not minor_role_data.id_role in role_ids and minor_role_data.id_role != '':
    #		role_ids.append(int(minor_role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    # except:
    #	ewutils.logMsg('error: couldn\'t find minor role {}'.format(poi_minor_role))

    try:
        role_data = EwRole(id_server=id_server, name=role_gellphone)
        if not role_data.id_role in role_ids and role_data.id_role != '':
            role_ids.append(int(role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    except:
        ewutils.logMsg('error: couldn\'t find gellphone role {}'.format(role_gellphone))

    try:
        role_data = EwRole(id_server=id_server, name=role_slimernalia)
        if not role_data.id_role in role_ids and role_data.id_role != '':
            role_ids.append(int(role_data.id_role))
    # ewutils.logMsg('found role {} with id {}'.format(role_data.name, role_data.id_role))
    except:
        ewutils.logMsg('error: couldn\'t find slimernalia role {}'.format(role_slimernalia))

    # if faction_role not in role_names:
    # 	role_names.append(faction_role)
    # if poi_role != None and poi_role not in role_names:
    # 	role_names.append(poi_role)

    # replacement_roles = []
    # for name in role_names:
    #	role = roles_map.get(name)

    #	if role != None:
    #		replacement_roles.append(role)
    #	else:
    #		ewutils.logMsg("error: role missing \"{}\"".format(name))

    # ewutils.logMsg('looking for {} roles to replace'.format(len(role_ids)))
    replacement_roles = []

    for role in member.guild.roles:
        if role.id in role_ids:
            # ewutils.logMsg('found role {} with id {}'.format(role.name, role.id))
            replacement_roles.append(role)

    # ewutils.logMsg('found {} roles to replace'.format(len(replacement_roles)))

    try:
        await member.edit(roles=replacement_roles)
    except Exception as e:
        ewutils.logMsg('error: failed to replace roles for {}:{}'.format(member.display_name, str(e)))

    if refresh_perms:
        await refresh_user_perms(client=client, id_server=id_server, used_member=member)


# try:
#	await member.edit(roles=replacement_roles)
# except:
#	ewutils.logMsg('error: failed to replace roles for {}'.format(member.display_name))

# Removes and updates user permissions. It's got a fair amount of debuggers, sorry about the mess!
async def refresh_user_perms(client, id_server, used_member = None, startup = False):
    server = client.get_guild(id_server)

    has_overrides = False

    user_data = EwUser(member=used_member)
    user_poi_obj = poi_static.id_to_poi.get(user_data.poi)

    if not startup:
        for poi in poi_static.poi_list:
            channel = fe_utils.get_channel(server, poi.channel)
            if channel == None:
                # ewutils.logMsg('Error: In refresh_user_perms, could not get channel for {}'.format(poi.channel))
                # Second try
                channel = fe_utils.get_channel(server, poi.channel)
                if channel == None:
                    continue

            if used_member in channel.overwrites and user_data.poi != poi.id_poi:
                # Incorrect overwrite found for user

                try:

                    for chname in poi.permissions:
                        ch = fe_utils.get_channel(server, chname)
                        if ch != None:
                            await ch.set_permissions(used_member, overwrite=None)

                except:
                    ewutils.logMsg("Failed to remove permissions for {} in channel {}.".format(used_member.display_name, channel.name))

            # User doesn't have permissions for his current poi's gameplay channel
            elif used_member not in channel.overwrites and user_data.poi == poi.id_poi:

                correct_poi = poi_static.id_to_poi.get(user_data.poi)

                if correct_poi == None:
                    print('User {} has invalid POI of {}'.format(user_data.id_user, user_data.poi))
                    correct_poi = poi_static.id_to_poi.get(ewcfg.poi_id_downtown)

                try:

                    # Set permissions for the user's current poi

                    for chname in poi.permissions:
                        ch = fe_utils.get_channel(server, chname)
                        if ch != None:
                            permissions_dict = poi.permissions[chname]
                            overwrite = discord.PermissionOverwrite()
                            overwrite.read_messages = True if ewcfg.permission_read_messages in permissions_dict else False
                            overwrite.send_messages = True if ewcfg.permission_send_messages in permissions_dict else False
                            overwrite.connect = True if ewcfg.permission_connect_to_voice in permissions_dict else False
                            await ch.set_permissions(used_member, overwrite=overwrite)
                        else:
                            ewutils.logMsg("Channel {} not found".format(chname))

                except Exception as e:
                    ewutils.logMsg("Failed to add permissions to {} in channel {}:{}.".format(used_member.display_name, channel.name, str(e)))

                has_overrides = True

        if not has_overrides:
            # Member has no overwrites -- fix this:
            user_data = EwUser(member=used_member)

            # User might not have their poi set to downtown when they join the server.
            if user_data.poi == None:
                correct_poi = poi_static.id_to_poi.get(ewcfg.poi_id_downtown)
            else:
                correct_poi = poi_static.id_to_poi.get(user_data.poi)

            if correct_poi == None:
                print('User {} has invalid POI of {}'.format(user_data.id_user, user_data.poi))
                correct_poi = poi_static.id_to_poi.get(ewcfg.poi_id_downtown)

            try:

                # Set permissions for the user's current poi
                for chname in correct_poi.permissions:
                    ch = fe_utils.get_channel(server, chname)
                    if ch != None:

                        permissions_dict = correct_poi.permissions[chname]
                        overwrite = discord.PermissionOverwrite()

                        overwrite.read_messages = True if ewcfg.permission_read_messages in permissions_dict else False
                        overwrite.send_messages = True if ewcfg.permission_send_messages in permissions_dict else False
                        overwrite.connect = True if ewcfg.permission_connect_to_voice in permissions_dict else False
                        await ch.set_permissions(used_member, overwrite=overwrite)

                    else:
                        ewutils.logMsg("Channel {} not found".format(chname))

            except Exception as e:
                ewutils.logMsg("Failed to fix permissions for {}:{}.".format(used_member.display_name, str(e)))


# Remove all user overwrites in the server's POI channels
async def remove_user_overwrites(cmd):
    if not cmd.message.author.guild_permissions.administrator:
        return

    server = cmd.guild
    client = ewutils.get_client()

    for poi in poi_static.poi_list:

        searched_channel = poi.channel

        channel = fe_utils.get_channel(server, searched_channel)

        if channel == None:
            # Second try
            channel = fe_utils.get_channel(server, searched_channel)
            if channel == None:
                continue

        # print('{} overwrites: {}'.format(poi.id_poi, channel.overwrites))
        for tuple in channel.overwrites:
            # print('tuplevar: {}'.format(tuple) + '\n\n')
            if tuple not in server.roles:
                member = tuple

                print('removed overwrite in {} for {}'.format(channel, member))

                for i in range(ewcfg.permissions_tries):
                    await channel.set_permissions(member, overwrite=None)

    response = "DEBUG: ALL USER OVERWRITES DELETED."
    return await fe_utils.send_message(client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


def checkClearance(member = None):
    if member is None:
        return -1


    roles_map_user = ewutils.getRoleMap(member.roles)


    if ewcfg.role_bpadmin in roles_map_user:
        return 1 #currently in admin
    elif ewcfg.role_brimstoneprog in roles_map_user:
        return 2 #casual admin
    elif ewcfg.role_bdadmin in roles_map_user:
        return 3 #mod admin
    elif ewcfg.role_brimstonedesperados in roles_map_user:
        return 4 #casual mod admin
    else:
        return 10
