from django.test import TestCase
from django.http import Http404,JsonResponse
from django.core.exceptions import PermissionDenied

import random
import string

from unittest import mock
import testlib.mixins

from .. import middleware

class ErrorHandlingMiddlewareTest(TestCase,testlib.mixins.TestCommonMixin):

    def test_is_transparent_middleware(self):
        request=mock.MagicMock(name="request",spec_set=[])
        response=mock.MagicMock(name="response",spec_set=[])
        get_response=mock.MagicMock(name="get_response")
        get_response.return_value=response
        mw=middleware.ErrorHandlingMiddleware(get_response)
        ret=mw(request)
        get_response.assert_called_with(request)
        self.assertEqual(ret,response)

    def test_process_exception_text_html(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "text/html" })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        ret=mw.process_exception(request,Exception("x"))
        self.assertIsNone(ret)

    def test_process_exception_unknown(self):
        request=mock.MagicMock(name="request")
        #meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "text/html" })
        #type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        ret=mw.process_exception(request,Exception("x"))
        self.assertIsNone(ret)

    def test_process_exception_http404(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "application/json" })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,Http404(msg))
        self.assertIsInstance(ret,JsonResponse)
        self.assertEqual(ret.status_code,404)
        self.assertEqual(ret.content,b'{}')
        self.assertEqual(ret["Content-Type"],"application/json")

    def test_process_exception_http403(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "application/json" })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,PermissionDenied(msg))
        self.assertIsInstance(ret,JsonResponse)
        self.assertEqual(ret.status_code,403)
        self.assertEqual(ret.content,b'{}')
        self.assertEqual(ret["Content-Type"],"application/json")

    def test_process_exception_http404_text_html_browser(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,Http404(msg))
        self.assertIsNone(ret)

    def test_process_exception_http404_text_html_mixed(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": self.random_string(max_size=30,with_spaces=True)+"text/html"+self.random_string(max_size=30,with_spaces=True) })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,Http404(msg))
        self.assertIsNone(ret)

    def test_process_exception_http404_text_html(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "text/html" })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,Http404(msg))
        self.assertIsNone(ret)

    def test_process_exception_http403_text_html_browser(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,PermissionDenied(msg))
        self.assertIsNone(ret)

    def test_process_exception_http403_text_html(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": "text/html" })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,PermissionDenied(msg))
        self.assertIsNone(ret)

    def test_process_exception_http403_text_html_mixed(self):
        request=mock.MagicMock(name="request")
        meta=mock.PropertyMock(name="META",return_value={"HTTP_ACCEPT": self.random_string(max_size=30,with_spaces=True)+"text/html"+self.random_string(max_size=30,with_spaces=True) })
        type(request).META=meta
        get_response=mock.MagicMock(name="get_response")
        mw=middleware.ErrorHandlingMiddleware(get_response)
        msg=self.random_string()
        ret=mw.process_exception(request,PermissionDenied(msg))
        self.assertIsNone(ret)
