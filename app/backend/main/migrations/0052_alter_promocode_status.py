# Generated by Django 5.1.5 on 2025-03-17 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_payment_count_generations_video_for_gift_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='status',
            field=models.BooleanField(default=True, verbose_name='Status'),
        ),
    ]
