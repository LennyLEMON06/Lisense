# licen/management/commands/clear_old_notifications.py

from django.core.management.base import BaseCommand
from licen.models import LicenseNotification
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = "Удаляет старые уведомления"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help="Сколько дней хранить уведомления")

    def handle(self, *args, **kwargs):
        days = kwargs['days']
        cutoff_date = timezone.now().date() - timedelta(days=days)

        # Удаляем все уведомления, истёкшие более N дней назад
        deleted_count = LicenseNotification.objects.filter(expiration_date__lt=cutoff_date).delete()[0]
        self.stdout.write(self.style.SUCCESS(f"✅ Удалено {deleted_count} уведомлений старше {days} дней"))