from ..static import cfg as ewcfg

""" Food model object """


class EwFood:
    item_type = "food"

    # The main name of this food.
    id_food = ""

    # A list of alternative names.
    alias = []

    # Hunger reduced by eating this food.
    recover_hunger = 0

    # Cost in SlimeCoin to eat this food.
    price = 0

    # A nice string name describing this food.
    str_name = ""

    # Names of the vendors selling this food in the food court.
    vendors = []

    # Flavor text displayed when you eat this food.
    str_eat = ""

    # Alcoholic effect
    inebriation = 0

    # Flavor text displayed when you inspect this food.
    str_desc = ""

    # Expiration time (can be left blank for standard expiration time)
    time_expir = 0

    # The ingredients necessary to make this item via it's acquisition method
    ingredients = ""

    # The way that you can acquire this item. If blank, it's not relevant.
    acquisition = ""

    # Whether or not the item expires
    perishable = True

    # Timestamp when an item was fridged.

    time_fridged = 0

    def __init__(
            self,
            id_food = "",
            alias = [],
            recover_hunger = 0,
            price = 0,
            str_name = "",
            vendors = [],
            str_eat = "",
            inebriation = 0,
            str_desc = "",
            time_expir = 0,
            time_fridged = 0,
            ingredients = "",
            acquisition = "",
            perishable = True
    ):
        self.item_type = ewcfg.it_food

        self.id_food = id_food
        self.alias = alias
        self.recover_hunger = recover_hunger
        self.price = price
        self.str_name = str_name
        self.vendors = vendors
        self.str_eat = str_eat
        self.inebriation = inebriation
        self.str_desc = str_desc
        self.time_expir = time_expir if time_expir > 0 else ewcfg.std_food_expir
        self.time_fridged = time_fridged
        self.ingredients = ingredients
        self.acquisition = acquisition
        self.perishable = perishable
