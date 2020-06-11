from django.test import TestCase
from django.conf import settings
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse

from unittest import mock
import testlib.mixins

from .. import middleware

class FeniceSessionMiddlewareTest(TestCase,testlib.mixins.TestCommonMixin):

    def test_my_middleware(self):
        request=mock.MagicMock(name="request")
        request.META = { 
            "REQUEST_METHOD": "POST", 
            "HTTP_OPERATING_SYSTEM_VERSION":"ICE CREAM", 
            "HTTP_PLATFORM":"ANDROID", 
            "HTTP_APP_VERSION":"1.0.0", 
            "HTTP_USER_AGENT":"AUTOMATED TEST"
        }
        request.path = '/testURL/'
        request.session = {}

        def get_response(request):
            return HttpResponse("Here's the text of the Web page.")

        mw=middleware.FeniceSessionMiddleware(get_response)
        response=mw(request) 
        self.assertIn(settings.SESSION_COOKIE_NAME,response.cookies)

 
class SaveBrowserDataContextMiddlewareTest(TestCase,testlib.mixins.TestCommonMixin):

    def test_my_middleware_without_saved(self):
        request=mock.MagicMock(name="request")
        request.META = { 
            "REQUEST_METHOD": "POST", 
            "HTTP_OPERATING_SYSTEM_VERSION":"ICE CREAM", 
            "HTTP_PLATFORM":"ANDROID", 
            "HTTP_APP_VERSION":"1.0.0", 
            "HTTP_USER_AGENT":"AUTOMATED TEST"
        }
        request.path = '/testURL/'
        request.session = {}

        def get_response(request):
            return TemplateResponse(request,mock.MagicMock("template"),context={},
                                    content_type="text/html", status=200)

        mw=middleware.SaveBrowserDataContextMiddleware(get_response)
        response=mw(request) 
        response=mw.process_template_response(request,response)

        self.assertIn("save_browser_data",response.context_data)
        self.assertEqual(reverse('fenicestat:browser_create'),response.context_data["save_browser_data"])

    def test_my_middleware_with_saved_false(self):
        request=mock.MagicMock(name="request")
        request.META = { 
            "REQUEST_METHOD": "POST", 
            "HTTP_OPERATING_SYSTEM_VERSION":"ICE CREAM", 
            "HTTP_PLATFORM":"ANDROID", 
            "HTTP_APP_VERSION":"1.0.0", 
            "HTTP_USER_AGENT":"AUTOMATED TEST"
        }
        request.path = '/testURL/'
        request.session = { "saved_browser_data": False }

        def get_response(request):
            return TemplateResponse(request,mock.MagicMock("template"),context={},
                                    content_type="text/html", status=200)

        mw=middleware.SaveBrowserDataContextMiddleware(get_response)
        response=mw(request) 
        response=mw.process_template_response(request,response)

        self.assertIn("save_browser_data",response.context_data)
        self.assertEqual(reverse('fenicestat:browser_create'),response.context_data["save_browser_data"])

    def test_my_middleware_with_saved_different_key(self):
        request=mock.MagicMock(name="request")
        request.META = { 
            "REQUEST_METHOD": "POST", 
            "HTTP_OPERATING_SYSTEM_VERSION":"ICE CREAM", 
            "HTTP_PLATFORM":"ANDROID", 
            "HTTP_APP_VERSION":"1.0.0", 
            "HTTP_USER_AGENT":"AUTOMATED TEST"
        }
        request.path = '/testURL/'

        class MockSession(dict):
            def __init__(self,session_key):
                self.session_key=session_key
                dict.__init__(self)

        request.session = MockSession(self.random_string())
        request.session["saved_browser_data"]=self.random_string()

        def get_response(request):
            return TemplateResponse(request,mock.MagicMock("template"),context={},
                                    content_type="text/html", status=200)

        mw=middleware.SaveBrowserDataContextMiddleware(get_response)
        response=mw(request) 
        response=mw.process_template_response(request,response)

        self.assertIn("save_browser_data",response.context_data)
        self.assertEqual(reverse('fenicestat:browser_create'),response.context_data["save_browser_data"])

    def test_my_middleware_with_saved_same_key(self):
        request=mock.MagicMock(name="request")
        request.META = { 
            "REQUEST_METHOD": "POST", 
            "HTTP_OPERATING_SYSTEM_VERSION":"ICE CREAM", 
            "HTTP_PLATFORM":"ANDROID", 
            "HTTP_APP_VERSION":"1.0.0", 
            "HTTP_USER_AGENT":"AUTOMATED TEST"
        }
        request.path = '/testURL/'

        class MockSession(dict):
            def __init__(self,session_key):
                self.session_key=session_key
                dict.__init__(self)

        request.session = MockSession(self.random_string())
        request.session["saved_browser_data"]=request.session.session_key
        

        def get_response(request):
            return TemplateResponse(request,mock.MagicMock("template"),context={},
                                    content_type="text/html", status=200)

        mw=middleware.SaveBrowserDataContextMiddleware(get_response)
        response=mw(request) 
        response=mw.process_template_response(request,response)

        self.assertNotIn("save_browser_data",response.context_data)

 
