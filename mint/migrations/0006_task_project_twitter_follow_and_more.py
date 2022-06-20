# Generated by Django 4.0.5 on 2022-06-18 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0005_alter_project_project_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='twitter_follow',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='twitter_follow_link',
            field=models.URLField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='twitter_like',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='twitter_like_link',
            field=models.URLField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='twitter_retweet',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='twitter_retweet_link',
            field=models.URLField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='projects',
            field=models.ManyToManyField(blank=True, to='mint.project'),
        ),
    ]