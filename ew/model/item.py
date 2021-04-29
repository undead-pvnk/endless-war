from ..static import cfg as ewcfg
"""
    EwItemDef is a class used to model base items. These are NOT the items
    owned by players, but rather the description of what those items are.
"""
class EwItemDef:
    # This is the unique reference name for this item.
    item_type = ""

    # If this is true, the item can not be traded or stolen.
    soulbound = False

    # If this value is positive, the item may actually be a pile of the same type of item, up to the specified size.
    stack_max = -1

    # If this value is greater than one, creating this item will actually give the user that many of them.
    stack_size = 1

    # Nice display name for this item.
    str_name = ""

    # The long description of this item's appearance.
    str_desc = ""

    # A map of default additional properties.
    item_props = None

    def __init__(
        self,
        item_type = "",
        str_name = "",
        str_desc = "",
        soulbound = False,
        stack_max = -1,
        stack_size = 1,
        item_props = None
    ):
        self.item_type = item_type
        self.str_name = str_name
        self.str_desc = str_desc
        self.soulbound = soulbound
        self.stack_max = stack_max
        self.stack_size = stack_size
        self.item_props = item_props

"""
    These are unassuming, tangible, multi-faceted, customizable items that you can actually interact with in-game.
"""
class EwGeneralItem:
    item_type = "item"
    id_item = " "
    alias = []
    context = ""
    str_name = ""
    str_desc = ""
    ingredients = ""
    acquisition = ""
    price = 0
    durability = 0
    vendors = []

    def __init__(
        self,
        id_item = " ",
        alias = [],
        context = "",
        str_name = "",
        str_desc = "",
        ingredients = "",
        acquisition = "",
        price = 0,
        durability = 0,
        vendors = [],
    ):
        self.item_type = ewcfg.it_item
        self.id_item = id_item
        self.alias = alias
        self.context = context
        self.str_name = str_name
        self.str_desc = str_desc
        self.ingredients = ingredients
        self.acquisition = acquisition
        self.price = price
        self.durability = durability
        self.vendors = vendors

"""
	Cosmetic item model object
"""
class EwCosmeticItem:
	item_type = "cosmetic"

	# The proper name of the cosmetic item
	id_cosmetic = ""

	# The string name of the cosmetic item
	str_name = ""

	# The text displayed when you !inspect it
	str_desc = ""

	# The text displayed when you !adorn it
	str_onadorn = ""

	# The text displayed when you take it off
	str_unadorn = ""

	# The text displayed when it breaks! Oh no!
	str_onbreak = ""

	# How rare the item is, can be "Plebeian", "Patrician", or "Princeps"
	rarity = ""

	# The stats the item increases/decreases
	stats = {}

	# Some items have special abilities that act like less powerful Mutations
	ability = ""

	# While !adorn'd, this item takes damage-- If this reaches 0, it breaks
	durability = 0

	# How much space this item takes up on your person-- You can only wear so many items at a time, the amount is determined by your level
	size = 0

	# What fashion style the cosmetic belongs to: Goth, jock, prep, nerd
	style = ""

	# How fresh a cosmetic is, in other words how fleek, in other words how godDAMN it is, in other words how good it looks
	freshness = 0

	# The ingredients necessary to make this item via it's acquisition method
	ingredients = ""

	# Cost in SlimeCoin to buy this item.
	price = 0

	# Names of the vendors selling this item.
	vendors = []

	#Whether a cosmetic is a hat or not
	is_hat = False

	def __init__(
		self,
		id_cosmetic = "",
		str_name = "",
		str_desc = "",
		str_onadorn = "",
		str_unadorn = "",
		str_onbreak = "",
		rarity = "",
		stats = {},
		ability = "",
		durability = 0,
		size = 0,
		style = "",
		freshness = 0,
		ingredients = "",
		acquisition = "",
		price = 0,
		vendors = [],
		is_hat = False,

	):
		self.item_type = ewcfg.it_cosmetic

		self.id_cosmetic = id_cosmetic
		self.str_name = str_name
		self.str_desc = str_desc
		self.str_onadorn = str_onadorn
		self.str_unadorn = str_unadorn
		self.str_onbreak = str_onbreak
		self.rarity = rarity
		self.stats = stats
		self.ability = ability
		self.durability = durability
		self.size = size
		self.style = style
		self.freshness = freshness
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.price = price
		self.vendors = vendors
		self.is_hat = is_hat

class EwFurniture:
	item_type = "furniture"

	# The proper name of the furniture item
	id_furniture = ""

	# The string name of the furniture item
	str_name = ""

	# The text displayed when you look at it
	str_desc = ""

	# How rare the item is, can be "Plebeian", "Patrician", or "Princeps"
	rarity = ""

	# Cost in SlimeCoin to buy this item. (slime now, but hopefully we make an exception for furniture)
	price = 0

	# Names of the vendors selling this item. (yo munchy/ben, i kind of want to add a furniture mart)
	vendors = []

	#Text when placing the item
	furniture_place_desc = ""

	#Text when the generic "look" is used
	furniture_look_desc = ""

	#How you received this item
	acquisition = ""

	#the set that the furniture belongs to
	furn_set = ""

	#furniture color
	hue = ""



	def __init__(
		self,
		id_furniture = "",
		str_name = "",
		str_desc = "",
		rarity = "",
		acquisition = "",
		price = 0,
		vendors = [],
		furniture_place_desc = "",
		furniture_look_desc = "",
		furn_set = "",
		hue="",
		num_keys = 0

	):
		self.item_type = ewcfg.it_furniture
		self.id_furniture = id_furniture
		self.str_name = str_name
		self.str_desc = str_desc
		self.rarity = rarity
		self.acquisition = acquisition
		self.price = price
		self.vendors = vendors
		self.furniture_place_desc = furniture_place_desc
		self.furniture_look_desc = furniture_look_desc
		self.furn_set = furn_set
		self.hue = hue
		self.num_keys = num_keys

"""
	Prank items for Swilldermuk
"""
class EwPrankItem:
	item_type = "item"
	id_item = " "
	
	
	alias = []
	
	context = "prankitem"
	str_name = ""
	str_desc = ""
	
	prank_type = "" # Type of prank item. Can be an instant use, trap, or response item
	prank_desc = "" # A line of text that appears when the prank item gets used
	rarity = "" # Rarity of prank item. Used in determining how often it should spawn
	gambit = 0 # Gambit multiplier
	response_command = "" # All response items need a different command to break out of them
	response_desc_1 = "" # Response items contain additonal text which is indicative of how far the prank has progressed.
	response_desc_2 = ""
	response_desc_3 = ""
	response_desc_4 = ""
	trap_chance = 0 # All trap items only have a certain chance to activate
	trap_stored_credence = 0 # Trap items store half your current credence up front for later
	trap_user_id = "" # Trap items store your user id when you lay them down for later
	side_effect = "" # Some prank items have side-effects. Example: The 'bungis beam' will change a player's name to '[player name] (Bungis)'
	
	ingredients = ""
	acquisition = ""
	vendors = []

	def __init__(
		self,
		id_item=" ",
		alias = [],
		str_name = "",
		str_desc = "",
		prank_type = "",
		prank_desc = "",
		rarity = "",
		gambit = 0,
		response_command = "",
		response_desc_1 = "",
		response_desc_2 = "",
		response_desc_3 = "",
		response_desc_4 = "",
		trap_chance = 0,
		trap_stored_credence = 0,
		trap_user_id = "",
		side_effect = "",
		ingredients = "",
		acquisition = "",
		vendors = [],
	):
		self.item_type = "item"
		self.id_item = id_item
		self.alias = alias
		self.context = "prankitem"
		self.str_name = str_name
		self.str_desc = str_desc
		self.prank_type = prank_type
		self.prank_desc = prank_desc
		self.rarity = rarity
		self.gambit = gambit
		self.response_command = response_command
		self.response_desc_1 = response_desc_1
		self.response_desc_2 = response_desc_2
		self.response_desc_3 = response_desc_3
		self.response_desc_4 = response_desc_4
		self.trap_chance = trap_chance
		self.trap_stored_credence = trap_stored_credence
		self.trap_user_id = trap_user_id
		self.side_effect = side_effect
		self.ingredients = ingredients
		self.acquisition = acquisition
		self.vendors = vendors
		
"""
	Smelting Recipe Model Object
"""
class EwSmeltingRecipe:
	# The proper name of the recipe.
	id_recipe = ""

	# The string name of the recipe.
	str_name = ""

	# A list of alternative names.
	alias = []

	# The ingredients for the recipe, by str_name of the object.
	ingredients = []

	# The product(s) created by the recipe, A tuple of the item type (it_food, it_cosmetic, etc) and item_props.
	products = []

	def __init__(
		self,
		id_recipe="",
		str_name="",
		alias = [],
		ingredients = [],
		products = [],
	):
		self.id_recipe = id_recipe
		self.str_name = str_name
		self.alias = alias
		self.ingredients = ingredients
		self.products = products

