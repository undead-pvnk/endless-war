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

    # The ingredients for the recipe, by str_name of the object
    ingredients = []

    # The product(s) created by the recipe, A tuple of the item type (it_food, it_cosmetic, etc) and item_props
    products = []

    def __init__(
            self,
            id_recipe="",
            str_name="",
            ingredients=list,
            products=list
    ):
        self.id_recipe = id_recipe
        self.str_name = str_name
        self.ingredients = ingredients
        self.products = products

"""
	Craft Command
"""

async def craft(cmd):
    response = "You sacrifice your "
    user_data = EwUser(member = cmd.message.author)
    # Parse the ingredients

    ingredients = []
    item_counter = 0
    cmd.tokens.pop(0) # Removes the command from the token list
    item_list = cmd.tokens # Sets up list of items to be sought
    for item in item_list: # Looks for each item
        sought_item = ewitem.find_item(item_search=item, id_user=user_data.id_user, id_server=user_data.id_server)

        if sought_item != None: # If the item was found, add it to the response
            ewitem.item_drop(sought_item.get('id_item'))
            if item_counter != 0:
                response += " and " + sought_item.get('name')
            else:
                response += sought_item.get('name')
        item_counter += 1

        ingredients.append(sought_item) # Adds item to the ingredients

    # Check if all ingredients were found, and returns any items dropped if any weren't found
    if None in ingredients or ingredients == []:
        for ingredient in ingredients: # Iterates through ingredients
            if ingredient != None: # Won't try to return nonetype objects
                try:
                    ewitem.give_item(id_item = ingredient.get("id_item"), id_user = user_data.id_user, id_server = user_data.id_server) # Returns items
                    EwItem(id_item = ingredient.get('id_item')).persist()
                except:
                    print('Could not return ' + ingredient.get('name') + ' to ' + cmd.message.author.nickname) # Notifies bot if items couldn't be returned
        response = "You don't have those ingredients"
        await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
        return

    # Find matching recipe
    found_recipe = None
    for recipe in ewcfg.crafting_recipes_list: # Iterates through all recipes
        correct = False # Assumes it has not been found

        ingredient_names = []
        for ingredient in ingredients: # Turns ingredient list into list of names to easier match to a recipe's list
            ingredient_names.append(ingredient.get('name'))
        if recipe.ingredients == ingredient_names:
            correct = True

        # If every item, in order, matched up, set the recipe
        if correct:
            found_recipe = recipe
            break


    # If no recipe was found, stop, and return items
    if found_recipe == None:
        for ingredient in ingredients:
            try:
                ewitem.give_item(id_item = ingredient.get("id_item"), id_user = user_data.id_user, id_server = user_data.id_server) # Item return
                EwItem(id_item=ingredient.get('id_item')).persist()
            except:
                print('Could not return ' + ingredient.get('name') + ' to ' + cmd.message.author.nickname) # If item could not be returned print to console
        response = "That recipe does not exist"
        await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
        return

    # Remove ingredients and create the product
    response += " to get "

    for item in ingredients: # Actually deleting ingredients
        ewitem.item_delete(item.get('id_item'))

    product_counter = 1
    for product in found_recipe.products:
        # Adding products to response, quest items dont have a 'name' by default so they need to be handled separately
        if product_counter == 1:
            try:
                if product[0] != ewcfg.it_questitem:
                    response += product[1].get('name') + ' '
                else:
                    response += product[1].get('qitem_name') + ' '
            except:
                print('Failed to get item name for product ' + str(product_counter) + ' of ' + + found_recipe.str_name)
        elif product_counter != len(found_recipe.products):
            try:
                if product[0] != ewcfg.it_questitem:
                    response += 'and ' + product[1].get('name') + ' '
                else:
                    response += 'and ' + product[1].get('qitem_name') + ' '
            except:
                print('Failed to get item name for product ' + str(product_counter) + ' of ' + + found_recipe.str_name)
        else:
            try:
                if product[0] != ewcfg.it_questitem:
                    response += 'and ' + product[1].get('name') + '.'
                else:
                    response += 'and ' + product[1].get('qitem_name') + '.'
            except:
                print('Failed to get item name for product ' + str(product_counter) + ' of ' + + found_recipe.str_name)
        product_counter +=1
        #TODO
        # Figure out how to handle response formatting in a better way, this is bullshit and kinda huge but
        # It may need to be able to handle quest items in the future
        # Literally Fuck Names

        # Actually create the product
        ewitem.item_create(
            item_type=product[0],
            id_user=cmd.message.author.id,
            id_server=cmd.message.server.id,
            item_props=product[1]
        )

    user_data.persist()
    # Send response
    await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))