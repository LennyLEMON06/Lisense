# licen/context_processors.py

from django.urls import reverse
from django.utils.translation import gettext as _

def get_breadcrumbs(request):
    """
    Автоматическое построение хлебных крошек
    """
    breadcrumbs = []

    # Города
    breadcrumbs.append({
        'name': _('Города'),
        'url': reverse('city-list')
    })

    if 'city' in request.resolver_match.kwargs:
        city_id = request.resolver_match.kwargs['city_id']
        from licen.models import City
        try:
            city = City.objects.get(id=city_id)
            breadcrumbs.append({
                'name': str(city.name),
                'url': reverse('city-detail', args=[city.id])
            })
        except City.DoesNotExist:
            pass

    # Сети
    if 'network' in request.resolver_match.kwargs or 'network_id' in request.resolver_match.kwargs:
        network_id = request.resolver_match.kwargs.get('network', request.resolver_match.kwargs.get('network_id'))
        from licen.models import Network
        try:
            network = Network.objects.get(id=network_id)
            breadcrumbs.extend([
                {'name': _('Сети'), 'url': reverse('network-list')},
                {'name': str(network), 'url': reverse('network-detail', args=[network.id])}
            ])
        except Network.DoesNotExist:
            pass

    # Юрлицо
    if 'legal_entity' in request.resolver_match.kwargs or 'pk' in request.resolver_match.kwargs:
        legal_entity_id = request.resolver_match.kwargs.get('legal_entity', request.resolver_match.kwargs.get('pk'))
        from licen.models import LegalEntity
        try:
            legal_entity = LegalEntity.objects.get(id=legal_entity_id)
            breadcrumbs.extend([
                {'name': _('Юрлица'), 'url': reverse('legal-entity-list')},
                {'name': str(legal_entity), 'url': reverse('legal-entity-detail', args=[legal_entity.id])}
            ])
        except LegalEntity.DoesNotExist:
            pass

    # Адрес
    if 'address' in request.resolver_match.kwargs or 'pk' in request.resolver_match.kwargs:
        address_id = request.resolver_match.kwargs.get('address', request.resolver_match.kwargs.get('pk'))
        from licen.models import Address
        try:
            address = Address.objects.get(id=address_id)
            breadcrumbs.extend([
                {'name': _('Адреса'), 'url': reverse('address-list')},
                {'name': str(address), 'url': reverse('address-detail', args=[address.id])}
            ])
        except Address.DoesNotExist:
            pass

    return {'breadcrumbs': breadcrumbs}