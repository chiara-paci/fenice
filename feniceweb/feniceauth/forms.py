from django_registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django import forms
from django.utils.translation import gettext_lazy as _


from django.core.exceptions import ValidationError


from django.contrib.auth import get_user_model,password_validation
User=get_user_model()

class FeniceRegistrationForm(RegistrationFormUniqueEmail):
    class Meta(RegistrationFormUniqueEmail.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        RegistrationFormUniqueEmail.__init__(self,*args, **kwargs)
        self.fields['username'].help_text = _('Minimum 3, maximum 150 characters')
        self.fields['username'].widget = forms.TextInput(attrs={
            'placeholder': _('Choice an username . . .'),
            "minlength": "3",
            "maxlength": "150"
        })
        self.fields['email'].help_text = _('A valid email address')
        self.fields['email'].widget = forms.EmailInput(attrs={
            'placeholder':_('Enter your email . . .'),
            'pattern': r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$',
        }) 
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'placeholder':_('Choice a password . . .'),
            "minlength": "8",
        }) 
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'placeholder':_('Confirm the password . . .'),
            "minlength": "8",
        }) 

    def _post_clean(self):
        forms.ModelForm._post_clean(self)
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password1')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password1', error)

class FeniceAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder': _('Username')}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder':_('Password')}))
