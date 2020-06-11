from django.shortcuts import render
from django.conf import settings

from django.views import csrf
from django.http import HttpResponseForbidden


# Create your views here.

def csrf_failure(request,reason="",*args,**kwargs):
    if "HTTP_ACCEPT" not in request.META:
        return csrf.csrf_failure(request,reason=reason,*args,**kwargs)
    if request.META["HTTP_ACCEPT"]!="application/json":
        return csrf.csrf_failure(request,reason=reason,*args,**kwargs)
    if settings.DEBUG:
        content=b'{ "reason": "%s" }' % reason.encode()
    else:
        content=b'{}'
    return HttpResponseForbidden(content,content_type="application/json")

