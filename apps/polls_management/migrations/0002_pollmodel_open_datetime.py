# Generated by Django 4.1.4 on 2022-12-27 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollmodel',
            name='open_datetime',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Data Apertura'),
        ),
    ]