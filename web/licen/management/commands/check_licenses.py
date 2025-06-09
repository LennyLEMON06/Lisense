from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from licen.models import LicenseBaseModel, LicenseNotification


class Command(BaseCommand):
    help = 'Проверяет лицензии на истечение срока и отправляет уведомления'
    
    def handle(self, *args, **options):
        license_models = LicenseBaseModel.__subclasses__()
        today = timezone.now().date()
        
        for model in license_models:
            # Лицензии, которые истекают через 7 дней
            soon_date = today + timedelta(days=7)
            expiring_soon = model.objects.filter(end_date=soon_date)
            
            for license in expiring_soon:
                if not LicenseNotification.objects.filter(
                    license_type=model.__name__,
                    license_id=license.id,
                    notification_type='expiring_soon'
                ).exists():
                    notification = LicenseNotification.objects.create(
                        license_type=model.__name__,
                        license_id=license.id,
                        computer=license.computer,
                        expiration_date=license.end_date,
                        notification_type='expiring_soon'
                    )
                    notification.send_to_admins()
                    self.stdout.write(f"Создано уведомление для {license} (скоро истекает)")
            
            # Просроченные лицензии
            expired = model.objects.filter(end_date__lt=today)
            
            for license in expired:
                if not LicenseNotification.objects.filter(
                    license_type=model.__name__,
                    license_id=license.id,
                    notification_type='expired'
                ).exists():
                    notification = LicenseNotification.objects.create(
                        license_type=model.__name__,
                        license_id=license.id,
                        computer=license.computer,
                        expiration_date=license.end_date,
                        notification_type='expired'
                    )
                    notification.send_to_admins()
                    self.stdout.write(f"Создано уведомление для {license} (истек срок)")