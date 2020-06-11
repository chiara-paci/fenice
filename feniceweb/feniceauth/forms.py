from django_registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth import get_user_model
User=get_user_model()

class FeniceRegistrationForm(RegistrationFormUniqueEmail):
    class Meta(RegistrationFormUniqueEmail.Meta):
        model = User
