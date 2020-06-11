from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,Http404
from django.conf import settings
from functools import wraps

def debug_staff_or_404(view):
    @wraps(view)
    def new_view(request,*args,**kwargs):
        if not settings.DEBUG:
            raise Http404()
        if not hasattr(request,"user"):
            raise Http404()
        if not request.user.is_authenticated:
            raise Http404()
        if not request.user.is_staff:
            raise Http404()
        return view(request,*args,**kwargs)
    return new_view

def json_or_debug_staff_or_404(view):
    @wraps(view)
    def new_view(request,*args,**kwargs):
        content_accepted=request.META.get('HTTP_ACCEPT')
        if content_accepted is not None:
            if content_accepted.startswith("application/json"):
                return view(request,*args,**kwargs)
        if not settings.DEBUG:
            raise Http404()
        if not hasattr(request,"user"):
            raise Http404()
        if not request.user.is_authenticated:
            raise Http404()
        if not request.user.is_staff:
            raise Http404()
        return view(request,*args,**kwargs)
    return new_view

def staff_or_404(view):
    @wraps(view)
    def new_view(request,*args,**kwargs):
        if not hasattr(request,"user"):
            raise Http404()
        if not request.user.is_authenticated:
            raise Http404()
        if not request.user.is_staff:
            raise Http404()
        return view(request,*args,**kwargs)
    return new_view


# def require_ownership(model):
#     def decor(view):
#         view=login_required(login_url="/")(view)
#         def new_view(request,*args,**kwargs):
#             pk=kwargs["pk"]
#             try:
#                 obj=model.objects.get(pk=pk)
#             except model.DoesNotExist as e:
#                 raise Http404
#             if request.user!=obj.owner: 
#                 raise Http404
#             return view(request,*args,**kwargs)
#         new_view.__doc__ = view.__doc__
#         new_view.__name__ = view.__name__
#         if hasattr(view,"csrf_exempt"):
#             new_view.csrf_exempt=view.csrf_exempt
#         return new_view
#     return decor

# def error_to_json(view):
#     def new_view(request,*args,**kwargs):
#         try:
#             return view(request,*args,**kwargs)
#         except Http404 as e:
#             if "HTTP_ACCEPT" not in request.META:
#                 raise e
#             if request.META["HTTP_ACCEPT"].startswith("application/json"):
#                 return JsonResponse({"errors": str(e)}, status=404)
#             raise e
#     new_view.__doc__ = view.__doc__
#     new_view.__name__ = view.__name__
#     if hasattr(view,"csrf_exempt"):
#         new_view.csrf_exempt=view.csrf_exempt
#     return new_view

# def json_login_required(view):
#     def new_view(request,*args,**kwargs):
#         if not hasattr(request,"user"):
#             return JsonResponse({"errors": "login required"}, status=403)
#         if not request.user.is_authenticated:
#             return JsonResponse({"errors": "login required"}, status=403)
#         return view(request,*args,**kwargs)
#     new_view.__doc__ = view.__doc__
#     new_view.__name__ = view.__name__
#     if hasattr(view,"csrf_exempt"):
#         new_view.csrf_exempt=view.csrf_exempt
#     return new_view

# def set_request_accept(accept):
#     def decorator(view):
#         def new_view(request,*args,**kwargs):
#             request.META["HTTP_ACCEPT"]=accept
#             return view(request,*args,**kwargs)
#         new_view.__doc__ = view.__doc__
#         new_view.__name__ = view.__name__
#         if hasattr(view,"csrf_exempt"):
#             new_view.csrf_exempt=view.csrf_exempt
#         return new_view
#     return decorator
