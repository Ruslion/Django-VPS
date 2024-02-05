from django.db import models

# Create your models here.

class HistoryDataETH(models.Model):
    # Raw data columns

    timestamp = models.DateTimeField(primary_key=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close= models.FloatField()
    volume = models.FloatField()
    close_time = models.DateTimeField()
    quote_asset_volume = models.FloatField()
    num_trades = models.PositiveIntegerField()

    # Derived columns

    hour_sin = models.FloatField()
    hour_cos = models.FloatField()
    day_sin = models.FloatField()
    day_cos = models.FloatField()
    mon_sin = models.FloatField()
    mon_cos = models.FloatField()
    weekday_sin = models.FloatField()
    weekday_cos = models.FloatField()
    year = models.PositiveIntegerField() # !!! IntegerField
    RATIO_close_and_MA3 = models.FloatField()
    RATIO_close_and_MA6 = models.FloatField()
    RATIO_close_and_MA12 = models.FloatField()
    RATIO_close_and_MA24 = models.FloatField()
    RATIO_close_and_MA48 = models.FloatField()
    RATIO_close_and_MA96 = models.FloatField()
    RATIO_close_and_MA192 = models.FloatField()
    RATIO_close_and_MA384 = models.FloatField()
    RATIO_quote_asset_volume_and_MA3 = models.FloatField()
    RATIO_quote_asset_volume_and_MA6 = models.FloatField()
    RATIO_quote_asset_volume_and_MA12 = models.FloatField()
    RATIO_quote_asset_volume_and_MA24 = models.FloatField()
    RATIO_quote_asset_volume_and_MA48 = models.FloatField()
    RATIO_quote_asset_volume_and_MA96 = models.FloatField()
    RATIO_quote_asset_volume_and_MA192 = models.FloatField()
    RATIO_quote_asset_volume_and_MA384 = models.FloatField()
    RATIO_num_trades_and_MA3 = models.FloatField()
    RATIO_num_trades_and_MA6 = models.FloatField()
    RATIO_num_trades_and_MA12 = models.FloatField()
    RATIO_num_trades_and_MA24 = models.FloatField()
    RATIO_num_trades_and_MA48 = models.FloatField()
    RATIO_num_trades_and_MA96 = models.FloatField()
    RATIO_num_trades_and_MA192 = models.FloatField()
    RATIO_num_trades_and_MA384 = models.FloatField()
    RATIO_close_and_STD3 = models.FloatField()
    RATIO_close_and_STD6 = models.FloatField()
    RATIO_close_and_STD12 = models.FloatField()
    RATIO_close_and_STD24 = models.FloatField()
    RATIO_close_and_STD48 = models.FloatField()
    RATIO_close_and_STD96 = models.FloatField()
    RATIO_close_and_STD192 = models.FloatField()
    RATIO_close_and_STD384 = models.FloatField()
    RSI_3_close = models.FloatField()
    RSI_6_close = models.FloatField()
    RSI_12_close = models.FloatField()
    RSI_24_close = models.FloatField()
    RSI_48_close = models.FloatField()
    RSI_96_close = models.FloatField()
    RSI_192_close = models.FloatField()
    RSI_384_close = models.FloatField()


    
