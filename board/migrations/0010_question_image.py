# Generated by Django 3.2.21 on 2024-06-12 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0009_alter_question_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='question_images/'),
        ),
    ]
