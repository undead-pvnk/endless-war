import time
import random
import math

import ewcfg
import ewutils
import ewitem
import ewrolemgr
import ewstats

from ew import EwUser
from ewitem import EwItem
from ewmarket import EwMarket
from ewplayer import EwPlayer
from ewdistrict import EwDistrict
from ewslimeoid import EwSlimeoid

""" Enemy data model for database persistence """


class EwEnemy:
    id_enemy = 0
    id_server = ""

    slimes = 0
    totaldamage = 0
    ai = ""
    display_name = ""
    level = 0
    poi = ""
    life_state = 0
    type = ""
    attacktype = ""
    bleed_storage = 0
    time_lastenter = 0
    initialslimes = 0
    lifetime = 0

    # slimeoid = EwSlimeoid(member = cmd.message.author, )
    # slimeoid = EwSlimeoid(id_slimeoid = 12)

    """ Load the enemy data from the database. """

    def __init__(self, id_enemy=None, id_server=None):
        query_suffix = ""

        if id_enemy != None:
            query_suffix = " WHERE id_enemy = '{}'".format(id_enemy)
        else:

            if id_server != None:
                query_suffix = " WHERE id_server = '{}'".format(id_server)
                if type != None:
                    query_suffix += " AND type = '{}'".format(type)

        if query_suffix != "":
            try:
                conn_info = ewutils.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor();

                # Retrieve object
                cursor.execute(
                    "SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM enemies{}".format(
                        ewcfg.col_id_enemy,
                        ewcfg.col_id_server,
                        ewcfg.col_enemy_slimes,
                        ewcfg.col_enemy_totaldamage,
                        ewcfg.col_enemy_ai,
                        ewcfg.col_enemy_type,
                        ewcfg.col_enemy_attacktype,
                        ewcfg.col_enemy_name,
                        ewcfg.col_enemy_level,
                        ewcfg.col_enemy_poi,
                        ewcfg.col_enemy_life_state,
                        ewcfg.col_enemy_bleed_storage,
                        ewcfg.col_enemy_time_lastenter,
                        ewcfg.col_enemy_initialslimes,
                        ewcfg.col_enemy_lifetime,
                        query_suffix
                    ))
                result = cursor.fetchone();

                if result != None:
                    # Record found: apply the data to this object.
                    self.id_enemy = result[0]
                    self.id_server = result[1]
                    self.slimes = result[2]
                    self.totaldamage = result[3]
                    self.ai = result[4]
                    self.type = result[5]
                    self.attacktype = result[6]
                    self.display_name = result[7]
                    self.level = result[8]
                    self.poi = result[9]
                    self.life_state = result[10]
                    self.bleed_storage = result[11]
                    self.time_lastenter = result[12]
                    self.initialslimes = result[13]
                    self.lifetime = result[14]

            finally:
                # Clean up the database handles.
                cursor.close()
                ewutils.databaseClose(conn_info)

    """ Save enemy data object to the database. """

    def persist(self):
        try:
            conn_info = ewutils.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor();

            # Save the object.
            cursor.execute(
                "REPLACE INTO enemies({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
                    ewcfg.col_id_enemy,
                    ewcfg.col_id_server,
                    ewcfg.col_enemy_slimes,
                    ewcfg.col_enemy_totaldamage,
                    ewcfg.col_enemy_ai,
                    ewcfg.col_enemy_type,
                    ewcfg.col_enemy_attacktype,
                    ewcfg.col_enemy_name,
                    ewcfg.col_enemy_level,
                    ewcfg.col_enemy_poi,
                    ewcfg.col_enemy_life_state,
                    ewcfg.col_enemy_bleed_storage,
                    ewcfg.col_enemy_time_lastenter,
                    ewcfg.col_enemy_initialslimes,
                    ewcfg.col_enemy_lifetime,
                ), (
                    self.id_enemy,
                    self.id_server,
                    self.slimes,
                    self.totaldamage,
                    self.ai,
                    self.type,
                    self.attacktype,
                    self.display_name,
                    self.level,
                    self.poi,
                    self.life_state,
                    self.bleed_storage,
                    self.time_lastenter,
                    self.initialslimes,
                    self.lifetime,
                ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            ewutils.databaseClose(conn_info)

    async def kill(self):

        client = ewutils.get_client()

        enemy_data = self



        time_now = int(time.time())
        resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
        district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)
        market_data = EwMarket(id_server=enemy_data.id_server)
        ch_name = ewcfg.id_to_poi.get(enemy_data.poi).channel
        number_of_players = district_data.get_players_in_district()

        target_data = None
        target_player = None
        target_slimeoid = None
        target_num = 0

        if enemy_data.attacktype != None:
            attacktype = ewcfg.attack_type_map.get(enemy_data.attacktype)

        enemy_data.persist()

        if len(number_of_players) >= 1:

            users = ewutils.execute_sql_query(
                "SELECT {id_user}, {life_state} FROM users WHERE {poi} = %s AND {id_server} = %s".format(
                    id_user=ewcfg.col_id_user,
                    life_state=ewcfg.col_life_state,
                    poi=ewcfg.col_poi,
                    id_server=ewcfg.col_id_server
                ), (
                    enemy_data.poi,
                    enemy_data.id_server
                ))

            # Get target's info based on its AI.

            if enemy_data.ai == "Coward":
                if random.randrange(100) > 95:
                    response = random.choice(ewcfg.coward_responses)
                    response = response.format(enemy_data.display_name, enemy_data.display_name)
                    resp_cont.add_channel_response(ch_name, response)

            elif enemy_data.ai == "Attacker-A":
                # print(len(users))

                while target_num < len(users):
                    # checks if target is alive
                    if users[target_num][1] != 0:
                        target_data = EwUser(id_user=users[target_num][0], id_server=enemy_data.id_server)
                        target_num = len(users)
                    else:
                        target_num += 1
            else:
                print(enemy_data.ai)

        if target_data != None:

            # print('no targets!')
            # target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server)
            target_player = EwPlayer(id_user=target_data.id_user)
            target_slimeoid = EwSlimeoid(id_user=target_data.id_user)

            server = client.get_server(target_data.id_server)
            # server = discord.Server(id=target_data.id_server)
            # print(target_data.id_server)
            # channel = discord.utils.get(server.channels, name=ch_name)

            # print(server)

            # member = discord.utils.get(channel.server.members, name=target_player.display_name)

            # for m in channel.server.members:
            #     if m.id == target_data.id_user:
            #         member = m

            member = server.get_member(target_data.id_user)
            # print(member)

            # for m in members:
            #    if m.id == target_data.id_user:
            #        member = m

            # print(member)
            # member.id = target_data.id_user
            # member.server.id = target_data.id_server

            target_mutations = target_data.get_mutations()

            miss = False
            crit = False
            strikes = 0

            # maybe enemies COULD have weapon skills? could punishes players who die to the same enemy without mining up beforehand
            # slimes_damage = int((slimes_spent * 4) * (100 + (user_data.weaponskill * 10)) / 100.0)

            # since enemies dont use up slime or hunger, this is only used for damage calculation
            slimes_spent = int(ewutils.slime_bylevel(enemy_data.level) / 20)

            slimes_damage = int(slimes_spent * 4)

            if attacktype is 'unarmed':
                slimes_damage /= 2  # specific to juvies
            elif attacktype is 'unarmed' and enemy_data.type == "microslime":
                slimes_damage *= 200  # specific to microslime

            slimes_dropped = target_data.totaldamage + target_data.slimes

            target_iskillers = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_killers
            target_isrowdys = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_rowdys
            target_isslimecorp = target_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
            target_isjuvie = target_data.life_state == ewcfg.life_state_juvenile
            target_isnotdead = target_data.life_state != ewcfg.life_state_corpse

            if target_data.life_state == ewcfg.life_state_kingpin:
                # Disallow killing generals.
                response = "The enemy tries to attack the kingpin, but is taken aback by the sheer girth of their slime."
                resp_cont.add_channel_response(ch_name, response)

            elif (time_now - target_data.time_lastrevive) < ewcfg.invuln_onrevive:
                # User is currently invulnerable.
                response = "The enemy tries to attack {}, but they have died too recently and are immune.".format(
                    target_player.display_name)
                resp_cont.add_channel_response(ch_name, response)

            # enemies dont fuck with ghosts, ghosts dont fuck with enemies.

            elif (target_iskillers or target_isrowdys or target_isjuvie) and (target_isnotdead):
                was_killed = False
                was_hurt = False

                if target_data.life_state in [ewcfg.life_state_enlisted, ewcfg.life_state_juvenile,
                                              ewcfg.life_state_lucky,
                                              ewcfg.life_state_executive]:
                    # Target can be shot.

                    was_hurt = True

                if was_hurt:
                    # Weaponized flavor text.
                    randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]

                    # Attacking-type-specific adjustments
                    if attacktype != None and attacktype.fn_effect != None:
                        # Build effect container
                        ctn = EwEnemyEffectContainer(
                            miss=miss,
                            crit=crit,
                            slimes_damage=slimes_damage,
                            enemy_data=enemy_data,
                            target_data=target_data
                        )

                        # Make adjustments
                        attacktype.fn_effect(ctn)

                        # Apply effects for non-reference values
                        miss = ctn.miss
                        crit = ctn.crit
                        slimes_damage = ctn.slimes_damage
                        strikes = ctn.strikes
                    # enemy_data and target_data should be passed by reference, so there's no need to assign them back from the effect container.

                    # can't hit lucky lucy
                    if target_data.life_state == ewcfg.life_state_lucky:
                        miss = True

                    if miss:
                        slimes_damage = 0

                    enemy_data.persist()
                    target_data = EwUser(member=member)

                    if slimes_damage >= target_data.slimes - target_data.bleed_storage:
                        was_killed = True
                        slimes_damage = max(target_data.slimes - target_data.bleed_storage, 0)

                    sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=enemy_data.id_server)

                    # move around slime as a result of the shot
                    if target_isjuvie:
                        slimes_drained = int(3 * slimes_damage / 4)  # 3/4
                    else:
                        slimes_drained = 0

                    damage = str(slimes_damage)

                    slimes_tobleed = int((slimes_damage - slimes_drained) / 2)
                    if ewcfg.mutation_id_bleedingheart in target_mutations:
                        slimes_tobleed *= 2

                    slimes_directdamage = slimes_damage - slimes_tobleed
                    slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained

                    district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
                    target_data.bleed_storage += slimes_tobleed
                    target_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
                    sewer_data.change_slimes(n=slimes_drained)

                    if was_killed:

                        # Drop all items into district
                        ewitem.item_dropall(id_server=target_data.id_server, id_user=target_data.id_user)

                        # Give a bonus to the player's weapon skill for killing a stronger player.
                        # if target_data.slimelevel >= user_data.slimelevel and weapon is not None:
                        # enemy_data.add_weaponskill(n = 1, weapon_type = weapon.id_weapon)

                        explode_damage = ewutils.slime_bylevel(target_data.slimelevel) / 5
                        # explode, damaging everyone in the district

                        # release bleed storage
                        slimes_todistrict = target_data.slimes

                        district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)

                        # Player was killed.
                        target_data.id_killer = enemy_data.id_enemy
                        target_data.die(cause=ewcfg.cause_killing)
                        target_data.change_slimes(n=-slimes_dropped / 10, source=ewcfg.source_ghostification)

                        kill_descriptor = "beaten to death"
                        if attacktype != None:
                            response = attacktype.str_damage.format(
                                name_enemy=enemy_data.display_name,
                                name_target=member.display_name,
                                hitzone=randombodypart,
                                strikes=strikes
                            )
                            kill_descriptor = attacktype.str_killdescriptor
                            if crit:
                                response += " {}".format(attacktype.str_crit.format(
                                    name_enemy=enemy_data.display_name,
                                    name_target=member.display_name
                                ))

                            response += "\n\n{}".format(attacktype.str_kill.format(
                                name_enemy=enemy_data.display_name,
                                name_target=member.display_name,
                                emote_skull=ewcfg.emote_slimeskull
                            ))
                            target_data.trauma = attacktype.id_type

                        else:
                            response = "{name_target} is hit!!\n\n{name_target} has died.".format(
                                name_target=member.display_name)

                            target_data.trauma = ""

                        if target_slimeoid.life_state == ewcfg.slimeoid_state_active:
                            brain = ewcfg.brain_map.get(target_slimeoid.ai)
                            response += "\n\n" + brain.str_death.format(slimeoid_name=target_slimeoid.name)

                        deathreport = "You were {} by {}. {}".format(kill_descriptor, enemy_data.display_name,
                                                                     ewcfg.emote_slimeskull)
                        deathreport = "{} ".format(ewcfg.emote_slimeskull) + ewutils.formatMessage(member, deathreport)

                        target_data.persist()
                        enemy_data.persist()
                        resp_cont.add_channel_response(ewcfg.channel_sewers, deathreport)
                        resp_cont.add_channel_response(ch_name, response)
                        if ewcfg.mutation_id_spontaneouscombustion in target_mutations:
                            import ewwep
                            explode_resp = "\n{} spontaneously combusts, horribly dying in a fiery explosion of slime and shrapnel!! Oh, the humanity!".format(
                                member.display_name)
                            resp_cont.add_channel_response(ch_name, explode_resp)
                            explosion = ewwep.explode(damage=explode_damage, district_data=district_data)
                            resp_cont.add_response_container(explosion)

                        # don't recreate enemy data if enemy was killed in explosion
                        # print("DELETE GATE 2")

                        if check_death(enemy_data) == False:
                            enemy_data = EwEnemy(id_enemy=self.id_enemy)

                        target_data = EwUser(member=member)
                    else:
                        # A non-lethal blow!

                        if attacktype != 'unarmed':
                            if miss:
                                response = "{}".format(attacktype.str_miss.format(
                                    name_enemy=enemy_data.display_name,
                                    name_target=member.display_name
                                ))
                            else:
                                response = attacktype.str_damage.format(
                                    name_enemy=enemy_data.display_name,
                                    name_target=member.display_name,
                                    hitzone=randombodypart,
                                    strikes=strikes
                                )
                                if crit:
                                    response += " {}".format(attacktype.str_crit.format(
                                        name_enemy=enemy_data.display_name,
                                        name_target=member.display_name
                                    ))
                                response += " {target_name} loses {damage} slime!".format(
                                    target_name=member.display_name,
                                    damage=damage
                                )
                        else:
                            if miss:
                                response = "{target_name} dodges the {enemy_name}'s strike.".format(
                                    target_name=member.display_name, enemy_name=enemy_data.display_name)
                            else:
                                response = "{target_name} is hit!! {target_name} loses {damage} slime!".format(
                                    target_name=member.display_name,
                                    damage=damage
                                )
                        resp_cont.add_channel_response(ch_name, response)
                else:
                    response = '{} is unable to attack {}.'.format(enemy_data.display_name, member.display_name)
                    resp_cont.add_channel_response(ch_name, response)

                # Persist user and enemy data.
                if enemy_data.life_state == 1:
                    enemy_data.persist()
                target_data.persist()

                district_data.persist()

                # Assign the corpse role to the newly dead player.
                if was_killed:
                    await ewrolemgr.updateRoles(client=client, member=member)
                    # announce death in kill feed channel
                    # killfeed_channel = ewutils.get_channel(enemy_data.id_server, ewcfg.channel_killfeed)
                    killfeed_resp = resp_cont.channel_responses[ch_name]
                    for r in killfeed_resp:
                        resp_cont.add_channel_response(ewcfg.channel_killfeed, r)
                    resp_cont.format_channel_response(ewcfg.channel_killfeed, enemy_data)
                    resp_cont.add_channel_response(ewcfg.channel_killfeed, "`-------------------------`")
                # await ewutils.send_message(client, killfeed_channel, ewutils.formatMessage(enemy_data.display_name, killfeed_resp))

        # Send the response to the player.
        resp_cont.format_channel_response(ch_name, enemy_data)
        await resp_cont.post()

    def change_slimes(self, n=0, source=None):
        change = int(n)
        self.slimes += change


async def summon_enemy(cmd):
    # debug command, though could be kept around for events
    time_now = int(time.time())
    response = ""
    user_data = EwUser(member=cmd.message.author)

    if user_data.poi not in ewcfg.capturable_districts:
        response = "**DEBUG**: MUST SUMMON IN CAPTURABLE DISTRICT."
        return await ewutils.send_message(cmd.client, cmd.message.channel,
                                          ewutils.formatMessage(cmd.message.author, response))

    enemytype = None

    if len(cmd.tokens) > 1:
        enemytype = ewutils.flattenTokenListToString(cmd.tokens[1:])

    if enemytype != None:

        enemy = get_enemy(enemytype)
        enemy.id_server = user_data.id_server
        enemy.poi = user_data.poi
        enemy.level = level_byslime(enemy.slimes)
        enemy.initialslimes = enemy.slimes
        enemy.lifetime = time_now

        enemy.persist()

        response = "**DEBUG**: You have summoned **{}**, a level {} enemy. It has {} slime.".format(enemy.display_name,
                                                                                                    enemy.level,
                                                                                                    enemy.slimes)
    else:
        response = "**DEBUG**: PLEASE RE-SUMMON WITH APPLICABLE TYPING"

    await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def hurtmesoftly(cmd):
    # debug command
    user_data = EwUser(member=cmd.message.author)
    resp_cont = ewutils.EwResponseContainer(id_server=user_data.id_server)

    enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {poi} = %s".format(
        id_enemy=ewcfg.col_id_enemy,
        poi=ewcfg.col_enemy_poi,
    ), (
        user_data.poi,
    ))

    for row in enemydata:
        enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
        resp_cont = await enemy.kill()
        await resp_cont.post()


async def enemy_kill(id_server):
    enemydata = ewutils.execute_sql_query("SELECT * FROM enemies")
    for row in enemydata:
        enemy = EwEnemy(id_enemy=row[0], id_server=id_server)
        if enemy.life_state == 0 or (enemy.lifetime < (int(time.time()) - ewcfg.time_despawn)):
            print("DELETE GATE 1")
            delete_enemy(enemy)
        else:
            resp_cont = await enemy.kill()
            if resp_cont != None:
                await resp_cont.post()


async def spawn_enemy(id_server):
    time_now = int(time.time())
    response = ""
    ch_name = ""
    chosen_poi = ""

    enemies_count = ewcfg.max_enemies
    try_count = 0

    rarity_choice = random.randrange(10000)

    if rarity_choice <= 7000:
        # common enemies
        enemytype = random.choice(common_enemies)
    elif rarity_choice <= 9000:
        # uncommon enemies
        enemytype = random.choice(uncommon_enemies)
    elif rarity_choice <= 9990:
        # rare enemies
        enemytype = random.choice(rare_enemies)
    else:
        # raid bosses
        enemytype = random.choice(raid_bosses)

    # debug manual reassignment
    enemytype = random.choice(common_enemies)

    # TODO: Make enemies spawn in outskirts

    while enemies_count >= ewcfg.max_enemies and try_count < 5:

        # potential_chosen_poi = random.choice(outskirts_districts)
        potential_chosen_poi = 'greenlightdistrict'
        potential_chosen_district = EwDistrict(district=potential_chosen_poi, id_server=id_server)
        enemy_constructor = EwEnemy()
        enemies_count_list = potential_chosen_district.get_enemies_in_district(enemy_constructor)
        enemies_count = len(enemies_count_list)

        if enemies_count < ewcfg.max_enemies:
            chosen_poi = potential_chosen_poi
            try_count = 5
        else:
            # try again
            try_count += 1


    if enemytype != None and chosen_poi != "":
        enemy = get_enemy(enemytype)

        enemy.id_server = id_server
        enemy.level = level_byslime(enemy.slimes)

        enemy.lifetime = time_now

        enemy.initialslimes = enemy.slimes

        enemy.poi = chosen_poi

        enemy.persist()

        response = "**An enemy spawned!** It's a level {} {}, and has {} slime.".format(enemy.level, enemy.display_name,
                                                                                        enemy.slimes)
        ch_name = ewcfg.id_to_poi.get(enemy.poi).channel

    return response, ch_name


def find_enemy(enemy_search=None, user_data=None):
    enemy_found = None
    if enemy_search != None:

        enemy_search_tokens = enemy_search.split(' ')

        if enemy_search_tokens[len(enemy_search_tokens) - 1].isdigit():
            # user passed in a positive integer, identify enemy by number

            searched_id = enemy_search_tokens[len(enemy_search_tokens) - 1]

            enemydata = ewutils.execute_sql_query(
                "SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {id_enemy} = %s".format(
                    id_enemy=ewcfg.col_id_enemy,
                    poi=ewcfg.col_enemy_poi,
                ), (
                    user_data.poi,
                    searched_id,
                ))

            for row in enemydata:
                enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
                enemy_found = enemy
                break
        else:

            enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {poi} = %s".format(
                id_enemy=ewcfg.col_id_enemy,
                poi=ewcfg.col_enemy_poi,
            ), (
                user_data.poi,
            ))

            # find the first (i.e. the oldest) item that matches the search
            for row in enemydata:
                enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
                if enemy.display_name.lower() == enemy_search:
                    enemy_found = enemy
                    break

    return enemy_found


def delete_enemy(enemy_data):
    print("DEBUG - {} - {} DELETED".format(enemy_data.id_enemy, enemy_data.display_name))
    ewutils.execute_sql_query("DELETE FROM enemies WHERE {id_enemy} = %s".format(
        id_enemy=ewcfg.col_id_enemy
    ), (
        enemy_data.id_enemy,
    ))


def drop_enemy_loot(enemy_data, district_data):
    response = ""

    item_counter = 0

    poudrin_dropped = False
    poudrin_range = 0
    poudrin_amount = 0

    pleb_dropped = False
    pleb_range = 0
    pleb_amount = 0

    patr_dropped = False
    patr_range = 0
    patr_amount = 0

    crop_dropped = False
    crop_range = 0
    crop_amount = 0

    if enemy_data.type == 'juvie':

        poudrin_dropped = random.randrange(2) == 0
        pleb_dropped = random.randrange(10) == 0
        crop_dropped = random.randrange(10) <= 2

        if poudrin_dropped:
            poudrin_range = random.randrange(2)
            if poudrin_range == 0:
                poudrin_amount = 1
            else:
                poudrin_amount = 2
        if pleb_dropped:
            pleb_amount = 1
        if crop_dropped:
            crop_amount = 1

    elif enemy_data.type == 'microslime':
        patr_dropped = True
        patr_amount = 1

    elif enemy_data.type == 'slimeasaur':

        poudrin_dropped = True
        pleb_dropped = random.randrange(10) <= 3
        # meat_dropped = True

        poudrin_range = random.randrange(2)

        if poudrin_range == 0:
            poudrin_amount = 3
        else:
            poudrin_amount = 4

        if pleb_dropped:
            pleb_range = random.randrange(2)
            if pleb_range == 0:
                pleb_amount = 1
            else:
                pleb_amount = 2

    elif enemy_data.type == 'slimeadactyl':

        poudrin_dropped = True
        pleb_dropped = random.randrange(10) <= 3

        poudrin_range = random.randrange(2)

        if poudrin_range == 0:
            poudrin_amount = 3
        else:
            poudrin_amount = 4

        if pleb_dropped:
            pleb_range = random.randrange(2)
            if pleb_range == 0:
                pleb_amount = 1
            else:
                pleb_amount = 2

    elif enemy_data.type == 'desertraider':

        poudrin_dropped = True
        pleb_dropped = True
        pleb_amount = 1
        crop_dropped = random.randrange(2) == 0

        poudrin_range = random.randrange(2) == 0

        if poudrin_range == 0:
            poudrin_amount = 1
        else:
            poudrin_amount = 2

        if crop_dropped:
            crop_range = random.randrange(4)
            if crop_range == 0:
                crop_amount = 3
            elif crop_range == 1:
                crop_amount = 4
            elif crop_range == 2:
                crop_amount = 5
            else:
                crop_amount = 6

    elif enemy_data.type == 'megaslime':

        poudrin_dropped = True
        pleb_dropped = True
        patr_dropped = random.randrange(3) == 0

        poudrin_range = random.randrange(3)
        if poudrin_range == 0:
            poudrin_amount = 8
        elif poudrin_range == 1:
            poudrin_amount = 9
        else:
            poudrin_amount = 10

        pleb_range = random.randrange(3)
        if pleb_range == 0:
            pleb_amount = 2
        elif pleb_range == 1:
            pleb_amount = 3
        else:
            pleb_amount = 4

        if patr_dropped:
            patr_amount = 1


    if pleb_dropped or patr_dropped:
        cosmetics_list = []

        for result in ewcfg.cosmetic_items_list:
            if result.ingredients == "":
                cosmetics_list.append(result)
            else:
                pass

    if poudrin_dropped:
        item_counter = 0

        while item_counter < poudrin_amount:
            ewitem.item_create(
                item_type=ewcfg.it_slimepoudrin,
                id_user=district_data.name,
                id_server=district_data.id_server,
            )
            response += "They dropped a slime poudrin!\n"

            item_counter += 1

    if pleb_dropped:
        item_counter = 0

        while item_counter < pleb_amount:
            items = []

            for cosmetic in cosmetics_list:
                if cosmetic.rarity == ewcfg.rarity_plebeian:
                    items.append(cosmetic)

            item = items[random.randint(0, len(items) - 1)]

            ewitem.item_create(
                item_type=ewcfg.it_cosmetic,
                id_user=district_data.name,
                id_server=district_data.id_server,
                item_props={
                    'id_cosmetic': item.id_cosmetic,
                    'cosmetic_name': item.str_name,
                    'cosmetic_desc': item.str_desc,
                    'rarity': item.rarity,
                    'adorned': 'false'
                }
            )
            response += "They dropped a {item_name}!\n".format(item_name=item.str_name)

            item_counter += 1

    if patr_dropped:
        item_counter = 0

        while item_counter < patr_amount:
            items = []

            for cosmetic in cosmetics_list:
                if cosmetic.rarity == ewcfg.rarity_patrician:
                    items.append(cosmetic)

            item = items[random.randint(0, len(items) - 1)]

            ewitem.item_create(
                item_type=ewcfg.it_cosmetic,
                id_user=district_data.name,
                id_server=district_data.id_server,
                item_props={
                    'id_cosmetic': item.id_cosmetic,
                    'cosmetic_name': item.str_name,
                    'cosmetic_desc': item.str_desc,
                    'rarity': item.rarity,
                    'adorned': 'false'
                }
            )
            response += "They dropped a {item_name}!\n".format(item_name=item.str_name)

            item_counter += 1

    if crop_dropped:
        item_counter = 0

        while item_counter < crop_amount:

            vegetable = random.choice(ewcfg.vegetable_list)

            ewitem.item_create(
                id_user=district_data.name,
                id_server=district_data.id_server,
                item_type=ewcfg.it_food,
                item_props={
                    'id_food': vegetable.id_food,
                    'food_name': vegetable.str_name,
                    'food_desc': vegetable.str_desc,
                    'recover_hunger': vegetable.recover_hunger,
                    'str_eat': vegetable.str_eat,
                    'time_expir': time.time() + ewcfg.farm_food_expir
                }
            )
            response += "They dropped a {vegetable_name}!\n".format(vegetable_name=vegetable.str_name)

            item_counter += 1

    if not poudrin_dropped and not pleb_dropped and not patr_dropped and not crop_dropped:
        response = "They didn't drop anything..."

    return response


def kill_enemy(user_data, slimeoid, enemy_data, weapon, market_data, ctn, cmd):
    time_now = int(time.time())
    response = ""
    resp_cont = ewutils.EwResponseContainer(id_server=cmd.message.server.id)
    member = enemy_data

    # Get shooting player's info
    if user_data.slimelevel <= 0:
        user_data.slimelevel = 1
        user_data.persist()

    user_mutations = user_data.get_mutations()
    district_data = EwDistrict(district=user_data.poi, id_server=cmd.message.server.id)

    miss = False
    crit = False
    strikes = 0

    slimes_spent = int(ewutils.slime_bylevel(user_data.slimelevel) / 20)
    slimes_damage = int((slimes_spent * 4) * (100 + (user_data.weaponskill * 10)) / 100.0)

    if weapon is None:
        slimes_damage /= 2  # penalty for not using a weapon, otherwise fists would be on par with other weapons
    slimes_dropped = enemy_data.totaldamage + enemy_data.slimes

    # fumble_chance = (random.randrange(10) - 4)
    # if fumble_chance > user_data.weaponskill:
    # miss = True

    user_iskillers = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_killers
    user_isrowdys = user_data.life_state == ewcfg.life_state_enlisted and user_data.faction == ewcfg.faction_rowdys
    user_isslimecorp = user_data.life_state == ewcfg.life_state_lucky

    if (slimes_spent > user_data.slimes):
        # Not enough slime to shoot.
        response = "You don't have enough slime to attack. ({:,}/{:,})".format(user_data.slimes, slimes_spent)
        resp_cont.add_channel_response(cmd.message.channel.name, response)

    elif (time_now - user_data.time_lastkill) < ewcfg.cd_kill:
        # disallow kill if the player has killed recently
        response = "Take a moment to appreciate your last slaughter."
        resp_cont.add_channel_response(cmd.message.channel.name, response)

    elif user_iskillers == False and user_isrowdys == False and user_isslimecorp == False:
        # Only killers, rowdys, the cop killer, and rowdy fucker can shoot people.
        if user_data.life_state == ewcfg.life_state_juvenile:
            response = "Juveniles lack the moral fiber necessary for violence."
        else:
            response = "You lack the moral fiber necessary for violence."
        resp_cont.add_channel_response(cmd.message.channel.name, response)

    else:
        user_inital_level = user_data.slimelevel

        was_juvenile = False
        was_killed = False

        # hunger drain
        user_data.hunger += ewcfg.hunger_pershot * ewutils.hunger_cost_mod(user_data.slimelevel)

        # Weaponized flavor text.
        randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]

        # Weapon-specific adjustments
        if weapon != None and weapon.fn_effect != None:
            # Build effect container
            ctn.miss = miss
            ctn.crit = crit
            ctn.slimes_damage = slimes_damage
            ctn.slimes_spent = slimes_spent

            # Make adjustments
            weapon.fn_effect(ctn)

            # Apply effects for non-reference values
            miss = ctn.miss
            crit = ctn.crit
            slimes_damage = ctn.slimes_damage
            slimes_spent = ctn.slimes_spent
            strikes = ctn.strikes
        # user_data and shootee_data should be passed by reference, so there's no need to assign them back from the effect container.

        if ewcfg.mutation_id_sharptoother in user_mutations:
            if random.random() < 0.5:
                miss = False

        if miss:
            slimes_damage = 0

        # Remove !revive invulnerability.
        user_data.time_lastrevive = 0

        if ewcfg.mutation_id_organicfursuit in user_mutations and (
                (market_data.day % 31 == 0 and market_data.clock >= 20)
                or (market_data.day % 31 == 1 and market_data.clock < 6)
        ):
            slimes_damage *= 2

        if ewcfg.mutation_id_socialanimal in user_mutations:
            allies_in_district = district_data.get_players_in_district(
                min_level=math.ceil((1 / 10) ** 0.25 * user_data.slimelevel),
                life_states=[ewcfg.life_state_enlisted],
                factions=[user_data.faction]
            )
            if user_data.id_user in allies_in_district:
                allies_in_district.remove(user_data.id_user)

            slimes_damage *= 1 + 0.05 * len(allies_in_district)
        if ewcfg.mutation_id_dressedtokill in user_mutations:
            items = ewitem.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.message.server.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            adorned_items = 0
            for it in items:
                i = EwItem(it.get('id_item'))
                if i.item_props['adorned'] == 'true':
                    adorned_items += 1

            if adorned_items >= ewutils.max_adorn_bylevel(user_data.slimelevel):
                slimes_damage *= 1.2

        # Spend slimes, to a minimum of zero
        user_data.change_slimes(n=(-user_data.slimes if slimes_spent >= user_data.slimes else -slimes_spent),
                                source=ewcfg.source_spending)

        # Damage stats
        ewstats.track_maximum(user=user_data, metric=ewcfg.stat_max_hitdealt, value=slimes_damage)
        ewstats.change_stat(user=user_data, metric=ewcfg.stat_lifetime_damagedealt, n=slimes_damage)

        # Remove repeat killing protection if.
        if user_data.id_killer == enemy_data.id_enemy:
            user_data.id_killer = ""

        user_data.persist()
        # enemy_data = EwEnemy(member = member)

        if slimes_damage >= enemy_data.slimes - enemy_data.bleed_storage:
            was_killed = True
            if ewcfg.mutation_id_thickerthanblood in user_mutations:
                slimes_damage = 0
            else:
                slimes_damage = max(enemy_data.slimes - enemy_data.bleed_storage, 0)

        sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=cmd.message.server.id)
        # move around slime as a result of the shot

        slimes_drained = 0

        damage = str(slimes_damage)

        slimes_tobleed = int((slimes_damage - slimes_drained) / 2)
        if ewcfg.mutation_id_nosferatu in user_mutations and (market_data.clock < 6 or market_data.clock >= 20):
            slimes_tobleed = 0

        slimes_directdamage = slimes_damage - slimes_tobleed
        slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained

        district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
        enemy_data.bleed_storage += slimes_tobleed
        enemy_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
        sewer_data.change_slimes(n=slimes_drained)

        if was_killed:
            # adjust statistics
            # TODO: change these to enemy kill stats
            ewstats.increment_stat(user=user_data, metric=ewcfg.stat_kills)
            ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
            if user_data.slimelevel > enemy_data.level:
                ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_ganks)
            elif user_data.slimelevel < enemy_data.level:
                ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_takedowns)

            # Give a bonus to the player's weapon skill for killing a stronger player.
            if enemy_data.level >= user_data.slimelevel and weapon is not None:
                user_data.add_weaponskill(n=1, weapon_type=weapon.id_weapon)

            # release bleed storage
            if ewcfg.mutation_id_thickerthanblood in user_mutations:
                slimes_todistrict = 0
                slimes_tokiller = enemy_data.slimes
            else:
                slimes_todistrict = enemy_data.slimes / 2
                slimes_tokiller = enemy_data.slimes / 2
            district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)
            levelup_response = user_data.change_slimes(n=slimes_tokiller, source=ewcfg.source_killing)
            if ewcfg.mutation_id_fungalfeaster in user_mutations:
                user_data.hunger = max(0, user_data.hunger - user_data.get_hunger_max() / 2)

            # Enemy was killed.
            delete_enemy(enemy_data)
            print("DEBUG - ENEMY DELETED BY PLAYER KILLING")

            kill_descriptor = "beaten to death"
            if weapon != None:
                response = weapon.str_damage.format(
                    name_player=cmd.message.author.display_name,
                    name_target=member.display_name,
                    hitzone=randombodypart,
                    strikes=strikes
                )
                kill_descriptor = weapon.str_killdescriptor
                if crit:
                    response += " {}".format(weapon.str_crit.format(
                        name_player=cmd.message.author.display_name,
                        name_target=member.display_name
                    ))

                response += "\n\n{}".format(weapon.str_kill.format(
                    name_player=cmd.message.author.display_name,
                    name_target=member.display_name,
                    emote_skull=ewcfg.emote_slimeskull
                ))

            else:
                response = "{name_target} is hit!!\n\n{name_target} has died.".format(
                    name_target=member.display_name)

            # give player item for defeating enemy
            response += "\n\n" + drop_enemy_loot(enemy_data, district_data)

            if slimeoid.life_state == ewcfg.slimeoid_state_active:
                brain = ewcfg.brain_map.get(slimeoid.ai)
                response += "\n\n" + brain.str_kill.format(slimeoid_name=slimeoid.name)

            user_data.persist()
            resp_cont.add_channel_response(cmd.message.channel.name, response)
            user_data = EwUser(member=cmd.message.author)
        else:
            # A non-lethal blow!

            if weapon != None:
                if miss:
                    response = "{}".format(weapon.str_miss.format(
                        name_player=cmd.message.author.display_name,
                        name_target=member.display_name
                    ))
                else:
                    response = weapon.str_damage.format(
                        name_player=cmd.message.author.display_name,
                        name_target=member.display_name,
                        hitzone=randombodypart,
                        strikes=strikes
                    )
                    if crit:
                        response += " {}".format(weapon.str_crit.format(
                            name_player=cmd.message.author.display_name,
                            name_target=member.display_name
                        ))
                    response += " {target_name} loses {damage} slime! **({current}/{total})**".format(
                        target_name=member.display_name,
                        damage=damage,
                        current=enemy_data.slimes,
                        total=enemy_data.initialslimes
                    )
                    if enemy_data.ai == 'Coward':
                        coward_response = random.choice(ewcfg.coward_responses_hurt)
                        coward_response = coward_response.format(enemy_data.display_name)
                        response += coward_response
            else:
                if miss:
                    response = "{target_name} dodges your strike.".format(target_name=member.display_name)
                else:
                    response = "{target_name} is hit!! {target_name} loses {damage} slime! **({current}/{total})**".format(
                        target_name=member.display_name,
                        damage=damage,
                        current=enemy_data.slimes,
                        total=enemy_data.initialslimes
                    )
                    if enemy_data.ai == 'Coward':
                        coward_response = random.choice(ewcfg.coward_responses_hurt)
                        coward_response = coward_response.format(enemy_data.display_name)
                        response += coward_response

            enemy_data.persist()
            resp_cont.add_channel_response(cmd.message.channel.name, response)

        if was_killed and enemy_data.type == 'juvie':
            # announce death in kill feed channel
            # killfeed_channel = ewutils.get_channel(enemy_data.id_server, ewcfg.channel_killfeed)
            killfeed_resp = resp_cont.channel_responses[cmd.message.channel.name]
            for r in killfeed_resp:
                resp_cont.add_channel_response(ewcfg.channel_killfeed, r)
            resp_cont.format_channel_response(ewcfg.channel_killfeed, enemy_data)
            resp_cont.add_channel_response(ewcfg.channel_killfeed, "`-------------------------`")
        # await ewutils.send_message(client, killfeed_channel, ewutils.formatMessage(enemy_data.display_name, killfeed_resp))

        # Add level up text to response if appropriate
        if user_inital_level < user_data.slimelevel:
            resp_cont.add_channel_response(cmd.message.channel.name, "\n" + levelup_response)
        # Enemy kills don't award slime to the kingpin.

        # Persist every users' data.
        user_data.persist()

        district_data.persist()

    return resp_cont


def level_byslime(slime):
    return int(abs(slime) ** 0.25)

class EwAttackType:
    # A name used to identify the attacking type
    id_type = ""

    # Displayed when this weapon is used for a !kill
    str_kill = ""

    # Displayed to the dead victim in the sewers. Brief phrase such as "gunned down" etc.
    str_killdescriptor = ""

    # Displayed when viewing the !trauma of another player.
    str_trauma = ""

    # Displayed when viewing the !trauma of yourself.
    str_trauma_self = ""

    # Displayed when a non-lethal hit occurs.
    str_damage = ""

    # Function that applies the special effect for this weapon.
    fn_effect = None

    # Displayed when a weapon effect causes a critical hit.
    str_crit = ""

    # Displayed when a weapon effect causes a miss.
    str_miss = ""

    def __init__(
            self,
            id_type="",
            str_kill="",
            str_killdescriptor="",
            str_trauma="",
            str_trauma_self="",
            str_damage="",
            fn_effect=None,
            str_crit="",
            str_miss="",
    ):
        self.id_type = id_type
        self.str_kill = str_kill
        self.str_killdescriptor = str_killdescriptor
        self.str_trauma = str_trauma
        self.str_trauma_self = str_trauma_self
        self.str_damage = str_damage
        self.fn_effect = fn_effect
        self.str_crit = str_crit
        self.str_miss = str_miss


class EwEnemyEffectContainer:
    miss = False
    crit = False
    strikes = 0
    slimes_damage = 0
    enemy_data = None
    target_data = None

    # Debug method to dump out the members of this object.
    def dump(self):
        print(
            "effect:\nmiss: {miss}\ncrit: {crit}\nstrikes: {strikes}\nslimes_damage: {slimes_damage}\nslimes_spent: {slimes_spent}".format(
                miss=self.miss,
                crit=self.crit,
                strikes=self.strikes,
                slimes_damage=self.slimes_damage,
                slimes_spent=self.slimes_spent
            ))

    def __init__(
            self,
            miss=False,
            crit=False,
            strikes=0,
            slimes_damage=0,
            slimes_spent=0,
            enemy_data=None,
            target_data=None
    ):
        self.miss = miss
        self.crit = crit
        self.strikes = strikes
        self.slimes_damage = slimes_damage
        self.slimes_spent = slimes_spent
        self.enemy_data = enemy_data
        self.target_data = target_data


def check_death(enemy_data):
    if enemy_data.slimes <= 0 or enemy_data.life_state == 0:
        # delete_enemy(enemy_data)
        return True
    else:
        return False


def get_enemy(enemy_type):
    enemy = EwEnemy()

    if enemy_type == 'juvie':

        enemy.id_server = ""
        enemy.slimes = get_enemy_slime('juvie')
        enemy.totaldamage = 0
        enemy.ai = "Coward"
        enemy.display_name = "Lost Juvie"
        enemy.level = 0
        # enemy.poi = 'greenlightdistrict'
        enemy.life_state = 1
        enemy.type = enemy_type
        enemy.attacktype = 'unarmed'
        enemy.bleed_storage = 0
        enemy.time_lastenter = 0
        enemy.initialslimes = 0

    elif enemy_type == 'slimeasaur':

        enemy.id_server = ""
        enemy.slimes = get_enemy_slime('slimeasaur')
        enemy.totaldamage = 0
        enemy.ai = "Attacker-A"
        enemy.display_name = "Slimeasaur"
        enemy.level = 0
        # enemy.poi = 'greenlightdistrict',
        enemy.life_state = 1
        enemy.type = enemy_type
        enemy.attacktype = "fangs"
        enemy.bleed_storage = 0
        enemy.time_lastenter = 0
        enemy.initialslimes = 0

    return enemy


def get_enemy_slime(enemy_type):
    slime = 0
    if enemy_type == 'juvie':
        slime = (random.randrange(40000) + 10000)
    elif enemy_type == 'slimeasaur':
        slime = (random.randrange(250000) + 250000)

    return slime

common_enemies = ['juvie', 'slimeasaur']

uncommon_enemies = ['slimeadactyl', 'desertraider']

rare_enemies = ['microslime']

raid_bosses = ['megaslime']
