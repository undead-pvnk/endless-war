from ew.static import cfg as ewcfg
from . import slimetwittercmds

cmd_map = {

    # Send a tweet
    ewcfg.cmd_tweet: slimetwittercmds.tweet,

    # Get Verified
    ewcfg.cmd_verification: slimetwittercmds.verification,
    ewcfg.cmd_verification_alt: slimetwittercmds.verification,

}

dm_cmd_map = {

    # !tweet
    ewcfg.cmd_tweet: slimetwittercmds.tweet,

}
