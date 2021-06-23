from ew.static import cfg
from . import wepcmds

cmd_map = {

    # !kill
    cfg.cmd_kill: wepcmds.attack,
    cfg.cmd_shoot: wepcmds.attack,
    cfg.cmd_shoot_alt1: wepcmds.attack,
    cfg.cmd_shoot_alt2: wepcmds.attack,
    cfg.cmd_shoot_alt3: wepcmds.attack,
    cfg.cmd_shoot_alt4: wepcmds.attack,
    cfg.cmd_shoot_alt5: wepcmds.attack,
    cfg.cmd_shoot_alt6: wepcmds.attack,
    cfg.cmd_shoot_alt7: wepcmds.attack,
    cfg.cmd_shoot_alt8: wepcmds.attack,
    cfg.cmd_attack: wepcmds.attack,
    cfg.cmd_win: wepcmds.attack,
    # Slimefest
    # ewcfg.cmd_win: ewwep.attack,

    # !reload
    cfg.cmd_reload: wepcmds.reload,
    cfg.cmd_reload_alt1: wepcmds.reload,

    # !equip
    cfg.cmd_equip: wepcmds.equip,
    cfg.cmd_arm: wepcmds.equip,
    cfg.cmd_arsenalize: wepcmds.equip,

    # !sidearm
    cfg.cmd_sidearm: wepcmds.sidearm,

    # !suicide
    cfg.cmd_suicide: wepcmds.suicide,
    cfg.cmd_suicide_alt1: wepcmds.suicide,
    cfg.cmd_suicide_alt2: wepcmds.suicide,
    # Used to be suicide aliases
    cfg.cmd_haveastroke: wepcmds.null_cmd,
    cfg.cmd_moonhurtingbeam: wepcmds.null_cmd,

    # !spar
    cfg.cmd_spar: wepcmds.spar,

    # !annoint
    cfg.cmd_annoint: wepcmds.annoint,
    cfg.cmd_annoint_alt1: wepcmds.annoint,

    # !marry
    cfg.cmd_marry: wepcmds.marry,

    # !divorce
    cfg.cmd_divorce: wepcmds.divorce,

    # combat commands
    cfg.cmd_taunt: wepcmds.taunt,
    cfg.cmd_aim: wepcmds.aim,
    cfg.cmd_dodge: wepcmds.dodge,
    cfg.cmd_dodge_alt1: wepcmds.dodge,
    cfg.cmd_dodge_alt2: wepcmds.dodge,

    # !spray
    cfg.cmd_spray: wepcmds.spray,
    cfg.cmd_spray_alt1: wepcmds.spray,

    # !sanitize
    cfg.cmd_sanitize: wepcmds.sanitize,

    # !switch
    cfg.cmd_switch: wepcmds.switch_weapon,
    cfg.cmd_switch_alt_1: wepcmds.switch_weapon,

    # Dueling
    cfg.cmd_duel: wepcmds.duel,

}

apt_dm_cmd_map = {

    # Name your current weapon.
    cfg.cmd_annoint: wepcmds.annoint,
    cfg.cmd_annoint_alt1: wepcmds.annoint,

    # !equip
    cfg.cmd_equip: wepcmds.equip,
    cfg.cmd_arm: wepcmds.equip,
    cfg.cmd_arsenalize: wepcmds.equip,

    # !switch
    cfg.cmd_switch: wepcmds.switch_weapon,
    cfg.cmd_switch_alt_1: wepcmds.switch_weapon,

    # !sidearm
    cfg.cmd_sidearm: wepcmds.sidearm,

}
