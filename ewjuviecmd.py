"""
	Commands and utilities related to Juveniles.
"""
import time
import random
import math

import ewcfg
import ewutils
import ewcmd
import ewitem
import ewmap
import ewrolemgr
import ewstats
from ewitem import EwItem
from ew import EwUser
from ewmarket import EwMarket
from ewdistrict import EwDistrict

# Map of user ID to a map of recent miss-mining time to count. If the count
# exceeds 3 in 5 seconds, you die.
last_mismined_times = {}

juviesrow_mines = {}
toxington_mines = {}
cratersville_mines = {}

mines_map = {
	ewcfg.poi_id_mine: juviesrow_mines,
	ewcfg.poi_id_tt_mines: toxington_mines,
	ewcfg.poi_id_cv_mines: cratersville_mines
}


class EwMineGrid:
	grid = []

	message = ""
	wall_message = ""

	times_edited = 0

	time_last_posted = 0

	cells_mined = 0

	def __init__(self, grid):
		self.grid = grid
		self.message = ""
		self.wall_message = ""
		self.times_edited = 0
		self.time_last_posted = 0
		self.cells_mined = 0


""" player enlists in a faction/gang """
async def enlist(cmd):
	user_data = EwUser(member = cmd.message.author)
	user_slimes = user_data.slimes
	time_now = int(time.time())
	bans = user_data.get_bans()
	vouchers = user_data.get_vouchers()

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "You're dead, bitch."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	elif user_slimes < ewcfg.slimes_toenlist:
		response = "You need to mine more slime to rise above your lowly station. ({}/{})".format(user_slimes, ewcfg.slimes_toenlist)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.tokens_count > 1:
		desired_faction = cmd.tokens[1].lower()
	else:
		response = "Which faction? Say '{} {}' or '{} {}'.".format(ewcfg.cmd_enlist, ewcfg.faction_killers, ewcfg.cmd_enlist, ewcfg.faction_rowdys)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if desired_faction == ewcfg.faction_killers:
		if ewcfg.faction_killers in bans:
			response = "You are banned from enlisting in the {}.".format(ewcfg.faction_killers)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif ewcfg.faction_killers not in vouchers and user_data.faction != ewcfg.faction_killers:
			response = "You need a current gang member's permission to join the {}.".format(ewcfg.faction_killers)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		elif user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers:
			response = "You are already enlisted in the {}! Look, your name is purple! Get a clue, idiot.".format(user_data.faction)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif user_data.faction == ewcfg.faction_rowdys:
			response = "Traitor! You can only {} in the {}, you treacherous cretin. Ask for a {} if you're that weak-willed.".format(ewcfg.cmd_enlist, user_data.faction, ewcfg.cmd_pardon)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		else:
			response = "Enlisting in the {}.".format(ewcfg.faction_killers)
			user_data.life_state = ewcfg.life_state_enlisted
			user_data.faction = ewcfg.faction_killers
			user_data.time_lastenlist = time_now + ewcfg.cd_enlist
			user_data.persist()
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

	elif desired_faction == ewcfg.faction_rowdys:
		if ewcfg.faction_rowdys in bans:
			response = "You are banned from enlisting in the {}.".format(ewcfg.faction_rowdys)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		if ewcfg.faction_rowdys not in vouchers and user_data.faction != ewcfg.faction_rowdys:
			response = "You need a current gang member's permission to join the {}.".format(ewcfg.faction_rowdys)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_rowdys:
			response = "You are already enlisted in the {}! Look, your name is pink! Get a clue, idiot.".format(user_data.faction)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		elif user_data.faction == ewcfg.faction_killers:
			response = "Traitor! You can only {} in the {}, you treacherous cretin. Ask for a {} if you're that weak-willed.".format(ewcfg.cmd_enlist, user_data.faction, ewcfg.cmd_pardon)
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

		else:
			response = "Enlisting in the {}.".format(ewcfg.faction_rowdys)
			user_data.life_state = ewcfg.life_state_enlisted
			user_data.faction = ewcfg.faction_rowdys
			user_data.time_lastenlist = time_now + ewcfg.cd_enlist
			user_data.persist()
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

	else:
		response = "That's not a valid gang you can enlist in, bitch."

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def renounce(cmd):
	user_data = EwUser(member = cmd.message.author)

	if user_data.life_state == ewcfg.life_state_corpse:
		response = "You're dead, bitch."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	elif user_data.life_state != ewcfg.life_state_enlisted:
		response = "What exactly are you renouncing? Your lackadaisical, idyllic life free of vice and violence? You aren't actually currently enlisted in any gang, retard."

	elif user_data.poi not in [ewcfg.poi_id_rowdyroughhouse, ewcfg.poi_id_copkilltown]:
		response = "To turn in your badge, you must return to your soon-to-be former gang base."

	else:
		renounce_fee = int(user_data.slimes) / 2
		user_data.change_slimes(n = -renounce_fee)
		faction = user_data.faction
		user_data.life_state = ewcfg.life_state_juvenile
		user_data.weapon = -1
		user_data.persist()
		response = "You are no longer enlisted in the {}, but you are not free of association with them. Your former teammates immediately begin to beat the shit out of you, knocking {} slime out of you before you're able to get away.".format(faction, renounce_fee)
		await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" mine for slime (or endless rocks) """
async def mine(cmd):
	market_data = EwMarket(id_server = cmd.message.author.server.id)
	user_data = EwUser(member = cmd.message.author)
	mutations = user_data.get_mutations()
	time_now = int(time.time())

	response = ""
	# Kingpins can't mine.
	if user_data.life_state == ewcfg.life_state_kingpin or user_data.life_state == ewcfg.life_state_grandfoe:
		return

	# ghosts cant mine (anymore)
	if user_data.life_state == ewcfg.life_state_corpse:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You can't mine while you're dead. Try {}.".format(ewcfg.cmd_revive)))

	# Enlisted players only mine at certain times.
	if user_data.life_state == ewcfg.life_state_enlisted:
		if user_data.faction == ewcfg.faction_rowdys and (market_data.clock < 8 or market_data.clock > 17):
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Rowdies only mine in the daytime. Wait for full daylight at 8am.".format(ewcfg.cmd_revive)))

		if user_data.faction == ewcfg.faction_killers and (market_data.clock < 20 and market_data.clock > 5):
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Killers only mine under cover of darkness. Wait for nightfall at 8pm.".format(ewcfg.cmd_revive)))

	# Mine only in the mines.
	if cmd.message.channel.name in [ewcfg.channel_mines, ewcfg.channel_cv_mines, ewcfg.channel_tt_mines]:

		if user_data.hunger >= user_data.get_hunger_max():
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You've exhausted yourself from mining. You'll need some refreshment before getting back to work."))

		else:
			printgrid = True
			hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
			extra = hunger_cost_mod - int(hunger_cost_mod)  # extra is the fractional part of hunger_cost_mod

			if user_data.poi not in mines_map:
				response = "You can't mine here! Go to the mines in Juvie's Row, Toxington, or Cratersville!"
				return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
			elif user_data.id_server not in mines_map.get(user_data.poi):
				init_grid(user_data.poi, user_data.id_server)
				printgrid = True
			grid_cont = mines_map.get(user_data.poi).get(user_data.id_server)
			grid = grid_cont.grid

			#minesweeper = False
			if cmd.tokens_count < 2:
				response = "Please specify which vein to mine."
				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
				return await print_grid(cmd)

			else:
				#minesweeper = True
				#grid_multiplier = grid_cont.cells_mined ** 0.4
				#flag = False
				row = -1
				col = -1
				bubble_add = None
				for token in cmd.tokens[1:]:
				
					if token.lower() == "reset":
						user_data.hunger += ewcfg.hunger_perminereset * int(hunger_cost_mod)
						if random.random() < extra:
							user_data.hunger += ewcfg.hunger_perminereset
						user_data.persist()
						init_grid(user_data.poi, user_data.id_server)
						return await print_grid(cmd)

					if col < 1:
						char = token.lower()
					
						if char in ewcfg.alphabet:
							col = ewcfg.alphabet.index(char)

					if bubble_add == None:
						bubble = token.lower()
						if bubble in ewcfg.cell_bubbles:
							bubble_add = bubble


				row = len(grid)
				row -= 1
			
				if col not in range(len(grid[0])):
					response = "Invalid vein."
					await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
					return await print_grid(cmd)

				if bubble_add == None:
					response = "Invalid bubble."
					await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
					return await print_grid(cmd)

				mining_yield = 0
				mining_accident = False

				cells_to_clear = []
				
				slimes_pertile = ewcfg.slimes_pertile
				if grid[row][col] != ewcfg.cell_empty:
					mining_accident = True
				else:
					grid[row][col] = bubble_add

					cells_to_check = apply_gravity(grid)

					cells_to_check.append((row,col))

					while len(cells_to_check) > 0:
						mining_yield += slimes_pertile * check_and_explode(grid, cells_to_check)
						
						cells_to_check = apply_gravity(grid)

				grid_cont.cells_mined += 1
				grid_height = get_height(grid)

				if grid_cont.cells_mined % 15 == 10 or grid_height < 5:
					if grid_height < len(grid):
						add_row(grid)
					else:
						mining_accident = True

				if mining_accident:
					user_data.change_slimes(n = -(user_data.slimes * 0.5))
					user_data.persist()

					init_grid(user_data.poi, user_data.id_server)
					response = "You have lost an arm and a leg in a mining accident. Tis but a scratch."

					await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
					return await print_grid(cmd)


				if mining_yield == 0:
					user_data.hunger += ewcfg.hunger_permine * int(hunger_cost_mod)
					user_data.persist()
					#response = "This vein has already been mined dry."
					#await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
					if printgrid:
						return await print_grid(cmd)
					else:
						return


			has_pickaxe = False

			if user_data.weapon >= 0:
				weapon_item = EwItem(id_item = user_data.weapon)
				weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
				if weapon.id_weapon == ewcfg.weapon_id_pickaxe:
					has_pickaxe = True

			# Determine if an item is found.
			unearthed_item = False
			unearthed_item_amount = 0

			# juvies get items 4 times as often as enlisted players
			unearthed_item_chance = 1 / ewcfg.unearthed_item_rarity
			if user_data.life_state == ewcfg.life_state_juvenile:
				unearthed_item_chance *= 2
			if has_pickaxe == True:
				unearthed_item_chance *= 1.5
			if ewcfg.mutation_id_lucky in mutations:
				unearthed_item_chance *= 1.33


			if random.random() < unearthed_item_chance:
				unearthed_item = True
				unearthed_item_amount = 1 if random.randint(1, 3) != 1 else 2  # 33% chance of extra drop

			if unearthed_item == True:
				# If there are multiple possible products, randomly select one.
				item = random.choice(ewcfg.mine_results)

				item_props = ewitem.gen_item_props(item)

				for creation in range(unearthed_item_amount):
					ewitem.item_create(
						item_type = item.item_type,
						id_user = cmd.message.author.id,
						id_server = cmd.message.server.id,
						item_props = item_props
					)

				if unearthed_item_amount == 1:
					response = "You unearthed a {}! ".format(item.str_name)
				elif unearthed_item_amount == 2:
					response = "You unearthed two (2) {}! ".format(item.str_name)


				ewstats.change_stat(user = user_data, metric = ewcfg.stat_lifetime_poudrins, n = unearthed_item_amount)

				ewutils.logMsg('{} has found {} {}(s)!'.format(cmd.message.author.display_name, item.str_name, unearthed_item_amount))

			user_initial_level = user_data.slimelevel

			# Add mined slime to the user.
			slime_bylevel = ewutils.slime_bylevel(user_data.slimelevel)

			#mining_yield = math.floor((slime_bylevel / 10) + 1)
			#alternate_yield = math.floor(200 + slime_bylevel ** (1 / math.e))

			#mining_yield = min(mining_yield, alternate_yield)

			if has_pickaxe == True:
				mining_yield *= 2

			# Fatigue the miner.

			user_data.hunger += ewcfg.hunger_permine * int(hunger_cost_mod)
			if extra > 0:  # if hunger_cost_mod is not an integer
				# there's an x% chance that an extra stamina is deducted, where x is the fractional part of hunger_cost_mod in percent (times 100)
				if random.randint(1, 100) <= extra * 100:
					user_data.hunger += ewcfg.hunger_permine

			levelup_response = user_data.change_slimes(n = mining_yield, source = ewcfg.source_mining)

			was_levelup = True if user_initial_level < user_data.slimelevel else False

			# Tell the player their slime level increased and/or they unearthed an item.
			if was_levelup:
				response += levelup_response

			user_data.persist()

			if printgrid:
				await print_grid(cmd)

	else:
		response = "You can't mine here! Go to the mines in Juvie's Row, Toxington, or Cratersville!"

	if len(response) > 0:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


"""
	Mining in the wrong channel or while exhausted. This is deprecated anyway but let's sorta keep it around in case we need it.
"""
async def mismine(cmd, user_data, cause):
	time_now = int(time.time())
	global last_mismined_times

	mismined = last_mismined_times.get(cmd.message.author.id)

	if mismined is None:
		mismined = {
			'time': time_now,
			'count': 0
		}

	if time_now - mismined['time'] < 5:
		mismined['count'] += 1
	else:
		# Reset counter.
		mismined['time'] = time_now
		mismined['count'] = 1

	last_mismined_times[cmd.message.author.id] = mismined

	if mismined['count'] >= 11:  # up to 6 messages can be buffered by discord and people have been dying unfairly because of that
		# Lose some slime
		last_mismined_times[cmd.message.author.id] = None
		# user_data.die(cause = ewcfg.cause_mining)

		user_data.change_slimes(n = -(user_data.slimes / 5))
		user_data.persist()

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You have lost an arm and a leg in a mining accident. Tis but a scratch."))
		# await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
		# sewerchannel = ewutils.get_channel(cmd.message.server, ewcfg.channel_sewers)
		# await ewutils.send_message(cmd.client, sewerchannel, "{} ".format(ewcfg.emote_slimeskull) + ewutils.formatMessage(cmd.message.author, "You have died in a mining accident. {}".format(ewcfg.emote_slimeskull)))
	else:
		if cause == "exhaustion":
			response = "You've exhausted yourself from mining. You'll need some refreshment before getting back to work."
		else:
			response = "You can't mine in this channel. Go elsewhere."

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" scavenge for slime """
async def scavenge(cmd):
	market_data = EwMarket(id_server = cmd.message.author.server.id)
	user_data = EwUser(member = cmd.message.author)
	mutations = user_data.get_mutations()

	time_now = int(time.time())
	response = ""

	time_since_last_scavenge = time_now - user_data.time_lastscavenge

	# Kingpins can't scavenge.
	if user_data.life_state == ewcfg.life_state_kingpin or user_data.life_state == ewcfg.life_state_grandfoe:
		return

	# ghosts cant scavenge 
	if user_data.life_state == ewcfg.life_state_corpse:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "What would you want to do that for? You're a ghost, you have no need for such lowly materialistic possessions like slime. You only engage in intellectual pursuits now. {} if you want to give into your base human desire to see numbers go up.".format(ewcfg.cmd_revive)))
	# currently not active - no cooldown
	if time_since_last_scavenge < ewcfg.cd_scavenge:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Slow down, you filthy hyena."))

	# Scavenge only in location channels
	if ewmap.channel_name_is_poi(cmd.message.channel.name) == True:
		if user_data.hunger >= user_data.get_hunger_max():
			return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You are too exhausted to scrounge up scraps of slime off the street! Go get some grub!"))
		else:
			district_data = EwDistrict(district = user_data.poi, id_server = cmd.message.author.server.id)

			user_initial_level = user_data.slimelevel
			# add scavenged slime to user
			if ewcfg.mutation_id_trashmouth in mutations:
				time_since_last_scavenge *= 3

			time_since_last_scavenge = min(max(1, time_since_last_scavenge), 30)


			scavenge_mod = 0.003 * (time_since_last_scavenge ** 0.9)

			if ewcfg.mutation_id_whitenationalist in mutations and market_data.weather == "snow":
				scavenge_mod *= 1.5

			if ewcfg.mutation_id_webbedfeet in mutations:
				district_slimelevel = len(str(district_data.slimes))
				scavenge_mod *= max(1, min(district_slimelevel - 3, 4))

			scavenge_yield = math.floor(scavenge_mod * district_data.slimes)

			levelup_response = user_data.change_slimes(n = scavenge_yield, source = ewcfg.source_scavenging)
			district_data.change_slimes(n = -1 * scavenge_yield, source = ewcfg.source_scavenging)
			district_data.persist()

			if levelup_response != "":
				response += levelup_response + "\n\n"
			#response += "You scrape together {} slime from the streets.\n\n".format(scavenge_yield)
			if cmd.tokens_count > 1:
				item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
				loot_resp = ewitem.item_lootspecific(
					id_server = user_data.id_server,
					id_user = user_data.id_user,
					item_search = item_search
				)

				response += loot_resp

			else:
				loot_multiplier = 1.0 + ewitem.get_inventory_size(owner = user_data.poi, id_server = user_data.id_server)
				loot_chance = loot_multiplier / ewcfg.scavenge_item_rarity
				if ewcfg.mutation_id_dumpsterdiver in mutations:
					loot_chance *= 10
				if random.random() < loot_chance:
					loot_resp = ewitem.item_lootrandom(
						id_server = user_data.id_server,
						id_user = user_data.id_user
					)
					response += loot_resp


			# Fatigue the scavenger.
			hunger_cost_mod = ewutils.hunger_cost_mod(user_data.slimelevel)
			extra = hunger_cost_mod - int(hunger_cost_mod)  # extra is the fractional part of hunger_cost_mod

			user_data.hunger += ewcfg.hunger_perscavenge * int(hunger_cost_mod)
			if extra > 0:  # if hunger_cost_mod is not an integer
				# there's an x% chance that an extra stamina is deducted, where x is the fractional part of hunger_cost_mod in percent (times 100)
				if random.randint(1, 100) <= extra * 100:
					user_data.hunger += ewcfg.hunger_perscavenge

			user_data.time_lastscavenge = time_now

			user_data.persist()

			if not response == "":
				await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "You'll find no slime here, this place has been picked clean. Head into the city to try and scavenge some slime."))

def init_grid(poi, id_server):
	grid = []
	num_rows = 12
	num_cols = 12
	for i in range(num_rows):
		row = []
		for j in range(num_cols):
			if i > 8:
				row.append(ewcfg.cell_empty)
				continue
			cell = random.choice(ewcfg.cell_bubbles)
			randomn = random.random()
			if randomn < 0.15 and j > 0:
				cell = row[-1]
			elif randomn < 0.3 and i > 0:
				cell = grid[-1][j]

			row.append(cell)
		grid.append(row)


			
	if poi in mines_map:
		grid_cont = EwMineGrid(grid = grid)
		mines_map.get(poi)[id_server] = grid_cont

async def print_grid(cmd):
	grid_str = ""
	user_data = EwUser(member = cmd.message.author)
	poi = user_data.poi
	id_server = cmd.message.server.id
	time_now = int(time.time())
	use_emotes = False
	if poi in mines_map:
		grid_map = mines_map.get(poi)
		if id_server not in grid_map:
			init_grid_ms(poi, id_server)
		grid_cont = grid_map.get(id_server)

		grid = grid_cont.grid

		#grid_str += "   "
		for j in range(len(grid[0])):
			letter = ewcfg.alphabet[j]
			grid_str += "{} ".format(letter)
		grid_str += "\n"
		for i in range(len(grid)):
			row = grid[i]
			#if i+1 < 10:
			#	grid_str += " "

			#grid_str += "{} ".format(i+1)
			for j in range(len(row)):
				cell = row[j]
				cell_str = get_cell_symbol(cell)
				if use_emotes:
					cell_str = ewcfg.number_emote_map.get(int(cell))
				grid_str += cell_str + " "
			#grid_str += "{}".format(i+1)
			grid_str += "\n"


		#grid_str += "   "
		for j in range(len(grid[0])):
			letter = ewcfg.alphabet[j]
			grid_str += "{} ".format(letter)

		grid_edit = "\n```\n{}\n```".format(grid_str)
		if use_emotes:
			grid_edit = "\n" + grid_str
		if time_now > grid_cont.time_last_posted + 10 or grid_cont.times_edited > 8 or grid_cont.message == "":
			grid_cont.message = await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, grid_edit))
			grid_cont.time_last_posted = time_now
			grid_cont.times_edited = 0
		else:
			await ewutils.edit_message(cmd.client, grid_cont.message, ewutils.formatMessage(cmd.message.author, grid_edit))
			grid_cont.times_edited += 1

		if grid_cont.wall_message == "":
			wall_channel = ewcfg.mines_wall_map.get(poi)
			resp_cont = ewutils.EwResponseContainer(id_server = id_server)
			resp_cont.add_channel_response(wall_channel, grid_edit)
			msg_handles = await resp_cont.post()
			grid_cont.wall_message = msg_handles[0]
		else:
			await ewutils.edit_message(cmd.client, grid_cont.wall_message, grid_edit)

def get_cell_symbol(cell):
	if cell == "0":
		return " "
	return cell
	cell_str = " "
	#if cell > 2 * ewcfg.slimes_invein:
	#	cell_str = "&"
	#elif cell > 1.5 * ewcfg.slimes_invein:
	#	cell_str = "S"
	if cell > 0.4 * ewcfg.slimes_invein:
		cell_str = "~"
	#elif cell > 0.5 * ewcfg.slimes_invein:
	#	cell_str = ";"
	elif cell > 0:
		cell_str = ";"
	elif cell > -40 * ewcfg.slimes_pertile:
		cell_str = " "
	#elif cell > -40 * ewcfg.slimes_pertile:
	#	cell_str = "+"
	else:
		cell_str = "X"
	return cell_str

async def crush(cmd):
	member = cmd.message.author
	user_data = EwUser(member=member)
	response = ""
	
	poudrin = ewitem.find_item(item_search="slimepoudrin", id_user=cmd.message.author.id, id_server=cmd.message.server.id if cmd.message.server is not None else None)
	
	if user_data.life_state == ewcfg.life_state_corpse:
		response = "Alas, you try to shatter the hardened slime crystal, but your ghostly form cannot firmly grasp it."
		return 	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	
	if poudrin is None:
		response = "You need a slime poudrin."
	else:
		# delete a slime poudrin from the player's inventory
		ewitem.item_delete(id_item=poudrin.get('id_item'))
		
		user_data.slimes += ewcfg.crush_slimes
		user_data.persist()
		
		response = "You crush the hardened slime crystal with your bare hands.\nYou gain 10,000 slime. Sick, dude!!"
		
	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

def apply_gravity(grid):
	cells_to_check = []
	for row in range(1,len(grid)):
		for col in range(len(grid[row])):
			coords = (row, col)
			new_coords = bubble_fall(grid, (row,col))
			if coords != new_coords:
				cells_to_check.append(new_coords)

	return cells_to_check


def bubble_fall(grid, coords):
	row = coords[0]
	col = coords[1]
	if grid[row][col] == ewcfg.cell_empty:
		return coords
	falling_bubble = grid[row][col]
	while row > 0 and grid[row-1][col] == ewcfg.cell_empty:
		row -= 1

	grid[coords[0]][coords[1]] = ewcfg.cell_empty
	grid[row][col] = falling_bubble
	return (row,col)

def check_and_explode(grid, cells_to_check):
	slime_yield = 0

	for coords in cells_to_check:
		bubble = grid[coords[0]][coords[1]]
		if bubble == ewcfg.cell_empty:
			continue

		bubble_cluster = [coords]
		to_check = [coords]
		while len(to_check) > 0:
			to_check_next = []
			for coord in to_check:
				neighs = neighbors(grid, coord)
				for neigh in neighs:
					if neigh in bubble_cluster:
						continue
					if grid[neigh[0]][neigh[1]] == bubble:
						bubble_cluster.append(neigh)
						to_check_next.append(neigh)
			to_check = to_check_next
						

		if len(bubble_cluster) >= ewcfg.bubbles_to_burst:
			for coord in bubble_cluster:
				grid[coord[0]][coord[1]] = ewcfg.cell_empty
				slime_yield += 1

	return slime_yield
		

def neighbors(grid, coords):
	neighs = []
	row = coords[0]
	col = coords[1]
	if row-1 >= 0:
		neighs.append((row-1,col))
	if row+1 < len(grid):
		neighs.append((row+1,col))
	if col-1 >= 0:
		neighs.append((row,col-1))
	if col+1 < len(grid[row]):
		neighs.append((row,col+1))
	return neighs

def add_row(grid):
	new_row = []
	for i in range(len(grid[0])):
		
		cell = random.choice(ewcfg.cell_bubbles)
		randomn = random.random()
		if randomn < 0.15 and i > 0:
			cell = new_row[-1]
		elif randomn < 0.3:
			cell = grid[0][i]
		if cell == ewcfg.cell_empty:
			cell = random.choice(ewcfg.cell_bubbles)

		new_row.append(cell)
	grid.insert(0, new_row)
	return grid.pop(-1)

def get_height(grid):
	row = 0

	while row < len(grid):
		is_empty = True
		for cell in grid[row]:
			if cell != ewcfg.cell_empty:
				is_empty = False
				break
		if is_empty:
			break
		row += 1

	return row
		
