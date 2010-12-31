from django.template import Library, Node, TemplateSyntaxError
import re
from pixelcms.apps.menus import Menu, MenuItem

register = Library()

class MenuItemNode(Node):
	
	def __init__(self, menu_id, context_var):
		self.menu_id, self.context_var = menu_id, context_var
		
	def render(self, context):
		menu_instance = Menu.objects.get(unique_id=self.menu_id)
		context[self.context_var] = MenuItem.objects(menu=menu_instance)
		return ''

@register.simple_tag
def active_fixed(request, pattern):
	if request.get_full_path() == pattern:
		return 'class="active"'
	return ''

@register.simple_tag
def is_active(request, url):
	if request.path == url:
		return 'class="current"'
	return ''

@register.tag
def get_menu_items(parser, token):
	# Usage:
    #   {% get_menu_items menu_name as menu_item_list %}
    #   {% for item in menu_item_list %}
    #       <li>{{ item.title }}</li>
    #   {% endfor %}
	bits = token.contents.split()
	if len(bits) != 4:
		raise TemplateSyntaxError, "get_menu_items tag takes exactly three arguments"

	return MenuItemNode(bits[1],bits[3])
