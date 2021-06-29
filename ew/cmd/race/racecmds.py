import asyncio
import random
import time

from ew.utils import core as ewutils
from ew.backend import item as bknd_item
from ew.backend.market import EwMarket
from ew.static import cfg as ewcfg
from ew.static import items as static_items
from ew.static import poi as poi_static
from ew.utils import cmd as cmd_utils
from ew.utils import frontend as fe_utils
from ew.utils.combat import EwUser
from ew.utils.district import EwDistrict



async def set_race(cmd):
    response = ""
    user_data = EwUser(member=cmd.message.author)
    time_now = int(time.time())

    forbidden_races = [
        'retard',
        'anime',
        'animegirl',
        'white',
        'black',
        'aryan',
        'epic',  # this one is for you, meaty
    ]


    if time_now > user_data.time_racialability or ewutils.DEBUG_OPTIONS['no_race_cooldown'] == True: #pass cooldown check when debug racecooldown is on
        if len(cmd.tokens) > 1:
            desired_race = cmd.tokens[1]

            
            if desired_race in forbidden_races:
                desired_race = ewcfg.race_forbidden

            selected_race = ewcfg.defined_races.get(desired_race)

            #if race found in dictionary, set race
            if selected_race != None:
                response = selected_race.get("acknowledgement_str").format(cmd = selected_race.get("racial_cmd"))

                # only set the cooldown if the user is switching race, rather than setting it up for the first time
                if user_data.race:
                    user_data.time_racialability = time_now + ewcfg.cd_change_race
                user_data.race = desired_race
                user_data.persist()
            else:
                race_list = list(ewcfg.defined_races.keys())
                race_list.remove("forbidden")
                response = '"{unknown_race}" is not an officially recognized race in NLACakaNM. Try one of the following instead: {race_list}.'.format(unknown_race = desired_race, race_list = ", ".join(["**{}**".format(race) for race in race_list]))
        else:
            race_list = list(ewcfg.defined_races.keys())
            race_list.remove("forbidden")
            response = "Please select a race from the following: {race_list}.".format(race_list = ", ".join(["**{}**".format(race) for race in race_list]))
    else:
        response = "You have changed your race recently. Try again later, race traitor."



    return await fe_utils.send_response(response, cmd)


async def exist(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_humanoid:
        exist_responses = [
            "You look at the sky and wonder how the weather will be tomorrow. Maybe you'll get to see the sun for once.",
            "You take a deep breath and reminisce about your childhood. Mom, I miss you...",
            "You suddenly remember something funny you did with your friends many years ago, and break into a bittersweet smile. Man, those were the times.",
            "You contemplate what to have for dinner tomorrow. If only you had someone to share it with.",
            "You almost trip, but quickly react to avoid falling. God, I hope no one saw that.",
            "You catch a whiff of body odour, and stealthily check if it's coming from you. Did you forget to put on deodorant this morning?",
            "You come up with a witty reply to an argument you had last week. If only you were always this clever.",
        ]
        response = random.choice(exist_responses)

    else: 
        response = "You people are not allowed to do that."


    return await fe_utils.send_response(response, cmd)
    


async def ree(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""

    if user_data.race == ewcfg.race_amphibian:
        response = "*{}* lets out a sonorous warcry.\n".format(cmd.message.author.display_name)
        roll = random.randrange(50)

        if roll == 0: # cute frog video
            response += "https://youtu.be/cBkWhkAZ9ds"
        else: # long ree
            response += "**R{}**".format(random.randrange(200, 500) * "E")

        return await fe_utils.send_response(response, cmd, format_name = False)
    else:
        response = "You people are not allowed to do that."
        return await fe_utils.send_response(response, cmd)

    


async def autocannibalize(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_food:
        time_now = int(time.time())
        if time_now > user_data.time_racialability or ewutils.DEBUG_OPTIONS['no_race_cooldown'] == True: #pass cooldown check when debug racecooldown is on
            response = "You give in to the the existential desire all foods have, and take a small bite out of yourself. It hurts like a bitch, but God **DAMN** you're tasty."
            user_data.time_racialability = time_now + ewcfg.cd_autocannibalize
            user_data.hunger = max(user_data.hunger - (user_data.get_hunger_max() * 0.01), 0)
            user_data.change_slimes(n=-user_data.slimes * 0.001)
            user_data.persist()
        else:
            response = "Slow down! You don't want to eat yourself into oblivion."
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def rattle(cmd):
    user_data = EwUser(member=cmd.message.author)

    if user_data.race == ewcfg.race_skeleton:
        time_now = int(time.time())

        # generate bone item when off cooldown
        if (time_now > user_data.time_racialability or ewutils.DEBUG_OPTIONS['no_race_cooldown'] == True) and random.randrange(10) == 0: #pass cooldown check when debug racecooldown is on
            bone_item = next(i for i in static_items.item_list if i.context == "player_bone")
            bknd_item.item_create(
                item_type=ewcfg.it_item,
                id_user=user_data.poi,
                id_server=cmd.guild.id,
                item_props={
                    'id_item': bone_item.id_item,
                    'context': bone_item.context,
                    'item_name': bone_item.str_name,
                    'item_desc': bone_item.str_desc,
                }
            )
            user_data.time_racialability = time_now + ewcfg.cd_drop_bone
            user_data.persist()

        # spook mentioned player
        if cmd.mentions_count == 1:
            responses = [
                ", sending a shiver down their spine.",
                ", who clearly does not appreciate it.",
                ". They almost faint in shock.",
                ", scaring them so bad they pee themselves a little.",
                ". **NYEEEH!**",
                ", trying to appeal to the bones deep within them.",
                " a little bit too hard. Oof ouch owie.",
                " so viciously they actually get offended.",
                " in an attempt to socialize, but they don't think you should.",
            ]
            response = "You rattle your bones at {}{}".format(cmd.mentions[0].display_name, random.choice(responses))

        # rattle alone
        else:
            response = "You rattle your bones."
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def beep(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_robot:
        roll = random.randrange(100)
        responses = []
        if roll > 19:
            responses = [
                "**BEEP**",
                "**BOOP**",
                "**BRRRRRRT**",
                "**CLICK CLICK**",
                "**BZZZZT**",
                "**WHIRRRRRRR**",
            ]
        elif roll > 0:
            responses = [
                "`ERROR: 'yiff' not in function library in ewrobot.py ln 366`",
                "`ERROR: 418 I'm a teapot`",
                "`ERROR: list index out of range`",
                "`ERROR: 'response' is undefined`",
                "https://youtu.be/7nQ2oiVqKHw",
                "https://youtu.be/Gb2jGy76v0Y"
            ]
        else:
            resp = await cmd_utils.start(cmd=cmd)
            response = "```CRITICAL ERROR: 'life_state' NOT FOUND\nINITIATING LIFECYCLE TERMINATION SEQUENCE IN "
            await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, response + "10 SECONDS...```"))
            for i in range(10, 0, -1):
                await asyncio.sleep(1)
                await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, response + "{} SECONDS...```".format(i)))
            await asyncio.sleep(1)
            await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, response + "0 SECONDS...```"))
            await asyncio.sleep(1)
            await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, response + "0 SECONDS...\nERROR: 'reboot' not in function library in ewrobot.py ln 459```"))
            return
        response = random.choice(responses)
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def yiff(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_furry:
        if cmd.mentions_count == 1:
            target_data = EwUser(member=cmd.mentions[0])
            if target_data.race == ewcfg.race_furry:
                poi = poi_static.id_to_poi.get(user_data.poi)
                if (target_data.poi == user_data.poi) and poi.is_apartment:  # low effort
                    responses = [
                        "Wow.",
                        "Mhmm.",
                        "You yiff.",
                        "Yikes.",
                        "🤮",
                        "Yup."
                        "Congratulations."
                    ]
                    response = random.choice(responses)
                else:
                    response = "Out here, in the streets? Fuck no, what's wrong with you?"
            else:
                response = "Only furries can yiff, better find another partner."
            pass
        elif cmd.mentions_count == 0:
            response = "You can't yiff by yourself."
        elif cmd.mentions_count > 1:
            response = "The world is not prepared for a furry orgy."
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def hiss(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_scalie:
        response = "*{}* lets out a piercing hiss.\n".format(cmd.message.author.display_name)
        sssss = random.randrange(200, 500) * "s"  # sssssssss
        response += "**HIS{}**".format(''.join(random.choice((str.upper, str.lower))(s) for s in sssss))
        return await fe_utils.send_response(response, cmd, format_name = False)

    else:
        response = "You people are not allowed to do that."
        return await fe_utils.send_response(response, cmd)


async def jiggle(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_slimederived:
        if cmd.mentions_count == 0:
            response = "You pleasantly jiggle by yourself."
        if cmd.mentions_count > 1:
            response = "You jiggle at the crowd."
        if cmd.mentions_count == 1:
            target_member = cmd.mentions[0]
            target_data = EwUser(member=target_member)

            #jiggle with fellow slime-derived
            if target_data.race == ewcfg.race_slimederived:
                response = "You jiggle along with {}.".format(target_member.display_name)
            
            #jiggle at ghost
            elif target_data.life_state == ewcfg.life_state_corpse and user_data.life_state != ewcfg.life_state_corpse:
                response = "You jiggle in fear of {}.".format(target_member.display_name)

            #jiggle at kingpin
            elif target_data.life_state == ewcfg.life_state_kingpin:
                if target_data.life_state == ewcfg.life_state_enlisted and target_data.faction != user_data.faction:
                    response = "You spitefully jiggle at {}.".format(target_member.display_name)
                else:
                    response = "You jiggle in awe of {}.".format(target_member.display_name)
                
            #jiggle at gangster
            elif target_data.life_state == ewcfg.life_state_enlisted:
                if target_data.faction == user_data.faction:
                    response = "You jiggle at {} as a gesture of friendship.".format(target_member.display_name)
                else:
                    response = "You jiggle at {} menacingly.".format(target_member.display_name)
            
            #catch all
            else:
                response = "You jiggle at {}.".format(target_member.display_name)
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def flutter(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.race == ewcfg.race_avian:
        district_data = EwDistrict(district=user_data.poi, id_server=cmd.guild.id)
        market_data = EwMarket(id_server=cmd.guild.id)
        response = "You flap your wings in an attempt to fly, but "
        excuses = []

        if market_data.weather == ewcfg.weather_lightning:
            excuses.append("the current weather would make that a bit dangerous, so you decide not to.")
        if ewcfg.mutation_id_bigbones in user_data.get_mutations():
            excuses.append("your bones are too big for you to get off the ground.")
        if ewcfg.mutation_id_lightasafeather in user_data.get_mutations():
            excuses.append("your wings are too skinny to generate enough lift.")

        if 6 <= market_data.clock >= 20:
            excuses.append("it's not safe to fly at night, so you decide not to.")
        else:
            excuses.append("flying in plain daylight might get you shot off the sky, so you decide not to.")

        if user_data.slimes > 1000000:
            excuses.append("you have too much slime on you, so you don't even get off the ground.")
        else:
            excuses.append("you're too weak for this right now, gonna need to get more slime.")

        if user_data.life_state == ewcfg.life_state_corpse:
            excuses.append("your incorporeal wings generate no lift.")
        elif user_data.life_state == ewcfg.life_state_juvenile:
            excuses.append("you lack the moral fiber to do so.")
        else:
            if user_data.faction == ewcfg.faction_rowdys:
                excuses.append("you end up thrashing with your wings in an unorganized fashion.")
            if user_data.faction == ewcfg.faction_killers:
                excuses.append("you end up doing rapid dabs instead.")

        if len(district_data.get_players_in_district()) > 1:
            excuses.append("it's embarassing to do so with other people around.")
        else:
            excuses.append("you can't be bothered if there's no one here to see you do it.")

        if user_data.hunger / user_data.get_hunger_max() < 0.5:
            excuses.append("you're too hungry, and end up looking for worms instead.")
        else:
            excuses.append("you're too full from your last meal for such vigorous exercise.")

        response += random.choice(excuses)
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def request_petting(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_critter:
        if cmd.mentions_count == 0:
            response = "Request petting from who?"
        if cmd.mentions_count > 1:
            response = "You would die of overpetting."
        if cmd.mentions_count == 1:
            target_member = cmd.mentions[0]
            proposal_response = "You rub against {}'s leg and look at them expectantly. Will they **{}** and give you a rub, or do they **{}** your affection?".format(target_member.display_name, ewcfg.cmd_accept, ewcfg.cmd_refuse)
           
            await fe_utils.send_response(proposal_response, cmd)

            accepted = False
            try:
                msg = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == target_member and
                                                                                             message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])
                if msg != None:
                    if msg.content.lower() == ewcfg.cmd_accept:
                        accepted = True
                    elif msg.content.lower() == ewcfg.cmd_refuse:
                        accepted = False
            except:
                accepted = False

            if accepted:
                responses = [
                    "{user} gets on their back, and {target} gives them a thorough belly rub!",
                    "{target} cups {user}'s head between their hands, rubbing near their little ears with their thumbs.",
                    "{target} picks {user} up and carries them over the place for a little while, so they can see things from above.",
                    "{target} sits down next to {user}, who gets on their lap. They both lie there for a while, comforting one another.",
                    "{target} gets on the floor and starts petting the heck out of {user}!",
                ]
                accepted_response = random.choice(responses).format(user=cmd.message.author.display_name, target=target_member.display_name)
                await fe_utils.send_response(accepted_response, cmd)

            else:
                response = "The pain of rejection will only make you stronger, {}.".format(cmd.message.author.display_name)
    else:
        response = "You people are not allowed to do that."
    if response:
        return await fe_utils.send_response(response, cmd)


async def rampage(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_monster:
        responses = [
            "You repeatedly stomp on the ground with all your savage fury, causing a minor tremor.",
            "You let out a **R" + (random.randrange(10, 100) * "O") + (random.randrange(10, 100) * "A") + "R**.",
            "You bare your teeth and ***SLAM*** the ground below you with your fists.",
            "You fling yourself all over the place while screaming, just to let off some of your primal anger.",
            "You get so fucking furious in such a short period of time you actually just pass out for a second.",
        ]
        response = random.choice(responses)
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def entomize(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_insectoid:
        responses = [
            "You bust some crazy dance moves and waggling motions to alert all onlookers where they may find the nearest diner.",
            "You think back to when you were just a little grub, suckling on the regurgitated nutrient slurry of your caretakers from the hive. Ah...",
            "Like the noble violinist, you croon your hindleg and forewing together to make a beautiful chirping sound, alerting everyone in the immediate vicinity that you're totally DTF right now. _Nice_.",
            "You think about how cool it is to be just a little bug. _Awww yeeeah_.",
            "The biological imperative to propagate future members of your species flares up, blotting out all other thoughts.\nYou remind yourself that you will most likely be cannibalized post-coitus, which thankfully kills your libido.",
            "You wiggle your thorax and rhythmically bounce up and down on all segmented legs, imitating the rustling of leaves and branches in the wind to confuse potential predators.\nThe only thing you accomplish is causing passersby to clear away from you quickly and awkwardly.",
            "A wayward leaf brushes against your neck, sending a shock down each and every one of your muscles and ligaments. You instinctively skitter up the wall of a nearby apartment complex.",
        ]
        response = random.choice(responses)
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def confuse(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_other:
        if cmd.mentions_count == 0:
            if random.randrange(20) == 0:
                response = "ENDLESS WAR takes a cursory glance at you. It still doesn't know what the fuck you are."
            else:
                response = "You confuse yourself. What?"
        if cmd.mentions_count > 1:
            response = "The crowd looks at you, winces slightly, and looks away."
        if cmd.mentions_count == 1:
            target_member = cmd.mentions[0]
            target_data = EwUser(member=target_member)
            if target_data.race == ewcfg.race_other:
                response = "You and {} actually understand each other in a way, despite your differences.".format(target_member.display_name)
            else:
                responses = [
                    "{} doesn't know what on earth they're looking at.".format(target_member.display_name),
                    "{} stares at you, expressionless, then turns away.".format(target_member.display_name),
                    "{} gets a little dizzy from staring at you for too long.".format(target_member.display_name),
                    "{} wonders how you're even alive. Are you?".format(target_member.display_name),
                    "{} has seen some shit. Now they've seen some more.".format(target_member.display_name)
                ]
                response = random.choice(responses)
    else:
        response = "You people are not allowed to do that."

    return await fe_utils.send_response(response, cmd)


async def shamble(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_shambler:
        # Stole response system from the yiff system.
        responses = [
            "You shamble about aimlessly.",
            "You run a decaying hand across the street, remembering what was.",
            "You gnaw on the buildings, trying to relive the glory days.",
            "You groan and walk about.",
            "You remember when all the city was shambled, damn those gankers ruined it all...",  # thanks dakat for this one
            "It was a graveyard smash"
        ]
        response = random.choice(responses)
    else:
        response = "You people are not allowed to do that."
        
    return await fe_utils.send_response(response, cmd)




async def netrun(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_cyborg:
        
        target_name = ""
        responses = []

        if cmd.mentions_count == 1:
            target_name = cmd.mentions[0].display_name
            responses = [
                "You decryped {target}'s harddrive and delete system32.",
                "You hack into {target}'s Instagrime and delete their most liked picture. You monster.",
            ]
        else:
            roll = random.randrange(50)

            if roll < 5: #rare response
                responses = [
                    "https://www.youtube.com/watch?v=rlfwXNOG0eI",
                    "You become the hacker known only as 4chan. Your hands fly across the keyboard as you write an algorithm to steal passwords, credit card information and bank statements. \n```\meranojijn\n   fuvfeourfevrflaerfk;erbperibfeprifaerifaer\n   eifahbniaio\n   eofajpm\neraijnamkmekopkk,\n```",
                ]
            else: #common response
                responses = [
                    "***WHOA DUDE!*** You're walking on the internet.",
                    "As you run through the netscape, you dodge ads for **HOT SLIMEGIRLS IN YOUR AREA**.",
                    "\*Hacker voice\* I'm in.",
                    "A holographic interfaces surround you, the hardlight constucts coming from your cybernetics. You use various arm gestures and hand motions to make seemingly meaningful beeps boops.",
                    '*bzzt* **"Subvert all world governments"** *kzchhh* **"Ship everything to China"**',
                ]
            
        response = random.choice(responses).format(target = target_name)
               
    else:
        response = "You people are not allowed to do that."
        
    return await fe_utils.send_response(response, cmd)

async def strike_deal(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""
    if user_data.race == ewcfg.race_demon:

        # check for proper number of mentions
        if cmd.mentions_count == 0:
            response = "Who are you trying to make a deal with?"
        if cmd.mentions_count > 1:
            response = "You can't strike a deal with {count} people at once.".format(count = cmd.mentions_count)
        
        if cmd.mentions_count == 1:

            #propose deal
            target_member = cmd.mentions[0]
            if (target_member.id == cmd.message.author.id):
                
                response = "You can't strike a deal with yourself."
                return await fe_utils.send_response(response, cmd)
            else:

                proposal_response = "*{target}:* {user} is proposing a deal with the devil. Will you **{accept}** or **{refuse}** their offer?".format(target=target_member.display_name, user=cmd.message.author.display_name, accept=ewcfg.cmd_accept, refuse=ewcfg.cmd_refuse)
                await fe_utils.send_response(proposal_response, cmd, format_name=False)

                #wait for response
                accepted = False
                try:
                    msg = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == target_member and
                                                                                                message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])
                    if msg != None:
                        if msg.content.lower() == ewcfg.cmd_accept:
                            accepted = True
                        elif msg.content.lower() == ewcfg.cmd_refuse:
                            accepted = False
                except:
                    accepted = False

                response = ""
                #deal accepted response
                if accepted:
                    target_data = EwUser(member=target_member)
                    responses = []
                    #if target has no soul
                    if target_data.has_soul == 0: 
                        responses = [
                            "*{target}:* {user} dances around in excitement before realizing you don’t have a soul. They shout obscenities at you for wasting their time.",
                        ] 
                    else:
                        responses = [
                            "*{target}:* {user} cackles maniacally as magic ethereal chains bind you from the depths of hell. It’s a good thing mist can’t prevent you from going about your buisness.",
                            "*{target}:* {user} presents the contract on an ancient looking piece of parchment. Oddly enough it looks like a printer did most of the writing. Locating the fine print, you see it’s so small that it’s basically a pixel smudge. You sign the deal knowing it’ll never hold up in any court.",
                            "*{user}:* {target} accepts your deal with bold enthusiasm. They begin listing off all the rewards they’d dream of receiving ranging from game updates to funny hats. Maybe you shouldn’t tell them it’ll cost them their soul... \n\nyet.",
                        ]

                    response = random.choice(responses).format(user=cmd.message.author.display_name, target=target_member.display_name)
        

                #deal refused response
                else:
                    responses = [
                        "*{user}:* Offput by the deal's sinister vibes and your pushiness, {target} declines your offer. ",
                        "*{target}:* {user} grinds their teeth at your refusal. They try and play it cool but it’s pretty obvious when a demon is seething"
                    ]
                    response = random.choice(responses).format(user=cmd.message.author.display_name, target=target_member.display_name)


        return await fe_utils.send_response(response, cmd, format_name=False)
    else:
        response = "You people are not allowed to do that."
        return await fe_utils.send_response(response, cmd)
