# Generated by Django 5.1.5 on 2025-02-24 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_newsletter_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promt',
            name='text',
            field=models.TextField(unique=True, verbose_name='Текст'),
        ),
    ]
