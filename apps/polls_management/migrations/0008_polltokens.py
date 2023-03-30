# Generated by Django 4.1.7 on 2023-03-30 08:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls_management', '0007_pollmodel_randomize_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollTokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_name', models.CharField(max_length=200)),
                ('single_option_use', models.BooleanField(default=False)),
                ('majority_use', models.BooleanField(default=False)),
                ('poll_fk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls_management.pollmodel')),
                ('token_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
