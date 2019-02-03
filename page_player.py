#!/usr/bin/python3
#
# page_player
# mperron (2019)
#
# Read a player's data from the endless-war database and present an HTML view.
import sys
import cgi

import ewutils
import ewcmd
import ewcfg

from ew import EwUser
from ewplayer import EwPlayer

def faction(faction, life_state):
	url = "<img src=/img/icons/{}.png style=\"height: 1em;\"> "

	if life_state == 2:
		if faction == "killers" or faction == "rowdys":
			return url.format(faction)
	elif life_state == 1:
		return url.format("juveniles")
	elif life_state == 0:
		return url.format("ghost")

	return ""

if len(sys.argv) >= 3:
	id_server = sys.argv[1]
	id_user = sys.argv[2]
else:
	print("<p><i>Nothing but dust...</i></p>")
	sys.exit(0)

print("<article class=story>")

user_data = EwUser(id_user = id_user, id_server = id_server)
player = EwPlayer(id_user = id_user)

# Left-hand floating profile section
print("<div class=profile_float><img src=\"{avatar_url}\" class=profile_avatar>".format(
	avatar_url = player.avatar
))
print("</div>")


# Header bar
print("<header><h2>{faction}<a href=player.html?pl={id_user}>{display_name}</a></h2></header>".format(
	id_user = id_user,
	display_name = cgi.escape(player.display_name),
	faction = faction(user_data.faction, user_data.life_state)
))


# Main body
print("<div>")

print("<p>{}</p>".format(cgi.escape(ewcmd.gen_data_text(
	id_user = id_user,
	id_server = id_server,
	display_name = player.display_name
))))

print("<table>")
print("<tr><td>Faction</td><td>{icon}{faction}</td></tr>".format(
	icon = faction(user_data.faction, user_data.life_state),
	faction = user_data.faction

))
print("<tr><td>Slime</td><td>{slime:,}</td></tr>".format(slime = user_data.slimes))
print("<tr><td>SlimeCoin</td><td>{slimecredit:,}</td></tr>".format(slimecredit = user_data.slimecredit))
print("<tr><td>Bounty</td><td>{bounty:,}</td></tr>".format(bounty = int((user_data.bounty + 1) / ewcfg.slimecoin_exchangerate)))
print("</table>")

print("</div>")
print("</article>")
