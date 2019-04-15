import time

# import ewcmd
import ewitem
import ewrolemgr
import ewutils
import ewcfg
import ewstats
from ew import EwUser

class EwMarket:
	id_server = ""

	clock = 0
	weather = 'sunny'
	day = 0

	slimes_casino = 0
	slimes_revivefee = 0

	market_rate = 1000
	exchange_rate = 1000000
	boombust = 0
	time_lasttick = 0
	negaslime = 0
	decayed_slimes = 0

	""" Load the market data for this server from the database. """
	def __init__(self, id_server = None):
		if(id_server != None):
			self.id_server = id_server

			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute("SELECT {time_lasttick}, {slimes_revivefee}, {negaslime}, {clock}, {weather}, {day}, {decayed_slimes} FROM markets WHERE id_server = %s".format(
					time_lasttick = ewcfg.col_time_lasttick,
					slimes_revivefee = ewcfg.col_slimes_revivefee,
					negaslime = ewcfg.col_negaslime,
					clock = ewcfg.col_clock,
					weather = ewcfg.col_weather,
					day = ewcfg.col_day,
					decayed_slimes = ewcfg.col_decayed_slimes
				), (self.id_server, ))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.time_lasttick = result[0]
					self.slimes_revivefee = result[1]
					self.negaslime = result[2]
					self.clock = result[3]
					self.weather = result[4]
					self.day = result[5]
					self.decayed_slimes = result[6]
				else:
					# Create a new database entry if the object is missing.
					cursor.execute("REPLACE INTO markets(id_server) VALUES(%s)", (id_server, ))

					conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save market data object to the database. """
	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save the object.
			cursor.execute("REPLACE INTO markets ({id_server}, {time_lasttick}, {slimes_revivefee}, {negaslime}, {clock}, {weather}, {day}, {decayed_slimes}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)".format(
				id_server = ewcfg.col_id_server,
				time_lasttick = ewcfg.col_time_lasttick,
				slimes_revivefee = ewcfg.col_slimes_revivefee,
				negaslime = ewcfg.col_negaslime,
				clock = ewcfg.col_clock,
				weather = ewcfg.col_weather,
				day = ewcfg.col_day,
				decayed_slimes = ewcfg.col_decayed_slimes
			), (
				self.id_server,
				self.time_lasttick,
				self.slimes_revivefee,
				self.negaslime,
				self.clock,
				self.weather,
				self.day,
				self.decayed_slimes
			))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

class EwStock:
	id_server = ""

	# The stock's identifying string
	id_stock = ""

	market_rate = 1000

	exchange_rate = 1000000

	boombust = 0

	total_shares = 0

	timestamp = 0

	previous_entry = 0

	def __init__(self, id_server = None, stock = None):
		if id_server is not None and stock is not None:
			self.id_server = id_server
			self.id_stock = stock

			data = ewutils.execute_sql_query("SELECT {stock}, {market_rate}, {exchange_rate}, {boombust}, {total_shares}, {timestamp} FROM stocks WHERE id_server = %s AND {stock} = %s ORDER BY {timestamp} DESC".format(
				stock = ewcfg.col_stock,
				market_rate = ewcfg.col_market_rate,
				exchange_rate = ewcfg.col_exchange_rate,
				boombust = ewcfg.col_boombust,
				total_shares = ewcfg.col_total_shares,
				timestamp = ewcfg.col_timestamp
			), (
				id_server,
				stock
			))

			# slimecoin_total = ewutils.execute_sql_query()

			if len(data) > 0:  # if data is not empty, i.e. it found an entry
				# data is always a two-dimensional array and if we only fetch one row, we have to type data[0][x]
				self.id_stock = data[0][0]
				self.market_rate = data[0][1]
				self.exchange_rate = data[0][2]
				self.boombust = data[0][3]
				self.total_shares = data[0][4]
				self.timestamp = data[0][5]
				self.previous_entry = data[1] if len(data) > 1 else 0 #gets the previous stock
			else:  # create new entry
				ewutils.execute_sql_query("INSERT INTO stocks ({id_server}, {stock}, {timestamp}) VALUES (%s, %s, %s)".format(
					id_server = ewcfg.col_id_server,
					stock = ewcfg.col_stock,
					timestamp = ewcfg.col_timestamp
				), (
					id_server,
					stock,
					time.time(),
				))

	def persist(self):
		ewutils.execute_sql_query("INSERT INTO stocks ({id_server}, {stock}, {market_rate}, {exchange_rate}, {boombust}, {total_shares}, {timestamp}) VALUES(%s, %s, %s, %s, %s, %s, %s)".format(
			id_server = ewcfg.col_id_server,
			stock = ewcfg.col_stock,
			market_rate = ewcfg.col_market_rate,
			exchange_rate = ewcfg.col_exchange_rate,
			boombust = ewcfg.col_boombust,
			total_shares = ewcfg.col_total_shares,
			timestamp = ewcfg.col_timestamp
		), (
			self.id_server,
			self.id_stock,
			self.market_rate,
			self.exchange_rate,
			self.boombust,
			self.total_shares,
			time.time(),
		))

""" player invests slime in the market """
async def invest(cmd):
	user_data = EwUser(member = cmd.message.author)
	market_data = EwMarket(id_server = cmd.message.author.server.id)
	time_now = int(time.time())

	if user_data.poi != ewcfg.poi_id_stockexchange:
		# Only allowed in the stock exchange.
		response = ewcfg.str_exchange_channelreq.format(currency = "slime", action = "invest")
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		return

	roles_map_user = ewutils.getRoleMap(cmd.message.author.roles)
	if ewcfg.role_rowdyfucker in roles_map_user or ewcfg.role_copkiller in roles_map_user:
		# Disallow investments by RF and CK kingpins.
		response = "You're too powerful to be playing the market."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		value = None
		if cmd.tokens_count > 1:
			value = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)

		if value != None:
			if value < 0:
				value = user_data.slimecoin
			if value <= 0:
				value = None

		if value != None:
			# Apply a brokerage fee of ~5% (rate * 1.05)
			exchange_rate = (market_data.exchange_rate / 1000000.0)
			feerate = 1.05

			# The user can only buy a whole number of coins, so adjust their cost based on the actual number of coins purchased.
			gross_coins = int(value / exchange_rate)

			fee = int((gross_coins * feerate) - gross_coins)

			net_coins = gross_coins - fee

			if value > user_data.slimes:
				response = "You don't have that much slime to invest."
			elif user_data.time_lastinvest + ewcfg.cd_invest > time_now:
				# Limit frequency of investments.
				response = ewcfg.str_exchange_busy.format(action = "invest")
			else:
				user_data.slimes -= value
				user_data.slimecoin += net_coins
				user_data.time_lastinvest = time_now

				response = "You invest {slime:,} slime and receive {coin:,} SlimeCoin. Your slimebroker takes his nominal fee of {fee:,} SlimeCoin.".format(
					slime = value, coin = net_coins, fee = fee)

				user_data.persist()
				market_data.persist()

		else:
			response = ewcfg.str_exchange_specify.format(currency = "slime", action = "invest")

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" player withdraws slime from the market """
async def withdraw(cmd):
	user_data = EwUser(member = cmd.message.author)
	market_data = EwMarket(id_server = cmd.message.author.server.id)
	time_now = int(time.time())

	if user_data.poi != ewcfg.poi_id_stockexchange:
		# Only allowed in the stock exchange.
		response = ewcfg.str_exchange_channelreq.format(currency = "SlimeCoin", action = "withdraw")
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	else:
		value = None
		if cmd.tokens_count > 1:
			value = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)

		if value != None:
			if value < 0:
				value = user_data.slimecoin
			if value <= 0:
				value = None

		if value != None:

			exchange_rate = (market_data.exchange_rate / 1000000.0)

			coins = value
			slimes = int(value * exchange_rate)

			if value > user_data.slimecoin:
				response = "You don't have that many SlimeCoin to exchange."
			elif user_data.time_lastinvest + ewcfg.cd_invest > time_now:
				# Limit frequency of withdrawals
				response = ewcfg.str_exchange_busy.format(action = "withdraw")
			else:
				user_data.slimes += slimes
				user_data.slimecoin -= coins
				user_data.time_lastinvest = time_now

				response = "You exchange {coins:,} SlimeCoin for {slimes:,} slime.".format(coins = coins,
																							 slimes = slimes)
				user_data.persist()
				market_data.persist()

		else:
			response = ewcfg.str_exchange_specify.format(currency = "SlimeCoin", action = "withdraw")

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" donate slime to slimecorp in exchange for slimecoin """
async def donate(cmd):
	time_now = int(time.time())

	if cmd.message.channel.name != ewcfg.channel_slimecorphq:
		# Only allowed in SlimeCorp HQ.
		response = "You must go to SlimeCorp HQ to donate slime."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		return

	user_data = EwUser(member = cmd.message.author)

	value = None
	if cmd.tokens_count > 1:
		value = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)

	if value != None:
		if value < 0:
			value = user_data.slimes
		if value <= 0:
			value = None

	if value != None and value < ewcfg.slimecoin_exchangerate:
		response = "You must volunteer to donate at least %d slime to receive compensation." % ewcfg.slimecoin_exchangerate

	elif value != None:
		# Amount of slime invested.
		cost_total = int(value)
		coin_total = int(value / ewcfg.slimecoin_exchangerate)

		if user_data.slimes < cost_total:
			response = "Acid-green flashes of light and bloodcurdling screams emanate from small window of SlimeCorp HQ. Unfortunately, you did not survive the procedure. Your body is dumped down a disposal chute to the sewers."
			user_data.die(cause = ewcfg.cause_donation)
			user_data.persist()
			# Assign the corpse role to the player. He dead.
			await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
			sewerchannel = ewutils.get_channel(cmd.message.server, ewcfg.channel_sewers)
			await ewutils.send_message(cmd.client, sewerchannel, "{} ".format(ewcfg.emote_slimeskull) + ewutils.formatMessage(cmd.message.author, "You have died in a medical mishap. {}".format(ewcfg.emote_slimeskull)))
		else:
			# Do the transfer if the player can afford it.
			user_data.change_slimes(n = -cost_total, source = ewcfg.source_spending)
			user_data.change_slimecoin(n = coin_total, coinsource = ewcfg.coinsource_donation)
			user_data.time_lastinvest = time_now

			# Persist changes
			user_data.persist()

			response = "You stumble out of a Slimecorp HQ vault room in a stupor. You don't remember what happened in there, but your body hurts and you've got {slimecoin:,} shiny new SlimeCoin in your pocket.".format(slimecoin = coin_total)

	else:
		response = ewcfg.str_exchange_specify.format(currency = "slime", action = "donate")

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

""" transfer slimecoin between players """
async def xfer(cmd):
	time_now = int(time.time())

	if cmd.message.channel.name != ewcfg.channel_stockexchange:
		# Only allowed in the stock exchange.
		response = ewcfg.str_exchange_channelreq.format(currency = "SlimeCoin", action = "transfer")
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		return

	if cmd.mentions_count != 1:
		# Must have exactly one target to send to.
		response = "Mention the player you want to send SlimeCoin to."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		return

	member = cmd.mentions[0]
	target_data = EwUser(member = member)

	if target_data.life_state == ewcfg.life_state_kingpin:
		# Disallow transfers to RF and CK kingpins.
		response = "You can't transfer SlimeCoin to a known criminal warlord."
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		return

	user_data = EwUser(member = cmd.message.author)
	market_data = EwMarket(id_server = cmd.message.author.server.id)

	if cmd.message.author.id == member.id:
		user_data.id_killer = cmd.message.author.id
		user_data.die(cause = ewcfg.cause_suicide)
		user_data.persist()

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, "Gaming the slimeconomy is punishable by death. SlimeCorp soldiers execute you immediately."))
		await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)
		return

	# Parse the slime value to send.
	value = None
	if cmd.tokens_count > 1:
		value = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True)

	if value != None:
		if value < 0:
			value = user_data.slimes
		if value <= 0:
			value = None

	if value != None:
		# Cost including the 5% transfer fee.
		cost_total = int(value * 1.05)

		if user_data.slimecoin < cost_total:
			response = "You don't have enough SlimeCoin. ({:,}/{:,})".format(user_data.slimecoin, cost_total)
		else:
			# Do the transfer if the player can afford it.
			target_data.change_slimecoin(n = value, coinsource = ewcfg.coinsource_transfer)
			user_data.change_slimecoin(n = -cost_total, coinsource = ewcfg.coinsource_transfer)
			user_data.time_lastinvest = time_now

			# Persist changes
			response = "You transfer {slime:,} SlimeCoin to {target_name}. Your slimebroker takes his nominal fee of {fee:,} SlimeCoin.".format(slime = value, target_name = member.display_name, fee = (cost_total - value))

			target_data.persist()
			user_data.persist()
	else:
		response = ewcfg.str_exchange_specify.format(currency = "SlimeCoin", action = "transfer")

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" show the current market exchange rate """
async def rate(cmd):
	stock = None
	if cmd.tokens_count > 0:
		stock = ewutils.formatNiceList(cmd.tokens[1:])

	if stock in ewcfg.stocks:
		stock = EwStock(id_server = cmd.message.server.id, stock = stock)
		response = "The current value of {stock} stocks is {cred} SlimeCoin per Share.".format(stock = ewcfg.stock_names.get(stock.id_stock), cred=int(stock.exchange_rate / 1000.0))
	else:
		response = "That's not a valid stock name, please use a proper one, you cunt: {}".format(ewutils.formatNiceList(names = ewcfg.stocks))

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


""" show player's slimecoin balance """
async def slimecoin(cmd):
	response = ""
	user_data = None

	if cmd.mentions_count == 0:
		coins = EwUser(member = cmd.message.author).slimecoin
		response = "You have {:,} SlimeCoin.".format(coins)
	else:
		member = cmd.mentions[0]
		coins = EwUser(member = member).slimecoin
		response = "{} has {:,} SlimeCoin.".format(member.display_name, coins)

	# Send the response to the player.
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


