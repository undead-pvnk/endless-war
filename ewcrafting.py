import random
import time

import ewcfg
import ewitem
import ewutils

from ew import EwUser
from ewitem import EwItem

"""
	Crafting Recipe Model Object
"""

class EwCraftingRecipe:
	# The proper name of the recipe
	id_recipe = ""

	# The string name of the recipe
	str_name = ""

	# A list of alternative names.
	alias = []

	# The ingredients for the recipe, by str_name of the object
	ingredients = []

	# The product(s) created by the recipe, A tuple of the item type (it_food, it_cosmetic, etc) and item_props
	products = []

	def __init__(
		self,
		id_recipe="",
		str_name="",
		alias = [],
		ingredients = [],
		products = [],
	):
		self.id_recipe = id_recipe
		self.str_name = str_name
		self.alias = alias
		self.ingredients = ingredients
		self.products = products

"""
	Craft Command
"""

async def craft(cmd):
	user_data = EwUser(member = cmd.message.author)

	# Find sought recipe.
	if cmd.tokens_count > 1:
		sought_result = cmd.tokens[1].lower()
		found_recipe = ewcfg.crafting_recipe_map.get(sought_result)

		if found_recipe != None:
			# Checks what ingredients are needed to smelt the recipe.
			necessary_ingredients = found_recipe.ingredients

			owned_ingredients = []

			for item in necessary_ingredients:
				item_sought = ewitem.find_item(item_search = item, id_user = user_data.id_user, id_server = user_data.id_server)
				if item_sought != None:
					owned_ingredients.append(item)
					ewitem.item_drop(item_sought.get('id_item'))
				else:
					pass

			if len(necessary_ingredients) > len(owned_ingredients):
				#todo have it actually refund you the items
				for refund_item in owned_ingredients:
					try:
						ewitem.give_item(id_item = refund_item.get("id_item"), id_user = user_data.id_user, id_server = user_data.id_server) # Item return
						EwItem(id_item = refund_item.get('id_item')).persist()
					except:
						print('Could not do it.')

				response = "To smelt a {}, you need {}.".format(found_recipe.str_name, ewutils.formatNiceList(names = necessary_ingredients, conjunction = "and"))

				if len(owned_ingredients) != 0:
					response += " You only have {}.".format(ewutils.formatNiceList(names = owned_ingredients, conjunction = "and"))

			else:
				possible_results = []

				for result in ewcfg.item_list:
					if result.id_item not in found_recipe.products:
						pass
					else:
						possible_results.append(result)

				for result in ewcfg.food_list:
					if result.id_food not in found_recipe.products:
						pass
					else:
						possible_results.append(result)

				for result in ewcfg.cosmetic_items_list:
					if result.id_cosmetic not in found_recipe.products:
						pass
					else:
						possible_results.append(result)

				item = random.choice(possible_results)

				if hasattr(item, 'id_item'):
					ewitem.item_create(
						item_type = ewcfg.it_item,
						id_user = cmd.message.author.id,
						id_server = cmd.message.server.id,
						item_props = {
							'id_item': item.id_item,
							'context': item.context,
							'subcontext': item.subcontext,
							'item_name': item.str_name,
							'item_desc': item.str_desc,
							'ingredients': item.ingredients,
						}
					),

				elif hasattr(item, 'id_food'):
					ewitem.item_create(
						item_type = ewcfg.it_food,
						id_user = cmd.message.author.id,
						id_server = cmd.message.server.id,
						item_props = {
							'id_food': item.id_food,
							'food_name': item.str_name,
							'food_desc': item.str_desc,
							'recover_hunger': item.recover_hunger,
							'inebriation': item.inebriation,
							'str_eat': item.str_eat,
							'time_expir': time.time() + ewcfg.farm_food_expir
						}
					),

				elif hasattr(item, 'id_cosmetic'):
					ewitem.item_create(
						item_type = ewcfg.it_cosmetic,
						id_user = cmd.message.author.id,
						id_server = cmd.message.server.id,
						item_props = {
							'id_cosmetic': item.id_cosmetic,
							'cosmetic_name': item.str_name,
							'cosmetic_desc': item.str_desc,
							'rarity': item.rarity,
							'adorned': 'false'
						}
					),

				#todo have it actually delete items
				for used_item in owned_ingredients:
					ewitem.item_delete(id_item = used_item.get('id_item'))

				response = "You sacrifice your {} to smelt a {}!!".format(ewutils.formatNiceList(names = necessary_ingredients, conjunction = "and"), item.str_name)

				user_data.persist()

		else:
			response = "There is no recipe by the name."

	else:
		response = "Please specify a desired smelt result."

	# Send response
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))




# async def craft(cmd):
# 	user_data = EwUser(member = cmd.message.author)
# 	response = "You sacrifice your "
#
# 	# Parse the ingredients.
# 	ingredients = []
# 	item_counter = 0
# 	cmd.tokens.pop(0) # Removes the command from the token list.
# 	item_list = cmd.tokens # Sets up list of items to be sought.
# 	for item in item_list: # Looks for each item.
# 		sought_item = ewitem.find_item(item_search=item, id_user=user_data.id_user, id_server=user_data.id_server)
#
# 		if sought_item != None: # If the item was found, add it to the response.
# 			ewitem.item_drop(sought_item.get('id_item'))
# 			if item_counter != 0:
# 				response += " and " + sought_item.get('name')
# 			else:
# 				response += sought_item.get('name')
#
# 		item_counter += 1
#
# 		ingredients.append(sought_item) # Adds item to the ingredients list.
#
# 	# Check if all ingredients were found, and returns any items dropped if any weren't found.
# 	if None in ingredients or ingredients == []:
# 		for ingredient in ingredients: # Iterates through ingredients.
# 			if ingredient != None: # Won't try to return nonetype objects.
# 				try:
# 					ewitem.give_item(id_item = ingredient.get("id_item"), id_user = user_data.id_user, id_server = user_data.id_server) # Returns items.
# 					EwItem(id_item = ingredient.get('id_item')).persist()
# 				except:
# 					print('Could not return ' + ingredient.get('name') + ' to ' + cmd.message.author.nickname) # Notifies bot if items couldn't be returned.
# 		response = "You don't have those ingredients."
# 		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 		return
#
# 	# Find matching recipe
# 	found_recipe = None
# 	for recipe in ewcfg.crafting_recipe_list: # Iterates through all recipes.
# 		correct = False # Assumes it has not been found.
#
# 		ingredient_names = []
# 		for i in ingredients: # Turns ingredient list into list of names to easier match to a recipe's list.
# 			ingredient_names.append(i.get('name'))
# 		if recipe.ingredients == ingredient_names:
# 			correct = True
#
# 		# If every item, in order, matched up, set the recipe.
# 		if correct:
# 			found_recipe = recipe
# 			break
#
#
# 	# If no recipe was found, stop, and return items.
# 	if found_recipe == None:
# 		for ingredient in ingredients:
# 			try:
# 				ewitem.give_item(id_item = ingredient.get("id_item"), id_user = user_data.id_user, id_server = user_data.id_server) # Item return
# 				EwItem(id_item=ingredient.get('id_item')).persist()
# 			except:
# 				print('Could not return ' + ingredient.get('name') + ' to ' + cmd.message.author.nickname) # If item could not be returned print to console
# 		response = "That recipe does not exist."
# 		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
# 		return
#
# 	# Remove ingredients and create the product.
# 	response += " to get "
#
# 	for item in ingredients: # Actually deleting ingredients.
# 		ewitem.item_delete(item.get('id_item'))
#
# 	product_counter = 1
# 	for product in found_recipe.products:
# 		# Adding products to response, quest items dont have a 'name' by default so they need to be handled separately.
# 		if product_counter == 1:
# 			try:
# 				if product[0] != ewcfg.it_questitem:
# 					response += product[1].get('name') + ' '
# 				else:
# 					response += product[1].get('qitem_name') + ' '
# 			except:
# 				print('Failed to get item name for product ' + str(product_counter) + ' of ' + + found_recipe.str_name)
# 		elif product_counter != len(found_recipe.products):
# 			try:
# 				if product[0] != ewcfg.it_questitem:
# 					response += 'and ' + product[1].get('name') + ' '
# 				else:
# 					response += 'and ' + product[1].get('qitem_name') + ' '
# 			except:
# 				print('Failed to get item name for product ' + str(product_counter) + ' of ' + + found_recipe.str_name)
# 		else:
# 			try:
# 				if product[0] != ewcfg.it_questitem:
# 					response += 'and ' + product[1].get('name') + '.'
# 				else:
# 					response += 'and ' + product[1].get('qitem_name') + '.'
# 			except:
# 				print('Failed to get item name for product ' + str(product_counter) + ' of ' + + found_recipe.str_name)
# 		product_counter +=1
# 		#TODO
# 		# Figure out how to handle response formatting in a better way, this is bullshit and kinda huge but
# 		# It may need to be able to handle quest items in the future
# 		# Literally Fuck Names
#
# 		# Actually create the product.
# 		ewitem.item_create(
# 			item_type=product[0],
# 			id_user=cmd.message.author.id,
# 			id_server=cmd.message.server.id,
# 			item_props=product[1]
# 		)
#
# 	user_data.persist()
# 	# Send response
# 	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))