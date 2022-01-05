from ..model.item import EwRelic
relic_list = [

    EwRelic(
        id_relic = "mysenseofhumor",
        str_name = "My Sense of Humor",
        str_desc = "It's a relic alright. Used and abused.",
        rarity = "patrician",
        price = 999999999999,
        vendors = [],
        acquisition = "",
        str_museum = "",
        str_use = "",
        amount_yield=0,
        has_effect=False
    ),

]


debug1 = 'suckdick'
debug2 = 'clownfart'
debug11 = "!midlifecrisis"

relic_map = {}
relic_names = []
alt_relics = []


for relic in relic_list:
    relic_map[relic.id_relic] = relic
    relic_names.append(relic.id_relic)
    if relic.id_relic[0]=='_':
        alt_relics.append(relic.id_relic[1:])



datatext_relic = {

}