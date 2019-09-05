import asyncio

import ewcfg
import ewutils

from ew import EwUser

async def vouch(cmd):
	user_data = EwUser(member = cmd.message.author)
	response = ""
	
	if user_data.faction == "":
		response = "You have to join a faction before you can vouch for anyone."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.mentions_count == 0:
		response = "Vouch for whom?"
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	member = cmd.mentions[0]
	vouchee_data = EwUser(member = member)

	if vouchee_data.faction == user_data.faction:
		response = "{} has already joined your faction.".format(member.display_name)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	vouchers = vouchee_data.get_vouchers()

	if user_data.faction in vouchers:
		response = "A member of your faction has already vouched for {}.".format(member.display_name)
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
		
	vouchee_data.vouch(faction = user_data.faction)

	response = "You place your undying trust in {}.".format(member.display_name)
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

