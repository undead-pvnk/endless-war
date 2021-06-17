from ew.static import cfg as ewcfg
from . import cmds

cmd_map = {

    # Send a tweet
    ewcfg.cmd_tweet: cmds.tweet,

    # Get Verified
    ewcfg.cmd_verification: cmds.verification,
    ewcfg.cmd_verification_alt: cmds.verification,

}

dm_cmd_map = {

    # !tweet
    ewcfg.cmd_tweet: cmds.tweet,

}
