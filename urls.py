from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.conf import settings

from pixelcms.views.core import (home,recent_entries, tagged_entries, entry_detail, 
                               tag_cloud, archive, RssFeed, AtomFeed, page_detail)
from pixelcms.views.admin import (dashboard, delete_entry, add_entry, edit_entry,manage_entry,
								delete_comment, manage_page, add_page, edit_page, delete_page, 
								manage_menu, add_menu, edit_menu, delete_menu, manage_menu_item,
								add_menu_item, delete_menu_item, edit_menu_item,manage_general_settings,
								)
from pixelcms.views.install import (install)
from pixelcms.views.auth import (signup)

feeds = {
    'rss': RssFeed,
	'atom': AtomFeed,
}

theme = getattr(settings, 'PIXELCMS_THEME', 'default')

urlpatterns = patterns('',
	url('^$', home, name='home'),
    url('^blog/$', recent_entries, name='recent-entries'),
    url('^blog/(?P<page_number>\d+)/$', recent_entries, name='recent-entries'),
    url('^blog/(\d{4}/\w{3}/\d{2})/([\w-]+)/$', entry_detail, name='entry-detail'),
    url('^tag/(?P<tag>[a-z0-9_-]+)/$', tagged_entries, name='tagged-entries'),
    url('^tag/(?P<tag>[a-z0-9_-]+)/(?P<page_number>\d+)/$', tagged_entries, 
        name='tagged-entries'),
    url('^archive/$', archive, name='archive'),
    url('^archive/(?P<page_number>\d+)/$', archive, name='archive'),
    url('^archive/(?P<entry_type>[a-z0-9_-]+)/$', archive, name='archive'),
    url('^archive/(?P<entry_type>[a-z0-9_-]+)/(?P<page_number>\d+)/$',
        archive, name='archive'),
    url('^tags/$', tag_cloud, name='tag-cloud'),
	url('^admin/install/$', install, name='install'),
    url('^admin/$', dashboard, name='dashboard'),
	url('^admin/settings/$', manage_general_settings, name='manage-general-settings'),
	url('^admin/menu/$', manage_menu, name='manage-menu'),
	url('^admin/menu/add/$', add_menu, name='add-menu'),
	url('^admin/menu/edit/(\w+)/$', edit_menu, name='edit-menu'),
	url('^admin/menu/delete/$', delete_menu, name='delete-menu'),
	url('^admin/menu/edit-item/(\w+)/$', manage_menu_item, name='manage-menu-item'),
	url('^admin/menu/item/add/(\w+)/$', add_menu_item, name='add-menu-item'),
	url('^admin/menu/item/edit/(\w+)/$', edit_menu_item, name='edit-menu-item'),
	url('^admin/menu/item/delete/$', delete_menu_item, name='delete-menu-item'),
	url('^admin/page/$', manage_page, name='manage-page'),
	url('^admin/page/add/$', add_page, name='add-page'),
	url('^admin/page/edit/(\w+)/$', edit_page, name='edit-page'),
	url('^admin/page/delete/$', delete_page, name='delete-page'),
	url('^admin/blog/$', manage_entry, name='manage-entry'),
    url('^admin/blog/add/(\w+)/$', add_entry, name='add-entry'),
    url('^admin/blog/edit/(\w+)/$', edit_entry, name='edit-entry'),
    url('^admin/blog/delete/$', delete_entry, name='delete-entry'),
    url('^admin/delete-comment/$', delete_comment, name='delete-comment'),
	url('^account/signup/$', signup, name='signup'),
    url('^account/login/$', login, {'template_name': 'pixelcms/themes/%s/login.html' % theme}, 
        name='log-in'),
    url('^account/logout/$', logout, {'next_page': '/'}, name='log-out'),
    url('^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}, name='feeds'),
	(r'^tiny_mce/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/pixelcms/themes/default/js/tiny_mce'}),
	url('^(?P<slug>[-\w]+)/$', page_detail, name='page-detail'),
)
