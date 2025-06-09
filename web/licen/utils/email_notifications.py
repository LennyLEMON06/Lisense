# licen/utils/email_notifications.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_license_notification(notification, user):
    from django.conf import settings
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags

    subject = f"[Уведомление] Лицензия {notification.license_type} скоро истекает"

    context = {
        'user': user,
        'license_type': notification.license_type,
        'license_id': notification.license_id,
        'expiration_date': notification.expiration_date,
        'days_left': notification.days_left or 0,
        'admin_url': f"{settings.BASE_URL}/admin/licen/{notification.license_type.lower()}/{notification.license_id}/change/"
    }

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