from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from pixelcms.apps.auth.signup import SignupForm
from django.conf import settings
from django.template import RequestContext

def _lookup_template(name):
    theme = getattr(settings, 'PIXELCMS_THEME', 'default')
    return 'pixelcms/themes/%s/%s.html' % (theme, name)

def signup(request):
	if request.method == 'POST':
		form = SignupForm(data=request.POST)
		if form.is_valid():
			new_user = form.save()
			return HttpResponseRedirect(reverse('log-in'))
	else:
		form = SignupForm()
	
	context = {
		'form': form,
		'title': 'User Signup'
	}
	return render_to_response(_lookup_template('signup'), context,
								context_instance=RequestContext(request))