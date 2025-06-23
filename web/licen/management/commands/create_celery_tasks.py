# licen/management/commands/create_celery_tasks.py

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Create or update Celery Beat tasks'

    def handle(self, *args, **options):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES
        )

        PeriodicTask.objects.update_or_create(
            name='Send daily notifications',
            defaults={
                'task': 'licen.tasks.send_daily_notifications',
                'interval': schedule,
                'enabled': True,
                'description': 'Отправка ежедневных уведомлений',
            }
        )

        PeriodicTask.objects.update_or_create(
            name='Clear old notifications',
            defaults={
                'task': 'licen.tasks.clear_old_notifications',
                'interval': schedule,
                'enabled': True,
                'description': 'Удаление старых уведомлений',
            }
        )

        PeriodicTask.objects.update_or_create(
            name='Clear expired licenses',
            defaults={
                'task': 'licen.tasks.clear_expired_licenses',
                'interval': schedule,
                'enabled': True,
                'description': 'Очистка просроченных лицензий',
            }
        )

        PeriodicTask.objects.update_or_create(
            name='Check license expirations',
            defaults={
                'task': 'licen.tasks.check_license_expirations',
                'interval': schedule,
                'enabled': True,
                'description': 'Проверка на истекающие лицензии',
            }
        )
