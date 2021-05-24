from .. import debugrelics as ewdebugrelics

relic_list = ewdebugrelics.relic_list

relic_map = {}
relic_names = []


for relic in relic_list:
    relic_map[relic.id_relic] = relic
    relic_names.append(relic.id_relic)


relic_functions = {
    "greenankh": ewdebugrelics.greenankh

}

