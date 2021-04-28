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
