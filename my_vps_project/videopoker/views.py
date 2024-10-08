from django.shortcuts import render, redirect
from .helpers import deal_draw
from .helpers.init_data_verification import check_webapp_signature
from .helpers import database_connect
from django.http import JsonResponse
import os
import json
from datetime import datetime, timedelta
import requests


TEL_TOKEN = os.environ['TEL_TOKEN']
INITIAL_CHIPS_AMOUNT = 5000 # The amount given at registration.
FRIEND_REF_AMOUNT = 2000
AD_VIEWED_AMOUNT = 100
ADSGRAM_VIEWS_LIMIT = 20
BET_MIN = 100 # The minimum amount of chips bet.
EMPTY_CONTEXT = {'drawn_cards': [1, 2, 3, 4, 5],
                'dealt':False} # Empty context is used as placeholder for the first call of the index page.
CLOWN_CONTEXT = {'drawn_cards': [[u"\U0001F921", ''], # Clown face emoji. This context is used when someone messes with the client's post form.
                                [u"\U0001F921", ''],
                                [u"\U0001F921", ''],
                                [u"\U0001F921", ''],
                                [u"\U0001F921", '']
                                ],
                'dealt':False}
HELD_VALUES = [16, 8, 4, 2, 1] # Held values are used to encode/decode the held cards from client's side.

ADSGRAM_REWARD_KEY = 'Honey2403'

# Combinations IDs as in database.
COMBINATIONS_ID = {'Royal Flush':10, 'Straight Flush':9, 'Four of a Kind':8, 'Full House':7,
                   'Flush':6, 'Straight':5, 'Three of a Kind':4, 'Two pairs':3, 'Jacks or Better':2,'No value':1}
# Combinations winning factor
COMBINATIONS_FACTOR = {'Royal Flush':250, 'Straight Flush':50, 'Four of a Kind':25, 'Full House':9,
                   'Flush':6, 'Straight':4, 'Three of a Kind':3, 'Two pairs':2, 'Jacks or Better':1,'No value':0}

# The following dictionary is used for invoice creation. The keys: amount of chips to be bought, the value is the price in stars.
AMOUNT_DICT = {'5000':'120',
                    '10000':'228',
                    '20000':'432',
                    '40000':'816',
                    '80000':'1536'}

# Help function. Not view. This function prepares context for the new hand dealt.
def get_context(current_bet, telegram_id):
    drawn_cards, extra_cards = deal_draw.deal_cards()
    value_of_new_hand = deal_draw.evaluate_hand(drawn_cards)
    context = {'drawn_cards':[], 'extra_cards':extra_cards}
    context['combination'] = COMBINATIONS_ID[value_of_new_hand]
    context['dealt'] = True
    for card in drawn_cards:
        card_and_color = []
        card_and_color.append(card)
        if card[1] in [ '♥', '♦']:
            card_and_color.append('red')
        else:
            card_and_color.append('') # Black font color is default thus empty string is sufficient.
        context['drawn_cards'].append(card_and_color) # drawn_cards list will have two variables: card itself and its color.

    balance_update_sql = '''UPDATE videopoker_users SET balance = balance - %s WHERE telegram_id = %s RETURNING balance;'''
    result_balance = database_connect.execute_insert_update_sql(balance_update_sql, (current_bet, telegram_id))
    if result_balance:
        context['balance'] = result_balance[0]

    return context

# This view is used for initial application download.
def index(request):

    # Regardless of the options 'dealt' key is equals to False
    request.session['dealt'] = False

    # Below for the cases when session variable 'telegram_id' not specified yet
    if request.method == "GET":
        # Access if telegram_id variable is already in the session.
        telegram_id = request.session.get('telegram_id', False)
        if telegram_id:
            # Telegram id found in session variable.
            # Verifying record in database.
            result_balance = database_connect.execute_select_sql("SELECT balance, id FROM videopoker_users WHERE telegram_id = %s", (telegram_id,))
            if result_balance: # Record in database found
                EMPTY_CONTEXT['balance'] = result_balance[0][0]
                EMPTY_CONTEXT['telegram_id'] = telegram_id
                request.session['balance'] = result_balance[0][0]
                request.session['user_id'] = result_balance[0][1]
                request.session['win_value'] = 0
                return render(request, "videopoker/index.html", EMPTY_CONTEXT)

        # Probably user is not logged in yet.
        # Verifying whether it was reference link.
        
        reference = request.GET.get('tgWebAppStartParam', None)
        if reference:
            # Reference link. Processing.
            if reference[:7] == 'refr_id':
                # Seems to be valid
                refr_id = reference[7:]
                try:
                    user_id = int(refr_id)
                except ValueError:
                    refr_id = None
                if refr_id:
                    # Saving ref_user_id in session for future use.
                    request.session['ref_user_id'] = refr_id


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
            result_balance = database_connect.execute_select_sql("SELECT balance, id FROM videopoker_users WHERE telegram_id = %s", (telegram_id,))
            
            if result_balance:
                # The record is in database
                request.session['telegram_id'] = int(telegram_id)
                EMPTY_CONTEXT['balance'] = result_balance[0][0]
                EMPTY_CONTEXT['telegram_id'] = telegram_id
                request.session['balance'] = result_balance[0][0]
                request.session['user_id'] = result_balance[0][1]
                return render(request, "videopoker/index.html", EMPTY_CONTEXT)
            else:
                # The record is not in database yet. Creating new record.
                insert_user_sql = '''INSERT INTO videopoker_users (telegram_id, first_name, last_name, username, language_code, 
                                allows_write_to_pm, is_premium, photo_url, balance, adsgram_views_today, adsgram_viewed_day) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
                
                '''
                is_premium = user_data.get('is_premium', False)
                photo_url = user_data.get('photo_url', False)
                username = user_data.get('username', 'No_user_name')
                username = username[:500] # Avoid overflow
                first_name = user_data.get('first_name', "")
                first_name = first_name[:200] # Avoid overflow
                last_name = user_data.get('last_name', "")
                last_name = last_name[:200] # Avoid overflow
                allows_write_to_pm = user_data.get('allows_write_to_pm', False)
                lang_code = user_data.get('language_code', "")

                data_tuple = (user_data['id'], 
                                first_name,
                                last_name,
                                username,
                                lang_code, allows_write_to_pm, is_premium, photo_url,
                                INITIAL_CHIPS_AMOUNT, ADSGRAM_VIEWS_LIMIT, datetime.now())
                result = database_connect.execute_insert_update_sql(insert_user_sql, data_tuple)
                request.session['telegram_id'] = int(telegram_id)
                EMPTY_CONTEXT['balance']  = INITIAL_CHIPS_AMOUNT
                EMPTY_CONTEXT['telegram_id'] = telegram_id
                request.session['balance'] = INITIAL_CHIPS_AMOUNT
                request.session['user_id'] = result[0]

                # Updating referal balance
                ref_user_id = request.session.get('ref_user_id', None)
                if ref_user_id:
                    balance_update_sql = '''UPDATE videopoker_users SET balance = balance + %s WHERE telegram_id = %s RETURNING balance;'''
                    result_balance = database_connect.execute_insert_update_sql(balance_update_sql, (FRIEND_REF_AMOUNT, ref_user_id))
                    del request.session['ref_user_id']
                    request.session.modified = True
                return render(request, "videopoker/index.html", EMPTY_CONTEXT)
                
        else:
            # Data invalid
            return redirect("https://t.me/VideoPokerMiniAppBot/VideoPoker")
        
    
# This view is used to control game flow (Hands dealt and assessed)
def deal(request):
    if request.method == "POST":
        if request.session.get('dealt', False) == True:
            request.session['dealt'] = False # Changing card deal/draw stage.
            # Cards are dealt and now needs to be drawn. Cards verifiction below.
            held = int(request.POST.get('held')) # Need to verify held value
            telegram_id = request.session['telegram_id']
            new_hand_of_cards = []
            cards_to_evaluate = []
            context = {}
            context['dealt'] = False
            i = 0
            for index, value in enumerate(HELD_VALUES):
                if held >= value:
                    # This index card is held
                    held-=value
                    new_hand_of_cards.append([card[:] for card in request.session['drawn_cards'][index]]) # creating deep copy to avoid convering Ts to 10s.
                    cards_to_evaluate.append(request.session['drawn_cards'][index][0])
                    
                else:
                    # This index card is not held
                    card = request.session['extra_cards'][i]
                    i+=1
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
            context['combination'] = COMBINATIONS_ID[value_of_new_hand]

            if context['combination'] > 1:
                # Hand has winning combination. Updating balance.
                bet_m = request.session['bet_m']
                if context['combination'] == 10 and bet_m == 5:
                    # Royal Flush with max bet identified. Different multiplier applied.
                    winning_value = BET_MIN * 4000
                else:
                    winning_value = COMBINATIONS_FACTOR[value_of_new_hand] * BET_MIN * bet_m
                balance_update_sql = '''UPDATE videopoker_users SET balance = balance + %s WHERE telegram_id = %s RETURNING balance;'''
                result_balance = database_connect.execute_insert_update_sql(balance_update_sql, (winning_value, telegram_id))
                if result_balance:
                    context['balance'] = result_balance[0]
                    request.session['balance'] = context['balance']
            else:
                # The hand is not winning. Need to return previous value of the balance.
                winning_value = 0
                context['balance'] = request.session['balance']

            request.session['win_value'] = winning_value

            # Saving hand into database.
            saving_hand_sql = '''INSERT INTO videopoker_Hands_dealt (user_id_id, date_time, bet_multiplier, initial_hand,
            final, win_amount, final_comb_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            '''
            

            insert_tuple = (request.session['user_id'], datetime.now(), int(request.session['bet_m']), 
                            ''.join([card_list[0] for card_list in request.session['drawn_cards']]), # Initial cards
                            ''.join(cards_to_evaluate), # final cards
                            winning_value,
                            context['combination'])
            result_insert_hand = database_connect.execute_insert_update_sql(saving_hand_sql, insert_tuple)
            
            return render(request, "videopoker/deal.html", context)
        else:
            # New hand is dealt.
            request.session['dealt'] = True # Changing card deal/draw stage.
            # 1. Need to verify current balance first.
            telegram_id = request.session['telegram_id']
            bet_m = int(request.POST.get('bet_m', 1)) # Bet_m validation required too.
            request.session['bet_m'] = bet_m

            current_bet = bet_m * BET_MIN
            if request.session['balance'] >= current_bet:
                context = get_context(current_bet, telegram_id)
            else:
                # Current bet is higher than balance
                request.session['dealt'] = False
                return render(request, "videopoker/deal.html", CLOWN_CONTEXT)

            
            request.session['drawn_cards'] = [x[:] for x in context['drawn_cards']] # to create deep copy list
            request.session['extra_cards'] = context['extra_cards']
            request.session['balance'] = context['balance']
            for card_list in context['drawn_cards']:
                if 'T' in card_list[0]:
                    card_list[0] = '10' + card_list[0][1:]
            
            context['win_value'] = request.session.get('win_value', 0)
            return render(request, "videopoker/deal.html", context)

    if request.method == "GET": # Returning NO ACCESS list of string if accessed via GET method.
        return render(request, "videopoker/deal.html", CLOWN_CONTEXT)

def leaderboard(request):
    # Selecting leaders for the previous day
    select_leaders_sql = '''SELECT telegram_id, first_name, last_name, SUM(win_amount) AS win from videopoker_hands_dealt hd 
                            JOIN videopoker_users u ON u.id = hd.user_id_id
                            WHERE hd.date_time = CURRENT_DATE AND hd.win_amount > 0
                            GROUP BY u.id
                            ORDER by win DESC, first_name
                            LIMIT 100;'''
    result_leaders = database_connect.execute_select_sql(select_leaders_sql, None)
    
    

    select_locale_sql = '''SELECT language_code FROM videopoker_users
                            GROUP BY language_code
                            ORDER by language_code;
                        '''
    result_locale = database_connect.execute_select_sql(select_locale_sql, None)
    context = {'leaders':result_leaders,
                'locale':[l[0] for l in result_locale],
                'server_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'tel_id': request.session['telegram_id']
            }
    
    request.session['locale'] = context['locale']
    return render(request, "videopoker/leaderboard.html", context)

def leaders(request):
    if request.method == "GET":
        # The page accessed via GET. Nothing to be shown.
        context = {'leaders':[{'username':'Clown',
                                'won':u"\U0001F921"},
                                {'username':'Clown',
                                'won':u"\U0001F921"},
                                {'username':'Clown',
                                'won':u"\U0001F921"},
                                {'username':'Clown',
                                'won':u"\U0001F921"},
            ]}
        return render(request, "videopoker/leaders.html", context)

    # Rendering Top 100 players based on the filters.
    filter_for_sql = request.POST.get('filter', None)
    filter_loc_for_sql = request.POST.get('locale_filter', None)

    select_leaders_sql = '''SELECT telegram_id, first_name, last_name, SUM(win_amount) AS win from videopoker_hands_dealt hd 
                            JOIN videopoker_users u ON u.id = hd.user_id_id
                            WHERE hd.win_amount > 0 AND '''
                            # AND u.language_code LIKE %s
                            

    select_leaders_sql_ending = ''' GROUP BY u.id
                            ORDER by win DESC, first_name
                            LIMIT 100;'''
    match filter_for_sql:
        case 'day':
            filter_for_sql = 'hd.date_time = CURRENT_DATE'
        case 'week':
            # Need to calculate the dates for the previous week
            today = datetime.today().date()
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=7)

            start = start.strftime("%Y-%m-%d")
            end = end.strftime("%Y-%m-%d")

            filter_for_sql = f"""hd.date_time >= '{start}' AND hd.date_time < '{end}'
                                """
        case 'month':
            # Need to calculate the dates for the previous month
            end = datetime.today().replace(day=1).date()
            start = (end - timedelta(days=1)).replace(day=1)

            start = start.strftime("%Y-%m-%d")
            end = end.strftime("%Y-%m-%d")

            filter_for_sql = f"""hd.date_time >= '{start}' AND hd.date_time < '{end}'
            """
        case 'all-time':
            filter_for_sql = """hd.date_time > '2024-01-01'
                            """
        case _:
            # No valid filter. Applying day filter
            filter_for_sql = 'hd.date_time = CURRENT_DATE - 1'
    
    if filter_loc_for_sql in request.session['locale']:
        # Valid locale selected
        filter_loc_for_sql = f""" AND u.language_code = '{filter_loc_for_sql}'
                                """
    else:
        # No valid locale selected OR all selected.
        filter_loc_for_sql = ""


    # Final SQL combination
    select_leaders_sql = select_leaders_sql + filter_for_sql + filter_loc_for_sql + select_leaders_sql_ending

    result_leaders = database_connect.execute_select_sql(select_leaders_sql, None)
    context = {'leaders':result_leaders,
            'tel_id': request.session['telegram_id']}
    return render(request, "videopoker/leaders.html", context)

def createInvoiceLink(request):
    # This function returns InvoiceLink for payment.
    if request.method == "GET":
        # Request method GET. Returning nothing.
        return JsonResponse ({"ok":False,"result":"Get method detected. Failed"})
    
    if request.method == "POST":

        amount_to_buy = request.POST.get('amount')

        if amount_to_buy in AMOUNT_DICT.keys():
            # valid amount
            url_begin = 'https://api.telegram.org/bot'
            method_name = '/createInvoiceLink'
            url_final = url_begin + TEL_TOKEN + method_name
            payload = {'telegram_id':request.session.get('telegram_id', '0'),
                        'amount':amount_to_buy,
                        'price':AMOUNT_DICT[amount_to_buy]}
            # Creating params based on the data from POST method
            params = {'description': amount_to_buy + ' chips for Video Poker game',
                'title': amount_to_buy + ' chips',
                'payload': json.dumps(payload),
                'currency': 'XTR',
                'prices': '[{"label":"' + amount_to_buy + ' chips","amount":' + AMOUNT_DICT[amount_to_buy] +'}]',
                'photo_url': 'https://pychampion.site/static/videopoker/chips.png'
                }
            
            result = requests.get(url_final, params=params)
            context = json.loads(result.text)
            if 'result' not in context.keys():
                context['result'] = 'Request failed'
            if 'description' not in context.keys():
                context['description'] = 'No description'
            return render(request, "videopoker/invoiceLink.html", context)
        else:
            # invalid amount
            return JsonResponse ({"ok":False,"result":"Invalid amount. Failed"})

def adsgramReward(request):
    ''' This view is invoked from Adsgram servers to verify that Ad was viewed.
    '''
    if request.method == "GET":
        # Request method GET. Verifying variables.
        user_id = request.GET.get('userid', False)
        key = request.GET.get('key', None)

        if key == ADSGRAM_REWARD_KEY and user_id:
            # Verifying user_id
            result_balance = database_connect.execute_select_sql("SELECT balance, id FROM videopoker_users WHERE telegram_id = %s", (user_id,))
            if result_balance: # Record in database found
                # Updating user's balance
                balance_update_sql = '''UPDATE videopoker_users SET balance = balance + %s WHERE telegram_id = %s RETURNING balance;'''
                result_balance = database_connect.execute_insert_update_sql(balance_update_sql, (AD_VIEWED_AMOUNT, user_id))
                return JsonResponse ({"ok":True,"result":"Reward has been accrued."})
            else:
                # Record not found in the database
                return JsonResponse ({"ok":False,"result":"The user_id not found in the database. Failed"})
        else:
            # Either key is wrong or user_id not sent with parameters.
            return JsonResponse ({"ok":False,"result":"Either key is wrong or user_id was not sent. Failed"})
    else:
        return JsonResponse ({"ok":False,"result":"Method other than GET detected. Failed"})

def update_balance(request, user_id=None):
    ''' This function returns updated balance in the following HTML tags.
    <input type="hidden"  id="balance" value="{{balance}}">
    '''
    context = {'balance': 0}
    
    if request.method == "GET":
        if user_id:
            result_balance = database_connect.execute_select_sql("SELECT balance FROM videopoker_users WHERE telegram_id = %s", (user_id,))
            if result_balance: # Record in database found
                context['balance'] = result_balance[0][0]
                request.session['balance'] = result_balance[0][0]
                return render(request, "videopoker/update_balance.html", context)
            else:
                # Record not found in the database
                print(f"Record {user_id} not found in the database")
                return render(request, "videopoker/update_balance.html", context)
        else:
            # user_id parameter not found
            return render(request, "videopoker/update_balance.html", context)
    else:
        return render(request, "videopoker/update_balance.html", context)
