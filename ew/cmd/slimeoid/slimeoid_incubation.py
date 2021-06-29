
"""
    Initialize incubation process
"""
async def incubateslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)

    if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
        response = "You must go to the NLACU Laboratories in Brawlden to create a Slimeoid."
        # Go to final response

    elif user_data.life_state == ewcfg.life_state_corpse:
        response = "Ghosts cannot interact with the NLACU Lab apparati."
        # Go to final response

    #TODO: change this because player can have more than one slimeoid now
    # this is fucking brutal. poor slimeoid
    elif slimeoid_data.life_state == ewcfg.slimeoid_state_active:
        response = "You have already created a Slimeoid. Dissolve your current slimeoid before incubating a new one."
        # Go to final response

    elif slimeoid_data.life_state == ewcfg.slimeoid_state_forming:
        response = "You are already in the process of incubating a Slimeoid."
        # Go to final response


    else:
        
        #Check if player has too many slimeoids
        slimeoid_count = get_slimeoid_count(user_id=cmd.message.author.id, server_id=cmd.guild.id)
        
        if slimeoid_count >= 3:
            response = "You have too many slimeoids."
            # Go to final response


        else:
            #Check if player has a poudrin
            poudrin = bknd_item.find_item(item_search=ewcfg.item_id_slimepoudrin, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)
            if poudrin is None:
                response = "You need a slime poudrin."
                # Go to final response
    

            else:
                # Get arguement for how big the slimeoid should be made
                injected_slime = None
                if cmd.tokens_count > 1:
                    injected_slime = ewutils.getIntToken(tokens=cmd.tokens, allow_all=True)
                    # -1 from getIntToken() means use all slime
                    if injected_slime == -1:
                        injected_slime = user_data.slimes

                if injected_slime == None:
                    response = "You must contribute some of your own slime to create a Slimeoid. Specify how much slime you will sacrifice."
                    # Go to final response

                elif injected_slime > user_data.slimes:
                    response = "You do not have that much slime to sacrifice."
                    # Go to final response

                else:
                    # delete a slime poudrin from the player's inventory
                    bknd_item.item_delete(id_item=poudrin.get('id_item'))

                    # Remove slime
                    user_data.change_slimes(n=-injected_slime)
                    user_data.persist()

                    # Setup gestating slimeoid
                    level = len(str(injected_slime))
                    slimeoid.life_state = ewcfg.slimeoid_state_forming
                    slimeoid.level = level
                    slimeoid.id_user = str(user_data.id_user)
                    slimeoid.id_server = user_data.id_server
                    slimeoid.persist()

                    response = "You place a poudrin into a small opening on the console. As you do, a needle shoots up and pricks your finger, intravenously extracting {injected_slime} slime from your body. The poudrin is then dropped into the gestation tank. Looking through the observation window, you see what was once your slime begin to seep into the tank and accrete around the poudrin. The incubation of a new Slimeoid has begun! {slime_emote}".format(
                        injected_slime = str(injected_slime), 
                        slime_emote = ewcfg.emote_slime2
                    )
                    # Go to final response



    # Final response
    await fe_utils.send_response(response, cmd)


"""
    Handle all part changes of slimeoid during incubation process
"""
async def change_body_part(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    # Check if player is in the labs and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response


    if reponse is None: # Slimeoid is incubating

        button_pressed = None

        # If player does not provide an argument for the button they pressed
        if cmd.tokens_count == 1:
            response = "You must specify a body type. Choose an option from the buttons on the body console labelled A through G."
            # Go to final response

        else:
            
            # Interperate which part player is trying to grow by command name

            cmd_to_change_type = {
                ewcfg.cmd_growbody: ("change body", sl_static.body_map),
                ewcfg.cmd_growhead: ("change head", sl_static.head_map),
                ewcfg.cmd_growlegs: ("change legs", sl_static.mobility_map),
                ewcfg.cmd_growweapon: ("change weapon", sl_static.offense_map),
                ewcfg.cmd_growarmor: ("change armor", sl_static.defense_map),
                ewcfg.cmd_growspecial: ("change special", sl_static.special_map),
                ewcfg.cmd_growbrain: ("change brain", sl_static.brain_map),
            }

            # Gets part_map based on command used
            desired_change, part_map = cmd_to_change_type.get(cmd.tokens[0])
            pressed_button = cmd.tokens[1].lower()

            # Check if desired part is in part map 
            part = part_map.get(pressed_button)

            # If no part is found
            if part == None:
                response = "Choose an option from the buttons on the body console labelled A through G."
                # Go to final response

            
            else: 

                #TODO: this could be simplified if slimeoid part id variables to one name
                # e.g. EwSlimeoidBody.id_body and EwSlimeoidBody.id_head were called EwSlimeoidBody.part_id and EwSlimeoidBody.part_id instead
                if desired_change == "change body":
                    slimeoid.body = part.id_body

                elif desired_change == "change head":
                    slimeoid.head = part.id_head

                elif desired_change == "change legs":
                    slimeoid.legs = part.id_mobility

                elif desired_change == "change weapon":
                    slimeoid.weapon = part.id_offense

                elif desired_change == "change armor":
                    slimeoid.armor = part.id_defense

                elif desired_change == "change special":
                    slimeoid.special = part.id_special

                elif desired_change == "change brain":
                    slimeoid.ai = part.id_brain

                else:
                    response = f"Some thing when wrong with {cmd.tokens[0]} command. Please report bug." # something when wrong in cmd_to_change_type
                    return await fe_utils.send_response(response, cmd)
                    # Break out of command early because of error

                
                slimeoid.persist()
                response = "{}".format(part.str_create)
                # Go to final response


    # Final response
    await fe_utils.send_response(response, cmd)
                

"""
    Name slimeoid during incubation process
"""
async def name_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    # Check if player is in the labs and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response


    if reponse is None: # Slimeoid is incubating


        # Check if player has specified a name
        if cmd.tokens_count < 2:
            response = "You must specify a name."
            # Go to final response


        else:

            # Turn entire message minus "!nameslimeoid" in to name variable
            name = cmd.message.content[(len(ewcfg.cmd_nameslimeoid)):].strip()

            # Limit name length to 32 characters
            if len(name) > 32:
                response = "That name is too long. ({:,}/32)".format(len(name))
                # Go to final response


            else:
                # Save slimeoid name
                slimeoid.name = str(name)

                user_data.persist()
                slimeoid.persist()

                response = "You enter the name {} into the console.".format(str(name))
                # Go to final response


    # Final response
    await fe_utils.send_response(response, cmd)


"""
    Handle all raise and lower stat commands during slimeoid incubation
"""
async def change_stat(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    # Check if player is in the labs and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response


    if reponse is None: # Slimeoid is incubating

        available_points = slimeoid.level - slimeoid.atk - slimeoid.defense - slimeoid.intel

        # Check if stat points are available
        if (available_points >= slimeoid.level):
            response = "You have allocated all of your Slimeoid's potential. Try !lowering some of its attributes first."
            response += stat_breakdown_str(slimeoid.atk, slimeoid.defense, slimeoid.intel, available_points)
            # Go to final response


        else:

            # Interperate which stat player is trying to change by command name

            cmd_to_change_type = {
                ewcfg.cmd_raisemoxie: "+ moxie",
                ewcfg.cmd_raisegrit: "+ grit",
                ewcfg.cmd_raisechutzpah: "+ chutzpah",
                ewcfg.cmd_lowermoxie: "- moxie",
                ewcfg.cmd_lowergrit: "- grit",
                ewcfg.cmd_lowerchutzpah: "- chutzpah",
            }
            desired_change = cmd_to_change_type.get(cmd.tokens[0])

            moxie_mod = 0
            grit_mod = 0
            chutzpah_mod = 0
            
            # Plus one stat
            if desired_change == "+ moxie":
                moxie_mod = 1
                changed_stat = "moxie"

            elif desired_change == "+ grit":
                grit_mod = 1
                changed_stat = "grit"

            elif desired_change == "+ chutzpah":
                chutzpah_mod = 1
                changed_stat = "chutzpah"

            # Minus one stat
            elif desired_change == "- moxie":
                moxie_mod = -1
                changed_stat = "moxie"

            elif desired_change == "- grit":
                grit_mod = -1
                changed_stat = "grit"

            elif desired_change == "- chutzpah":
                mox_mod = -1
                chutzpah_mod = "chutzpah"

            else:
                response = f"Some thing when wrong with {cmd.tokens[0]} command. Please report bug." # something when wrong in cmd_to_change_type
                return await fe_utils.send_response(response, cmd)
                # Break out of command early because of error


            # Now that we no what stat is trying to be changed do the final checks

            # Check if player is trying to lower a stat below zero
            if ((slimeoid.atk + moxie_mod < 0) or (slimeoid.defense + grit_mod < 0) or (slimeoid.intel + chutzpah_mod < 0))
                response = f"You cannot reduce your slimeoid's {changed_stat} any further."
                response += stat_breakdown_str(slimeoid.atk, slimeoid.defense, slimeoid.intel, available_points)
                # Go to final response


            # Command successful
            else:
                
                # Change slimeoid stats
                slimeoid.atk + moxie_mod 
                slimeoid.defense + grit_mod 
                slimeoid.intel + chutzpah_mod
                # Save changes
                slimeoid.persist()

                # Generate response
                if (moxie_mod + grit_mod + chuzpah_mod > 0)
                    response = f"Your gestating slimeoid gains more {changed_stat}."
                else:
                    response = f"Your gestating slimeoid loses some {changed_stat}."
                response += stat_breakdown_str(slimeoid.atk, slimeoid.defense, slimeoid.intel, available_points)
                # Go to final response



    # Final response
    await fe_utils.send_response(response, cmd)


"""
    Check if all parts have been added and complete the incubation processs
"""
async def spawnslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    # Check if player is in the labs and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response


    if reponse is None: # Slimeoid is incubating
            incomplete = False
            required_parts_explanation = ""


            # Check if parts are missing 
            # Bold missing part names for visual clarity
            if (slimeoid.body == ""):
                incomplete = True
                required_parts_explanation += "\nIts **BODY** has not yet been given a distinct form."

            if (slimeoid.head == ""):
                incomplete = True
                required_parts_explanation += "\nIt does not yet have a **HEAD**."

            if (slimeoid.legs == ""):
                incomplete = True
                required_parts_explanation = += "\nIt has no **LEGS** or means of locomotion."

            if (slimeoid.weapon == ""):
                incomplete = True
                required_parts_explanation = += "\nIt lacks a means of **WEAPON**."

            if (slimeoid.armor == ""):
                incomplete = True
                required_parts_explanation = += "\nIt lacks any form of **ARMOR**."

            if (slimeoid.special == ""):
                incomplete = True
                required_parts_explanation = += "\nIt lacks a **SPECIAL** ability."

            if (slimeoid.ai == ""):
                incomplete = True
                required_parts_explanation = "\nIt does not yet have a **BRAIN**."

            if ((slimeoid.atk + slimeoid.defense + slimeoid.intel) < (slimeoid.level)):
                incomplete = True
                required_parts_explanation = "\nIt still has potential that must be distributed between **MOXIE**, **GRIT** and **CHUTZPAH**."

            if (slimeoid.name == ""):
                incomplete = True
                required_parts_explanation = "\nIt needs a **NAME**."

            if incomplete:
                # Add explanation of which parts need to be added
                response = f"Your slimeoid is not yet ready to be spawned from the gestation vat. {required_parts_explanation}"
                # Go to final response

            
            else: 
                # Set slimeoid as active
                slimeoid.life_state = ewcfg.slimeoid_state_active
                # Save slimeoid
                slimeoid.persist()

                # Generate spawning flavor text
                response = "You press the big red button labelled 'SPAWN'. The console lights up and there is a rush of mechanical noise as the fluid drains rapidly out of the gestation tube. The newly born Slimeoid within writhes in confusion before being sucked down an ejection chute and spat out messily onto the laboratory floor at your feet. Happy birthday, {slimeoid_name} the Slimeoid!! {slime_heart_emote}".format(
                    slimeoid_name = slimeoid.name, 
                    slime_heart_emote = ewcfg.emote_slimeheart
                )


                # Add slimeoid description
                response += "\n\n{} is a {}-foot-tall Slimeoid.".format(slimeoid.name, str(slimeoid.level))
                response += slimeoid_utils.slimeoid_describe(slimeoid)


                # Add slimeoid's reaction based on brain type
                brain = sl_static.brain_map.get(slimeoid.ai)
                response += "\n\n" + brain.str_spawn.format(
                    slimeoid_name=slimeoid.name
                )
                # Go to final response


    # Final response
    await fe_utils.send_response(response, cmd)


###
# Utilities
###

""" 
    Does some of the basic checks all slimeoid growing commands do
    Returns response string if there is a reason the player can't do the command
"""
def basic_slimeoid_incubation_checks(channel_name, user_data, slimeoid_data)
    # Check if player in labs and is not a ghost 
    if channel_name != ewcfg.channel_slimeoidlab:
        return "You must go to the NLACU Laboratories in Brawlden to create a Slimeoid."
    elif user_data.life_state == ewcfg.life_state_corpse:
        return "Ghosts cannot interact with the NLACU Lab apparati."
     
    # Check for incubating slimeoid
    # TODO: other checks for slimeoid lifestates?
    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        return "You must begin incubating a new slimeoid first."
    elif slimeoid.life_state == ewcfg.slimeoid_state_active:
        return "Your slimeoid is already fully formed."

    else:
        return None

def stat_breakdown_str(moxie, grit, chuzpah, available_points = None):
    response = f"\nMoxie: {moxie}"
    response += f"\nGrit: {grit}"
    response += f"\nChutzpah: {chuzpah}"
    
    #optional line if you just want to print the stats alone
    if available_points != None:
        response += f"\nPoints remaining: {available_points}"

    return response
    