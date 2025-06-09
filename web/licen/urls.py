from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (

    city_list,
    city_detail,

    legal_entity_create_for_city,

    city_create,
    city_update,
    city_delete,

    contact_person_list,
    contact_person_detail,
    contact_person_create,
    contact_person_update,
    contact_person_delete,

    LegalEntityCreateView,

    ChangePasswordView,

    login_view,
    home_view,
    register_view,
    

    profile_view,
    user_detail,
    user_update,
    user_delete,

    search_results,

    dashboard, 

    license_list, 
    license_detail,
    license_create,
    license_select_type,

    crypto_pro_list,
    crypto_pro_detail,
    crypto_pro_create,

    # fiscal_number_list,
    # fiscal_number_detail,
    # fiscal_number_create,

    legal_entity_list,
    legal_entity_detail,
    network_create_for_legal_entity,
    legal_entity_create,
    legal_entity_update,
    legal_entity_delete,

    network_list,
    network_detail,

    address_create_for_network,

    network_create,
    network_update,
    network_delete,

    address_list,
    address_detail,
    
    mobile_operator_create_for_address,
    personal_account_mobile_create_for_address,

    internet_provider_create_for_address,
    personal_account_internet_create_for_address,

    wifi_create_for_address,
    router_admin_panel_create_for_address,
    computer_create_for_address,

    address_create,
    address_update,
    address_delete,

    computer_list,
    computer_detail,
    
    fiscal_number_create_for_computer,
    crypto_pro_create_for_computer,
    ecp_create_for_computer,
    utm_rsa_keys_create_for_computer,
    mcd_create_for_computer,
    honest_sign_create_for_computer,
    ofd_create_for_computer,
    remote_access_create_for_computer,

    computer_create,
    computer_update,
    computer_delete,

    remote_access_list,
    remote_access_detail,
    remote_access_create,
    remote_access_update,
    remote_access_delete,

    fiscal_number_list_one,
    fiscal_number_detail_one,
    fiscal_number_create_one,
    fiscal_number_update_one,
    fiscal_number_delete_one,

    crypto_pro_list,
    crypto_pro_detail,
    crypto_pro_create,
    crypto_pro_update,
    crypto_pro_delete,

    ecp_list,
    ecp_detail,
    ecp_create,
    ecp_update,
    ecp_delete,

    utmr_sakeys_list,
    utmr_sakeys_detail,
    utmr_sakeys_create,
    utmr_sakeys_update,
    utmr_sakeys_delete,

    mcd_list,
    mcd_detail,
    mcd_create,
    mcd_update,
    mcd_delete,

    usa_is_list,
    usa_is_detail,
    usa_is_create,
    usa_is_update,
    usa_is_delete,
    usa_is_create_for_computer,

    honest_sign_list,
    honest_sign_detail,
    honest_sign_create,
    honest_sign_update,
    honest_sign_delete,

    ofd_list,
    ofd_detail,
    ofd_create,
    ofd_update,
    ofd_delete,

    mobile_operator_list,
    mobile_operator_detail,
    mobile_operator_create,
    mobile_operator_update,
    mobile_operator_delete,

    internet_provider_list,
    internet_provider_detail,
    internet_provider_create,
    internet_provider_update,
    internet_provider_delete,

    wifi_list,
    wifi_detail,
    wifi_create,
    wifi_update,
    wifi_delete,

    router_admin_panel_list,
    router_admin_panel_detail,
    router_admin_panel_create,
    router_admin_panel_update,
    router_admin_panel_delete,

    personal_account_internet_provider_list,
    personal_account_internet_provider_detail,
    personal_account_internet_provider_create,
    personal_account_internet_provider_update,
    personal_account_internet_provider_delete,

    personal_account_mobile_operator_list,
    personal_account_mobile_operator_detail,
    personal_account_mobile_operator_create,
    personal_account_mobile_operator_update,
    personal_account_mobile_operator_delete,
)


urlpatterns = [
    path('home/', home_view, name='home'),
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('', auth_views.LogoutView.as_view(), name='logout'),

    path('search/', search_results, name='search-results'),

    path('profile/', profile_view, name='profile'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('users/<int:pk>/edit/', user_update, name='user-update'),
    path('users/<int:pk>/delete/', user_delete, name='user-delete'),

    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/<int:user_id>/change-password/', ChangePasswordView.as_view(), name='change-user-password'),

    # Юрлица
    path('cities/<int:city_id>/add_legal_entity/', LegalEntityCreateView.as_view(), name='legal-entity-create'),

    # Города
    path('cities/', city_list, name='city-list'),
    path('cities/<int:pk>/', city_detail, name='city-detail'),

    path('cities/<int:city_id>/legal-entities/new/', legal_entity_create_for_city, name='legal-entity-create-for-city'),

    path('cities/new/', city_create, name='city-create'),
    path('cities/<int:pk>/edit/', city_update, name='city-update'),
    path('cities/<int:pk>/delete/', city_delete, name='city-delete'),

    #Почты
    path('contact-persons/', contact_person_list, name='contact-person-list'),
    path('contact-persons/<int:pk>/', contact_person_detail, name='contact-person-detail'),
    path('contact-persons/new/', contact_person_create, name='contact-person-create'),
    path('contact-persons/<int:pk>/edit/', contact_person_update, name='contact-person-update'),
    path('contact-persons/<int:pk>/delete/', contact_person_delete, name='contact-person-delete'),

    # Юрлица
    path('legal-entities/', legal_entity_list, name='legal-entity-list'),
    path('legal-entities/<int:pk>/', legal_entity_detail, name='legal-entity-detail'),
    
    path('legal-entities/<int:legal_entity_id>/new-network/', network_create_for_legal_entity, name='network-create-for-legal-entity'),    path('legal-entities/new/', legal_entity_create, name='legal-entity-create'),
    
    path('legal-entities/<int:pk>/edit/', legal_entity_update, name='legal-entity-update'),
    path('legal-entities/<int:pk>/delete/', legal_entity_delete, name='legal-entity-delete'),

    # Сети
    path('networks/', network_list, name='network-list'),
    path('networks/<int:pk>/', network_detail, name='network-detail'),
    
    path('networks/<int:network_id>/addresses/new/', address_create_for_network, name='address-create-for-network'),

    path('networks/new/', network_create, name='network-create'),
    path('networks/<int:pk>/edit/', network_update, name='network-update'),
    path('networks/<int:pk>/delete/', network_delete, name='network-delete'),

    # Адреса
    path('addresses/', address_list, name='address-list'),
    path('addresses/<int:pk>/', address_detail, name='address-detail'),
    
     # Мобильный оператор
    path('addresses/<int:address_id>/mobile-operator/new/', mobile_operator_create_for_address, name='mobile-operator-create-for-address'),
    path('addresses/<int:address_id>/personal-account/mobile/new/', personal_account_mobile_create_for_address, name='personal-account-mobile-create-for-address'),

    # Интернет-провайдер
    path('addresses/<int:address_id>/internet-provider/new/', internet_provider_create_for_address, name='internet-provider-create-for-address'),
    path('addresses/<int:address_id>/personal-account/internet/new/', personal_account_internet_create_for_address, name='personal-account-internet-create-for-address'),

    # WiFi
    path('addresses/<int:address_id>/wifi/new/', wifi_create_for_address, name='wifi-create-for-address'),

    # Роутер
    path('addresses/<int:address_id>/router-admin-panel/new/', router_admin_panel_create_for_address, name='router-admin-panel-create-for-address'),

    # Компьютер
    path('addresses/<int:address_id>/computer/new/', computer_create_for_address, name='computer-create-for-address'),

    path('addresses/new/', address_create, name='address-create'),
    path('addresses/<int:pk>/edit/', address_update, name='address-update'),
    path('addresses/<int:pk>/delete/', address_delete, name='address-delete'),

    # Компьютеры
    path('computers/', computer_list, name='computer-list'),
    path('computers/<int:pk>/', computer_detail, name='computer-detail'),
    
     # Лицензии
    path('computers/<int:computer_id>/fiscal-numbers/new/', fiscal_number_create_for_computer, name='fiscal-number-create-for-computer'),
    path('computers/<int:computer_id>/crypto-pro/new/', crypto_pro_create_for_computer, name='crypto-pro-create-for-computer'),
    path('computers/<int:computer_id>/ecp/new/', ecp_create_for_computer, name='ecp-create-for-computer'),
    path('computers/<int:computer_id>/utm-rsa-keys/new/', utm_rsa_keys_create_for_computer, name='utm-rsa-keys-create-for-computer'),
    path('computers/<int:computer_id>/mcd/new/', mcd_create_for_computer, name='mcd-create-for-computer'),
    path('computers/<int:computer_id>/honest-sign/new/', honest_sign_create_for_computer, name='honest-sign-create-for-computer'),
    path('computers/<int:computer_id>/ofd/new/', ofd_create_for_computer, name='ofd-create-for-computer'),
    path('computers/<int:computer_id>/egais/new/', usa_is_create_for_computer, name='usais-create-for-computer'),

    # Удалённый доступ
    path('computers/<int:computer_id>/remote-access/new/', remote_access_create_for_computer, name='remote-access-create-for-computer'),
    
    path('computers/new/', computer_create, name='computer-create'),
    path('computers/<int:pk>/edit/', computer_update, name='computer-update'),
    path('computers/<int:pk>/delete/', computer_delete, name='computer-delete'),

    # Удаленный доступ
    path('remote-access/', remote_access_list, name='remote-access-list'),
    path('remote-access/<int:pk>/', remote_access_detail, name='remote-access-detail'),
    path('remote-access/new/', remote_access_create, name='remote-access-create'),
    path('remote-access/<int:pk>/edit/', remote_access_update, name='remote-access-update'),
    path('remote-access/<int:pk>/delete/', remote_access_delete, name='remote-access-delete'),

    # Фискальные номера
    path('fiscal-numbers/', fiscal_number_list_one, name='fiscal-number-list-one'),
    path('fiscal-numbers/<int:pk>/', fiscal_number_detail_one, name='fiscal-number-detail-one'),
    path('fiscal-numbers/new/', fiscal_number_create_one, name='fiscal-number-create-one'),
    path('fiscal-numbers/<int:pk>/edit/', fiscal_number_update_one, name='fiscal-number-update-one'),
    path('fiscal-numbers/<int:pk>/delete/', fiscal_number_delete_one, name='fiscal-number-delete-one'),

    # Главная страница
    path('dashboard/', dashboard, name='dashboard'),

    # Лицензии
    path('licenses/', license_list, name='license-list'),
    path('licenses/<str:license_type>/', license_list, name='license-list-by-type'),
    path('licenses/<str:license_type>/<int:license_id>/', license_detail, name='license-detail'),
    path('licenses/<str:license_type>/new/', license_create, name='license-create'),
    path('select-type/', license_select_type, name='license-select-type'),

    # CryptoPro
    path('crypto-pro/', crypto_pro_list, name='crypto-pro-list'),
    path('crypto-pro/<int:pk>/', crypto_pro_detail, name='crypto-pro-detail'),
    path('crypto-pro/new/', crypto_pro_create, name='crypto-pro-create'),
    path('crypto-pro/<int:pk>/edit/', crypto_pro_update, name='crypto-pro-update'),
    path('crypto-pro/<int:pk>/delete/', crypto_pro_delete, name='crypto-pro-delete'),

    # ECP
    path('ecps/', ecp_list, name='ecp-list'),
    path('ecps/<int:pk>/', ecp_detail, name='ecp-detail'),
    path('ecps/new/', ecp_create, name='ecp-create'),
    path('ecps/<int:pk>/edit/', ecp_update, name='ecp-update'),
    path('ecps/<int:pk>/delete/', ecp_delete, name='ecp-delete'),

    # utmr-keys
    path('utmr-keys/', utmr_sakeys_list, name='utmr-sakeys-list'),
    path('utmr-keys/<int:pk>/', utmr_sakeys_detail, name='utmr-sakeys-detail'),
    path('utmr-keys/new/', utmr_sakeys_create, name='utmr-sakeys-create'),
    path('utmr-keys/<int:pk>/edit/', utmr_sakeys_update, name='utmr-sakeys-update'),
    path('utmr-keys/<int:pk>/delete/', utmr_sakeys_delete, name='utmr-sakeys-delete'),

    # МЧД
    path('mcd/', mcd_list, name='mcd-list'),
    path('mcd/<int:pk>/', mcd_detail, name='mcd-detail'),
    path('mcd/new/', mcd_create, name='mcd-create'),
    path('mcd/<int:pk>/edit/', mcd_update, name='mcd-update'),
    path('mcd/<int:pk>/delete/', mcd_delete, name='mcd-delete'),

    # Честный знак
    path('honest-sign/', honest_sign_list, name='honest-sign-list'),
    path('honest-sign/<int:pk>/', honest_sign_detail, name='honest-sign-detail'),
    path('honest-sign/new/', honest_sign_create, name='honest-sign-create'),
    path('honest-sign/<int:pk>/edit/', honest_sign_update, name='honest-sign-update'),
    path('honest-sign/<int:pk>/delete/', honest_sign_delete, name='honest-sign-delete'),

     # === USAIS / ЕГАИС ===
    path('egais/', usa_is_list, name='usais-list'),
    path('egais/<int:pk>/', usa_is_detail, name='usais-detail'),
    path('egais/new/', usa_is_create, name='usais-create'),
    path('egais/<int:pk>/edit/', usa_is_update, name='usais-update'),
    path('egais/<int:pk>/delete/', usa_is_delete, name='usais-delete'),

    # OFD
    path('ofd/', ofd_list, name='ofd-list'),
    path('ofd/<int:pk>/', ofd_detail, name='ofd-detail'),
    path('ofd/new/', ofd_create, name='ofd-create'),
    path('ofd/<int:pk>/edit/', ofd_update, name='ofd-update'),
    path('ofd/<int:pk>/delete/', ofd_delete, name='ofd-delete'),

    # Мобильные операторы
    path('mobile-operators/', mobile_operator_list, name='mobile-operator-list'),
    path('mobile-operators/<int:pk>/', mobile_operator_detail, name='mobile-operator-detail'),
    path('mobile-operators/new/', mobile_operator_create, name='mobile-operator-create'),
    path('mobile-operators/<int:pk>/edit/', mobile_operator_update, name='mobile-operator-update'),
    path('mobile-operators/<int:pk>/delete/', mobile_operator_delete, name='mobile-operator-delete'),

    # Интернет провайдер
    path('internet-providers/', internet_provider_list, name='internet-provider-list'),
    path('internet-providers/<int:pk>/', internet_provider_detail, name='internet-provider-detail'),
    path('internet-providers/new/', internet_provider_create, name='internet-provider-create'),
    path('internet-providers/<int:pk>/edit/', internet_provider_update, name='internet-provider-update'),
    path('internet-providers/<int:pk>/delete/', internet_provider_delete, name='internet-provider-delete'),

    # WiFi
    path('wifi/', wifi_list, name='wifi-list'),
    path('wifi/<int:pk>/', wifi_detail, name='wifi-detail'),
    path('wifi/new/', wifi_create, name='wifi-create'),
    path('wifi/<int:pk>/edit/', wifi_update, name='wifi-update'),
    path('wifi/<int:pk>/delete/', wifi_delete, name='wifi-delete'),

    # Роутер админ панель
    path('router-admin-panels/', router_admin_panel_list, name='router-admin-panel-list'),
    path('router-admin-panels/<int:pk>/', router_admin_panel_detail, name='router-admin-panel-detail'),
    path('router-admin-panels/new/', router_admin_panel_create, name='router-admin-panel-create'),
    path('router-admin-panels/<int:pk>/edit/', router_admin_panel_update, name='router-admin-panel-update'),
    path('router-admin-panels/<int:pk>/delete/', router_admin_panel_delete, name='router-admin-panel-delete'),


    path('personal-accounts/internet/', personal_account_internet_provider_list, name='personal-account-internet-provider-list'),
    path('personal-accounts/internet/<int:pk>/', personal_account_internet_provider_detail, name='personal-account-internet-provider-detail'),
    path('personal-accounts/internet/new/', personal_account_internet_provider_create, name='personal-account-internet-provider-create'),
    path('personal-accounts/internet/<int:pk>/edit/', personal_account_internet_provider_update, name='personal-account-internet-provider-update'),
    path('personal-accounts/internet/<int:pk>/delete/', personal_account_internet_provider_delete, name='personal-account-internet-provider-delete'),

    path('personal-accounts/mobile/', personal_account_mobile_operator_list, name='personal-account-mobile-operator-list'),
    path('personal-accounts/mobile/<int:pk>/', personal_account_mobile_operator_detail, name='personal-account-mobile-operator-detail'),
    path('personal-accounts/mobile/new/', personal_account_mobile_operator_create, name='personal-account-mobile-operator-create'),
    path('personal-accounts/mobile/<int:pk>/edit/', personal_account_mobile_operator_update, name='personal-account-mobile-operator-update'),
    path('personal-accounts/mobile/<int:pk>/delete/', personal_account_mobile_operator_delete, name='personal-account-mobile-operator-delete'),

    #  # CryptoPro
    # path('crypto-pro/<int:license_id>/', crypto_pro_detail, name='crypto-pro-detail'),
    # path('crypto-pro/new/', crypto_pro_create, name='crypto-pro-create'),

    # # FiscalNumber
    # path('fiscal-number/', fiscal_number_list, name='fiscal-number-list'),
    # path('fiscal-number/<int:license_id>/', fiscal_number_detail, name='fiscal-number-detail'),
    # path('fiscal-number/new/', fiscal_number_create, name='fiscal-number-create'),

]