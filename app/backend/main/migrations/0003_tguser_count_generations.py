# Generated by Django 5.1.5 on 2025-02-06 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='tguser',
            name='count_generations',
            field=models.PositiveIntegerField(default=0, verbose_name='Кол-во генераций'),
        ),
    ]
