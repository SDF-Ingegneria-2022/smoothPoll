# Generated by Django 4.1.4 on 2023-01-04 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0006_pollmodel_close_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollmodel',
            name='predefined',
            field=models.BooleanField(default=False, verbose_name='Predefinito'),
        ),
    ]
