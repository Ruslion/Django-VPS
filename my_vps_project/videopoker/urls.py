from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("deal/", views.deal, name="deal"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("leaders/", views.leaders, name="leaders"),
]