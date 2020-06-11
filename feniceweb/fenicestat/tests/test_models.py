import unittest
import random
import abc

import os.path

from unittest import skip
from unittest import mock

from django.core.exceptions import ValidationError,PermissionDenied
from django.db.utils import IntegrityError
from django.conf import settings
from django.db import models as dj_models

from . import common
from .. import models

from fenicemisc import functions

from django.test import TestCase

class BaseModelTestMixin(common.FeniceStatMixin,abc.ABC): 
    model=None
    fields=[]
    defaults={}
    str_format=""

    @abc.abstractmethod
    def _data(self,add=[]): return {}

    @abc.abstractmethod
    def _correct_cases(self): return {}

    @abc.abstractmethod
    def _wrong_cases(self): return {}

    def test_create(self):
        data=self._data()
        obj=self.model.objects.create(**data)

        for field in self.fields:
            with self.subTest(field=field):
                self.assertTrue(hasattr(obj,field),
                                msg="Model %s don't have field %s" % (self.model.__name__,field))
        for field in self.defaults:
            with self.subTest(field=field):
                expected=self.defaults[field]
                if hasattr(expected,"__call__"):
                    expected=expected()
                actual=getattr(obj,field)
                if isinstance(actual,dj_models.Model):
                    self.assertEqual(actual.id,expected,
                                     msg="Default for %s.%s: expected %s, actual %s" % (self.model.__name__,field,expected,actual))
                else:
                    self.assertEqual(actual,expected,
                                     msg="Default for %s.%s: expected %s, actual %s" % (self.model.__name__,field,expected,actual))

    def test_wrong_cases(self):
        wrong=self._wrong_cases()
        for k in wrong:
            with self.subTest(wrong_case=k):
                obj = self.model(**(wrong[k]))
                with self.assertRaises(ValidationError):
                    obj.full_clean()
                    obj.save() # pragma: no cover

    def test_correct_cases(self):
        correct=self._correct_cases()
        for k in correct:
            with self.subTest(correct_case=k):
                obj = self.model(**(correct[k]))
                obj.full_clean()
                obj.save() # pragma: no cover

    def test_str(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        self.assertEqual(self.str_format % data,str(obj))

class BrowserModelTest(TestCase,BaseModelTestMixin):
    model=models.Browser

    fields=[ 
        "session_key", "created", 
	"code_name",
	"name",
	"version",
	"language",
	"platform",
	"user_agent",
	"cookies_enabled",
	"screen_width",
	"screen_height",
	"screen_available_width",
	"screen_available_height",
	"screen_color_depth",
	"screen_pixel_depth",
        "viewport_height", "viewport_width",
	"luxon_intl",
	"luxon_intl_tokens",
	"luxon_zones",
	"luxon_relative",
	"timezone",
	"iso_timestamps"
    ]

    defaults= {

	"code_name": "",
	"name": "",
	"version": "",
	"language": "",
	"platform": "",
	"user_agent": "",
	"cookies_enabled": False,

	"screen_width": 0,
	"screen_height": 0,
	"screen_available_width": 0,
	"screen_available_height": 0,
	"screen_color_depth": 0,
	"screen_pixel_depth": 0,
        "viewport_height": 0, 
        "viewport_width": 0,

	"luxon_intl": False,
	"luxon_intl_tokens": False,
	"luxon_zones": False,
	"luxon_relative": False,
	"timezone": "",
	"iso_timestamps": ""
    }

    str_format = "%(session_key)s"

    def _data(self,add=[]):
        data= {
            "session_key": self.random_string(),
        }

        for k in [ "code_name",
	           "name",
	           "version",
	           "language",
	           "platform",
	           "user_agent","timezone","iso_timestamps" ]:
            if k in add:
                data[k]=self.random_string()

        for k in [ "screen_width", "screen_height", "screen_color_depth", "screen_pixel_depth", 
                   "screen_available_height", "screen_available_width","viewport_height", "viewport_width" ]:
            if k in add:
                data[k]=random.randint(100,2000)

        for k in [ "cookies_enabled",
	           "luxon_intl",
	           "luxon_intl_tokens",
	           "luxon_zones",
	           "luxon_relative" ]:
            if k in add:
                data[k]=self.random_boolean()
        return data

    def _wrong_cases(self):
        wrong ={
            "no session_key": self._data(),
        }
        wrong["no session_key"]["session_key"]=""
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
            "with all": self._data(add=[ 
	        "code_name",
	        "name",
	        "version",
	        "language",
	        "platform",
	        "user_agent",
	        "cookies_enabled",
	        "screen_width",
	        "screen_height",
	        "screen_available_width",
	        "screen_available_height",
	        "screen_color_depth",
	        "screen_pixel_depth",
                "viewport_height", "viewport_width",
	        "luxon_intl",
	        "luxon_intl_tokens",
	        "luxon_zones",
	        "luxon_relative",
                "timezone",
	        "iso_timestamps"
            ]),
        }
        return correct

    def test_serialize(self):
        data=self._data(add=[ 
	    "code_name",
	    "name",
	    "version",
	    "language",
	    "platform",
	    "user_agent",
	    "cookies_enabled",
	    "screen_width",
	    "screen_height",
	    "screen_available_width",
	    "screen_available_height",
	    "screen_color_depth",
	    "screen_pixel_depth",
            "viewport_height", "viewport_width",
	    "luxon_intl",
	    "luxon_intl_tokens",
	    "luxon_zones",
	    "luxon_relative",
	    "timezone",
	    "iso_timestamps"
        ])
        obj=self.model.objects.create(**data)
        ser=obj.__serialize__()
        for k in self.fields:
            with self.subTest(field=k):
                self.assertIn(k,ser)
                if k=="created":
                    self.assertJsonIsTimestamp(ser[k])
                    continue
                self.assertEqual(ser[k],data[k])

    def test_deserialize(self):
        ser=self._data(add=[ 
	    "code_name",
	    "name",
	    "version",
	    "language",
	    "platform",
	    "user_agent",
	    "cookies_enabled",
	    "screen_width",
	    "screen_height",
	    "screen_available_width",
	    "screen_available_height",
	    "screen_color_depth",
	    "screen_pixel_depth",
            "viewport_height", "viewport_width",
	    "luxon_intl",
	    "luxon_intl_tokens",
	    "luxon_zones",
	    "luxon_relative",
	    "timezone",
	    "iso_timestamps"
        ])
        created=self.random_datetime_utc()
        ser["created"]=functions.date_serialize(created)
        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            with self.subTest(field=k):
                self.assertTrue(hasattr(obj,k))
                if k=="created":
                    self.assertEqual(created,getattr(obj,k))
                    continue
                self.assertEqual(ser[k],getattr(obj,k))
        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)

