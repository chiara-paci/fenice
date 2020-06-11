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

class BaseModelTestMixin(common.FeniceGdprMixin,abc.ABC): 
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

class GDPRPolicyModelTest(TestCase,BaseModelTestMixin):
    model=models.GDPRPolicy
    fields=[ "text","version", "created","last_modified" ]
    defaults= {}
    str_format = "%(version)s"

    def _data(self,add=[]):
        data= {
            "text": self.random_string(),
            "version": self.random_string(min_size=2,max_size=10),
        }
        return data

    def _wrong_cases(self):
        wrong ={
            "no text": self._data(),
            "no version": self._data(),
        }

        wrong["no text"]["text"]=""
        wrong["no version"]["version"]=""
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
        }
        return correct

    def test_unique_version(self):
        data1=self._data()
        data2=self._data()
        data2["version"]=data1["version"]
        obj1 = self.model(**(data1))
        obj1.full_clean()
        obj1.save() # pragma: no cover
        obj2 = self.model(**(data1))
        with self.assertRaises(ValidationError):
            obj2.full_clean()
            obj2.save() # pragma: no cover

    def test_serialize(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        ser=obj.__serialize__()
        for k in self.fields:
            self.assertIn(k,ser)
            if k not in ["created","last_modified"]:
                self.assertEqual(ser[k],data[k])
                continue
            self.assertJsonIsTimestamp(ser[k])

    def test_created_always_in_the_past(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        created_past=self.random_datetime_utc(max_year=2019)
        created_future=self.random_datetime_utc(max_year=2500,min_year=2100)

        obj.created=created_past
        obj.full_clean()
        obj.save()
        obj.created=created_future
        with self.assertRaises(ValidationError):
            obj.full_clean()
            obj.save()
        

    def test_deserialize(self):
        ser=self._data()
        created=self.random_datetime_utc()
        last_modified=created+self.random_timedelta()
        ser["created"]=functions.date_serialize(created)
        ser["last_modified"]=functions.date_serialize(last_modified)
        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            with self.subTest(field=k):
                self.assertTrue(hasattr(obj,k))
                if k=="last_modified": continue
                if k not in ["created","last_modified"]:
                    self.assertEqual(ser[k],getattr(obj,k))
                    continue
                self.assertEqual(created,getattr(obj,k))

        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)

    def test_manager_current(self):
        policies=[ self.random_gdprpolicy() for n in range(random.randint(2,10)) ]
        policy=policies[-1]
        obj=self.model.objects.current()
        self.assertEqual(policy.id,obj.id)

class GDPRAgreementModelTest(TestCase,BaseModelTestMixin):
    model=models.GDPRAgreement
    fields=[ "name","text","version", "created","last_modified" ]
    defaults= {}
    str_format = "%(name)s %(version)s"

    def _data(self,add=[]):
        data= {
            "name": self.random_string(),
            "text": self.random_string(),
            "version": self.random_string(min_size=2,max_size=10),
        }
        return data

    def _wrong_cases(self):
        wrong ={
            "no name": self._data(),
            "no text": self._data(),
            "no version": self._data(),
        }

        wrong["no name"]["name"]=""
        wrong["no text"]["text"]=""
        wrong["no version"]["version"]=""
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
        }
        return correct

    def test_serialize(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        ser=obj.__serialize__()
        for k in self.fields:
            self.assertIn(k,ser)
            if k not in ["created","last_modified"]:
                self.assertEqual(ser[k],data[k])
                continue
            self.assertJsonIsTimestamp(ser[k])

    def test_created_always_in_the_past(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        created_past=self.random_datetime_utc(max_year=2019)
        created_future=self.random_datetime_utc(max_year=2500,min_year=2100)

        obj.created=created_past
        obj.full_clean()
        obj.save()
        obj.created=created_future
        with self.assertRaises(ValidationError):
            obj.full_clean()
            obj.save()
        

    def test_deserialize(self):
        ser=self._data()
        created=self.random_datetime_utc()
        last_modified=created+self.random_timedelta()
        ser["created"]=functions.date_serialize(created)
        ser["last_modified"]=functions.date_serialize(last_modified)
        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            with self.subTest(field=k):
                self.assertTrue(hasattr(obj,k))
                if k=="last_modified": continue
                if k not in ["created","last_modified"]:
                    self.assertEqual(ser[k],getattr(obj,k))
                    continue
                self.assertEqual(created,getattr(obj,k))

        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)

    def test_unique_name_version(self):
        data1=self._data()
        obj1 = self.model(**(data1))
        obj1.full_clean()
        obj1.save() # pragma: no cover

        data2=self._data()
        data2["version"]=data1["version"]
        data2["name"]=data1["name"]

        wrong={
            "both": data2
        }

        data3=self._data()
        data4=self._data()
        data3["version"]=data1["version"]
        data4["name"]=data1["name"]

        correct={
            "only version": data3,
            "only name": data4,
        }

        for k in correct:
            with self.subTest(correct_case=k):
                d2=correct[k]
                obj2 = self.model(**(d2))
                obj2.full_clean()
                obj2.save() # pragma: no cover

        for k in wrong:
            with self.subTest(wrong_case=k):
                d2=wrong[k]
                obj2 = self.model(**(d2))
                with self.assertRaises(ValidationError):
                    obj2.full_clean()
                    obj2.save() # pragma: no cover

