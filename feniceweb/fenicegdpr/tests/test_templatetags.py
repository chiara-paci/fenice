import unittest
from unittest import skip
import random
import string
from django.views.generic import TemplateView
from django.conf import settings
from django.template import Context, Template, TemplateSyntaxError

from django.utils.safestring import SafeString

import abc

import testlib.mixins
from django.test import TestCase

from django.urls import reverse
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape

from . import common
from .. import models
from ..templatetags import gdpr

class BaseTagTestMixin(common.FeniceGdprMixin,abc.ABC): pass

class GDPRAgreementTextTagTest(TestCase,BaseTagTestMixin):

    def test_mark_safe(self):
        agr=self.random_gdpragreement()
        ret=gdpr.gdpr_agreement_text(agr.name)
        self.assertIsInstance(ret,SafeString)

    def test_template_tag(self):
        agr=self.random_gdpragreement()
        out = Template(
            "{% load gdpr %}"
            "{% gdpr_agreement_text '"+agr.name+"' %}"
        ).render(Context({}))
        self.assertEqual(out,agr.text)

    def test_template_tag_create(self):
        name=self.random_string()
        out = Template(
            "{% load gdpr %}"
            "{% gdpr_agreement_text '"+name+"' %}"
        ).render(Context({}))
        self.assertEqual(out,"")
        L=list(models.GDPRAgreement.objects.filter(name=name))
        self.assertEqual(len(L),1)
        self.assertEqual(L[0].name,name)
        self.assertEqual(L[0].version,"0.1")
        
class GDPRAgreementPkTagTest(TestCase,BaseTagTestMixin):

    def test_template_tag(self):
        agr=self.random_gdpragreement()
        out = Template(
            "{% load gdpr %}"
            "{% gdpr_agreement_pk '"+agr.name+"' %}"
        ).render(Context({}))
        self.assertEqual(out,str(agr.pk))

    def test_template_tag_create(self):
        name=self.random_string()
        out = Template(
            "{% load gdpr %}"
            "{% gdpr_agreement_pk '"+name+"' %}"
        ).render(Context({}))
        L=list(models.GDPRAgreement.objects.filter(name=name))
        self.assertEqual(len(L),1)
        self.assertEqual(L[0].name,name)
        self.assertEqual(L[0].version,"0.1")
        self.assertEqual(out,str(L[0].pk))
        
