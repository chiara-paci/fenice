import unittest
from unittest import skip
import random
import string
from django.views.generic import TemplateView

from django.contrib.auth import get_user_model
User=get_user_model()
from django.test import override_settings

import abc

import testlib.mixins
from django.test import TestCase

from django.urls import reverse
from django.http import HttpRequest
from django.utils.html import escape

from . import common
#from .. import models,forms

class BaseFormTestMixin(common.FeniceBlogMixin,testlib.mixins.ViewTestMixin,abc.ABC):
    form_class=None

    @abc.abstractmethod
    def _data(self,add=[]): return {},{}

    def _correct_cases(self):
        d=self._data()
        return [
           ( "base", d[0], d[1] )
        ]

    def _wrong_cases(self):
        return [
            ( "empty", {}, {} )
        ]

    def _build_form(self,data,files):
        return self.form_class(data=data,files=files)

    def test_form_is_valid(self):
        correct=self._correct_cases()
        for label,data,files in correct:
            with self.subTest(correct=label):
                form=self._build_form(data,files)
                self.assertTrue(form.is_valid())
        
    def test_form_is_not_valid(self):
        wrong=self._wrong_cases()
        for label,data,files in wrong:
            with self.subTest(wrong=label):
                form=self._build_form(data,files)
                self.assertFalse(form.is_valid())

#class ArticleCreateFormTest(TestCase,BaseFormTestMixin):

#    def test_civetta(self):
#        print("Form per creazione articoli: 1) autori 2) pub time in local time")
#        self.assertTrue(False)


# class FamilyCreateFormTest(TestCase,BaseFormTestMixin):
#     _label="family"
#     form_class=common.FORMS[_label+"_create"]

#     def _data(self,add=[]):
#         return {
#             "cap": self.random_cap(),
#         },{}

#     def _build_form(self,data,files,session_key=None):
#         if session_key is None:
#             session_key=self.random_string()
#         return self.form_class(data=data,files=files,session_key=session_key)

#     def test_form_save_session_key(self):
#         correct=self._correct_cases()
#         for label,data,files in correct:
#             with self.subTest(correct=label):
#                 session_key=self.random_string()
#                 form=self._build_form(data,files,session_key=session_key)
#                 self.assertTrue(form.is_valid())
#                 obj=form.save()
#                 self.assertEqual(obj.session_key,session_key)

# class EmailCreateFormTest(TestCase,BaseFormTestMixin):
#     _label="email"
#     form_class=common.FORMS[_label+"_create"]

#     def _data(self,add=[]):
#         agreement=self.random_gdpragreement()
#         data= {
#             "email": self.random_email(),
#             "agreement": agreement.id,
#         }
#         return data,{}

#     def _build_form(self,data,files):
#         return self.form_class(data=data,files=files)

#     def test_form_save_policy_and_accept(self):
#         correct=self._correct_cases()
#         policies=[ self.random_gdprpolicy() for n in range(random.randint(2,10)) ]
#         policy=policies[-1]

#         for label,data,files in correct:
#             with self.subTest(correct=label):
#                 form=self._build_form(data,files)
#                 self.assertTrue(form.is_valid())
#                 obj=form.save()
#                 self.assertTrue(obj.accept)
#                 self.assertEqual(obj.policy.id,policy.id)
