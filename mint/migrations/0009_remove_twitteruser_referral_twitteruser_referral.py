# Generated by Django 4.0.6 on 2022-08-23 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0008_twitteruser_referral_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twitteruser',
            name='referral',
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='referral',
            field=models.ManyToManyField(blank=True, null=True, related_name='referred_by', to='mint.twitteruser'),
        ),
    ]