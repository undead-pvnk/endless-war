from ew.utils.combat import EwUser
import ew.utils as ewutils

class EwRelic:
    item_type = "relic"

    #The proper name of the relic
    id_relic = ""

    #The string name of the relic
    str_name = ""

    #The text displayed when you look at it
    str_desc = ""

    #How rare the item is, either plebeian, patrician, or princeps
    rarity = ""

    #Cost in slime to buy
    price = 0

    #Vendors selling the item
    vendors = []

    # How you received this item
    acquisition = ""

    # The dialogue you get at the museum
    str_museum = ""

    # The dialogue when the relic is used
    str_use = ""

    #The amount the relic is appraised for
    amount_yield = 0

    def __init__(
            self,
            id_relic = "",
            str_name = "",
            str_desc = "",
            rarity = "",
            price = "",
            vendors = [],
            acquisition = "",
            str_museum = "",
            str_use = "",
            amount_yield = 0

    ):
        self.id_relic = id_relic
        self.str_name = str_name
        self.str_desc = str_desc
        self.rarity = rarity
        self.price = price
        self.vendors = vendors
        self.acquisition = acquisition
        self.str_museum = str_museum
        self.str_use = str_use
        self.amount_yield = amount_yield

relic_list = [

    EwRelic(
        id_relic = "greenankh",
        str_name = "Green Ankh",
        str_desc = "It's a crystal obelisk, translucent green with a manic, darting eye fastened in its loop. With it, you possess the ability to create as much slime as your heart desires. You exist as a god today.",
        rarity = "patrician",
        price = "999999999999",
        vendors = [],
        acquisition = "",
        str_museum = "",
        str_use = "You tap into your ankh's reserves and conjure {} slime into yourself.",
        amount_yield=0
    ),
    EwRelic(
        id_relic="endlesspumice",
        str_name="Endless Rock",
        str_desc="It's a light, white rock with a bunch of little holes in it. The holes are on a solid surface, but won't stop shifting, expanding and contracting like bubbles. You have to preserve it in slime to keep it from pinching through your hand.",
        rarity="patrician",
        price="999999999999",
        vendors=[],
        acquisition="",
        str_museum="This is an Endless Rock, one that's mutated quite a bit from its original form. With all the radiation in NLACakaNM, it's shocking we didn't find one of these variants sooner. It may not look the same, but it's still a powerful stimulant to beings like ENDLESS WAR. One was even used to revive the monolith from death several years ago.",
        str_use="You raise the rock toward ENDLESS WAR, unsure of how to \"use\" it. Slowly, you notice ENDLESS WAR's eye begin to twitch. Its convulsions become more violent, and you notice a strange foam entering its iris. An impending sense of dread fills your stomach, and the slime in your coffers starts to lighten. Oh god. What have you done?\n\nENDLESS WAR is tripping balls. Decay is dramatically increased for players with over 7 million slime.",
        amount_yield=5000000
    ),
    EwRelic(
        id_relic="pyramididol",
        str_name="obsidian pyramid figurine",
        str_desc="You found this at some curio shop, practically a steal considering how old she said it was. It's a little pyramid figurine, with a spherical cavity that expands on the inside. There's some strange glyphs on the underside: (insert image link here)",
        rarity="patrician",
        price="1562000",
        vendors=['bazaar'],
        acquisition="",
        str_museum="ENDLESS WAR wasn't always a fixture of this city, you know. It actually rose out of the ground a little over a decade ago. Even so, throughout the history of this place we've always seen trinkets and idols like these. Historians aren't certain why that is. ENDLESS WAR could've existed a long time ago and had gone dormant, or perhaps its influence existed even underground. Maybe ENDLESS WAR formed its image from objects we already worshipped. Again, no idea.\n\nThose markings on the bottom aren't translating quite right. Conventional translation would have it say mtSRXek. But that's not a word. Is it?\nhttps://discord.gg/mtSRXek",
        str_use="",
        amount_yield=5000000
    ),
    EwRelic(
        id_relic="sacrificialdagger",
        str_name="sacrificial dagger",
        str_desc="It's a fancy looking bone knife. The bloodstains caked into the tip really give it that \"worn in\" feel. There's some strange glyphs on the hilt: (insert image link here)",
        rarity="patrician",
        price="999999999999",
        vendors=[],
        acquisition="",
        str_museum="Human sacrifice was commonplace in ancient NLACakaNM, actually. They would prepare two victims each ceremony, and they would fight to the death with these. Reading the tablets detailing such events, you get the impression the whole 'religious offering' part was kind of an afterthought, and the stabbing part was the real attraction.\n\nThe glyphs there translate to FyhACZGnyj.\nhttps://discord.gg/FyhACZGnyj",
        str_use="",
        amount_yield=5000000
    ),
    EwRelic(
        id_relic="petrifiedsecreaturescard",
        str_name="petrified secreatures card",
        str_desc="Secreatures, as we all know, has existed for centuries, like most children's card games do. Somebody must've dropped this card, after which it was covered in sediment and preserved for like 3,000 years. It's still a common card though. Just a Dinoslime. Practically worthless.",
        rarity="patrician",
        price="999999999999",
        vendors=[],
        acquisition="",
        str_museum="It may seem odd to display an exhibit you can normally find in the bargain bin at the pawnshop next door, but I have to make an exception for this 3500 B.C. verion of the card. The game balance was terrible back then! If you translate the card's description it basically lets you win the game if you have a second Dinoslime in your hand.",
        str_use="",
        amount_yield=500
    ),
]








