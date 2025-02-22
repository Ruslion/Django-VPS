# Generated by Django 5.0.1 on 2024-02-09 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading_bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_12_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_12_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_192_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_192_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_24_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_24_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_384_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_384_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_3_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_3_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_48_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_48_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_6_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_6_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_96_num_trades',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='historydataeth',
            name='RSI_96_quote_asset_volume',
            field=models.FloatField(null=True),
        ),
    ]
