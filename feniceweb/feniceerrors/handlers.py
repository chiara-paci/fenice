from django.core.exceptions import PermissionDenied
from django.http import HttpResponse,HttpResponseNotFound,Http404,JsonResponse
from django.test import SimpleTestCase, override_settings
from django.urls import path
from django.urls.exceptions import Resolver404

import django.views.defaults

def response_handler_404(request, exception, template_name='404.html'):
    if "HTTP_ACCEPT" not in request.META:
        return django.views.defaults.page_not_found(request,exception,template_name=template_name) 
    if request.META["HTTP_ACCEPT"]=="text/html":
        return django.views.defaults.page_not_found(request,exception,template_name=template_name) 
    if type(exception) is Http404:
        return JsonResponse({},status=404)
    if type(exception) is Resolver404:
        return JsonResponse({},status=404)
    return django.views.defaults.page_not_found(request,exception,template_name=template_name) 

def response_handler_403(request, exception, template_name='403.html'):
    if "HTTP_ACCEPT" not in request.META:
        return django.views.defaults.permission_denied(request,exception,template_name=template_name) 
    if request.META["HTTP_ACCEPT"]=="text/html":
        return django.views.defaults.permission_denied(request,exception,template_name=template_name) 
    if type(exception) is PermissionDenied:
        return JsonResponse({},status=403)
    return django.views.defaults.permission_denied(request,exception,template_name=template_name) 



