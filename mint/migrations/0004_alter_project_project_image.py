# Generated by Django 4.0.6 on 2022-08-03 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mint', '0003_alter_project_project_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_image',
            field=models.ImageField(upload_to='public/media/uploads/'),
        ),
    ]