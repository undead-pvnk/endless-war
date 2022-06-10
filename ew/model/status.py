class EwStatusEffectDef:
    id_status = ""
    # Time until expiration, negative values have specific expiration conditions
    time_expire = -1

    str_acquire = ""
    str_describe = ""
    str_describe_self = ""
    dmg_mod_self = 0
    hit_chance_mod_self = 0
    crit_mod_self = 0
    dmg_mod = 0
    hit_chance_mod = 0
    crit_mod = 0

    def __init__(
            self,
            id_status = "",
            time_expire = -1,
            str_acquire = "",
            str_describe = "",
            str_describe_self = "",
            dmg_mod_self = 0,
            hit_chance_mod_self = 0,
            crit_mod_self = 0,
            dmg_mod = 0,
            hit_chance_mod = 0,
            crit_mod = 0
    ):
        self.id_status = id_status
        self.time_expire = time_expire
        self.str_acquire = str_acquire
        self.str_describe = str_describe
        self.str_describe_self = str_describe_self
        self.dmg_mod_self = dmg_mod_self
        self.hit_chance_mod_self = hit_chance_mod_self
        self.crit_mod_self = crit_mod_self
        self.dmg_mod = dmg_mod
        self.hit_chance_mod = hit_chance_mod
        self.crit_mod = crit_mod


class EwTrauma:
    # The trauma's name
    id_trauma = ""

    # String used to describe the trauma when you !data yourself
    str_trauma_self = ""

    # String used to describe the trauma when you !data another player
    str_trauma = ""

    # the trauma's effect
    trauma_class = ""

    def __init__(self,
                 id_trauma = "",
                 str_trauma_self = "",
                 str_trauma = "",
                 trauma_class = "",
                 ):

        self.id_trauma = id_trauma

        if str_trauma_self == "":
            str_trauma_self = "You have the {} trauma.".format(self.id_trauma)
        self.str_trauma_self = str_trauma_self

        if str_trauma == "":
            str_trauma = "They have the {} trauma.".format(self.id_trauma)
        self.str_trauma = str_trauma

        self.trauma_class = trauma_class


class EwHitzone:
    name = ""

    aliases = []

    id_injury = ""

    def __init__(self,
                 name = "",
                 aliases = [],
                 id_injury = "",
                 ):
        self.name = name
        self.aliases = aliases
        self.id_injury = id_injury
