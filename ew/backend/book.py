from . import core as bknd_core
from ..static import cfg as ewcfg
from ..utils import core as ewutils

class EwBook:
	id_book = 0
	id_server = -1
	id_user = -1

	# The name of the book
	title = ""

	# The name of the author
	author = ""

	# If its been published or not
	book_state = 0

	# The in-game day it was published
	date_published = 0

	# Genre of zine (0-7)
	genre = -1

	# Length of the book after publishing
	length = 0

	# The total sales of the published book
	sales = 0

	# The average rating of the published book
	rating = 0

	# The number of people who have rated the book
	rates = 0

	# The number of pages in a book (between 5 and 20)
	pages = 10

	# The contents of the book
	book_pages = {}

	def __init__(
			self,
			id_book = None,
			member = None,
			book_state = None,
	):
		self.book_pages = {}

		query_suffix = ""
		if id_book is not None:
			self.id_book = id_book
			query_suffix = " id_book = {}".format(self.id_book)

		elif member is not None:
			self.id_server = member.guild.id
			self.id_user = member.id
			query_suffix = " id_server = {} AND id_user = {}".format(self.id_server, self.id_user)
			if book_state is not None:
				self.book_state = book_state
				query_suffix += " AND book_state = {}".format(self.book_state)

		try:
			conn_info = bknd_core.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Retrieve object
			cursor.execute("SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM books WHERE{}".format(
				ewcfg.col_id_book,
				ewcfg.col_id_user,
				ewcfg.col_id_server,
				ewcfg.col_title,
				ewcfg.col_author,
				ewcfg.col_book_state,
				ewcfg.col_date_published,
				ewcfg.col_genre,
				ewcfg.col_length,
				ewcfg.col_sales,
				ewcfg.col_rating,
				ewcfg.col_rates,
				ewcfg.col_pages,
				query_suffix,
			))
			result = cursor.fetchone();

			if result != None:
				# Record found: apply the data to this object.
				self.id_book = result[0]
				self.id_user = result[1]
				self.id_server = result[2]
				self.title = result[3]
				self.author = result[4]
				self.book_state = result[5]
				self.date_published = result[6]
				self.genre = result[7]
				self.length = result[8]
				self.sales = result[9]
				self.rating = result[10]
				self.rates = result[11]
				self.pages = result[12]

				# Retrieve additional properties
				cursor.execute("SELECT {}, {} FROM book_pages WHERE id_book = %s".format(
					ewcfg.col_page,
					ewcfg.col_contents
				), (
					self.id_book,
				))

				for row in cursor:
					# this try catch is only necessary as long as extraneous props exist in the table
					try:
						self.book_pages[row[0]] = row[1]
					except:
						ewutils.logMsg("extraneous book_pages row detected.")

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
			cursor.execute(
				"REPLACE INTO books({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
					ewcfg.col_id_book,
					ewcfg.col_id_server,
					ewcfg.col_id_user,
					ewcfg.col_title,
					ewcfg.col_author,
					ewcfg.col_book_state,
					ewcfg.col_date_published,
					ewcfg.col_genre,
					ewcfg.col_length,
					ewcfg.col_sales,
					ewcfg.col_rating,
					ewcfg.col_rates,
					ewcfg.col_pages,
				), (
					self.id_book,
					self.id_server,
					self.id_user,
					self.title,
					self.author,
					self.book_state,
					self.date_published,
					self.genre,
					self.length,
					self.sales,
					self.rating,
					self.rates,
					self.pages,
				))

			# Remove all existing property rows.
			cursor.execute("DELETE FROM book_pages WHERE {} = %s".format(
				ewcfg.col_id_book
			), (
				self.id_book,
			))

			# Write out all current property rows.
			for name in self.book_pages:
				cursor.execute("INSERT INTO book_pages({}, {}, {}) VALUES(%s, %s, %s)".format(
					ewcfg.col_id_book,
					ewcfg.col_page,
					ewcfg.col_contents
				), (
					self.id_book,
					name,
					self.book_pages[name]
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			bknd_core.databaseClose(conn_info)


# The purpose of this is to make finding the average rating easier and to measure sales based on the amount of different people that buy them.
class EwBookSale:
	id_book = 0
	id_user = -1
	id_server = -1

	# If a user bought the book. 0 is not bought.
	bought = 0

	# A user's rating of a book. 0 is unrated.
	rating = 0

	def __init__(
			self,
			id_book = None,
			member = None,
	):
		self.id_book = id_book
		self.id_user = member.id
		self.id_server = member.guild.id

		try:
			conn_info = bknd_core.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor()

			# Retrieve object
			cursor.execute("SELECT {}, {} FROM book_sales WHERE {} = %s AND {} = %s AND {} = %s".format(
				ewcfg.col_bought,
				ewcfg.col_rating,
				ewcfg.col_id_book,
				ewcfg.col_id_user,
				ewcfg.col_id_server,
			), (
				self.id_book,
				self.id_user,
				self.id_server,
			))
			result = cursor.fetchone();

			if result != None:
				# Record found: apply the data to this object.
				self.bought = result[0]
				self.rating = result[1]

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
			cursor.execute(
				"REPLACE INTO book_sales({}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s)".format(
					ewcfg.col_id_book,
					ewcfg.col_id_server,
					ewcfg.col_id_user,
					ewcfg.col_bought,
					ewcfg.col_rating,
				), (
					self.id_book,
					self.id_server,
					self.id_user,
					self.bought,
					self.rating,
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			bknd_core.databaseClose(conn_info)

