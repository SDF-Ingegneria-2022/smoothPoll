# Generated by Django 4.1.4 on 2023-01-03 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0005_remove_pollmodel_close_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollmodel',
            name='close_datetime',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Data Chiusura'),
        ),
    ]
