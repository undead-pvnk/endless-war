import datetime

from ..static import cfg as ewcfg
from ..static import poi as poi_static
from .. import utils as ewutils
from . import core as bknd_core

from ..user import EwUser
from .player import EwPlayer
from .market import EwMarket, EwStock
from .district import EwDistrict



async def post_leaderboards(client = None, server = None):
	leaderboard_channel = ewutils.get_channel(server = server, channel_name = ewcfg.channel_leaderboard)

	market = EwMarket(id_server = server.id)
	time = "day {}".format(market.day) 

	await ewutils.send_message(client, leaderboard_channel, "▓▓{} **STATE OF THE CITY:** {} {}▓▓".format(ewcfg.emote_theeye, time, ewcfg.emote_theeye))

	kingpins = make_kingpin_board(server = server, title = ewcfg.leaderboard_kingpins)
	await ewutils.send_message(client, leaderboard_channel, kingpins)
	districts = make_district_control_board(id_server = server.id, title = ewcfg.leaderboard_districts)
	await ewutils.send_message(client, leaderboard_channel, districts)
	topslimes = make_userdata_board(server = server, category = ewcfg.col_slimes, title = ewcfg.leaderboard_slimes)
	await ewutils.send_message(client, leaderboard_channel, topslimes)
	#topcoins = make_userdata_board(server = server, category = ewcfg.col_slimecoin, title = ewcfg.leaderboard_slimecoin)
	ewutils.logMsg("starting net worth calc")
	topcoins = make_stocks_top_board(server = server)
	ewutils.logMsg("finished net worth calc")
	await ewutils.send_message(client, leaderboard_channel, topcoins)
	topghosts = make_userdata_board(server = server, category = ewcfg.col_slimes, title = ewcfg.leaderboard_ghosts, lowscores = True, rows = 3)
	await ewutils.send_message(client, leaderboard_channel, topghosts)
	topbounty = make_userdata_board(server = server, category = ewcfg.col_bounty, title = ewcfg.leaderboard_bounty, divide_by = ewcfg.slimecoin_exchangerate)
	await ewutils.send_message(client, leaderboard_channel, topbounty)
	#topfashion = make_userdata_board(server = server, category = ewcfg.col_freshness, title = ewcfg.leaderboard_fashion)
	ewutils.logMsg("starting freshness calc")
	topfashion = make_freshness_top_board(server = server)
	ewutils.logMsg("finished freshness calc")
	await ewutils.send_message(client, leaderboard_channel, topfashion)
	topdonated = make_userdata_board(server = server, category = ewcfg.col_splattered_slimes, title = ewcfg.leaderboard_donated)
	await ewutils.send_message(client, leaderboard_channel, topdonated)
	#topdegraded = make_userdata_board(server = server, category = ewcfg.col_degradation, title = ewcfg.leaderboard_degradation)
	#await ewutils.send_message(client, leaderboard_channel, topdegraded)
	#topshamblerkills = make_statdata_board(server = server, category = ewcfg.stat_shamblers_killed, title = ewcfg.leaderboard_shamblers_killed)
	#await ewutils.send_message(client, leaderboard_channel, topshamblerkills)
	topslimeoids = make_slimeoids_top_board(server = server)
	await ewutils.send_message(client, leaderboard_channel, topslimeoids)
	#topfestivity = make_slimernalia_board(server = server, title = ewcfg.leaderboard_slimernalia)
	#await ewutils.send_message(client, leaderboard_channel, topfestivity)
	topzines = make_zines_top_board(server=server)
	await ewutils.send_message(client, leaderboard_channel, topzines)
	#topgambit = make_gambit_leaderboard(server = server, title = ewcfg.leaderboard_gambit_high)
	#await ewutils.send_message(client, leaderboard_channel, topgambit)
	#bottomgambit = make_gambit_leaderboard(server = server, title = ewcfg.leaderboard_gambit_low)
	#await ewutils.send_message(client, leaderboard_channel, bottomgambit)

def make_stocks_top_board(server = None):
	entries = []
	try:
		players_coin = bknd_core.execute_sql_query((
			"SELECT pl.display_name, u.life_state, u.faction, u.slimecoin, IFNULL(sh_kfc.shares, 0), IFNULL(sh_tb.shares, 0), IFNULL(sh_ph.shares, 0), u.id_user " +
			"FROM users AS u " +
			"INNER JOIN players AS pl ON u.id_user = pl.id_user " +
			"LEFT JOIN shares AS sh_kfc ON sh_kfc.id_user = u.id_user AND sh_kfc.id_server = u.id_server AND sh_kfc.stock = 'kfc' " +
			"LEFT JOIN shares AS sh_tb ON sh_tb.id_user = u.id_user AND sh_tb.id_server = u.id_server AND sh_tb.stock = 'tacobell' " +
			"LEFT JOIN shares AS sh_ph ON sh_ph.id_user = u.id_user AND sh_ph.id_server = u.id_server AND sh_ph.stock = 'pizzahut' " +
			"WHERE u.id_server = %(id_server)s " +
			"ORDER BY u.slimecoin DESC"
		), {
			"id_server" : server.id,
		})
		
		stock_kfc = EwStock(id_server = server.id, stock = 'kfc')
		stock_tb = EwStock(id_server = server.id, stock = 'tacobell')
		stock_ph = EwStock(id_server = server.id, stock = 'pizzahut')

		shares_value = lambda shares, stock: round(shares * (stock.exchange_rate / 1000.0))

		net_worth = lambda u: u[3] + shares_value(u[4], stock_kfc) + shares_value(u[5], stock_tb) + shares_value(u[6], stock_ph)


		nw_map = {}
		for user in players_coin:
			nw_map[user[-1]] = net_worth(user)

		players_coin = sorted(players_coin, key = lambda u: nw_map.get(u[-1]), reverse=True)

		data = map(lambda u: [u[0], u[1], u[2], nw_map.get(u[-1])], players_coin[:5])

		if data != None:
			for row in data:
				if row != None:
					entries.append(row)
	except:
		ewutils.logMsg("Error occured while fetching stock leaderboard")

	
	return format_board(entries = entries, title = ewcfg.leaderboard_slimecoin)

def make_freshness_top_board(server = None):
	entries = []
	try:
		all_adorned = bknd_core.execute_sql_query("SELECT id_item FROM items WHERE id_server = %s " + 
			"AND id_item IN (SELECT id_item FROM items_prop WHERE name = 'adorned' AND value = 'true')",
			( server.id, )
		)

		all_adorned = tuple(map(lambda a : a[0], all_adorned))
 
		if len(all_adorned) == 0:
			return format_board(entries = entries, title = ewcfg.leaderboard_fashion)

		all_basefresh = bknd_core.execute_sql_query("SELECT id_item, value FROM items_prop WHERE name = 'freshness' " + 
			"AND id_item IN %s",
			( all_adorned, )
		)

		all_users = bknd_core.execute_sql_query("SELECT id_item, id_user FROM items WHERE id_item IN %s", ( all_adorned, ))


		fresh_map = {}

		user_fresh = {}
		for row in all_basefresh:
			basefresh = int(row[1])
			fresh_map[row[0]] = basefresh

		for row in all_users:
			user_fresh[row[1]] = 0

		for row in all_users:
			item_fresh = fresh_map.get(row[0])
			if type(item_fresh) != int:
				item_fresh = 0
			user_fresh[row[1]] += item_fresh

		user_ids = sorted(user_fresh, key=lambda u : user_fresh[u], reverse=True)

		
		top_five = []

		current_user = None

		max_fresh = lambda base : base * 50 + 100

		while len(user_ids) > 0 and (len(top_five) < 5 or top_five[-1].freshness < max_fresh(user_fresh.get(user_ids[0]))):
			current_user = EwUser(id_user = user_ids.pop(0), id_server = server.id, data_level = 2)

			top_five.append(current_user)

			top_five.sort(key=lambda u : u.freshness, reverse=True)
			
			top_five = top_five[:5]

		

		data = []

		for user in top_five:
			player_data = EwPlayer(id_user = user.id_user)

			data.append([player_data.display_name, user.life_state, user.faction, user.freshness])

		if data != None:
			for row in data:
				if row != None:
					entries.append(row)
	except:
		ewutils.logMsg("Error occured while fetching fashion leaderboard")
	
	return format_board(entries = entries, title = ewcfg.leaderboard_fashion)

def make_slimeoids_top_board(server = None):
	board = "{mega} ▓▓▓▓▓ TOP SLIMEOIDS (CLOUT) ▓▓▓▓▓ {mega}\n".format(
		mega = "<:megaslime:436877747240042508>"
	)

	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		cursor.execute((
			"SELECT pl.display_name, sl.name, sl.clout " +
			"FROM slimeoids AS sl " +
			"INNER JOIN players AS pl ON sl.id_user = pl.id_user " +
			"WHERE sl.id_server = %s AND sl.life_state = 2 " +
			"ORDER BY sl.clout DESC LIMIT 3"
		), (
			server.id,
		))

		data = cursor.fetchall()
		if data != None:
			for row in data:
				board += "{} `{:_>3} | {}'s {}`\n".format(
					ewcfg.emote_blank,
					row[2],
					row[0].replace("`",""),
					row[1].replace("`","")
				)
	finally:
		# Clean up the database handles.
		cursor.close()
		bknd_core.databaseClose(conn_info)

	return board

def make_zines_top_board(server = None):
	board = "{zine} ▓▓▓▓▓ BESTSELLING ZINES ▓▓▓▓▓ {zine}\n".format(
		zine = "<:zine:655854388761460748>"
	)

	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		cursor.execute((
			"SELECT b.title, b.author, b.sales " +
			"FROM books as b " +
			"WHERE b.id_server = %s AND b.book_state = 1 " +
			"ORDER BY b.sales DESC LIMIT 5"
		), (
			server.id,
		))

		data = cursor.fetchall()
		if data != None:
			for row in data:
				board += "{} `{:_>3} | {} by {}`\n".format(
					ewcfg.emote_blank,
					row[2],
					row[0].replace("`",""),
					row[1].replace("`","")
				)
	finally:
		# Clean up the database handles.
		cursor.close()
		bknd_core.databaseClose(conn_info)

	return board

def make_userdata_board(server = None, category = "", title = "", lowscores = False, rows = 5, divide_by = 1):
	entries = []
	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		cursor.execute("SELECT {name}, {state}, {faction}, {category} FROM users, players WHERE users.id_server = %s AND users.{id_user} = players.{id_user} AND users.{state} != {state_kingpin} ORDER BY {category} {order} LIMIT {limit}".format(
			name = ewcfg.col_display_name,
			state = ewcfg.col_life_state,
			faction = ewcfg.col_faction,
			category = category,
			id_user = ewcfg.col_id_user,
			state_kingpin = ewcfg.life_state_kingpin,
			order = ('DESC' if lowscores == False else 'ASC'),
			limit = rows
		), (
			server.id, 
		))
		i = 0
		row = cursor.fetchone()
		while (row != None) and (i < rows):
			if row[1] == ewcfg.life_state_kingpin or row[1] == ewcfg.life_state_grandfoe or row[1] == ewcfg.life_state_lucky:
				row = cursor.fetchone()
			else:
				entries.append(row)
				row = cursor.fetchone()
				i += 1

	finally:
		# Clean up the database handles.
		cursor.close()
		bknd_core.databaseClose(conn_info)

	return format_board(entries = entries, title = title, divide_by = divide_by)

def make_statdata_board(server = None, category = "", title = "", lowscores = False, rows = 5, divide_by = 1):
	entries = []
	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		cursor.execute("SELECT {name}, {state}, {faction}, stats.{category_value} FROM users, players, stats WHERE users.id_server = %s AND users.{id_user} = players.{id_user} AND stats.id_server = users.id_server AND stats.{id_user} = users.{id_user} AND stats.{category_name} = %s ORDER BY stats.{category_value} {order} LIMIT {limit}".format(
			name = ewcfg.col_display_name,
			state = ewcfg.col_life_state,
			faction = ewcfg.col_faction,
			category_name = ewcfg.col_stat_metric,
			category_value = ewcfg.col_stat_value,
			id_user = ewcfg.col_id_user,
			order = ('DESC' if lowscores == False else 'ASC'),
			limit = rows
		), (
			server.id, 
			category
		))

		i = 0
		row = cursor.fetchone()
		while (row != None) and (i < rows):
			if row[1] == ewcfg.life_state_kingpin or row[1] == ewcfg.life_state_grandfoe or row[1] == ewcfg.life_state_lucky:
				row = cursor.fetchone()
			else:
				entries.append(row)
				row = cursor.fetchone()
				i += 1

	finally:
		# Clean up the database handles.
		cursor.close()
		bknd_core.databaseClose(conn_info)

	return format_board(entries = entries, title = title, divide_by = divide_by)
def make_kingpin_board(server = None, title = ""):
	entries = []
	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()

		cursor.execute("SELECT {name}, {state}, {faction}, {category} FROM users, players WHERE users.id_server = %s AND {state} = %s AND users.{id_user} = players.{id_user} ORDER BY {category} DESC".format(
			name = ewcfg.col_display_name,
			state = ewcfg.col_life_state,
			faction = ewcfg.col_faction,
			category = ewcfg.col_slimes,
			id_user = ewcfg.col_id_user
		), (
			server.id, 
			ewcfg.life_state_kingpin
		))

		rows = cursor.fetchall()
		for row in rows:
			entries.append(row)

	finally:
		# Clean up the database handles.
		cursor.close()
		bknd_core.databaseClose(conn_info)

	return format_board(entries = entries, title = title)


def make_district_control_board(id_server, title):
	entries = []
	
	districts = []
	for poi in poi_static.poi_list:
		if poi.is_district:
			districts.append(poi.id_poi)
			
	rowdy_districts = 0
	killer_districts = 0

	for district in districts:
		district_data = EwDistrict(district = district, id_server = id_server)
		if district_data.controlling_faction == ewcfg.faction_rowdys:
			rowdy_districts += 1
		elif district_data.controlling_faction == ewcfg.faction_killers:
			killer_districts += 1

	rowdy_entry = [ewcfg.faction_rowdys.capitalize(), rowdy_districts]
	killer_entry = [ewcfg.faction_killers.capitalize(), killer_districts]

	return format_board(
		entries = [rowdy_entry, killer_entry] if rowdy_districts > killer_districts else [killer_entry, rowdy_entry],
		title = title,
		entry_type = ewcfg.entry_type_districts
	)

#SLIMERNALIA
def make_slimernalia_board(server, title):
	entries = []
	data = bknd_core.execute_sql_query(
		"SELECT {display_name}, {state}, {faction}, FLOOR({festivity}) + COALESCE(sigillaria, 0) + FLOOR({festivity_from_slimecoin}) as total_festivity FROM users "\
		"LEFT JOIN (SELECT id_user, COUNT(*) * 1000 as sigillaria FROM items INNER JOIN items_prop ON items.{id_item} = items_prop.{id_item} WHERE {name} = %s AND {value} = %s GROUP BY items.{id_user}) f on users.{id_user} = f.{id_user}, players "\
		"WHERE users.{id_server} = %s AND users.{id_user} = players.{id_user} ORDER BY total_festivity DESC LIMIT 5".format(
			id_user = ewcfg.col_id_user,
			id_server = ewcfg.col_id_server,
			id_item = ewcfg.col_id_item,
			festivity = ewcfg.col_festivity,
			festivity_from_slimecoin = ewcfg.col_festivity_from_slimecoin,
			name = ewcfg.col_name,
			display_name = ewcfg.col_display_name,
			value = ewcfg.col_value,
			state = ewcfg.col_life_state,
			faction = ewcfg.col_faction
		), (
			"id_furniture",
			ewcfg.item_id_sigillaria,
			server.id
		)
	)

	for row in data:
		entries.append(row)
	
	return format_board(entries = entries, title = title)

#SWILLDERMUK
def make_gambit_leaderboard(server, title, rows = 3):
	entries = []
	
	lowgambit = False
	if title == ewcfg.leaderboard_gambit_high:
		lowgambit = False
	else:
		lowgambit = True
	
	try:
		conn_info = bknd_core.databaseConnect()
		conn = conn_info.get('conn')
		cursor = conn.cursor()
	
		cursor.execute(
			"SELECT {name}, {state}, {faction}, {gambit} FROM users, players WHERE users.id_server = %s AND users.{id_user} = players.{id_user} ORDER BY {gambit} {order} LIMIT {limit}".format(
				name=ewcfg.col_display_name,
				gambit=ewcfg.col_gambit,
				state=ewcfg.col_life_state,
				faction=ewcfg.col_faction,
				id_user=ewcfg.col_id_user,
				order=('DESC' if lowgambit == False else 'ASC'),
				limit=rows
			), (
				server.id,
			))
	
		i = 0
		row = cursor.fetchone()
		while (row != None) and (i < rows):
			if row[1] == ewcfg.life_state_kingpin or row[1] == ewcfg.life_state_grandfoe or row[1] == ewcfg.life_state_lucky:
				row = cursor.fetchone()
			else:
				entries.append(row)
				row = cursor.fetchone()
				i += 1

	finally:
		# Clean up the database handles.
		cursor.close()
		bknd_core.databaseClose(conn_info)

	return format_board(entries=entries, title=title)

"""
	convert leaderboard data into a message ready string 
"""
def format_board(entries = None, title = "", entry_type = "player", divide_by = 1):
	result = ""
	result += board_header(title)

	for entry in entries:
		result += board_entry(entry, entry_type, divide_by)

	return result

def board_header(title):
	emote = None
	emote2 = None

	bar = " ▓▓▓▓▓"

	if title == ewcfg.leaderboard_slimes:
		emote = ewcfg.emote_slime2
		bar += "▓▓▓ "

	elif title == ewcfg.leaderboard_slimecoin:
		emote = ewcfg.emote_slimecoin
		bar += " "

	elif title == ewcfg.leaderboard_ghosts:
		emote = ewcfg.emote_negaslime
		bar += "▓ "

	elif title == ewcfg.leaderboard_bounty:
		emote = ewcfg.emote_slimegun
		bar += "▓ "

	elif title == ewcfg.leaderboard_kingpins:
		emote = ewcfg.emote_theeye
		bar += " "

	elif title == ewcfg.leaderboard_districts:
		emote = ewcfg.emote_nlacakanm
		bar += " "

	elif title == ewcfg.leaderboard_donated:
		emote = ewcfg.emote_slimecorp
		bar += " "
	
	elif title == ewcfg.leaderboard_slimernalia:
		emote = ewcfg.emote_slimeheart
		bar += " "

	elif title == ewcfg.leaderboard_degradation:
		emote = ewcfg.emote_slimeskull
		bar += " "

	elif title == ewcfg.leaderboard_shamblers_killed:
		emote = ewcfg.emote_slimeshot
		bar += " "
	
	elif title == ewcfg.leaderboard_gambit_high:
		emote = ewcfg.emote_janus1
		emote2 = ewcfg.emote_janus2
		bar += " "
	
	elif title == ewcfg.leaderboard_gambit_low:
		emote = ewcfg.emote_janus1
		emote2 = ewcfg.emote_janus2
		bar += " "

	elif title == ewcfg.leaderboard_fashion:
		emote = ewcfg.emote_111
		bar += " "
		
	if emote2 != None:
		return emote + bar + title + bar + emote2 + "\n"
	else:
		return emote + bar + title + bar + emote + "\n"

def board_entry(entry, entry_type, divide_by):
	result = ""

	if entry_type == ewcfg.entry_type_player:
		faction = ewutils.get_faction(life_state = entry[1], faction = entry[2])
		faction_symbol = ewutils.get_faction_symbol(faction, entry[2])

		number = int(entry[3] / divide_by)

		if number > 999999999:
			num_str = "{:.3e}".format(number)
		else:
			num_str = "{:,}".format(number)

		result = "{} `{:_>15} | {}`\n".format(
			faction_symbol,
			num_str,
			entry[0].replace("`","")
		)

	elif entry_type == ewcfg.entry_type_districts:
		faction = entry[0]
		districts = entry[1]
		faction_symbol = ewutils.get_faction_symbol(faction.lower())

		result = "{} `{:_>15} | {}`\n".format(
			faction_symbol,
			faction,
			districts
		)

	return result
