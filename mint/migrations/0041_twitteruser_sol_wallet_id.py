# Generated by Django 4.0.5 on 2022-07-05 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0040_project_wallet_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteruser',
            name='sol_wallet_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]