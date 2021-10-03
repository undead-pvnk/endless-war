import random
import time

from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend import hunting as bknd_hunting
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.quadrants import EwQuadrant
from ew.static import cfg as ewcfg
from ew.static import hue as hue_static
from ew.static import poi as poi_static
from ew.static import slimeoid as sl_static
from ew.utils import casino as casino_utils
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as item_utils
from ew.utils import slimeoid as slimeoid_utils
from ew.utils import combat as cmbt_utils
from ew.utils.combat import EwUser
from ew.utils.combat import EwEnemy
from ew.utils.district import EwDistrict
from ew.utils.slimeoid import EwSlimeoid
from .slimeoidutils import battle_slimeoids
from .slimeoidutils import can_slimeoid_battle
from .slimeoidutils import get_slimeoid_count


# Destroy a slimeoid
async def dissolveslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid = EwSlimeoid(member=cmd.message.author)
    # roles_map_user = ewutils.getRoleMap(message.author.roles)

    if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
        response = "You must go to the SlimeCorp Laboratories in Brawlden to create a Slimeoid."

    elif user_data.life_state == ewcfg.life_state_corpse:
        response = "Ghosts cannot interact with the SlimeCorp Lab apparati."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You have no slimeoid to dissolve."

    elif ewutils.active_slimeoidbattles.get(slimeoid.id_slimeoid):
        response = "You can't do that right now."

    else:

        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        if district_data.is_degraded():
            response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            
        else:
            if slimeoid.life_state != ewcfg.slimeoid_state_forming:
                brain = sl_static.brain_map.get(slimeoid.ai)
                response = brain.str_dissolve.format(
                    slimeoid_name=slimeoid.name
                )
                response += "{}".format(ewcfg.emote_slimeskull)
            else:
                response = "You hit a large red button with a white X on it. Immediately a buzzer goes off and the half-formed body of what would have been your new Slimeoid is flushed out of the gestation tank and down a drainage tube, along with your poudrin and slime. What a waste."                

            cosmetics = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            # get the cosmetics worn by the slimeoid
            for item in cosmetics:
                cos = EwItem(id_item=item.get('id_item'))
                if cos.item_props.get('slimeoid') == 'true':
                    cos.item_props['slimeoid'] = 'false'
                    cos.persist()

            bknd_core.execute_sql_query(
                "DELETE FROM slimeoids WHERE {id_user} = %s AND {id_server} = %s".format(
                    id_user=ewcfg.col_id_user,
                    id_server=ewcfg.col_id_server,
                ), (
                    slimeoid.id_user,
                    slimeoid.id_server,
                ))

        user_data.active_slimeoid = -1
        user_data.persist()

    # Send the response to the player.

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# Show a player's slimeoid data.
async def slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    member = None
    selfcheck = True
    response = ""

    if cmd.mentions_count == 0:
        selfcheck = True
        slimeoid = EwSlimeoid(member=cmd.message.author)
    else:
        selfcheck = False
        member = cmd.mentions[0]
        user_data = EwUser(member=member)
        slimeoid = EwSlimeoid(member=member)

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        if selfcheck == True:
            response = "You have not yet created a slimeoid."
        else:
            response = "{} has not yet created a slimeoid.".format(member.display_name)

    else:
        if slimeoid.life_state == ewcfg.slimeoid_state_forming:
            if selfcheck == True:
                response = "Your Slimeoid is still forming in the gestation vat. It is about {} feet from end to end.".format(str(slimeoid.level))
            else:
                response = "{}'s Slimeoid is still forming in the gestation vat. It is about {} feet from end to end.".format(member.display_name, str(slimeoid.level))
        elif slimeoid.life_state == ewcfg.slimeoid_state_active:
            if selfcheck == True:
                response = "You are accompanied by {}, a {}-foot-tall Slimeoid.".format(slimeoid.name, str(slimeoid.level))
            else:
                response = "{} is accompanied by {}, a {}-foot-tall Slimeoid.".format(member.display_name, slimeoid.name, str(slimeoid.level))

        response += slimeoid_utils.slimeoid_describe(slimeoid)

        cosmetics = bknd_item.inventory(
            id_user=user_data.id_user,
            id_server=cmd.guild.id,
            item_type_filter=ewcfg.it_cosmetic
        )

        # get the cosmetics worn by the slimeoid
        adorned_cosmetics = []
        for item in cosmetics:
            cos = EwItem(id_item=item.get('id_item'))
            if cos.item_props.get('slimeoid') == 'true':
                hue = hue_static.hue_map.get(cos.item_props.get('hue'))
                adorned_cosmetics.append((hue.str_name + " colored " if hue != None else "") + cos.item_props.get('cosmetic_name'))

        if len(adorned_cosmetics) > 0:
            response += "\n\nIt has {} adorned.".format(ewutils.formatNiceList(adorned_cosmetics, "and"))

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# play with your slimeoid
async def playfetch(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif user_data.has_soul == 0:
        response = "You reel back to throw the stick, but your motivation wears thin halfway through. You drop it on the ground with a sigh."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to play fetch with."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} is too beat up from its last battle to play fetch right now.".format(slimeoid.name)

    else:
        head = sl_static.head_map.get(slimeoid.head)
        response = head.str_fetch.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def petslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())
    target = None
    target_data = None
    list_ids = None

    # mentions[0]
    if cmd.mentions_count > 0:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)

        list_ids = []

        for quadrant in ewcfg.quadrant_ids:
            quadrant_data = EwQuadrant(id_server=cmd.guild.id, id_user=cmd.message.author.id, quadrant=quadrant)
            if quadrant_data.id_target != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target)
            if quadrant_data.id_target2 != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target2)

        if target_data.poi != user_data.poi:
            response = "You can't pet them because they aren't here."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.id_user not in list_ids:
            response = "You try to pet {}'s slimeoid, but you're not close enough for them to trust you. Better whip out those quadrants...".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.life_state == ewcfg.life_state_corpse:
            response = "Slimeoids don't fuck with ghosts.".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            slimeoid = EwSlimeoid(member=target)

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif cmd.mentions_count > 1:
        response = "Getting a bit too touchy-feely with these slimeoids, eh? You can only pet one at a time."

    elif user_data.has_soul == 0:
        response = "The idea doesn't even occur to you because your soul is missing."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to pet."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} whimpers. It's still recovering from being beaten up.".format(slimeoid.name)

    else:

        armor = sl_static.defense_map.get(slimeoid.armor)
        response = armor.str_pet.format(
            slimeoid_name=slimeoid.name
        )
        response += " "
        brain = sl_static.brain_map.get(slimeoid.ai)
        response += brain.str_pet.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def abuseslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())
    target = None
    target_data = None
    list_ids = None

    # mentions[0]
    if cmd.mentions_count > 0:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)

        list_ids = []

        for quadrant in ewcfg.quadrant_ids:
            quadrant_data = EwQuadrant(id_server=cmd.guild.id, id_user=cmd.message.author.id, quadrant=quadrant)
            if quadrant_data.id_target != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target)
            if quadrant_data.id_target2 != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target2)

        if target_data.poi != user_data.poi:
            response = "You can't beat them up them because they aren't here."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.id_user not in list_ids:
            response = "You try to lynch {}'s slimeoid, but you're not close enough for them to trust you. Better whip out those quadrants...".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.life_state == ewcfg.life_state_corpse:
            response = "Slimeoids don't fuck with ghosts.".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            slimeoid = EwSlimeoid(member=target)

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif cmd.mentions_count > 1:
        response = "Control your anger! Everybody knows it's more efficient to inflict trauma on one slimeoid at a time."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to hurt."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    # elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
    #		response = "{} whimpers. It's still recovering from being beaten up.".format(slimeoid.name)

    else:

        armor = sl_static.defense_map.get(slimeoid.armor)
        response = armor.str_abuse.format(
            slimeoid_name=slimeoid.name
        )
        response += " "
        brain = sl_static.brain_map.get(slimeoid.ai)
        response += brain.str_abuse.format(
            slimeoid_name=slimeoid.name
        )
        slimeoid.time_defeated = time_now
        slimeoid.persist()
    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def walkslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif user_data.has_soul == 0:
        response = "Why take it on a walk? It's not like it understands your needs."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to take for a walk."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} can barely move. It's still recovering from its injuries.".format(slimeoid.name)

    else:
        brain = sl_static.brain_map.get(slimeoid.ai)
        response = brain.str_walk.format(
            slimeoid_name=slimeoid.name
        )
        poi = poi_static.id_to_poi.get(user_data.poi)
        response += " With that done, you go for a leisurely stroll around {}, while ".format(poi.str_name)
        legs = sl_static.mobility_map.get(slimeoid.legs)
        response += legs.str_walk.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def observeslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to observe."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} lies totally inert, recuperating from being recently pulverized.".format(slimeoid.name)

    else:
        options = [
            'body',
            'weapon',
            'special',
            'brain',
        ]

        roll = random.randrange(len(options))
        result = options[roll]

        if result == 'body':
            part = sl_static.body_map.get(slimeoid.body)

        if result == 'weapon':
            part = sl_static.offense_map.get(slimeoid.weapon)

        if result == 'special':
            part = sl_static.special_map.get(slimeoid.special)

        if result == 'brain':
            part = sl_static.brain_map.get(slimeoid.ai)

        response = part.str_observe.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def slimeoidbattle(cmd):
    # if cmd.message.channel.name != ewcfg.channel_arena:
    # Only at the arena
    #	response = "You can only have Slimeoid Battles at the Battle Arena."
    #	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    pvp_battle = False
    response = ""
    user_name = "" # get it, like a username!
    target_name = ""

    if ewutils.channel_name_is_poi(str(cmd.message.channel)) is False:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

    if cmd.mentions_count > 1:
        response = "Slow down there, bucko! You can only challenge one person to a slimeoid battle at a time."
        return await fe_utils.send_response(response, cmd)
    elif cmd.mentions_count == 1:
        pvp_battle = True
    
    author = cmd.message.author
    user_name = author.display_name
    challenger = EwUser(member=author)
    challenger_slimeoid = EwSlimeoid(member=author)
    
    if pvp_battle:
        member = cmd.mentions[0]
        target_name = member.display_name

        if author.id == member.id:
            response = "You can't challenge yourself, dumbass."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

        challengee = EwUser(member=member)
        challengee_slimeoid = EwSlimeoid(member=member)

        bet = ewutils.getIntToken(tokens=cmd.tokens, allow_all=True)

        if bet == None or challenger.poi != ewcfg.poi_id_arena:
            bet = 0
        
        if bet == -1:
            bet = challenger.slimes
    else:
        
        # Try to find an enemy by the name / indicator given
        targetenemy = " ".join(cmd.tokens[1:]).lower()
        challengee = cmbt_utils.find_enemy(targetenemy, challenger)
        
        if challengee is None:
            response = "Huh? Who do you want to challenge?"
            return await fe_utils.send_response(response, cmd)
        
        target_name = challengee.display_name
        challengee_slimeoid = EwSlimeoid(id_user=challengee.id_enemy, id_server=cmd.message.guild.id)
        
        bet = 0

    # Check if you can throw down
    response = can_slimeoid_battle(challenger, challengee, challenger_slimeoid, challengee_slimeoid, bet)
    if response != "":
        return await fe_utils.send_response(response, cmd)

    # Assign a challenger so partipants can't be challenged again
    challenger_slimeoid_id = challenger_slimeoid.id_slimeoid
    challengee_slimeoid_id = challengee_slimeoid.id_slimeoid
    ewutils.active_slimeoidbattles[challenger_slimeoid_id] = True
    ewutils.active_slimeoidbattles[challengee_slimeoid_id] = True

    if pvp_battle:
        ewutils.active_target_map[challengee.id_user] = challenger.id_user
        response = "You have been challenged by {} to a Slimeoid Battle. Do you !accept or !refuse?".format(user_name).replace("@", "\{at\}")
        await fe_utils.send_response(response, cmd)

        # Wait for an answer
        accepted = 0
        try:
            msg = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == member and message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

            if msg != None:
                if msg.content == ewcfg.cmd_accept:
                    accepted = 1
        except:
            accepted = 0

        # Load information again in case it changed while we were awaiting the challenge
        challengee = EwUser(member=member)
        challengee_slimeoid = EwSlimeoid(member=member)
        challenger = EwUser(member=author)
        challengee_slimeoid = EwSlimeoid(member=member)

        ewutils.active_target_map[challengee.id_user] = ""
        ewutils.active_target_map[challenger.id_user] = ""

        # Double check to make sure nothing has happened in the mean time

        if challenger_slimeoid.life_state != ewcfg.slimeoid_state_active:
            ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
            ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False
            response = "You do not have a Slimeoid ready to battle with!"
            return await fe_utils.send_response(response, cmd)

        if challengee_slimeoid.life_state != ewcfg.slimeoid_state_active:
            ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
            ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False
            response = "{} does not have a Slimeoid ready to battle with!".format(target_name)
            return await fe_utils.send_response(response, cmd)
    else:
        accepted = 1

    # Start game
    if accepted == 1:
        # Don't change slimes unless we realllllyyyyyy have to
        # Winnings needs to be established in order for this to work.
        winnings = 0
        if bet != 0:
            challengee.change_slimes(n=-bet, source=ewcfg.source_slimeoid_betting)
            challenger.change_slimes(n=-bet, source=ewcfg.source_slimeoid_betting)

            challengee.persist()
            challenger.persist()

            winnings = bet * 2

        if not pvp_battle:
            winnings = 1000000 * challengee_slimeoid.level

        # The actual battle goes here
        result = await battle_slimeoids(
            id_s1=challengee_slimeoid.id_slimeoid,
            id_s2=challenger_slimeoid.id_slimeoid,
            channel=cmd.message.channel,
            battle_type=ewcfg.battle_type_arena,
            challengee_name=target_name,
            challenger_name=user_name
        )

        # Challenger won
        if result ==  1:
            winner = challenger
            winner_slimeoid_name = challenger_slimeoid.name
            winner_trainer_name = user_name
        else:
            winner = challengee
            winner_slimeoid_name = challengee_slimeoid.name
            winner_trainer_name = target_name

        response = "\n**{slimeoid_name} has won the Slimeoid battle!! The crowd erupts into cheers for {slimeoid_name} and {trainer_name}!!** :tada:".format(
            slimeoid_name = winner_slimeoid_name,
            trainer_name = winner_trainer_name
            )
        if winnings != 0 and isinstance(winner, EwUser):
            if pvp_battle:
                response += "\nThey recieve {:,} slime!".format(winnings)
            if not pvp_battle:
                response += "\nThey recieve {:,} slimecoin!".format(winnings)

        if challengee_slimeoid.coating != '' and pvp_battle:
            response += "\n{} coating has been tarnished by battle.".format(challengee_slimeoid.name, challengee_slimeoid.coating)
            challengee_slimeoid.coating = ''
            challengee_slimeoid.persist()
        
        if challenger_slimeoid.coating != '':
            response += "\n{} coating has been tarnished by battle.".format(challenger_slimeoid.name, challenger_slimeoid.coating)
            challenger_slimeoid.coating = ''
            challenger_slimeoid.persist()
        
        await fe_utils.send_message(cmd.client, cmd.message.channel, response)

        # Putting this here because something broke, and... idk!!!! Geez!!!!
        ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
        ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False

        if pvp_battle or not isinstance(winner, EwEnemy):
            # Update the winner's state one last time, then give 'em their winnings!
            challenger = EwUser(member=author)
            if winner.life_state != ewcfg.life_state_corpse and pvp_battle:
                winner.change_slimes(n=winnings)
                winner.persist()
            if winner.life_state != ewcfg.life_state_corpse and not pvp_battle:
                challenger.change_slimecoin(n=winnings, coinsource=ewcfg.coinsource_bounty)
                challenger.persist()

        
        if not pvp_battle and not isinstance(winner, EwEnemy):
            # Fucking delete 'em if they lose!
            response = "{name} is out of useable Slimeoids! {name} blacked out!".format(name=challengee.display_name)
            await fe_utils.send_message(cmd.client, cmd.message.channel, response)
            
            bknd_hunting.delete_enemy(challengee)
            challengee_slimeoid.delete()
    else:
        response = "{} was too cowardly to accept your challenge.".format(member.display_name).replace("@", "\{at\}")

        # Send the response to the player.
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
    ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False


async def saturateslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "Wow, great idea! Too bad you don’t even have a slimeoid with which to saturate! You’d think you’d remember really obvious stuff like that, but no. What a dumbass."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif item_sought:
        value = item_search
        hue = hue_static.hue_map.get(value)

        if hue != None:
            if hue.id_hue in [ewcfg.hue_id_copper, ewcfg.hue_id_chrome, ewcfg.hue_id_gold]:
                response = "You saturate your {} with the {} paint! {}".format(slimeoid.name, hue.str_name, hue.str_saturate)
                slimeoid.hue = hue.id_hue
                slimeoid.coating = hue.id_hue
                slimeoid.persist()

                paint_bucket_item = EwItem(id_item=item_sought.get('id_item'))
                if int(paint_bucket_item.item_props.get('durability')) <= 1:
                    bknd_item.item_delete(id_item=item_sought.get('id_item'))
                    response += "\nThe paint bucket is consumed in the process."
                else:
                    await item_utils.lower_durability(item_sought)
                user_data.persist()
            else:
                response = "You saturate your {} with the {} dye! {}".format(slimeoid.name, hue.str_name, hue.str_saturate)
                slimeoid.hue = hue.id_hue
                slimeoid.persist()

                bknd_item.item_delete(id_item=item_sought.get('id_item'))
                user_data.persist()

        else:
            response = "You can only saturate your slimeoid with dyes and paints."

    else:
        if item_search:  # if they didn't forget to specify an item and it just wasn't found
            response = "You can only saturate your slimeoid with dyes and paints."
        else:
            response = "Saturate your slimeoid with what, exactly? (check **!inventory**)"

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def restoreslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state == ewcfg.life_state_shambler:
        response = "You lack the higher brain functions required to {}.".format(cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid = EwSlimeoid(member=cmd.message.author)
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)

    if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
        response = "You must go to the SlimeCorp Laboratories in Brawlden to restore a Slimeoid."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

    if district_data.is_degraded():
        response = "{} has been degraded by shamblers. You can't {} here anymore.".format(poi.str_name, cmd.tokens[0])
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Ghosts cannot interact with the SlimeCorp Lab apparati."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if slimeoid.life_state != ewcfg.slimeoid_state_none:
        response = "You already have an active slimeoid."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if item_sought is None:
        if item_search:
            response = "You need a slimeoid's heart to restore it to life."
        else:
            response = "Restore which slimeoid?"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    item_data = EwItem(id_item=item_sought.get('id_item'))

    if item_data.item_props.get('context') != ewcfg.context_slimeoidheart:
        response = "You need a slimeoid's heart to restore it to life."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid = EwSlimeoid(id_slimeoid=item_data.item_props.get('subcontext'))
    slimes_to_restore = 2 * 10 ** (slimeoid.level - 2)  # 1/5 of the original cost

    if user_data.slimes < slimes_to_restore:
        response = "You need at least {} slime to restore this slimeoid.".format(slimes_to_restore)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid.life_state = ewcfg.slimeoid_state_active
    slimeoid.id_user = str(user_data.id_user)
    slimeoid.persist()

    bknd_item.item_delete(id_item=item_data.id_item)

    user_data.change_slimes(n=-slimes_to_restore, source=ewcfg.source_spending)
    user_data.persist()

    response = "You insert the heart of your beloved {} into one of the restoration tanks. A series of clattering sensors analyze the crystalline core. Then, just like when it was first incubated, the needle pricks you and extracts slime from your body, which coalesces around the poudrin-like heart. Bit by bit the formless mass starts to assume a familiar shape.\n\n{} has been restored to its former glory!".format(
        slimeoid.name, slimeoid.name)
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def bottleslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to bottle."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif ewutils.active_slimeoidbattles.get(slimeoid.id_slimeoid):
        response = "You can't do that right now."

    else:
        items = bknd_item.inventory(id_user=user_data.id_user, id_server=user_data.id_server, item_type_filter=ewcfg.it_item)

        bottles = []
        for item in items:
            item_data = EwItem(id_item=item.get('id_item'))
            if item_data.item_props.get('context') == ewcfg.context_slimeoidbottle:
                bottles.append(item_data)

        if len(bottles) >= 2:
            response = "You can't carry any more slimeoid bottles."

        else:
            slimeoid.life_state = ewcfg.slimeoid_state_stored
            slimeoid.id_user = ""

            user_data.active_slimeoid = -1

            slimeoid.persist()
            user_data.persist()

            item_props = {
                'context': ewcfg.context_slimeoidbottle,
                'subcontext': slimeoid.id_slimeoid,
                'item_name': "Bottle containing {}".format(slimeoid.name),
                'item_desc': "A slimeoid bottle."
            }
            bknd_item.item_create(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type=ewcfg.it_item,
                item_props=item_props
            )

            response = "You shove {} into a random bottle. It's a tight squeeze, but in the end you manage to make it fit.".format(slimeoid.name)

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def unbottleslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.tokens_count < 2:
        response = "Specify which Slimeoid you want to unbottle."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid_search = cmd.message.content[len(cmd.tokens[0]):].lower().strip()

    items = bknd_item.inventory(id_user=user_data.id_user, id_server=user_data.id_server, item_type_filter=ewcfg.it_item)

    bottles = []
    for item in items:
        item_data = EwItem(id_item=item.get('id_item'))
        if item_data.item_props.get('context') == ewcfg.context_slimeoidbottle:
            bottles.append(item_data)

    slimeoid = None
    bottle_data = None
    for bottle in bottles:
        slimeoid_data = EwSlimeoid(id_slimeoid=bottle.item_props.get('subcontext'))
        name = slimeoid_data.name.lower()
        if slimeoid_search in name or bottle.id_item == slimeoid_search:
            slimeoid = slimeoid_data
            bottle_data = bottle
            break

    if slimeoid is None:
        response = "You aren't carrying a bottle containing that Slimeoid."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    active_slimeoid = EwSlimeoid(member=cmd.message.author)

    if active_slimeoid.life_state == ewcfg.slimeoid_state_active:

        if ewutils.active_slimeoidbattles.get(active_slimeoid.id_slimeoid):
            response = "You can't do that right now."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        active_slimeoid.life_state = ewcfg.slimeoid_state_stored
        active_slimeoid.id_user = ""

        user_data.active_slimeoid = -1

        active_slimeoid.persist()
        user_data.persist()

        item_props = {
            'context': ewcfg.context_slimeoidbottle,
            'subcontext': active_slimeoid.id_slimeoid,
            'item_name': "Bottle containing {}".format(active_slimeoid.name),
            'item_desc': "A slimeoid bottle."
        }
        bknd_item.item_create(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type=ewcfg.it_item,
            item_props=item_props
        )
        response += "You shove {} into a random bottle. It's a tight squeeze, but in the end you manage to make it fit.\n\n".format(active_slimeoid.name)

    slimeoid.life_state = ewcfg.slimeoid_state_active
    slimeoid.id_user = str(user_data.id_user)

    slimeoid.persist()

    user_data.active_slimeoid = slimeoid.id_slimeoid
    user_data.persist()

    bknd_item.item_delete(id_item=bottle_data.id_item)

    response += "You crack open a fresh bottle of Slimeoid. After a bit of shaking {} sits beside you again, fully formed.".format(slimeoid.name)
    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def feedslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())
    response = ""

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to feed."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif cmd.tokens_count < 2:
        response = "Specify which item you want to feed to your slimeoid."
    else:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        item_sought = bknd_item.find_item(item_search=item_search, id_user=user_data.id_user, id_server=user_data.id_server)

        if item_sought:
            item_data = EwItem(id_item=item_sought.get('id_item'))
            if item_data.item_type == ewcfg.it_item and item_data.item_props.get('context') == ewcfg.context_slimeoidfood:
                feed_success = slimeoid.eat(item_data)
                if feed_success:
                    slimeoid.persist()
                    bknd_item.item_delete(id_item=item_data.id_item)
                    response = "{slimeoid_name} eats the {food_name}."
                    slimeoid_brain = sl_static.brain_map.get(slimeoid.ai)
                    slimeoid_head = sl_static.head_map.get(slimeoid.head)
                    if slimeoid_brain != None and slimeoid_head != None:
                        response = "{} {}".format(slimeoid_brain.str_feed, slimeoid_head.str_feed)
                else:
                    response = "{slimeoid_name} refuses to eat the {food_name}."

                response = response.format(slimeoid_name=slimeoid.name, food_name=item_sought.get('name'))
            else:
                response = "That item is not suitable for slimeoid consumption."

        else:
            response = "You don't have an item like that."

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def dress_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    market_data = EwMarket(id_server=user_data.id_server)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You'll have to create a Slimeoid if you want to play dress up."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif slimeoid.life_state != ewcfg.slimeoid_state_active:
        response = "You don't have a Slimeoid with you."

    else:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_search)
        except:
            item_id_int = None

        if item_search != None and len(item_search) > 0:

            cosmetics = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            item_sought = None
            already_adorned = False
            item_from_user = None
            for item in cosmetics:
                if item.get('id_item') == item_id_int or item_search in ewutils.flattenTokenListToString(item.get('name')):
                    cos = EwItem(item.get('id_item'))
                    if item_from_user == None and cos.item_props.get('adorned') == 'true':
                        item_from_user = cos
                        continue

                    if cos.item_props.get('slimeoid') == 'true':
                        already_adorned = True
                    elif cos.item_props.get("context") == 'costume':
                        if not ewutils.check_fursuit_active(market_data):
                            response = "You can't dress your slimeoid with your costume right now."
                            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        else:
                            item_sought = cos
                            break
                    else:
                        item_sought = cos
                        break

            if item_sought == None:
                item_sought = item_from_user

            if item_sought != None:
                # get the cosmetics worn by the slimeoid
                adorned_cosmetics = []
                for item in cosmetics:
                    cos = EwItem(id_item=item.get('id_item'))
                    if cos.item_props.get('slimeoid') == 'true':
                        adorned_cosmetics.append(cos)

                if len(adorned_cosmetics) < slimeoid.level:
                    # Remove hat from player if adorned
                    if item_sought.item_props.get('adorned') == 'true':
                        item_sought.item_props['adorned'] = 'false'

                        response = "You take off your {} and give it to {}.".format(item_sought.item_props.get('cosmetic_name'), slimeoid.name)
                    else:
                        response = "You give {} a {}.".format(slimeoid.name, item_sought.item_props.get('cosmetic_name'))

                    item_sought.item_props['slimeoid'] = 'true'
                    item_sought.persist()
                    user_data.persist()
                else:
                    response = 'Your slimeoid is too small to wear any more clothes.'
            elif already_adorned:
                response = "Your slimeoid is already wearing it."
            else:
                response = 'You don\'t have one.'
        else:
            response = 'Adorn which cosmetic? Check your **!inventory**.'

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def undress_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You'll have to create a Slimeoid if you want to play dress up."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif slimeoid.life_state != ewcfg.slimeoid_state_active:
        response = "You don't have a Slimeoid with you."

    elif ewutils.active_slimeoidbattles.get(slimeoid.id_slimeoid):
        response = "You can't do that right now."

    else:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_search)
        except:
            item_id_int = None

        if item_search != None and len(item_search) > 0:

            cosmetics = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            item_sought = None
            for item in cosmetics:
                if item.get('id_item') == item_id_int or item_search in ewutils.flattenTokenListToString(item.get('name')):
                    cos = EwItem(item.get('id_item'))
                    if cos.item_props.get('slimeoid') == 'true':
                        item_sought = cos
                        break

            if item_sought != None:

                response = "You take the {} back from {}".format(item_sought.item_props.get('cosmetic_name'), slimeoid.name)
                item_sought.item_props['slimeoid'] = 'false'

                item_sought.persist()
            else:
                response = 'You don\'t have one.'
        else:
            response = 'Dedorn which cosmetic? Check your **!inventory**.'

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# Check if a negaslimoid exists and describe it
async def negaslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""

    if cmd.mentions_count > 0:
        # Can't mention any players
        response = "Negaslimeoids obey no masters. You'll have to address the beast directly."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    if cmd.tokens_count < 2:
        response = "Name the horror you wish to behold."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid_search = cmd.message.content[len(cmd.tokens[0]):].lower().strip()

    potential_slimeoids = ewutils.get_slimeoids_in_poi(id_server=cmd.guild.id, sltype=ewcfg.sltype_nega)

    negaslimeoid = None
    for id_slimeoid in potential_slimeoids:

        slimeoid_data = EwSlimeoid(id_slimeoid=id_slimeoid)
        name = slimeoid_data.name.lower()
        if slimeoid_search in name:
            negaslimeoid = slimeoid_data
            break

    if negaslimeoid is None:
        response = "There is no Negaslimeoid by that name."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    response = "{} is a {}-foot-tall Negaslimeoid.".format(negaslimeoid.name, negaslimeoid.level)
    response += slimeoid_utils.slimeoid_describe(negaslimeoid)

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def negaslimeoidbattle(cmd):
    if not ewutils.channel_name_is_poi(cmd.message.channel.name):
        response = "You must go into the city to challenge an eldritch abomination."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.mentions_count > 0:
        # Can't mention any players
        response = "Negaslimeoids obey no masters. You'll have to address the beast directly."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.tokens_count < 2:
        response = "Name the horror you wish to face."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid_search = cmd.message.content[len(cmd.tokens[0]):].lower().strip()

    author = cmd.message.author

    challenger = EwUser(member=author)
    challenger_slimeoid = EwSlimeoid(member=author)

    # Player has to be alive
    if challenger.life_state == ewcfg.life_state_corpse:
        response = "Your Slimeoid won't battle for you while you're dead.".format(author.display_name).replace("@", "\{at\}")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    potential_challengees = ewutils.get_slimeoids_in_poi(id_server=cmd.guild.id, poi=challenger.poi, sltype=ewcfg.sltype_nega)

    challengee_slimeoid = None
    for id_slimeoid in potential_challengees:

        slimeoid_data = EwSlimeoid(id_slimeoid=id_slimeoid)
        name = slimeoid_data.name.lower()
        if slimeoid_search in name:
            challengee_slimeoid = slimeoid_data
            break

    if challengee_slimeoid is None:
        response = "There is no Negaslimeoid by that name here."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # Players have been challenged
    if ewutils.active_slimeoidbattles.get(challenger_slimeoid.id_slimeoid):
        response = "Your slimeoid is already in the middle of a battle."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    if ewutils.active_slimeoidbattles.get(challengee_slimeoid.id_slimeoid):
        response = "{} is already in the middle of a battle.".format(challengee_slimeoid.name)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    if challenger_slimeoid.life_state != ewcfg.slimeoid_state_active:
        response = "You do not have a Slimeoid ready to battle with!"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    time_now = int(time.time())

    if (time_now - challenger_slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "Your Slimeoid is still recovering from its last defeat!"
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    # Assign a challenger so players can't be challenged
    ewutils.active_slimeoidbattles[challenger_slimeoid.id_slimeoid] = True
    ewutils.active_slimeoidbattles[challengee_slimeoid.id_slimeoid] = True

    # Start game
    try:
        result = await battle_slimeoids(id_s1=challengee_slimeoid.id_slimeoid, id_s2=challenger_slimeoid.id_slimeoid, channel=cmd.message.channel, battle_type=ewcfg.battle_type_nega, challengee_name="null", challenger_name=author.display_name)
        if result == 1:
            # Losing in a nega battle means death
            district_data = EwDistrict(district=challenger.poi, id_server=cmd.guild.id)
            slimes = min(int(2 * 10 ** (challengee_slimeoid.level - 2)), 1000000)
            district_data.change_slimes(n=slimes)
            district_data.persist()
            challengee_slimeoid.delete()
            response = "The dulled colors become vibrant again, as {} fades back into its own reality.".format(challengee_slimeoid.name)
            await fe_utils.send_message(cmd.client, cmd.message.channel, response)
        elif result == -1:
            # Dedorn all items
            cosmetics = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )
            # get the cosmetics worn by the slimeoid
            for item in cosmetics:
                cos = EwItem(id_item=item.get('id_item'))
                if cos.item_props.get('slimeoid') == 'true':
                    cos.item_props['slimeoid'] = 'false'
                    cos.persist()
            # Losing in a nega battle means death
            item_props = {
                'context': ewcfg.context_slimeoidheart,
                'subcontext': challenger_slimeoid.id_slimeoid,
                'item_name': "Heart of {}".format(challenger_slimeoid.name),
                'item_desc': "A poudrin-like crystal. If you listen carefully you can hear something that sounds like a faint heartbeat."
            }
            bknd_item.item_create(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type=ewcfg.it_item,
                item_props=item_props
            )
            challenger_slimeoid.die()
            challenger_slimeoid.persist()
            challenger = EwUser(member=author)
            challenger.active_slimeoid = -1
            challenger.persist()
            response = "{} feasts on {}'s slime. All that remains is a small chunk of crystallized slime.".format(challengee_slimeoid.name, challenger_slimeoid.name)
            response += "\n\n{} is no more. {}".format(challenger_slimeoid.name, ewcfg.emote_slimeskull)
            if challenger_slimeoid.level > challengee_slimeoid.level:
                challengee_slimeoid.level += 1
                rand = random.randrange(3)
                if rand == 0:
                    challengee_slimeoid.atk += 1
                elif rand == 1:
                    challengee_slimeoid.defense += 1
                else:
                    challengee_slimeoid.intel += 1
                challengee_slimeoid.persist()
                response += "\n\n{} was empowered by the slaughter and grew a foot taller.".format(challengee_slimeoid.name)
            await fe_utils.send_message(cmd.client, cmd.message.channel, response)
    except:
        ewutils.logMsg("An error occured in the Negaslimeoid battle against {}".format(challengee_slimeoid.name))
    finally:
        ewutils.active_slimeoidbattles[challenger_slimeoid.id_slimeoid] = False
        ewutils.active_slimeoidbattles[challengee_slimeoid.id_slimeoid] = False


async def summon_negaslimeoid(cmd):
    response = ""
    user_data = EwUser(member=cmd.message.author)
    if user_data.life_state != ewcfg.life_state_corpse:
        response = "Only the dead have the occult knowledge required to summon a cosmic horror."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if user_data.poi not in poi_static.capturable_districts:
        response = "You can't conduct the ritual here."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    name = None
    if cmd.tokens_count > 1:
        # value = ewutils.getIntToken(tokens = cmd.tokens, allow_all = True, negate = True)
        slimeoid = EwSlimeoid(member=cmd.message.author, sltype=ewcfg.sltype_nega)
        if slimeoid.life_state != ewcfg.slimeoid_state_none:
            response = "You already have an active negaslimeoid."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        negaslimeoid_name = cmd.message.content[(len(cmd.tokens[0])):].strip()

        if len(negaslimeoid_name) > 32:
            response = "That name is too long. ({:,}/32)".format(len(negaslimeoid_name))
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        market_data = EwMarket(id_server=cmd.message.author.guild.id)

        if market_data.negaslime >= 0:
            response = "The dead haven't amassed any negaslime yet."
        else:
            max_level = min(len(str(user_data.slimes)) - 1, len(str(market_data.negaslime)) - 1)
            level = random.randint(1, max_level)
            value = 10 ** (level - 1)
            # user_data.change_slimes(n = int(value/10))
            market_data.negaslime += value
            slimeoid.sltype = ewcfg.sltype_nega
            slimeoid.life_state = ewcfg.slimeoid_state_active
            slimeoid.level = level
            slimeoid.id_user = str(user_data.id_user)
            slimeoid.id_server = user_data.id_server
            slimeoid.poi = user_data.poi
            slimeoid.name = negaslimeoid_name
            slimeoid.body = random.choice(sl_static.body_names)
            slimeoid.head = random.choice(sl_static.head_names)
            slimeoid.legs = random.choice(sl_static.mobility_names)
            slimeoid.armor = random.choice(sl_static.defense_names)
            slimeoid.weapon = random.choice(sl_static.offense_names)
            slimeoid.special = random.choice(sl_static.special_names)
            slimeoid.ai = random.choice(sl_static.brain_names)
            for i in range(level):
                rand = random.randrange(3)
                if rand == 0:
                    slimeoid.atk += 1
                elif rand == 1:
                    slimeoid.defense += 1
                else:
                    slimeoid.intel += 1

            user_data.persist()
            slimeoid.persist()
            market_data.persist()

            response = "You have summoned **{}**, a {}-foot-tall Negaslimeoid.".format(slimeoid.name, slimeoid.level)
            desc = slimeoid_utils.slimeoid_describe(slimeoid)
            response += desc

    else:
        response = "To summon a negaslimeoid you must first know its name."
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
