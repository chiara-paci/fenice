from django.db import connection, models
from django.test import TestCase
import abc

from html_sanitizer.django import get_sanitizer

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from unittest import mock

from .. import fields
from . import common

class BaseFieldTestMixin(common.FeniceMiscMixin,abc.ABC):

    def test_pre_save_sanitize(self):
        txt=self.random_string(add_chars="<>")
        sanitizer=get_sanitizer()
        TestModel=self._test_model()
        m=TestModel()
        meta=TestModel._meta
        html=meta.local_concrete_fields[1]
        m.html=txt
        html.pre_save(m,False)
        self.assertEqual(m.html,sanitizer.sanitize(txt))

class CleanHtmlFieldTest(TestCase,BaseFieldTestMixin):
    def _test_model(self):
        class TestModel1(models.Model):
            html = fields.CleanHtmlField(max_length=1024)
        return TestModel1

class CleanHtmlRichTextFieldTest(TestCase,BaseFieldTestMixin):
    def _test_model(self):
        class TestModel2(models.Model):
            html = fields.CleanHtmlRichTextField()
        return TestModel2

class CleanHtmlRichTextUploadingFieldTest(TestCase,BaseFieldTestMixin):
    def _test_model(self):
        class TestModel3(models.Model):
            html = fields.CleanHtmlRichTextUploadingField()
        return TestModel3

