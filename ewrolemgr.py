import asyncio

import ewcfg
import ewutils

from ew import EwUser

class EwRole:
	id_server = ""
	id_role = ""
	name = ""

	def __init__(self, id_server = None, name = None):
		if id_server is not None and name is not None:
			self.id_server = id_server
			self.name = name


			data = ewutils.execute_sql_query("SELECT {id_role} FROM roles WHERE id_server = %s AND {name} = %s".format(
				id_role = ewcfg.col_id_role,
				name = ewcfg.col_role_name
			), (
				id_server,
				name
			))

			if len(data) > 0:  # if data is not empty, i.e. it found an entry
				# data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
				self.id_role = data[0][0]
			else:  # create new entry
				ewutils.execute_sql_query("REPLACE INTO roles ({id_server}, {name}) VALUES (%s, %s)".format(
					id_server = ewcfg.col_id_server,
					name = ewcfg.col_role_name
				), (
					id_server,
					name
				))

	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO roles (id_server, {id_role}, {name}) VALUES(%s, %s, %s)".format(
			id_role = ewcfg.col_id_role,
			name = ewcfg.col_role_name
		), (
			self.id_server,
			self.id_role,
			self.name
		))
			



def setupRoles(client = None, id_server = ""):
	
	roles_map = ewutils.getRoleMap(client.get_server(id_server).roles)
	for poi in ewcfg.poi_list:
		if poi.role in roles_map:
			try:
				role_data = EwRole(id_server = id_server, name = poi.role)
				role_data.id_role = roles_map[poi.role].id
				role_data.persist()
			except:
				ewutils.logMsg('Failed to set up role {}'.format(poi.role))

	for faction_role in ewcfg.faction_roles:
		if faction_role in roles_map:
			try:
				role_data = EwRole(id_server = id_server, name = faction_role)
				role_data.id_role = roles_map[faction_role].id
				role_data.persist()
			except:
				ewutils.logMsg('Failed to set up role {}'.format(faction_role))

async def hideRoleNames(client = None, id_server = ""):
	
	server = client.get_server(id_server)
	roles_map = ewutils.getRoleMap(server.roles)
	for poi in ewcfg.poi_list:
		try:
			if poi.role in roles_map:
				role = roles_map[poi.role]
				await client.edit_role(server = server, role = role, name = ewcfg.generic_role_name)
		except:
			ewutils.logMsg('Failed to hide role name for {}'.format(poi.role))


async def restoreRoleNames(cmd):

	member = cmd.message.author
	
	if not member.server_permissions.administrator:
		return
	
	client = cmd.client
	server = member.server
	for poi in ewcfg.poi_list:
		try:
			role_data = EwRole(id_server = server.id, name = poi.role)
			for role in server.roles:
				if role.id == role_data.id_role:
					await client.edit_role(server = server, role = role, name = role_data.name)
		except:
			ewutils.logMsg('Failed to restore role name for {}'.format(poi.role))

"""
	Fix the Discord roles assigned to this member.
"""
async def updateRoles(
	client = None,
	member = None
):
	user_data = EwUser(member = member)
	id_server = user_data.id_server

	roles_map = ewutils.getRoleMap(member.server.roles)
	roles_map_user = ewutils.getRoleMap(member.roles)

	if user_data.life_state != ewcfg.life_state_kingpin and ewcfg.role_kingpin in roles_map_user:
		# Fix the life_state of kingpins, if somehow it wasn't set.
		user_data.life_state = ewcfg.life_state_kingpin
		user_data.persist()
	elif user_data.life_state != ewcfg.life_state_grandfoe and ewcfg.role_grandfoe in roles_map_user:
		# Fix the life_state of a grand foe.
		user_data.life_state = ewcfg.life_state_grandfoe
		user_data.persist()

	#faction_roles_remove = [
	#	ewcfg.role_juvenile,
	#	ewcfg.role_juvenile_pvp,
	#	ewcfg.role_rowdyfuckers,
	#	ewcfg.role_rowdyfuckers_pvp,
	#	ewcfg.role_copkillers,
	#	ewcfg.role_copkillers_pvp,
	#	ewcfg.role_corpse,
	#	ewcfg.role_corpse_pvp,
	#	ewcfg.role_kingpin,
	#	ewcfg.role_grandfoe
	#]

	# Manage faction roles.
	faction_role = ewutils.get_faction(user_data = user_data)

	#faction_roles_remove.remove(faction_role)

	# Manage location roles.
	poi_role = None

	poi = ewcfg.id_to_poi.get(user_data.poi)
	if poi != None:
		poi_role = poi.id_poi

	#poi_roles_remove = []
	#for poi in ewcfg.poi_list:
	#	if poi.role != None and poi.role != poi_role:
	#		poi_roles_remove.append(poi.role)

	#for poi in ewcfg.poi_list:
	#	if poi.id_poi != None and poi.id_poi != poi_role:
	#		poi_roles_remove.append(poi.id_poi)

	#for i in range(len(faction_roles_remove)):
	#	try:
	#		faction_roles_remove[i] = ewcfg.roles_map[faction_roles_remove[i]][id_server]
	#	except:
	#		ewutils.logMsg('error: couldn\'t find role {}'.format(faction_roles_remove[i]))

	#for i in range(len(poi_roles_remove)):
	#	try:
	#		poi_roles_remove[i] = ewcfg.roles_map[poi_roles_remove[i]][id_server]
	#	except:
	#		ewutils.logMsg('error: ouldn\'t find role {}'.format(poi_roles_remove[i]))

	#role_names = []
	#for roleName in roles_map_user:
	#	if roleName not in faction_roles_remove and roleName not in poi_roles_remove:
	#		role_names.append(roleName)

	role_ids = []
	try:
		role_data = EwRole(id_server = id_server, name = faction_role)
		role_ids.append(role_data.id_role)
	except:
		ewutils.logMsg('error: couldn\'t find role {}'.format(faction_role))

	try:
		role_data = EwRole(id_server = id_server, name = poi_role)
		role_ids.append(role_data.id_role)
	except:
		ewutils.logMsg('error: couldn\'t find role {}'.format(poi_role))

	if user_data.life_state == ewcfg.life_state_kingpin:
		try:
			role_data = EwRole(id_server = id_server, name = ewcfg.role_kingpin)
			role_ids.append(role_data.id_role)
		except:
			ewutils.logMsg('error: couldn\'t find role {}'.format(ewcfg.role_kingpin))

	if user_data.life_state == ewcfg.life_state_grandfoe:
		try:
			role_data = EwRole(id_server = id_server, name = ewcfg.role_grandfoe)
			role_ids.append(role_data.id_role)
		except:
			ewutils.logMsg('error: couldn\'t find role {}'.format(ewcfg.role_grandfoe))
		

	#for role_id in roles_map_user:
	#	if role_id not in faction_roles_remove and role_id not in poi_roles_remove:
	#		role_ids.append(role_id)

	#if faction_role not in role_names:
	#	role_names.append(faction_role)
	#if poi_role != None and poi_role not in role_names:
	#	role_names.append(poi_role)

	#replacement_roles = []
	#for name in role_names:
	#	role = roles_map.get(name)

	#	if role != None:
	#		replacement_roles.append(role)
	#	else:
	#		ewutils.logMsg("error: role missing \"{}\"".format(name))

	replacement_roles = []

	for role in member.server.roles:
		if role.id in role_ids:
			replacement_roles.append(role)


	try:
		await client.replace_roles(member, *replacement_roles)
	except:
		ewutils.logMsg('error: failed to replace roles for {}'.format(member.display_name))

	#try:
	#	await client.replace_roles(member, *replacement_roles)
	#except:
	#	ewutils.logMsg('error: failed to replace roles for {}'.format(member.display_name))
