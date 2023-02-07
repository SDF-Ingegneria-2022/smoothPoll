# Generated by Django 4.1.5 on 2023-02-01 12:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls_management', '0009_alter_pollmodel_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollmodel',
            name='author',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
