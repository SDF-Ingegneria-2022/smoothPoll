# Generated by Django 4.2 on 2023-04-14 08:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0013_alter_pollmodel_protection'),
    ]

    operations = [
        migrations.AddField(
            model_name='polltokens',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
