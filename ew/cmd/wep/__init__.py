from . import cmds
from .utils import *
from ew.static import cfg

cmd_map = {

    # !kill
    cfg.cmd_kill: cmds.attack,
	cfg.cmd_shoot: cmds.attack,
	cfg.cmd_shoot_alt1: cmds.attack,
	cfg.cmd_shoot_alt2: cmds.attack,
	cfg.cmd_shoot_alt3: cmds.attack,
	cfg.cmd_shoot_alt4: cmds.attack,
	cfg.cmd_shoot_alt5: cmds.attack,
	cfg.cmd_shoot_alt6: cmds.attack,
	cfg.cmd_shoot_alt7: cmds.attack,
	cfg.cmd_shoot_alt8: cmds.attack,
	cfg.cmd_attack: cmds.attack,
	cfg.cmd_win: cmds.attack,
	# Slimefest
	# ewcfg.cmd_win: ewwep.attack,

    # !reload
    cfg.cmd_reload: cmds.reload,
	cfg.cmd_reload_alt1: cmds.reload,

    # !equip
	cfg.cmd_equip: cmds.equip,
	cfg.cmd_arm: cmds.equip,
	cfg.cmd_arsenalize: cmds.equip,

	# !sidearm
	cfg.cmd_sidearm: cmds.sidearm,

    # !suicide
	cfg.cmd_suicide: cmds.suicide,
	cfg.cmd_suicide_alt1: cmds.suicide,
	cfg.cmd_suicide_alt2: cmds.suicide,

	# !spar
	cfg.cmd_spar: cmds.spar,

	# !annoint
	cfg.cmd_annoint: cmds.annoint,
	cfg.cmd_annoint_alt1: cmds.annoint,

	# !marry
	cfg.cmd_marry: cmds.marry,
	
	# !divorce
	cfg.cmd_divorce: cmds.divorce,
	
	# combat commands
	cfg.cmd_taunt: cmds.taunt,
	cfg.cmd_aim: cmds.aim,
	cfg.cmd_dodge: cmds.dodge,
	cfg.cmd_dodge_alt1: cmds.dodge,
	cfg.cmd_dodge_alt2: cmds.dodge,
	
	# !spray
	cfg.cmd_spray: cmds.spray,
	cfg.cmd_spray_alt1: cmds.spray,
	
	# !sanitize
	cfg.cmd_sanitize: cmds.sanitize,
	
	# !switch
	cfg.cmd_switch: cmds.switch_weapon,
	cfg.cmd_switch_alt_1: cmds.switch_weapon

}

apt_dm_cmd_map = {

	# Name your current weapon.
	cfg.cmd_annoint: cmds.annoint,
	cfg.cmd_annoint_alt1: cmds.annoint,

	# !equip
	cfg.cmd_equip: cmds.equip,
	cfg.cmd_arm: cmds.equip,
	cfg.cmd_arsenalize: cmds.equip,

	# !switch
	cfg.cmd_switch: cmds.switch_weapon,
	cfg.cmd_switch_alt_1: cmds.switch_weapon,

	# !sidearm
	cfg.cmd_sidearm: cmds.sidearm,

}