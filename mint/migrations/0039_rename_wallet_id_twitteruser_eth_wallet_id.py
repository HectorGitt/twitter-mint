# Generated by Django 4.0.5 on 2022-07-05 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0038_alter_emailnotification_content_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='twitteruser',
            old_name='wallet_id',
            new_name='eth_wallet_id',
        ),
    ]