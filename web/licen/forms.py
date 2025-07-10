from django import forms
from .models import (
    City, LegalEntity, Network, Address, Computer, RemoteAccess,
    CryptoPro, FiscalNumber, ECP, UTMRSAKeys, MCD, HonestSign,
    OFD, USAIS, MobileOperator, InternetProvider, WiFi, RouterAdminPanel,
    PersonalAccountMobileOperator, PersonalAccountInternetProvider, UserProfile,
    ContactPerson
)
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UsernameField

from django.utils.translation import gettext_lazy as _

# === Регистрация пользователя ===
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text=_('Обязательно. Например: user@example.com')
    )

    username = UsernameField(
        label="Имя пользователя",
        help_text="Обязательное поле. Только латинские буквы, цифры и символы: @/./+/-/_"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        help_texts = {
            'username': _('Не более 150 символов. Только латинские буквы, цифры и символы (@, ., +, -, _).'),
        }
        error_messages = {
            'username': {
                'unique': _('Пользователь с таким именем уже существует')
            }
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            return username

        # Проверяем, есть ли в имени русские буквы
        cyrillic_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        if any(char.lower() in cyrillic_chars for char in username):
            raise forms.ValidationError("Имя пользователя не должно содержать русские буквы.")

        return username

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].help_text = _('Пароль должен быть сложным')
        self.fields['password2'].help_text = _('Повторите пароль')

class UserForm(forms.ModelForm):
    username = forms.CharField(
        label="Имя пользователя",
        help_text="Только латинские буквы, цифры и символы: @/./+/-/_"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        help_texts = {
            'username': _('Не более 150 символов. Только буквы, цифры и @/./+/-/_'),
            'email': _('Обязательно. Например: user@example.com'),
        }
        error_messages = {
            'username': {
                'unique': _('Пользователь с таким именем уже существует')
            },
            'email': {
                'unique': _('Этот email уже используется')
            }
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            return username

        cyrillic_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        if any(char.lower() in cyrillic_chars for char in username):
            raise forms.ValidationError("Имя пользователя не должно содержать русские буквы.")

        return username

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'department']
        help_texts = {
            'role': _('Выберите роль пользователя'),
            'phone': _('Формат: +7 (XXX) XXX-XX-XX'),
            'department': _('Например: Отдел продаж'),
        }
        error_messages = {
            'phone': {
                'invalid': _('Введите корректный телефонный номер')
            }
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['department'].widget.attrs.update({'class': 'form-control'})

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'

# === Города ===
class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Москва'}),
        }
        labels = {
            'name': _('Название города'),
        }
        help_texts = {
            'name': _('Введите полное название города'),
        }

class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = ContactPerson
        fields = '__all__'
        widgets = {
            'city': forms.Select(attrs={'class': 'form-select'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+79991234567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'user@example.com'}),
            'email_password': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
        }
        labels = {
            'full_name': _('ФИО'),
            'position': _('Должность'),
            'phone_number': _('Номер телефона'),
            'email': _('Email'),
            'email_password': _('Пароль от почты'),
        }
        help_texts = {
            'email_password': _('Используйте безопасный пароль или хешируйте его перед сохранением')
        }

# === Юрлица ===
class LegalEntityForm(forms.ModelForm):
    class Meta:
        model = LegalEntity
        fields = ['name', 'comments', 'city']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ООО Тестовая компания'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Название сети'),
            'comments': _('Комментарии'),
            'city': _('Город'),
        }


# === Сети ===
class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Сеть Москва'}),
            'inn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ИНН 10-12 цифр'}),
            'legal_entity': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': _('Юридическое лицо'),
            'inn': _('ИНН'),
            'legal_entity': _('Наименование сети'),
            'comments': _('Комментарии'),
        }
        help_texts = {
            'name': _('Введите уникальное имя сети'),
            'inn': _('Введите 10-12 цифр ИНН'),
        }
        error_messages = {
            'inn': {
                'unique': _('Юрлицо с таким ИНН уже существует')
            }
        }


# === Адреса ===
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'ул. Ленина, д. 1'}),
            'network': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'address': _('Адрес'),
            'network': _('Юридическое лицо'),
            'comments': _('Комментарии'),
        }
        help_texts = {
            'address': _('Полный адрес установки'),
        }


# === Компьютеры ===
class ComputerForm(forms.ModelForm):
    class Meta:
        model = Computer
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: PC-001'}),
            'ipv4_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.1'}),
            'mac_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AA:BB:CC:DD:EE:FF'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Имя компьютера'),
            'ipv4_address': _('IPv4 адрес'),
            'mac_address': _('MAC-адрес'),
            'address': _('Адрес'),
            'comments': _('Комментарии'),
        }
        help_texts = {
            'mac_address': _('Формат: AA:BB:CC:DD:EE:FF'),
        }
        error_messages = {
            'ipv4_address': {
                'unique_together': _('Этот IP-адрес уже используется на этом адресе'),
            },
            'mac_address': {
                'invalid': _('Введите корректный MAC-адрес'),
            }
        }


# === Удаленный доступ ===
class RemoteAccessForm(forms.ModelForm):
    class Meta:
        model = RemoteAccess
        fields = '__all__'
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'access_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID доступа'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Тип удаленного доступа'),
            'access_id': _('ID доступа'),
            'password': _('Пароль'),
            'computer': _('Компьютер'),
            'comments': _('Комментарии'),
        }
        help_texts = {
            'password': _('Пароль будет скрыт при просмотре'),
        }


# === Фискальные номера ===
class FiscalNumberForm(forms.ModelForm):
    class Meta:
        model = FiscalNumber
        fields = '__all__'
        widgets = {
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'zn': forms.TextInput(attrs={'class': 'form-control'}),
            'reg_number': forms.TextInput(attrs={'class': 'form-control'}),
            'fn': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'model': _('Модель'),
            'zn': _('ЗН'),
            'reg_number': _('Регистрационный номер'),
            'fn': _('ФН'),
            'start_date': _('Дата начала действия'),
            'end_date': _('Дата окончания действия'),
            'address': _('Адрес'),
        }
        help_texts = {
            'reg_number': _('Пример: 0123456789'),
        }
        error_messages = {
            'reg_number': {
                'unique': _('ФН с таким регистрационным номером уже существует')
            },
            'fn': {
                'unique': _('ФН уже используется')
            }
        }

# === КриптоПро ===
class CryptoProForm(forms.ModelForm):
    class Meta:
        model = CryptoPro
        fields = '__all__'
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ключ лицензии'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'key': _('Ключ'),
            'start_date': _('Дата начала действия'),
            'end_date': _('Дата окончания действия'),
            'computer': _('Компьютер'),
        }
        help_texts = {
            'key': _('Введите ключ CryptoPro без пробелов'),
        }
        error_messages = {
            'key': {
                'unique': _('Ключ уже используется')
            }
        }

# === ЭЦП ===
class ECPForm(forms.ModelForm):
    class Meta:
        model = ECP
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': _('ФИО сотрудника'),
            'start_date': _('Дата начала действия'),
            'end_date': _('Дата окончания действия'),
        }
        help_texts = {
            'full_name': _('Как указано в сертификате'),
        }

# === УТМ RSA ключи ===
class UTMRSAKeysForm(forms.ModelForm):
    class Meta:
        model = UTMRSAKeys
        fields = '__all__'
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RSA-KEY-123456'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'key': _('Ключ'),
            'start_date': _('Дата начала действия'),
            'end_date': _('Дата окончания действия'),
            'computer': _('Компьютер'),
        }
        help_texts = {
            'key': _('Пример: RSA-KEY-123456'),
        }
        error_messages = {
            'key': {
                'unique': _('Ключ уже существует')
            }
        }

# === МЧД ===
class MCDForm(forms.ModelForm):
    class Meta:
        model = MCD
        fields = '__all__'
        widgets = {
            'mcd_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MCD-12345'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'mcd_id': _('Идентификатор МЧД'),
        }
        help_texts = {
            'mcd_id': _('Пример: MCD-123456'),
        }
        error_messages = {
            'mcd_id': {
                'unique': _('МЧД с таким ID уже существует')
            }
        }

# === ЕГАИС ===
class USAISForm(forms.ModelForm):
    class Meta:
        model = USAIS
        fields = '__all__'
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HS-123456'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'key': _('Ключ'),
        }
        help_texts = {
            'key': _('Пример: HS-123456'),
        }
        error_messages = {
            'key': {
                'unique': _('Лицензия с таким ключом уже существует')
            }
        }

# === Честный Знак ===
class HonestSignForm(forms.ModelForm):
    class Meta:
        model = HonestSign
        fields = '__all__'
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HS-123456'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'key': _('Ключ'),
        }
        help_texts = {
            'key': _('Пример: HS-123456'),
        }
        error_messages = {
            'key': {
                'unique': _('Лицензия с таким ключом уже существует')
            }
        }


# === ОФД ===
class OFDForm(forms.ModelForm):
    class Meta:
        model = OFD
        fields = '__all__'
        widgets = {
            'reg_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OFD-12345'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'computer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'reg_number': _('Регистрационный номер'),
        }
        help_texts = {
            'reg_number': _('Пример: OFD-123456'),
        }
        error_messages = {
            'reg_number': {
                'unique': _('ОФД с таким рег. номером уже существует')
            }
        }


# === Мобильные операторы ===
class MobileOperatorForm(forms.ModelForm):
    class Meta:
        model = MobileOperator
        fields = '__all__'
        widgets = {
            'operator': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+79001234567'}),
            'employee_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван'}),
            'contract': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Договор #123'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'phone_number': _('Номер телефона'),
            'employee_name': _('ФИО сотрудника'),
            'contract': _('Договор'),
            'address': _('Адрес'),
        }
        help_texts = {
            'phone_number': _('Пример: +79001234567'),
        }
        error_messages = {
            'phone_number': {
                'unique': _('Номер телефона уже используется')
            }
        }


# === Интернет-провайдеры ===
class InternetProviderForm(forms.ModelForm):
    class Meta:
        model = InternetProvider
        fields = '__all__'
        widgets = {
            'provider': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'speed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '100 Mbps'}),
            'contract': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'contract': _('Договор'),
            'price': _('Стоимость'),
            'speed': _('Скорость'),
            'address': _('Адрес'),
        }
        help_texts = {
            'price': _('В рублях за месяц'),
        }
        error_messages = {
            'contract': {
                'unique': _('Рег. номер уже существует')
            }
        }


# === WiFi ===
class WiFiForm(forms.ModelForm):
    class Meta:
        model = WiFi
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WiFi-Office'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency_band': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('SSID'),
            'password': _('Пароль'),
            'frequency_band': _('Диапазон частот'),
            'address': _('Адрес'),
        }
        help_texts = {
            'password': _('Пароль будет скрыт при просмотре'),
        }
        error_messages = {
            'name': {
                'unique': _('WiFi с таким SSID уже существует для этого адреса')
            }
        }


# === Роутер ===
class RouterAdminPanelForm(forms.ModelForm):
    class Meta:
        model = RouterAdminPanel
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Router-1'}),
            'login': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'admin'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.1'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Название панели'),
            'login': _('Логин'),
            'password': _('Пароль'),
            'ip_address': _('IP-адрес роутера'),
            'address': _('Адрес'),
        }
        help_texts = {
            'ip_address': _('Например: 192.168.1.1'),
        }
        error_messages = {
            'ip_address': {
                'unique': _('IP-адрес уже используется')
            }
        }


# === Личный кабинет мобильного оператора ===
class PersonalAccountMobileOperatorForm(forms.ModelForm):
    class Meta:
        model = PersonalAccountMobileOperator
        fields = '__all__'
        widgets = {
            'login': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'user123'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.100'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Select(attrs={'class': 'form-control'}),
            'mobile_operator': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'login': _('Логин'),
            'password': _('Пароль'),
            'ip_address': _('IP-адрес'),
            'mobile_operator': _('Мобильный оператор'),
        }
        help_texts = {
            'ip_address': _('Если есть связь через IP'),
        }
        error_messages = {
            'login': {
                'unique': _('Логин уже используется')
            }
        }

    def clean_login(self):
        login = self.cleaned_data.get("login")
        if not login:
            return login

        cyrillic_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        if any(char.lower() in cyrillic_chars for char in login):
            raise forms.ValidationError("Логин не должен содержать русские буквы.")
        return login


# === Личный кабинет интернет-провайдера ===
class PersonalAccountInternetProviderForm(forms.ModelForm):
    class Meta:
        model = PersonalAccountInternetProvider
        fields = '__all__'
        widgets = {
            'login': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'user123'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.100'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Select(attrs={'class': 'form-control'}),
            'internet_provider': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'login': _('Логин'),
            'password': _('Пароль'),
            'ip_address': _('IP-адрес'),
            'internet_provider': _('Интернет-провайдер'),
        }
        help_texts = {
            'ip_address': _('Если есть привязка к IP'),
        }
        error_messages = {
            'login': {
                'unique': _('Логин уже используется')
            }
        }