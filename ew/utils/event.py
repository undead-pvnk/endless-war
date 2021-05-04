
import random

from ..static import cfg as ewcfg
from ..static import weapons as static_weapons
from ..static import poi as poi_static

from ..backend import core as bknd_core
from ..backend import item as bknd_item

from .. import wep as ewwep
from .. import item as ewitem
from .. import hunting as ewhunting

from . import core as ewutils

from ..backend.user import EwUser
from ..backend.player import EwPlayer
from ..backend.hunting import EwEnemy
from ..backend.market import EwMarket
from ..backend.item import EwItem

""" Damage all players in a district """
def explode(damage = 0, district_data = None, market_data = None):
	id_server = district_data.id_server
	poi = district_data.name

	if market_data == None:
		market_data = EwMarket(id_server = district_data.id_server)

	client = ewutils.get_client()
	server = client.get_guild(id_server)

	resp_cont = EwResponseContainer(id_server = id_server)
	response = ""
	channel = poi_static.id_to_poi.get(poi).channel

	life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive, ewcfg.life_state_shambler]
	users = district_data.get_players_in_district(life_states = life_states, pvp_only = True)

	enemies = district_data.get_enemies_in_district()

	# damage players
	for user in users:
		user_data = EwUser(id_user = user, id_server = id_server, data_level = 1)
		mutations = user_data.get_mutations()

		user_weapon = None
		user_weapon_item = None
		if user_data.weapon >= 0:
			user_weapon_item = EwItem(id_item = user_data.weapon)
			user_weapon = static_weapons.weapon_map.get(user_weapon_item.item_props.get("weapon_type"))

		# apply defensive mods
		slimes_damage_target = damage * ewwep.damage_mod_defend(
			shootee_data = user_data,
			shootee_mutations = mutations,
			shootee_weapon = user_weapon,
			market_data = market_data
		)

		# apply sap armor
		#sap_armor = ewwep.get_sap_armor(shootee_data = user_data, sap_ignored = 0)
		#slimes_damage_target *= sap_armor
		#slimes_damage_target = int(max(0, slimes_damage_target))

		# apply fashion armor

		# disabled until held items update
		# fashion_armor = ewwep.get_fashion_armor(shootee_data = user_data)
		# slimes_damage_target *= fashion_armor
		slimes_damage_target = int(max(0, slimes_damage_target))

		player_data = EwPlayer(id_user = user_data.id_user)
		response = "{} is blown back by the explosion’s sheer force! They lose {:,} slime!!".format(player_data.display_name, slimes_damage_target)
		resp_cont.add_channel_response(channel, response)
		slimes_damage = slimes_damage_target
		if user_data.slimes < slimes_damage + user_data.bleed_storage:
			# die in the explosion
			district_data.change_slimes(n = user_data.slimes, source = ewcfg.source_killing)
			district_data.persist()
			slimes_dropped = user_data.totaldamage + user_data.slimes

			user_data.trauma = ewcfg.trauma_id_environment
			user_data.die(cause = ewcfg.cause_killing)
			#user_data.change_slimes(n = -slimes_dropped / 10, source = ewcfg.source_ghostification)
			user_data.persist()

			response = "Alas, {} was caught too close to the blast. They are consumed by the flames, and die in the explosion.".format(player_data.display_name)
			resp_cont.add_channel_response(channel, response)

			resp_cont.add_member_to_update(server.get_member(user_data.id_user))
		else:
			# survive
			slime_splatter = 0.5 * slimes_damage
			district_data.change_slimes(n = slime_splatter, source = ewcfg.source_killing)
			district_data.persist()
			slimes_damage -= slime_splatter
			user_data.bleed_storage += slimes_damage
			user_data.change_slimes(n = -slime_splatter, source = ewcfg.source_killing)
			user_data.persist()

	# damage enemies
	for enemy in enemies:
		enemy_data = EwEnemy(id_enemy = enemy, id_server = id_server)

		response = "{} is blown back by the explosion’s sheer force! They lose {:,} slime!!".format(enemy_data.display_name, damage)
		resp_cont.add_channel_response(channel, response)

		slimes_damage_target = damage
			
		# apply sap armor
		#sap_armor = ewwep.get_sap_armor(shootee_data = enemy_data, sap_ignored = 0)
		#slimes_damage_target *= sap_armor
		#slimes_damage_target = int(max(0, slimes_damage_target))

		slimes_damage = slimes_damage_target
		if enemy_data.slimes < slimes_damage + enemy_data.bleed_storage:
			# die in the explosion
			district_data.change_slimes(n = enemy_data.slimes, source = ewcfg.source_killing)
			district_data.persist()
			# slimes_dropped = enemy_data.totaldamage + enemy_data.slimes
			# explode_damage = ewutils.slime_bylevel(enemy_data.level)

			response = "Alas, {} was caught too close to the blast. They are consumed by the flames, and die in the explosion.".format(enemy_data.display_name)
			resp_cont.add_response_container(ewhunting.drop_enemy_loot(enemy_data, district_data))
			resp_cont.add_channel_response(channel, response)

			enemy_data.life_state = ewcfg.enemy_lifestate_dead
			enemy_data.persist()

		else:
			# survive
			slime_splatter = 0.5 * slimes_damage
			district_data.change_slimes(n = slime_splatter, source = ewcfg.source_killing)
			district_data.persist()
			slimes_damage -= slime_splatter
			enemy_data.bleed_storage += slimes_damage
			enemy_data.change_slimes(n = -slime_splatter, source = ewcfg.source_killing)
			enemy_data.persist()
	return resp_cont

async def activate_trap_items(district, id_server, id_user):
	# Return if --> User has 0 credence, there are no traps, or if the trap setter is the one who entered the district.
	#print("TRAP FUNCTION")
	trap_was_dud = False
	
	user_data = EwUser(id_user=id_user, id_server=id_server)
	# if user_data.credence == 0:
	# 	#print('no credence')
	# 	return
	
	if user_data.life_state == ewcfg.life_state_corpse:
		#print('get out ghosts reeeee!')
		return
	
	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor();

		district_channel_name = poi_static.id_to_poi.get(district).channel

		client = ewutils.get_client()

		server = client.get_guild(id_server)
		
		member = server.get_member(id_user)

		district_channel = get_channel(server=server, channel_name=district_channel_name)
		
		searched_id = district + '_trap'
		
		cursor.execute("SELECT id_item, id_user FROM items WHERE id_user = %s AND id_server = %s".format(
			id_item = ewcfg.col_id_item,
			id_user = ewcfg.col_id_user
		), (
			searched_id,
			id_server,
		))

		traps = cursor.fetchall()
		
		if len(traps) == 0:
			#print('no traps')
			return
		
		trap_used = traps[0]
		
		trap_id_item = trap_used[0]
		#trap_id_user = trap_used[1]
		
		trap_item_data = EwItem(id_item=trap_id_item)
		
		trap_chance = int(trap_item_data.item_props.get('trap_chance'))
		trap_user_id = trap_item_data.item_props.get('trap_user_id')
		
		if int(trap_user_id) == user_data.id_user:
			#print('trap same user id')
			return
		
		if random.randrange(101) < trap_chance:
			# Trap was triggered!
			pranker_data = EwUser(id_user=int(trap_user_id), id_server=id_server)
			pranked_data = user_data

			response = trap_item_data.item_props.get('prank_desc')

			side_effect = trap_item_data.item_props.get('side_effect')

			if side_effect != None:
				response += await ewitem.perform_prank_item_side_effect(side_effect, member=member)
			
			#calculate_gambit_exchange(pranker_data, pranked_data, trap_item_data, trap_used=True)
		else:
			# Trap was a dud.
			trap_was_dud = True
			response = "Close call! You were just about to eat shit and fall right into someone's {}, but luckily, it was a dud.".format(trap_item_data.item_props.get('item_name'))
		
		bknd_item.item_delete(trap_id_item)
		
	finally:
		# Clean up the database handles.
		cursor.close()
		bknd_core.databaseClose(conn_info)
	await send_message(client, district_channel, formatMessage(member, response))
	
	# if not trap_was_dud:
	# 	client = ewutils.get_client()
	# 	server = client.get_server(id_server)
	# 
	# 	prank_feed_channel = get_channel(server, 'prank-feed')
	# 
	# 	response += "\n`-------------------------`"
	# 	await send_message(client, prank_feed_channel, formatMessage(member, response))


async def assign_status_effect(cmd = None, status_name = None, user_id = None, server_id = None):
	if status_name is not None:
		user_data = EwUser(id_server=server_id, id_user = user_id)
		response = user_data.applyStatus(id_status=status_name, source = user_id, id_target = user_id)
	else:
		if not cmd.message.author.guild_permissions.administrator or cmd.mentions_count == 0:
			return await fake_failed_command(cmd)
		target = cmd.mentions[0]
		status_name = ewutils.flattenTokenListToString(cmd.tokens[2:])
		user_data = EwUser(member=target)
		response = user_data.applyStatus(id_status=status_name, source=user_data.id_user, id_target=user_data.id_user)
	return await send_message(cmd.client, cmd.message.channel, formatMessage(cmd.message.author, response))


