import time

from . import core as bknd_core
from ..static import cfg as ewcfg
from ..utils import core as ewutils

""" Enemy data model for database persistence """
class EwEnemyBase:
	id_enemy = 0
	id_server = -1

	combatant_type = "enemy"

	# The amount of slime an enemy has
	slimes = 0

	# The total amount of damage an enemy has sustained throughout its lifetime
	totaldamage = 0

	# The type of AI the enemy uses to select which players to attack
	ai = ""

	# The name of enemy shown in responses
	display_name = ""

	# Used to help identify enemies of the same type in a district
	identifier = ""

	# An enemy's level, which determines how much damage it does
	level = 0

	# An enemy's location
	poi = ""

	# Life state 0 = Dead, pending for deletion when it tries its next attack / action
	# Life state 1 = Alive / Activated raid boss
	# Life state 2 = Raid boss pending activation
	life_state = 0

	# Used to determine how much slime an enemy gets, what AI it uses, as well as what weapon it uses.
	enemytype = ""

	# The 'weapon' of an enemy
	attacktype = ""

	# An enemy's bleed storage
	bleed_storage = 0

	# Used for determining when a raid boss should be able to move between districts
	time_lastenter = 0

	# Used to determine how much slime an enemy started out with to create a 'health bar' ( current slime / initial slime )
	initialslimes = 0

	# Enemies despawn when this value is less than int(time.time())
	expiration_date = 0

	# Used by the 'defender' AI to determine who it should retaliate against
	id_target = -1

	# Used by raid bosses to determine when they should activate
	raidtimer = 0
	
	# Determines if an enemy should use its rare variant or not
	rare_status = 0
	
	# What kind of weather the enemy is suited to
	weathertype = 0

	# Sap armor
	#hardened_sap = 0
	
	# What faction the enemy belongs to
	faction = ""
	
	# What class the enemy belongs to
	enemyclass = ""
	
	# Tracks which user is associated with the enemy
	owner = -1

	# Coordinate used for enemies in Gankers Vs. Shamblers
	gvs_coord = ""
	
	# Various properties different enemies might have
	enemy_props = ""

	""" Load the enemy data from the database. """

	def __init__(self, id_enemy=None, id_server=None, enemytype=None):
		self.combatant_type = ewcfg.combatant_type_enemy
		self.enemy_props = {}

		query_suffix = ""

		if id_enemy != None:
			query_suffix = " WHERE id_enemy = '{}'".format(id_enemy)
		else:

			if id_server != None:
				query_suffix = " WHERE id_server = '{}'".format(id_server)
				if enemytype != None:
					query_suffix += " AND enemytype = '{}'".format(enemytype)

		if query_suffix != "":
			try:
				conn_info = bknd_core.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object
				cursor.execute(
					"SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM enemies{}".format(
						ewcfg.col_id_enemy,
						ewcfg.col_id_server,
						ewcfg.col_enemy_slimes,
						ewcfg.col_enemy_totaldamage,
						ewcfg.col_enemy_ai,
						ewcfg.col_enemy_type,
						ewcfg.col_enemy_attacktype,
						ewcfg.col_enemy_display_name,
						ewcfg.col_enemy_identifier,
						ewcfg.col_enemy_level,
						ewcfg.col_enemy_poi,
						ewcfg.col_enemy_life_state,
						ewcfg.col_enemy_bleed_storage,
						ewcfg.col_enemy_time_lastenter,
						ewcfg.col_enemy_initialslimes,
						ewcfg.col_enemy_expiration_date,
						ewcfg.col_enemy_id_target,
						ewcfg.col_enemy_raidtimer,
						ewcfg.col_enemy_rare_status,
						#ewcfg.col_enemy_hardened_sap,
						ewcfg.col_enemy_weathertype,
						ewcfg.col_faction,
						ewcfg.col_enemy_class,
						ewcfg.col_enemy_owner,
						ewcfg.col_enemy_gvs_coord,
						query_suffix
					))
				result = cursor.fetchone()

				if result != None:
					# Record found: apply the data to this object.
					self.id_enemy = result[0]
					self.id_server = result[1]
					self.slimes = result[2]
					self.totaldamage = result[3]
					self.ai = result[4]
					self.enemytype = result[5]
					self.attacktype = result[6]
					self.display_name = result[7]
					self.identifier = result[8]
					self.level = result[9]
					self.poi = result[10]
					self.life_state = result[11]
					self.bleed_storage = result[12]
					self.time_lastenter = result[13]
					self.initialslimes = result[14]
					self.expiration_date = result[15]
					self.id_target = result[16]
					self.raidtimer = result[17]
					self.rare_status = result[18]
					#self.hardened_sap = result[19]
					self.weathertype = result[19]
					self.faction = result[20]
					self.enemyclass = result[21]
					self.owner = result[22]
					self.gvs_coord = result[23]

					# Retrieve additional properties
					cursor.execute("SELECT {}, {} FROM enemies_prop WHERE id_enemy = %s".format(
						ewcfg.col_name,
						ewcfg.col_value
					), (
						self.id_enemy,
					))

					for row in cursor:
						# this try catch is only necessary as long as extraneous props exist in the table
						try:
							self.enemy_props[row[0]] = row[1]
						except:
							ewutils.logMsg("extraneous enemies_prop row detected.")

			finally:
				# Clean up the database handles.
				cursor.close()
				bknd_core.databaseClose(conn_info)

	""" Save enemy data object to the database. """

	def persist(self):
		try:
			conn_info = bknd_core.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute(
				"REPLACE INTO enemies({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
					ewcfg.col_id_enemy,
					ewcfg.col_id_server,
					ewcfg.col_enemy_slimes,
					ewcfg.col_enemy_totaldamage,
					ewcfg.col_enemy_ai,
					ewcfg.col_enemy_type,
					ewcfg.col_enemy_attacktype,
					ewcfg.col_enemy_display_name,
					ewcfg.col_enemy_identifier,
					ewcfg.col_enemy_level,
					ewcfg.col_enemy_poi,
					ewcfg.col_enemy_life_state,
					ewcfg.col_enemy_bleed_storage,
					ewcfg.col_enemy_time_lastenter,
					ewcfg.col_enemy_initialslimes,
					ewcfg.col_enemy_expiration_date,
					ewcfg.col_enemy_id_target,
					ewcfg.col_enemy_raidtimer,
					ewcfg.col_enemy_rare_status,
					#ewcfg.col_enemy_hardened_sap,
					ewcfg.col_enemy_weathertype,
					ewcfg.col_faction,
					ewcfg.col_enemy_class,
					ewcfg.col_enemy_owner,
					ewcfg.col_enemy_gvs_coord
				), (
					self.id_enemy,
					self.id_server,
					self.slimes,
					self.totaldamage,
					self.ai,
					self.enemytype,
					self.attacktype,
					self.display_name,
					self.identifier,
					self.level,
					self.poi,
					self.life_state,
					self.bleed_storage,
					self.time_lastenter,
					self.initialslimes,
					self.expiration_date,
					self.id_target,
					self.raidtimer,
					self.rare_status,
					#self.hardened_sap,
					self.weathertype,
					self.faction,
					self.enemyclass,
					self.owner,
					self.gvs_coord,
				))
			
			# If the enemy doesn't have an ID assigned yet, have the cursor give us the proper ID.
			if self.id_enemy == 0:
				used_enemy_id = cursor.lastrowid
				#print('used new enemy id')
			else:
				used_enemy_id = self.id_enemy
				#print('used existing enemy id')
		
			# Remove all existing property rows.
			cursor.execute("DELETE FROM enemies_prop WHERE {} = %s".format(
				ewcfg.col_id_enemy
			), (
				used_enemy_id,
			))
			
			if self.enemy_props != None:
				for name in self.enemy_props:
					cursor.execute("INSERT INTO enemies_prop({}, {}, {}) VALUES(%s, %s, %s)".format(
						ewcfg.col_id_enemy,
						ewcfg.col_name,
						ewcfg.col_value
					), (
						used_enemy_id,
						name,
						self.enemy_props[name]
					))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			bknd_core.databaseClose(conn_info)


		
class EwOperationData:
	
	# The ID of the user who chose a seedpacket/tombstone for that operation
	id_user = 0
	
	# The district that the operation takes place in
	district = ""
	
	# The enemytype associated with that seedpacket/tombstone.
	# A single Garden Ganker can not choose two of the same enemytype. No duplicate tombstones are allowed at all.
	enemytype = ""
	
	# The 'faction' of whoever chose that enemytype. This is either set to 'gankers' or 'shamblers'.
	faction = ""
	
	# The ID of the item used in the operation
	id_item = 0
	
	# The amount of shamblers stored in a tombstone.
	shambler_stock = 0

	def __init__(
		self,
		id_user = -1,
		district = "",
		enemytype = "",
		faction = "",
		id_item = -1,
		shambler_stock = 0,
	):
		self.id_user = id_user
		self.district = district
		self.enemytype = enemytype
		self.faction = faction
		self.id_item = id_item
		self.shambler_stock = shambler_stock
		
		if(id_user != ""):

			try:
				conn_info = bknd_core.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()
	
				# Retrieve object
				cursor.execute("SELECT {}, {}, {} FROM gvs_ops_choices WHERE {} = %s AND {} = %s AND {} = %s".format(
					ewcfg.col_faction,
					ewcfg.col_id_item,
					ewcfg.col_shambler_stock,
					
					ewcfg.col_id_user,
					ewcfg.col_district,
					ewcfg.col_enemy_type
				), (
					self.id_user,
					self.district,
					self.enemytype,
				))
				result = cursor.fetchone()
	
				if result != None:
					# Record found: apply the data to this object.
					self.faction = result[0]
					self.id_item = result[1]
					self.shambler_stock = result[2]
				else:
					# Create a new database entry if the object is missing.
					cursor.execute("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
						ewcfg.col_id_user,
						ewcfg.col_district,
						ewcfg.col_enemy_type,
						ewcfg.col_faction,
						ewcfg.col_id_item,
						ewcfg.col_shambler_stock,
					), (
						self.id_user,
						self.district,
						self.enemytype,
						self.faction,
						self.id_item,
						self.shambler_stock,
					))
	
					conn.commit()

			finally:
				# Clean up the database handles.
				cursor.close()
				bknd_core.databaseClose(conn_info)

	def persist(self):
		try:
			conn_info = bknd_core.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Save the object.
			cursor.execute("REPLACE INTO gvs_ops_choices({}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_user,
				ewcfg.col_district,
				ewcfg.col_enemy_type,
				ewcfg.col_faction,
				ewcfg.col_id_item,
				ewcfg.col_shambler_stock
			), (
				self.id_user,
				self.district,
				self.enemytype,
				self.faction,
				self.id_item,
				self.shambler_stock
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			bknd_core.databaseClose(conn_info)
	
	def delete(self):
		try:
			conn_info = bknd_core.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			cursor.execute("DELETE FROM gvs_ops_choices WHERE {id_user} = %s AND {enemytype} = %s AND {district} = %s".format(
				id_user=ewcfg.col_id_user,
				enemytype=ewcfg.col_enemy_type,
				district=ewcfg.col_district,
			), (
				self.id_user,
				self.enemytype,
				self.district
			))
			
		finally:
			# Clean up the database handles.
			cursor.close()
			bknd_core.databaseClose(conn_info)



async def delete_all_enemies(cmd=None, query_suffix="", id_server_sent=""):
	if cmd != None:
		author = cmd.message.author

		if not author.guild_permissions.administrator:
			return

		id_server = cmd.message.guild.id

		bknd_core.execute_sql_query("DELETE FROM enemies WHERE id_server = {id_server}".format(
			id_server=id_server
		))

		ewutils.logMsg("Deleted all enemies from database connected to server {}".format(id_server))

	else:
		id_server = id_server_sent

		bknd_core.execute_sql_query("DELETE FROM enemies WHERE id_server = {} {}".format(
			id_server,
			query_suffix
		))

		ewutils.logMsg(
			"Deleted all enemies from database connected to server {}. Query suffix was '{}'".format(id_server,
																									 query_suffix))

# Check if raidboss is ready to attack / be attacked
def check_raidboss_countdown(enemy_data):
	time_now = int(time.time())

	# Wait for raid bosses
	if enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.raidtimer <= time_now - ewcfg.time_raidcountdown:
		# Raid boss has activated!
		return True
	elif enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.raidtimer > time_now - ewcfg.time_raidcountdown:
		# Raid boss hasn't activated.
		return False

# Check if an enemy is dead. Implemented to prevent enemy data from being recreated when not necessary.
def check_death(enemy_data):
	if enemy_data.slimes <= 0 or enemy_data.life_state == ewcfg.enemy_lifestate_dead:
		# delete_enemy(enemy_data)
		return True
	else:
		return False


# Deletes an enemy the database.
def delete_enemy(enemy_data):
	# print("DEBUG - {} - {} DELETED".format(enemy_data.id_enemy, enemy_data.display_name))
	enemy_data.clear_allstatuses()
	bknd_core.execute_sql_query("DELETE FROM enemies WHERE {id_enemy} = %s".format(
		id_enemy=ewcfg.col_id_enemy
	), (
		enemy_data.id_enemy,
	))


def ga_check_coord_for_shambler(enemy_data, ga_range, direction, piercing, splash, pierceamount, singletilepierce):
	current_coord = enemy_data.gvs_coord
	detected_shamblers = {}

	for sh_row in ewcfg.gvs_valid_coords_shambler:

		if current_coord in sh_row:
			index = sh_row.index(current_coord)
			checked_coords = gvs_grid_gather_coords(enemy_data.enemyclass, int(ga_range), direction, sh_row, index)

			# print('GAIA -- CHECKED COORDS FOR {} WITH ID {}: {}'.format(enemy_data.enemytype, enemy_data.id_enemy, checked_coords))

			# Check coordinate for shamblers in range of gaiaslimeoid.
			shambler_data = bknd_core.execute_sql_query(
				"SELECT {id_enemy}, {enemytype} FROM enemies WHERE {enemyclass} = %s AND {gvs_coord} IN %s AND {poi} = %s AND {id_server} = %s AND NOT ({life_state} = {life_state_dead} OR {life_state} = {life_state_unactivated})".format(
					id_enemy=ewcfg.col_id_enemy,
					enemyclass=ewcfg.col_enemy_class,
					enemytype=ewcfg.col_enemy_type,
					gvs_coord=ewcfg.col_enemy_gvs_coord,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					life_state=ewcfg.col_life_state,
					life_state_dead=ewcfg.enemy_lifestate_dead,
					life_state_unactivated=ewcfg.enemy_lifestate_unactivated,
				), (
					ewcfg.enemy_class_shambler,
					tuple(checked_coords),
					enemy_data.poi,
					enemy_data.id_server
				))

			# print(len(shambler_data))
			if len(shambler_data) > 0:

				for shambler in shambler_data:

					current_shambler_data = EwEnemyBase(id_enemy=shambler[0], id_server=enemy_data.id_server)
					detected_shamblers[current_shambler_data.id_enemy] = current_shambler_data.gvs_coord

					if shambler[1] in [ewcfg.enemy_type_juvieshambler] and current_shambler_data.enemy_props.get(
							'underground') == 'true':
						del detected_shamblers[current_shambler_data.id_enemy]

				if piercing == 'false':
					detected_shamblers = gvs_find_nearest_shambler(checked_coords, detected_shamblers)
				elif int(pierceamount) > 0:
					detected_shamblers = gvs_find_nearest_shambler(checked_coords, detected_shamblers, pierceamount,
																   singletilepierce)

			# print('gaia in coord {} found shambler in coords {} in {}.'.format(current_coord, checked_coords, enemy_data.poi))

			if splash == 'true':

				if detected_shamblers == {}:
					checked_splash_coords = checked_coords
				else:
					checked_splash_coords = []
					for shambler in detected_shamblers.keys():
						checked_splash_coords.append(detected_shamblers[shambler])

				splash_coords = gvs_get_splash_coords(checked_splash_coords)

				splash_shambler_data = bknd_core.execute_sql_query(
					"SELECT {id_enemy}, {enemytype}, {gvs_coord} FROM enemies WHERE {enemyclass} = %s AND {gvs_coord} IN %s AND {poi} = %s AND {id_server} = %s".format(
						id_enemy=ewcfg.col_id_enemy,
						enemyclass=ewcfg.col_enemy_class,
						enemytype=ewcfg.col_enemy_type,
						gvs_coord=ewcfg.col_enemy_gvs_coord,
						poi=ewcfg.col_poi,
						id_server=ewcfg.col_id_server,
					), (
						ewcfg.enemy_class_shambler,
						tuple(splash_coords),
						enemy_data.poi,
						enemy_data.id_server
					))

				for splashed_shambler in splash_shambler_data:
					detected_shamblers[splashed_shambler[0]] = splashed_shambler[2]
			break

	return detected_shamblers


def sh_check_coord_for_gaia(enemy_data, sh_range, direction):
	current_coord = enemy_data.gvs_coord
	gaias_in_coord = []

	if current_coord not in ewcfg.gvs_coords_end:

		for sh_row in ewcfg.gvs_valid_coords_shambler:

			if current_coord in sh_row:
				index = sh_row.index(current_coord)
				checked_coord = gvs_grid_gather_coords(enemy_data.enemyclass, sh_range, direction, sh_row, index)[0]

				for gaia_row in ewcfg.gvs_valid_coords_gaia:
					if checked_coord in gaia_row:
						# Check coordinate for gaiaslimeoids in front of the shambler.
						gaia_data = bknd_core.execute_sql_query(
							"SELECT {id_enemy}, {enemytype} FROM enemies WHERE {enemyclass} = %s AND {gvs_coord} = %s AND {poi} = %s AND {id_server} = %s AND NOT ({life_state} = {life_state_dead})".format(
								id_enemy=ewcfg.col_id_enemy,
								enemyclass=ewcfg.col_enemy_class,
								enemytype=ewcfg.col_enemy_type,
								gvs_coord=ewcfg.col_enemy_gvs_coord,
								poi=ewcfg.col_poi,
								id_server=ewcfg.col_id_server,
								life_state=ewcfg.col_life_state,
								life_state_dead=ewcfg.enemy_lifestate_dead,
							), (
								ewcfg.enemy_class_gaiaslimeoid,
								checked_coord,
								enemy_data.poi,
								enemy_data.id_server
							))

						# print(len(gaia_data))
						if len(gaia_data) > 0:

							low_attack_priority = [ewcfg.enemy_type_gaia_rustealeaves]
							high_attack_priority = [ewcfg.enemy_type_gaia_steelbeans]
							mid_attack_priority = []
							for enemy_id in ewcfg.gvs_enemies_gaiaslimeoids:
								if enemy_id not in low_attack_priority and enemy_id not in high_attack_priority:
									mid_attack_priority.append(enemy_id)

							gaia_types = {}
							for gaia in gaia_data:
								gaia_types[gaia[1]] = gaia[0]

							# Rustea Leaves only have a few opposing shamblers that can damage them
							if ewcfg.enemy_type_gaia_rustealeaves in gaia_types.keys() and enemy_data.enemytype not in [
								ewcfg.enemy_type_gigashambler, ewcfg.enemy_type_shambonidriver,
								ewcfg.enemy_type_ufoshambler]:
								del gaia_types[ewcfg.enemy_type_gaia_rustealeaves]

							for target in high_attack_priority:
								if target in gaia_types.keys():
									gaias_in_coord.append(gaia_types[target])

							for target in mid_attack_priority:
								if target in gaia_types.keys():
									gaias_in_coord.append(gaia_types[target])

							for target in low_attack_priority:
								if target in gaia_types.keys():
									gaias_in_coord.append(gaia_types[target])

					# print('shambler in coord {} found gaia in coord {} in {}.'.format(current_coord, checked_coord, enemy_data.poi))

	return gaias_in_coord


def gvs_grid_gather_coords(enemyclass, gr_range, direction, row, index):
	checked_coords = []

	if enemyclass == ewcfg.enemy_class_shambler:
		index_change = -2
		if direction == 'right':
			index_change *= -1

		try:
			checked_coords.append(row[index + index_change])
		except:
			pass

	else:

		index_changes = []

		# Default if range is 1, only reaches 0.5 and 1 full tile ahead
		for i in range(gr_range):
			index_changes.append(i + 1)

		# If it reaches backwards with a range of 1, reflect current index changes
		if direction == 'left':
			new_index_changes = []

			for change in index_changes:
				change *= -1
				new_index_changes.append(change)

			index_changes = new_index_changes

		# If it reaches both directions with a range of 1, add in opposite tiles.
		elif direction == 'frontandback':
			new_index_changes = []

			for change in index_changes:
				change *= -1
				new_index_changes.append(change)

			index_changes += new_index_changes

		# If it attacks in a ring formation around itself, there are no coord changes.
		# The proper coordinates will be fetched later as 'splash' damage.
		elif direction == 'ring':
			index_changes = [0]

		# Catch exceptions when necessary
		for index_change in index_changes:
			try:
				checked_coords.append(row[index + index_change])
			except:
				pass

	# print(index_changes)

	# print(gr_range)
	# print(checked_coords)
	# print(enemyclass)

	return checked_coords


def gvs_find_nearest_shambler(checked_coords, detected_shamblers, pierceamount=1, singletilepierce='false'):
	pierceattempts = 0
	current_dict = {}
	chosen_coord = ''

	for coord in checked_coords:
		for shambler in detected_shamblers.keys():
			if detected_shamblers[shambler] == coord:
				current_dict[shambler] = coord

				if singletilepierce == 'true':
					chosen_coord = coord
					for shambler in detected_shamblers.keys():
						if detected_shamblers[shambler] == chosen_coord:
							current_dict[shambler] = chosen_coord
						pierceattempts += 1
						if pierceattempts == pierceamount:
							return current_dict

			pierceattempts += 1
			if pierceattempts == pierceamount:
				return current_dict


def gvs_get_splash_coords(checked_splash_coords):
	# Grab any random coordinate from the supplied splash coordinates, then get the row that it's in.
	plucked_coord = checked_splash_coords[0]
	plucked_row = plucked_coord[0]
	top_row = None
	middle_row = None
	bottom_row = None

	extra_top_row = None  # Joybean Pawpaw
	extra_bottom_row = None  # Joybean Pawpaw
	row_range = 5  # Joybean Dankwheat = 9
	row_backpedal = 2  # Joybean Dankwheat = 4

	current_index = 0

	all_splash_coords = []
	if plucked_row == 'A':
		middle_row = 0
		bottom_row = 1
	elif plucked_row == 'B':
		top_row = 0
		middle_row = 1
		bottom_row = 2
	elif plucked_row == 'C':
		top_row = 1
		middle_row = 2
		bottom_row = 3
	elif plucked_row == 'D':
		top_row = 2
		middle_row = 3
		bottom_row = 4
	elif plucked_row == 'E':
		top_row = 3
		middle_row = 4

	for coord in checked_splash_coords:
		for sh_row in ewcfg.gvs_valid_coords_shambler:
			if coord in sh_row:
				current_index = sh_row.index(coord)
				break

		if top_row != None:
			for i in range(row_range):
				try:
					all_splash_coords.append(
						ewcfg.gvs_valid_coords_shambler[top_row][current_index - row_backpedal + i])
				except:
					pass
		if bottom_row != None:
			for i in range(row_range):
				try:
					all_splash_coords.append(
						ewcfg.gvs_valid_coords_shambler[bottom_row][current_index - row_backpedal + i])
				except:
					pass

		for i in range(row_range):
			try:
				all_splash_coords.append(ewcfg.gvs_valid_coords_shambler[middle_row][current_index - row_backpedal + i])
			except:
				pass

	return all_splash_coords

