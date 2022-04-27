import math
import shlex

from ew.static import cfg as ewcfg
from ew.utils import frontend as fe_utils
from ew.utils import stats as ewstats

def payout(winnings, bet, user_data, currency_used):
    response = ""
    if currency_used == ewcfg.currency_slimecoin:
        user_data.change_slimecoin(n=winnings, coinsource=ewcfg.coinsource_casino)
    elif currency_used == ewcfg.currency_slime:
        levelup_response = user_data.change_slimes(n=winnings, source=ewcfg.source_casino)
        if levelup_response != "":
            response = "\n\n" + levelup_response
        
        # SLIMERNALIA
        if ewcfg.slimernalia_active:
            lifestate_mod = 0.5
            
            # Gangsters and ghosts are bad at slimernalia gambling
            if user_data.life_state == ewcfg.life_state_juvenile:
                lifestate_mod = 1

            ewstats.change_stat(id_server=user_data.id_server, id_user=user_data.id_user, metric=ewcfg.stat_festivity, n=(calc_payout_festivity(winnings) * lifestate_mod))


    user_data.persist()
    # print("Paid out a value of {} to {}.".format(winnings, user_data.id_user))
    return response

def calc_payout_festivity(value):
    if value >= 1000:
        return value / 1000
    else:
        return 1

async def collect_bet(cmd, resp, value, user_data, currency_used):
    response = ""
    if currency_used == ewcfg.currency_slimecoin:
        if value == -1:
            value = user_data.slimecoin

        if value > user_data.slimecoin:
            response = "You don't have enough SlimeCoin for that bet."
            return await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, response))

        # subtract costs
        user_data.change_slimecoin(n=-value, coinsource=ewcfg.coinsource_casino)
    
    elif currency_used == ewcfg.currency_slime:
        if user_data.life_state == ewcfg.life_state_corpse:
            return await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, ewcfg.str_casino_negaslime_dealer))

        if user_data.poi != ewcfg.poi_id_thecasino:
            response = "You try to shove the slime through your phone into the casino, but it just bounces off the screen. Better use a digital currency. Or your soul."
            return await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, response))

        if value == -1:
            value = user_data.slimes

        if value > user_data.slimes:
            response = "You don't have enough slime for that bet."
            return await fe_utils.edit_message(cmd.client, resp, fe_utils.formatMessage(cmd.message.author, response))

        # Phoebus likes big bets and he cannot lie
        if ewcfg.slimernalia_active and (value > ewcfg.phoebus_bet_floor):
            ewstats.change_stat(id_server=user_data.id_server, id_user=user_data.id_user, metric=ewcfg.stat_festivity, n=value / 10000)

        # subtract costs
        user_data.change_slimes(n=-value, source=ewcfg.source_casino)
    # print("Collected bet of {} from {}.".format(value, user_data.id_user))
    return value


def printcard(card):
    img_base = "http://165.227.192.207/img/cas/sb/"
    response = ""
    rank = ""
    suit = ""
    str_ranksuit = " the **{} of {}**. "

    if card in ["1", "14", "27", "40"]:
        rank = "Ace"
    elif card in ["7", "20", "33", "46"]:
        rank = "Seven"
    elif card in ["8", "21", "34", "47"]:
        rank = "Eight"
    elif card in ["9", "22", "35", "48"]:
        rank = "Nine"
    elif card in ["10", "23", "36", "49"]:
        rank = "Ten"
    elif card in ["11", "24", "37", "50"]:
        rank = "Jack"
    elif card in ["12", "25", "38", "51"]:
        rank = "Queen"
    elif card in ["13", "26", "39", "52"]:
        rank = "King"

    if card in ["1", "7", "8", "9", "10", "11", "12", "13"]:
        suit = "Hearts"
    elif card in ["14", "20", "21", "22", "23", "24", "25", "26"]:
        suit = "Slugs"
    elif card in ["27", "33", "34", "35", "36", "37", "38", "39"]:
        suit = "Hats"
    elif card in ["40", "46", "47", "48", "49", "50", "51", "52"]:
        suit = "Shields"

    response += str_ranksuit.format(rank, suit) + img_base + card + ".png"

    return response


def printhand(hand):
    response = ""
    i = 0
    resp_list = []
    for card in hand:
        i += 1
        response += "Card {} is ".format(i) + printcard(card) + "\n"
        if i % 5 == 0:
            resp_list.append(response)
            response = ""

    resp_list.append(response)

    return resp_list


def evaluatehand(hand, skat, trumps):
    multi = 0
    if trumps[0] in hand or trumps[0] in skat:
        for t in trumps:
            if t in hand or t in skat:
                multi += 1
            else:
                return multi
    else:
        for t in trumps:
            if t not in hand and t not in skat:
                multi += 1
            else:
                return multi
    return multi


def evaluatetrick(trick):
    value = 0
    for card in trick:
        if card in ["1", "14", "27", "40"]:  # aces
            value += 11
        elif card in ["7", "20", "33", "46"]:  # sevens
            value += 0
        elif card in ["8", "21", "34", "47"]:  # eights
            value += 0
        elif card in ["9", "22", "35", "48"]:  # nines
            value += 0
        elif card in ["10", "23", "36", "49"]:  # tens
            value += 10
        elif card in ["11", "24", "37", "50"]:  # jacks
            value += 2
        elif card in ["12", "25", "38", "51"]:  # queens
            value += 3
        elif card in ["13", "26", "39", "52"]:  # kings
            value += 4
    return value


def checkiflegal(hand, play, first, trump):
    if play < 0 or play >= len(hand):
        return False
    hearts = ["1", "7", "8", "9", "10", "11", "12", "13"]
    slugs = ["14", "20", "21", "22", "23", "24", "25", "26"]
    hats = ["27", "33", "34", "35", "36", "37", "38", "39"]
    shields = ["40", "46", "47", "48", "49", "50", "51", "52"]
    suits = [slugs, shields, hearts, hats]
    playcard = hand[play]
    for suit in suits:
        for card in trump:
            if card in suit:
                suit.remove(card)
    suits.append(trump)
    for suit in suits:
        if first in suit:
            if playcard in suit:
                return True
            else:
                canfollow = False
                for card in hand:
                    if card in suit:
                        canfollow = True
                return not canfollow


# Unused?
def check_skat_join(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_join) or content.startswith(ewcfg.cmd_slimeskat_decline):
        return True
    return False


# Unused?
def check_skat_bidding(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_bid) or content.startswith(ewcfg.cmd_slimeskat_pass) or content.startswith(ewcfg.cmd_slimeskat_call):
        return True
    return False


def check_skat_bid(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_bid) or content.startswith(ewcfg.cmd_slimeskat_pass):

        # tokenize the message. the command should be the first word.
        try:
            tokens = shlex.split(message.content)  # it's split with shlex now because shlex regards text within quotes as a single token
        except:
            tokens = content.split(' ')  # if splitting via shlex doesnt work (odd number of quotes), use the old splitting method so it doesnt give an exception

        tokens_count = len(tokens)
        cmd = tokens[0].lower()
        if cmd == ewcfg.cmd_slimeskat_pass:
            return 0
        elif tokens_count < 2:
            return -1
        else:
            for t in tokens[1:]:
                if t.isdigit():
                    return int(t)
    return -1


def check_skat_call(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_call) or content.startswith(ewcfg.cmd_slimeskat_pass):

        # tokenize the message. the command should be the first word.
        try:
            tokens = shlex.split(message.content)  # it's split with shlex now because shlex regards text within quotes as a single token
        except:
            tokens = content.split(' ')  # if splitting via shlex doesnt work (odd number of quotes), use the old splitting method so it doesnt give an exception

        tokens_count = len(tokens)
        cmd = tokens[0].lower()
        if cmd == ewcfg.cmd_slimeskat_pass:
            return 0
        elif cmd == ewcfg.cmd_slimeskat_call:
            return 1
    return -1


# Unused?
def check_skat_hand(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_hand) or content.startswith(ewcfg.cmd_slimeskat_take):
        return True
    return False


# Unused?
def check_skat_choice(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_choose):
        return True
    return False


def skat_putback(message, hand, skat):
    content = message.content.lower()
    putback = False

    # tokenize the message. the command should be the first word.
    try:
        tokens = shlex.split(message.content)  # it's split with shlex now because shlex regards text within quotes as a single token
    except:
        tokens = content.split(' ')  # if splitting via shlex doesnt work (odd number of quotes), use the old splitting method so it doesnt give an exception

    tokens_count = len(tokens)
    cmd = tokens[0].lower()
    toremove = len(hand) - 10
    for t in tokens:
        if t.isdigit() and int(t) <= len(hand):
            skat.append(hand[int(t) - 1])
            hand[int(t) - 1] = "remove"
            toremove -= 1
            putback = True
            if toremove == 0:
                break
    while "remove" in hand:
        hand.remove("remove")
    return putback


# Unused?
def check_skat_declare(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_slugs) or content.startswith(ewcfg.cmd_slimeskat_shields) or content.startswith(ewcfg.cmd_slimeskat_hearts) or content.startswith(ewcfg.cmd_slimeskat_hats) or content.startswith(ewcfg.cmd_slimeskat_grand) or content.startswith(ewcfg.cmd_slimeskat_null):
        return True
    return False


# Unused?
def check_skat_play(message):
    content = message.content.lower()
    if content.startswith(ewcfg.cmd_slimeskat_play):
        return True
    return False


def get_skat_play(message, hand):
    content = message.content.lower()
    # tokenize the message. the command should be the first word.
    try:
        tokens = shlex.split(content)  # it's split with shlex now because shlex regards text within quotes as a single token
    except:
        tokens = content.split(' ')  # if splitting via shlex doesnt work (odd number of quotes), use the old splitting method so it doesnt give an exception

    tokens_count = len(tokens)
    cmd = tokens[0].lower()
    play = -1
    for t in tokens:
        if t.isdigit() and int(t) <= len(hand):
            play = int(t)
            break
    return play


def determine_trick_taker(trick, gametype, trump):
    first = trick[0]
    winner = 0
    ranking_table = []
    ranking_table.extend(trump)
    if gametype == "null":
        hearts = ["1", "13", "12", "11", "10", "9", "8", "7"]
        slugs = ["14", "26", "25", "24", "23", "22", "21", "20"]
        hats = ["27", "39", "38", "37", "36", "35", "34", "33"]
        shields = ["40", "52", "51", "50", "49", "48", "47", "46"]

    else:
        hearts = ["1", "10", "13", "12", "9", "8", "7"]
        slugs = ["14", "23", "26", "25", "22", "21", "20"]
        hats = ["27", "36", "39", "38", "35", "34", "33"]
        shields = ["40", "49", "52", "51", "48", "47", "46"]

    suits = [slugs, shields, hearts, hats]
    for suit in suits:
        for card in trump:
            if card in suit:
                suit.remove(card)

    if not first in trump:
        for suit in suits:
            if first in suit:
                ranking_table.extend(suit)

    ranks = []
    for card in trick:
        if card in ranking_table:
            ranks.append(ranking_table.index(card))
        else:
            ranks.append(100)
    return ranks.index(min(ranks))
