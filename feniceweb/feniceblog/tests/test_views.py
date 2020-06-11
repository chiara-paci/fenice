import unittest
from unittest import skip
import random
import string
from django.views.generic import TemplateView

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

#from django.contrib.auth import get_user_model
#User=get_user_model()
from django.test import override_settings
from django.conf import settings
from django.utils.text import slugify


import abc

import testlib.mixins
from django.test import TestCase

from django.urls import reverse
from django.http import HttpRequest
from django.utils.html import escape

from . import common
#from .. import models,forms

class BaseViewTestMixin(common.FeniceBlogMixin,testlib.mixins.ViewTestMixin,abc.ABC):
    def test_returns_status_ok(self):
        response = self.client.get(common.get_url(self._label))
        self.assertStatus(response,200)

    def test_uses_view(self):
        response = self.client.get(common.get_url(self._label))
        self.assertUsesViewClass(response,common.VIEWS[self._label])

    def test_renders_template(self):
        if not self._label in common.TEMPLATES: return
        response = self.client.get(common.get_url(self._label))
        self.assertTemplateUsed(response, common.TEMPLATES[self._label])



class ArticleArchiveViewTest(TestCase,BaseViewTestMixin):
    _label="article_archive"

class ArticleDetailViewTest(TestCase,BaseViewTestMixin):
    _label="article_detail"

    def _urls(self,obj):
        return [
            ("pk", common.get_url(self._label,pk=obj.pk)),
            ("pk+slug", common.get_url(self._label,pk=obj.pk,slug=slugify(obj.title))),
        ]

    def test_returns_status_ok(self):
        obj=self.random_article()        
        for label,url in self._urls(obj):
            with self.subTest(case=label):
                response = self.client.get(url)
                self.assertStatus(response,200)

    def test_uses_view(self):
        obj=self.random_article()        
        for label,url in self._urls(obj):
            with self.subTest(case=label):
                response = self.client.get(url)
                self.assertUsesViewClass(response,common.VIEWS[self._label])

    def test_renders_template(self):
        if not self._label in common.TEMPLATES: return
        obj=self.random_article()        
        for label,url in self._urls(obj):
            with self.subTest(case=label):
                response = self.client.get(url)
                self.assertTemplateUsed(response, common.TEMPLATES[self._label])


    
