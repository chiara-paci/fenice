import unittest
import random
import abc
from django.contrib.auth import get_user_model
User=get_user_model()

from django.utils.text import slugify

import os.path

from unittest import skip
from unittest import mock

from django.core.exceptions import ValidationError,PermissionDenied
from django.db.utils import IntegrityError
from django.conf import settings
from django.db import models as dj_models

from django.urls import reverse_lazy

from . import common
from .. import models

from fenicemisc import functions

from django.test import TestCase

class BaseModelTestMixin(common.FeniceBlogMixin,abc.ABC): 
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

    def _create(self,data):
        return self.model.objects.create(**data)

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

class NameOnlyTestMixin(BaseModelTestMixin,abc.ABC):
    fields=[ "name" ]
    defaults= {}
    str_format = "%(name)s"

    def _data(self,add=[]):
        data= {
            "name": self.random_string(),
        }
        return data

    def _wrong_cases(self):
        wrong ={
            "no name": self._data(),
        }

        wrong["no name"]["name"]=""
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
        }
        return correct

    def test_unique_name(self):
        data1=self._data()
        data2=self._data()
        data2["name"]=data1["name"]
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
        self.assertEqual(ser,obj.name)

    def test_deserialize(self):
        ser=self._data()
        ser=ser["name"]
        obj=self.model.objects.deserialize(ser)
        self.assertEqual(ser,obj.name)
        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)

    def test_slug(self):
        data=self._data()
        data["name"]+=" "+self.random_string()
        obj=self.model.objects.create(**data)
        self.assertEqual(obj.slug,slugify(obj.name).replace('-','_'))

    
# class BlogCategoryModelTest(TestCase,NameOnlyTestMixin):
#     model=models.BlogCategory

# class TagModelTest(TestCase,NameOnlyTestMixin):
#     model=models.Tag

class ArticleModelTest(TestCase,BaseModelTestMixin):
    model=models.Article

    fields=[ "title","content","publishing_date","visible",
             "created","last_modified",
             "created_by","last_modified_by" ]
    defaults= {
        "visible": True,
    }
    str_format = "%(title)s"

    def setUp(self):
        self.user=User.objects.clean_and_create_user(username=self.random_string(max_size=30,min_size=4),
                                                     password=self.random_string(max_size=30,min_size=8),
                                                     email=self.random_email())
        

    def _data(self,add=[]):
        data= {
            "title": self.random_string(),
            "content": self.random_string(),
            "publishing_date": self.random_datetime_utc(),
        }
        if "visible" in add:
            data["visible"]=self.random_boolean()
        if "created_by" in add:
            data["created_by"]=self.random_user()
        if "last_modified_by" in add:
            data["last_modified_by"]=self.random_user()
        return data

    def _wrong_cases(self):
        wrong ={
            "no title": self._data(),
            "no content": self._data(),
            "no publishing date": self._data(),
        }
        wrong["no title"]["title"]=""
        wrong["no content"]["content"]=""
        wrong["no publishing date"]["publishing_date"]=""
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
            "with visible": self._data(add=["visible"]),
        }
        return correct

    def test_slug(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        self.assertEqual(obj.slug,slugify(obj.title))

    def test_get_absolute_url(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        exp=reverse_lazy("feniceblog:article",kwargs={"pk": obj.pk, "slug": obj.slug})

    def test_unique_title(self):
        data1=self._data()
        data2=self._data()
        data2["title"]=data1["title"]
        obj1 = self.model(**(data1))
        obj1.full_clean()
        obj1.save() # pragma: no cover
        obj2 = self.model(**(data1))
        with self.assertRaises(ValidationError):
            obj2.full_clean()
            obj2.save() # pragma: no cover

    def test_serialize(self):
        data=self._data(add=["visible","created_by","last_modified_by"])
        obj=self.model.objects.create(**data)
        ser=obj.__serialize__()
        for k in self.fields:
            self.assertIn(k,ser)
            if k in ["created","last_modified","publishing_date"]:
                self.assertJsonIsTimestamp(ser[k])
                continue
            if k in ["created_by","last_modified_by"]:
                u=getattr(obj,k)
                for j in ["username","email","last_name","first_name" ]:
                    self.assertIn(j,ser[k])
                    self.assertEqual(ser[k][j],getattr(u,j))
                continue
            self.assertEqual(ser[k],data[k])

    def test_deserialize(self):
        ser=self._data(add=["visible","created_by","last_modified_by"])
        created=self.random_datetime_utc()
        last_modified=created+self.random_timedelta()
        unser={
            "publishing_date": ser["publishing_date"],
            "created_by": ser["created_by"],
            "last_modified_by":ser["last_modified_by"],
            "created": created
        }
        ser["created"]=functions.date_serialize(created)
        ser["last_modified"]=functions.date_serialize(last_modified)
        ser["publishing_date"]=functions.date_serialize(ser["publishing_date"])
        ser["created_by"]=ser["created_by"].__serialize__()
        ser["last_modified_by"]=ser["last_modified_by"].__serialize__()

        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            self.assertTrue(hasattr(obj,k))
            if k=="last_modified": continue
            if k in unser:
                self.assertEqual(unser[k],getattr(obj,k))
                continue
            self.assertEqual(ser[k],getattr(obj,k))
        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)

