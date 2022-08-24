# Generated by Django 4.0.6 on 2022-08-23 22:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0009_remove_twitteruser_referral_twitteruser_referral'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twitteruser',
            name='referral',
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='referred_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals', to='mint.twitteruser'),
        ),
    ]