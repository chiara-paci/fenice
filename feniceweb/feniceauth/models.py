from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser,Permission
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.auth.models import GroupManager as DjangoGroupManager
from django.contrib.auth.models import Group as DjangoGroup

from fenicemisc import functions

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.contrib.contenttypes.models import ContentType

import warnings

from . import validators

# Create your models here.

class GroupManager(DjangoGroupManager):
    def deserialize(self,ser): 
        if "description" in ser:
            defaults={"description": ser["description"]}
        obj,created=self.update_or_create(name=ser["name"],defaults=defaults)
        if "permissions" not in ser: return obj
        
        for s_perm in ser["permissions"]:
            ctype = ContentType.objects.get(app_label=s_perm["content_type"]["app_label"], model=s_perm["content_type"]["model"])
            perm = Permission.objects.get(codename=s_perm["codename"],content_type=ctype)
            obj.permissions.add(perm)

        return obj

class Group(DjangoGroup):
    description=models.CharField(max_length=4096,null=True, blank=True)
    objects=GroupManager()

    def _perm_serialize(self,perm):
        return {
            "name": perm.name,
            "codename": perm.codename,
            "content_type": {
                "app_label": perm.content_type.app_label,
                "model": perm.content_type.model,
            }
        }

    def __serialize__(self):
        ret={
            "name": self.name,
            "description": self.description,
            "permissions": [ self._perm_serialize(p) for p in self.permissions.all() ],
        }
        return ret

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

class UserCreateMethodWarning(DeprecationWarning): pass

class UserManager(DjangoUserManager):
    @classmethod
    def normalize_email(cls, email):
        if email is None: return None
        return email.lower()

    def create(self,*args,**kwargs):
        warnings.warn("Avoid UserManager.create() method, instead use create_user() or clean_and_create_user()",
                      UserCreateMethodWarning)
        return DjangoUserManager.create(self,*args,**kwargs)

    def clean_and_create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)
        """
        Create and save a user with the given username, email, and password, and validate it before actual saving.
        """
        # if not username:
        #     raise ValueError('The given username must be set',code="required")
        # if not email:
        #     raise ValueError('The given email must be set',code="required")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        if password is None:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        return user

    def deserialize(self,ser):
        ser=ser.copy()
        if "groups" in ser:
            groups=ser["groups"]
            del(ser["groups"])
        else:
            groups=[]
        if "date_joined" in ser:
            ser["date_joined"]=functions.date_deserialize(ser["date_joined"])
        if "last_login" in ser:
            ser["last_login"]=functions.date_deserialize(ser["last_login"])
        try:
            user=self.clean_and_create_user(**ser)
        except ValidationError as e:
            if "username" in e.error_dict:
                user=self.get(username=ser["username"])
            elif "email" in e.error_dict:
                user=self.get(email=ser["email"])
            else:
                raise e
        for name in groups:
            grp=Group.objects.get(name=name)
            user.groups.add(grp)
        return user

class User(AbstractUser):
    objects=UserManager()
    username_validator = validators.UsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    email = models.EmailField(_('email address'), 
                              unique=True,
                              error_messages={
                                  'unique': _("A user with that email already exists."),
                              })

    # password
    # is_superuser (no ser.)
    # is_staff (no ser.)
    # is_active
    # date_joined
    # last_login
    # first_name
    # last_name
    # groups
    # user_permissions (no ser.)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self,*args,**kwargs):
        self.email=UserManager.normalize_email(self.email)
        AbstractUser.save(self,*args,**kwargs)

    def __serialize__(self):
        ret={
            "username": self.username,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "email": self.email,
            "is_active": self.is_active,
            "date_joined": functions.date_serialize(self.date_joined),
        }
        if self.last_login:
            ret["last_login"]=functions.date_serialize(self.last_login)
        return ret

