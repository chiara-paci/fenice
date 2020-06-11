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

from django.test import TestCase

class BaseModelTestMixin(common.FeniceMiscMixin,abc.ABC): 
    model=None
    fields=[]
    defaults={}

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

class OpenLicenseModelTest(TestCase,BaseModelTestMixin):
    model=models.OpenLicense
    fields=[ "short_name","long_name", "url" ]
    defaults= {
        "url": "",
    }

    def _data(self,add=[]):
        data= {
            "short_name": self.random_string(),
            "long_name": self.random_string(),
        }
        if "url" in add:
            data["url"]=self.random_url()
        return data

    def _wrong_cases(self):
        wrong ={
            "no short name": self._data(),
            "no long name": self._data(),
            "no short name (url)": self._data(add=["url"]),
            "no long name (url)": self._data(add=["url"]),
            "wrong url": self._data(add=["url"]),
        }

        wrong["no short name"]["short_name"]=""
        wrong["no short name (url)"]["short_name"]=""
        wrong["no long name"]["long_name"]=""
        wrong["no long name (url)"]["long_name"]=""
        wrong["wrong url"]["url"]=self.random_string()
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
            "with url": self._data(add=["url"])
        }
        return correct

    def test_str(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        self.assertEqual("%(short_name)s - %(long_name)s" % data,str(obj))

    def test_serialize(self):
        data=self._data(add=["url"])
        obj=self.model.objects.create(**data)
        ser=obj.__serialize__()
        for k in self.fields:
            self.assertIn(k,ser)
            self.assertEqual(ser[k],data[k])

    def test_deserialize(self):
        ser=self._data(add=["url"])
        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            self.assertTrue(hasattr(obj,k))
            self.assertEqual(ser[k],getattr(obj,k))
        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)
        
    def test_unique_short_name(self):
        data1=self._data()
        data2=self._data()
        data2["short_name"]=data1["short_name"]
        obj1 = self.model(**(data1))
        obj1.full_clean()
        obj1.save() # pragma: no cover
        obj2 = self.model(**(data1))
        with self.assertRaises(ValidationError):
            obj2.full_clean()
            obj2.save() # pragma: no cover


class OpenImageCreditModelTest(TestCase,BaseModelTestMixin):
    model=models.OpenImageCredit

    fields=[
        'thumb_path',
        'title',
        'license',
        'description',
        'author',
        'url',
    ]

    defaults={
        'title': "",
        'license': models.get_default_open_license,
        'description': "",
        'author': "",
        'url': "",
    }

    def _data(self,add=[]):
        data={
            "thumb_path": os.path.join(settings.CREDITS_THUMBNAILS_DIR,self.random_path())
        }
        if "license" in add:
            data["license"]=self.random_openlicense()
        if "url" in add:
            data["url"]=self.random_url()
        for k in [ 'title',
                   'description',
                   'author' ]:
            if k in add:
                data[k]=self.random_string()
        return data

    def _wrong_cases(self):
        wrong ={
            "no thumb": self._data(),
            "wrong url": self._data(add=["url"]),
        }

        wrong["no thumb"]["thumb_path"]=""
        wrong["wrong url"]["url"]=self.random_string()
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
            "with url": self._data(add=["url"]),
            "with license": self._data(add=["license"]),
            "with all": self._data(add=["url","license","title","author","description"]),
        }
        return correct

    def test_deserialize(self):
        ser=self._data(add=["url","title","description","author","license"])
        obj_license=ser["license"]
        ser["license"]=ser["license"].__serialize__()
        ser["thumb_path"]=os.path.relpath(ser["thumb_path"],settings.CREDITS_THUMBNAILS_DIR)
        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            self.assertTrue(hasattr(obj,k))
            if k=="thumb_path":
                self.assertEqual(os.path.join(settings.CREDITS_THUMBNAILS_DIR,ser[k]),getattr(obj,k))
                continue
            if k != "license":
                self.assertEqual(ser[k],getattr(obj,k))
                continue
            for kl in ["short_name","long_name","url"]:
                self.assertTrue(hasattr(obj.license,kl))
                self.assertEqual(ser["license"][kl],getattr(obj.license,kl))
                
        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)


    def test_serialize(self):
        data=self._data(add=["url","title","description","author","license"])
        obj=self.model.objects.create(**data)
        ser=obj.__serialize__()
        for k in self.fields:
            self.assertIn(k,ser)
            if k=="thumb_path":
                self.assertEqual(ser[k],os.path.relpath(data[k],settings.CREDITS_THUMBNAILS_DIR))
                continue
            if k!="license":
                self.assertEqual(ser[k],data[k])
                continue
            self.assertIn("license",ser)
            self.assertEqual(ser[k]["short_name"],data[k].short_name)
            self.assertEqual(ser[k]["long_name"],data[k].long_name)
            self.assertEqual(ser[k]["url"],data[k].url)


    def test_unique_thumb_path(self):
        data1=self._data()
        data2=self._data()
        data2["thumb_path"]=data1["thumb_path"]
        obj1 = self.model(**(data1))
        obj1.full_clean()
        obj1.save() # pragma: no cover
        obj2 = self.model(**(data1))
        with self.assertRaises(ValidationError):
            obj2.full_clean()
            obj2.save() # pragma: no cover

    def test_thumb_url(self):
        rel_path=self.random_path()
        thumb_path=os.path.join(settings.CREDITS_THUMBNAILS_DIR,rel_path)
        thumb_context=os.path.join(settings.CREDITS_THUMBNAILS_CONTEXT,rel_path)
        credit=models.OpenImageCredit.objects.create(thumb_path=thumb_path)
        self.assertEqual(credit.thumb_url,thumb_context)

    def test_thumb_name(self):
        rel_path=self.random_path()
        name=rel_path.split("/")[-1]
        thumb_path=os.path.join(settings.CREDITS_THUMBNAILS_DIR,rel_path)
        thumb_context=os.path.join(settings.CREDITS_THUMBNAILS_CONTEXT,rel_path)
        credit=models.OpenImageCredit.objects.create(thumb_path=thumb_path)
        self.assertEqual(credit.thumb_name,name)

    def test_str(self):
        data=self._data()
        obj=self.model.objects.create(**data)
        self.assertEqual("%(thumb_path)s" % data,str(obj))
    
