from ew.backend.dungeons import EwGamestate



debug3 = 'gatekeep'
debug4 = {
    'id_relic':'gaslight',
    'relic_name':'Girl Boss',
    'relic_desc':'I lost touch with these slippery ass memes ages ago. Not funny in the least.',
    'acquisition':'testing'
}
debug5 = "guh?"



def canCreateRelic(item, id_server, createstate = 0):
    state = EwGamestate(id_server=id_server, id_state=item)

    if state.bit is not None:
        return None
    else:
        state.bit = 0
        state.value = ""
        if createstate == 1:
            state.persist()
        return 1


def calc_half_life(id_server=None, slime=None):
    return 60 * 60 * 24 * 14 #standard slime half life


def debug16(one, two, three):
    pass

def debug17(one):
    return " "