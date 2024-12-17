from django.db import models

class Users(models.Model):
    username = models.CharField(max_length=500, blank=True)
    telegram_id = models.PositiveBigIntegerField(blank=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    language_code = models.CharField(max_length=4, blank=True )
    is_premium = models.BooleanField(default=False)
    photo_url = models.TextField(blank=True)
    allows_write_to_pm = models.BooleanField(default=False)
    balance = models.PositiveBigIntegerField(default = 5000)
    adsgram_views_today = models.SmallIntegerField(default = 20)
    adsgram_viewed_day = models.DateField(auto_now_add=True, editable=True)

class Hands_dealt(models.Model):
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    date_time = models.DateField(auto_now_add=True)
    bet_multiplier = models.PositiveSmallIntegerField()
    initial_hand = models.CharField(max_length=10)
    # extra_cards = models.CharField(max_length=10)
    final = models.CharField(max_length=10, blank=True)
    win_amount = models.PositiveIntegerField(default=0)
    final_comb = models.ForeignKey("Combinations", on_delete=models.CASCADE, default=1)

class Combinations(models.Model):
    combination = models.CharField(max_length=20)
    bronze = models.PositiveIntegerField()
    silver = models.PositiveIntegerField()
    gold = models.PositiveIntegerField()
    platinum = models.PositiveIntegerField()

class SuccessfulPayment(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3)
    total_amount = models.PositiveSmallIntegerField()
    chips_bought = models.PositiveIntegerField()
    telegram_id = models.PositiveBigIntegerField(blank=True)
    telegram_payment_charge_id = models.CharField(max_length=512)
    provider_payment_charge_id = models.CharField(max_length=512)

# The following class will be used to store the all-time agrregated stats in order to avoid recalculation.
class All_Time_stats(models.Model):
    user_id = models.ForeignKey("Users", on_delete=models.CASCADE)
    hands_dealt = models.PositiveBigIntegerField()
    amount_won = models.PositiveBigIntegerField()
    royal_flush = models.PositiveIntegerField()
    straight_flush = models.PositiveIntegerField()
    four_of_kind = models.PositiveIntegerField()
    full_house =  models.PositiveIntegerField()
    flush =  models.PositiveIntegerField()
    straight = models.PositiveIntegerField()
    three_of_kind = models.PositiveIntegerField()
    two_pairs = models.PositiveIntegerField()
    jacks_or_better = models.PositiveBigIntegerField()
    no_value_hand = models.PositiveBigIntegerField()

class Suggestions(models.Model):
    telegram_id = models.PositiveBigIntegerField(blank=True)
    suggestion = models.CharField(max_length=212)





