from django.db import models

# class Users(models.Model):
#     username = models.CharField(max_length=500)
#     telegram_id = models.PositiveBigIntegerField(blank=True)
#     first_name = models.CharField(max_length=200, blank=True)
#     last_name = models.CharField(max_length=200, blank=True)
#     language_code = models.CharField(max_length=4, blank=True )
#     is_premium = models.BooleanField(default=False)
#     photo_url = models.TextField(blank=True)
#     allows_write_to_pm = models.BooleanField(default=False)
#     balance = models.PositiveBigIntegerField(default = 2000)

# class Hands_dealt(models.Model):
#     user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
#     date_time = models.DateTimeField(auto_now_add=True)
#     bet_multiplier = models.PositiveSmallIntegerField()
#     initial_hand = models.CharField(max_length=10)
#     extra_cards = models.CharField(max_length=10)
#     discarded = models.CharField(max_length=10, blank=True)
#     final_comb = models.ForeignKey("Combinations", on_delete=models.CASCADE, default=1)

# class Combinations(models.Model):
#     combination = models.CharField(max_length=20)

