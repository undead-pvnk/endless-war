class EwFarmAction:
    id_action = 0

    action = ""

    str_check = ""

    str_execute = ""

    str_execute_fail = ""

    aliases = []

    def __init__(self,
                 id_action = 0,
                 action = "",
                 str_check = "",
                 str_execute = "",
                 str_execute_fail = "",
                 aliases = []
                 ):
        self.id_action = id_action
        self.action = action
        self.str_check = str_check
        self.str_execute = str_execute
        self.str_execute_fail = str_execute_fail
        self.aliases = aliases
