import asyncio

import ewcfg
import ewutils

from ew import EwUser

class EwDungeonScene:

	# The text sent when a scene starts
	text = ""

	# Whether or not the dungeon is active
	dungeon_state = True

	# Where the scene is taking place
	poi = None

	# life state to assign for this scene
	life_state = None

	# Commands that can be used in a scene, and what scene ID that leads to
	options = {}

	def __init__(
			self,
			text="",
			dungeon_state=True,
			options={},
			poi=None,
			life_state=None,
	):
		self.text = text
		self.dungeon_state = dungeon_state
		self.options = options
		self.poi = poi
		self.life_state = life_state


# maps users to where they are in the tutorial
user_to_tutorial_state = {}


def format_tutorial_response(scene):
	response = scene.text
		if scene.dungeon_state:
			response += "\n\nWhat do you do?\n\n**>options: "
			options = []
			for path in scene.options.keys():
				options.append("{}{}".format(ewcfg.cmd_prefix, path))
			response += ewutils.formatNiceList(names = options, conjunction = "or")
			response += "**"

	return response

async def tutorial_cmd(cmd):
	user_data = EwUser(member = cmd.message.author)
	client = cmd.client

	if user_data.poi not in ewcfg.tutorial_pois:
		return

	if user_data.id_user not in user_to_tutorial_state:
		user_to_tutorial_state[user_data.id_user] = 0

	
	tutorial_state = user_to_tutorial_state.get(user_data.id_user)

	tutorial_scene = ewcfg.dungeon_tutorial[tutorial_state]

	cmd_content = cmd.content[1:].lower()

	if cmd_content in tutorial_scene.options:
		new_state = tutorial_scene.options.get(cmd_content)
		user_to_tutorial_state[user_data.id_user] = new_state
			
		scene = ewcfg.dungeon_tutorial[new_state]

		if scene.poi != None:
			user_data.poi = scene.poi

		if scene.life_state != None:
			user_data.life_state = scene.life_state

		user_data.persist()

		await ewrolemgr.updateRoles(client = cmd.client, member = cmd.message.author)

		response = format_tutorial_response(scene)

		poi_def = ewcfg.id_to_poi.get(user_data.poi)
		channels = [poi_def.channel]
		return await ewutils.post_in_channels(cmd.message.server.id, ewutils.formatMessage(cmd.message.author, response), channels)


	else:
		""" couldn't process the command. bail out!! """
		""" bot rule 0: be cute """
		randint = random.randint(1,3)
		msg_mistake = "ENDLESS WAR is growing frustrated."
		if randint == 2:
			msg_mistake = "ENDLESS WAR denies you his favor."
		elif randint == 3:
			msg_mistake = "ENDLESS WAR pays you no mind."

		msg = await ewutils.send_message(client, cmd.message.channel, msg_mistake)
		await asyncio.sleep(2)
		try:
			await client.delete_message(msg)
		except:
			pass

		response = format_tutorial_response(tutorial_scene)
		return await ewutils.send_message(client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def dungeon_test(cmd):
	response = "Starting tutorial..."
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	dungeon_state = True
	scene_id = 0
	while dungeon_state:
		scene = dungeon_01[scene_id]
		response = scene.text
		if scene.dungeon_state:
			response += "\n\nWhat do you do?\n\n**>options: "
			for path in scene.options.keys():
				response += "!{}, ".format(path)
			response += "**"
			await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
			try:
		msg = await cmd.client.wait_for_message(timeout = 120, author = member, check = check)

		if msg != None:
			if message.content[1:] in scene.options.keys():
			scene_id = scene.options
			else:
						response = "You can't do that."
						await ewutils.send_message(cmd.client, cmd.message.author, ewutils.formatMessage(cmd.message.author, response))
					continue
			except:
		return
