# Generated by Django 3.1.2 on 2020-10-25 13:15

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calorietracker', '0009_auto_20201021_2217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='log_progress_pic',
        ),
        migrations.AddField(
            model_name='log',
            name='back_progress_pic',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
        migrations.AddField(
            model_name='log',
            name='front_progress_pic',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
        migrations.AddField(
            model_name='log',
            name='side_progress_pic',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
