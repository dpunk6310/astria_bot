# Generated by Django 5.1.5 on 2025-02-09 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_tguser_referal'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricelist',
            name='learn_model',
            field=models.BooleanField(default=False, verbose_name='Обучение модели'),
        ),
    ]
