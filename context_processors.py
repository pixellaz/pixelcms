from django.conf import settings

def auth(request):
    if hasattr(request, 'user'):
        return {'user': request.user}
    return {}

def site_info(context):
	title = getattr(settings, 'SITE_INFO_TITLE', 'Pixellaz')
	description = getattr(settings, 'SITE_INFO_DESC', 'Pixellaz Official Site')
	home_url = getattr(settings, 'SITE_HOME_URL', 'http://127.0.0.1:8000')
	admin_desc = getattr(settings, 'SITE_ADMIN_TITLE', 'Administration')
	return {
	    'SITE_INFO_TITLE': title,
	    'SITE_INFO_DESC': description,
		'SITE_ADMIN_TITLE': admin_desc,
		'SITE_HOME_URL': home_url,
	}

def site_footer(context):
    footer_text = getattr(settings, 'SITE_FOOTER_TEXT', 'Copyright &copy 2010 Pixellaz Company Limited.')
    return {
        'SITE_FOOTER_TEXT': footer_text,
    }