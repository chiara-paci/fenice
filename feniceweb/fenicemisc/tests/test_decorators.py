from django.core.exceptions import PermissionDenied
from django.http import HttpResponse,HttpResponseNotFound,Http404,JsonResponse
from django.test import override_settings,TestCase
from django.urls import path
from django.test import RequestFactory
import collections

from django.contrib.auth import get_user_model
User=get_user_model()

from unittest import mock

from . import common
from .. import decorators

class BaseDecoratorMixin(common.FeniceMiscMixin):
    def _decorate(self,view):
        return view

    @override_settings(DEBUG=True)
    def test_correct_cases_debug(self):
        def a_view(req): return HttpResponse()
        reqs=self.correct_cases_debug()
        for label,req in reqs:
            with self.subTest(case=label):
                response=self._decorate(a_view)(req)
                self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False)
    def test_correct_cases_no_debug(self):
        def a_view(req): return HttpResponse()
        reqs=self.correct_cases_no_debug()
        for label,req in reqs:
            with self.subTest(case=label):
                response=self._decorate(a_view)(req)
                self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_wrong_cases_debug(self):
        def a_view(req): return HttpResponse()
        reqs=self.wrong_cases_debug()
        for label,req in reqs:
            with self.subTest(case=label):
                with self.assertRaises(Http404):
                    response=self._decorate(a_view)(req)

    @override_settings(DEBUG=False)
    def test_wrong_cases_no_debug(self):
        def a_view(req): return HttpResponse()
        reqs=self.wrong_cases_no_debug()
        for label,req in reqs:
            with self.subTest(case=label):
                with self.assertRaises(Http404):
                    response=self._decorate(a_view)(req)

class DebugStaffOr404Test(BaseDecoratorMixin,TestCase):

    def _decorate(self,view):
        return decorators.debug_staff_or_404(view)

    def setUp(self):
        self._cases=collections.OrderedDict()

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=True
        request.user.is_authenticated=True
        self._cases["staff"]= request

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=False
        request.user.is_authenticated=True
        self._cases["no staff"]=request

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=True
        request.user.is_authenticated=False
        self._cases["no auth"]=request

        request = mock.MagicMock(name="request",spec_set=[])
        self._cases["no user"]=request

    def correct_cases_no_debug(self): return []

    def wrong_cases_no_debug(self):
        return self._cases.items()

    def correct_cases_debug(self): 
        return [
            ("staff",self._cases["staff"])
        ]

    def wrong_cases_debug(self):
        return [ (k,self._cases[k]) for k in self._cases if k != "staff"]


class JsonOrDebugStaffOr404Test(BaseDecoratorMixin,TestCase):

    def _decorate(self,view):
        return decorators.json_or_debug_staff_or_404(view)

    def setUp(self):
        self._cases=collections.OrderedDict()

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=True
        request.user.is_authenticated=True
        self._cases["staff"]= request

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=False
        request.user.is_authenticated=True
        self._cases["no staff"]=request

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=True
        request.user.is_authenticated=False
        self._cases["no auth"]=request

        request = mock.MagicMock(name="request",spec_set=["META"])
        self._cases["no user"]=request

        for k in self._cases:
            self._cases[k].META=mock.MagicMock(name="META")
            self._cases[k].META.get=mock.MagicMock(name="get")
            self._cases[k].META.get.return_value=self.random_string()

        self._cases_json=collections.OrderedDict()
        for k in self._cases:
            request = mock.MagicMock(name="request")
            request.META=mock.MagicMock(name="META")
            request.META.get=mock.MagicMock(name="get")
            request.META.get.return_value="application/json"
            if k!="no user":
                request.user = mock.MagicMock(name="user")
                request.user.is_staff=self._cases[k].user.is_staff
                request.user.is_authenticated=self._cases[k].user.is_authenticated
            self._cases_json[k+" json"]=request

    def correct_cases_no_debug(self): 
        return self._cases_json.items()

    def wrong_cases_no_debug(self):
        return self._cases.items()

    def correct_cases_debug(self): 
        return [
            ("staff",self._cases["staff"])
        ]+list(self._cases_json.items())

    def wrong_cases_debug(self):
        return [ (k,self._cases[k]) for k in self._cases if k != "staff"]


class StaffOr404Test(BaseDecoratorMixin,TestCase):

    def _decorate(self,view):
        return decorators.staff_or_404(view)

    def setUp(self):
        self._cases=collections.OrderedDict()

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=True
        request.user.is_authenticated=True
        self._cases["staff"]= request

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=False
        request.user.is_authenticated=True
        self._cases["no staff"]=request

        request = mock.MagicMock(name="request")
        request.user = mock.MagicMock(name="user")
        request.user.is_staff=True
        request.user.is_authenticated=False
        self._cases["no auth"]=request

        request = mock.MagicMock(name="request",spec_set=[])
        self._cases["no user"]=request

    def correct_cases_no_debug(self): return self.correct_cases_debug()

    def wrong_cases_no_debug(self): return self.wrong_cases_debug()

    def correct_cases_debug(self): 
        return [
            ("staff",self._cases["staff"])
        ]

    def wrong_cases_debug(self):
        return [ (k,self._cases[k]) for k in self._cases if k != "staff"]
