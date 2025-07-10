from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy, reverse

class LicenseBaseModel(models.Model):
    """Абстрактная базовая модель для лицензий"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    start_date = models.DateField(verbose_name=_('Дата начала действия (с)'))
    end_date = models.DateField(verbose_name=_('Дата окончания действия (по)'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    computer = models.ForeignKey(
        'Computer',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name=_('Компьютер')
    )

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.end_date < timezone.now().date()

    @property
    def is_expiring_soon_30(self):
        from datetime import timedelta
        from django.utils import timezone
        return (self.end_date - timedelta(days=30)) == timezone.now().date()

    @property
    def is_expiring_soon_7(self):
        from datetime import timedelta
        from django.utils import timezone
        return (self.end_date - timedelta(days=7)) == timezone.now().date()

    @property
    def is_expiring_soon_5(self):
        from datetime import timedelta
        from django.utils import timezone
        return (self.end_date - timedelta(days=5)) == timezone.now().date()

    @property
    def is_expiring_soon_1(self):
        from datetime import timedelta
        from django.utils import timezone
        return (self.end_date - timedelta(days=1)) == timezone.now().date()
    
    
    
    @property
    def address(self):
        return self.computer.address if self.computer else None

    @property
    def network(self):
        try:
            return self.computer.address.network
        except AttributeError:
            return None

    @property
    def legal_entity(self):
        try:
            return self.computer.address.network.legal_entity
        except AttributeError:
            return None

    @property
    def city(self):
        try:
            return self.computer.address.network.legal_entity.city
        except AttributeError:
            return None

        
    def get_verbose_name(self):
        return self._meta.verbose_name
            
    class Meta:
        abstract = True
        ordering = ['-end_date']
        indexes = [
            models.Index(fields=['end_date']),
        ]

class TimestampModel(models.Model):
    """Абстрактная модель для добавления временных меток"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        abstract = True

# Если нужна роль пользователя — можно сделать отдельную модель Profile с FK на User
# или добавить поле role в отдельной модели UserProfile

class City(TimestampModel):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Название города'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Город')
        verbose_name_plural = _('Города')
        ordering = ['name']

class ContactPerson(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='contact_persons',
        verbose_name=_('Город')
    )
    full_name = models.CharField(max_length=255, verbose_name=_('ФИО'))
    position = models.CharField(max_length=255, verbose_name=_('Должность'))
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name=_('Номер телефона')
    )
    email = models.EmailField(verbose_name=_('Email'))
    email_password = models.CharField(
        max_length=255,
        verbose_name=_('Пароль от почты'),
        help_text=_('Введите пароль или зашифрованное значение')
    )

    def __str__(self):
        return f"{self.full_name} ({self.position}) — {self.city.name}"

    class Meta:
        verbose_name = _('Контактное лицо')
        verbose_name_plural = _('Контактные лица')
        ordering = ['full_name']

class LegalEntity(TimestampModel):
    name = models.CharField(max_length=255, verbose_name=_('Наименование сети'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='legal_entities',
        verbose_name=_('Город')
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Сеть')
        verbose_name_plural = _('Сети')
        ordering = ['name']
        unique_together = ['name', 'city']


class Network(TimestampModel):
    name = models.CharField(max_length=255, verbose_name=_('Название юридического лица'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    legal_entity = models.ForeignKey(
        LegalEntity,
        on_delete=models.CASCADE,
        related_name='networks',
        verbose_name=_('Сеть')
    )
    inn = models.CharField(
        max_length=12,
        unique=True,
        validators=[MinLengthValidator(10)],
        verbose_name=_('ИНН')
    )

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"

    class Meta:
        verbose_name = _('Юридическое лицо')
        verbose_name_plural = _('Юридические лица')
        ordering = ['name']
        indexes = [
            models.Index(fields=['inn']),
        ]

class Address(TimestampModel):
    address = models.TextField(verbose_name=_('Адрес сети'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('Юридическое лицо')
    )

    def __str__(self):
        return f"{self.address} ({self.network})"

    class Meta:
        verbose_name = _('Адрес')
        verbose_name_plural = _('Адреса')
        ordering = ['network', 'address']

class Operator(TimestampModel):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Название оператора'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Оператор')
        verbose_name_plural = _('Операторы')
        ordering = ['name']

class Provider(TimestampModel):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Название провайдера'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Провайдер')
        verbose_name_plural = _('Провайдеры')
        ordering = ['name']

class MobileOperator(TimestampModel):
    operator = models.ForeignKey(
        Operator,
        on_delete=models.PROTECT,
        related_name='mobile_operators',
        verbose_name=_('Оператор')
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        verbose_name=_('Номер телефона')
    )
    employee_name = models.CharField(max_length=255, verbose_name=_('ФИО сотрудника'))
    contract = models.CharField(max_length=100, verbose_name=_('Договор'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='mobile_operators',
        verbose_name=_('Адрес')
    )

    def __str__(self):
        return f"{self.operator} ({self.phone_number})"

    class Meta:
        verbose_name = _('Мобильный оператор')
        verbose_name_plural = _('Мобильные операторы')
        ordering = ['operator', 'phone_number']
        unique_together = ['phone_number', 'address']

class InternetProvider(TimestampModel):
    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        related_name='internet_providers',
        verbose_name=_('Провайдер')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена')
    )
    speed = models.CharField(max_length=50, verbose_name=_('Скорость'))
    contract = models.CharField(max_length=100, verbose_name=_('Договор'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='internet_providers',
        verbose_name=_('Адрес')
    )

    def __str__(self):
        return f"{self.provider} ({self.speed})"

    class Meta:
        verbose_name = _('Интернет-провайдер')
        verbose_name_plural = _('Интернет-провайдеры')
        ordering = ['provider', 'address']
        unique_together = ['provider', 'address']

class RouterAdminPanel(TimestampModel):
    name = models.CharField(max_length=100, verbose_name=_('Имя'))
    login = models.CharField(max_length=50, verbose_name=_('Логин'))
    password = models.CharField(max_length=100, verbose_name=_('Пароль'))
    ip_address = models.GenericIPAddressField(verbose_name=_('IP-адрес'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='router_admin_panels',
        verbose_name=_('Адрес')
    )

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    class Meta:
        verbose_name = _('Доступ в админ панель роутера')
        verbose_name_plural = _('Доступы в админ панели роутеров')
        ordering = ['address', 'name']
        unique_together = ['ip_address', 'address']

class PersonalAccountBase(TimestampModel):
    """Абстрактная базовая модель для личных кабинетов"""
    login = models.CharField(max_length=50, verbose_name=_('Логин'))
    password = models.CharField(max_length=100, verbose_name=_('Пароль'))
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('IP-адрес')
    )
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name=_('Адрес')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.login} ({self.ip_address})"

class PersonalAccountMobileOperator(PersonalAccountBase):
    mobile_operator = models.ForeignKey(
        MobileOperator,
        on_delete=models.CASCADE,
        related_name='personal_accounts',
        verbose_name=_('Мобильный оператор'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Личный кабинет мобильного оператора')
        verbose_name_plural = _('Личные кабинеты мобильных операторов')
        ordering = ['mobile_operator', 'login']

class PersonalAccountInternetProvider(PersonalAccountBase):
    internet_provider = models.ForeignKey(
        InternetProvider,
        on_delete=models.CASCADE,
        related_name='personal_accounts',
        verbose_name=_('Интернет-провайдер'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Личный кабинет интернет-провайдера')
        verbose_name_plural = _('Личные кабинеты интернет-провайдеров')
        ordering = ['internet_provider', 'login']

class WiFi(TimestampModel):
    class FrequencyBand(models.TextChoices):
        GHZ_2_4 = '2.4', _('2.4 ГГц')
        GHZ_5 = '5', _('5 ГГц')
        DUAL_BAND = 'dual', _('Двухдиапазонный (2.4/5 ГГц)')

    name = models.CharField(max_length=100, verbose_name=_('Имя сети (SSID)'))
    password = models.CharField(max_length=100, verbose_name=_('Пароль'))
    frequency_band = models.CharField(
        max_length=10,
        choices=FrequencyBand.choices,
        default=FrequencyBand.DUAL_BAND,
        verbose_name=_('Диапазон частот')
    )
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='wifi_networks',
        verbose_name=_('Адрес')
    )

    def __str__(self):
        return f"{self.name} ({self.frequency_band})"

    class Meta:
        verbose_name = _('WiFi сеть')
        verbose_name_plural = _('WiFi сети')
        ordering = ['name']


# === License (обновлённая) ===
class Computer(TimestampModel):
    name = models.CharField(max_length=100, verbose_name=_('Имя компьютера'))
    mac_address = models.CharField(
        blank=True,
        null=True,
        max_length=17,
        validators=[RegexValidator(
            regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
            message='Введите корректный MAC-адрес'
        )],
        verbose_name=_('MAC-адрес')
    )
    ipv4_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        protocol='IPv4',
        verbose_name=_('IPv4 адрес')
    )
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='computers',
        verbose_name=_('Адрес')
    )

    def __str__(self):
        return f"{self.name} ({self.ipv4_address})"

    class Meta:
        verbose_name = _('Компьютер')
        verbose_name_plural = _('Компьютеры')
        ordering = ['address', 'name']
        unique_together = ['ipv4_address', 'address']


class FiscalNumber(LicenseBaseModel):
    model = models.CharField(
        max_length=100,
        verbose_name=_('Модель')
    )
    zn = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('ЗН')
    )

    reg_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Регистрационный номер')
    )
    fn = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('ФН')
    )

    def __str__(self):
        return f"ФН {self.reg_number}"

    class Meta:
        verbose_name = _('ФН')
        verbose_name_plural = _('ФН')

class CryptoPro(LicenseBaseModel):
    key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Ключ')
    )

    def __str__(self):
        return f"КриптоПро {self.key}"
    
    class Meta:
        verbose_name = _('КриптоПро')
        verbose_name_plural = _('КриптоПро')

class ECP(LicenseBaseModel):
    full_name = models.CharField(max_length=255, verbose_name=_('ФИО'))

    def __str__(self):
        return f"ЭЦП {self.full_name}"

    class Meta:
        verbose_name = _('ЭЦП')
        verbose_name_plural = _('ЭЦП')

class UTMRSAKeys(LicenseBaseModel):
    key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Ключ')
    )

    def __str__(self):
        return f"УТМ RSA Ключ {self.key}"

    class Meta:
        verbose_name = _('УТМ RSA Ключ')
        verbose_name_plural = _('УТМ RSA Ключи')

class MCD(LicenseBaseModel):
    mcd_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('ID')
    )

    def __str__(self):
        return f"МЧД {self.mcd_id}"

    class Meta:
        verbose_name = _('МЧД')
        verbose_name_plural = _('МЧД')

class USAIS(LicenseBaseModel):
    key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Ключ')
    )

    def __str__(self):
        return f"ЕГАИС {self.key}"

    class Meta:
        verbose_name = _('ЕГАИС')
        verbose_name_plural = _('ЕГАИС')

class HonestSign(LicenseBaseModel):
    key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Ключ')
    )

    def __str__(self):
        return f"Честный знак {self.key}"

    class Meta:
        verbose_name = _('Честный знак')
        verbose_name_plural = _('Честные знаки')

class OFD(LicenseBaseModel):
    reg_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Регистрационный номер')
    )

    def __str__(self):
        return f"ОФД {self.reg_number}"

    class Meta:
        verbose_name = _('ОФД')
        verbose_name_plural = _('ОФД')

class RemoteAccess(TimestampModel):
    class AccessType(models.TextChoices):
        TEAMVIEWER = 'teamviewer', _('TeamViewer')
        ANYDESK = 'anydesk', _('AnyDesk')
        RDP = 'rdp', _('Remote Desktop')
        RUSTDESK = 'rustdesk', _('RustDesk')
        AWESUN = 'awesun', _('AweSun')
        OTHER = 'other', _('Другое')
        
    name = models.CharField(
        max_length=100,
        choices=AccessType.choices,
        default=AccessType.TEAMVIEWER,
        verbose_name=_('Тип доступа')
    )
    access_id = models.CharField(max_length=100, verbose_name=_('ID'))
    password = models.CharField(max_length=100, verbose_name=_('Пароль удаленного доступа'))
    comments = models.TextField(blank=True, null=True, verbose_name=_('Комментарии'))
    computer = models.ForeignKey(
        Computer,
        on_delete=models.CASCADE,
        related_name='remote_accesses',
        verbose_name=_('Компьютер')
    )

    def __str__(self):
        return f"{self.get_name_display()} ({self.access_id})"

    class Meta:
        verbose_name = _('Удаленный доступ')
        verbose_name_plural = _('Удаленные доступы')
        ordering = ['computer', 'name']
        unique_together = ['name', 'access_id', 'computer']

class LicenseNotification(TimestampModel):
    class NotificationType(models.TextChoices):
        EXPIRING_SOON_30 = 'expiring_soon_30', _('Скоро истекает (30 дней)')
        EXPIRING_SOON_7 = 'expiring_soon_7', _('Скоро истекает (7 дней)')
        EXPIRING_SOON_5 = 'expiring_soon_5', _('Скоро истекает (5 дней)')
        EXPIRING_SOON_1 = 'expiring_soon_1', _('Скоро истекает (1 день)')
        EXPIRED = 'expired', _('Истёк срок')

    notification_type = models.CharField(
        max_length=25,
        choices=NotificationType.choices,
        default=NotificationType.EXPIRING_SOON_7
    )

    license_type = models.CharField(max_length=100)
    license_id = models.PositiveIntegerField()

    computer = models.ForeignKey(
        'Computer',
        on_delete=models.CASCADE,
        related_name='license_notifications',
        verbose_name=_('Компьютер'),
        null=True,
        blank=True,
    )
    legal_entity = models.ForeignKey(
        LegalEntity,
        on_delete=models.CASCADE,
        related_name='license_notifications',
        verbose_name=_('Юридическое лицо'),
        null=True,
        blank=True,
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='license_notifications',
        verbose_name=_('Адрес'),
        null=True,
        blank=True,
    )
    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        related_name='license_notifications',
        verbose_name=_('Сеть'),
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='license_notifications',
        verbose_name=_('Город'),
        null=True,
        blank=True,
    )
    expiration_date = models.DateField(null=True, blank=True)
    days_left = models.PositiveIntegerField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    user_notified = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_notification_type_display()} ({self.license_type} ID: {self.license_id})"


    def get_license_object(self):
        # model = globals().get(self.license_type)
        # if model and issubclass(model, LicenseBaseModel):
        #     return model.objects.filter(id=self.license_id).first()
        # return None
        from django.apps import apps
        try:
            model_class = apps.get_model('licen', self.license_type)
            if model_class and issubclass(model_class, LicenseBaseModel):
                return model_class.objects.filter(id=self.license_id).first()
        except (LookupError, TypeError):
            return None
        return None
    
    def send_to_user(self, user):
        """
        Отправляет уведомление конкретному пользователю
        """
        from .utils.email_notifications import send_license_notification
        success = send_license_notification(self, user)
        if success:
            self.is_sent = True
            self.user_notified = user
            self.save()
        return success
    
    def get_absolute_url(self):
        return reverse('license-detail', args=[str(self.pk)])
    
    # def send_to_admins(self):
    #     from django.contrib.auth import get_user_model
    #     from django.apps import apps

    #     User = get_user_model()
    #     UserProfile = apps.get_model('licen', 'UserProfile')

    #     admins = User.objects.filter(profile__role=UserProfile.Role.ADMIN, is_active=True)

    #     results = []
    #     for admin in admins:
    #         results.append(self.send_to_user(admin))
    #     return any(results)

    # licen/models.py

    def send_to_admins(self):
        from django.contrib.auth import get_user_model
        from licen.models import UserProfile

        User = get_user_model()

        admins = User.objects.filter(profile__role=UserProfile.Role.ADMIN, is_active=True)

        results = []
        for admin in admins:
            results.append(self.send_to_user(admin))
        return any(results)
    
    class Meta:
        verbose_name = _('Уведомление о лицензии')
        verbose_name_plural = _('Уведомления о лицензиях')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_sent']),
            models.Index(fields=['expiration_date']),
            models.Index(fields=['notification_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['license_type', 'license_id', 'notification_type'],
                name='unique_notification_per_license'
            )
        ]

class UserProfile(TimestampModel):
    class Role(models.TextChoices):
        JOURNALIST = 'moderator', _('Пользователь')
        MODERATOR = 'journalist', _('Бухгалтер') 
        ADMIN = 'admin', _('Администратор')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('Пользователь'))
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.JOURNALIST, verbose_name=_('Роль пользователя'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Телефон'))
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Отдел'))

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')


# Можно добавить сигнал для создания профиля при создании пользователя:

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# licen/models.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from licen.tasks import check_license_expirations

@receiver(post_save, sender=FiscalNumber)
def on_license_saved(sender, instance, **kwargs):
    check_license_expirations.delay()

@receiver(post_save, sender=CryptoPro)
def on_fiscal_number_saved(sender, instance, **kwargs):
    check_license_expirations.delay()

@receiver(post_save, sender=ECP)
def on_ecp_saved(sender, instance, created, **kwargs):
    check_license_expirations.delay()

@receiver(post_save, sender=UTMRSAKeys)
def on_ecp_saved(sender, instance, created, **kwargs):
    check_license_expirations.delay()

@receiver(post_save, sender=MCD)
def on_ecp_saved(sender, instance, created, **kwargs):
    check_license_expirations.delay()

@receiver(post_save, sender=HonestSign)
def on_ecp_saved(sender, instance, created, **kwargs):
    check_license_expirations.delay()

@receiver(post_save, sender=OFD)
def on_ecp_saved(sender, instance, created, **kwargs):
    check_license_expirations.delay()

@receiver(post_save, sender=USAIS)
def on_ecp_saved(sender, instance, created, **kwargs):
    check_license_expirations.delay()

# licen/models.py

# Явно импортируем все модели, чтобы они были доступны через apps.get_model()
# Или просто убедись, что LicenseBaseModel определена в этом файле
# licen/models.py

# Явно импортируем все модели, чтобы они были доступны через get_model()
__all__ = ['LicenseBaseModel', 'CryptoPro', 'FiscalNumber', 'ECP', 'UTMRSAKeys', 'MCD', 'OFD', 'HonestSign', 'USAIS']

# licen/models.py

...

# Явно импортируем все модели, чтобы __subclasses__() работало
from .models import CryptoPro, FiscalNumber, ECP, UTMRSAKeys, MCD, OFD, HonestSign, USAIS

import licen.models