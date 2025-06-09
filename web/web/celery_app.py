# celery_app.py

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

app = Celery('web')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Регистрация задач
app.autodiscover_tasks(['licen'])

# app.conf.beat_schedule = {
#     'clear-expired-licenses': {
#         'task': 'licen.tasks.clear_expired_licenses',
#         'schedule': crontab(day_of_month='1'),  # Каждый 1-е число месяца
#         'args': (90,),  # Удаляем лицензии, устаревшие более чем на 90 дней
#     },
# }