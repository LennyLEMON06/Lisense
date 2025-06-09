# licen/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from licen.models import LicenseNotification
from licen.tasks import check_license_expirations

@receiver(post_save, sender='auth.User')
def on_user_saved(sender, instance, **kwargs):
    # При изменении профиля пользователя запускай задачу
    check_license_expirations.delay()