from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("deal/", views.deal, name="deal"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("leaders/", views.leaders, name="leaders"),
    path("createInvoiceLink/", views.createInvoiceLink, name="createInvoiceLink"),
    path("adsgramReward/", views.adsgramReward, name="adsgramReward"),
    path("update_balance/<int:user_id>", views.update_balance, name="update_balance"),
]