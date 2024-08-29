from django.contrib import admin

from .models import Combinations, Users, Hands_dealt, SuccessfulPayment, Suggestions

admin.site.register(Combinations)
admin.site.register(Users)
admin.site.register(Hands_dealt)
admin.site.register(SuccessfulPayment)
admin.site.register(Suggestions)
