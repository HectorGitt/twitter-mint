# Generated by Django 4.0.5 on 2022-07-06 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0044_alter_project_wallet_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailnotification',
            name='heading',
            field=models.CharField(default='Congratulations!!!', max_length=60),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='heading_secondary',
            field=models.CharField(default='You have been selected.', max_length=100),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='subject',
            field=models.CharField(default='Congratulations, You have been selected', max_length=80),
        ),
    ]
