from django.shortcuts import render
from .helpers import deal_draw
from .helpers.init_data_verification import check_webapp_signature
import os

TEL_TOKEN = os.environ['TEL_TOKEN']

def index(request):
    # Verifying session is active
    if 'telegram_id' in request.session:
        # User is logged in
        drawn_cards = deal_draw.deal_cards()
        context = {'drawn_cards': drawn_cards}
        return render(request, "videopoker/index.html", context)

    if request.method == "GET":
        # Probably user is not logged in yet
        # Sending to login page
        return render(request, "videopoker/login.html")
    # If POST request but no session.
    else:
        # User is not logged in yet
        init_data = request.POST['init_data']
        valid_data, parsed_data = check_webapp_signature(TEL_TOKEN, init_data)
        if valid_data:
            # Data valid
            # Verifying whether in db or not

        else:
            # Data invalid
        
    
    
        
   
    return render(request, "videopoker/index.html", context)

def deal(request):
    if request.method == "GET":
        drawn_cards = [c for c in 'NO ACCESS']
        context = {'drawn_cards': drawn_cards}
    if request.method == "POST":
        drawn_cards = deal_draw.deal_cards()
        context = {'drawn_cards': drawn_cards}
    
    return render(request, "videopoker/deal.html", context)
    