# Generated by Django 4.0.5 on 2022-07-07 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0045_alter_emailnotification_heading_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitteruser',
            name='eth_wallet_id',
            field=models.CharField(default='00', max_length=255),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='sol_wallet_id',
            field=models.CharField(default='00', max_length=255),
        ),
    ]