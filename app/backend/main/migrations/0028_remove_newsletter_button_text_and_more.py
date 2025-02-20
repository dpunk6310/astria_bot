# Generated by Django 5.1.5 on 2025-02-20 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_newsletter_tguser_sent_messages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsletter',
            name='button_text',
        ),
        migrations.RemoveField(
            model_name='newsletter',
            name='button_url',
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='delay_hours',
            field=models.FloatField(blank=True, null=True, verbose_name='Задержка в часах'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название рассылки'),
        ),
    ]
