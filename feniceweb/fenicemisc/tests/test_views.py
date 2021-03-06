import unittest
from unittest import skip
import random
import string
from django.views.generic import TemplateView
from django.conf import settings

import abc

import testlib.mixins
from django.test import TestCase

from django.urls import reverse
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape

from . import common
from .. import models

class BaseViewTestMixin(common.FeniceMiscMixin,testlib.mixins.ViewTestMixin,abc.ABC):
    def test_returns_status_ok(self):
        response = self.client.get(common.get_url(self._label))
        self.assertStatus(response,200)

    def test_uses_view(self):
        response = self.client.get(common.get_url(self._label))
        self.assertUsesViewClass(response,common.VIEWS[self._label])

    def test_renders_template(self):
        response = self.client.get(common.get_url(self._label))
        self.assertTemplateUsed(response, common.TEMPLATES[self._label])  

class CreditsTest(TestCase,BaseViewTestMixin):
    _label="credits"

    def test_context(self):
        L=[ self.random_openimagecredit() for k in range(0,random.randint(2,10)) ]
        response = self.client.get(common.get_url(self._label))
        self.assertIn("openimagecredit_list",response.context)
        self.assertEqual(len(L),len(response.context["openimagecredit_list"]))
        for obj in L:
            self.assertIn(obj,response.context["openimagecredit_list"])

class HomeTest(TestCase,BaseViewTestMixin):
    _label="home"
    



