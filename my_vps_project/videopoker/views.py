from django.shortcuts import render
from django.template import loader

# Create your views here.

from django.http import HttpResponse


def index(request):
    template = loader.get_template("videopoker/index.html")
    context = None
    return HttpResponse(template.render(context, request))