# licen/admin_filters.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.db import models

class IsExpiredListFilter(admin.SimpleListFilter):
    title = _('Статус лицензии')
    parameter_name = 'license_status'

    def lookups(self, request, model_admin):
        return (
            ('expired', _('Истекла')),
            ('expiring_soon', _('Скоро истекает')),
            ('active', _('Активна')),
        )

    def queryset(self, request, queryset):
        today = models.DateField().to_python(timezone.now().date())
        if self.value() == 'expired':
            return queryset.filter(end_date__lt=today)
        elif self.value() == 'expiring_soon':
            soon_date = today + timedelta(days=7)
            return queryset.filter(end_date__gte=today, end_date__lte=soon_date)
        elif self.value() == 'active':
            return queryset.filter(end_date__gte=today)
        return queryset