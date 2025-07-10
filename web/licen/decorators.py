from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from licen.models import UserProfile

def role_required(*allowed_roles):
    """
    Декоратор для проверки роли пользователя.
    Пример использования:
        @role_required(UserProfile.Role.ADMIN)
        def view(request, ...): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                raise PermissionDenied("У пользователя нет профиля.")
            if profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("У вас недостаточно прав для доступа к этой странице.")
        return _wrapped_view
    return decorator