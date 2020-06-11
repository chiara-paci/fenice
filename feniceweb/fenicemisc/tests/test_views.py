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
    
    def test_context(self):
        response = self.client.get(common.get_url(self._label))

        self.assertIn("save_email_url",response.context_data)

        self.assertIn("product_list",response.context)
        self.assertEqual(6,len(response.context["product_list"]))
        for obj in response.context["product_list"]:
            self.assertIn("image_url",obj)
            self.assertIn("color",obj)
            self.assertIn("percent",obj)

            self.assertIn("name",obj)
            self.assertIn("description",obj)
            self.assertIn("target",obj)
            self.assertIn("quote",obj)
            self.assertIn("measure",obj)
            self.assertIn("achievement",obj)

            self.assertIn("arc",obj)
            self.assertIn("start_x",obj["arc"])
            self.assertIn("start_y",obj["arc"])
            self.assertIn("end_x",obj["arc"])
            self.assertIn("end_y",obj["arc"])
            self.assertIn("large_arc",obj["arc"])


