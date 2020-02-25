import asyncio
import math
import time
import random

import discord


class EwTrauma:

	# The mutation's name
	id_trauma = ""

	# String used to describe the mutation when you !data yourself
	str_describe_self = ""

	# String used to describe the mutation when you !data another player
	str_describe_other = ""


	def __init__(self,
		id_mutation = "",
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



