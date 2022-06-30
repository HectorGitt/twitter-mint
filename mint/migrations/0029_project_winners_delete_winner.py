# Generated by Django 4.0.5 on 2022-06-30 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0028_alter_winner_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='winners',
            field=models.ManyToManyField(blank=True, related_name='winners', to='mint.twitteruser'),
        ),
        migrations.DeleteModel(
            name='Winner',
        ),
    ]
