from django.shortcuts import render
from . import deal_draw

def index(request):
    if request.method != "POST":
        drawn_cards = ['D', 'E', 'A', 'L', '!']
        context = {'drawn_cards': drawn_cards}
        
    # else:
    #     drawn_cards = deal_draw.deal_cards()
    #     context = {'drawn_cards': drawn_cards}
    #     context['method'] = request.method + ' method'
    return render(request, "videopoker/index.html", context)

def deal(request):
    if request.method == "GET":
        drawn_cards = [c for c in 'NO ACCESS']
        context = {'drawn_cards': drawn_cards}
    if request.method == "POST":
        drawn_cards = deal_draw.deal_cards()
        context = {'drawn_cards': drawn_cards}
    
    return render(request, "videopoker/deal.html", context)
    