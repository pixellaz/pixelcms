from django import forms
from mongoengine import *


class Menu(Document):
	title = StringField(max_length=50,required=True)
	unique_id = StringField(max_length=25, required=True, unique=True)
	
	def save(self):
		super(Menu, self).save()
	
	def __unicode__(self):
		return self.title
		
	class Meta:
	    verbose_name = 'menu'
	    verbose_name_plural = 'menus'
		
	class AdminForm(forms.Form):
		title = forms.CharField(help_text='Title of menu')
		unique_id = forms.CharField(help_text='Unique id in format of \'menu_name\'')
	
class MenuItem(Document):
	title = StringField(max_length=50,required=True)
	menu = ReferenceField(Menu, required=True)
	url = StringField(required=True)
	label = StringField(max_length=50, required=True)
	order = IntField(default=0, required=True)
	parent = StringField(required=False)
	
	meta = {
	        'ordering': ['order']
	}
	
	type = 'Menu Item'
	
	@queryset_manager
	def objects(doc_cls, queryset):
		return queryset.order_by('order')
		
	def save(self):
		super(MenuItem, self).save()
	
	def __unicode__(self):
		return self.title
		
	class AdminForm(forms.Form):
		title = forms.CharField(help_text='Title of the menu item')
		menu = forms.CharField()
		url = forms.CharField()
		label = forms.CharField()
		order = forms.IntegerField(max_value=10, min_value=0)
		parent = forms.CharField(required=False)
		