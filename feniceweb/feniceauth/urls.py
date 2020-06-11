from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.urls import path

from django_registration.backends.activation.views import RegistrationView,ActivationView

from feniceauth.forms import FeniceRegistrationForm

app_name="feniceauth"

# django auth
urlpatterns=[
    path('login/', auth_views.LoginView.as_view(), 
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), 
         name='logout'),
    path('password_change/', 
         login_required(auth_views.PasswordChangeView.as_view(success_url=reverse_lazy("feniceauth:password_change_done"))), 
         name="password_change"),
    path('password_change/done/', 
         login_required(auth_views.PasswordChangeDoneView.as_view()), 
         name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy("feniceauth:password_reset_done")), 
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy("feniceauth:password_reset_complete")), 
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
]

# django_registration
urlpatterns += [
    path(
        "activate/complete/",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="activation_complete",
    ),
    path(
        "activate/<str:activation_key>/",
        ActivationView.as_view(success_url=reverse_lazy("feniceauth:activation_complete")), # django_registration/activation_failed.html
        name="activate",
    ),
    path(
        "register/",
        RegistrationView.as_view(
            form_class=FeniceRegistrationForm,
            success_url=reverse_lazy("feniceauth:complete"),
            disallowed_url=reverse_lazy("feniceauth:disallowed")
        ), # django_registration/registration_form.html
        name="register",
    ),
    path(
        "register/complete/",
        TemplateView.as_view(
            template_name="django_registration/registration_complete.html"
        ),
        name="complete",
    ),
    path(
        "register/closed/",
        TemplateView.as_view(
            template_name="django_registration/registration_closed.html"
        ),
        name="disallowed",
    ),
]

urlpatterns += [
    path('profile/',
         login_required(TemplateView.as_view(template_name="feniceauth/profile.html")), 
         name="profile"),
]
