import unittest
import random
import abc

from django.utils.text import slugify

import os.path

from unittest import skip
from unittest import mock

from django.core.exceptions import ValidationError,PermissionDenied
from django.db.utils import IntegrityError
from django.conf import settings
from django.db import models as dj_models

from . import common
from .. import models

from django.contrib.auth import get_user_model
User=get_user_model()

from fenicemisc import functions

from django.test import TestCase

class BaseModelTestMixin(common.FeniceAuthMixin,abc.ABC): 
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
        obj=self._create(data)

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

    def _init_model(self,data):
        return self.model(**data)

    def test_wrong_cases(self):
        wrong=self._wrong_cases()
        for k in wrong:
            with self.subTest(wrong_case=k):
                obj = self._init_model(wrong[k])
                with self.assertRaises(ValidationError):
                    obj.full_clean()
                    obj.save() # pragma: no cover

    def test_correct_cases(self):
        correct=self._correct_cases()
        for k in correct:
            with self.subTest(correct_case=k):
                obj = self._init_model(correct[k])
                obj.full_clean()
                obj.save() # pragma: no cover

    def test_str(self):
        data=self._data()
        obj=self._create(data)
        self.assertEqual(self.str_format % data,str(obj))

class GroupModelTest(TestCase,BaseModelTestMixin):
    model=models.Group

    fields=["name","description","permissions"]

    defaults = {
        "description": None,
    }

    str_format="%(name)s"

    def _data(self,add=[]):
        data= {
            "name": self.random_string(max_size=150),
        }
        if "description" in add:
            data["description"]=self.random_string()
        if "permissions" in add:
            data["permissions"]=set([ self.random_permission() for n in range(random.randint(2,10))])
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
            "with": self._data(add=["description"]),
        }
        return correct

    def _create(self,data):
        base={}
        for k in [ "name","description" ]:
            if k in data:
                base[k]=data[k]
        obj=self.model.objects.create(**base)
        if "permissions" not in data: return obj
        for perm in data["permissions"]:
            obj.permissions.add(perm)
        return obj

    def test_serialize(self):
        data=self._data(add=["description","permissions"])
        obj=self._create(data)
        ser=obj.__serialize__()
        for k in self.fields:
            self.assertIn(k,ser)
            if k!="permissions":
                self.assertEqual(ser[k],data[k])
                continue
            self.assertEqual(len(ser[k]),len(data[k]))
            for perm in data["permissions"]:
                p_ser=list(filter(lambda x: x["name"]==perm.name,ser["permissions"]))
                self.assertEqual(len(p_ser),1)
                p_ser=p_ser[0]
                self.assertTrue(p_ser["codename"],perm.codename)
                self.assertIn("content_type",p_ser)
                self.assertIn("app_label",p_ser["content_type"])
                self.assertIn("model",p_ser["content_type"])
                self.assertTrue(p_ser["content_type"]["app_label"],perm.content_type.app_label)
                self.assertTrue(p_ser["content_type"]["model"],perm.content_type.model)

    def _perm_serialize(self,perm):
        return {
            "name": perm.name,
            "codename": perm.codename,
            "content_type": {
                "app_label": perm.content_type.app_label,
                "model": perm.content_type.model,
            }
        }

    def test_deserialize(self):
        ser=self._data(add=["description","permissions"])
        permissions=ser["permissions"]
        ser["permissions"]=[self._perm_serialize(p) for p in permissions]
        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            self.assertTrue(hasattr(obj,k))
            if k!="permissions":
                self.assertEqual(ser[k],getattr(obj,k))
                continue
            for perm in permissions:
                self.assertIn(perm,obj.permissions.all())
        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)


class UserModelTest(TestCase,BaseModelTestMixin):
    model=User

    fields=[ "username","first_name","last_name",
             "email","password","date_joined","last_login",
             "is_active" ]
    defaults= {
        "first_name": "",
        "last_name": "",
    }
    str_format = "%(username)s"

    def _create(self,data):
        if "groups" not in data: 
            obj=self.model.objects.create_user(**data)
            return obj
        data=data.copy()
        groups=data["groups"]
        del(data["groups"])
        obj=self.model.objects.create_user(**data)
        for grp in groups:
            obj.groups.add(grp)
        return obj

    def _data(self,add=[]):
        data= {
            "username": self.random_string(max_size=150),
            "email": self.random_email(),
            "password": self.random_string(),
            "is_active": self.random_boolean(),
        }
        if "first_name" in add:
            data["first_name"]=self.random_string(max_size=30)
        if "last_name" in add:
            data["last_name"]=self.random_string(max_size=150)
        if "password" in add:
            data["password"]=self.random_string()
        if "last_login" in add:
            data["last_login"]=self.random_datetime_utc()
        if "groups" in add:
            data["groups"]=set([ self.random_group() for n in range(random.randint(2,10))])
        return data

    def _wrong_cases(self):
        wrong ={
            "no username": self._data(),
            "no email": self._data(),
        }
        wrong["no username"]["username"]=""
        wrong["no email"]["email"]=""
        return wrong

    def _correct_cases(self):
        correct={
            "base": self._data(),
            "with": self._data(add=["last_name","first_name","password"]),
        }
        return correct

    def test_unique_username(self):
        data1=self._data()
        data2=self._data()
        data2["username"]=data1["username"]
        obj1 = self._init_model(data1)
        obj1.full_clean()
        obj1.save() # pragma: no cover
        obj2 = self._init_model(data1)
        with self.assertRaises(ValidationError):
            obj2.full_clean()
            obj2.save() # pragma: no cover

    def test_unique_email(self):
        data1=self._data()
        data2=self._data()
        data2["email"]=data1["email"]
        obj1 = self._init_model(data1)
        obj1.full_clean()
        obj1.save() # pragma: no cover
        obj2 = self._init_model(data1)
        with self.assertRaises(ValidationError):
            obj2.full_clean()
            obj2.save() # pragma: no cover

    def test_user_create_method_triggers_warning(self):
        username=self.random_string(min_size=8,max_size=150,with_spaces=False)
        password=self.random_string(max_size=128)
        email=self.random_email(max_size=254)
        with self.assertWarns(models.UserCreateMethodWarning):
            user=User.objects.create(username=username,email=email,password=password)

    def test_email_is_always_lowercase(self):
        username=self.random_string(min_size=8,max_size=150,with_spaces=False)
        password=self.random_string(max_size=128)
        email=self.random_email(max_size=254)
        user=User.objects.clean_and_create_user(username=username,email=email,password=password)
        self.assertEqual(user.email,email.lower(),
                         msg="Email %s is not saved with lower case" % user.email)

    def test_serialize(self):
        data=self._data(add=["last_name","first_name","last_login","groups"])
        obj=self._create(data)
        ser=obj.__serialize__()
        for k in self.fields:
            if k=="password":
                self.assertNotIn(k,ser)
                continue
            self.assertIn(k,ser)
            if k=="email":
                self.assertEqual(ser[k],data[k].lower())
                continue
            if k=="date_joined":
                self.assertJsonIsTimestamp(ser[k])
                continue
            if k=="last_login":
                self.assertJsonIsTimestamp(ser[k])
                continue
            if k!="groups":
                self.assertEqual(ser[k],data[k])
                continue
            self.assertEqual(len(ser[k]),len(data[k]))
            for grp in data["groups"]:
                g_ser=list(filter(lambda x: x==grp.name,ser["groups"]))
                self.assertEqual(len(g_ser),1)
                g_ser=g_ser[0]
                self.assertTrue(g_ser,grp.name)

    def test_deserialize(self):
        ser=self._data(add=["last_name","first_name","last_login","groups"])
        date_joined=self.random_datetime_utc()
        last_login=ser["last_login"]
        groups=ser["groups"]
        ser["groups"]=[g.name for g in groups]
        ser["date_joined"]=functions.date_serialize(date_joined)
        ser["last_login"]=functions.date_serialize(last_login)
        del(ser["password"])
        obj=self.model.objects.deserialize(ser)
        for k in self.fields:
            self.assertTrue(hasattr(obj,k))
            if k=="password": continue
            if k=="email":
                self.assertEqual(ser[k].lower(),obj.email)
                continue
            if k=="date_joined":
                self.assertEqual(date_joined,getattr(obj,k))
                continue
            if k=="last_login":
                self.assertEqual(last_login,getattr(obj,k))
                continue
            if k!="groups":
                self.assertEqual(ser[k],getattr(obj,k))
                continue
            for grp in groups:
                self.assertIn(grp,obj.groups.all())
                
        obj2=self.model.objects.deserialize(ser)
        self.assertEqual(obj.id,obj2.id)

