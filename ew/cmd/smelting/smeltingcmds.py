import random

from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.static import cfg as ewcfg
from ew.static import cosmetics
from ew.static import cosmetics as static_cosmetics
from ew.static import smelting
from ew.static import vendors
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as itm_utils
from ew.utils.combat import EwUser
from .smeltingutils import smeltsoul


# Smelting command. It's like other games call "crafting"... but BETTER and for FREE!!
async def smelt(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # Find sought recipe.
    if cmd.tokens_count > 1:
        sought_result = ewutils.flattenTokenListToString(cmd.tokens[1:])
        found_recipe = smelting.smelting_recipe_map.get(sought_result)

        if found_recipe != None:
            if 'soul' in found_recipe.products:
                return await smeltsoul(cmd=cmd)

            # Checks what ingredients are needed to smelt the recipe.
            necessary_ingredients = found_recipe.ingredients
            necessary_ingredients_list = []

            owned_ingredients = []

            # Seeks out the necessary ingredients in your inventory.
            missing_ingredients = []

            for matched_item in necessary_ingredients:
                necessary_items = necessary_ingredients.get(matched_item)
                necessary_str = "{} {}".format(necessary_items, matched_item)
                if necessary_items > 1:
                    necessary_str += "s"
                necessary_ingredients_list.append(necessary_str)

                sought_items = itm_utils.find_item_all(item_search=matched_item, id_user=user_data.id_user, id_server=user_data.id_server)
                missing_items = necessary_items - len(sought_items)
                if missing_items > 0:
                    missing_str = "{} {}".format(missing_items, matched_item)
                    if missing_items > 1:
                        missing_str += "s"
                    missing_ingredients.append(missing_str)
                else:
                    for i in range(necessary_ingredients.get(matched_item)):
                        sought_item = sought_items.pop()
                        owned_ingredients.append(sought_item.get('id_item'))

            # If you don't have all the necessary ingredients.
            if len(missing_ingredients) > 0:
                response = "You've never done this before, have you? To smelt {}, you’ll need to combine *{}*.".format(found_recipe.str_name, ewutils.formatNiceList(names=necessary_ingredients_list, conjunction="and"))

                response += " You are missing *{}*.".format(ewutils.formatNiceList(names=missing_ingredients, conjunction="and"))

            else:
                # If you try to smelt a random cosmetic, use old smelting code to calculate what your result will be.
                if found_recipe.id_recipe == "coolcosmetic" or found_recipe.id_recipe == "toughcosmetic" or found_recipe.id_recipe == "smartcosmetic" or found_recipe.id_recipe == "beautifulcosmetic" or found_recipe.id_recipe == "cutecosmetic":

                    if not bknd_item.check_inv_capacity(user_data=user_data, item_type=ewcfg.it_cosmetic):
                        response = "You can't carry anymore cosmetic items."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    patrician_rarity = 100
                    patrician_smelted = random.randint(1, patrician_rarity)
                    patrician = False

                    if patrician_smelted <= 5:
                        patrician = True

                    cosmetics_list = []

                    if found_recipe.id_recipe == "toughcosmetic":
                        style = ewcfg.style_tough
                    elif found_recipe.id_recipe == "smartcosmetic":
                        style = ewcfg.style_smart
                    elif found_recipe.id_recipe == "beautifulcosmetic":
                        style = ewcfg.style_beautiful
                    elif found_recipe.id_recipe == "cutecosmetic":
                        style = ewcfg.style_cute
                    else:
                        style = ewcfg.style_cool

                    for result in static_cosmetics.cosmetic_items_list:
                        if result.style == style and result.acquisition == ewcfg.acquisition_smelting and result.id_cosmetic not in static_cosmetics.unique_smeltables:
                            cosmetics_list.append(result)
                        else:
                            pass

                    items = []

                    for cosmetic in cosmetics_list:
                        if patrician and cosmetic.rarity == ewcfg.rarity_patrician:
                            items.append(cosmetic)
                        elif not patrician and cosmetic.rarity == ewcfg.rarity_plebeian:
                            items.append(cosmetic)

                    item = items[random.randint(0, len(items) - 1)]

                    item_props = itm_utils.gen_item_props(item)

                    bknd_item.item_create(
                        item_type=item.item_type,
                        id_user=cmd.message.author.id,
                        id_server=cmd.guild.id,
                        item_props=item_props
                    )

                # If you're trying to smelt a specific item.
                else:
                    possible_results = []

                    # Matches the recipe's listed products to actual items.
                    for result in vendors.smelt_results:
                        if hasattr(result, 'id_item'):
                            if result.id_item not in found_recipe.products:
                                pass
                            else:
                                possible_results.append(result)
                        if hasattr(result, 'id_food'):
                            if result.id_food not in found_recipe.products:
                                pass
                            else:
                                possible_results.append(result)
                        if hasattr(result, 'id_cosmetic'):
                            if result.id_cosmetic not in found_recipe.products:
                                pass
                            else:
                                possible_results.append(result)
                        if hasattr(result, 'id_weapon'):
                            if result.id_weapon not in found_recipe.products:
                                pass
                            else:
                                possible_results.append(result)
                        if hasattr(result, 'id_furniture'):
                            if result.id_furniture not in found_recipe.products:
                                pass
                            else:
                                possible_results.append(result)
                    # If there are multiple possible products, randomly select one.
                    item = random.choice(possible_results)

                    if not bknd_item.check_inv_capacity(user_data=user_data, item_type=item.item_type):
                        # Check for ingredients of the same type as the target item
                        same_type_count = 0
                        for ingred_id in owned_ingredients:
                            ingredient_it = EwItem(id_item=ingred_id)
                            if ingredient_it.item_type == item.item_type:
                                same_type_count += 1
                        # Allow people to craft items over the type limit if it lowers the overall number of that type
                        if same_type_count <= 1:
                            response = "You can't carry any more {}s.".format(item.item_type)
                            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    item_props = itm_utils.gen_item_props(item)

                    newitem_id = bknd_item.item_create(
                        item_type=item.item_type,
                        id_user=cmd.message.author.id,
                        id_server=cmd.guild.id,
                        item_props=item_props
                    )

                for id_item in owned_ingredients:
                    item_check = EwItem(id_item=id_item)
                    if item_check.item_props.get('id_cosmetic') != 'soul':
                        bknd_item.item_delete(id_item=id_item)
                    else:
                        newitem = EwItem(id_item=newitem_id)
                        newitem.item_props['target'] = id_item
                        newitem.persist()
                        bknd_item.give_item(id_item=id_item, id_user='soulcraft', id_server=cmd.guild.id)

                name = ""
                if hasattr(item, 'str_name'):
                    name = item.str_name
                elif hasattr(item, 'id_weapon'):
                    name = item.id_weapon

                response = "You sacrifice your {} to smelt a {}!!".format(ewutils.formatNiceList(names=necessary_ingredients_list, conjunction="and"), name)

                user_data.persist()

        else:
            response = "There is no recipe by the name."

    else:
        response = "Please specify a desired smelt result."

    # Send response
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# "wcim", "whatcanimake", "whatmake", "usedfor" command - finds the item the player is asking for and tells them all smelting recipes that use that item
# added by huck on 9/3/2020
async def find_recipes_by_item(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    used_recipe = None

    # if the player specifies an item name
    if cmd.tokens_count > 1:
        sought_item = ewutils.flattenTokenListToString(cmd.tokens[1:])

        # Allow for the use of recipe aliases
        found_recipe = smelting.smelting_recipe_map.get(sought_item)
        if found_recipe != None:
            used_recipe = found_recipe.id_recipe

        # item_sought_in_inventory = bknd_item.find_item(item_search=sought_item, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)
        makes_sought_item = []
        uses_sought_item = []

        # if the item name is an item in the player's inventory, we're assuming that the player is looking up information about this item specifically.
        # if item_sought_in_inventory is not None:
        # sought_item = item_sought_in_inventory.id_item
        # print(item_sought_in_inventory['item_def'])
        # man i could NOT get this to work . maybe another day

        # finds the recipes in questions that applys
        for name in smelting.recipe_names:
            # find recipes that this item is used as an ingredient in
            if smelting.smelting_recipe_map[name].ingredients.get(sought_item) is not None:
                uses_sought_item.append(name)

            # find recipes used to create this item
            elif sought_item in smelting.smelting_recipe_map[name].products:
                makes_sought_item.append(smelting.smelting_recipe_map[name])

            # finds recipes based on possible recipe aliases
            elif used_recipe in smelting.smelting_recipe_map[name].products:
                makes_sought_item.append(smelting.smelting_recipe_map[name])

        # zero matches in either of the above:
        if len(makes_sought_item) < 1 and len(uses_sought_item) < 1:
            response = "No recipes found for *{}*.".format(sought_item)

        # adds the recipe list to a response
        else:
            response = "\n"
            number_recipe = 1
            list_length = len(makes_sought_item)
            for item in makes_sought_item:
                if (item.id_recipe == "toughcosmetic" and cosmetics.cosmetic_map[sought_item].style != ewcfg.style_tough
                        or item.id_recipe == "smartcosmetic" and cosmetics.cosmetic_map[sought_item].style != ewcfg.style_smart
                        or item.id_recipe == "beautifulcosmetic" and cosmetics.cosmetic_map[sought_item].style != ewcfg.style_beautiful
                        or item.id_recipe == "cutecosmetic" and cosmetics.cosmetic_map[sought_item].style != ewcfg.style_cute
                        or item.id_recipe == "coolcosmetic" and cosmetics.cosmetic_map[sought_item].style != ewcfg.style_cool
                        or (item.id_recipe in ["toughcosmetic", "smartcosmetic", "beautifulcosmetic", "cutecosmetic", "coolcosmetic"] and cosmetics.cosmetic_map[sought_item].id_cosmetic in cosmetics.unique_smeltables)):
                    list_length -= 1
                    continue
                else:
                    # formats items in form "# item" (like "1 poudrin" or whatever)
                    ingredients_list = []
                    ingredient_strings = []
                    for ingredient in item.ingredients:
                        ingredient_strings.append("{} {}".format(item.ingredients.get(ingredient), ingredient))

                    if number_recipe == 1:
                        response += "To smelt this item, you'll need *{}*. ({})\n".format(ewutils.formatNiceList(names=ingredient_strings, conjunction="and"), item.id_recipe)
                    else:
                        response += "Alternatively, to smelt this item, you'll need *{}*. ({})\n".format(ewutils.formatNiceList(names=ingredient_strings, conjunction="and"), item.id_recipe)
                    number_recipe += 1

            if len(uses_sought_item) > 0:
                response += "This item can be used to smelt *{}*.".format(ewutils.formatNiceList(names=uses_sought_item, conjunction="and"))



    # if the player doesnt specify a 2nd argument
    else:
        response = "Please specify an item you would like to look up usage for."

    # send response to player
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
