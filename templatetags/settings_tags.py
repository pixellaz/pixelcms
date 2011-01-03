from django.template import Library, Node, TemplateSyntaxError
import re

from pixelcms.apps.conf import GeneralSettings
register = Library()

@register.simple_tag
def site_title():
	settings = GeneralSettings.objects.get()
	return settings.site_title
	
@register.simple_tag
def tagline():
	settings = GeneralSettings.objects.get()
	return settings.tagline
	
@register.simple_tag
def site_url():
	settings = GeneralSettings.objects.get()
	return settings.site_url
	
@register.simple_tag
def footer_text():
	settings = GeneralSettings.objects.get()
	return settings.footer_text