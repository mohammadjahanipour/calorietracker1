# Generated by Django 3.1.2 on 2020-10-16 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0004_auto_20201016_1657'),
        ('calorietracker', '0006_auto_20201014_0650'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('referral_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='referrals.referral')),
            ],
            bases=('referrals.referral',),
        ),
    ]
