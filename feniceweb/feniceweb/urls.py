"""feniceweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,include,reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

import feniceauth.urls
import fenicegdpr.urls
import fenicestat.urls
import feniceblog.urls

import ckeditor_uploader.urls

import fenicemisc.views
import fenicemisc.decorators
import feniceerrors.handlers

from decorator_include import decorator_include

admin.site.site_header=_(settings.COMMUNITY_NAME+' Administration')
admin.site.site_title=_(settings.COMMUNITY_NAME+' Site Admin')
admin.site.index_title=_(settings.COMMUNITY_NAME+' Administration')

urlpatterns = [
    path(r'', fenicemisc.views.HomePageView.as_view(), name="home"),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path(r'admin/', decorator_include([fenicemisc.decorators.staff_or_404], admin.site.urls)),
    path(r'stat/',  include(fenicestat.urls)),
    path(r'credits/', fenicemisc.views.CreditsView.as_view(), name="credits"),
    path(r'accounts/', include(feniceauth.urls)),
    path(r'privacy/', include(fenicegdpr.urls)),
    path(r'ckeditor/', include(ckeditor_uploader.urls)),
    path(r'blog/', include(feniceblog.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = feniceerrors.handlers.response_handler_404
handler403 = feniceerrors.handlers.response_handler_403
