from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin
from django.contrib import admin

from django.contrib.auth import models as auth_models 

from . import models

# Register your models here.
class UserAdmin(DefaultUserAdmin): pass

admin.site.register(models.User,UserAdmin)
admin.site.register(models.Group,DefaultGroupAdmin)

admin.site.unregister(auth_models.Group)

admin.site.register(auth_models.Permission)
