from django.urls import path

from . import views

app_name="fenicegdpr"

urlpatterns=[
    path('policy/', views.PolicyView.as_view(), 
         name='policy'),
]
