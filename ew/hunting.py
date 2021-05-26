import time

from .backend import item as bknd_item 
from .backend.item import EwItem
from .backend.market import EwMarket
from .static import cfg as ewcfg
from .static import poi as poi_static
from .utils import frontend as fe_utils
from .utils import hunting as hunt_utils
from .utils.combat import EwUser


# Debug command. Could be used for events, perhaps?
async def summonenemy(cmd):

	author = cmd.message.author

	if not author.guild_permissions.administrator:
		return

	time_now = int(time.time())
	response = ""
	user_data = EwUser(member=cmd.message.author)
	data_level = 0

	enemytype = None
	enemy_location = None
	enemy_coord = None
	poi = None
	enemy_slimes = None
	enemy_displayname = None
	enemy_level = None
	
	resp_cont = None

	if len(cmd.tokens) >= 3:

		enemytype = cmd.tokens[1]
		enemy_location = cmd.tokens[2]
		
		if len(cmd.tokens) >= 6:
			enemy_slimes = cmd.tokens[3]
			enemy_level = cmd.tokens[4]
			enemy_coord = cmd.tokens[5]
			enemy_displayname = " ".join(cmd.tokens[6:])
	
		poi = poi_static.id_to_poi.get(enemy_location)

	if enemytype != None and poi != None:
		
		data_level = 1

		if enemy_slimes != None and enemy_displayname != None and enemy_level != None and enemy_coord != None:
			data_level = 2
			
		if data_level == 1:
			resp_cont = hunt_utils.spawn_enemy(id_server=cmd.message.guild.id, pre_chosen_type=enemytype, pre_chosen_poi=poi.id_poi, manual_spawn=True)
		elif data_level == 2:
			
			resp_cont = hunt_utils.spawn_enemy(
				id_server=cmd.message.guild.id,
				pre_chosen_type=enemytype, 
				pre_chosen_poi=poi.id_poi, 
				pre_chosen_level=enemy_level, 
				pre_chosen_slimes=enemy_slimes,
				pre_chosen_initialslimes = enemy_slimes,
				pre_chosen_coord = enemy_coord,
				pre_chosen_displayname=enemy_displayname,
				pre_chosen_weather=ewcfg.enemy_weathertype_normal,
				manual_spawn = True,
			)
			
		await resp_cont.post()
		
	else:
		response = "**DEBUG**: PLEASE RE-SUMMON WITH APPLICABLE TYPING / LOCATION. ADDITIONAL OPTIONS ARE SLIME / LEVEL / COORD / DISPLAYNAME"
		await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def summongvsenemy(cmd):
	author = cmd.message.author

	if not author.guild_permissions.administrator:
		return

	time_now = int(time.time())
	response = ""
	user_data = EwUser(member=cmd.message.author)

	poi = None
	enemytype = None
	coord = None
	joybean_status = None

	if cmd.tokens_count == 4:
		enemytype = cmd.tokens[1]
		coord = cmd.tokens[2]
		joybean_status = cmd.tokens[3]
		poi = poi_static.id_to_poi.get(user_data.poi)
	else:
		response = "Correct usage: !summongvsenemy [type] [coord] [joybean status ('yes', otherwise false)]"
		return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
		
	if enemytype != None and poi != None and joybean_status != None and coord != None:
		props = None
		try:
			props = ewcfg.enemy_data_table[enemytype]["props"]

			if joybean_status.lower() == 'yes':
				props['joybean'] = 'true'
			
		except:
			pass

		resp_cont = hunt_utils.spawn_enemy(
			id_server=cmd.message.guild.id, 
			pre_chosen_type=enemytype, 
			pre_chosen_poi=poi.id_poi,
			pre_chosen_coord=coord.upper(),
			pre_chosen_props=props,
			pre_chosen_weather=ewcfg.enemy_weathertype_normal,
			manual_spawn=True,
		)
	
		await resp_cont.post()

# SAFARI ADVENTURE KILL-A-THON CODE FUCK YEAH

# Check thee safari power level
async def safari_power(cmd):
	user_data = EwUser(member=cmd.message.author)
	market_data = EwMarket(id_server = user_data.id_server)
	safari_power = user_data.safari_power
	total_safari_power = market_data.total_safari_power
	if user_data.poi != ewcfg.poi_id_charcoalpark:
		response = "You get out your trusty messenger boomerang and lob it towards Charcoal Park. It returns, bearing a hastily-scribbled message: \n'Thou hast {} safari power, and thou city's power is {}'".format(safari_power, total_safari_power)
	else: 
		response = "You ask a volunteer about how it's going. They launch into a lengthy discussion about their recent divorce, medical problems and overall dissatisfaction with the status quo. Not wanting to interrupt, you let them continue their spiel before asking about how the ***SAFARI*** is going.\n They respond: 'You have {} safari power, and the city's power is {}.'".format(safari_power, total_safari_power)
	return await fe_utils.send_response(response, cmd)

# Submit your trophies to the Safari Gods, and let ye be judg-ed
async def safari_submit(cmd):
	user_data = EwUser(member=cmd.message.author)
	market_data = EwMarket(id_server = user_data.id_server)
	if user_data.poi != ewcfg.poi_id_charcoalpark:
		response = "You try to hand in your hunting trophies to a random passerby. They politely point you towards Charcoal Park before sprinting away."
	elif user_data.life_state == ewcfg.life_state_corpse or user_data.life_state == ewcfg.life_state_shambler:
		response = "The volunteer responds in a meek voice that ghosts and the undead aren't allowed in the contest. They seem scared shitless."
	elif user_data.life_state == ewcfg.life_state_kingpin:
		response = "The volunteer nearly faints upon seeing the visage of a **KINGPIN**. Their teeth chatter uncontrollably, their knees rapidly loss strength and their sweater breaks out into spaghetti stains. 'U-h-hh-h-h-h-h-h-h-' is all they can utter before they collapse."
	else:	
		power_gain = 0
		trophy_count = 0
		trophies_to_remove = [] 
		
		# TODO: Figure out a way to optimise this, yikes!
		inv_items = bknd_item.inventory(id_user = user_data.id_user, id_server = user_data.id_server,item_type_filter = ewcfg.it_item)
		
		for item in inv_items:
			trophy = EwItem(id_item = item.get('id_item'))
			if trophy.item_props.get('acquisition') == ewcfg.acquisition_huntingtrophy:
				trophies_to_remove.append(trophy.id_item)
				trophy_type = trophy.item_props.get('id_item')
				trophy_value = ewcfg.safari_trophy_values[trophy_type]
				power_gain += trophy_value
				trophy_count += 1
		
		if trophy_count > 0:
			# Add the value to the player's profile and to the total
			user_data.safari_power += power_gain
			market_data.total_safari_power += power_gain

			# Remove the trophies from the player's inventory
			for id in trophies_to_remove:
				bknd_item.item_delete(id_item=id)

			user_data.persist()
			market_data.persist()

			# Tell the user how many trophies they just handed in, and how many points they got
			response = "You hand over your trophies and receive {} levels of safari power. The volunteer smiles a weary smile.".format(power_gain)
		else:
			response = 'The volunteer blinks.\n"Huh? Sorry, I could\'ve sworn someone without any hunting trophies just tried to hand some in. Must\'ve been the wind."'

	return await fe_utils.send_response(response, cmd)