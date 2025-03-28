# from __future__ import absolute_import, unicode_literals
import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('astria_bot')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.timezone = 'Europe/Moscow'

__all__ = ('app',)