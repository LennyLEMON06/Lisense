# licen/utils/email_notifications.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from licen.models import LicenseNotification


def send_license_notification(notification, user):
    subject = f"[Уведомление] Лицензия {notification.license_type} скоро истекает"

    license_obj = notification.get_license_object()

    # Достаём связанные объекты из license_obj, не из notification
    computer = getattr(license_obj, 'computer', None)
    address = getattr(license_obj, 'address', None)
    legal_entity = getattr(license_obj, 'legal_entity', None)
    network = getattr(license_obj, 'network', None)
    city = getattr(license_obj, 'city', None)

    context = {
        'user': user,
        'license_type': notification.license_type,
        'license_id': notification.license_id,
        'expiration_date': notification.expiration_date,
        'days_left': notification.days_left or 0,
        'computer': computer.name if computer else '',
        'address': address.address if address else '',
        'legal_entity': legal_entity.name if legal_entity else '',
        'network': network.name if network else '',
        'city': city.name if city else '',
        'detail_url': f"http://localhost:8000/licenses/{notification.license_type}/{notification.license_id}/"
    }

    # ВАЖНО: НЕ используем переменную notification в шаблоне больше!
    html_message = render_to_string('email/license_notification.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)
        notification.is_sent = True
        notification.save()
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")
        return False
