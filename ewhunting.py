import time
import random
import math
import asyncio

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

    # The amount of slime an enemy has
    slimes = 0

    # The total amount of damage an enemy has sustained throughout its lifetime
    totaldamage = 0

    # The type of AI the enemy uses to select which players to attack
    ai = ""

    # The name of enemy shown in responses
    display_name = ""

    # Used to help identify enemies of the same type in a district
    identifier = ""

    # An enemy's level, which determines how much damage it does
    level = 0

    # An enemy's location
    poi = ""

    # Life state 0 = Dead, pending for deletion when it tries its next attack / action
    # Life state 1 = Alive / Activated raid boss
    # Life state 2 = Raid boss pending activation
    life_state = 0

    # Used to determine how much slime an enemy gets, what AI it uses, as well as what weapon it uses.
    type = ""

    # The 'weapon' of an enemy
    attacktype = ""

    # An enemy's bleed storage
    bleed_storage = 0

    # Used for determining when a raid boss should be able to move between districts
    time_lastenter = 0

    # Used to determine how much slime an enemy started out with to create a 'health bar' ( current slime / initial slime )
    initialslimes = 0

    # Enemies despawn when this number reaches 10800 (3 hours)
    lifetime = 0

    # Used by the 'defender' AI to determine who it should retaliate against
    id_target = ""

    # Used by raid bosses to determine when they should activate
    raidtimer = 0

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
                    "SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM enemies{}".format(
                        ewcfg.col_id_enemy,
                        ewcfg.col_id_server,
                        ewcfg.col_enemy_slimes,
                        ewcfg.col_enemy_totaldamage,
                        ewcfg.col_enemy_ai,
                        ewcfg.col_enemy_type,
                        ewcfg.col_enemy_attacktype,
                        ewcfg.col_enemy_display_name,
                        ewcfg.col_enemy_identifier,
                        ewcfg.col_enemy_level,
                        ewcfg.col_enemy_poi,
                        ewcfg.col_enemy_life_state,
                        ewcfg.col_enemy_bleed_storage,
                        ewcfg.col_enemy_time_lastenter,
                        ewcfg.col_enemy_initialslimes,
                        ewcfg.col_enemy_lifetime,
                        ewcfg.col_enemy_id_target,
                        ewcfg.col_enemy_raidtimer,
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
                    self.identifier = result[8]
                    self.level = result[9]
                    self.poi = result[10]
                    self.life_state = result[11]
                    self.bleed_storage = result[12]
                    self.time_lastenter = result[13]
                    self.initialslimes = result[14]
                    self.lifetime = result[15]
                    self.id_target = result[16]
                    self.raidtimer = result[17]

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
                "REPLACE INTO enemies({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
                    ewcfg.col_id_enemy,
                    ewcfg.col_id_server,
                    ewcfg.col_enemy_slimes,
                    ewcfg.col_enemy_totaldamage,
                    ewcfg.col_enemy_ai,
                    ewcfg.col_enemy_type,
                    ewcfg.col_enemy_attacktype,
                    ewcfg.col_enemy_display_name,
                    ewcfg.col_enemy_identifier,
                    ewcfg.col_enemy_level,
                    ewcfg.col_enemy_poi,
                    ewcfg.col_enemy_life_state,
                    ewcfg.col_enemy_bleed_storage,
                    ewcfg.col_enemy_time_lastenter,
                    ewcfg.col_enemy_initialslimes,
                    ewcfg.col_enemy_lifetime,
                    ewcfg.col_enemy_id_target,
                    ewcfg.col_enemy_raidtimer,
                ), (
                    self.id_enemy,
                    self.id_server,
                    self.slimes,
                    self.totaldamage,
                    self.ai,
                    self.type,
                    self.attacktype,
                    self.display_name,
                    self.identifier,
                    self.level,
                    self.poi,
                    self.life_state,
                    self.bleed_storage,
                    self.time_lastenter,
                    self.initialslimes,
                    self.lifetime,
                    self.id_target,
                    self.raidtimer,
                ))

            conn.commit()
        finally:
            # Clean up the database handles.
            cursor.close()
            ewutils.databaseClose(conn_info)

    # Function that enemies use to attack or otherwise interact with players.
    async def kill(self):

        client = ewutils.get_client()

        last_messages = []
        should_post_resp_cont = True

        enemy_data = self

        time_now = int(time.time())
        resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
        district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)
        market_data = EwMarket(id_server=enemy_data.id_server)
        ch_name = ewcfg.id_to_poi.get(enemy_data.poi).channel

        target_data = None
        target_player = None
        target_slimeoid = None

        attacktype = 'unarmed'

        if enemy_data.attacktype != 'unarmed':
            attacktype = ewcfg.attack_type_map.get(enemy_data.attacktype)

        enemy_data.persist()

        # Get target's info based on its AI.

        if enemy_data.ai == "Coward":
            users = ewutils.execute_sql_query(
                "SELECT {id_user}, {life_state} FROM users WHERE {poi} = %s AND {id_server} = %s AND NOT {life_state} = '0'".format(
                    id_user=ewcfg.col_id_user,
                    life_state=ewcfg.col_life_state,
                    poi=ewcfg.col_poi,
                    id_server=ewcfg.col_id_server
                ), (
                    enemy_data.poi,
                    enemy_data.id_server
                ))
            if len(users) > 0:
                if random.randrange(100) > 92:
                    response = random.choice(ewcfg.coward_responses)
                    response = response.format(enemy_data.display_name, enemy_data.display_name)
                    resp_cont.add_channel_response(ch_name, response)
        else:
            target_data = get_target_by_ai(enemy_data)

        if check_raidboss_countdown(enemy_data) and enemy_data.life_state == 2:
            # Raid boss has activated!
            response = "*The ground quakes beneath your feet as slime begins to pool into one hulking, solidified mass...*" \
                       "\n{} **{} has arrvied! It's level {} and has {} slime!** {}\n".format(
                ewcfg.emote_megaslime,
                enemy_data.display_name,
                enemy_data.level,
                enemy_data.slimes,
                ewcfg.emote_megaslime
            )
            resp_cont.add_channel_response(ch_name, response)

            enemy_data.life_state = 1
            enemy_data.time_lastenter = time_now
            enemy_data.persist()

            target_data = None

        elif check_raidboss_countdown(enemy_data) and enemy_data.life_state == 1:
            # Raid boss attacks.
            pass

        # If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
        elif check_raidboss_countdown(enemy_data) == False:

            target_data = None

            while check_raidboss_countdown(enemy_data) == False:
                timer = (enemy_data.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

                if timer < ewcfg.enemy_attack_tick_length and timer != 0:
                    timer = ewcfg.enemy_attack_tick_length

                countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
                resp_cont.add_channel_response(ch_name, countdown_response)

                try:
                    await asyncio.sleep(ewcfg.enemy_attack_tick_length)
                    await client.delete_message(last_messages[len(last_messages)-1])
                except:
                    pass

                last_messages = await resp_cont.post()

            #Once it exits the loop, delete the final countdown message
            try:
                await asyncio.sleep(ewcfg.enemy_attack_tick_length)
                await client.delete_message(last_messages[len(last_messages) - 1])
            except:
                pass

            # Don't make an attempt post resp_cont, since it should be emptied out after the loop exit
            should_post_resp_cont = False


        if target_data != None:

            target_player = EwPlayer(id_user=target_data.id_user)
            target_slimeoid = EwSlimeoid(id_user=target_data.id_user)

            server = client.get_server(target_data.id_server)
            # server = discord.Server(id=target_data.id_server)
            # print(target_data.id_server)
            # channel = discord.utils.get(server.channels, name=ch_name)

            # print(server)

            # member = discord.utils.get(channel.server.members, name=target_player.display_name)
            member = server.get_member(target_data.id_user)
            # print(member)

            target_mutations = target_data.get_mutations()

            miss = False
            crit = False
            strikes = 0

            # maybe enemies COULD have weapon skills? could punishes players who die to the same enemy without mining up beforehand
            # slimes_damage = int((slimes_spent * 4) * (100 + (user_data.weaponskill * 10)) / 100.0)

            # since enemies dont use up slime or hunger, this is only used for damage calculation
            slimes_spent = int(ewutils.slime_bylevel(enemy_data.level) / 20)

            slimes_damage = int(slimes_spent * 4)

            if attacktype == 'unarmed':
                slimes_damage /= 2  # specific to juvies
            if enemy_data.type == "microslime":
                slimes_damage *= 20  # specific to microslime

            slimes_dropped = target_data.totaldamage + target_data.slimes

            target_iskillers = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_killers
            target_isrowdys = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_rowdys
            target_isslimecorp = target_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
            target_isjuvie = target_data.life_state == ewcfg.life_state_juvenile
            target_isnotdead = target_data.life_state != ewcfg.life_state_corpse

            if target_data.life_state == ewcfg.life_state_kingpin:
                # Disallow killing generals.
                response = "The {} tries to attack the kingpin, but is taken aback by the sheer girth of their slime.".format(enemy_data.display_name)
                resp_cont.add_channel_response(ch_name, response)

            elif (time_now - target_data.time_lastrevive) < ewcfg.invuln_onrevive:
                # User is currently invulnerable.
                response = "The {} tries to attack {}, but they have died too recently and are immune.".format(
                    enemy_data.display_name,
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
                    if attacktype != 'unarmed' and attacktype.fn_effect != None:
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
                        target_data.die(cause=ewcfg.cause_enemy_killing)
                        target_data.change_slimes(n=-slimes_dropped / 10, source=ewcfg.source_ghostification)

                        # If a player is killed, remove that player's ID from the enemy's designated target ID.
                        enemy_data.id_target = ""

                        kill_descriptor = "beaten to death"
                        if attacktype != 'unarmed':
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
                if enemy_data.life_state == 1 or enemy_data.life_state == 2:
                    enemy_data.persist()
                target_data.persist()

                district_data.persist()

                # Assign the corpse role to the newly dead player.
                if was_killed:
                    await ewrolemgr.updateRoles(client=client, member=member)
                    # announce death in kill feed channel
                    # killfeed_channel = ewutils.get_channel(enemy_data.id_server, ewcfg.channel_killfeed)
                    # killfeed_resp = resp_cont.channel_responses[ch_name]
                    # for r in killfeed_resp:
                    #     resp_cont.add_channel_response(ewcfg.channel_killfeed, r)
                    # resp_cont.format_channel_response(ewcfg.channel_killfeed, enemy_data)
                    # resp_cont.add_channel_response(ewcfg.channel_killfeed, "`-------------------------`")
                # await ewutils.send_message(client, killfeed_channel, ewutils.formatMessage(enemy_data.display_name, killfeed_resp))

        # Send the response to the player.
        resp_cont.format_channel_response(ch_name, enemy_data)
        if should_post_resp_cont:
            await resp_cont.post()

    def move(self):
        resp_cont = ewutils.EwResponseContainer(id_server=self.id_server)

        old_district_response = ""
        new_district_response = ""
        gang_base_response = ""

        try:
            # Raid bosses can only move into the city (capturable districts), never back into the outskirts.
            destinations = ewcfg.poi_neighbors.get(self.poi).intersection(set(ewcfg.capturable_districts))
            if len(destinations) > 0:
                old_poi = self.poi
                new_poi = random.choice(list(destinations))
                self.poi = new_poi
                self.time_lastenter = int(time.time())

                print("DEBUG - {} MOVED FROM {} TO {}".format(self.display_name, old_poi, new_poi))

                #new_district = EwDistrict(district=new_poi, id_server=self.id_server)
                #enemy_data_constructor = EwEnemy()
                #if len(new_district.get_enemies_in_district(enemy_data_constructor)) > 0:

                # When a raid boss enters a new district, give it a new identifier
                self.identifier = set_identifier(new_poi, self.id_server)

                new_poi_def = ewcfg.id_to_poi.get(new_poi)
                new_ch_name = new_poi_def.channel
                new_district_response = "*A low roar booms throughout the district, as slime on the ground begins to slosh all around.*\n {} **{} has arrived!** {}".format(
                    ewcfg.emote_megaslime,
                    self.display_name,
                    ewcfg.emote_megaslime
                )
                resp_cont.add_channel_response(new_ch_name, new_district_response)

                old_district_response = "{} has moved to {}!".format(self.display_name, new_poi_def.str_name)
                old_poi_def = ewcfg.id_to_poi.get(old_poi)
                old_ch_name = old_poi_def.channel
                resp_cont.add_channel_response(old_ch_name, old_district_response)

                gang_base_response = "There are reports of a powerful enemy roaming around {}.".format(new_poi_def.str_name)
                resp_cont.add_channel_response(ewcfg.channel_rowdyroughhouse, gang_base_response)
                resp_cont.add_channel_response(ewcfg.channel_copkilltown, gang_base_response)
        finally:
            self.persist()
            return resp_cont

    def change_slimes(self, n=0, source=None):
        change = int(n)
        self.slimes += change

        if n < 0:
            change *= -1  # convert to positive number
            if source == ewcfg.source_damage or source == ewcfg.source_bleeding or source == ewcfg.source_self_damage:
                self.totaldamage += change

        self.persist()

# Debug command. Could be used for events, perhaps?
async def summon_enemy(cmd):
    author = cmd.message.author

    if not author.server_permissions.administrator:
        return

    time_now = int(time.time())
    response = ""
    user_data = EwUser(member=cmd.message.author)

    #if user_data.poi not in ewcfg.capturable_districts:
    #   response = "**DEBUG**: MUST SUMMON IN CAPTURABLE DISTRICT."
    #    return await ewutils.send_message(cmd.client, cmd.message.channel,
    #                                      ewutils.formatMessage(cmd.message.author, response))

    enemytype = None
    enemy_location = None
    poi = None

    if len(cmd.tokens) > 2:
        enemytype = cmd.tokens[1]
        enemy_location = cmd.tokens[2]
        poi = ewcfg.id_to_poi.get(enemy_location)


    if enemytype != None and poi != None:

        enemy = get_enemy_data(enemytype)

        # Assign enemy attributes that weren't assigned in get_enemy_data
        enemy.id_server = user_data.id_server
        enemy.poi = poi.id_poi
        enemy.level = level_byslime(enemy.slimes)
        enemy.initialslimes = enemy.slimes
        enemy.lifetime = time_now
        enemy.identifier = set_identifier(poi.id_poi, user_data.id_server)

        enemy.persist()

        response = "**DEBUG**: You have summoned **{}**, a level {} enemy. It has {} slime. It spawned in {}.".format(
            enemy.display_name,
            enemy.level,
            enemy.slimes,
            enemy.poi
        )
    else:
        response = "**DEBUG**: PLEASE RE-SUMMON WITH APPLICABLE TYPING / LOCATION"

    await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

# Gathers all enemies from the database and has them perform an action
async def enemy_perform_action(id_server):
    enemydata = ewutils.execute_sql_query("SELECT * FROM enemies")
    for row in enemydata:
        enemy = EwEnemy(id_enemy=row[0], id_server=id_server)

        # If an enemy is marked for death or has been alive too long, delete it
        if enemy.life_state == 0 or (enemy.lifetime < (int(time.time()) - ewcfg.time_despawn)):
            print("DELETE GATE 1")
            delete_enemy(enemy)
        else:
            # If an enemy is an activated raid boss, it has a 1/10 chance to move between districts.
            if enemy.type in ewcfg.raid_bosses and enemy.life_state == 1 and check_raidboss_movecooldown(enemy):
                if random.randrange(20) == 0:
                    resp_cont = enemy.move()
                    if resp_cont != None:
                        await resp_cont.post()

            # If an enemy is alive, make it peform the kill function.
            resp_cont = await enemy.kill()
            if resp_cont != None:
                await resp_cont.post()

# Spawns an enemy in a randomized outskirt district. If a district is full, it will try again, up to 5 times.
async def spawn_enemy(id_server):
    time_now = int(time.time())
    response = ""
    ch_name = ""
    chosen_poi = ""

    enemies_count = ewcfg.max_enemies
    try_count = 0

    rarity_choice = random.randrange(10000)

    if rarity_choice <= 5000:
        # common enemies
        enemytype = random.choice(ewcfg.common_enemies)
    elif rarity_choice <= 7500:
        # uncommon enemies
        enemytype = random.choice(ewcfg.uncommon_enemies)
    elif rarity_choice <= 9000:
        # rare enemies
        enemytype = random.choice(ewcfg.rare_enemies)
    else:
        # raid bosses
        enemytype = random.choice(ewcfg.raid_bosses)

    # debug manual reassignment
    # enemytype = 'juvie'

    while enemies_count >= ewcfg.max_enemies and try_count < 5:

        potential_chosen_poi = random.choice(outskirts_districts)
        # potential_chosen_poi = 'cratersvilleoutskirts'
        potential_chosen_district = EwDistrict(district=potential_chosen_poi, id_server=id_server)
        enemy_constructor = EwEnemy()
        enemies_list = potential_chosen_district.get_enemies_in_district(enemy_constructor)
        enemies_count = len(enemies_list)

        if enemies_count < ewcfg.max_enemies:
            chosen_poi = potential_chosen_poi
            try_count = 5
        else:
            # Enemy couldn't spawn in that district, try again
            try_count += 1

    if enemytype != None and chosen_poi != "":
        enemy = get_enemy_data(enemytype)

        # Assign enemy attributes that weren't assigned in get_enemy_data
        enemy.id_server = id_server
        enemy.level = level_byslime(enemy.slimes)
        enemy.lifetime = time_now
        enemy.initialslimes = enemy.slimes
        enemy.poi = chosen_poi
        enemy.identifier = set_identifier(chosen_poi, id_server)

        enemy.persist()

        if enemytype not in ewcfg.raid_bosses:
            response = "**An enemy draws near!!** It's a level {} {}, and has {} slime.".format(enemy.level, enemy.display_name, enemy.slimes)
        ch_name = ewcfg.id_to_poi.get(enemy.poi).channel

    return response, ch_name

# Finds an enemy based on its regular/shorthand name, or its ID.
def find_enemy(enemy_search=None, user_data=None):
    enemy_found = None
    enemy_search_alias = None

    if enemy_search != None:

        if enemy_search in ewcfg.enemy_aliases:
            enemy_search_alias = ewcfg.enemy_aliases[enemy_search]

        enemy_search_tokens = enemy_search.split(' ')

        if enemy_search_tokens[len(enemy_search_tokens) - 1].upper() in identifier_letters:
            # user passed in an identifier for a distirct specific enemy

            searched_identifier = enemy_search_tokens[len(enemy_search_tokens) - 1]

            enemydata = ewutils.execute_sql_query(
                "SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {identifier} = %s AND {life_state} = 1".format(
                    id_enemy=ewcfg.col_id_enemy,
                    poi=ewcfg.col_enemy_poi,
                    identifier=ewcfg.col_enemy_identifier,
                    life_state=ewcfg.col_enemy_life_state
                ), (
                    user_data.poi,
                    searched_identifier,
                ))

            for row in enemydata:
                enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
                enemy_found = enemy
                break
        else:
            # last token was a string, identify enemy by name

            enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {life_state} = 1".format(
                id_enemy=ewcfg.col_id_enemy,
                poi=ewcfg.col_enemy_poi,
                life_state=ewcfg.col_enemy_life_state
            ), (
                user_data.poi,
            ))

            # find the first (i.e. the oldest) item that matches the search
            for row in enemydata:
                enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
                if (enemy.display_name.lower() == enemy_search) or (enemy.display_name.lower() == enemy_search_alias):
                    enemy_found = enemy
                    break

    return enemy_found

# Deletes an enemy the database.
def delete_enemy(enemy_data):
    print("DEBUG - {} - {} DELETED".format(enemy_data.id_enemy, enemy_data.display_name))
    ewutils.execute_sql_query("DELETE FROM enemies WHERE {id_enemy} = %s".format(
        id_enemy=ewcfg.col_id_enemy
    ), (
        enemy_data.id_enemy,
    ))

# Drops items into the district when an enemy dies.
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

    meat_dropped = False

    cards_dropped = False

    # Determines what items should be dropped based on enemy type.
    if enemy_data.type == 'juvie':

        poudrin_dropped = random.randrange(2) == 0
        pleb_dropped = random.randrange(10) == 0
        crop_dropped = random.randrange(10) <= 2
        cards_dropped = random.randrange(10) <= 1

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

    elif enemy_data.type == 'dinoslime':

        poudrin_dropped = True
        pleb_dropped = random.randrange(10) <= 3
        meat_dropped = random.randrange(3) != 0

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

    elif enemy_data.type == 'mammoslime':
        patr_dropped = random.randrange(3) == 0
        poudrin_dropped = random.randrange(10) <= 6

        if poudrin_dropped:
            poudrin_range = random.randrange(2)
            if poudrin_range == 0:
                poudrin_amount = 1
            else:
                poudrin_amount = 2
        if patr_dropped:
            patr_range = random.randrange(2)
            if patr_range == 0:
                patr_amount = 1
            else:
                patr_amount = 2

    elif enemy_data.type == 'megaslime' or enemy_data.type == 'slimeasaurusrex':

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

    # Drops items one-by-one
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
            for item in ewcfg.item_list:
                if item.context == "poudrin":
                    ewitem.item_create(
                        item_type=ewcfg.it_item,
                        id_user=district_data.name,
                        id_server=district_data.id_server,
                        item_props={
                            'id_item': item.id_item,
                            'context': item.context,
                            'item_name': item.str_name,
                            'item_desc': item.str_desc,
                        }
                    ),
                    item = EwItem(id_item=item.id_item)
                    item.persist()
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
            response += "They dropped a bushel of {vegetable_name}!\n".format(vegetable_name=vegetable.str_name)

            item_counter += 1

    # Drop dinoslime meat
    if meat_dropped:
        meat = None

        for food in ewcfg.food_list:
            if food.id_food == ewcfg.item_id_dinoslimemeat:
                meat = food
        ewitem.item_create(
            id_user=district_data.name,
            id_server=district_data.id_server,
            item_type=ewcfg.it_food,
            item_props={
                'id_food': meat.id_food,
                'food_name': meat.str_name,
                'food_desc': meat.str_desc,
                'recover_hunger': meat.recover_hunger,
                'str_eat': meat.str_eat,
                'time_expir': time.time() + ewcfg.std_food_expir
            }
        )
        response += "They dropped a piece of meat!\n"

    if cards_dropped:
        cards = None

        for item in ewcfg.item_list:
            if item.id_item == ewcfg.item_id_tradingcardpack:
                cards = item

        print(cards)

        ewitem.item_create(
            id_user=district_data.name,
            id_server=district_data.id_server,
            item_type=ewcfg.it_item,
            item_props={
                'id_item': cards.id_item,
                'context': cards.context,
                'item_name': cards.str_name,
                'item_desc': cards.str_desc,
            }
        )
        response += "They dropped a pack of trading cards!\n"

    if not poudrin_dropped and not pleb_dropped and not patr_dropped and not crop_dropped and not meat_dropped and not cards_dropped:
        response = "They didn't drop anything..."

    return response

# Attacking function for when a player uses !kill on an enemy.
async def kill_enemy(user_data, slimeoid, enemy_data, weapon, market_data, ctn, cmd):
    time_now = int(time.time())
    response = ""
    old_response = ""
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
            ewstats.increment_stat(user=user_data, metric=ewcfg.stat_pve_kills)
            ewstats.track_maximum(user=user_data, metric=ewcfg.stat_biggest_kill, value=int(slimes_dropped))
            if user_data.slimelevel > enemy_data.level:
                ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_pve_ganks)
            elif user_data.slimelevel < enemy_data.level:
                ewstats.increment_stat(user=user_data, metric=ewcfg.stat_lifetime_pve_takedowns)

            # Give a bonus to the player's weapon skill for killing a stronger enemy.
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

            # When a raid boss dies, use this response instead so its drops aren't shown in the killfeed
            old_response = response

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
                    elif enemy_data.ai == 'Defender':
                        enemy_data.id_target = user_data.id_user
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
                    elif enemy_data.ai == 'Defender':
                        enemy_data.id_target = user_data.id_user

            enemy_data.persist()
            resp_cont.add_channel_response(cmd.message.channel.name, response)

        if was_killed and enemy_data.type in ewcfg.raid_bosses:
            # announce raid boss kill in kill feed channel

            killfeed_resp = "*{}*: {}\n\n".format(cmd.message.author.display_name, old_response)
            killfeed_resp +="`-------------------------`"

            killfeed_resp_cont = ewutils.EwResponseContainer(id_server=cmd.message.server.id)
            killfeed_resp_cont.add_channel_response(ewcfg.channel_killfeed, killfeed_resp)
            await killfeed_resp_cont.post()

        # Add level up text to response if appropriate
        if user_inital_level < user_data.slimelevel:
            resp_cont.add_channel_response(cmd.message.channel.name, "\n" + levelup_response)
        # Enemy kills don't award slime to the kingpin.

        # Persist every users' data.
        user_data.persist()

        district_data.persist()

    return resp_cont

# Determines what level an enemy is based on their slime count.
def level_byslime(slime):
    return int(abs(slime) ** 0.25)

# Reskinned version of weapon class from ewwep.
class EwAttackType:

    # An name used to identify the attacking type
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

# Reskinned version of effect container from ewwep.
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

# Check if an enemy is dead. Implemented to prevent enemy data from being recreated when not necessary.
def check_death(enemy_data):
    if enemy_data.slimes <= 0 or enemy_data.life_state == 0:
        # delete_enemy(enemy_data)
        return True
    else:
        return False

# Assigns enemies most of their necessary attributes based on their type.
def get_enemy_data(enemy_type):
    enemy = EwEnemy()

    enemy.id_server = ""
    enemy.slimes = get_enemy_slime(enemy_type)
    enemy.totaldamage = 0
    enemy.level = 0
    enemy.life_state = 1
    enemy.type = enemy_type
    enemy.bleed_storage = 0
    enemy.time_lastenter = 0
    enemy.initialslimes = 0
    enemy.id_target = ""
    enemy.raidtimer = 0

    # Normal enemies
    if enemy_type == 'juvie':
        enemy.ai = "Coward"
        enemy.display_name = "Lost Juvie"
        enemy.attacktype = 'unarmed'

    elif enemy_type == 'microslime':
        enemy.ai = "Defender"
        enemy.display_name = "Microslime"
        enemy.attacktype = 'unarmed'

    elif enemy_type == 'dinoslime':
        enemy.ai = "Attacker-A"
        enemy.display_name = "Dinoslime"
        enemy.attacktype = "fangs"

    elif enemy_type == 'slimeadactyl':
        enemy.ai = "Attacker-B"
        enemy.display_name = "Slimeadactyl"
        enemy.attacktype = "talons"

    elif enemy_type == 'desertraider':
        enemy.ai = "Attacker-B"
        enemy.display_name = "Desert Raider"
        enemy.attacktype = "scythe"

    elif enemy_type == 'mammoslime':
        enemy.ai = "Defender"
        enemy.display_name = "Mammoslime"
        enemy.attacktype = "tusks"

    # Raid bosses
    elif enemy_type == 'megaslime':
        enemy.ai = "Attacker-A"
        enemy.display_name = "Megaslime"
        enemy.life_state = 2
        enemy.attacktype = "gunk shot"
        enemy.raidtimer = int(time.time())

    elif enemy_type == 'slimeasaurusrex':
        enemy.ai = "Attacker-B"
        enemy.display_name = "Slimeasaurus Rex"
        enemy.life_state = 2
        enemy.attacktype = "fangs"
        enemy.raidtimer = int(time.time())

    return enemy

# Returns a randomized amount of slime based on enemy type
def get_enemy_slime(enemy_type):
    slime = 0
    if enemy_type == 'juvie':
        slime = ((random.randrange(40000) + 10000) + 1)
    elif enemy_type == 'microslime':
        slime = 10000
    elif enemy_type == 'dinoslime':
        slime = ((random.randrange(250000) + 250000) + 1)
    elif enemy_type == 'slimeadactyl':
        slime = ((random.randrange(250000) + 500000) + 1)
    elif enemy_type == 'desertraider':
        slime = ((random.randrange(500000) + 250000) + 1)
    elif enemy_type == 'mammoslime':
        slime = ((random.randrange(300000) + 600000) + 1)
    elif enemy_type == 'megaslime':
        slime = 1000000
    elif enemy_type == 'slimeasaurusrex':
        slime = 1500000
    return slime

# Selects which non-ghost user to attack based on certain parameters.
def get_target_by_ai(enemy_data):

    target_data = None

    time_now = int(time.time())

    # If a player's time_lastenter is greater than this, it can be attacked.
    targettimer = time_now - ewcfg.time_enemyaggro

    if enemy_data.ai == "Defender":
        if enemy_data.id_target != "":
            target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server)

    elif enemy_data.ai == "Attacker-A":
        users = ewutils.execute_sql_query(
            "SELECT {id_user}, {life_state}, {time_lastenter} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND NOT {life_state} = '0' ORDER BY {time_lastenter} ASC".format(
                id_user=ewcfg.col_id_user,
                life_state=ewcfg.col_life_state,
                time_lastenter=ewcfg.col_time_lastenter,
                poi=ewcfg.col_poi,
                id_server=ewcfg.col_id_server,
                targettimer=targettimer
            ), (
                enemy_data.poi,
                enemy_data.id_server
            ))
        if len(users) > 0:
            target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server)

    elif enemy_data.ai == "Attacker-B":
        users = ewutils.execute_sql_query(
            "SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND NOT {life_state} = '0' ORDER BY {slimes} DESC".format(
                id_user=ewcfg.col_id_user,
                life_state=ewcfg.col_life_state,
                slimes=ewcfg.col_slimes,
                poi=ewcfg.col_poi,
                id_server=ewcfg.col_id_server,
                time_lastenter=ewcfg.col_time_lastenter,
                targettimer=targettimer
            ), (
                enemy_data.poi,
                enemy_data.id_server
            ))
        if len(users) > 0:
            target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server)

    return target_data

# Check if raidboss is ready to attack / be attacked
def check_raidboss_countdown(enemy_data):
    time_now = int(time.time())

    # Wait for raid bosses
    if enemy_data.type in ewcfg.raid_bosses and enemy_data.raidtimer <= time_now - ewcfg.time_raidcountdown:
        # Raid boss has activated!
        return True
    elif enemy_data.type in ewcfg.raid_bosses and enemy_data.raidtimer > time_now - ewcfg.time_raidcountdown:
        # Raid boss hasn't activated.
        return False

def check_raidboss_movecooldown(enemy_data):
    time_now = int(time.time())

    if enemy_data.type in ewcfg.raid_bosses and enemy_data.time_lastenter <= time_now - ewcfg.time_raidboss_movecooldown:
        # Raid boss can move
        return True
    elif enemy_data.type in ewcfg.raid_bosses and enemy_data.time_lastenter > time_now - ewcfg.time_raidboss_movecooldown:
        # Raid boss can't move yet
        return False

# Gives enemy an identifier so it's easier to pick out in a crowd of enemies
def set_identifier(poi, id_server):
    enemy_constructor = EwEnemy()
    district = EwDistrict(district=poi, id_server=id_server)
    enemies_list = district.get_enemies_in_district(enemy_constructor)

    # A list of identifiers from enemies in a district
    enemy_identifiers = []

    new_identifier = identifier_letters[0]

    if len(enemies_list) > 0:
        for enemy_id in enemies_list:
            enemy = EwEnemy(id_enemy=enemy_id)
            enemy_identifiers.append(enemy.identifier)

        # Sort the list of identifiers alphabetically
        enemy_identifiers.sort()

        for checked_enemy_identifier in enemy_identifiers:
            # If the new identifier matches one from the list of enemy identifiers, give it the next applicable letter
            # Repeat until a unique identifier is given
            if new_identifier == checked_enemy_identifier:
                next_letter = (identifier_letters.index(checked_enemy_identifier) + 1)
                new_identifier = identifier_letters[next_letter]
            else:
                continue

    return new_identifier

# List of outskirt districts for spawning purposes
outskirts_districts = [
    "wreckingtonoutskirts",
    "cratersvilleoutskirts",
    "oozegardensoutskirts",
    "southsleezeboroughoutskirts",
    "crooklineoutskirts",
    "dreadfordoutskirts",
    "jaywalkerplainoutskirts",
    "westglocksburyoutskirts",
    "poloniumhilloutskirts",
    "charcoalparkoutskirts",
    "toxingtonoutskirts",
    "astatineheightsoutskirts",
    "arsonbrookoutskirts",
    "brawldenoutskirts",
    "newnewyonkersoutskirts",
    "assaultflatsbeachoutskirts"
]

# Letters that an enemy can identify themselves with
identifier_letters = [
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
]
