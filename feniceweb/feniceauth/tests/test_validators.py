# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError,FieldDoesNotExist
#from django.core.validators import EmailValidator

from unittest import mock,skip

from . import common
from .. import validators


class UsernameValidatorTest(common.FeniceAuthMixin):
    def test_valid_username(self):
        username=self.random_string()
        validator=validators.UsernameValidator()
        ret=validator(username)
        self.assertIsNone(ret)

    def test_has_deconstruct(self):
        validator=validators.UsernameValidator()
        self.assertTrue(hasattr(validator,"deconstruct"))
        path,args,kwargs=validator.deconstruct()
        self.assertEqual(path,"feniceauth.validators.UsernameValidator")
        self.assertEqual(args,[])
        self.assertEqual(kwargs,{})


