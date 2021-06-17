from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Smoke a cosmetic. preferably a cigarette
    ewcfg.cmd_smoke: cmds.smoke,

    # Wearing cosmetics
    ewcfg.cmd_adorn: cmds.adorn,
    ewcfg.cmd_dedorn: cmds.dedorn,
    ewcfg.cmd_dedorn_alt1: cmds.dedorn,

    # Reworking/fixing
    ewcfg.cmd_sew: cmds.sew,
    ewcfg.cmd_retrofit: cmds.retrofit,

    # Dyeing
    ewcfg.cmd_dyecosmetic: cmds.dye,
    ewcfg.cmd_dyecosmetic_alt1: cmds.dye,
    ewcfg.cmd_dyecosmetic_alt2: cmds.dye,
    ewcfg.cmd_dyecosmetic_alt3: cmds.dye,

    # admins manipulate/make items
    ewcfg.cmd_balance_cosmetics: cmds.balance_cosmetics,

}

apt_dm_cmd_map = {

    # Smoke a cosmetic. preferably a cigarette
    ewcfg.cmd_smoke: cmds.smoke,

    # Wearing cosmetics
    ewcfg.cmd_adorn: cmds.adorn,
    ewcfg.cmd_dedorn: cmds.dedorn,
    ewcfg.cmd_dedorn_alt1: cmds.dedorn,

    # Dyeing
    ewcfg.cmd_dyecosmetic: cmds.dye,
    ewcfg.cmd_dyecosmetic_alt1: cmds.dye,
    ewcfg.cmd_dyecosmetic_alt2: cmds.dye,
    ewcfg.cmd_dyecosmetic_alt3: cmds.dye,

}
