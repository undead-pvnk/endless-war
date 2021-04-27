async def quarterlyreport(cmd):
    progress = 0
    completion = False
    q5state = EwGamestate(id_server=cmd.guild.id, id_state='qreport5')
    if q5state.bit == False:
        objective = 30
        goal = "DISTRICTS GENTRIFIED"
        completion = False

        districts = []
        for poi in ewcfg.poi_list:
            if poi.is_district and poi.is_capturable == True:
                districts.append(poi)

        for district in districts:
            dist_obj = EwDistrict(id_server=cmd.guild.id, district=district.id_poi)
            if dist_obj.capture_points >= ewcfg.limit_influence[
                dist_obj.property_class] and dist_obj.cap_side == 'slimecorp':
                progress += 1
        """try:
            conn_info = ewutils.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            # Display the progress towards the current Quarterly Goal, whatever that may be.
            cursor.execute("SELECT {metric} FROM markets WHERE id_server = %s".format(
                metric = ewcfg.col_splattered_slimes
            ), (cmd.guild.id, ))

            result = cursor.fetchone();

            if result != None:
                progress = result[0]

                if progress == None:
                    progress = 0

                if progress >= objective:
                    progress = objective
                    completion = True

        finally:
            cursor.close()
            ewutils.databaseClose(conn_info)"""
        if progress >= 30:
            completion = True
        response = "{:,} / {:,} {}.".format(progress, objective, goal)
        if completion == True:
            response += " THE QUARTERLY GOAL HAS BEEN REACHED. PLEASE STAY TUNED FOR FURTHER ANNOUNCEMENTS."
    else:
        goal1 = 'SLIME DONATED'
        objective1 = 1000000000
        progress1 = 0
        goal2 = 'SLIMECOIN DONATED'
        objective2 = 1000000000000000000
        progress2 = 0
        goal3 = 'POUDRINS DONATED'
        progress3 = 0
        objective3 = 3000
        shermanslime = EwGamestate(id_server=cmd.guild.id, id_state='shermanslime')
        shermancoin = EwGamestate(id_server=cmd.guild.id, id_state='shermancoin')
        shermanpoud = EwGamestate(id_server=cmd.guild.id, id_state='shermanpoud')
        progress1 = int(shermanslime.value)
        progress2 = int(shermancoin.value)
        progress3 = int(shermanpoud.value)
        response = "\n5TH QUARTERLY GOAL:\n{:,} / {:,} {}.".format(progress1, objective1, goal1)
        response += "\n\n{:,} / {:,} {}.".format(progress2, objective2, goal2)
        response += "\n\n{:,} / {:,} {}.".format(progress3, objective3, goal3)

        if progress1 >= objective1 and progress2 >= objective2 and progress3 >= objective3:
            completion = True
        if completion == True:
            response += " THE QUARTERLY GOAL HAS BEEN REACHED. PLEASE STAY TUNED FOR SHERMAN ACTUALLY DOING SOMETHING."

    return await ewutils.send_message(cmd.client, cmd.message.channel,
                                      ewutils.formatMessage(cmd.message.author, response))


async def win(cmd):
    # if cmd.message.channel.name != ewcfg.channel_slimefest:
    #	response = "You have to participate in #{} to win.".format(ewcfg.channel_slimefest)
    #	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

    """user_data = EwUser(member=cmd.message.author)

    response = ''

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "You have no dog in this race. You're not even a real live person."
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_juvenile:
        response = "You're too scared to take Slimecorp down."
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

    if user_data.life_state == ewcfg.life_state_kingpin:
        response = "Slime what?"
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

    #if user_data.slimes < 1:
    #	response = "You don't have enough slime to win Slimefest!"
    #	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

    if user_data.faction == ewcfg.faction_slimecorp:
        response = "You better. N11 won't be so nice anymore if you fuck this up for him."
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

    if user_data.faction in [ewcfg.faction_killers, ewcfg.faction_rowdys]:
        response = "YEEEEEAAAAAAAHHHHHHH!!!! FUCK SHILLS!."
        #user_data.slimes -= 1
        #user_data.persist()
        #market_data = EwMarket(id_server = cmd.guild.id)
        #market_data.winner = user_data.faction
        #market_data.persist()
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

        """

    async def n1_die(cmd):
        user_data = EwUser(member=cmd.message.author, data_level=1)
        if ewcfg.status_n1 not in user_data.getStatusEffects():
            return await ewutils.fake_failed_command(cmd)
        else:
            life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive]
            district_data = EwDistrict(district=user_data.poi, id_server=user_data.id_server)
            players = district_data.get_players_in_district(life_states=life_states)

            if len(players) > 1:
                players.remove(user_data.id_user)

                target = random.choice(players)
                return await attack(cmd=cmd, n1_die=target)

def sherman_donate(cmd):
    quarter5slime = ewdebug.EwGamestate(id_server=cmd.guild.id, id_state="shermanslime")
    user_data = EwUser(member=cmd.message.author)
    value = ewutils.getIntToken(tokens=cmd.tokens, allow_all=True)
    emptied = 0
    if quarter5slime.bit == 0:
        response = "You can't donate here. Try it at SlimeCorp HQ!"
        return response
    elif value < 0:
        response = "Sherman needs an exact number. Try to confuse him with words and he'll be sniffing your pockets all day long."
    else:
        if cmd.tokens_count != 3:
            response = "Make sure you're giving Sherman money in the right format. It's !donate <donation type> <amount>."
        elif ewutils.flattenTokenListToString(cmd.tokens[1]) not in ['poudrins', 'slime', 'slimecoin']:
            response = "You need to donate in the form of Slimecoin, poudrins, or slime. Sherman doesn't take credit cards because he doesn't understand them."
        else:
            if ewutils.flattenTokenListToString(cmd.tokens[1]) == "poudrins":
                quarter5pouds = ewdebug.EwGamestate(id_server=cmd.guild.id, id_state="shermanpoud")
                valuecount = 0
                while valuecount <= value or poudrin == None:
                    poudrin = find_item(item_search=ewcfg.item_id_slimepoudrin, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)
                    if poudrin is None:
                        emptied = 1
                        break
                    item_delete(id_item = poudrin.get('id_item'))
                    valuecount += 1
                currentpouds = int(quarter5pouds.value)
                currentpouds += valuecount
                quarter5pouds.value = str(currentpouds)
                quarter5pouds.persist()
                if emptied:
                    response = "Sherman empties your pockets of all your precious poudrins. He tries to juggle them all and fails miserably."
                else:
                    response = "You give Sherman {} poudrins. He joyfully tries to juggle them all and fails miserably.".format(value)


            elif ewutils.flattenTokenListToString(cmd.tokens[1]) == "slime":
                if user_data.slimes < value:
                    response = "You don't have enough slime."
                else:
                    user_data.change_slimes(n = -value, source = ewcfg.source_spending)
                    user_data.persist()
                    currentslime = int(quarter5slime.value)
                    currentslime += value
                    quarter5slime.value = str(currentslime)
                    quarter5slime.persist()
                    response = "You donate {} slime to Sherman. He excitedly throws it up in the air and does a stupid little dance.".format(value)

            elif ewutils.flattenTokenListToString(cmd.tokens[1]) == "slimecoin":
                quarter5coin = ewdebug.EwGamestate(id_server=cmd.guild.id, id_state="shermancoin")
                if user_data.slimecoin < value:
                    response = "You don't have enough slimecoin."

                else:
                    user_data.change_slimecoin(n=-value, coinsource=ewcfg.source_spending)
                    user_data.persist()
                    currentcoin = int(quarter5coin.value)
                    currentcoin += value
                    quarter5coin.value = str(currentcoin)
                    quarter5coin.persist()
                    response = "You whip out Coinbase and transfer {} SlimeCoin into Sherman's account. He laughs giddily and slaps his thighs together.".format(value)

        return response


async def combo(cmd):
    user_data = EwUser(member=cmd.message.author)
    command1 = EwGamestate(id_server=cmd.guild.id, id_state="lobbylock1")
    command2 = EwGamestate(id_server=cmd.guild.id, id_state="lobbylock2")

    combi = ewutils.flattenTokenListToString(cmd.tokens[1:])

    if user_data.poi != "lobbybackroom":
        return await ewutils.fake_failed_command(cmd=cmd)
    elif combi == '571621183412910':
        response = "You enter 5-7-1-6-2-1-1-8-3-4-1-2-9-1-0 into the dial. **c-CHK!** Bingo! You got one of the latches!"
        command1.bit = 1
        command1.persist()
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    elif combi == '384111355':
        response = "You enter 3-8-4-1-1-1-3-5-5. **c-CHK!** Nice, there goes the second latch!"
        command2.bit = 1
        command2.persist()
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
    else:
        response = "BZZZT! Wrong combo, shithead!"
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def elevator_call(cmd):
    user_data = EwUser(member=cmd.message.author)
    if 'office' not in user_data.poi or user_data.poi == 'n12office':
        return await ewutils.fake_failed_command(cmd)
    else:
        gamestate = EwGamestate(id_server=cmd.guild.id, id_state="elevator")
        gamestate.value = user_data.poi
        gamestate.persist()
        response = "You call the elevator down to your floor."
        return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))