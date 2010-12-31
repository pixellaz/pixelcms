from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.functional import lazy

from datetime import datetime, timedelta

from pixelcms.apps.entrytypes import markup, EntryType, Comment, PageType
from pixelcms.apps.entrytypes.core import HtmlComment

NO_ENTRIES_MESSAGES = (
    ('Have <a href="http://icanhazcheezburger.com">some kittens</a> instead.'),
    ('Have <a href="http://xkcd.com">a comic</a> instead.'),
    ('How about <a href="http://www.youtube.com/watch?v=oHg5SJYRHA0">'
     'a song</a> instead.'),
)

def _lookup_template(name):
    theme = getattr(settings, 'PIXELCMS_THEME', 'default')
    return 'pixelcms/themes/%s/%s.html' % (theme, name)

def home(request):
	context = {
    	'title': 'Welcome To Pixelaz Official Homepage',
	}
	return render_to_response(_lookup_template('home'), context,
		context_instance=RequestContext(request))

def archive(request, entry_type=None, page_number=1):
    """Display an archive of posts.
    """
    num = getattr(settings, 'PIXELCMS_NUM_ENTRIES_PER_PAGE', 10)
    entry_types = [e.type for e in EntryType._types.values()]
    entry_class = EntryType
    type = "All"

    if entry_type and entry_type in [e.lower() for e in entry_types]:
        entry_class = EntryType._types[entry_type.lower()]
        type = entry_class.type

    paginator = Paginator(entry_class.live_entries(), num)
    try:
        entries = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)

    context = {
        'entry_types': entry_types,
        'entries': entries,
        'num_entries': entry_class.live_entries().count(),
        'entry_type': type,
    }
    return render_to_response(_lookup_template('archive'), context,
                              context_instance=RequestContext(request))

def page_detail(request,slug):
    entry = PageType.objects(slug=slug)[0]
    context = {
        'title': entry.title,
        'entry': entry,
    }
    return render_to_response(_lookup_template('page_detail'), context,
                              context_instance=RequestContext(request))


def recent_entries(request, page_number=1):
    """Show the [n] most recent entries.
    """
    num = getattr(settings, 'PIXELCMS_NUM_ENTRIES_PER_PAGE', 10)
    entry_list = EntryType.live_entries()
    paginator = Paginator(entry_list, num)
    try:
        entries = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)
    context = {
        'title': 'Recent Entries',
        'entries': entries,
        'no_entries_messages': NO_ENTRIES_MESSAGES,
    }
    return render_to_response(_lookup_template('list_entries'), context,
                              context_instance=RequestContext(request))

def entry_detail(request, date, slug):
    """Display one entry with the given slug and date.
    """
    try:
        today = datetime.strptime(date, "%Y/%b/%d")
        tomorrow = today + timedelta(days=1)
    except:
        raise Http404

    try:
        entry = EntryType.objects(publish_date__gte=today, 
                                  publish_date__lt=tomorrow, slug=slug)[0]
    except IndexError:
        raise Http404

    # Select correct form for entry type
    form_class = Comment.CommentForm

    if request.method == 'POST':
        form = form_class(request.user, request.POST)
        if form.is_valid():
            # Get necessary post data from the form
            comment = HtmlComment(**form.cleaned_data)
            if request.user.is_authenticated():
                comment.is_admin = True
            # Update entry with comment
            q = EntryType.objects(id=entry.id)
            comment.rendered_content = markup(comment.body, escape=True,
                                              small_headings=True)
            q.update(push__comments=comment)

            return HttpResponseRedirect(entry.get_absolute_url()+'#comments')
    else:
        form = form_class(request.user)

    # Check for comment expiry
    comments_expired = False
    if entry.comments_expiry_date:
        if entry.comments_expiry_date < datetime.now():
            comments_expired = True

    context = {
        'entry': entry,
        'form': form,
        'comments_expired': comments_expired,
		'datenow': datetime.now(),
    }
    return render_to_response(_lookup_template('entry_detail'), context,
                              context_instance=RequestContext(request))

def tagged_entries(request, tag=None, page_number=1):
    """Show a list of all entries with the given tag.
    """
    tag = tag.strip().lower()
    num = getattr(settings, 'PIXELCMS_NUM_ENTRIES_PER_PAGE', 10)
    entry_list = EntryType.live_entries(tags=tag)
    paginator = Paginator(entry_list, num)
    try:
        entries = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)
    context = {
        'title': 'Entries Tagged "%s"' % tag,
        'entries': entries,
        'no_entries_messages': NO_ENTRIES_MESSAGES,
    }
    return render_to_response(_lookup_template('list_entries'), context,
                              context_instance=RequestContext(request))

def tag_cloud(request):
    """A page containing a 'tag-cloud' of the tags present on entries.
    """
    entries = EntryType.live_entries
    
    freqs = entries.item_frequencies('tags', normalize=True)
    freqs = sorted(freqs.iteritems(), key=lambda (k,v):(v,k))
    freqs.reverse()

    context = {
        'tag_cloud': freqs,
    }
    return render_to_response(_lookup_template('tag_cloud'), context,
                              context_instance=RequestContext(request))


_lazy_reverse = lazy(reverse, str)

class RssFeed(Feed):
    title = getattr(settings, 'SITE_INFO_TITLE', 'Pixellaz Recent Entries')
    link = _lazy_reverse('recent-entries')
    description = ""
    title_template = 'pixelcms/feeds/rss_title.html'
    description_template = 'pixelcms/feeds/rss_description.html'

    def items(self):
        return EntryType.live_entries[:30]

    def item_pubdate(self, item):
        return item.publish_date


class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description
    title_template = 'pixelcms/feeds/atom_title.html'
    description_template = 'pixelcms/feeds/atom_description.html'
