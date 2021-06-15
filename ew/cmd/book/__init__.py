from . import cmds
from .utils import *
from ew.static import cfg as ewcfg

cmd_map = {

    # BOOK COMMANDS OH YEAH
	ewcfg.cmd_beginmanuscript: cmds.begin_manuscript,
	ewcfg.cmd_beginmanuscript_alt_1: cmds.begin_manuscript,
	ewcfg.cmd_beginmanuscript_alt_2: cmds.begin_manuscript,
	ewcfg.cmd_setpenname: cmds.set_pen_name,
	ewcfg.cmd_setpenname_alt_1: cmds.set_pen_name,
	ewcfg.cmd_settitle: cmds.set_title,
	ewcfg.cmd_settitle_alt_1: cmds.set_title,
	ewcfg.cmd_setgenre: cmds.set_genre,
	ewcfg.cmd_editpage: cmds.edit_page,
	ewcfg.cmd_viewpage: cmds.view_page,
	ewcfg.cmd_checkmanuscript: cmds.check_manuscript,
	ewcfg.cmd_publishmanuscript: cmds.publish_manuscript,
	ewcfg.cmd_readbook: cmds.read_book,
	ewcfg.cmd_nextpage: cmds.next_page,
	ewcfg.cmd_nextpage_alt_1: cmds.next_page,
	ewcfg.cmd_previouspage: cmds.previous_page,
	ewcfg.cmd_previouspage_alt_1: cmds.previous_page,
	ewcfg.cmd_previouspage_alt_2: cmds.previous_page,
	ewcfg.cmd_browsezines: cmds.browse_zines,
	ewcfg.cmd_buyzine: cmds.order_zine,
	ewcfg.cmd_buyzine_alt_1: cmds.order_zine,
	ewcfg.cmd_rate: cmds.rate_zine,
	ewcfg.cmd_rate_alt_1: cmds.rate_zine,
	ewcfg.cmd_rate_alt_2: cmds.rate_zine,
	ewcfg.cmd_setpages: cmds.set_length,
	ewcfg.cmd_setpages_alt_1: cmds.set_length,
	ewcfg.cmd_setpages_alt_2: cmds.set_length,
	ewcfg.cmd_takedown: cmds.take_down_zine,
	ewcfg.cmd_takedown_alt_1: cmds.take_down_zine,
	ewcfg.cmd_takedown_alt_2: cmds.take_down_zine,
	ewcfg.cmd_untakedown: cmds.untake_down_zine,
	ewcfg.cmd_untakedown_alt_1: cmds.untake_down_zine,
	ewcfg.cmd_untakedown_alt_2: cmds.untake_down_zine,

}

dm_cmd_map = {

    ewcfg.cmd_beginmanuscript: cmds.begin_manuscript,
	ewcfg.cmd_beginmanuscript_alt_1: cmds.begin_manuscript,
	ewcfg.cmd_beginmanuscript_alt_2: cmds.begin_manuscript,
	ewcfg.cmd_setpenname: cmds.set_pen_name,
	ewcfg.cmd_setpenname_alt_1: cmds.set_pen_name,
	ewcfg.cmd_settitle: cmds.set_title,
	ewcfg.cmd_settitle_alt_1: cmds.set_title,
	ewcfg.cmd_setgenre: cmds.set_genre,
	ewcfg.cmd_editpage: cmds.edit_page,
	ewcfg.cmd_viewpage: cmds.view_page,
	ewcfg.cmd_checkmanuscript: cmds.check_manuscript,
	ewcfg.cmd_publishmanuscript: cmds.publish_manuscript,
	ewcfg.cmd_readbook: cmds.read_book,
	ewcfg.cmd_nextpage: cmds.next_page,
	ewcfg.cmd_nextpage_alt_1: cmds.next_page,
	ewcfg.cmd_previouspage: cmds.previous_page,
	ewcfg.cmd_previouspage_alt_1: cmds.previous_page,
	ewcfg.cmd_previouspage_alt_2: cmds.previous_page,
	ewcfg.cmd_rate: cmds.rate_zine,
	ewcfg.cmd_rate_alt_1: cmds.rate_zine,
	ewcfg.cmd_rate_alt_2: cmds.rate_zine,
	ewcfg.cmd_accept: fake_cmd,
	ewcfg.cmd_refuse: fake_cmd,
	ewcfg.cmd_setpages: cmds.set_length,
	ewcfg.cmd_setpages_alt_1: cmds.set_length,
	ewcfg.cmd_setpages_alt_2: cmds.set_length,

}
