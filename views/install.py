from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from pixelcms.apps.auth import User
from pixelcms.apps.conf import GeneralSettings
from pixelcms.apps.menus import Menu, MenuItem
from django.template import RequestContext
from django.core.urlresolvers import reverse

def _lookup_template(name):
	return 'pixelcms/admin/%s.html' % name
	
def create_menu():
	default_menu = Menu(title='Main', unique_id='main_menu')
	default_menu.save()
	home_menu_item = MenuItem(title = 'Home', menu = default_menu, url = '/',
					label = 'Home', order = 0, parent = '')
	home_menu_item.save()
	blog_menu_item = MenuItem(title = 'Blog', menu = default_menu, url = '/blog/',
									label = 'Blog', order = 1, parent = '')
	blog_menu_item.save()
	
	return ''
	
def create_data(request):
	s_form = GeneralSettings.AdminForm
	u_form = User.AdminForm
	user_form = u_form(request.POST)
	if user_form.is_valid():
		user = User()
		user.create_user(user_form.cleaned_data['username'], user_form.cleaned_data['password'], 
													user_form.cleaned_data['email'])
		user.is_superuser = True
		user.is_staff = True
		user.save()
		
	settings_form = s_form(request.POST)
	if settings_form.is_valid():
		settings = GeneralSettings(**settings_form.cleaned_data)
		settings.save()
	create_menu()
	return HttpResponseRedirect(reverse('dashboard'))

def install(request):
	
	# First check if there is no General Settings exist, hence new site setup.
	try:
		settings = GeneralSettings.objects.get()
	except GeneralSettings.DoesNotExist:
		if request.method == 'POST':
			create_data(request)
		else:
			u_form = User.AdminForm
			user_form = u_form()
			s_form = GeneralSettings.AdminForm
			settings_form = s_form()
			context = {
				'title': 'Site initial setup',
				'user_form': user_form,
				'settings_form': settings_form,
			}
			return render_to_response(_lookup_template('install'), context,
										context_instance=RequestContext(request))
	return HttpResponseRedirect(reverse('dashboard'))