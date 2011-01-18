from django.conf import settings

def auth(request):
    if hasattr(request, 'user'):
        return {'user': request.user}
    return {}

def site_info(context):
    title = getattr(settings, 'SITE_INFO_TITLE', 'WAYS')
    description = getattr(settings, 'SITE_INFO_DESC', 'We are your store')
    return {
        'SITE_INFO_TITLE': title,
        'SITE_INFO_DESC': description,
    }
