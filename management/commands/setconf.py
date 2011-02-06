import getpass
import hashlib
from django.core.management.base import BaseCommand

from pixelcms.apps.conf import GeneralSettings


class Command(BaseCommand):
    
    def _get_string(self, prompt, reader_func=raw_input, required=True):
        """Helper method to get a non-empty string.
        """
        string = ''
        while not string:
            string = reader_func(prompt + ': ')
            if not required:
                break
        return string

    def handle(self, **kwargs):
        site_title = self._get_string('Site Title')
        tagline = self._get_string('Site Tagline', required=False)
        site_url = self._get_string('Site URL')
        footer_text = self._get_string('Set you site footer text')

        settings = GeneralSettings(site_title=site_title)
        settings.tagline = tagline
        settings.site_url = site_url
        settings.footer_text = footer_text
        settings.save()

        print 'Setting for site "%s" successfully added' % site_title
