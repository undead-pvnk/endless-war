import time
import random

from ew.backend.user import EwUserBase
from ew.utils import core as ewutils, rolemgr as ewrolemgr, district as bknd_district, stats as ewstats
from ew.utils import frontend as fe_utils
from ew.utils import event as evt_utils
from ew.static import cfg as ewcfg
from ew.static import weapons as static_weapons
from ew.static import poi as poi_static
from ew.static import mutations as static_mutations
from ew import item as ewitem
from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend import status as bknd_status

from ew.utils.frontend import EwResponseContainer
from ew.backend.market import EwMarket

""" User model for database persistence """
class EwUser(EwUserBase):
	move_speed = 1 # not a database column

	weaponskill = 0

	attack = 0
	defense = 0
	speed = 0
	freshness = 0

	def __init__(self, ew_id=None, member=None, id_user=None, id_server=None, data_level=0):
		super().__init__(ew_id, member, id_user, id_server)

		self.weaponskill = bknd_item.get_weaponskill(self)

		if data_level > 0:
			result = self.get_fashion_stats()
			self.attack = result[0]
			self.defense = result[1]
			self.speed = result[2]

			if data_level > 1:
				self.freshness = self.get_freshness()

			self.move_speed = get_move_speed(self)

		self.limit_fix()

	""" gain or lose slime, recording statistics and potentially leveling up. """
	def change_slimes(self, n = 0, source = None):
		change = int(n)
		self.slimes += change
		#if self.life_state == ewcfg.life_state_juvenile:
		#
		#	if self.juviemode == 1 and self.slimes > ewcfg.max_safe_slime:
		#		self.slimes = ewcfg.max_safe_slime

		response = ""

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
			if self.life_state != ewcfg.life_state_corpse:
				response += "You have been empowered by slime and are now a level {} slimeboi.".format(new_level)
			for level in range(self.slimelevel+1, new_level+1):
				current_mutations = self.get_mutations()
				if (level >= self.get_mutation_level() + self.get_mutation_next_level()) and (self.life_state not in [ewcfg.life_state_corpse, ewcfg.life_state_shambler]) and (self.get_mutation_level() < 50):
					
					new_mutation = self.get_mutation_next()

					add_success = self.add_mutation(new_mutation)
					if add_success:
						response += "\n\nWhat’s this? You are mutating!! {}".format(static_mutations.mutations_map[new_mutation].str_acquire)
						
			self.slimelevel = new_level
			if self.life_state == ewcfg.life_state_corpse:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_max_ghost_level, value = self.slimelevel)
			else:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_max_level, value = self.slimelevel)

		return response

		
	def die(self, cause = None):


		time_now = int(time.time())

		ewutils.end_trade(self.id_user)

		resp_cont = EwResponseContainer(id_server = self.id_server)



		client = ewcfg.get_client()
		server = client.get_guild(self.id_server)

		deathreport = ''
		
		# remove ghosts inhabiting player
		self.remove_inhabitation()

		# Make The death report
		deathreport = fe_utils.create_death_report(cause = cause, user_data = self)
		resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)


		poi = poi_static.id_to_poi.get(self.poi)
		if cause == ewcfg.cause_weather:
			resp_cont.add_channel_response(poi.channel, deathreport)

		status = self.getStatusEffects()
		if "n1" in status:
			self.change_slimes(n=-self.slimes, source=ewcfg.source_killing)
			return(resp_cont)

		# Grab necessary data for spontaneous combustion before stat reset
		explosion_block_list = [ewcfg.cause_leftserver, ewcfg.cause_cliff]
		user_hasCombustion = False
		if (cause not in explosion_block_list) and (poi.pvp):
			if ewcfg.mutation_id_spontaneouscombustion in self.get_mutations():
				user_hasCombustion = True
				explode_damage = ewutils.slime_bylevel(self.slimelevel) / 5
				explode_district = bknd_district.EwDistrict(district = self.poi, id_server = self.id_server)
				explode_poi_channel = poi_static.id_to_poi.get(self.poi).channel

		if self.life_state == ewcfg.life_state_corpse:
			self.busted = True
			self.poi = ewcfg.poi_id_thesewers
			#self.slimes = int(self.slimes * 0.9)
		else:
			if cause != ewcfg.cause_suicide or self.slimelevel > 10:
				self.rand_seed = random.randrange(500000)

			if ewcfg.mutation_id_rigormortis in self.get_mutations():
				rigor = True
			else:
				rigor = False

			self.busted = False  # reset busted state on normal death; potentially move this to ewspooky.revive
			self.slimes = 0
			self.slimelevel = 1
			self.clear_mutations()
			self.clear_allstatuses()
			self.totaldamage = 0
			self.bleed_storage = 0
			self.hunger = 0
			self.inebriation = 0
			self.bounty = 0
			self.time_lastdeath = time_now



	
			# if self.life_state == ewcfg.life_state_shambler:
			# 	self.degradation += 1
			# else:
			# 	self.degradation += 5

			ewstats.increment_stat(user = self, metric = ewcfg.stat_lifetime_deaths)
			ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_slimeloss, n = self.slimes)

			if cause == ewcfg.cause_cliff:
				pass
			else:
				if self.life_state == ewcfg.life_state_juvenile: # If you were a Juvenile.
					item_fraction = 4
					food_fraction = 4
					cosmetic_fraction = 4

					# Remove them from Garden Ops where applicable
					bknd_core.execute_sql_query("DELETE FROM gvs_ops_choices WHERE id_user = {}".format(self.id_user))

				else:  # If you were a Gangster.
					item_fraction = 2
					food_fraction = 2
					cosmetic_fraction = 2

				ewitem.item_dropsome(id_server = self.id_server, id_user = self.id_user, item_type_filter = ewcfg.it_item, fraction = item_fraction, rigor=rigor) # Drop a random fraction of your items on the ground.
				ewitem.item_dropsome(id_server = self.id_server, id_user = self.id_user, item_type_filter = ewcfg.it_food, fraction = food_fraction, rigor=rigor) # Drop a random fraction of your food on the ground.

				ewitem.item_dropsome(id_server = self.id_server, id_user = self.id_user, item_type_filter = ewcfg.it_cosmetic, fraction = cosmetic_fraction, rigor=rigor) # Drop a random fraction of your unadorned cosmetics on the ground.
				bknd_item.item_dedorn_cosmetics(id_server = self.id_server, id_user = self.id_user) # Unadorn all of your adorned hats.

				ewitem.item_dropsome(id_server = self.id_server, id_user = self.id_user, item_type_filter = ewcfg.it_weapon, fraction = 1, rigor=rigor) # Drop random fraction of your unequipped weapons on the ground.
				ewutils.weaponskills_clear(id_server = self.id_server, id_user = self.id_user, weaponskill = ewcfg.weaponskill_max_onrevive)

			try:
				bknd_core.execute_sql_query(
					"DELETE FROM items_prop WHERE {} = %s AND  {} = %s".format(
						ewcfg.col_name,
						ewcfg.col_value
					),
					(
						'preserved',
						self.id_user
					))

			except:
				ewutils.logMsg('Failed to remove preserved tags from items.')

			self.life_state = ewcfg.life_state_corpse
			self.poi_death = self.poi
			self.poi = ewcfg.poi_id_thesewers
			self.weapon = -1
			self.sidearm = -1
			self.time_expirpvp = 0

		if cause == ewcfg.cause_killing_enemy:  # If your killer was an Enemy. Duh.
			ewstats.increment_stat(user = self, metric = ewcfg.stat_lifetime_pve_deaths)

		if cause == ewcfg.cause_leftserver:
			bknd_item.item_dropall(self)

		#self.sap = 0
		#self.hardened_sap = 0
		self.attack = 0
		self.defense = 0
		self.speed = 0

		ewutils.moves_active[self.id_user] = 0
		ewutils.active_target_map[self.id_user] = ""
		ewutils.active_restrictions[self.id_user] = 0
		ewstats.clear_on_death(id_server = self.id_server, id_user = self.id_user)

		self.persist()

		if cause not in explosion_block_list: # Run explosion after location/stat reset, to prevent looping onto self
			if user_hasCombustion:
				explode_resp = "\n{} spontaneously combusts, horribly dying in a fiery explosion of slime and shrapnel!! Oh, the humanity!\n".format(server.get_member(self.id_user).display_name)
				ewutils.logMsg("")
				resp_cont.add_channel_response(explode_poi_channel, explode_resp)

				explosion = evt_utils.explode(damage = explode_damage, district_data = explode_district)
				resp_cont.add_response_container(explosion)

		#bknd_item.item_destroyall(id_server = self.id_server, id_user = self.id_user)

		ewutils.logMsg('server {}: {} was killed by {} - cause was {}'.format(self.id_server, self.id_user, self.id_killer, cause))

		return(resp_cont)

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
			if coinsource == ewcfg.coinsource_recycle:
				ewstats.change_stat(user = self, metric = ewcfg.stat_total_slimecoin_from_recycling, n = change)
		else:
			change *= -1
			if coinsource == ewcfg.coinsource_revival:
				ewstats.change_stat(user = self, metric = ewcfg.stat_slimecoin_spent_on_revives, n = change)
			if coinsource == ewcfg.coinsource_casino:
				ewstats.track_maximum(user = self, metric = ewcfg.stat_biggest_casino_loss, value = change)
				ewstats.change_stat(user = self, metric = ewcfg.stat_lifetime_casino_losses, n = change)
			if coinsource == ewcfg.coinsource_invest:
				ewstats.change_stat(user = self, metric = ewcfg.stat_total_slimecoin_invested, n = change)
			if coinsource == ewcfg.coinsource_swearjar:
				ewstats.change_stat(user = self, metric = ewcfg.stat_total_slimecoin_from_swearing, n = change)
			if coinsource == ewcfg.coinsource_salary:
				ewstats.change_stat(user = self, metric = ewcfg.stat_total_slimecoin_from_salary, n = change)


	def add_weaponskill(self, n = 0, weapon_type = None):
		# Save the current weapon's skill
		if self.weapon != None and self.weapon >= 0:
			if self.weaponskill == None:
				self.weaponskill = 0

			self.weaponskill += int(n)
			ewstats.track_maximum(user = self, metric = ewcfg.stat_max_wepskill, value = self.weaponskill)

			weapon = static_weapons.weapon_map.get(weapon_type)
			if ewcfg.weapon_class_paint in weapon.classes and self.weaponskill > 16:
				self.weaponskill = 16

			ewutils.weaponskills_set(
				id_server = self.id_server,
				id_user = self.id_user,
				weapon = weapon_type,
				weaponskill = self.weaponskill
			)

	def divide_weaponskill(self, fraction = 0, weapon_type = None):
		# Save the current weapon's skill.
		if self.weapon != None and self.weapon >= 0:
			if self.weaponskill == None:
				self.weaponskill = 0

			new_weaponskill = int(self.weaponskill / fraction)

			ewutils.weaponskills_set(
				id_server = self.id_server,
				id_user = self.id_user,
				weapon = weapon_type,
				weaponskill = new_weaponskill
			)

	def eat(self, food_item = None):
		item_props = food_item.item_props
		mutations = self.get_mutations()
		statuses = self.getStatusEffects()

		# Find out if the item is perishable
		if item_props.get('perishable') != None:
			perishable_status = item_props.get('perishable')
			if perishable_status == 'true' or perishable_status == '1':
				item_is_non_perishable = False
			else:
				item_is_non_perishable = True
		else:
			item_is_non_perishable = False
			
		user_has_spoiled_appetite = ewcfg.mutation_id_spoiledappetite in mutations
		item_has_expired = float(getattr(food_item, "time_expir", 0)) < time.time()
		if item_has_expired and not (user_has_spoiled_appetite or item_is_non_perishable):
			response = "You realize that the food you were trying to eat is already spoiled. Ugh, not eating that."
			#ewitem.item_drop(food_item.id_item)
		else:
			hunger_restored = int(item_props['recover_hunger'])
			if self.id_user in ewutils.food_multiplier and ewutils.food_multiplier.get(self.id_user) > 0:
				if ewcfg.mutation_id_bingeeater in mutations:
					hunger_restored *= ewutils.food_multiplier.get(self.id_user)
					if ewutils.food_multiplier.get(self.id_user) >= 5 and ewcfg.status_foodcoma_id not in self.getStatusEffects():
						self.applyStatus(id_status=ewcfg.status_foodcoma_id, source=self.id_user, id_target=self.id_user)
				ewutils.food_multiplier[self.id_user] += 1
			else:
				ewutils.food_multiplier[self.id_user] = 1

			if ewcfg.status_high_id in statuses:
				hunger_restored *= 0.5			
	
			hunger_restored = round(hunger_restored)

			self.hunger -= hunger_restored
			if self.hunger < 0:
				self.hunger = 0
			self.inebriation += int(item_props['inebriation'])
			if self.inebriation > 20:
				self.inebriation = 20
						
			try:
				if item_props['id_food'] in ["coleslaw","bloodcabbagecoleslaw"]:
					self.clear_status(id_status = ewcfg.status_ghostbust_id)
					self.applyStatus(id_status = ewcfg.status_ghostbust_id)
					#Bust player if they're a ghost
					if self.life_state == ewcfg.life_state_corpse:
						self.die(cause = ewcfg.cause_busted)
				if item_props['id_food'] == ewcfg.item_id_seaweedjoint:
					self.applyStatus(id_status = ewcfg.status_high_id)

			except:
				# An exception will occur if there's no id_food prop in the database. We don't care.
				pass

			response = item_props['str_eat'] + ("\n\nYou're stuffed!" if self.hunger <= 0 else "")


			bknd_item.item_delete(food_item.id_item)

		return response


	def add_mutation(self, id_mutation, is_artificial = 0):
		mutations = self.get_mutations()
		if id_mutation in mutations:
			return False
		try:
			bknd_core.execute_sql_query("REPLACE INTO mutations({id_server}, {id_user}, {id_mutation}, {tier}, {artificial}) VALUES (%s, %s, %s, %s, %s)".format(
					id_server = ewcfg.col_id_server,
					id_user = ewcfg.col_id_user,
					id_mutation = ewcfg.col_id_mutation,
					tier = ewcfg.col_tier,
					artificial = ewcfg.col_artificial
				),(
					self.id_server,
					self.id_user,
					id_mutation,
					static_mutations.mutations_map.get(id_mutation).tier,
					is_artificial
				))

			return True
		except:
			ewutils.logMsg("Failed to add mutation for user {}.".format(self.id_user))
			return False


	def clear_mutations(self):
		try:
			bknd_core.execute_sql_query("DELETE FROM mutations WHERE {id_server} = %s AND {id_user} = %s".format(
					id_server = ewcfg.col_id_server,
					id_user = ewcfg.col_id_user
				),(
					self.id_server,
					self.id_user
				))
		except:
			ewutils.logMsg("Failed to clear mutations for user {}.".format(self.id_user))

	def get_mutation_level(self):
		result = 0

		try:
			tiers = bknd_core.execute_sql_query(
				"SELECT SUM({tier}) FROM mutations WHERE {id_server} = %s AND {id_user} = %s;".format(
					tier = ewcfg.col_tier,
					id_server=ewcfg.col_id_server,
					id_user=ewcfg.col_id_user,

				), (
					self.id_server,
					self.id_user
				))

			for tier_data in tiers:
				result = tier_data[0]


			if result is None:
				result = 0

			#random.seed(self.rand_seed + mutation_dat)

		except:
			ewutils.logMsg("Failed to fetch mutations for user {}.".format(self.id_user))

		finally:
			return result


	def get_mutation_next_level(self):
		next_mutation = self.get_mutation_next()
		next_mutation_obj = static_mutations.mutations_map.get(next_mutation)
		if next_mutation_obj != None:
			return next_mutation_obj.tier
		else:
			return 50


	def get_mutation_next(self):
		counter = 0
		result = ""
		current_mutations = self.get_mutations()

		if self.get_mutation_level() >= 50:
			return 0

		seed = int(self.rand_seed)
		try:
			counter_data = bknd_core.execute_sql_query(
				"SELECT SUM({mutation_counter}) FROM mutations WHERE {id_server} = %s AND {id_user} = %s;".format(
					mutation_counter=ewcfg.col_mutation_counter,
					id_server=ewcfg.col_id_server,
					id_user=ewcfg.col_id_user,

				), (
					self.id_server,
					self.id_user
				))

			for ids in counter_data:
				counter = ids[0]
			if counter == None:
				counter = 0
			random.seed(counter + seed)

			for x in range(1000):
				result = random.choice(list(static_mutations.mutation_ids))

				if result == ewcfg.mutation_id_airlock:
					if ewcfg.mutation_id_whitenationalist in current_mutations or ewcfg.mutation_id_lightasafeather in current_mutations:
						continue
				if result in [ewcfg.mutation_id_lightasafeather, ewcfg.mutation_id_whitenationalist]:
					if ewcfg.mutation_id_airlock in current_mutations:
						continue
				if result == ewcfg.mutation_id_onemansjunk:
					if ewcfg.mutation_id_davyjoneskeister in current_mutations:
						continue
				if result == ewcfg.mutation_id_davyjoneskeister:
					if ewcfg.mutation_id_onemansjunk in current_mutations:
						continue

				if result not in current_mutations and static_mutations.mutations_map[result].tier + self.get_mutation_level() <= 50:
					return result

			result = ""

		except:
			ewutils.logMsg("Failed to fetch mutations for user {}.".format(self.id_user))

		finally:
			return result



	def equip(self, weapon_item = None):
		return bknd_item.equip(self, weapon_item)

	def equip_sidearm(self, sidearm_item = None):
		return bknd_item.equip_sidearm(self, sidearm_item)

	def getStatusEffects(self):
		values = []

		try:
			data = bknd_core.execute_sql_query("SELECT {id_status} FROM status_effects WHERE {id_server} = %s and {id_user} = %s".format(
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

	def applyStatus(self, id_status = None, value = 0, source = "", multiplier = 1, id_target = -1):
		
		return bknd_status.applyStatus(self, id_status, value, source, multiplier, id_target)

	def clear_status(self, id_status = None):
		if id_status != None:
			try:
				conn_info = bknd_core.databaseConnect()
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
				bknd_core.databaseClose(conn_info)

	def clear_allstatuses(self):
		try:
			bknd_core.execute_sql_query("DELETE FROM status_effects WHERE {id_server} = %s AND {id_user} = %s".format(
					id_server = ewcfg.col_id_server,
					id_user = ewcfg.col_id_user
				),(
					self.id_server,
					self.id_user
				))
		except:
			ewutils.logMsg("Failed to clear status effects for user {}.".format(self.id_user))
		

	def apply_injury(self, id_injury, severity, source):
		return bknd_status.apply_injury(self, id_injury, severity, source)

	def get_weapon_capacity(self):
		mutations = self.get_mutations()
		base_capacity = ewutils.weapon_carry_capacity_bylevel(self.slimelevel)
		if ewcfg.mutation_id_2ndamendment in mutations:
			return base_capacity + 1
		else:
			return base_capacity

	def get_food_capacity(self):
		mutations = self.get_mutations()
		base_capacity = ewutils.food_carry_capacity_bylevel(self.slimelevel)
		if ewcfg.mutation_id_bigbones in mutations:
			return 2 * base_capacity
		else:
			return base_capacity


	def get_mention(self):
		return "<@{id_user}>".format(id_user = self.id_user)

	def ban(self, faction = None):
		if faction is None:
			return
		bknd_core.execute_sql_query("REPLACE INTO bans ({id_user}, {id_server}, {faction}) VALUES (%s,%s,%s)".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			faction = ewcfg.col_faction
		),(
			self.id_user,
			self.id_server,
			faction
		))

	def unban(self, faction = None):
		if faction is None:
			return
		bknd_core.execute_sql_query("DELETE FROM bans WHERE {id_user} = %s AND {id_server} = %s AND {faction} = %s".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			faction = ewcfg.col_faction
		),(
			self.id_user,
			self.id_server,
			faction
		))

	def get_bans(self):
		bans = []
		data = bknd_core.execute_sql_query("SELECT {faction} FROM bans WHERE {id_user} = %s AND {id_server} = %s".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			faction = ewcfg.col_faction
		),(
			self.id_user,
			self.id_server
		))

		for row in data:
			bans.append(row[0])

		return bans


	def vouch(self, faction = None):
		if faction is None:
			return
		bknd_core.execute_sql_query("REPLACE INTO vouchers ({id_user}, {id_server}, {faction}) VALUES (%s,%s,%s)".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			faction = ewcfg.col_faction
		),(
			self.id_user,
			self.id_server,
			faction
		))

	def unvouch(self, faction = None):
		if faction is None:
			return
		bknd_core.execute_sql_query("DELETE FROM vouchers WHERE {id_user} = %s AND {id_server} = %s AND {faction} = %s".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			faction = ewcfg.col_faction
		),(
			self.id_user,
			self.id_server,
			faction
		))

	def get_vouchers(self):
		vouchers = []
		data = bknd_core.execute_sql_query("SELECT {faction} FROM vouchers WHERE {id_user} = %s AND {id_server} = %s".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			faction = ewcfg.col_faction
		),(
			self.id_user,
			self.id_server
		))

		for row in data:
			vouchers.append(row[0])

		return vouchers

	def get_inhabitants(self):
		inhabitants = []
		data = bknd_core.execute_sql_query("SELECT {id_ghost} FROM inhabitations WHERE {id_fleshling} = %s AND {id_server} = %s".format(
			id_ghost = ewcfg.col_id_ghost,
			id_fleshling = ewcfg.col_id_fleshling,
			id_server = ewcfg.col_id_server,
		),(
			self.id_user,
			self.id_server
		))

		for row in data:
			inhabitants.append(row[0])

		return inhabitants

	def get_inhabitee(self):
		data = bknd_core.execute_sql_query("SELECT {id_fleshling} FROM inhabitations WHERE {id_ghost} = %s AND {id_server} = %s".format(
			id_fleshling = ewcfg.col_id_fleshling,
			id_ghost = ewcfg.col_id_ghost,
			id_server = ewcfg.col_id_server,
		),(
			self.id_user,
			self.id_server
		))

		try:
			# return ID of inhabited player if there is one
			return data[0][0]
		except:
			# otherwise return None
			return None

	async def move_inhabitants(self, id_poi = None):
		client = ewutils.get_client()
		inhabitants = self.get_inhabitants()
		if inhabitants:
			server = client.get_guild(self.id_server)
			for ghost in inhabitants:
				ghost_data = EwUser(id_user = ghost, id_server = self.id_server)
				ghost_data.poi = id_poi
				ghost_data.time_lastenter = int(time.time())
				ghost_data.persist()
    
				ghost_member = server.get_member(ghost)
				await ewrolemgr.updateRoles(client = client, member = ghost_member)
  
	def remove_inhabitation(self):
		user_is_alive = self.life_state != ewcfg.life_state_corpse
		bknd_core.execute_sql_query("DELETE FROM inhabitations WHERE {id_target} = %s AND {id_server} = %s".format(
			# remove ghosts inhabiting player if user is a fleshling,
			# or remove fleshling inhabited by player if user is a ghost
			id_target = ewcfg.col_id_fleshling if user_is_alive else ewcfg.col_id_ghost,
			id_server = ewcfg.col_id_server,
		),(
			self.id_user,
			self.id_server
		))

	def get_possession(self, possession_type = ''):
		user_is_alive = self.life_state != ewcfg.life_state_corpse
		data = bknd_core.execute_sql_query("SELECT {id_ghost}, {id_fleshling}, {id_server}, {empowered} FROM inhabitations WHERE {id_target} = %s AND {id_server} = %s AND {inverted} {empowered} = %s".format(
			id_ghost = ewcfg.col_id_ghost,
			id_fleshling = ewcfg.col_id_fleshling,
			id_server = ewcfg.col_id_server,
			id_target = ewcfg.col_id_fleshling if user_is_alive else ewcfg.col_id_ghost,
			empowered = ewcfg.col_empowered,
			inverted = '' if possession_type else 'NOT'
		),(
			self.id_user,
			self.id_server,
			possession_type
		))

		try:
			# return inhabitation data if available
			return data[0]
		except:
			# otherwise return None
			return None

	def cancel_possession(self):
		user_is_alive = self.life_state != ewcfg.life_state_corpse
		bknd_core.execute_sql_query(
			"UPDATE inhabitations SET {empowered} = '' WHERE {id_target} = %s AND {id_server} = %s".format(
				empowered = ewcfg.col_empowered,
				id_target = ewcfg.col_id_fleshling if user_is_alive else ewcfg.col_id_ghost,
				id_server = ewcfg.col_id_server,
			),(
				self.id_user,
				self.id_server,
			)
		)

	def get_fashion_stats(self):
		return bknd_item.get_fashion_stats(self)

	def get_freshness(self):
		return bknd_item.get_freshness(self)

	def get_festivity(self):
		data = bknd_core.execute_sql_query(
		"SELECT {festivity} + COALESCE(sigillaria, 0) + {festivity_from_slimecoin} FROM users "\
		"LEFT JOIN (SELECT {id_user}, {id_server}, COUNT(*) * 1000 as sigillaria FROM items INNER JOIN items_prop ON items.{id_item} = items_prop.{id_item} "\
		"WHERE {type} = %s AND {name} = %s AND {value} = %s GROUP BY items.{id_user}, items.{id_server}) f on users.{id_user} = f.{id_user} AND users.{id_server} = f.{id_server} WHERE users.{id_user} = %s AND users.{id_server} = %s".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			festivity = ewcfg.col_festivity,
			festivity_from_slimecoin = ewcfg.col_festivity_from_slimecoin,
			type = ewcfg.col_item_type,
			name = ewcfg.col_name,
			value = ewcfg.col_value,
			id_item = ewcfg.col_id_item,
		),(
			ewcfg.it_furniture,
			"id_furniture",
			ewcfg.item_id_sigillaria,
			self.id_user,
			self.id_server
		))
		res = 0

		for row in data:
			res = row[0]

		return res


def get_move_speed(user_data):
	time_now = int(time.time())
	mutations = user_data.get_mutations()
	statuses = user_data.getStatusEffects()
	market_data = EwMarket(id_server=user_data.id_server)
	# trauma = se_static.trauma_map.get(user_data.trauma)
	# disabled until held items update
	# move_speed = 1 + (user_data.speed / 50)
	move_speed = 1

	if user_data.life_state == ewcfg.life_state_shambler:
		if market_data.weather == ewcfg.weather_bicarbonaterain:
			move_speed *= 2
		else:
			move_speed *= 0.5

	# if ewcfg.status_injury_legs_id in statuses:
	#	status_data = EwStatusEffect(id_status = ewcfg.status_injury_legs_id, user_data = user_data)
	#	try:
	#		move_speed *= max(0, (1 - 0.2 * int(status_data.value) / 10))
	#	except:
	#		ewutils.logMsg("failed int conversion while getting move speed for user {}".format(user_data.id_user))

	# if (trauma != None) and (trauma.trauma_class == ewcfg.trauma_class_movespeed):
	#	move_speed *= max(0, (1 - 0.5 * user_data.degradation / 100))

	if ewcfg.mutation_id_organicfursuit in mutations and ewutils.check_fursuit_active(market_data):
		move_speed *= 2
	if (
			ewcfg.mutation_id_lightasafeather in mutations or ewcfg.mutation_id_airlock) in mutations and market_data.weather == "windy":
		move_speed *= 2
	if ewcfg.mutation_id_fastmetabolism in mutations and user_data.hunger / user_data.get_hunger_max() < 0.4:
		move_speed *= 1.33

	# TODO remove after double halloween
	# if user_data.life_state == ewcfg.life_state_corpse:
	#	move_speed *= 2

	move_speed = max(0.1, move_speed)

	return move_speed
