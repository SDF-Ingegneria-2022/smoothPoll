# Generated by Django 4.1.3 on 2022-11-29 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_remove_majorityoptionmodel_poll_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='majorityvotemodel',
            name='majority_poll_vote',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.majorityoptionmodel'),
        ),
    ]
