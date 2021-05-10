import random
import time

from . import core as bknd_core
from ..static import cfg as ewcfg
from ..utils import core as ewutils


class EwUserBase:
	id_user = -1
	id_server = -1
	id_killer = -1

	combatant_type = "player"

	slimes = 0
	slimecoin = 0
	slime_donations = 0
	poudrin_donations = 0
	slimelevel = 1
	hunger = 0
	totaldamage = 0
	bleed_storage = 0
	bounty = 0
	weapon = -1
	sidearm = -1
	trauma = ""
	poi_death = ""
	inebriation = 0
	faction = ""
	poi = ""
	life_state = 0
	busted = False
	time_last_action = 0
	weaponmarried = False
	arrested = False
	active_slimeoid = -1
	splattered_slimes = 0
	#sap = 0
	#hardened_sap = 0
	race = ""

	#SLIMERNALIA
	festivity = 0
	festivity_from_slimecoin = 0
	slimernalia_kingpin = False

	manuscript = -1
	spray = "https://img.booru.org/rfck//images/3/a69d72cf29cb750882de93b4640a175a88cdfd70.png"
	salary_credits = 0
	degradation = 0

	#SWILLDERMUK
	gambit = 0
	credence = 0
	credence_used = 0

	time_lastkill = 0
	time_lastrevive = 0
	time_lastspar = 0
	time_lasthaunt = 0
	time_lastinvest = 0
	time_lastscavenge = 0
	time_lastenter = 0
	time_lastoffline = 0
	time_joined = 0
	time_expirpvp = 0
	time_lastenlist = 0
	time_lastdeath = 0
	time_racialability = 0
	time_lastpremiumpurchase = 0

	#GANKERS VS SHAMBLERS
	juviemode = 0
	gvs_time_lastshambaquarium = 0

	apt_zone = "empty"
	visiting = "empty"
	has_soul = 1
	#random seed for mutaiton calculation
	rand_seed = 0
	#when a user was last hit
	time_lasthit = 2

	# twitter
	verified = False

	move_speed = 1 # not a database column

	""" fix data in this object if it's out of acceptable ranges """
	def limit_fix(self):
		if self.hunger > self.get_hunger_max():
			self.hunger = self.get_hunger_max()

		if self.life_state == ewcfg.life_state_shambler:
			self.hunger = 0

		if self.inebriation < 0:
			self.inebriation = 0

		if self.poi == '':
			self.poi = ewcfg.poi_id_downtown

		if self.time_last_action <= 0:
			self.time_last_action = int(time.time())

		if self.move_speed <= 0:
			self.move_speed = 1

		#self.sap = max(0, min(self.sap, ewutils.sap_max_bylevel(self.slimelevel) - self.hardened_sap))

		#self.hardened_sap = max(0, min(self.hardened_sap, ewutils.sap_max_bylevel(self.slimelevel) - self.sap))

		self.degradation = max(0, self.degradation)


	""" Create a new EwUser and optionally retrieve it from the database. """

	def __init__(self, ew_id=None, member=None, id_user=None, id_server=None):

		self.combatant_type = ewcfg.combatant_type_player

		if ew_id != None:
			id_user = ew_id.user
			id_server = ew_id.guild

		if (id_user == None) and (id_server == None):
			if (member != None):
				id_server = member.guild.id
				id_user = member.id

		# Retrieve the object from the database if the user is provided.
		if (id_user != None) and (id_server != None):
			self.id_server = id_server
			self.id_user = id_user

			try:
				conn_info = bknd_core.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Retrieve object

				cursor.execute(
					"SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM users WHERE id_user = %s AND id_server = %s".format(

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
						ewcfg.col_inebriation,
						ewcfg.col_faction,
						ewcfg.col_poi,
						ewcfg.col_life_state,
						ewcfg.col_busted,
						ewcfg.col_time_last_action,
						ewcfg.col_weaponmarried,
						ewcfg.col_time_lastscavenge,
						ewcfg.col_bleed_storage,
						ewcfg.col_time_lastenter,
						ewcfg.col_time_lastoffline,
						ewcfg.col_time_joined,
						ewcfg.col_poi_death,
						ewcfg.col_slime_donations,
						ewcfg.col_poudrin_donations,
						ewcfg.col_arrested,
						ewcfg.col_splattered_slimes,
						ewcfg.col_time_expirpvp,
						ewcfg.col_time_lastenlist,
						ewcfg.col_apt_zone,
						ewcfg.col_visiting,
						ewcfg.col_active_slimeoid,
						ewcfg.col_has_soul,
						# ewcfg.col_sap,
						# ewcfg.col_hardened_sap,
						ewcfg.col_festivity,
						ewcfg.col_festivity_from_slimecoin,
						ewcfg.col_slimernalia_kingpin,
						ewcfg.col_manuscript,
						ewcfg.col_spray,
						ewcfg.col_salary_credits,
						ewcfg.col_degradation,
						ewcfg.col_time_lastdeath,
						ewcfg.col_sidearm,
						ewcfg.col_gambit,
						ewcfg.col_credence,
						ewcfg.col_credence_used,
						ewcfg.col_race,
						ewcfg.col_time_racialability,
						ewcfg.col_time_lastpremiumpurchase,
						ewcfg.col_juviemode,
						ewcfg.col_gvs_time_lastshambaquarium,
						ewcfg.col_rand_seed,
						ewcfg.col_time_lasthit,
						ewcfg.col_verified,
					), (
						id_user,
						id_server
					))
				result = cursor.fetchone()

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
					self.inebriation = result[14]
					self.faction = result[15]
					self.poi = result[16]
					self.life_state = result[17]
					self.busted = (result[18] == 1)
					self.time_last_action = result[19]
					self.weaponmarried = (result[20] == 1)
					self.time_lastscavenge = result[21]
					self.bleed_storage = result[22]
					self.time_lastenter = result[23]
					self.time_lastoffline = result[24]
					self.time_joined = result[25]
					self.poi_death = result[26]
					self.slime_donations = result[27]
					self.poudrin_donations = result[28]
					self.arrested = (result[29] == 1)
					self.splattered_slimes = result[30]
					self.time_expirpvp = result[31]
					self.time_lastenlist = result[32]
					self.apt_zone = result[33]
					self.visiting = result[34]
					self.active_slimeoid = result[35]
					self.has_soul = result[36]
					# self.sap = result[37]
					# self.hardened_sap = result[38]
					self.festivity = result[37]
					self.festivity_from_slimecoin = result[38]
					self.slimernalia_kingpin = (result[39] == 1)
					self.manuscript = result[40]
					self.spray = result[41]
					self.salary_credits = result[42]
					self.degradation = result[43]
					self.time_lastdeath = result[44]
					self.sidearm = result[45]
					self.gambit = result[46]
					self.credence = result[47]
					self.credence_used = result[48]
					self.race = result[49]
					self.time_racialability = result[50]
					self.time_lastpremiumpurchase = result[51]
					self.juviemode = result[52]
					self.gvs_time_lastshambaquarium = result[53]
					self.rand_seed = result[54]
					self.time_lasthit = result[55]
					self.verified = result[56]

				else:
					self.poi = ewcfg.poi_id_downtown
					self.life_state = ewcfg.life_state_juvenile
					# Create a new database entry if the object is missing.
					cursor.execute(
						"REPLACE INTO users(id_user, id_server, poi, life_state, rand_seed) VALUES(%s, %s, %s, %s, %s)",
						(
							id_user,
							id_server,
							self.poi,
							self.life_state,
							random.randrange(500000)
						))

					conn.commit()

				if (self.time_joined == 0) and (member != None) and (member.joined_at != None):
					self.time_joined = int(member.joined_at.timestamp())

				self.limit_fix()
			finally:
				# Clean up the database handles.
				cursor.close()
				bknd_core.databaseClose(conn_info)

	""" Save this user object to the database. """

	def persist(self):

		try:
			# Get database handles if they weren't passed.
			conn_info = bknd_core.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			self.limit_fix()

			# Save the object.

			cursor.execute(
				"REPLACE INTO users({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
					ewcfg.col_id_user,
					ewcfg.col_id_server,
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
					ewcfg.col_inebriation,
					ewcfg.col_faction,
					ewcfg.col_poi,
					ewcfg.col_life_state,
					ewcfg.col_busted,
					ewcfg.col_time_last_action,
					ewcfg.col_weaponmarried,
					ewcfg.col_time_lastscavenge,
					ewcfg.col_bleed_storage,
					ewcfg.col_time_lastenter,
					ewcfg.col_time_lastoffline,
					ewcfg.col_time_joined,
					ewcfg.col_poi_death,
					ewcfg.col_slime_donations,
					ewcfg.col_poudrin_donations,
					ewcfg.col_arrested,
					ewcfg.col_splattered_slimes,
					ewcfg.col_time_expirpvp,
					ewcfg.col_time_lastenlist,
					ewcfg.col_apt_zone,
					ewcfg.col_visiting,
					ewcfg.col_active_slimeoid,
					ewcfg.col_has_soul,
					# ewcfg.col_sap,
					# ewcfg.col_hardened_sap,
					ewcfg.col_festivity,
					ewcfg.col_festivity_from_slimecoin,
					ewcfg.col_slimernalia_kingpin,
					ewcfg.col_manuscript,
					ewcfg.col_spray,
					ewcfg.col_salary_credits,
					ewcfg.col_degradation,
					ewcfg.col_time_lastdeath,
					ewcfg.col_sidearm,
					ewcfg.col_gambit,
					ewcfg.col_credence,
					ewcfg.col_credence_used,
					ewcfg.col_race,
					ewcfg.col_time_racialability,
					ewcfg.col_time_lastpremiumpurchase,
					ewcfg.col_juviemode,
					ewcfg.col_gvs_time_lastshambaquarium,
					ewcfg.col_rand_seed,
					ewcfg.col_time_lasthit,
					ewcfg.col_verified,
				), (
					self.id_user,
					self.id_server,
					self.slimes,
					self.slimelevel,
					self.hunger,
					self.totaldamage,
					self.bounty,
					self.weapon,
					self.trauma,
					self.slimecoin,
					self.time_lastkill,
					self.time_lastrevive,
					self.id_killer,
					self.time_lastspar,
					self.time_lasthaunt,
					self.time_lastinvest,
					self.inebriation,
					self.faction,
					self.poi,
					self.life_state,
					(1 if self.busted else 0),
					self.time_last_action,
					(1 if self.weaponmarried else 0),
					self.time_lastscavenge,
					self.bleed_storage,
					self.time_lastenter,
					self.time_lastoffline,
					self.time_joined,
					self.poi_death,
					self.slime_donations,
					self.poudrin_donations,
					(1 if self.arrested else 0),
					self.splattered_slimes,
					self.time_expirpvp,
					self.time_lastenlist,
					self.apt_zone,
					self.visiting,
					self.active_slimeoid,
					self.has_soul,
					# self.sap,
					# self.hardened_sap,
					self.festivity,
					self.festivity_from_slimecoin,
					self.slimernalia_kingpin,
					self.manuscript,
					self.spray,
					self.salary_credits,
					self.degradation,
					self.time_lastdeath,
					self.sidearm,
					self.gambit,
					self.credence,
					self.credence_used,
					self.race,
					self.time_racialability,
					self.time_lastpremiumpurchase,
					self.juviemode,
					self.gvs_time_lastshambaquarium,
					self.rand_seed,
					self.time_lasthit,
					self.verified
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			bknd_core.databaseClose(conn_info)

	def get_hunger_max(self):
		mutations = self.get_mutations()
		has_ba = 0
		if ewcfg.mutation_id_bottomlessappetite in mutations:
			has_ba = 1
		return ewutils.hunger_max_bylevel(slimelevel=self.slimelevel, has_bottomless_appetite=has_ba)
	def get_mutations(self):
		result = []
		try:
			mutations = bknd_core.execute_sql_query("SELECT {id_mutation} FROM mutations WHERE {id_server} = %s AND {id_user} = %s;".format(
					id_mutation = ewcfg.col_id_mutation,
					id_server = ewcfg.col_id_server,
					id_user = ewcfg.col_id_user
				),(
					self.id_server,
					self.id_user
				))

			for mutation_data in mutations:
				result.append(mutation_data[0])
		except:
			ewutils.logMsg("Failed to fetch mutations for user {}.".format(self.id_user))

		finally:
			return result

	def has_gellphone(self):
		"""
		gellphones = ewitem.find_item_all(item_search = ewcfg.item_id_gellphone, id_user = self.id_user, id_server = self.id_server, item_type_filter = ewcfg.it_item)

		for phone in gellphones:
			phone_data = EwItem(id_item = phone.get('id_item'))
			if phone_data.item_props.get('active') == 'true':
				return True
		"""
		data = bknd_core.execute_sql_query(
		"SELECT it.* FROM items it INNER JOIN items_prop itp ON it.id_item = itp.id_item WHERE it.{id_user} = '%s' AND itp.{name} = %s AND itp.{value} = %s".format(
			id_user = ewcfg.col_id_user,
			id_item = ewcfg.col_id_item,
			name = ewcfg.col_name,
			value = ewcfg.col_value
		),(
			self.id_user,
			"gellphoneactive",
			"true"
		))

		return len(data) > 0

