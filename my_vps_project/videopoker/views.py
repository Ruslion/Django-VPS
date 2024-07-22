from django.shortcuts import render

def index(request):
    context = None
    return render(request, "videopoker/index.html", context)