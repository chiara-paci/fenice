import re
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.utils.translation import gettext_lazy as _

class UsernameValidator(object):
    def __call__(self,value): return None

    def deconstruct(self):
        return "feniceauth.validators.UsernameValidator",[],{}

