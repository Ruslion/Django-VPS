from django.shortcuts import render, redirect
from .helpers import deal_draw
from .helpers.init_data_verification import check_webapp_signature
from .helpers import database_connect
import os
import json


TEL_TOKEN = os.environ['TEL_TOKEN']
INITIAL_CHIPS_AMOUNT = 5000
BET_FACTOR = 100
EMPTY_CONTEXT = {'drawn_cards': [1, 2, 3, 4, 5]}
CLOWN_CONTEXT = {'drawn_cards': [[u"\U0001F921", ''], # Clown face emoji
                                [u"\U0001F921", ''],
                                [u"\U0001F921", ''],
                                [u"\U0001F921", ''],
                                [u"\U0001F921", '']
                                ]}
HELD_VALUES = [16, 8, 4, 2, 1]

COMBINATIONS = {''}

def get_context(current_bet, telegram_id):
    drawn_cards, extra_cards = deal_draw.deal_cards()
    context = {'drawn_cards':[], 'extra_cards':extra_cards}
    
    for card in drawn_cards:
        card_and_color = []
        card_and_color.append(card)
        if card[1] in [ '♥', '♦']:
            card_and_color.append('red')
        else:
            card_and_color.append('')
        context['drawn_cards'].append(card_and_color) # drawn_cards list will have two variables: card itself and its color.

    balance_update_sql = '''UPDATE videopoker_users SET balance = balance - %s WHERE telegram_id = %s RETURNING balance;'''
    result_balance = database_connect.execute_insert_update_sql(balance_update_sql, (current_bet, telegram_id))
    if result_balance:
        context['balance'] = result_balance[0]

    return context


def index(request):

    # Regardless of the options 'dealt' key is equals to False
    request.session['dealt'] = False

    # Verifying session is active
    if 'telegram_id' in request.session:
        # User is logged in. Empty context with balance.
        telegram_id = request.session['telegram_id']
        result_balance = database_connect.execute_select_sql("SELECT balance FROM videopoker_users WHERE telegram_id = %s",
                                    (telegram_id,))
        EMPTY_CONTEXT['balance'] = result_balance[0][0]
        return render(request, "videopoker/index.html", EMPTY_CONTEXT)

    # Below for the cases when session variable 'telegram_id' not specified yet
    if request.method == "GET":
        # Access for myself
        if request.GET.get('password', 'not_found') == '438763601':
            request.session['telegram_id'] = 438763601
            telegram_id = 438763601
            result_balance = database_connect.execute_select_sql("SELECT balance FROM videopoker_users WHERE telegram_id = %s", (telegram_id,))
            EMPTY_CONTEXT['balance'] = result_balance[0][0]
            return render(request, "videopoker/index.html", EMPTY_CONTEXT)

        # Probably user is not logged in yet
        # Sending to login page
        return render(request, "videopoker/login.html")
    # If POST request but no session 'telegram_id' varialbe
    else:
        # User is not logged in yet. New user?
        init_data = request.POST.get('init_data', '')
        if init_data != '':
            # Verifying data
            valid_data, parsed_data = check_webapp_signature(TEL_TOKEN, init_data)
        else:
            # Init_data is empty. Website opened outside of the Telegram. Redirecting.
            return redirect("https://t.me/VideoPokerMiniAppBot/VideoPoker")

        if valid_data:
            # Data valid
            # Verifying whether in db or not
            user_data = json.loads(parsed_data['user'])
            telegram_id = int(user_data['id'])
            result_balance = database_connect.execute_select_sql("SELECT balance FROM videopoker_users WHERE telegram_id = %s", (telegram_id,))
            
            if result_balance:
                # The record is in database
                request.session['telegram_id'] = telegram_id
                EMPTY_CONTEXT['balance'] = result_balance[0][0]
                return render(request, "videopoker/index.html", EMPTY_CONTEXT)
            else:
                # The record is not in database yet. Creating new record.
                insert_user_sql = '''INSERT INTO videopoker_users (telegram_id, first_name, last_name, username, language_code, 
                                allows_write_to_pm, is_premium, photo_url, balance) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                
                '''
                is_premium = user.data.get('is_premium', False)
                photo_url = user.data.get('photo_url', None)

                data_tuple = (user_data['id'], user_data['first_name'], user_data['last_name'], user_data['username'],
                            user_data['language_code'], user_data['allows_write_to_pm'], is_premium, photo_url,
                            INITIAL_CHIPS_AMOUNT)
                result = database_connect.execute_insert_update_sql(insert_user_sql, data_tuple)
                request.session['telegram_id'] = telegram_id
                EMPTY_CONTEXT['balance']  = INITIAL_CHIPS_AMOUNT
                return render(request, "videopoker/index.html", EMPTY_CONTEXT)
                
        else:
            # Data invalid
            return redirect("https://t.me/VideoPokerMiniAppBot/VideoPoker")
        
    

def deal(request):
    if request.method == "POST":
        if request.session.get('dealt', False) == True:
            request.session['dealt'] = False # Changing card deal/draw phase.
            # Cards are dealt and now needs to be drawn. Cards verifiction below.
            held = int(request.POST.get('held'))
            new_hand_of_cards = []
            cards_to_evaluate = []
            context = {}
            for index, value in enumerate(HELD_VALUES):
                if held >= value:
                    # This index card is held
                    held-=value
                    new_hand_of_cards.append(request.session['drawn_cards'][index])
                    cards_to_evaluate.append(request.session['drawn_cards'][index][0])
                    
                else:
                    # This index card is not held
                    card = request.session['extra_cards'][index]
                    cards_to_evaluate.append(card)

                    if card[1] in ['♥', '♦']:
                        new_hand_of_cards.append([card, 'red'])
                    else:
                        new_hand_of_cards.append([card, ''])


            context['drawn_cards'] = new_hand_of_cards

            for card_list in context['drawn_cards']:
                if 'T' in card_list[0]:
                    card_list[0] = '10' + card_list[0][1:]

            value_of_new_hand = deal_draw.evaluate_hand(cards_to_evaluate)


            return render(request, "videopoker/deal.html", context)
        else:
            # New hand is dealt.
            # 1. Need to verify current balance first.
            telegram_id = int(request.session['telegram_id'])
            bet_m = request.POST.get('bet_m', 1) # Bet_m validation required too.
            request.session['bet_m'] = bet_m

            current_bet = int(bet_m) * BET_FACTOR

            context = get_context(current_bet, telegram_id)

            if context['balance'] < 0:
                # Not enough chips for a bet
                # Need to restore balance respectively.
                balance_update_sql = '''UPDATE videopoker_users SET balance = balance + %s WHERE telegram_id = %s;'''
                result_balance_update = database_connect.execute_insert_update_sql(balance_update_sql, (current_bet, telegram_id,))
                # Balance is not enough to place a bet.
            else:
                request.session['drawn_cards'] = [x[:] for x in context['drawn_cards']] # to create deep copy list
                request.session['extra_cards'] = context['extra_cards']
                request.session['dealt'] = True
                
                for card_list in context['drawn_cards']:
                    if 'T' in card_list[0]:
                        card_list[0] = '10' + card_list[0][1:]

                
                return render(request, "videopoker/deal.html", context)

    if request.method == "GET": # Returning NO ACCESS list of string if accessed via GET method.
        return render(request, "videopoker/deal.html", CLOWN_CONTEXT)
    
    
    