# Generated by Django 4.0.5 on 2022-07-07 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0046_alter_twitteruser_eth_wallet_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitteruser',
            name='eth_wallet_id',
            field=models.CharField(default='00', max_length=25),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='sol_wallet_id',
            field=models.CharField(default='00', max_length=25),
        ),
    ]