# Generated by Django 5.1.5 on 2025-03-17 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_promocode_alter_payment_options_delete_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='count_generations_video_for_gift',
            field=models.PositiveIntegerField(default=0, verbose_name='Кол-во генераций видео для подарка'),
        ),
        migrations.AddField(
            model_name='promocode',
            name='count_video_generations',
            field=models.PositiveIntegerField(default=0, verbose_name='Кол-во генераций видео'),
        ),
        migrations.AddField(
            model_name='promocode',
            name='is_learn_model',
            field=models.BooleanField(default=False, verbose_name='Обучение модели'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='count_generations_for_gift',
            field=models.PositiveIntegerField(default=0, verbose_name='Кол-во генераций фото для подарка'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='count_generations',
            field=models.PositiveIntegerField(default=0, verbose_name='Кол-во генераций фото'),
        ),
    ]
