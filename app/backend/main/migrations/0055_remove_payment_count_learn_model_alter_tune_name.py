# Generated by Django 5.1.5 on 2025-03-17 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_alter_tune_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='count_learn_model',
        ),
        migrations.AlterField(
            model_name='tune',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Название'),
        ),
    ]
