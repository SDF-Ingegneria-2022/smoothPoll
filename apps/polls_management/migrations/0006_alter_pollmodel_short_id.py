# Generated by Django 4.1.5 on 2023-03-09 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0005_alter_pollmodel_short_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollmodel',
            name='short_id',
            field=models.CharField(blank=True, default=None, max_length=60, null=True, unique=True, verbose_name='ID Corto'),
        ),
    ]