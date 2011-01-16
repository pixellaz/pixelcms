from django import forms
from mongoengine import *
from mongoengine.django.auth import User

class GeneralSettings(Document):
	site_title = StringField()
	tagline = StringField()
	site_url = URLField()
	footer_text = StringField()

	def save(self):
		super(GeneralSettings, self).save()

	class Meta:
	    verbose_name = 'General Setting'
	    verbose_name_plural = 'General Settings'

	class AdminForm(forms.Form):
		site_title = forms.CharField()
		tagline = forms.CharField()
		site_url = forms.URLField()
		footer_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 5}))