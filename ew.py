import time

import ewutils
import ewcfg
import ewstats
import ewitem
import ewstatuseffects
from ewstatuseffects import EwStatusEffect

""" User model for database persistence """
class EwUser:
	id_user = ""
	id_server = ""
	id_killer = ""

	slimes = 0
	slimecoin = 0
	slimelevel = 1
	hunger = 0
	totaldamage = 0
	bleed_storage = 0
	bounty = 0
	weapon = ""
	weaponskill = 0
	trauma = ""
	ghostbust = False
	inebriation = 0
	faction = ""
	poi = ""
	life_state = 0
	busted = False
	rr_challenger = ""
	time_last_action = 0
	weaponmarried = False

	time_lastkill = 0
	time_lastrevive = 0
	time_lastspar = 0
	time_lasthaunt = 0
	time_lastinvest = 0
	time_lastscavenge = 0
	time_lastenter = 0
	time_lastoffline = 0
	time_joined = 0

	""" fix data in this object if it's out of acceptable ranges """
	def limit_fix(self):
		if self.hunger > ewutils.hunger_max_bylevel(self.slimelevel):
			self.hunger = ewutils.hunger_max_bylevel(self.slimelevel)

		if self.inebriation < 0:
			self.inebriation = 0

		if self.poi == '':
			self.poi = ewcfg.poi_id_downtown

		if self.time_last_action <= 0:
			self.time_last_action = int(time.time())
			
	""" gain or lose slime, recording statistics and potentially leveling up. """
	def change_slimes(self, n = 0, source = None):
		change = int(n)
		self.slimes += change

		if n >= 0:
			ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimes, n = change)
			ewstats.track_maximum(user = self, metric = ewcfg.stat_max_slimes, value = self.slimes)

			if source == ewcfg.source_mining:
				ewstats.change_stat(user = self, metric = ewcfg.stat_slimesmined, n = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimesmined, n = change)

			if source == ewcfg.source_killing:
				ewstats.change_stat(user = self, metric = ewcfg.stat_slimesfromkills, n = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimesfromkills, n = change)

			if source == ewcfg.source_farming:
				ewstats.change_stat(user = self, metric = ewcfg.stat_slimesfarmed, n = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimesfarmed, n = change)

			if source == ewcfg.source_scavenging:
				ewstats.change_stat(user = self, metric = ewcfg.stat_slimesscavenged, n = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimesscavenged, n = change)

		else:
			change *= -1 # convert to positive number
			if source != ewcfg.source_spending and source != ewcfg.source_ghostification:
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimeloss, n = change)

			if source == ewcfg.source_damage or source == ewcfg.source_bleeding:
				self.totaldamage += change
				ewstats.track_maximum(user = self, metric = ewcfg.stat_max_hitsurvived, value = change)

			if source == ewcfg.source_self_damage:
				self.totaldamage += change
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_selfdamage, n = change)

			if source == ewcfg.source_decay:
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimesdecayed, n = change)

			if source == ewcfg.source_haunter:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_max_hauntinflicted, value = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimeshaunted, n = change)

		# potentially level up
		new_level = ewutils.level_byslime(self.slimes)
		if new_level > self.slimelevel:
			self.slimelevel = new_level
			if self.life_state == ewcfg.life_state_corpse:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_max_ghost_level, value = self.slimelevel)
			else:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_max_level, value = self.slimelevel)

	def die(self, cause = None):
		if cause == ewcfg.cause_busted:
			self.busted = True
		else:
			self.busted = False  # reset busted state on normal death; potentially move this to ewspooky.revive
			self.life_state = ewcfg.life_state_corpse
			ewstats.increment_stat(user = self, metric = ewcfg.stat_lifetime_deaths)
			ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimeloss, n = self.slimes)
			if cause != ewcfg.cause_killing and cause != ewcfg.cause_suicide and cause != ewcfg.cause_bleeding:
				ewstats.increment_stat(user = self, metric = ewcfg.stat_lifetime_pve_deaths)
		ewitem.item_dedorn_cosmetics(id_server = self.id_server, id_user = self.id_user)
		ewitem.item_dropall(id_server = self.id_server, id_user = self.id_user)
		self.slimes = 0
		self.poi = ewcfg.poi_id_thesewers
		self.bounty = 0
		self.totaldamage = 0
		self.bleed_storage = 0
		self.slimelevel = 1
		self.hunger = 0
		self.inebriation = 0
		self.ghostbust = False
		# Clear weapon and weaponskill.
		self.weapon = ""
		self.weaponskill = 0
		self.weaponmarried = False
		ewutils.moves_active[self.id_user] = 0
		ewutils.weaponskills_clear(id_server = self.id_server, id_user = self.id_user)
		ewstats.clear_on_death(id_server = self.id_server, id_user = self.id_user)
		#ewitem.item_destroyall(id_server = self.id_server, id_user = self.id_user)

		statuses = self.getStatusEffects()

		for status in statuses:
			self.clear_status(id_status=status)

		ewutils.logMsg('server {}: {} was killed by {} - cause was {}'.format(self.id_server, self.id_user, self.id_killer, cause))

	def add_bounty(self, n = 0):
		self.bounty += int(n)
		ewstats.track_maximum(user = self, metric = ewcfg.stat_max_bounty, value = self.bounty)

	def change_slimecoin(self, n = 0, coinsource = None):
		change = int(n)
		self.slimecoin += change

		if change >= 0:
			ewstats.track_maximum(user = self, metric = ewcfg.stat_max_slimecoin, value = self.slimecoin)
			ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimecoin, n = change)
			if coinsource == ewcfg.coinsource_bounty:
				ewstats.change_stat(user = self, metric = ewcfg.stat_bounty_collected, n = change)
			if coinsource == ewcfg.coinsource_casino:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_biggest_casino_win, value = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_casino_winnings, n = change)
			if coinsource == ewcfg.coinsource_withdraw:
				ewstats.change_stat(user = self, metric = ewcfg.stat_total_slimecoin_withdrawn, n = change)
		else:
			change *= -1
			if coinsource == ewcfg.coinsource_revival:
				ewstats.change_stat(user = self, metric = ewcfg.stat_slimecoin_spent_on_revives, n = change)
			if coinsource == ewcfg.coinsource_casino:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_biggest_casino_loss, value = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_casino_losses, n = change)
			if coinsource == ewcfg.coinsource_invest:
				ewstats.change_stat(user = self, metric = ewcfg.stat_total_slimecoin_invested, n = change)

	def add_weaponskill(self, n = 0, weapon_type = None):
		# Save the current weapon's skill
		if self.weapon != None and self.weapon != "":
			if self.weaponskill == None:
				self.weaponskill = 0

			self.weaponskill += int(n)
			ewstats.track_maximum(user = self, metric = ewcfg.stat_max_wepskill, value = self.weaponskill)

			ewutils.weaponskills_set(
				id_server = self.id_server,
				id_user = self.id_user,
				weapon = weapon_type,
				weaponskill = self.weaponskill
			)

	def eat(self, food_item = None):
		item_props = food_item.item_props

		if float(food_item.time_expir if food_item.time_expir is not None else 0) < time.time():
			response = "You realize that the food you were trying to eat is already spoiled. In disgust, you throw it away."
		else:
			resp_status = ""
			self.hunger -= int(item_props['recover_hunger'])
			if self.hunger < 0:
				self.hunger = 0
			self.inebriation += int(item_props['inebriation'])
			if self.inebriation > 20:
				self.inebriation = 20
			if self.inebriation >= 10:
				resp_status = "\n" + self.applyStatus(id_status=ewcfg.status_drunk_id)
						
			try:
				if item_props['id_food'] == "coleslaw":
					self.applyStatus(id_status=ewcfg.status_ghostbust_id)
					#Bust player if they're a ghost
					if self.life_state == ewcfg.life_state_corpse:
						self.die(cause = ewcfg.cause_busted)
			except:
				# An exception will occur if there's no id_food prop in the database. We don't care.
				pass

			response = item_props['str_eat'] + ("\n\nYou're stuffed!" if self.hunger <= 0 else "")

			if resp_status:
				response += resp_status	

		ewitem.item_delete(food_item.id_item)

		return response

	def equip(self, weapon_item = None):
		if self.life_state == ewcfg.life_state_corpse:
			response = "Ghosts can't equip weapons."
		elif self.life_state == ewcfg.life_state_juvenile:
			response = "Juvies can't equip weapons."
		elif self.weaponmarried == True:
			current_weapon = ewitem.EwItem(id_item = self.weapon)
			response = "You reach to pick up a new weapon, but your old {} remains motionless with jealousy. You dug your grave, now decompose in it.".format(current_weapon.item_props.get("weapon_name") if len(current_weapon.item_props.get("weapon_name")) > 0 else "partner")
		else:
			response = "You equip your " + (weapon_item.item_props.get("weapon_type") if len(weapon_item.item_props.get("weapon_name")) == 0 else weapon_item.item_props.get("weapon_name"))
			self.weapon = weapon_item.id_item

		return response

	def getStatusEffects(self):
		values = []

		try:
			data = ewutils.execute_sql_query("SELECT {id_status} FROM status_effects WHERE {id_server} = %s and {id_user} = %s".format(
				id_status = ewcfg.col_id_status,
				id_server = ewcfg.col_id_server,
				id_user = ewcfg.col_id_user
			), (
				self.id_server,
				self.id_user
			))

			for row in data:
				values.append(row[0])

		except:
			pass
		finally:
			return values

	def applyStatus(self, id_status = None, value = 0, source = 0):
		response = ""
		if id_status != None:
			status = None

			status = ewcfg.status_effects_map.get(id_status)

			if status != None:
				statuses = self.getStatusEffects()

				status_effect = EwStatusEffect(id_status=id_status, user_data=self, time_expire=status.time_expire, value=value, source=source)

				if id_status in statuses:
					status_effect.value = value

					if status.time_expire > 0 and id_status in ewcfg.stackable_status_effects:
						status_effect.time_expire += status.time_expire
						response = status.str_acquire

					status_effect.persist() 
				else:
					response = status.str_acquire
					

		return response		

	def clear_status(self, id_status = None):
		if id_status != None:
			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Save the object.
				cursor.execute("DELETE FROM status_effects WHERE {id_status} = %s and {id_user} = %s and {id_server} = %s".format(
					id_status = ewcfg.col_id_status,
					id_user = ewcfg.col_id_user,
					id_server = ewcfg.col_id_server
				), (
					id_status,
					self.id_user,
					self.id_server
				))

				conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Create a new EwUser and optionally retrieve it from the database. """
	def __init__(self, member = None, id_user = None, id_server = None):
		if(id_user == None) and (id_server == None):
			if(member != None):
				id_server = member.server.id
				id_user = member.id

		# Retrieve the object from the database if the user is provided.
		if(id_user != None) and (id_server != None):
			self.id_server = id_server
			self.id_user = id_user

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute("SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM users WHERE id_user = %s AND id_server = %s".format(
					ewcfg.col_slimes,
					ewcfg.col_slimelevel,
					ewcfg.col_hunger,
					ewcfg.col_totaldamage,
					ewcfg.col_bounty,
					ewcfg.col_weapon,
					ewcfg.col_trauma,
					ewcfg.col_slimecoin,
					ewcfg.col_time_lastkill,
					ewcfg.col_time_lastrevive,
					ewcfg.col_id_killer,
					ewcfg.col_time_lastspar,
					ewcfg.col_time_lasthaunt,
					ewcfg.col_time_lastinvest,
					ewcfg.col_ghostbust,
					ewcfg.col_inebriation,
					ewcfg.col_faction,
					ewcfg.col_poi,
					ewcfg.col_life_state,
					ewcfg.col_busted,
					ewcfg.col_rrchallenger,
					ewcfg.col_time_last_action,
					ewcfg.col_weaponmarried,
					ewcfg.col_time_lastscavenge,
					ewcfg.col_bleed_storage,
					ewcfg.col_time_lastenter,
					ewcfg.col_time_lastoffline,
					ewcfg.col_time_joined
				), (
					id_user,
					id_server
				))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.slimes = result[0]
					self.slimelevel = result[1]
					self.hunger = result[2]
					self.totaldamage = result[3]
					self.bounty = result[4]
					self.weapon = result[5]
					self.trauma = result[6]
					self.slimecoin = result[7]
					self.time_lastkill = result[8]
					self.time_lastrevive = result[9]
					self.id_killer = result[10]
					self.time_lastspar = result[11]
					self.time_lasthaunt = result[12]
					self.time_lastinvest = result[13]
					self.ghostbust = (result[14] == 1)
					self.inebriation = result[15]
					self.faction = result[16]
					self.poi = result[17]
					self.life_state = result[18]
					self.busted = (result[19] == 1)
					self.rr_challenger = result[20]
					self.time_last_action = result[21]
					self.weaponmarried = (result[22] == 1)
					self.time_lastscavenge = result[23]
					self.bleed_storage = result[24]
					self.time_lastenter = result[25]
					self.time_lastoffline = result[26]
					self.time_joined = result[27]
				else:
					self.poi = ewcfg.poi_id_downtown
					self.life_state = ewcfg.life_state_juvenile
					# Create a new database entry if the object is missing.
					cursor.execute("REPLACE INTO users(id_user, id_server, poi, life_state) VALUES(%s, %s, %s, %s)", (
						id_user,
						id_server,
						ewcfg.poi_id_downtown,
						ewcfg.life_state_juvenile
					))
					
					conn.commit()

				if (self.time_joined == 0) and (member != None) and (member.joined_at != None):
					self.time_joined = int(member.joined_at.timestamp())

				# Get the skill for the user's current weapon.
				if self.weapon != None and self.weapon != "":
					skills = ewutils.weaponskills_get(
						id_server = id_server,
						id_user = id_user
					)

					weapon_item = ewitem.EwItem(id_item = self.weapon)

					skill_data = skills.get(weapon_item.item_props.get("weapon_type"))
					if skill_data != None:
						self.weaponskill = skill_data['skill']
					else:
						self.weaponskill = 0

					if self.weaponskill == None:
						self.weaponskill = 0
				else:
					self.weaponskill = 0

				self.limit_fix();
			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save this user object to the database. """
	def persist(self):
	
		try:
			# Get database handles if they weren't passed.
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			self.limit_fix();

			# Save the object.
			# Todo Preserve Farming Data 	farmActive, plantType, time_lastsow
			cursor.execute("REPLACE INTO users({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
				ewcfg.col_id_user,
				ewcfg.col_id_server,
				ewcfg.col_slimes,
				ewcfg.col_slimelevel,
				ewcfg.col_hunger,
				ewcfg.col_totaldamage,
				ewcfg.col_bounty,
				ewcfg.col_weapon,
				ewcfg.col_weaponskill,
				ewcfg.col_trauma,
				ewcfg.col_slimecoin,
				ewcfg.col_time_lastkill,
				ewcfg.col_time_lastrevive,
				ewcfg.col_id_killer,
				ewcfg.col_time_lastspar,
				ewcfg.col_time_lasthaunt,
				ewcfg.col_time_lastinvest,
				ewcfg.col_ghostbust,
				ewcfg.col_inebriation,
				ewcfg.col_faction,
				ewcfg.col_poi,
				ewcfg.col_life_state,
				ewcfg.col_busted,
				ewcfg.col_rrchallenger,
				ewcfg.col_time_last_action,
				ewcfg.col_weaponmarried,
				ewcfg.col_time_lastscavenge,
				ewcfg.col_bleed_storage,
				ewcfg.col_time_lastenter,
				ewcfg.col_time_lastoffline,
				ewcfg.col_time_joined
			), (
				self.id_user,
				self.id_server,
				self.slimes,
				self.slimelevel,
				self.hunger,
				self.totaldamage,
				self.bounty,
				self.weapon,
				self.weaponskill,
				self.trauma,
				self.slimecoin,
				self.time_lastkill,
				self.time_lastrevive,
				self.id_killer,
				self.time_lastspar,
				self.time_lasthaunt,
				self.time_lastinvest,
				(1 if self.ghostbust else 0),
				self.inebriation,
				self.faction,
				self.poi,
				self.life_state,
				(1 if self.busted else 0),
				self.rr_challenger,
				self.time_last_action,
				(1 if self.weaponmarried else 0),
				self.time_lastscavenge,
				self.bleed_storage,
				self.time_lastenter,
				self.time_lastoffline,
				self.time_joined
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

