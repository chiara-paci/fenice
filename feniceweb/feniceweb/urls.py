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

from machina import urls as machina_urls

import feniceauth.urls
import fenicegdpr.urls
import fenicestat.urls
import feniceblog.urls

import ckeditor_uploader.urls
import avatar.urls
import helpdesk.urls

import fenicemisc.views
import fenicemisc.decorators
import feniceerrors.handlers

from decorator_include import decorator_include

params={
    "community_name": settings.COMMUNITY_NAME
}

admin.site.site_header=_('%(community_name)s Administration') % params
admin.site.site_title=_('%(community_name)s Site Admin') % params
admin.site.index_title=_('%(community_name)s Administration') % params

urlpatterns = [
    path(r'', fenicemisc.views.HomePageView.as_view(), name="home"),
    path(r'admin/doc/', include('django.contrib.admindocs.urls')),
    path(r'admin/', decorator_include([fenicemisc.decorators.staff_or_404], admin.site.urls)),
    path(r'ckeditor/', include(ckeditor_uploader.urls)),
    path(r'avatar/', include(avatar.urls)),
    path(r'stat/',  include(fenicestat.urls)),
    path(r'credits/', fenicemisc.views.CreditsView.as_view(), name="credits"),
    path(r'accounts/', include(feniceauth.urls)),
    path(r'privacy/', include(fenicegdpr.urls)),
    path(r'blog/', include(feniceblog.urls)),
    path(r'forum/', include(machina_urls)),
    path(r'helpdesk/', include(helpdesk.urls)),
    path(r"badges/", include("pinax.badges.urls", namespace="pinax_badges")),
    path(r"announcements/", include("pinax.announcements.urls", namespace="pinax_announcements")),
    path(r"likes/", include("pinax.likes.urls", namespace="pinax_likes")),
    path(r"messages/", include("pinax.messages.urls", namespace="pinax_messages")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = feniceerrors.handlers.response_handler_404
handler403 = feniceerrors.handlers.response_handler_403
