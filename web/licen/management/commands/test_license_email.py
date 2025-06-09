from django.core.management.base import BaseCommand
from licen.models import LicenseNotification
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Отправляет тестовое уведомление администраторам'

    def handle(self, *args, **kwargs):
        test_notification = LicenseNotification.objects.first()
        if not test_notification:
            self.stdout.write(self.style.ERROR("Нет уведомлений"))
            return

        test_notification.send_to_admins()
        self.stdout.write(self.style.SUCCESS("Тестовое уведомление отправлено администраторам"))