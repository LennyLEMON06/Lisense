# licen/apps.py

from django.apps import AppConfig

class LicenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'licen'

    def ready(self):
        import licen.signals