from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("deal/", views.deal, name="deal"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("leaders/", views.leaders, name="leaders"),
    path("createInvoiceLink/<str:amount_to_buy>", views.createInvoiceLink, name="createInvoiceLink"),
    path("adsgramReward/", views.adsgramReward, name="adsgramReward"),
    path("update_balance/<int:telegram_id>", views.update_balance, name="update_balance"),
    path("update_adsgram_div/<int:telegram_id>", views.update_adsgram_div, name="update_adsgram_div"),
    path("user_stats/<int:telegram_id>", views.user_stats, name="user_stats"),
]