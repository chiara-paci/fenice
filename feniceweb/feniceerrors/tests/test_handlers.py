from django.core.exceptions import PermissionDenied
from django.http import HttpResponse,HttpResponseNotFound,Http404,JsonResponse
from django.test import SimpleTestCase, override_settings,TestCase
from django.urls import path

from .. import handlers

from unittest import mock

def http404_view(request):
    raise Http404()

def http403_view(request):
    raise PermissionDenied()


urlpatterns = [
    path('404/', http404_view),
    path('403/', http403_view),
]

handler404 = handlers.response_handler_404
handler403 = handlers.response_handler_403

# ROOT_URLCONF must specify the module that contains handler403 = ...
@override_settings(ROOT_URLCONF=__name__)
class CustomErrorHandlerTest(TestCase):
    
    def test_handler_not_found_text_html_defaults(self):
        response = self.client.get('/404xxx/',HTTP_ACCEPT="text/html")
        self.assertIsInstance(response,HttpResponse)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response["Content-Type"],"text/html")
        
    def test_handler_not_found(self):
        response = self.client.get('/404xxx/',HTTP_ACCEPT="application/json")
        self.assertIsInstance(response,JsonResponse)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.content,b'{}')
        self.assertEqual(response["Content-Type"],"application/json")

    def test_handler_view_raise_http404_text_html_defaults(self):
        response = self.client.get('/404/',HTTP_ACCEPT="text/html")
        self.assertIsInstance(response,HttpResponse)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response["Content-Type"],"text/html")
        
    def test_handler_view_raise_http404(self):
        response = self.client.get('/404/',HTTP_ACCEPT="application/json")
        self.assertIsInstance(response,JsonResponse)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.content,b'{}')
        self.assertEqual(response["Content-Type"],"application/json")

    def test_handler_view_raise_http403_text_html_defaults(self):
        response = self.client.get('/403/',HTTP_ACCEPT="text/html")
        self.assertIsInstance(response,HttpResponse)
        self.assertEqual(response.status_code,403)
        self.assertEqual(response["Content-Type"],"text/html")
        
    def test_handler_view_raise_http403(self):
        response = self.client.get('/403/',HTTP_ACCEPT="application/json")
        self.assertIsInstance(response,JsonResponse)
        self.assertEqual(response.status_code,403)
        self.assertEqual(response.content,b'{}')
        self.assertEqual(response["Content-Type"],"application/json")

