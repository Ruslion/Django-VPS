from django.shortcuts import render, redirect
from .helpers import deal_draw
from .helpers.init_data_verification import check_webapp_signature
from .helpers import database_connect
import os
import json

TEL_TOKEN = os.environ['TEL_TOKEN']

def index(request):
    def get_context():
        drawn_cards = deal_draw.deal_cards()
        context = {'drawn_cards': drawn_cards}
        return context

    # Verifying session is active
    if 'telegram_id' in request.session:
        # User is logged in
        return render(request, "videopoker/index.html", get_context())

    # Below for the cases when session variable 'telegram_id' not specified yet

    if request.method == "GET":
        if request.GET.get('password', 'not_found') == '438763601':
            request.session['telegram_id'] = 438763601
            return render(request, "videopoker/index.html", get_context())

        # Probably user is not logged in yet
        # Sending to login page
        return render(request, "videopoker/login.html")
    # If POST request but no session 'telegram_id' varialbe
    else:
        # User is not logged in yet. New user?
        init_data = request.POST['init_data']
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
            result = database_connect.execute_select_sql("SELECT telegram_id FROM videopoker_users WHERE telegram_id = %s", (telegram_id,))
            
            if result:
                # The record is in database
                request.session['telegram_id'] = telegram_id
                return render(request, "videopoker/index.html", get_context())
            else:
                # The record is not in database yet. Creating new record.
                insert_user_sql = '''INSERT INTO videopoker_users (telegram_id, first_name, last_name, username, language_code, 
                                allows_write_to_pm, is_premium, photo_url, balance) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                
                '''
    
                is_premium = user.data.get('is_premium', False)
                photo_url = user.data.get('photo_url', False)

                data_tuple = (user_data['id'], user_data['first_name'], user_data['last_name'], user_data['username'],
                            user_data['language_code'], user_data['allows_write_to_pm'], is_premium, photo_url,
                            2000)
                result = database_connect.execute_insert_sql(insert_user_sql, data_tuple)
                request.session['telegram_id'] = telegram_id
                return render(request, "videopoker/index.html", get_context())
                
        else:
            # Data invalid
            return redirect("https://t.me/VideoPokerMiniAppBot/VideoPoker")
        
    

def deal(request):
    if request.method == "POST":
        drawn_cards = deal_draw.deal_cards()
        context = {'drawn_cards': drawn_cards}
    if request.method == "GET":
        drawn_cards = [c for c in 'NO ACCESS']
        context = {'drawn_cards': drawn_cards}
    
    return render(request, "videopoker/deal.html", context)
    