# licen/tasks.py

from celery import shared_task
from django.apps import apps
from datetime import date
from django.utils import timezone
from datetime import timedelta

@shared_task(name="licen.tasks.check_license_expirations")
def check_license_expirations():
    from licen.models import LicenseNotification
    from licen.models import LicenseBaseModel

    # license_models = LicenseBaseModel.__subclasses__()
    license_model_names = ['CryptoPro', 'FiscalNumber', 'ECP', 'UTMRSAKeys', 'MCD', 'HonestSign', 'OFD', 'USAIS']
    license_models = [apps.get_model('licen', name) for name in license_model_names]
    today = timezone.now().date()

    for model in license_models:
        for obj in model.objects.all():
            days_left = (obj.end_date - today).days

            if days_left <= 0:
                LicenseNotification.objects.update_or_create(
                    license_type=model.__name__,
                    license_id=obj.id,
                    notification_type=LicenseNotification.NotificationType.EXPIRED,
                    defaults={
                        'computer': getattr(obj, 'computer', None),
                        'legal_entity': getattr(obj, 'legal_entity', None),
                        'address': getattr(obj, 'address', None),
                        'expiration_date': obj.end_date,
                        'days_left': 0  # Лицензия уже истекла
                    }
                )
            elif days_left == 1:
                LicenseNotification.objects.update_or_create(
                    license_type=model.__name__,
                    license_id=obj.id,
                    notification_type=LicenseNotification.NotificationType.EXPIRING_SOON_1,
                    defaults={
                        'computer': getattr(obj, 'computer', None),
                        'legal_entity': getattr(obj, 'legal_entity', None),
                        'address': getattr(obj, 'address', None),
                        'expiration_date': obj.end_date,
                        'days_left': days_left
                    }
                )
            elif days_left <= 5:
                LicenseNotification.objects.update_or_create(
                    license_type=model.__name__,
                    license_id=obj.id,
                    notification_type=LicenseNotification.NotificationType.EXPIRING_SOON_5,
                    computer=getattr(obj, 'computer', None),
                    legal_entity=getattr(obj, 'legal_entity', None),
                    address=getattr(obj, 'address', None),
                    defaults={
                        'expiration_date': obj.end_date,
                        'days_left': days_left
                    }
                )
            elif days_left <= 7:
                LicenseNotification.objects.update_or_create(
                    license_type=model.__name__,
                    license_id=obj.id,
                    notification_type=LicenseNotification.NotificationType.EXPIRING_SOON_7,
                    defaults={
                        'computer': getattr(obj, 'computer', None),
                        'legal_entity': getattr(obj, 'legal_entity', None),
                        'address': getattr(obj, 'address', None),
                        'expiration_date': obj.end_date,
                        'days_left': days_left
                    }
                )
            elif days_left <= 30:
                LicenseNotification.objects.update_or_create(
                    license_type=model.__name__,
                    license_id=obj.id,
                    notification_type=LicenseNotification.NotificationType.EXPIRING_SOON_30,
                    defaults={
                        'computer': getattr(obj, 'computer', None),
                        'legal_entity': getattr(obj, 'legal_entity', None),
                        'address': getattr(obj, 'address', None),
                        'expiration_date': obj.end_date,
                        'days_left': days_left
                    }
                )

    print("✅ Уведомления о лицензиях созданы")


@shared_task(name="licen.tasks.send_daily_notifications")
def send_daily_notifications():
    from licen.models import LicenseNotification
    from licen.utils.email_notifications import send_license_notification
    from django.contrib.auth import get_user_model
    from django.apps import apps

    User = get_user_model()
    UserProfile = apps.get_model('licen', 'UserProfile')

    admins = User.objects.filter(profile__role=UserProfile.Role.ADMIN, is_active=True)
    notifications = LicenseNotification.objects.filter(is_sent=False)

    #уведомления только для одного админа
    # sent_count = 0

    # for notification in notifications:
    #     for admin in admins:
    #         if send_license_notification(notification, admin):
    #             sent_count += 1
    #             break  # Чтобы не дублировать уведомления для всех админов

    # уведослеия для всех админов
    sent_count = 0

    for notification in notifications:
        for admin in admins:
            if send_license_notification(notification, admin):
                sent_count += 1

        # Только после отправки всем — помечаем как is_sent=True
        notification.is_sent = True
        notification.save()

    print(f"📧 Отправлено {sent_count} уведомлений админам")

@shared_task(name="licen.tasks.clear_old_notifications")
def clear_old_notifications(days=30):
    from licen.models import LicenseNotification
    from datetime import timedelta
    from django.utils import timezone

    cutoff_date = timezone.now().date() - timedelta(days=days)
    deleted_count = LicenseNotification.objects.filter(expiration_date__lt=cutoff_date).delete()[0]

    print(f"✅ Удалено {deleted_count} уведомлений старше {days} дней")
    return deleted_count

@shared_task(name="licen.tasks.clear_expired_licenses")  # ← добавлен декоратор
def clear_expired_licenses(days=30):
    from licen.models import LicenseNotification, LicenseBaseModel
    from datetime import timedelta
    from django.utils import timezone
    threshold_date = timezone.now().date() - timedelta(days=days)

    # Удаляем уведомления
    deleted_notifications, _ = LicenseNotification.objects.filter(
        expiration_date__lt=threshold_date
    ).delete()
    
    # Удаляем лицензии
    total_deleted = 0
    for model in LicenseBaseModel.__subclasses__():
        deleted, _ = model.objects.filter(end_date__lt=threshold_date).delete()
        total_deleted += deleted

    print(f"🧹 Очищено: {total_deleted} лицензий и {deleted_notifications} уведомлений")