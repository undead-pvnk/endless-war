class EwFish:
    # A unique name for the fish. This is used in the database and typed by users, so it should be one word, all lowercase letters.
    id_fish = ""

    # A list of alternative names.
    alias = []

    # Name of the fish.
    str_name = ""

    # Size of fish. Only assigned upon generation.
    size = ""

    # How rare a fish species is.
    rarity = ""

    # When it can be caught.
    catch_time = None

    # What weather the fish can be exclusively caught in.
    catch_weather = None

    # Description of the fish.
    str_desc = ""

    # What type of slime it exclusively resides in. None means both.
    slime = None

    # List of the vendors selling this item. (This will basically exclusively be none.)
    vendors = []

    item_type = 'food'

    def __init__(
            self,
            id_fish = "",
            str_name = "",
            size = "",
            rarity = "",
            catch_time = None,
            catch_weather = None,
            str_desc = "",
            slime = None,
            vendors = []
    ):
        self.id_fish = id_fish
        self.str_name = str_name
        self.size = size
        self.rarity = rarity
        self.catch_time = catch_time
        self.catch_weather = catch_weather
        self.str_desc = str_desc
        self.slime = slime
        self.vendors = vendors
