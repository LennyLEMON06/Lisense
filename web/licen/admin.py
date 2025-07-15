# admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .admin_filters import IsExpiredListFilter
from django.db import models
from .models import (
    City,
    LegalEntity,
    Network,
    Address,
    Operator,
    Provider,
    MobileOperator,
    InternetProvider,
    RouterAdminPanel,
    PersonalAccountMobileOperator,
    PersonalAccountInternetProvider,
    WiFi,
    Computer,
    FiscalNumber,
    CryptoPro,
    ECP,
    UTMRSAKeys,
    MCD,
    HonestSign,
    OFD,
    USAIS,
    RemoteAccess,
    LicenseNotification,
    UserProfile
)

# ================== Базовые модели ==================

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    verbose_name = _('Город')
    verbose_name_plural = _('Города')


@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name',)
    list_filter = ('city',)
    ordering = ('name',)
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'comments')
        }),
        (_('Местоположение'), {
            'fields': ('city',)
        }),
    )
    verbose_name = _('Сеть')
    verbose_name_plural = _('Сети')


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn','legal_entity')
    search_fields = ('name', 'inn')
    list_filter = ('legal_entity',)
    ordering = ('name',)
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'inn', 'legal_entity', 'comments')
        }),
    )
    verbose_name = _('Юридическое лицо')
    verbose_name_plural = _('Юридические лица')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'network')
    search_fields = ('address',)
    list_filter = ('network__legal_entity', 'network')
    ordering = ('network', 'address')
    fieldsets = (
        (_('Адрес'), {
            'fields': ('address', 'network', 'comments')
        }),
    )
    verbose_name = _('Адрес')
    verbose_name_plural = _('Адреса')


# ================== Операторы и провайдеры ==================

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    verbose_name = _('Оператор')
    verbose_name_plural = _('Операторы')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    verbose_name = _('Провайдер')
    verbose_name_plural = _('Провайдеры')


@admin.register(MobileOperator)
class MobileOperatorAdmin(admin.ModelAdmin):
    list_display = ('operator', 'phone_number', 'employee_name', 'address')
    search_fields = ('phone_number', 'employee_name')
    list_filter = ('operator', 'address__network__legal_entity')
    ordering = ('operator', 'phone_number')
    fieldsets = (
        (_('Оператор'), {
            'fields': ('operator',)
        }),
        (_('Контакт'), {
            'fields': ('phone_number', 'employee_name', 'contract')
        }),
        (_('Адрес'), {
            'fields': ('address',)
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('Мобильный оператор')
    verbose_name_plural = _('Мобильные операторы')


@admin.register(InternetProvider)
class InternetProviderAdmin(admin.ModelAdmin):
    list_display = ('provider', 'speed', 'price', 'address')
    search_fields = ('speed',)
    list_filter = ('provider', 'address__network__legal_entity')
    ordering = ('provider', 'address')
    fieldsets = (
        (_('Провайдер'), {
            'fields': ('provider',)
        }),
        (_('Технические данные'), {
            'fields': ('speed', 'price', 'contract')
        }),
        (_('Адрес'), {
            'fields': ('address',)
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('Интернет-провайдер')
    verbose_name_plural = _('Интернет-провайдеры')


# ================== Роутеры и аккаунты ==================

@admin.register(RouterAdminPanel)
class RouterAdminPanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'address')
    search_fields = ('ip_address',)
    list_filter = ('address__network__legal_entity',)
    ordering = ('address', 'name')
    fieldsets = (
        (_('Название'), {
            'fields': ('name',)
        }),
        (_('Доступ'), {
            'fields': ('login', 'password', 'ip_address')
        }),
        (_('Адрес'), {
            'fields': ('address',)
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('Доступ в админ панель роутера')
    verbose_name_plural = _('Доступы в админ панели роутеров')


@admin.register(PersonalAccountMobileOperator)
class PersonalAccountMobileOperatorAdmin(admin.ModelAdmin):
    list_display = ('login', 'mobile_operator', 'ip_address', 'address')
    search_fields = ('login',)
    list_filter = ('mobile_operator__operator', 'address__network__legal_entity')
    ordering = ('mobile_operator', 'login')
    fieldsets = (
        (_('Логин'), {
            'fields': ('login', 'password')
        }),
        (_('IP-адрес'), {
            'fields': ('ip_address',)
        }),
        (_('Связь'), {
            'fields': ('mobile_operator', 'address')
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('Личный кабинет мобильного оператора')
    verbose_name_plural = _('Личные кабинеты мобильных операторов')


@admin.register(PersonalAccountInternetProvider)
class PersonalAccountInternetProviderAdmin(admin.ModelAdmin):
    list_display = ('login', 'internet_provider', 'ip_address', 'address')
    search_fields = ('login',)
    list_filter = ('internet_provider__provider', 'address__network__legal_entity')
    ordering = ('internet_provider', 'login')
    fieldsets = (
        (_('Логин'), {
            'fields': ('login', 'password')
        }),
        (_('IP-адрес'), {
            'fields': ('ip_address',)
        }),
        (_('Связь'), {
            'fields': ('internet_provider', 'address')
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('Личный кабинет интернет-провайдера')
    verbose_name_plural = _('Личные кабинеты интернет-провайдеров')


# ================== WiFi ==================

@admin.register(WiFi)
class WiFiAdmin(admin.ModelAdmin):
    list_display = ('name', 'frequency_band', 'address')
    search_fields = ('name',)
    list_filter = ('frequency_band', 'address__network__legal_entity')
    ordering = ('name',)
    fieldsets = (
        (_('Сеть'), {
            'fields': ('name', 'frequency_band')
        }),
        (_('Пароль'), {
            'fields': ('password',)
        }),
        (_('Адрес'), {
            'fields': ('address',)
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('WiFi сеть')
    verbose_name_plural = _('WiFi сети')


# ================== Компьютеры и лицензии ==================

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ipv4_address', 'mac_address', 'address')
    search_fields = ('name', 'ipv4_address', 'mac_address')
    list_filter = ('address__network__legal_entity',)
    ordering = ('address', 'name')
    fieldsets = (
        (_('Название'), {
            'fields': ('name',)
        }),
        (_('Сетевые параметры'), {
            'fields': ('ipv4_address', 'mac_address')
        }),
        (_('Адрес'), {
            'fields': ('address',)
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('Компьютер')
    verbose_name_plural = _('Компьютеры')


# Лицензии — регистрируем каждую отдельно

for license_model in [
    FiscalNumber,
    CryptoPro,
    ECP,
    UTMRSAKeys,
    MCD,
    HonestSign,
    OFD,
    USAIS
]:
    @admin.register(license_model)
    class LicenseAdmin(admin.ModelAdmin):
        list_display = [f.name for f in license_model._meta.fields if f.name not in ['id', 'created_at', 'updated_at']]
        # list_filter = ('computer', 'is_expired', 'is_expiring_soon')
        list_filter = ('computer', IsExpiredListFilter)
        search_fields = [f.name for f in license_model._meta.fields if isinstance(f, models.CharField)]
        ordering = ['-end_date']
        date_hierarchy = 'end_date'
        readonly_fields = ('created_at', 'updated_at')
        fieldsets = (
            (_('Информация'), {
                'fields': ([f.name for f in license_model._meta.fields if f.name not in ['id', 'created_at', 'updated_at']])
            }),
            (_('Временные метки'), {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
        verbose_name = license_model._meta.verbose_name
        verbose_name_plural = license_model._meta.verbose_name_plural


# ================== Удалённый доступ ==================

@admin.register(RemoteAccess)
class RemoteAccessAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'access_id', 'computer')
    search_fields = ('access_id',)
    list_filter = ('name', 'computer__address__network__legal_entity')
    ordering = ('computer', 'name')
    fieldsets = (
        (_('Тип доступа'), {
            'fields': ('name',)
        }),
        (_('Данные подключения'), {
            'fields': ('access_id', 'password')
        }),
        (_('Компьютер'), {
            'fields': ('computer',)
        }),
        (_('Дополнительно'), {
            'fields': ('comments',)
        }),
    )
    verbose_name = _('Удаленный доступ')
    verbose_name_plural = _('Удаленные доступы')


# ================== Уведомления ==================

@admin.register(LicenseNotification)
class LicenseNotificationAdmin(admin.ModelAdmin):
    list_display = ('license_type', 'license_id', 'days_left', 'notification_type', 'expiration_date', 'is_sent', 'user_notified', 'days_left', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'expiration_date', 'days_left')
    search_fields = ('license_type', 'license_id')
    raw_id_fields = ('computer',)
    autocomplete_lookup_fields = {
        'fk': ['computer'],
    }
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Уведомление'), {
            'fields': ('license_type', 'license_id', 'notification_type', 'expiration_date', 'is_sent')
        }),
        (_('Получатель'), {
            'fields': ('user_notified',)
        }),
        (_('Временные метки'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    verbose_name = _('Уведомление о лицензии')
    verbose_name_plural = _('Уведомления о лицензиях')


# ================== Профиль пользователя ==================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_approved')
    list_editable = ('is_approved',)
    list_filter = ('role',)
    search_fields = ('user__username',)
    raw_id_fields = ('user',)
    autocomplete_lookup_fields = {
        'fk': ['user'],
    }
    fieldsets = (
        (_('Пользователь'), {
            'fields': ('user',)
        }),
        (_('Роль'), {
            'fields': ('role',)
        }),
        (_('Доступ'), {
            'fields': ('is_approved',)
        }),
    )
    verbose_name = _('Профиль пользователя')
    verbose_name_plural = _('Профили пользователей')