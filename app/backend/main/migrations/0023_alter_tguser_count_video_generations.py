# Generated by Django 5.1.5 on 2025-02-17 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_tguser_count_video_generations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tguser',
            name='count_video_generations',
            field=models.PositiveIntegerField(default=0, verbose_name='Кол-во генераций видео'),
        ),
    ]
