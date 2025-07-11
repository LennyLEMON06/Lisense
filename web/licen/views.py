from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import City, ContactPerson,LegalEntity, Network, Address, Computer, RemoteAccess, CryptoPro, FiscalNumber, ECP, UTMRSAKeys, MCD, HonestSign, USAIS, OFD, LicenseNotification, MobileOperator, InternetProvider, WiFi, RouterAdminPanel, PersonalAccountInternetProvider, PersonalAccountMobileOperator
from .forms import RegisterForm, CityForm, ContactPersonForm, LegalEntityForm, NetworkForm, AddressForm, ComputerForm, RemoteAccessForm, FiscalNumberForm, CryptoProForm, ECPForm, UTMRSAKeysForm, MCDForm, HonestSignForm, USAISForm, OFDForm, MobileOperatorForm, InternetProviderForm, WiFiForm, RouterAdminPanelForm, PersonalAccountInternetProviderForm, PersonalAccountMobileOperatorForm, UserForm, UserProfileForm, CustomPasswordChangeForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.forms import ModelForm
from django.utils import timezone
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from licen.models import UserProfile, LicenseNotification, User
from licen.tasks import check_license_expirations
from django.contrib.auth import logout
from licen.decorators import role_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.forms import SetPasswordForm

admin = UserProfile.Role.ADMIN
bookkeeper = UserProfile.Role.MODERATOR
user = UserProfile.Role.JOURNALIST

def login_view(request):
    # ✅ Если пользователь уже авторизован — сразу редирект
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Перенаправьте на домашнюю страницу после входа
    else:
        form = AuthenticationForm()
    return render(request, 'licen/log/login.html', {'form': form})

def register_view(request):
    # ✅ Если пользователь уже авторизован — сразу редирект
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Перенаправление на страницу входа после успешной регистрации
    else:
        form = RegisterForm()

    return render(request, 'licen/log/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

def password_reset_done(request):
    return render(request, 'licen/log/password_reset_done.html', {
        'title': 'Письмо отправлено'
    })

def password_reset_request(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        associated_users = User.objects.filter(username=username_or_email) or User.objects.filter(email=username_or_email)
        
        if associated_users.exists():
            for user in associated_users:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                subject = "Сброс пароля"
                message = render_to_string('licen/log/password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                plain_message = f"Перейдите по ссылке: {reset_link}"

                send_mail(subject, plain_message, 'ksenia.boul@yandex.ru', [user.email], html_message=message)

        return redirect('password_reset_done')

    return render(request, 'licen/log/password_reset_form.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'licen/log/password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'licen/log/password_reset_invalid.html')

@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Если профиль не создан — создаём его
        profile = UserProfile.objects.create(user=user)

    # Получаем уведомления о лицензиях
    license_notifications = LicenseNotification.objects.filter(
        user_notified=request.user
    ).order_by('-expiration_date')[:5]

    # Проверяем роль пользователя
    if profile.role == UserProfile.Role.ADMIN:
        # Для администраторов показываем список всех пользователей
        users = User.objects.all()
        return render(request, 'licen/profile/profile.html', {
            'user': user,
            'profile': profile,
            'users': users,
            'title': f"Профиль: {user.username}"
        })

    return render(request, 'licen/profile/profile.html', {
        'user': user,
        'profile': profile,
        'license_notifications': license_notifications,
        'title': f"Профиль: {user.username}"
    })

@role_required(admin)
@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, id=pk)
    profile = user.profile
    return render(request, 'licen/profile/user_detail.html', {
        'user': user,
        'profile': profile,
        'title': f"Профиль пользователя: {user.username}"
    })

@role_required(admin)
@login_required
def user_update(request, pk):
    user = get_object_or_404(User, id=pk)
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(reverse('user-detail', args=[user.id]))
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'licen/profile/user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': f"Редактировать профиль {user.username}",
    })

@role_required(admin)
@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('profile')
    return render(request, 'licen/profile/user_confirm_delete.html', {
        'user': user,
        'title': f"Удаление пользователя {user.username}"
    })

class ChangePasswordView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'licen/profile/change_password.html'
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_id = self.kwargs.get('user_id')
        if user_id:
            target_user = User.objects.get(id=user_id)
            if not self.request.user.is_superuser and self.request.user.profile.role != 'admin':
                raise PermissionDenied("У вас нет прав на это действие")
        return kwargs

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        if user_id:
            return User.objects.get(id=user_id)
        return self.request.user

    def get_success_url(self):
        # Если пришёл как админ — можешь вернуться к профилю пользователя
        user_id = self.kwargs.get('user_id')
        if user_id and self.request.user.profile.role == 'admin':
            return reverse_lazy('user-detail', kwargs={'pk': user_id})
        return reverse_lazy('profile')

@login_required
def search_results(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Приведём запрос к нижнему регистру для сравнения
        query_lower = query.lower()

        # Города
        for city in City.objects.all():
            if query_lower in (city.name or '').lower():
                results.append({
                    'type': 'Город',
                    'name': city.name,
                    'url': reverse('city-detail', args=[city.id])
                })

        # Сети
        for entity in LegalEntity.objects.all():
            if query_lower in entity.name.lower():
                results.append({
                    'type': 'Сеть',
                    'name': f"{entity.name}",
                    'url': reverse('legal-entity-detail', args=[entity.id])
                })

        # Юрлица — name или inn
        for network in Network.objects.all():
            if query_lower in network.name.lower() or query_lower in (network.inn or '').lower():
                results.append({
                    'type': 'Юрлицо',
                    'name': f"{network.name} (ИНН: {network.inn})",
                    'url': reverse('network-detail', args=[network.id])
                })

        # Адреса
        for address in Address.objects.all():
            if query_lower in (address.address or '').lower():
                results.append({
                    'type': 'Адрес',
                    'name': address.address,
                    'url': reverse('address-detail', args=[address.id])
                })

        # Компьютеры
        for computer in Computer.objects.all():
            if query_lower in (computer.name or '').lower() or query_lower in (computer.ipv4_address or '').lower():
                results.append({
                    'type': 'Компьютер',
                    'name': f"{computer.name} ({computer.ipv4_address})",
                    'url': reverse('computer-detail', args=[computer.id])
                })

        # Мобильные операторы
        for mobile_operator in MobileOperator.objects.all():
            if query_lower in (mobile_operator.operator.name or '').lower() or query_lower in (mobile_operator.phone_number or '').lower():
                results.append({
                    'type': 'Мобильный оператор',
                    'name': f"{mobile_operator.operator.name} — {mobile_operator.phone_number}",
                    'url': reverse('mobile-operator-detail', args=[mobile_operator.id])
                })

        # Интернет-провайдеры
        for internet_provider in InternetProvider.objects.all():
            if query_lower in (internet_provider.provider.name or '').lower() or query_lower in (internet_provider.speed or '').lower():
                results.append({
                    'type': 'Интернет-провайдер',
                    'name': f"{internet_provider.provider.name} — {internet_provider.speed}",
                    'url': reverse('internet-provider-detail', args=[internet_provider.id])
                })

        # WiFi
        for wifi in WiFi.objects.all():
            if query_lower in (wifi.name or '').lower():
                results.append({
                    'type': 'WiFi',
                    'name': f"{wifi.name} — {wifi.get_frequency_band_display()}",
                    'url': reverse('wifi-detail', args=[wifi.id])
                })

        # Роутеры
        for router in RouterAdminPanel.objects.all():
            if query_lower in (router.name or '').lower() or query_lower in (router.ip_address or '').lower():
                results.append({
                    'type': 'Роутер',
                    'name': f"{router.name} — {router.ip_address}",
                    'url': reverse('router-admin-panel-detail', args=[router.id])
                })

        # Фискальные номера
        for fiscal in FiscalNumber.objects.all():
            if query_lower in (fiscal.reg_number or '').lower() or query_lower in (fiscal.zn or '').lower():
                results.append({
                    'type': 'ФН',
                    'name': f"ФН: {fiscal.reg_number} ({fiscal.zn})",
                    'url': reverse('fiscal-number-detail-one', args=[fiscal.id])
                })

        # CryptoPro
        for crypto in CryptoPro.objects.all():
            if query_lower in (crypto.key or '').lower():
                results.append({
                    'type': 'CryptoPro',
                    'name': f"Ключ: {crypto.key}",
                    'url': reverse('crypto-pro-detail', args=[crypto.id])
                })

        # ЭЦП
        for ecp in ECP.objects.all():
            if query_lower in (ecp.full_name or '').lower():
                results.append({
                    'type': 'ЭЦП',
                    'name': f"ЭЦП: {ecp.full_name}",
                    'url': reverse('ecp-detail', args=[ecp.id])
                })

        # УТМ RSA ключи
        for utm_rsa in UTMRSAKeys.objects.all():
            if query_lower in (utm_rsa.key or '').lower():
                results.append({
                    'type': 'УТМ RSA',
                    'name': f"УТМ RSA: {utm_rsa.key}",
                    'url': reverse('utm-rsa-keys-detail', args=[utm_rsa.id])
                })

        # МЧД
        for mcd in MCD.objects.all():
            if query_lower in (mcd.mcd_id or '').lower():
                results.append({
                    'type': 'МЧД',
                    'name': f"Логин: {mcd.mcd_id}",
                    'url': reverse('mcd-detail', args=[mcd.id])
                })

        # Честный знак
        for honest_sign in HonestSign.objects.all():
            if query_lower in (honest_sign.key or '').lower():
                results.append({
                    'type': 'Честный знак',
                    'name': f"Честный Знак: {honest_sign.key}",
                    'url': reverse('honest-sign-detail', args=[honest_sign.id])
                })

        # ОФД
        for ofd in OFD.objects.all():
            if query_lower in (ofd.reg_number or '').lower():
                results.append({
                    'type': 'ОФД',
                    'name': f"ОФД: {ofd.reg_number}",
                    'url': reverse('ofd-detail', args=[ofd.id])
                })

    return render(request, 'licen/search_results.html', {
        'query': query,
        'results': results,
        'title': f"Результаты поиска для '{query}'"
    })

# ====== Города ======
@login_required
def city_list(request):
    cities = City.objects.all().order_by('name')
    return render(request, 'licen/city/city_list.html', {'cities': cities})

@login_required
def city_detail(request, pk):
    city = get_object_or_404(City, pk=pk)
    legal_entities = LegalEntity.objects.filter(city=city)

    return render(request, 'licen/city/city_detail.html', {
        'city': city,
        'legal_entities': legal_entities
    })

@role_required(admin, bookkeeper)
@login_required
def legal_entity_create_for_city(request, city_id):
    city = get_object_or_404(City, id=city_id)

    if request.method == 'POST':
        form = LegalEntityForm(request.POST)
        if form.is_valid():
            entity = form.save(commit=False)
            entity.city = city
            entity.save()
            return redirect(reverse('city-detail', kwargs={'pk': city.id}))
    else:
        form = LegalEntityForm()

    return render(request, 'licen/legal_entity/legal_entity_form.html', {
        'form': form,
        'city': city,  
        'title': f"Добавить юридическое лицо для города «{city.name}»"
    })

@role_required(admin, bookkeeper)
@login_required
def city_create(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('city-list'))
    else:
        form = CityForm()

    return render(request, 'licen/city/city_form.html', {
        'form': form,
        'title': 'Добавить город'
    })

@role_required(admin, bookkeeper)
@login_required
def city_update(request, pk):
    city = get_object_or_404(City, pk=pk)

    if request.method == 'POST':
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            return redirect(reverse('city-list'))
    else:
        form = CityForm(instance=city)

    return render(request, 'licen/city/city_form.html', {
        'form': form,
        'title': f"Редактировать {city.name}"
    })

@role_required(admin, bookkeeper)
@login_required
def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)

    if request.method == 'POST':
        city.delete()
        return redirect(reverse('city-list'))

    return render(request, 'licen/city/city_confirm_delete.html', {
        'object': city
    })

# ====== Почты ======
@login_required
def contact_person_list(request):
    persons = ContactPerson.objects.all().select_related('city')
    return render(request, 'licen/contact_person/contact_person_list.html', {
        'persons': persons,
        'title': 'Контактные лица'
    })

@login_required
def contact_person_detail(request, pk):
    person = get_object_or_404(ContactPerson, id=pk)
    return render(request, 'licen/contact_person/contact_person_detail.html', {
        'person': person,
        'title': f"Контактное лицо: {person.full_name}"
    })

@role_required(admin, bookkeeper)
@login_required
def contact_person_create(request):
    if request.method == 'POST':
        form = ContactPersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact-person-list')
    else:
        form = ContactPersonForm()

    return render(request, 'licen/contact_person/contact_person_form.html', {
        'form': form,
        'title': 'Добавить контактное лицо'
    })

@role_required(admin, bookkeeper)
@login_required
def contact_person_update(request, pk):
    person = get_object_or_404(ContactPerson, id=pk)

    if request.method == 'POST':
        form = ContactPersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect('contact-person-detail', pk=person.id)
    else:
        form = ContactPersonForm(instance=person)

    return render(request, 'licen/contact_person/contact_person_form.html', {
        'form': form,
        'title': f"Редактировать: {person.full_name}"
    })

@role_required(admin, bookkeeper)
@login_required
def contact_person_delete(request, pk):
    person = get_object_or_404(ContactPerson, id=pk)

    if request.method == 'POST':
        person.delete()
        return redirect('contact-person-list')

    return render(request, 'licen/contact_person/contact_person_confirm_delete.html', {
        'object': person
    })

# ====== Юр. лица ======
@login_required
def legal_entity_list(request):
    legal_entities = LegalEntity.objects.all().order_by('name')
    return render(request, 'licen/legal_entity/legal_entity_list.html', {'legal_entities': legal_entities})

@login_required
def legal_entity_detail(request, pk):
    legal_entity = get_object_or_404(LegalEntity, id=pk)
    networks = legal_entity.networks.all().order_by('name')  # ← загружаем все сети этого юрлица

    return render(request, 'licen/legal_entity/legal_entity_detail.html', {
        'legal_entity': legal_entity,
        'city': legal_entity.city,
        'networks': networks,
        'title': f"Сеть: {legal_entity.name}"
    })

@role_required(admin, bookkeeper)
@login_required
def network_create_for_legal_entity(request, legal_entity_id):
    legal_entity = get_object_or_404(LegalEntity, id=legal_entity_id)

    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            network = form.save(commit=False)
            network.legal_entity = legal_entity
            network.save()
            return redirect('legal-entity-detail', pk=legal_entity.id)
    else:
        form = NetworkForm()

    return render(request, 'licen/network/network_form.html', {
        'form': form,
        'title': f"Добавить юридическое лицо для «{legal_entity.name}»",
        'legal_entity': legal_entity  # ← чтобы использовать в шаблоне
    })

@login_required
def legal_entity_list_for_network(request, network_id):
    network = get_object_or_404(Network, id=network_id)
    legal_entities = LegalEntity.objects.filter(networks=network)
    return render(request, 'licen/legal_entity/legal_entity_list_for_network.html', {
        'legal_entities': legal_entities,
        'network': network
    })

@role_required(admin, bookkeeper)
@login_required
def legal_entity_create(request):
    if request.method == 'POST':
        form = LegalEntityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('legal-entity-list'))
    else:
        form = LegalEntityForm()

    return render(request, 'licen/legal_entity/legal_entity_form.html', {
        'form': form,
        'title': 'Добавить сеть'
    })

@role_required(admin, bookkeeper)
@login_required
def legal_entity_update(request, pk):
    legal_entity = get_object_or_404(LegalEntity, pk=pk)
    city = legal_entity.city

    if request.method == 'POST':
        form = LegalEntityForm(request.POST, instance=legal_entity)
        if form.is_valid():
            form.save()
            return redirect(reverse('legal-entity-list'))
    else:
        form = LegalEntityForm(instance=legal_entity)

    return render(request, 'licen/legal_entity/legal_entity_form.html', {
        'form': form,
        'city': city,
        'title': f"Редактировать {legal_entity.name}"
    })

@role_required(admin, bookkeeper)
@login_required
def legal_entity_delete(request, pk):
    legal_entity = get_object_or_404(LegalEntity, pk=pk)

    if request.method == 'POST':
        legal_entity.delete()
        return redirect(reverse('legal-entity-list'))

    return render(request, 'licen/legal_entity/legal_entity_confirm_delete.html', {
        'object': legal_entity
    })


# ====== Сети ======
@login_required
def network_list(request):
    networks = Network.objects.all().order_by('name')
    return render(request, 'licen/network/network_list.html', {'networks': networks})

@login_required
def network_detail(request, pk):
    network = get_object_or_404(Network, id=pk)
    addresses = network.addresses.all().order_by('address')  # ← загружаем адреса для этой сети
    
    return render(request, 'licen/network/network_detail.html', {
        'network': network,
        'addresses': addresses,
        'city': network.legal_entity.city,
        'legal_entity': network.legal_entity,
        'title': f"Юридическое лицо: {network.name}"
    })

@role_required(admin, bookkeeper)
@login_required
def address_create_for_network(request, network_id):
    from licen.models import Network, Address
    from licen.forms import AddressForm

    network = get_object_or_404(Network, id=network_id)

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.network = network
            address.save()
            return redirect(reverse('network-detail', kwargs={'pk': network.id}))
    else:
        form = AddressForm()

    return render(request, 'licen/address/address_form.html', {
        'form': form,
        'title': f"Добавить адрес для сети «{network.name}»",
        'network': network
    })

@login_required
def network_list_for_city(request, city_id):
    city = get_object_or_404(City, id=city_id)
    networks = Network.objects.filter(legal_entity__city=city)
    return render(request, 'licen/network/network_list_for_city.html', {'networks': networks, 'city': city})

@role_required(admin, bookkeeper)
@login_required
def network_create(request):
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('network-list'))
    else:
        form = NetworkForm()

    return render(request, 'licen/network/network_form.html', {
        'form': form,
        'title': 'Добавить юридическое лицо'
    })

@role_required(admin, bookkeeper)
@login_required
def network_update(request, pk):
    network = get_object_or_404(Network, pk=pk)
    legal_entity = network.legal_entity

    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()
            return redirect(reverse('network-list'))
    else:
        form = NetworkForm(instance=network)

    return render(request, 'licen/network/network_form.html', {
        'form': form,
        'legal_entity': legal_entity,
        'title': f"Редактировать {network.name}"
    })

@role_required(admin, bookkeeper)
@login_required
def network_delete(request, pk):
    network = get_object_or_404(Network, pk=pk)

    if request.method == 'POST':
        network.delete()
        return redirect(reverse('network-list'))

    return render(request, 'licen/network/network_confirm_delete.html', {
        'object': network
    })


# ====== Адреса ======
@login_required
def address_list(request):
    addresses = Address.objects.all().order_by('network', 'address')
    return render(request, 'licen/address/address_list.html', {'addresses': addresses})

@login_required
def address_detail(request, pk):
    address = get_object_or_404(Address, id=pk)
    
    return render(request, 'licen/address/address_detail.html', {
        'address': address,
        'network': address.network,
        'legal_entity': address.network.legal_entity,
        'city': address.network.legal_entity.city,
        'mobile_operators': MobileOperator.objects.filter(address=address),
        'internet_providers': InternetProvider.objects.filter(address=address),
        'wifis': WiFi.objects.filter(address=address),  # Убрали .first()
        'router_admin_panels': RouterAdminPanel.objects.filter(address=address),
        'computers': Computer.objects.filter(address=address),
        'personal_accounts_mobile': PersonalAccountMobileOperator.objects.filter(address=address),
        'personal_accounts_internet': PersonalAccountInternetProvider.objects.filter(address=address),
        'title': f"Адрес: {address.address}"
    })

@role_required(admin)
@login_required
def mobile_operator_create_for_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        form = MobileOperatorForm(request.POST)
        if form.is_valid():
            operator = form.save(commit=False)
            operator.address = address
            operator.save()
            return redirect(reverse('address-detail', kwargs={'pk': address.id}))
    else:
        form = MobileOperatorForm()

    return render(request, 'licen/mobile_operator/mobile_operator_form.html', {
        'form': form,
        'title': f"Добавить мобильного оператора для адреса {address.address}",
        'address': address
    })

# licen/views.py

@role_required(admin)
@login_required
def personal_account_mobile_create_for_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        form = PersonalAccountMobileOperatorForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.address = address
            account.save()
            return redirect(reverse('address-detail', kwargs={'pk': address.id}))
    else:
        form = PersonalAccountMobileOperatorForm()

    return render(request, 'licen/personal_account_mobile_operator/personal_account_mobile_operator_form.html', {
        'form': form,
        'title': f"Добавить личный кабинет для адреса «{address.address}»",
        'address': address  # ← эта строчка ОБЯЗАТЕЛЬНА
    })


# licen/views.py

@role_required(admin)
@login_required
def internet_provider_create_for_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        form = InternetProviderForm(request.POST)
        if form.is_valid():
            provider = form.save(commit=False)
            provider.address = address
            provider.save()
            return redirect(reverse('address-detail', kwargs={'pk': address.id}))
    else:
        form = InternetProviderForm()

    return render(request, 'licen/internet_provider/internet_provider_form.html', {
        'form': form,
        'title': f"Добавить интернет-провайдера для адреса «{address.address}»",
        'address': address
    })

# licen/views.py

@role_required(admin)
@login_required
def personal_account_internet_create_for_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        form = PersonalAccountInternetProviderForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.address = address
            account.save()
            return redirect(reverse('address-detail', kwargs={'pk': address.id}))
    else:
        form = PersonalAccountInternetProviderForm()

    return render(request, 'licen/personal_account_internet_provider/personal_account_internet_provider_form.html', {
        'form': form,
        'title': f"Добавить кабинет интернет-провайдера для адреса «{address.address}»",
        'address': address
    })

@role_required(admin)
@login_required
def wifi_create_for_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        form = WiFiForm(request.POST)
        if form.is_valid():
            wifi = form.save(commit=False)
            wifi.address = address
            wifi.save()
            return redirect(reverse('address-detail', kwargs={'pk': address.id}))
    else:
        form = WiFiForm()

    return render(request, 'licen/wifi/wifi_form.html', {
        'form': form,
        'title': f"Добавить WiFi сеть для адреса «{address.address}»",
        'address': address
    })

@role_required(admin)
@login_required
def router_admin_panel_create_for_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        form = RouterAdminPanelForm(request.POST)
        if form.is_valid():
            panel = form.save(commit=False)
            panel.address = address
            panel.save()
            return redirect(reverse('address-detail', kwargs={'pk': address.id}))
    else:
        form = RouterAdminPanelForm()

    return render(request, 'licen/router_admin_panel/router_admin_panel_form.html', {
        'form': form,
        'title': f"Добавить доступ в админ-панель роутера для адреса «{address.address}»",
        'address': address
    })

@role_required(admin, bookkeeper)
@login_required
def computer_create_for_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        form = ComputerForm(request.POST)
        if form.is_valid():
            computer = form.save(commit=False)
            computer.address = address
            computer.save()
            return redirect(reverse('address-detail', kwargs={'pk': address.id}))
    else:
        form = ComputerForm()

    return render(request, 'licen/computer/computer_form.html', {
        'form': form,
        'title': f"Добавить компьютер для адреса «{address.address}»",
        'address': address
    })

@role_required(admin, bookkeeper)
@login_required
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('address-list'))
    else:
        form = AddressForm()

    return render(request, 'licen/address/address_form.html', {
        'form': form,
        'title': 'Добавить адрес'
    })

@role_required(admin, bookkeeper)
@login_required
def address_update(request, pk):
    address = get_object_or_404(Address, pk=pk)
    network = address.network

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect(reverse('address-list'))
    else:
        form = AddressForm(instance=address)

    return render(request, 'licen/address/address_form.html', {
        'form': form,
        'network': network,
        'title': f"Редактировать {address.network}"
    })

@role_required(admin, bookkeeper)
@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk)

    if request.method == 'POST':
        address.delete()
        return redirect(reverse('address-list'))

    return render(request, 'licen/address/address_confirm_delete.html', {
        'object': address
    })


# ====== Компьютеры ======
@login_required
def computer_list(request):
    computers = Computer.objects.all().order_by('address', 'name')
    return render(request, 'licen/computer/computer_list.html', {'computers': computers})

@login_required
def computer_detail(request, pk):
    from licen.models import Computer, FiscalNumber, CryptoPro, ECP, UTMRSAKeys, MCD, HonestSign, OFD, RemoteAccess

    computer = get_object_or_404(Computer, id=pk)

    # Получаем все типы лицензий для этого компьютера
    fiscal_numbers = FiscalNumber.objects.filter(computer=computer)
    crypto_pros = CryptoPro.objects.filter(computer=computer)
    ecp_list = ECP.objects.filter(computer=computer)
    utm_rsa_list = UTMRSAKeys.objects.filter(computer=computer)
    mcd_list = MCD.objects.filter(computer=computer)
    honest_sign_list = HonestSign.objects.filter(computer=computer)
    ofd_list = OFD.objects.filter(computer=computer)
    remote_accesses = RemoteAccess.objects.filter(computer=computer)
    usais_list = USAIS.objects.filter(computer=computer)

    return render(request, 'licen/computer/computer_detail.html', {
        'computer': computer,
        'fiscal_numbers': fiscal_numbers,
        'crypto_pros': crypto_pros,
        'ecp_list': ecp_list,
        'utm_rsa_list': utm_rsa_list,
        'mcd_list': mcd_list,
        'honest_sign_list': honest_sign_list,
        'ofd_list': ofd_list,
        'remote_accesses': remote_accesses,
        'title': f"Компьютер: {computer.name}",
        'usais_list': usais_list,
        'address': computer.address,
        'network': computer.address.network,
        'legal_entity': computer.address.network.legal_entity,
        'city': computer.address.network.legal_entity.city,
    })

@role_required(admin, bookkeeper)
@login_required
def fiscal_number_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)
    form = FiscalNumberForm(request.POST or None)

    if form.is_valid():
        print("Форма валидна, сохраняем...")
        license = form.save(commit=False)
        license.computer = computer
        license.save()
        print("Переходим на компьютер", computer.id)
        return redirect('computer-detail', pk=computer.id)
    
    return render(request, 'licen/fiscal_number/fiscal_number_form.html', {
        'form': form,
        'title': f"Добавить фискальный номер для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def crypto_pro_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = CryptoProForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            license.computer = computer
            license.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = CryptoProForm()

    return render(request, 'licen/crypto_pro/crypto_pro_form.html', {
        'form': form,
        'title': f"Добавить CryptoPro для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def ecp_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = ECPForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            license.computer = computer
            license.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = ECPForm()

    return render(request, 'licen/ecp/ecp_form.html', {
        'form': form,
        'title': f"Добавить ЭЦП для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def utm_rsa_keys_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = UTMRSAKeysForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            license.computer = computer
            license.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = UTMRSAKeysForm()

    return render(request, 'licen/utmr_sakeys/utmr_sakeys_form.html', {
        'form': form,
        'title': f"Добавить УТМ RSA ключ для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def mcd_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = MCDForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            license.computer = computer
            license.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = MCDForm()

    return render(request, 'licen/mcd/mcd_form.html', {
        'form': form,
        'title': f"Добавить МЧД для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def honest_sign_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = HonestSignForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            license.computer = computer
            license.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = HonestSignForm()

    return render(request, 'licen/honest_sign/honest_sign_form.html', {
        'form': form,
        'title': f"Добавить Честный Знак для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def ofd_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = OFDForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            license.computer = computer
            license.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = OFDForm()

    return render(request, 'licen/ofd/ofd_form.html', {
        'form': form,
        'title': f"Добавить ОФД для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def remote_access_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = RemoteAccessForm(request.POST)
        if form.is_valid():
            access = form.save(commit=False)
            access.computer = computer
            access.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = RemoteAccessForm()

    return render(request, 'licen/remote_access/remote_access_form.html', {
        'form': form,
        'title': f"Добавить удалённый доступ для {computer.name}",
        'computer': computer
    })

@role_required(admin, bookkeeper)
@login_required
def computer_create(request):
    if request.method == 'POST':
        form = ComputerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('computer-list'))
    else:
        form = ComputerForm()

    return render(request, 'licen/computer/computer_form.html', {
        'form': form,
        'title': 'Добавить компьютер'
    })

@role_required(admin, bookkeeper)
@login_required
def computer_update(request, pk):
    computer = get_object_or_404(Computer, pk=pk)
    address = computer.address

    if request.method == 'POST':
        form = ComputerForm(request.POST, instance=computer)
        if form.is_valid():
            form.save()
            return redirect('computer-detail', pk=computer.id)  # ← ОБЯЗАТЕЛЬНО!
    else:
        form = ComputerForm(instance=computer)

    return render(request, 'licen/computer/computer_form.html', {
        'form': form,
        'title': f"Редактировать {computer.name}",
        'address': address
    })

@role_required(admin, bookkeeper)
@login_required
def computer_delete(request, pk):
    computer = get_object_or_404(Computer, pk=pk)

    if request.method == 'POST':
        computer.delete()
        return redirect(reverse('computer-list'))

    return render(request, 'licen/computer/computer_confirm_delete.html', {
        'object': computer
    })

# ====== Удаленный доступ ======
@login_required
def remote_access_list(request):
    accesses = RemoteAccess.objects.all().order_by('computer', 'name')
    return render(request, 'licen/remote_access/remote_access_list.html', {'accesses': accesses})

@login_required
def remote_access_detail(request, pk):
    access = get_object_or_404(RemoteAccess, pk=pk)
    return render(request, 'licen/remote_access/remote_access_detail.html', {'access': access})

@role_required(admin, bookkeeper)
@login_required
def remote_access_create(request):
    if request.method == 'POST':
        form = RemoteAccessForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('remote-access-list'))
    else:
        form = RemoteAccessForm()

    return render(request, 'licen/remote_access/remote_access_form.html', {
        'form': form,
        'title': 'Добавить удаленный доступ'
    })

@role_required(admin, bookkeeper)
@login_required
def remote_access_update(request, pk):
    access = get_object_or_404(RemoteAccess, pk=pk)
    computer = access.computer

    if request.method == 'POST':
        form = RemoteAccessForm(request.POST, instance=access)
        if form.is_valid():
            form.save()
            return redirect(reverse('remote-access-list'))
    else:
        form = RemoteAccessForm(instance=access)

    return render(request, 'licen/remote_access/remote_access_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {access.get_name_display()}"
    })

@role_required(admin, bookkeeper)
@login_required
def remote_access_delete(request, pk):
    access = get_object_or_404(RemoteAccess, pk=pk)

    if request.method == 'POST':
        access.delete()
        return redirect(reverse('remote-access-list'))

    return render(request, 'licen/remote_access/remote_access_confirm_delete.html', {
        'object': access
    })

# ====== фиск накоп ======
@login_required
def fiscal_number_list_one(request):
    fiscal_numbers = FiscalNumber.objects.all().order_by('reg_number', 'model')
    return render(request, 'licen/fiscal_number/fiscal_number_list.html', {'fiscal_numbers': fiscal_numbers})

@login_required
def fiscal_number_detail_one(request, pk):
    fiscal_number = get_object_or_404(FiscalNumber, pk=pk)
    return render(request, 'licen/fiscal_number/fiscal_number_detail.html', {'fiscal_number': fiscal_number})

@role_required(admin, bookkeeper)
@login_required
def fiscal_number_create_one(request):
    if request.method == 'POST':
        form = FiscalNumberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('fiscal-number-list-one'))
    else:
        form = FiscalNumberForm()

    return render(request, 'licen/fiscal_number/fiscal_number_form.html', {
        'form': form,
        'title': 'Добавить ФН'
    })

@role_required(admin, bookkeeper)
@login_required
def fiscal_number_update_one(request, pk):
    fiscal_number = get_object_or_404(FiscalNumber, pk=pk)
    computer = fiscal_number.computer

    if request.method == 'POST':
        form = FiscalNumberForm(request.POST, instance=fiscal_number)
        if form.is_valid():
            form.save()
            return redirect(reverse('fiscal-number-list-one'))
    else:
        form = FiscalNumberForm(instance=fiscal_number)

    return render(request, 'licen/fiscal_number/fiscal_number_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {fiscal_number.model} ({fiscal_number.reg_number})"
    })

@role_required(admin, bookkeeper)
@login_required
def fiscal_number_delete_one(request, pk):
    fiscal_number = get_object_or_404(FiscalNumber, pk=pk)

    if request.method == 'POST':
        fiscal_number.delete()
        return redirect(reverse('fiscal-number-list-one'))

    return render(request, 'licen/fiscal_number/fiscal_number_confirm_delete.html', {
        'object': fiscal_number
    })


# ====== Крипто про ======
@login_required
def crypto_pro_list(request):
    crypto_pros = CryptoPro.objects.all().order_by('end_date')
    return render(request, 'licen/crypto_pro/crypto_pro_list.html', {'crypto_pros': crypto_pros})

@login_required
def crypto_pro_detail(request, pk):
    crypto_pro = get_object_or_404(CryptoPro, pk=pk)
    return render(request, 'licen/crypto_pro/crypto_pro_detail.html', {'crypto_pro': crypto_pro})

@role_required(admin, bookkeeper)
@login_required
def crypto_pro_create(request):
    if request.method == 'POST':
        form = CryptoProForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('crypto-pro-list'))
    else:
        form = CryptoProForm()

    return render(request, 'licen/crypto_pro/crypto_pro_form.html', {
        'form': form,
        'title': 'Добавить CryptoPro'
    })

@role_required(admin, bookkeeper)
@login_required
def crypto_pro_update(request, pk):
    crypto_pro = get_object_or_404(CryptoPro, pk=pk)
    computer = crypto_pro.computer
    
    if request.method == 'POST':
        form = CryptoProForm(request.POST, instance=crypto_pro)
        if form.is_valid():
            form.save()
            return redirect(reverse('crypto-pro-list'))
    else:
        form = CryptoProForm(instance=crypto_pro)

    return render(request, 'licen/crypto_pro/crypto_pro_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {crypto_pro.key}"
    })

@role_required(admin, bookkeeper)
@login_required
def crypto_pro_delete(request, pk):
    crypto_pro = get_object_or_404(CryptoPro, pk=pk)

    if request.method == 'POST':
        crypto_pro.delete()
        return redirect(reverse('crypto-pro-list'))

    return render(request, 'licen/crypto_pro/crypto_pro_confirm_delete.html', {
        'object': crypto_pro
    })


# ====== ECP ======
@login_required
def ecp_list(request):
    ecps = ECP.objects.all().order_by('full_name')
    return render(request, 'licen/ecp/ecp_list.html', {'ecps': ecps})

@login_required
def ecp_detail(request, pk):
    ecp = get_object_or_404(ECP, pk=pk)
    return render(request, 'licen/ecp/ecp_detail.html', {'ecp': ecp})

@role_required(admin, bookkeeper)
@login_required
def ecp_create(request):
    if request.method == 'POST':
        form = ECPForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('ecp-list'))
    else:
        form = ECPForm()

    return render(request, 'licen/ecp/ecp_form.html', {
        'form': form,
        'title': 'Добавить ЭЦП'
    })

@role_required(admin, bookkeeper)
@login_required
def ecp_update(request, pk):
    ecp = get_object_or_404(ECP, pk=pk)
    computer = ecp.computer

    if request.method == 'POST':
        form = ECPForm(request.POST, instance=ecp)
        if form.is_valid():
            form.save()
            return redirect(reverse('ecp-list'))
    else:
        form = ECPForm(instance=ecp)

    return render(request, 'licen/ecp/ecp_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {ecp.full_name}"
    })

@role_required(admin, bookkeeper)
@login_required
def ecp_delete(request, pk):
    ecp = get_object_or_404(ECP, pk=pk)

    if request.method == 'POST':
        ecp.delete()
        return redirect(reverse('ecp-list'))

    return render(request, 'licen/ecp/ecp_confirm_delete.html', {
        'object': ecp
    })

# ====== utmr_sakeys ======
@login_required
def utmr_sakeys_list(request):
    keys = UTMRSAKeys.objects.all().order_by('key')
    return render(request, 'licen/utmr_sakeys/utmr_sakeys_list.html', {'keys': keys})

@login_required
def utmr_sakeys_detail(request, pk):
    key = get_object_or_404(UTMRSAKeys, pk=pk)
    return render(request, 'licen/utmr_sakeys/utmr_sakeys_detail.html', {'key': key})

@role_required(admin, bookkeeper)
@login_required
def utmr_sakeys_create(request):
    if request.method == 'POST':
        form = UTMRSAKeysForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('utmr-sakeys-list'))
    else:
        form = UTMRSAKeysForm()

    return render(request, 'licen/utmr_sakeys/utmr_sakeys_form.html', {
        'form': form,
        'title': 'Добавить УТМ RSA Ключ'
    })

@role_required(admin, bookkeeper)
@login_required
def utmr_sakeys_update(request, pk):
    key = get_object_or_404(UTMRSAKeys, pk=pk)
    computer = key.computer

    if request.method == 'POST':
        form = UTMRSAKeysForm(request.POST, instance=key)
        if form.is_valid():
            form.save()
            return redirect(reverse('utmr-sakeys-list'))
    else:
        form = UTMRSAKeysForm(instance=key)

    return render(request, 'licen/utmr_sakeys/utmr_sakeys_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {key.key}"
    })

@role_required(admin, bookkeeper)
@login_required
def utmr_sakeys_delete(request, pk):
    key = get_object_or_404(UTMRSAKeys, pk=pk)

    if request.method == 'POST':
        key.delete()
        return redirect(reverse('utmr-sakeys-list'))

    return render(request, 'licen/utmr_sakeys/utmr_sakeys_confirm_delete.html', {
        'object': key
    })

# ====== МЧД ======
@login_required
def mcd_list(request):
    mcds = MCD.objects.all().order_by('mcd_id')
    return render(request, 'licen/mcd/mcd_list.html', {'mcds': mcds})

@login_required
def mcd_detail(request, pk):
    mcd = get_object_or_404(MCD, pk=pk)
    return render(request, 'licen/mcd/mcd_detail.html', {'mcd': mcd})

@role_required(admin, bookkeeper)
@login_required
def mcd_create(request):
    if request.method == 'POST':
        form = MCDForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('mcd-list'))
    else:
        form = MCDForm()

    return render(request, 'licen/mcd/mcd_form.html', {
        'form': form,
        'title': 'Добавить МЧД'
    })

@role_required(admin, bookkeeper)
@login_required
def mcd_update(request, pk):
    mcd = get_object_or_404(MCD, pk=pk)
    computer = mcd.computer

    if request.method == 'POST':
        form = MCDForm(request.POST, instance=mcd)
        if form.is_valid():
            form.save()
            return redirect(reverse('mcd-list'))
    else:
        form = MCDForm(instance=mcd)

    return render(request, 'licen/mcd/mcd_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {mcd.mcd_id}"
    })

@role_required(admin, bookkeeper)
@login_required
def mcd_delete(request, pk):
    mcd = get_object_or_404(MCD, pk=pk)

    if request.method == 'POST':
        mcd.delete()
        return redirect(reverse('mcd-list'))

    return render(request, 'licen/mcd/mcd_confirm_delete.html', {
        'object': mcd
    })

# ====== ЕГАИС ======
@login_required
def usa_is_list(request):
    licenses = USAIS.objects.all().order_by('end_date', 'key')
    return render(request, 'licen/usais/usais_list.html', {'licenses': licenses})

@login_required
def usa_is_detail(request, pk):
    license = get_object_or_404(USAIS, id=pk)
    return render(request, 'licen/usais/usais_detail.html', {'license': license})

@role_required(admin, bookkeeper)
@login_required
def usa_is_create(request):
    if request.method == 'POST':
        form = USAISForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usais-list')
    else:
        form = USAISForm()

    return render(request, 'licen/usais/usais_form.html', {
        'form': form,
        'title': 'Добавить лицензию ЕГАИС'
    })

@role_required(admin, bookkeeper)
@login_required
def usa_is_update(request, pk):
    license = get_object_or_404(USAIS, id=pk)
    computer = license.computer

    if request.method == 'POST':
        form = USAISForm(request.POST, instance=license)
        if form.is_valid():
            form.save()
            return redirect('usais-list')
    else:
        form = USAISForm(instance=license)

    return render(request, 'licen/usais/usais_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {license.key}"
    })

@role_required(admin, bookkeeper)
@login_required
def usa_is_delete(request, pk):
    license = get_object_or_404(USAIS, id=pk)

    if request.method == 'POST':
        license.delete()
        return redirect('usais-list')

    return render(request, 'licen/usais/usais_confirm_delete.html', {
        'object': license
    })

@role_required(admin, bookkeeper)
@login_required
def usa_is_create_for_computer(request, computer_id):
    computer = get_object_or_404(Computer, id=computer_id)

    if request.method == 'POST':
        form = USAISForm(request.POST)
        if form.is_valid():
            usais = form.save(commit=False)
            usais.computer = computer
            usais.save()
            return redirect(reverse('computer-detail', kwargs={'pk': computer.id}))
    else:
        form = USAISForm()

    return render(request, 'licen/usais/usais_form.html', {
        'form': form,
        'title': f"Добавить ЕГАИС для {computer.name}",
        'computer': computer
    })


# ====== Честный знак ======
@login_required
def honest_sign_list(request):
    signs = HonestSign.objects.all().order_by('key')
    return render(request, 'licen/honest_sign/honest_sign_list.html', {'signs': signs})

@login_required
def honest_sign_detail(request, pk):
    sign = get_object_or_404(HonestSign, pk=pk)
    return render(request, 'licen/honest_sign/honest_sign_detail.html', {'sign': sign})

@role_required(admin, bookkeeper)
@login_required
def honest_sign_create(request):
    if request.method == 'POST':
        form = HonestSignForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('honest-sign-list'))
    else:
        form = HonestSignForm()

    return render(request, 'licen/honest_sign/honest_sign_form.html', {
        'form': form,
        'title': 'Добавить Честный знак'
    })

@role_required(admin, bookkeeper)
@login_required
def honest_sign_update(request, pk):
    sign = get_object_or_404(HonestSign, pk=pk)
    computer = sign.computer

    if request.method == 'POST':
        form = HonestSignForm(request.POST, instance=sign)
        if form.is_valid():
            form.save()
            return redirect(reverse('honest-sign-list'))
    else:
        form = HonestSignForm(instance=sign)

    return render(request, 'licen/honest_sign/honest_sign_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {sign.key}"
    })

@role_required(admin, bookkeeper)
@login_required
def honest_sign_delete(request, pk):
    sign = get_object_or_404(HonestSign, pk=pk)

    if request.method == 'POST':
        sign.delete()
        return redirect(reverse('honest-sign-list'))

    return render(request, 'licen/honest_sign/honest_sign_confirm_delete.html', {
        'object': sign
    })


# ====== OFD ======
@login_required
def ofd_list(request):
    ofds = OFD.objects.all().order_by('reg_number')
    return render(request, 'licen/ofd/ofd_list.html', {'ofds': ofds})

@login_required
def ofd_detail(request, pk):
    ofd = get_object_or_404(OFD, pk=pk)
    return render(request, 'licen/ofd/ofd_detail.html', {'ofd': ofd})

@role_required(admin, bookkeeper)
@login_required
def ofd_create(request):
    if request.method == 'POST':
        form = OFDForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('ofd-list'))
    else:
        form = OFDForm()

    return render(request, 'licen/ofd/ofd_form.html', {
        'form': form,
        'title': 'Добавить ОФД'
    })

@role_required(admin, bookkeeper)
@login_required
def ofd_update(request, pk):
    ofd = get_object_or_404(OFD, pk=pk)
    computer = ofd.computer

    if request.method == 'POST':
        form = OFDForm(request.POST, instance=ofd)
        if form.is_valid():
            form.save()
            return redirect(reverse('ofd-list'))
    else:
        form = OFDForm(instance=ofd)

    return render(request, 'licen/ofd/ofd_form.html', {
        'form': form,
        'computer': computer,
        'title': f"Редактировать {ofd.reg_number}"
    })

@role_required(admin, bookkeeper)
@login_required
def ofd_delete(request, pk):
    ofd = get_object_or_404(OFD, pk=pk)

    if request.method == 'POST':
        ofd.delete()
        return redirect(reverse('ofd-list'))

    return render(request, 'licen/ofd/ofd_confirm_delete.html', {
        'object': ofd
    })


# ====== Мобильные операторы ======
@role_required(admin)
@login_required
def mobile_operator_list(request):
    operators = MobileOperator.objects.all().order_by('operator', 'phone_number')
    return render(request, 'licen/mobile_operator/mobile_operator_list.html', {'operators': operators})

@role_required(admin)
@login_required
def mobile_operator_detail(request, pk):
    operator = get_object_or_404(MobileOperator, pk=pk)
    return render(request, 'licen/mobile_operator/mobile_operator_detail.html', {'operator': operator})

@role_required(admin)
@login_required
def mobile_operator_create(request):
    if request.method == 'POST':
        form = MobileOperatorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('mobile-operator-list'))
    else:
        form = MobileOperatorForm()

    return render(request, 'licen/mobile_operator/mobile_operator_form.html', {
        'form': form,
        'title': 'Добавить мобильного оператора'
    })

@role_required(admin)
@login_required
def mobile_operator_update(request, pk):
    operator = get_object_or_404(MobileOperator, pk=pk)

    if request.method == 'POST':
        form = MobileOperatorForm(request.POST, instance=operator)
        if form.is_valid():
            form.save()
            return redirect(reverse('mobile-operator-list'))
    else:
        form = MobileOperatorForm(instance=operator)

    return render(request, 'licen/mobile_operator/mobile_operator_form.html', {
        'form': form,
        'title': f"Редактировать {operator}",
        'address': operator.address
    })

@role_required(admin)
@login_required
def mobile_operator_delete(request, pk):
    operator = get_object_or_404(MobileOperator, pk=pk)

    if request.method == 'POST':
        operator.delete()
        return redirect(reverse('mobile-operator-list'))

    return render(request, 'licen/mobile_operator/mobile_operator_confirm_delete.html', {
        'object': operator
    })


# ====== Интернет провайдер ======
@role_required(admin)
@login_required
def internet_provider_list(request):
    providers = InternetProvider.objects.all().order_by('provider', 'address')
    return render(request, 'licen/internet_provider/internet_provider_list.html', {'providers': providers})

@role_required(admin)
@login_required
def internet_provider_detail(request, pk):
    provider = get_object_or_404(InternetProvider, pk=pk)
    return render(request, 'licen/internet_provider/internet_provider_detail.html', {'provider': provider})

@role_required(admin)
@login_required
def internet_provider_create(request):
    if request.method == 'POST':
        form = InternetProviderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('internet-provider-list'))
    else:
        form = InternetProviderForm()

    return render(request, 'licen/internet_provider/internet_provider_form.html', {
        'form': form,
        'title': 'Добавить интернет-провайдера'
    })

@role_required(admin)
@login_required
def internet_provider_update(request, pk):
    provider = get_object_or_404(InternetProvider, pk=pk)
    address = provider.address

    if request.method == 'POST':
        form = InternetProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return redirect(reverse('internet-provider-list'))
    else:
        form = InternetProviderForm(instance=provider)

    return render(request, 'licen/internet_provider/internet_provider_form.html', {
        'form': form,
        'title': f"Редактировать {provider.provider} ({provider.speed})",
        'address': address
    })

@role_required(admin)
@login_required
def internet_provider_delete(request, pk):
    provider = get_object_or_404(InternetProvider, pk=pk)

    if request.method == 'POST':
        provider.delete()
        return redirect(reverse('internet-provider-list'))

    return render(request, 'licen/internet_provider/internet_provider_confirm_delete.html', {
        'object': provider
    })


# ====== WiFi ======
@role_required(admin)
@login_required
def wifi_list(request):
    wifis = WiFi.objects.all().order_by('name')
    return render(request, 'licen/wifi/wifi_list.html', {'wifis': wifis})

@role_required(admin)
@login_required
def wifi_detail(request, pk):
    wifi = get_object_or_404(WiFi, pk=pk)
    return render(request, 'licen/wifi/wifi_detail.html', {'wifi': wifi})

@role_required(admin)
@login_required
def wifi_create(request):
    if request.method == 'POST':
        form = WiFiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('wifi-list'))
    else:
        form = WiFiForm()

    return render(request, 'licen/wifi/wifi_form.html', {
        'form': form,
        'title': 'Добавить WiFi'
    })

@role_required(admin)
@login_required
def wifi_update(request, pk):
    wifi = get_object_or_404(WiFi, pk=pk)
    address = wifi.address

    if request.method == 'POST':
        form = WiFiForm(request.POST, instance=wifi)
        if form.is_valid():
            form.save()
            return redirect(reverse('wifi-list'))
    else:
        form = WiFiForm(instance=wifi)

    return render(request, 'licen/wifi/wifi_form.html', {
        'form': form,
        'title': f"Редактировать {wifi.name}",
        'address': address
    })

@role_required(admin)
@login_required
def wifi_delete(request, pk):
    wifi = get_object_or_404(WiFi, pk=pk)

    if request.method == 'POST':
        wifi.delete()
        return redirect(reverse('wifi-list'))

    return render(request, 'licen/wifi/wifi_confirm_delete.html', {
        'object': wifi
    })


# ====== Роутер админ панель ======
@role_required(admin)
@login_required
def router_admin_panel_list(request):
    panels = RouterAdminPanel.objects.all().order_by('address', 'name')
    return render(request, 'licen/router_admin_panel/router_admin_panel_list.html', {'panels': panels})

@role_required(admin)
@login_required
def router_admin_panel_detail(request, pk):
    panel = get_object_or_404(RouterAdminPanel, pk=pk)
    return render(request, 'licen/router_admin_panel/router_admin_panel_detail.html', {'panel': panel})

@role_required(admin)
@login_required
def router_admin_panel_create(request):
    if request.method == 'POST':
        form = RouterAdminPanelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('router-admin-panel-list'))
    else:
        form = RouterAdminPanelForm()

    return render(request, 'licen/router_admin_panel/router_admin_panel_form.html', {
        'form': form,
        'title': 'Добавить панель роутера'
    })

@role_required(admin)
@login_required
def router_admin_panel_update(request, pk):
    panel = get_object_or_404(RouterAdminPanel, pk=pk)
    address = panel.address

    if request.method == 'POST':
        form = RouterAdminPanelForm(request.POST, instance=panel)
        if form.is_valid():
            form.save()
            return redirect(reverse('router-admin-panel-list'))
    else:
        form = RouterAdminPanelForm(instance=panel)

    return render(request, 'licen/router_admin_panel/router_admin_panel_form.html', {
        'form': form,
        'title': f"Редактировать {panel.name}",
        'address': address
    })

@role_required(admin)
@login_required
def router_admin_panel_delete(request, pk):
    panel = get_object_or_404(RouterAdminPanel, pk=pk)

    if request.method == 'POST':
        panel.delete()
        return redirect(reverse('router-admin-panel-list'))

    return render(request, 'licen/router_admin_panel/router_admin_panel_confirm_delete.html', {
        'object': panel
    })


# ====== Аккаунт интернет пров ======
@role_required(admin)
@login_required
def personal_account_internet_provider_list(request):
    accounts = PersonalAccountInternetProvider.objects.all().order_by('internet_provider', 'login')
    return render(request, 'licen/personal_account_internet_provider/personal_account_internet_provider_list.html', {'accounts': accounts})

@role_required(admin)
@login_required
def personal_account_internet_provider_detail(request, pk):
    account = get_object_or_404(PersonalAccountInternetProvider, pk=pk)
    return render(request, 'licen/personal_account_internet_provider/personal_account_internet_provider_detail.html', {'account': account})

@role_required(admin)
@login_required
def personal_account_internet_provider_create(request):
    if request.method == 'POST':
        form = PersonalAccountInternetProviderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('personal-account-internet-provider-list'))
    else:
        form = PersonalAccountInternetProviderForm()

    return render(request, 'licen/personal_account_internet_provider/personal_account_internet_provider_form.html', {
        'form': form,
        'title': 'Добавить личный кабинет интернет-провайдера'
    })

@role_required(admin)
@login_required
def personal_account_internet_provider_update(request, pk):
    account = get_object_or_404(PersonalAccountInternetProvider, pk=pk)
    address = account.address

    if request.method == 'POST':
        form = PersonalAccountInternetProviderForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect(reverse('personal-account-internet-provider-list'))
    else:
        form = PersonalAccountInternetProviderForm(instance=account)

    return render(request, 'licen/personal_account_internet_provider/personal_account_internet_provider_form.html', {
        'form': form,
        'title': f"Редактировать {account.login} ({account.ip_address})",
        'address': address
    })

@role_required(admin)
@login_required
def personal_account_internet_provider_delete(request, pk):
    account = get_object_or_404(PersonalAccountInternetProvider, pk=pk)

    if request.method == 'POST':
        account.delete()
        return redirect(reverse('personal-account-internet-provider-list'))

    return render(request, 'licen/personal_account_internet_provider_confirm/personal_account_internet_provider_delete.html', {
        'object': account
    })


# ====== Аккаунт мобильных операторов ======
@role_required(admin)
@login_required
def personal_account_mobile_operator_list(request):
    accounts = PersonalAccountMobileOperator.objects.all().order_by('mobile_operator', 'login')
    return render(request, 'licen/personal_account_mobile_operator/personal_account_mobile_operator_list.html', {'accounts': accounts})

@role_required(admin)
@login_required
def personal_account_mobile_operator_detail(request, pk):
    account = get_object_or_404(PersonalAccountMobileOperator, pk=pk)
    return render(request, 'licen/personal_account_mobile_operator/personal_account_mobile_operator_detail.html', {'account': account})

@role_required(admin)
@login_required
def personal_account_mobile_operator_create(request):
    if request.method == 'POST':
        form = PersonalAccountMobileOperatorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('personal-account-mobile-operator-list'))
    else:
        form = PersonalAccountMobileOperatorForm()

    return render(request, 'licen/personal_account_mobile_operator/personal_account_mobile_operator_form.html', {
        'form': form,
        'title': 'Добавить личный кабинет мобильного оператора'
    })

@role_required(admin)
@login_required
def personal_account_mobile_operator_update(request, pk):
    account = get_object_or_404(PersonalAccountMobileOperator, id=pk)
    address = account.address  # ← Получаем адрес из объекта

    if request.method == 'POST':
        form = PersonalAccountMobileOperatorForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect(reverse('personal-account-mobile-operator-list'))
    else:
        form = PersonalAccountMobileOperatorForm(instance=account)

    return render(request, 'licen/personal_account_mobile_operator/personal_account_mobile_operator_form.html', {
        'form': form,
        'title': f"Редактировать {account.login} ({account.mobile_operator})",
        'address': address  # ← Важно: передаём address
    })

@role_required(admin)
@login_required
def personal_account_mobile_operator_delete(request, pk):
    account = get_object_or_404(PersonalAccountMobileOperator, pk=pk)

    if request.method == 'POST':
        account.delete()
        return redirect(reverse('personal-account-mobile-operator-list'))

    return render(request, 'licen/personal_account_mobile_operator/personal_account_mobile_operator_confirm_delete.html', {
        'object': account
    })



# licen/views.py
 
@login_required
def license_list(request, license_type=None):
    from licen.models import LicenseBaseModel
    all_licenses = []

    for model in LicenseBaseModel.__subclasses__():
        for obj in model.objects.all():
            all_licenses.append({
                'object': obj,
                'verbose_name': model._meta.verbose_name,
                'type': model.__name__,
                'id': obj.id  # ← убедись, что id не None или ''
            })

    context = {
        'licenses': all_licenses,
        'title': 'Все лицензии'
    }
    return render(request, 'licen/license_list.html', context)
   

@login_required
def license_detail(request, license_type, license_id):
    from licen.models import LicenseBaseModel

    model_class = None
    for model in LicenseBaseModel.__subclasses__():
        if model.__name__ == license_type:
            model_class = model
            break
    
    if not model_class:
        raise Http404("Лицензия не найдена")

    obj = get_object_or_404(model_class, id=license_id)

    # Получаем связанные объекты
    computer = getattr(obj, 'computer', None)
    address = getattr(obj, 'address', None)
    legal_entity = getattr(obj, 'legal_entity', None)
    network = getattr(obj, 'network', None)
    city = getattr(obj, 'city', None)

    context = {
        'object': obj,
        'computer': computer,  # ← теперь это объект, а не строка
        'address': address,
        'legal_entity': legal_entity,
        'network': network,
        'city': city,
        'title': f"{obj._meta.verbose_name} #{obj.id}"
    }
    return render(request, 'licen/license_detail.html', context)

@login_required
@role_required(admin, bookkeeper)
def license_delete(request, license_type, license_id):
    from licen.models import LicenseBaseModel
    model_class = None
    for model in LicenseBaseModel.__subclasses__():
        if model.__name__ == license_type:
            model_class = model
            break
    
    if not model_class:
        raise Http404("Лицензия не найдена")

    obj = get_object_or_404(model_class, id=license_id)

    if request.method == 'POST':
        obj.delete()
        return HttpResponseRedirect(reverse('license-list'))

    return render(request, 'licen/license_confirm_delete.html', {
        'object': obj,
        'title': f'Удалить уведомление #{obj.id}'
    })

@role_required(admin, bookkeeper)
@login_required
def license_create(request, license_type):
    from licen.models import LicenseBaseModel

    model_class = None
    for model in LicenseBaseModel.__subclasses__():
        if model.__name__ == license_type:
            model_class = model
            break

    if not model_class:
        raise Http404("Неизвестный тип лицензии")

    form_class = type(f"{model_class.__name__}Form", (ModelForm,), {
        'Meta': type('Meta', (), {'model': model_class, 'fields': '__all__'})
    })

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = form_class()

    return render(request, 'licen/license_form.html', {
        'form': form,
        'title': f"Добавить {model_class._meta.verbose_name}"
    })

@login_required
def dashboard(request):
    context = {
        'total_licenses': LicenseNotification.objects.count(),
        'expired_count': LicenseNotification.objects.filter(notification_type='expired').count(),
        'expiring_soon_30': LicenseNotification.objects.filter(notification_type='expiring_soon_30'),
        'expiring_soon_7': LicenseNotification.objects.filter(notification_type='expiring_soon_7'),
        'expiring_soon_1': LicenseNotification.objects.filter(notification_type='expiring_soon_1'),
        'notifications': LicenseNotification.objects.filter(is_sent=False).order_by('-expiration_date')[:5],
        'title': 'Дашборд',
    }
    return render(request, 'licen/dashboard.html', context)

@login_required
def license_select_type(request):
    return render(request, 'licen/license_select_type.html', {
        'title': 'Выберите тип лицензии'
    })

# ====== Юрлица ======

class LegalEntityCreateView(CreateView):
    model = LegalEntity
    form_class = LegalEntityForm
    template_name = 'licen/legalentity_form.html'

    def get_initial(self):
        initial = super().get_initial()
        city_id = self.kwargs.get('city_id')
        if city_id:
            initial['city'] = city_id
        return initial

    def get_success_url(self):
        return reverse('city-detail', kwargs={'pk': self.object.city.pk})

# ====== Уведомления ======

class LicenseDetail(DetailView):
    model = LicenseNotification
    template_name = 'licen/license_detail.html'
    context_object_name = 'notification'

    def get_object(self, queryset=None):
        return get_object_or_404(LicenseNotification, pk=self.kwargs['pk'])