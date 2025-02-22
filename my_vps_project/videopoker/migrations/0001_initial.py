# Generated by Django 5.0.7 on 2024-08-08 09:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Combinations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combination', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=500)),
                ('telegram_id', models.PositiveBigIntegerField(blank=True)),
                ('first_name', models.CharField(blank=True, max_length=200)),
                ('last_name', models.CharField(blank=True, max_length=200)),
                ('language_code', models.CharField(blank=True, max_length=4)),
                ('is_premium', models.BooleanField(default=False)),
                ('photo_url', models.TextField(blank=True)),
                ('allows_write_to_pm', models.BooleanField(default=False)),
                ('balance', models.PositiveBigIntegerField(default=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Hands_dealt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('bet_multiplier', models.PositiveSmallIntegerField()),
                ('initial_hand', models.CharField(max_length=10)),
                ('extra_cards', models.CharField(max_length=10)),
                ('discarded', models.CharField(blank=True, max_length=10)),
                ('final_comb', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='videopoker.combinations')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videopoker.users')),
            ],
        ),
    ]
