from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import User


def permission_required(*roles, owner_model=None):
    """Authorize the session user against this project's custom User model."""
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('login')
            user = User.objects.filter(pk=user_id).first()
            if user is None:
                request.session.flush()
                return redirect('login')
            if user.role not in roles:
                raise PermissionDenied
            if owner_model is not None and user.role == 'user':
                if not owner_model.objects.filter(pk=kwargs.get('pk'), user_id=user.pk).exists():
                    raise PermissionDenied
            request.app_user = user
            return view(request, *args, **kwargs)
        return wrapped
    return decorate
