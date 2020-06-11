from django.test import TestCase
from django.conf import settings
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse

from unittest import mock
import testlib.mixins

from .. import middleware

class CommunityContextProcessorTest(TestCase,testlib.mixins.TestCommonMixin):

    def test_my_context_processor(self):
        self.assertTrue(False,"test da scrivere")
