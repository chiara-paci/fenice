from django_registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django import forms

from django.contrib.auth import get_user_model
User=get_user_model()

class FeniceRegistrationForm(RegistrationFormUniqueEmail):
    class Meta(RegistrationFormUniqueEmail.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        RegistrationFormUniqueEmail.__init__(self,*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'placeholder': 'Choice an username . . .'})
        self.fields['email'].widget = forms.EmailInput(attrs={'placeholder':'Enter your email . . .'}) 
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder':'Choice a password . . .'}) 
        self.fields['password2'].widget = forms.PasswordInput(attrs={'placeholder':'Confirm the password . . .'}) 

class FeniceAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder':'Password'}))
