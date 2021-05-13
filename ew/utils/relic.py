from ew.backend.dungeons import EwGamestate

def canCreateRelic(item, id_server):
    state = EwGamestate(id_server=id_server, id_state=item)
    if state.bit is not None:
        return None
    else:
        state.bit = 1
        state.value = ""
        state.persist()
        return 1