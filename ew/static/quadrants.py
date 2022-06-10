from . import cfg as ewcfg

from ..model.quadrants import EwQuadrantFlavor

quadrants_map = {}

quadrants = [
    EwQuadrantFlavor(
        id_quadrant=ewcfg.quadrant_sloshed,

        aliases=["maw", "maws", "soulvent", "soulution", "pinked", "pink", "hotpink", "brightpink",
                 "flushed", "heart", "hearts", "matesprit", "matespritship"],  # borrowing these from the original quadrants so people dont get mad/confused by using the "wrong" name

        resp_add_onesided="You have developed sloshed feelings for {}.",

        resp_add_relationship="You have entered into a soulution with {}.",

        resp_view_onesided="{} has a one-sided pink crush on {}.",

        resp_view_onesided_self="You have a one-sided pink crush on {}.",

        resp_view_relationship="{} is in a soulution with {}. " + ewcfg.emote_maws,

        resp_view_relationship_self="You are in a soulution with {}. " + ewcfg.emote_maws
    ),

    EwQuadrantFlavor(
        id_quadrant=ewcfg.quadrant_roseate,

        aliases=["hat", "hats", "bedenizen", "bedenaissance", "denizen", "palepink", "pastelpink",
                 "pale", "diamond", "diamonds", "moirail", "moiraillegiance"],  # borrowing these from the original quadrants so people dont get mad/confused by using the "wrong" name

        resp_add_onesided="You have developed roseate feelings for {}.",

        resp_add_relationship="You have entered into a bedenaissance with {}.",

        resp_view_onesided="{} has a one-sided roseate crush on {}.",

        resp_view_onesided_self="You have a one-sided roseate crush on {}.",

        resp_view_relationship="{} is in a bedenaissance with {}. " + ewcfg.emote_hats,

        resp_view_relationship_self="You are in a bedenaissance with {}. " + ewcfg.emote_hats
    ),

    EwQuadrantFlavor(
        id_quadrant=ewcfg.quadrant_violacious,

        aliases=["slug", "slugs", "amaranthagonist", "amaranthagony", "antagonist", "agony", "purple", "violent", "violet", "hotpurple",
                 "caliginous", "spade", "spades", "kismesis", "kismesissitude"],  # borrowing these from the original quadrants so people dont get mad/confused by using the "wrong" name

        resp_add_onesided="You have developed violacious feelings for {}.",

        resp_add_relationship="You have entered into a amaranthagony with {}.",

        resp_view_onesided="{} has a one-sided violet crush on {}.",

        resp_view_onesided_self="You have a one-sided violet crush on {}.",

        resp_view_relationship="{} is in a amaranthagony with {}. " + ewcfg.emote_slugs,

        resp_view_relationship_self="You are in a amaranthagony with {}. " + ewcfg.emote_slugs
    ),

    EwQuadrantFlavor(
        id_quadrant=ewcfg.quadrant_policitous,

        aliases=["shield", "shields", "arbitraitor", "arbitreason", "police", "traitor", "treason", "lightpurple", "pastelpurple",
                 "ashen", "club", "clubs", "auspistice", "auspisticism"],  # borrowing these from the original quadrants so people dont get mad/confused by using the "wrong" name

        resp_add_onesided="You have developed policitous feelings for {}.",

        resp_add_relationship="You have entered into an arbitreason with {}.",

        resp_view_onesided="{} has a one-sided policitous crush on {}.",

        resp_view_onesided_self="You have a one-sided policitous crush on {}.",

        resp_view_relationship="{} is in an arbitreason with {}. " + ewcfg.emote_shields,

        resp_view_relationship_self="You are in an arbitreason with {}. " + ewcfg.emote_shields
    )

]

for quadrant in quadrants:
    quadrants_map[quadrant.id_quadrant] = quadrant
    for alias in quadrant.aliases:
        quadrants_map[alias] = quadrant
