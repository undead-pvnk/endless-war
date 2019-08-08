import ewutils
import ewcfg

from ew import EwUser


async def vouch(cmd):
	user_data = EwUser(member = cmd.message.author)

	if len(user_data.faction) == 0:
		response = "What gang do you think you represent, to be vouching for anyone?"
	else:
		member = None
		if cmd.mentions_count == 1:
			member = cmd.mentions[0]
			if member.id == cmd.message.author.id:
				member = None

		if member == None:
			response = "Who?"
		else:
			member_data = EwUser(member = member)
			member_data.vouch(faction = user_data.faction)

			member_data.persist()
			response = "You are allowing {} to enter your gangbase and enlist in your gang.".format(member.display_name, user_data.faction)

	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
