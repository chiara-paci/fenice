import unittest
from unittest import skip
import random
import string
from django.views.generic import TemplateView

import abc

import testlib.mixins
from django.test import TestCase

from django.urls import reverse
from django.http import HttpRequest
from django.utils.html import escape

from . import common
from .. import models

class BaseViewTestMixin(common.FeniceGdprMixin,testlib.mixins.ViewTestMixin,abc.ABC):
    def test_returns_status_ok(self):
        response = self.client.get(common.get_url(self._label))
        self.assertStatus(response,200)

    def test_uses_view(self):
        response = self.client.get(common.get_url(self._label))
        self.assertUsesViewClass(response,common.VIEWS[self._label])

    def test_renders_template(self):
        response = self.client.get(common.get_url(self._label))
        self.assertTemplateUsed(response, common.TEMPLATES[self._label])  

class PolicyTest(TestCase,BaseViewTestMixin):
    _label="policy"

    def test_context(self):
        L=[ self.random_gdprpolicy() for k in range(0,random.randint(2,10)) ]
        response = self.client.get(common.get_url(self._label))
        last_p=L[-1]
        self.assertIn("policy",response.context)
        self.assertEqual(last_p,response.context["policy"])

    def test_context_no_policy(self):
        response = self.client.get(common.get_url(self._label))
        self.assertIn("policy",response.context)
        self.assertEqual(None,response.context["policy"])

    
