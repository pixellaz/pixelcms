from django.conf import settings

def auth(request):
    if hasattr(request, 'user'):
        return {'user': request.user}
    return {}