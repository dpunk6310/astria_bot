# Generated by Django 5.1.5 on 2025-03-17 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_tune_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tune',
            name='name',
            field=models.CharField(default=None, max_length=20, verbose_name='Название'),
            preserve_default=False,
        ),
    ]
