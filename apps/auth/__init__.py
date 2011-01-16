from mongoengine.django.auth import User
from mongoengine import *
from django import forms

class Group(Document):
	title = StringField()
	permission = StringField()
		
class User(User):
	group = ReferenceField(Group)
	
	class AdminForm(forms.Form):
		username = forms.CharField(max_length=20, required=True)
		first_name = forms.CharField(max_length=30)
		last_name = forms.CharField(max_length=30)
		email = forms.EmailField()
		password = forms.CharField(label='Password',widget=forms.PasswordInput(render_value=False))
		is_staff = forms.BooleanField(initial=False)
		is_active = forms.BooleanField(initial=True)
		is_superuser = forms.BooleanField(initial=False)
		
class UserAuthBackend(object): 
    def authenticate(self, username=None, password=None): 
        user = User.objects(username=username.lower()).first() 
        if user: 
            if password and user.check_password(password): 
                return user 
        return None 
    def get_user(self, user_id): 
        return User.objects.with_id(user_id)