# Generated by Django 4.1.4 on 2023-01-03 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0004_alter_pollmodel_close_datetime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pollmodel',
            name='close_datetime',
        ),
    ]