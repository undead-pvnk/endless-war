# Reskinned version of effect container from wep.
class EwEnemyEffectContainer:
    miss = False
    crit = False
    strikes = 0
    slimes_damage = 0
    enemy_data = None
    target_data = None
    # sap_damage = 0
    # sap_ignored = 0
    hit_chance_mod = 0
    crit_mod = 0

    # Debug method to dump out the members of this object.
    def dump(self):
        print(
            "effect:\nmiss: {miss}\ncrit: {crit}\nstrikes: {strikes}\nslimes_damage: {slimes_damage}\nslimes_spent: {slimes_spent}".format(
                miss=self.miss,
                crit=self.crit,
                strikes=self.strikes,
                slimes_damage=self.slimes_damage,
                slimes_spent=self.slimes_spent
            ))

    def __init__(
            self,
            miss = False,
            crit = False,
            strikes = 0,
            slimes_damage = 0,
            slimes_spent = 0,
            enemy_data = None,
            target_data = None,
            # sap_damage=0,
            # sap_ignored=0,
            hit_chance_mod = 0,
            crit_mod = 0
    ):
        self.miss = miss
        self.crit = crit
        self.strikes = strikes
        self.slimes_damage = slimes_damage
        self.slimes_spent = slimes_spent
        self.enemy_data = enemy_data
        self.target_data = target_data
        # self.sap_damage = sap_damage
        # self.sap_ignored = sap_ignored
        self.hit_chance_mod = hit_chance_mod
        self.crit_mod = crit_mod


# Reskinned version of weapon class from wep.
class EwAttackType:
    # An name used to identify the attacking type
    id_type = ""

    # Displayed when this weapon is used for a !kill
    str_kill = ""

    # Displayed to the dead victim in the sewers. Brief phrase such as "gunned down" etc.
    str_killdescriptor = ""

    # Displayed when viewing the !trauma of another player.
    str_trauma = ""

    # Displayed when viewing the !trauma of yourself.
    str_trauma_self = ""

    # Displayed when a non-lethal hit occurs.
    str_damage = ""

    # Function that applies the special effect for this weapon.
    fn_effect = None

    # Displayed when a weapon effect causes a critical hit.
    str_crit = ""

    # Displayed when a weapon effect causes a miss.
    str_miss = ""

    # Displayed when a weapon effect targets a group.
    str_groupattack = ""

    def __init__(
            self,
            id_type = "",
            str_kill = "",
            str_killdescriptor = "",
            str_trauma = "",
            str_trauma_self = "",
            str_damage = "",
            fn_effect = None,
            str_crit = "",
            str_miss = "",
            str_groupattack = "",
    ):
        self.id_type = id_type
        self.str_kill = str_kill
        self.str_killdescriptor = str_killdescriptor
        self.str_trauma = str_trauma
        self.str_trauma_self = str_trauma_self
        self.str_damage = str_damage
        self.fn_effect = fn_effect
        self.str_crit = str_crit
        self.str_miss = str_miss
        self.str_groupattack = str_groupattack
