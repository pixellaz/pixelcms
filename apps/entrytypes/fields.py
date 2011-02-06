from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Widget, Select, TextInput
from django.forms.extras.widgets import SelectDateWidget

import captcha


class ReCaptcha(forms.widgets.Widget):
    """Renders the proper ReCaptcha widget
    """
    def render(self, name, value, attrs=None):
        html = captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY)
        return mark_safe(u'%s' % html)

    def value_from_datadict(self, data, files, name):
        return [data.get('recaptcha_challenge_field', None), 
                data.get('recaptcha_response_field', None)]


class ReCaptchaField(forms.CharField):
    """Provides ReCaptcha functionality using ReCaptcha python client
    """
    default_error_messages = {
        'captcha_invalid': _(u'Invalid captcha.')
    }

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptcha
        self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        check_captcha = captcha.submit(recaptcha_challenge_value, 
            recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.util.ValidationError(
                    self.error_messages['captcha_invalid'])
        return values[0]

