from ..static import cfg as ewcfg

""" slimeoid model object """
class EwBody:
	id_body = ""
	alias = []
	str_create = ""
	str_body = ""
	def __init__(
		self,
		id_body = "",
		alias = [],
		str_create = "",
		str_body = "",
		str_observe = ""
	):
		self.id_body = id_body
		self.alias = alias
		self.str_create = str_create
		self.str_body = str_body
		self.str_observe = str_observe

class EwHead:
	id_head = ""
	alias = []
	str_create = ""
	str_head = ""
	def __init__(
		self,
		id_head = "",
		alias = [],
		str_create = "",
		str_head = "",
		str_feed = "",
		str_fetch = ""
	):
		self.id_head = id_head
		self.alias = alias
		self.str_create = str_create
		self.str_head = str_head
		self.str_feed = str_feed
		self.str_fetch = str_fetch
	
class EwMobility:
	id_mobility = ""
	alias = []
	str_advance = ""
	str_retreat = ""
	str_create = ""
	str_mobility = ""
	def __init__(
		self,
		id_mobility = "",
		alias = [],
		str_advance = "",
		str_advance_weak = "",
		str_retreat = "",
		str_retreat_weak = "",
		str_create = "",
		str_mobility = "",
		str_defeat = "",
		str_walk = ""
	):
		self.id_mobility = id_mobility
		self.alias = alias
		self.str_advance = str_advance
		self.str_advance_weak = str_advance_weak
		self.str_retreat = str_retreat
		self.str_retreat_weak = str_retreat_weak
		self.str_create = str_create
		self.str_mobility = str_mobility
		self.str_defeat = str_defeat
		self.str_walk = str_walk

class EwOffense:
	id_offense = ""
	alias = []
	str_attack = ""
	str_create = ""
	str_offense = ""
	def __init__(
		self,
		id_offense = "",
		alias = [],
		str_attack = "",
		str_attack_weak = "",
		str_attack_coup = "",
		str_create = "",
		str_offense = "",
		str_observe = ""
	):
		self.id_offense = id_offense
		self.alias = alias
		self.str_attack = str_attack
		self.str_attack_weak = str_attack_weak
		self.str_attack_coup = str_attack_coup
		self.str_create = str_create
		self.str_offense = str_offense
		self.str_observe = str_observe

class EwDefense:
	id_defense = ""
	alias = []
	str_create = ""
	str_defense = ""
	id_resistance = ""
	id_weakness = ""
	str_resistance = ""
	str_weakness = ""
	str_abuse = ""
	def __init__(
		self,
		id_defense = "",
		alias = [],
		str_create = "",
		str_defense = "",
		str_armor = "",
		str_pet = "",
		id_resistance = "",
		id_weakness = "",
		str_resistance = "",
		str_weakness = "",
		str_abuse = "",
	):
		self.id_defense = id_defense
		self.alias = alias
		self.str_create = str_create
		self.str_defense = str_defense
		self.str_armor = str_armor
		self.str_pet = str_pet
		self.id_resistance = id_resistance
		self.id_weakness = id_weakness
		self.str_resistance = str_resistance
		self.str_weakness = str_weakness
		self.str_abuse = str_abuse

	def get_resistance(self, offense = None):
		if offense is None:
			return ""

		if offense.id_offense == self.id_resistance:
			return self.str_resistance

		else:
			return ""

	def get_weakness(self, special = None):
		if special is None:
			return ""

		if special.id_special == self.id_weakness:
			return self.str_weakness

		else:
			return ""

class EwSpecial:
	id_special = ""
	alias = []
	str_special_attack = ""
	str_create = ""
	str_special = ""
	def __init__(
		self,
		id_special = "",
		alias = [],
		str_special_attack = "",
		str_special_attack_weak = "",
		str_special_attack_coup = "",
		str_create = "",
		str_special = "",
		str_observe = ""
	):
		self.id_special = id_special
		self.alias = alias
		self.str_special_attack = str_special_attack
		self.str_special_attack_weak = str_special_attack_weak
		self.str_special_attack_coup = str_special_attack_coup
		self.str_create = str_create
		self.str_special = str_special
		self.str_observe = str_observe

class EwBrain:
	id_brain = ""
	alias = []
	str_create = ""
	str_brain = ""
	def __init__(
		self,
		id_brain = "",
		alias = [],
		str_create = "",
		str_brain = "",
		str_dissolve = "",
		str_spawn = "",
		str_revive = "",
		str_death = "",
		str_victory = "",
		str_battlecry = "",
		str_battlecry_weak = "",
		str_movecry = "",
		str_movecry_weak = "",
		str_kill = "",
		str_walk = "",
		str_pet = "",
		str_observe = "",
		str_feed = "",
		get_strat = None,
		str_abuse = "",
	):
		self.id_brain = id_brain
		self.alias = alias
		self.str_create = str_create
		self.str_brain = str_brain
		self.str_dissolve = str_dissolve
		self.str_spawn = str_spawn
		self.str_revive = str_revive
		self.str_death = str_death
		self.str_victory = str_victory
		self.str_battlecry = str_battlecry
		self.str_battlecry_weak = str_battlecry_weak
		self.str_movecry = str_movecry
		self.str_movecry_weak = str_movecry_weak
		self.str_kill = str_kill
		self.str_pet = str_pet
		self.str_walk = str_walk
		self.str_observe = str_observe
		self.str_feed = str_feed
		self.get_strat = get_strat
		self.str_abuse = str_abuse


"""
	Slimeoid Food Items
"""
class EwSlimeoidFood:
	item_type = "item"
	id_item = " "
	alias = []
	context = "slimeoidfood"
	str_name = ""
	str_desc = ""
	ingredients = ""
	acquisition = ""
	price = 0
	vendors = []

	increase = ""
	decrease = ""

	def __init__(
		self,
		id_item = " ",
		alias = [],
		str_name = "",
		str_desc = "",
		ingredients = "",
		acquisition = "",
		price = 0,
		vendors = [],
		increase = "",
		decrease = "",
	):
		self.item_type = ewcfg.it_item
		self.id_item = id_item
		self.alias = alias
		self.context = ewcfg.context_slimeoidfood
		self.str_name = str_name
		self.str_desc = str_desc
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.price = price
		self.vendors = vendors
		self.increase = increase
		self.decrease = decrease

class EwHue:
	id_hue = ""
	alias = []
	str_saturate = ""
	str_name= ""
	str_desc = ""
	effectiveness = {}
	palette = []
	is_neutral = False
	def __init__(
		self,
		id_hue = "",
		alias = [],
		str_saturate = "",
		str_name= "",
		str_desc = "",
		effectiveness = {},
		palette = [],
		is_neutral = False
	):
		self.id_hue = id_hue
		self.alias = alias
		self.str_saturate = str_saturate
		self.str_name= str_name
		self.str_desc = str_desc
		self.effectiveness = effectiveness
		self.style_palette = palette
		self.is_neutral = is_neutral

