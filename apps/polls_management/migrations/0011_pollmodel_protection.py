# Generated by Django 4.1.7 on 2023-04-04 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0010_merge_20230331_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollmodel',
            name='protection',
            field=models.CharField(choices=[('unprotected', 'Non protetto'), ('token', 'Token')], default='unprotected', max_length=200),
        ),
    ]
