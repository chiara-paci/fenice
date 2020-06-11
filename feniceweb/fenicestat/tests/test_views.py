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
from .. import models

class BaseViewTestMixin(common.FeniceStatMixin,testlib.mixins.ViewTestMixin,abc.ABC):
    def test_returns_status_ok(self):
        response = self.client.get(common.get_url(self._label))
        self.assertStatus(response,200)

    def test_uses_view(self):
        response = self.client.get(common.get_url(self._label))
        self.assertUsesViewClass(response,common.VIEWS[self._label])

    def test_renders_template(self):
        response = self.client.get(common.get_url(self._label))
        self.assertTemplateUsed(response, common.TEMPLATES[self._label])  

class BaseListCreateViewTestMixin(common.FeniceStatMixin,testlib.mixins.ViewTestMixin,abc.ABC):
    model = None

    ## List

    @override_settings(DEBUG=True)
    def test_anonymous_list_returns_status_not_found(self):
        response = self.client.get(common.get_url(self._label+"_list"))
        self.assertStatus(response,404)
    
    @override_settings(DEBUG=True)
    def test_normal_user_list_returns_status_not_found(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(common.get_url(self._label+"_list"))
        self.assertStatus(response,404)
    
    @override_settings(DEBUG=False)
    def test_debug_false_list_returns_status_not_found(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(common.get_url(self._label+"_list"))
        self.assertStatus(response,404)

    @override_settings(DEBUG=True)
    def test_list_returns_status_ok(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(common.get_url(self._label+"_list"))
        self.assertStatus(response,200)

    @override_settings(DEBUG=True)
    def test_list_uses_view(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(common.get_url(self._label+"_list"))
        self.assertUsesViewClass(response,common.VIEWS[self._label+"_list"])

    @override_settings(DEBUG=True)
    def test_list_renders_template(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(common.get_url(self._label+"_list"))
        self.assertTemplateUsed(response, common.TEMPLATES[self._label+"_list"])  

    @override_settings(DEBUG=True)
    def test_list_context(self):
        self.client.force_login(self.staff_user)
        L=self._random_list()
        response = self.client.get(common.get_url(self._label+"_list"))
        self.assertIn(self._label+"_list",response.context)
        self.assertEqual(len(L),len(response.context[self._label+"_list"]))
        for obj in L:
            self.assertIn(obj,response.context[self._label+"_list"])
        self.assertIn("form",response.context)
        self.assertIsInstance(response.context["form"],
                              common.FORMS[self._label+"_create"])

    @abc.abstractmethod
    def _data(self,add=[]): return {}

    @abc.abstractmethod
    def _random_list(self): return []

    def _correct_cases(self):
        return [
           ( "base", self._data() )
        ]

    def _wrong_cases(self):
        return [
            ( "empty", {} )
        ]

    ## Create HTML

    @override_settings(DEBUG=True)
    def test_anonymous_create_html_valid_returns_status_not_found(self):
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,404)
    
    @override_settings(DEBUG=True)
    def test_normal_user_create_html_valid_returns_status_not_found(self):
        self.client.force_login(self.normal_user)
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,404)
    
    @override_settings(DEBUG=False)
    def test_debug_false_create_html_valid_returns_status_not_found(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,404)

    @override_settings(DEBUG=True)
    def test_anonymous_create_html_invalid_returns_status_not_found(self):
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,404)

    @override_settings(DEBUG=True)
    def test_normal_user_create_html_invalid_returns_status_not_found(self):
        self.client.force_login(self.normal_user)
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,404)
    
    @override_settings(DEBUG=False)
    def test_debug_false_create_html_invalid_returns_status_not_found(self):
        self.client.force_login(self.staff_user)
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,404)

    #
    @override_settings(DEBUG=True)
    def test_create_html_uses_view(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()+self._wrong_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertUsesViewClass(response,common.VIEWS[self._label+"_create"])

    @override_settings(DEBUG=True)
    def test_create_html_valid_creates_a_new_object(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                L_pre=self.model.objects.all().count()
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                L_post=self.model.objects.all().count()
                self.assertEquals(L_pre+1,L_post)

    @override_settings(DEBUG=True)
    def test_create_html_valid_returns_status_redirect(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,302)

    @override_settings(DEBUG=True)
    def test_create_html_valid_redirects_to_list_page(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertRedirects(response, common.get_url(self._label+"_list"))

    @override_settings(DEBUG=True)
    def test_create_html_valid_content_type(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertTrue(response["Content-type"].startswith("text/html"))

    @override_settings(DEBUG=True)
    def test_create_html_invalid_does_not_create_a_new_object(self):
        self.client.force_login(self.staff_user)
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                L_pre=self.model.objects.all().count()
                response = self.client.post(common.get_url(self._label+"_create"), data=data)
                L_post=self.model.objects.all().count()
                self.assertEquals(L_pre,L_post)

    @override_settings(DEBUG=True)
    def test_create_html_invalid_returns_status_ok(self):
        self.client.force_login(self.staff_user)
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertEquals(response.status_code,200)

    @override_settings(DEBUG=True)
    def test_create_html_invalid_renders_list_template(self):
        self.client.force_login(self.staff_user)
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertTemplateUsed(response, common.TEMPLATES[self._label+"_list"])  

    @override_settings(DEBUG=True)
    def test_create_html_invalid_content_type(self):
        self.client.force_login(self.staff_user)
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                self.assertTrue(response["Content-type"].startswith("text/html"))

    ## Create JSON 
        
    def test_create_json_uses_view(self):
        correct=self._correct_cases()+self._wrong_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data,HTTP_ACCEPT="application/json")
                self.assertUsesViewClass(response,common.VIEWS[self._label+"_create"])


    def test_create_json_valid_creates_a_new_object(self):
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                L_pre=self.model.objects.all().count()
                response = self.client.post(common.get_url(self._label+"_create"), data=data,HTTP_ACCEPT='application/json')
                L_post=self.model.objects.all().count()
                self.assertEquals(L_pre+1,L_post)

    def test_create_json_valid_returns_status_create(self):
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data,HTTP_ACCEPT='application/json')
                self.assertEquals(response.status_code,201)

    def test_create_json_valid_content_type(self):
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data,HTTP_ACCEPT='application/json')
                self.assertTrue(response["Content-type"].startswith("application/json"))

    def test_create_json_invalid_does_not_create_a_new_object(self):
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                L_pre=self.model.objects.all().count()
                response = self.client.post(common.get_url(self._label+"_create"), data=data,HTTP_ACCEPT='application/json')
                L_post=self.model.objects.all().count()
                self.assertEquals(L_pre,L_post)

    def test_create_json_invalid_returns_status_bad_request(self):
        data=self._data()
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data,HTTP_ACCEPT='application/json') 
                self.assertEquals(response.status_code,400)

    def test_create_json_invalid_content_type(self):
        wrong=self._wrong_cases()
        for label,data in wrong:
            with self.subTest(wrong=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data,HTTP_ACCEPT='application/json')
                self.assertTrue(response["Content-type"].startswith("application/json"))


class BrowserListCreateViewTest(TestCase,BaseListCreateViewTestMixin):
    _label="browser"
    model=models.Browser

    def setUp(self):
        self.normal_user=User.objects.create_user(username=self.random_string(max_size=30,min_size=4),
                                                  password=self.random_string(max_size=30,min_size=8),email=self.random_email())
        self.staff_user=User.objects.create_user(username=self.random_string(max_size=30,min_size=4),
                                                 password=self.random_string(max_size=30,min_size=8),email=self.random_email(),
                                                 is_staff=True)

    def _data(self,add=[]):
        return {}

    def _wrong_cases(self):
        wrong={
            "screen_width": self.random_string()
        }
        return [
            ( "no number", wrong )
        ]
    

    def _random_list(self):
        return [ self.random_browser() for k in range(0,random.randint(2,10)) ]

    @override_settings(DEBUG=True)
    def test_create_html_update_session(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()+self._wrong_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                session = self.client.session
                self.assertIn("saved_browser_data",session)
                self.assertTrue(session['saved_browser_data'])

    def test_create_json_update_session(self):
        correct=self._correct_cases()+self._wrong_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                response = self.client.post(common.get_url(self._label+"_create"),data=data,HTTP_ACCEPT="application/json")
                self.assertUsesViewClass(response,common.VIEWS[self._label+"_create"])
                session=self.client.session
                self.assertIn("saved_browser_data",session)
                self.assertTrue(session['saved_browser_data'])


    @override_settings(DEBUG=True)
    def test_create_html_valid_creates_a_new_object(self):
        self.client.force_login(self.staff_user)
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                L_pre=self.model.objects.all().count()
                response = self.client.post(common.get_url(self._label+"_create"),data=data)
                L_post=self.model.objects.all().count()
                self.assertEquals(L_pre+1,L_post)
                obj=self.model.objects.latest("id")
                session=self.client.session
                self.assertEquals(obj.session_key,session.session_key)


    def test_create_json_valid_creates_a_new_object(self):
        correct=self._correct_cases()
        for label,data in correct:
            with self.subTest(correct=label):
                L_pre=self.model.objects.all().count()
                response = self.client.post(common.get_url(self._label+"_create"), data=data,HTTP_ACCEPT='application/json')
                L_post=self.model.objects.all().count()
                self.assertEquals(L_pre+1,L_post)
                obj=self.model.objects.latest("id")
                session=self.client.session
                self.assertEquals(obj.session_key,session.session_key)
