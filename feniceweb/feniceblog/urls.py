from django.urls import path,re_path

from  django.views.generic import ListView, DetailView

from django.views.generic.dates import ArchiveIndexView

#from . import views

from . import models

app_name="feniceblog"

urlpatterns=[
    path('article/', ArchiveIndexView.as_view(model=models.Article,date_field="publishing_date",allow_empty=True), name='article_archive'),
    path('article/<int:pk>/', DetailView.as_view(model=models.Article), name='article_detail'),
    path('article/<int:pk>-<str:slug>/', DetailView.as_view(model=models.Article), name='article_detail'),
]
