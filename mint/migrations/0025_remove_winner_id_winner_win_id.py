# Generated by Django 4.0.5 on 2022-06-30 15:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0024_winner_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='winner',
            name='id',
        ),
        migrations.AddField(
            model_name='winner',
            name='win_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]