# licen/management/commands/clear_expired_licenses.py

from django.core.management.base import BaseCommand
from licen.models import LicenseNotification, LicenseBaseModel
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Очистка устаревших уведомлений и лицензий"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Сколько дней считается актуальной лицензия')

    def handle(self, *args, **options):
        days = options['days']
        threshold_date = timezone.now().date() - timedelta(days=days)

        # Удаление просроченных уведомлений
        expired_notifications = LicenseNotification.objects.filter(
            expiration_date__lt=threshold_date
        )
        count = expired_notifications.count()
        expired_notifications.delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Удалено {count} просроченных уведомлений"))

        # Удаление лицензий, у которых end_date < threshold_date
        from licen.models import LicenseBaseModel
        for model in LicenseBaseModel.__subclasses__():
            expired_licenses = model.objects.filter(end_date__lt=threshold_date)
            count = expired_licenses.count()
            if count > 0:
                expired_licenses.delete()
                self.stdout.write(self.style.SUCCESS(f"✅ Удалено {count} просроченных {model.__name__}"))