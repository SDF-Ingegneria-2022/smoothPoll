# Generated by Django 4.2 on 2023-05-16 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls_management', '0017_alter_pollmodel_poll_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchulzeVoteModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('order', models.CharField(max_length=200)),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls_management.pollmodel')),
            ],
        ),
    ]