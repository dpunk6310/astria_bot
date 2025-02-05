# Generated by Django 5.1.5 on 2025-02-05 13:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='Image path')),
                ('tg_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.tguser', verbose_name='TG User')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
                'db_table': 'images',
            },
        ),
    ]
