from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.template import defaultfilters
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, time
from mongoengine.django.auth import REDIRECT_FIELD_NAME
from pymongo.son import SON
import string

from mongoengine.django.auth import User

from pixelcms.apps.entrytypes import markup, EntryType, PageType
from pixelcms.apps.menus import Menu, MenuItem
from pixelcms.apps.conf import GeneralSettings
from django.core.context_processors import request

def _lookup_template(name):
	return 'pixelcms/admin/%s.html' % name

@login_required
def manage_general_settings(request):

	form_class = GeneralSettings.AdminForm

	try:
		general_settings = GeneralSettings.objects.get()
	except GeneralSettings.DoesNotExist:
		return HttpResponseRedirect(reverse('install'))

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			# Get necessary post data from the form
			for field, value in form.cleaned_data.items():
				if field in general_settings._fields.keys():
					general_settings[field] = value
			general_settings.save()
			return HttpResponseRedirect(reverse('manage-general-settings'))
	else:
		fields = general_settings._fields.keys()
		field_dict = dict([(name, general_settings[name]) for name in fields])
		form = form_class(field_dict)
		
	context = {
		'title': 'Edit site general settings',
		'form': form,
	}

	return render_to_response(_lookup_template('manage_general_settings'), context,
								context_instance=RequestContext(request))

@login_required
def delete_menu_item(request):
	menu_item_id = request.POST.get('menu_item_id', None)
	menu_id = request.POST.get('menu_id',None)
	menu_item = MenuItem.objects.with_id(menu_item_id)
	if request.method == 'POST' and menu_item:
		MenuItem.objects.with_id(menu_item_id).delete()
	return HttpResponseRedirect(reverse('manage-menu-item', args=[menu_id]))

@login_required
def edit_menu_item(request, menu_item_id):
	menu_item = MenuItem.objects.with_id(menu_item_id)
	#Getting the right Menu instance (new request, non-POST)
	menu = menu_item.menu
	if not menu_item:
		return HttpResponseRedirect(reverse('manage-menu'))

	form_class = MenuItem.AdminForm

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			for field, value in form.cleaned_data.items():
				if field in menu_item._fields.keys():
					menu_item[field] = value
			#Overight the MenuItem's menu field's value
			menu_item.menu = menu
			menu_item.save()
			return HttpResponseRedirect(reverse('manage-menu-item',args=[menu.id]))
	else:
		fields = menu_item._fields.keys()
		field_dict = dict([(name, menu_item[name]) for name in fields])
		form = form_class(field_dict)

	context = {
		'title': 'Edit menu item %s' %menu_item.title,
		'form': form,
	}

	return render_to_response(_lookup_template('add_menu_item'), context,
								context_instance=RequestContext(request))

@login_required
def add_menu_item(request, menu_id):
	form_class = MenuItem.AdminForm
	menu = Menu.objects.with_id(menu_id)
	#if this is a validating request
	if request.method == 'POST':
		form = form_class(request.POST)
		#menu_id = request.POST.get('menu_id', None)
		if form.is_valid():
			menu_item = MenuItem(**form.cleaned_data)
			#Override form Menu instance
			menu_item.menu = menu
			# Save the entry to the DB
			menu_item.save()
			return HttpResponseRedirect(reverse('manage-menu-item',args=[menu.id]))
	#if this is a new request
	else:
		data = {
			'menu' : menu#display menu name, not id
		}
		form = form_class(initial=data)
		#form = form_class()
	context = {
		'title': 'Add new menu item to {%s} menu' % menu.title,
		'form': form,
	}
	return render_to_response(_lookup_template('add_menu_item'), context,
							  context_instance=RequestContext(request))

@login_required
def manage_menu_item(request, menu_id):
	menu = Menu.objects.with_id(menu_id)
	menu_item_list = MenuItem.objects(menu=Menu.objects.with_id(menu_id))

	context = {
		'title' : 'All %s menu items' %menu.title,
		'menu_item_list' : menu_item_list,
		'menu' : menu
	}

	return render_to_response(_lookup_template('manage_menu_item'), context,
								context_instance=RequestContext(request))

@login_required
def delete_menu(request):
	entry_id = request.POST.get('menu_id', None)
	if request.method == 'POST' and entry_id:
		Menu.objects.with_id(entry_id).delete()
	return HttpResponseRedirect(reverse('manage-menu'))

@login_required
def edit_menu(request, entry_id):
	entry = Menu.objects.with_id(entry_id)
	if not entry:
		return HttpResponseRedirect(reverse('admin'))

	form_class=Menu.AdminForm

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			for field, value in form.cleaned_data.items():
				if field in entry._fields.keys():
					entry[field] = value
			entry.save()
			return HttpResponseRedirect(reverse('manage-menu'))
	else:
		fields = entry._fields.keys()
		field_dict = dict([(name, entry[name]) for name in fields])
		form = form_class(field_dict)

	context = {
		'title': 'Edit menu %s' %entry.title,
		'form': form,
	}
	return render_to_response(_lookup_template('edit_menu'), context,
							  context_instance=RequestContext(request))

@login_required
def add_menu(request):
	form_class = Menu.AdminForm

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			entry = Menu(**form.cleaned_data)
			# Save the entry to the DB
			entry.save()
			return HttpResponseRedirect(reverse('manage-menu'))
	else:
		form = form_class()

	context = {
		'title': 'Add new menu',
		'form': form,
	}
	return render_to_response(_lookup_template('add_menu'), context,
							  context_instance=RequestContext(request))

@login_required
def manage_menu(request):
	menu_list = Menu.objects.order_by('title')

	context = {
		'title': 'Manage menus',
		'menu_list': menu_list,
	}
	return render_to_response(_lookup_template('manage_menu'), context,
								context_instance=RequestContext(request))

@login_required
def dashboard(request):
	"""Display the main admin page.
	"""
	entry_types = [e.type for e in EntryType._types.values()]
	entries = EntryType.objects.order_by('-publish_date')[:10]

	context = {
		'title' : 'Dashboard',
		'entry_types': entry_types,
		'entries': entries,
		'datenow': datetime.now(),
	}
	return render_to_response(_lookup_template('dashboard'), context,
							  context_instance=RequestContext(request))

@login_required
def manage_page(request):
	"""Display the main admin page.
	"""
	page_types = [e.type for e in PageType._types.values()]
	entries = PageType.objects.order_by('-publish_date')[:10]

	context = {
		'title': 'Manage pages',
		'entry_types': page_types,
		'entries': entries,
		'datenow': datetime.now(),
		'page_edit': 1,
	}
	return render_to_response(_lookup_template('manage_page'), context,
							  context_instance=RequestContext(request))

@login_required
def add_page(request):
	form_class = PageType.AdminForm

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			entry = PageType(**form.cleaned_data)

			# Save the entry to the DB
			entry.save()
			return HttpResponseRedirect(entry.get_absolute_url())
	else:
		initial = {
			'publish_date': datetime.now(),
			'publish_time': datetime.now().time(),
		}
		# Pass in inital values from query string - added by bookmarklet
		for field, value in request.GET.items():
			if field in form_class.base_fields:
				initial[field] = value

		if 'title' in initial:
			initial['slug'] = defaultfilters.slugify(initial['title'])

		form = form_class(initial=initial)

	context = {
		'title': 'Add new page',
		'form': form,
	}
	return render_to_response(_lookup_template('add_page'), context,
							  context_instance=RequestContext(request))


@login_required
def edit_page(request, entry_id):
	entry = PageType.objects.with_id(entry_id)
	if not entry:
		return HttpResponseRedirect(reverse('admin'))

	# Select correct form for entry type
	form_class = entry.AdminForm

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			# Get necessary post data from the form
			for field, value in form.cleaned_data.items():
				if field in entry._fields.keys():
					entry[field] = value
			entry.save()
			return HttpResponseRedirect(entry.get_absolute_url())
	else:
		fields = entry._fields.keys()
		field_dict = dict([(name, entry[name]) for name in fields])

		# publish_time and expiry_time are not initialised as they
		# don't have a field in the DB
		field_dict['publish_time'] = time(
			hour=entry.publish_date.hour,
			minute=entry.publish_date.minute,
			second=entry.publish_date.second,
		)
		if field_dict['expiry_date']:
			field_dict['expiry_time'] = time(
				hour=entry.expiry_date.hour,
				minute=entry.expiry_date.minute,
				second=entry.expiry_date.second,
			)
		form = form_class(field_dict)

	context = {
		'title': 'Edit a page',
		'form': form,
	}
	return render_to_response(_lookup_template('add_page'), context,
							  context_instance=RequestContext(request))

@login_required
def delete_page(request):
	entry_id = request.POST.get('entry_id', None)
	if request.method == 'POST' and entry_id:
		PageType.objects.with_id(entry_id).delete()
	return HttpResponseRedirect(reverse('manage-page'))


@login_required
def manage_entry(request):
	entry_types = [e.type for e in EntryType._types.values()]
	entries = EntryType.objects.order_by('-publish_date')[:10]

	context = {
		'title': 'Manage posts',
		'entry_types': entry_types,
		'entries': entries,
		'datenow': datetime.now(),
	}
	return render_to_response(_lookup_template('manage_entry'), context,
							  context_instance=RequestContext(request))


@login_required
def edit_entry(request, entry_id):
	"""Edit an existing entry.
	"""
	entry = EntryType.objects.with_id(entry_id)
	if not entry:
		return HttpResponseRedirect(reverse('admin'))

	# Select correct form for entry type
	form_class = entry.AdminForm

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			# Get necessary post data from the form
			for field, value in form.cleaned_data.items():
				if field in entry._fields.keys():
					entry[field] = value
			entry.save()
			return HttpResponseRedirect(entry.get_absolute_url())
	else:
		fields = entry._fields.keys()
		field_dict = dict([(name, entry[name]) for name in fields])

		# tags are stored as a list in the db, convert them back to a string
		field_dict['tags'] = ', '.join(field_dict['tags'])

		# publish_time and expiry_time are not initialised as they
		# don't have a field in the DB
		field_dict['publish_time'] = time(
			hour=entry.publish_date.hour,
			minute=entry.publish_date.minute,
			second=entry.publish_date.second,
		)
		if field_dict['expiry_date']:
			field_dict['expiry_time'] = time(
				hour=entry.expiry_date.hour,
				minute=entry.expiry_date.minute,
				second=entry.expiry_date.second,
			)
		form = form_class(field_dict)

	link_url = reverse('add-entry', args=['Link'])
	video_url = reverse('add-entry', args=['Video'])
	context = {
		'title': 'Edit an entry',
		'type': type,
		'form': form,
		'link_url': request.build_absolute_uri(link_url),
		'video_url': request.build_absolute_uri(video_url),
	}
	return render_to_response(_lookup_template('add_entry'), context,
							  context_instance=RequestContext(request))

@login_required
def add_entry(request, type):
	"""Display the 'Add an entry' form when GET is used, and add an entry to
	the database when POST is used.
	"""
	# 'type' must be a valid entry type (e.g. html, image, etc..)
	if type.lower() not in EntryType._types:
		raise Http404

	# Use correct entry type Document class
	entry_type = EntryType._types[type.lower()]
	# Select correct form for entry type
	form_class = entry_type.AdminForm

	if request.method == 'POST':
		form = form_class(request.POST)
		if form.is_valid():
			entry = entry_type(**form.cleaned_data)

			# Save the entry to the DB
			entry.save()
			return HttpResponseRedirect(entry.get_absolute_url())
	else:
		initial = {
			'publish_date': datetime.now(),
			'publish_time': datetime.now().time(),
			'comments_enabled': True,
		}
		# Pass in inital values from query string - added by bookmarklet
		for field, value in request.GET.items():
			if field in form_class.base_fields:
				initial[field] = value

		if 'title' in initial:
			initial['slug'] = defaultfilters.slugify(initial['title'])

		form = form_class(initial=initial)

	link_url = reverse('add-entry', args=['Link'])
	video_url = reverse('add-entry', args=['Video'])
	context = {
		'title': 'Add %s Entry' % type,
		'type': type,
		'form': form,
		'link_url': request.build_absolute_uri(link_url),
		'video_url': request.build_absolute_uri(video_url),
	}
	return render_to_response(_lookup_template('add_entry'), context,
							  context_instance=RequestContext(request))

@login_required
def delete_entry(request):
	"""Delete an entry from the database.
	"""
	entry_id = request.POST.get('entry_id', None)
	if request.method == 'POST' and entry_id:
		EntryType.objects.with_id(entry_id).delete()
	return HttpResponseRedirect(reverse('recent-entries'))

@login_required
def delete_comment(request):
	"""Delete a comment from the database.
	"""
	comment_id = request.POST.get('comment_id', None)
	if request.method == 'POST' and comment_id:
		# Delete matching comment from entry
		entry = EntryType.objects(comments__id=comment_id).first()
		if entry:
			entry.comments = [c for c in entry.comments if c.id != comment_id]
			entry.save()
		return HttpResponseRedirect(entry.get_absolute_url()+'#comments')
	return HttpResponseRedirect(reverse('recent-entries'))

