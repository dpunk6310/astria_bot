# Generated by Django 5.1.5 on 2025-03-14 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_tguser_attempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='count_learn_model',
            field=models.PositiveIntegerField(default=0, verbose_name='Кол-во обучений модели'),
        ),
        migrations.AddField(
            model_name='payment',
            name='description',
            field=models.CharField(blank=True, null=True, verbose_name='Описание'),
        ),
    ]
