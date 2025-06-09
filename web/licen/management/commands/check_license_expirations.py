from django.core.management.base import BaseCommand
from licen.models import LicenseNotification
from django.apps import apps
from datetime import date
from licen.models import LicenseBaseModel  # Убедись, что импортирован

class Command(BaseCommand):
    help = 'Проверяет истекающие лицензии и создаёт уведомления'

    def handle(self, *args, **kwargs):
        today = date.today()

        # Получаем только модели, которые наследуются от LicenseBaseModel
        license_models = [
            model for model in apps.get_app_config('licen').get_models()
            if issubclass(model, LicenseBaseModel)
        ]

        for model in license_models:
            for obj in model.objects.all():
                if hasattr(obj, 'is_expired') and hasattr(obj, 'is_expiring_soon'):
                    if obj.is_expired:
                        LicenseNotification.objects.get_or_create(
                            license_type=model.__name__,
                            license_id=obj.id,
                            notification_type=LicenseNotification.NotificationType.EXPIRED,
                            defaults={
                                'computer': getattr(obj, 'computer', None),
                                'expiration_date': obj.end_date
                            }
                        )
                    elif obj.is_expiring_soon:
                        LicenseNotification.objects.get_or_create(
                            license_type=model.__name__,
                            license_id=obj.id,
                            notification_type=LicenseNotification.NotificationType.EXPIRING_SOON,
                            defaults={
                                'computer': getattr(obj, 'computer', None),
                                'expiration_date': obj.end_date
                            }
                        )

        self.stdout.write(self.style.SUCCESS("Уведомления созданы"))