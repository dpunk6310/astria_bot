# Generated by Django 5.1.5 on 2025-03-01 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_alter_newsletter_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletter',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/newsletter', verbose_name='Изображение'),
        ),
    ]
