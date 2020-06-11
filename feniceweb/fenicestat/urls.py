from django.urls import path

from . import views

app_name="fenicestat"

urlpatterns=[
    path('browser/', views.BrowserListCreateView.as_view(), name='browser_list'),
    path('browser/', views.BrowserListCreateView.as_view(), name='browser_create'),
]
