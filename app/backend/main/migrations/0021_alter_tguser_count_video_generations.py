# Generated by Django 5.1.5 on 2025-02-16 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_pricelist_type_price_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tguser',
            name='count_video_generations',
            field=models.PositiveIntegerField(default=2, verbose_name='Кол-во генераций видео'),
        ),
    ]
