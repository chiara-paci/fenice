from django.http import JsonResponse,Http404
from django.core.exceptions import PermissionDenied

class ErrorHandlingMiddleware(object):
    def __init__(self, get_response): 
        self._get_response=get_response

    def __call__(self,request):
        response=self._get_response(request)
        return response

    def process_exception(self,request,exception):
        if "HTTP_ACCEPT" not in request.META: return None
        if "text/html" in request.META["HTTP_ACCEPT"]: return None
        if type(exception) is Http404:
            return JsonResponse({},status=404)
        if type(exception) is PermissionDenied:
            return JsonResponse({},status=403)
        return None
