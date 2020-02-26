import asyncio
import math
import time
import random

import discord


class EwTrauma:

	# The trauma's name
	id_trauma = ""

	# String used to describe the trauma when you !data yourself
	str_describe_self = ""

	# String used to describe the trauma when you !data another player
	str_describe_other = ""


	def __init__(self,
		id_trauma = "",
		str_describe_self = "",
		str_describe_other = "",
		):

		self.id_trauma = id_trauma

		if str_describe_self == "":
			str_describe_self = "You have the {} trauma.".format(self.id_trauma)
		self.str_describe_self = str_describe_self

		if str_describe_other == "":
			str_describe_other = "They have the {} trauma.".format(self.id_trauma)
		self.str_describe_other = str_describe_other


class EwHitzone:
	

	name = ""

	aliases = []

	id_injury = ""

	def __init__(self,
		name = "",
		aliases = [],
		id_injury = "",
	):
		self.name = name
		self.aliases = aliases
		self.id_injury = id_injury


