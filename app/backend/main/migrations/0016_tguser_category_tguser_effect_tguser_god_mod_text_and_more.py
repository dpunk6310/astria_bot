# Generated by Django 5.1.5 on 2025-02-11 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_payment_is_first_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='tguser',
            name='category',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Выбраная категория'),
        ),
        migrations.AddField(
            model_name='tguser',
            name='effect',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Выбранный фильтр(эффект)'),
        ),
        migrations.AddField(
            model_name='tguser',
            name='god_mod_text',
            field=models.TextField(blank=True, null=True, verbose_name='Текст промта'),
        ),
        migrations.AddField(
            model_name='tguser',
            name='tune_id',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Выбранный TUNE'),
        ),
    ]
