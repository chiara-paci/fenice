from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse_lazy

class FeniceSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        SessionMiddleware.process_request(self,request)
        if not request.session or not request.session.session_key:
            request.session.save()

class SaveBrowserDataContextMiddleware(object):
    def __init__(self,get_response):
        self._get_response=get_response

    def __call__(self,request):
        response=self._get_response(request)
        return response

    def process_template_response(self,request,response):
        if "saved_browser_data" in request.session:
            if request.session["saved_browser_data"] and request.session["saved_browser_data"]==request.session.session_key:
                return response
        response.context_data["save_browser_data"]=reverse_lazy("fenicestat:browser_create")
        return response
