from .models import User


def current_user(request):
    user = getattr(request, 'app_user', None)
    if user is None:
        user_id = request.session.get('user_id')
        if user_id:
            user = User.objects.filter(pk=user_id).first()
    return {'current_user': user}
