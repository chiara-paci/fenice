from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
import os.path

from . import functions

#from .fields import *

# Create your models here.

class OpenLicenseManager(models.Manager):
    def deserialize(self,ser):
        defaults={
            "long_name": ser["long_name"],
            "url": ser["url"]
        }
        
        obj,created=self.update_or_create(short_name=ser["short_name"],defaults=defaults)
        return obj

class OpenLicense(models.Model):
    short_name = models.CharField(max_length=512,unique=True)
    long_name = models.CharField(max_length=4096)
    url = models.URLField(max_length=4096,default="",blank=True)

    objects=OpenLicenseManager()

    def __str__(self):
        return "%s - %s" % (self.short_name,self.long_name)

    def __serialize__(self):
        return {
            "short_name": self.short_name,
            "long_name": self.long_name,
            "url": self.url,
        }

def get_default_open_license():
    lic,create=OpenLicense.objects.get_or_create(short_name="CC BY-SA 4.0",defaults = {
        "long_name":"Creative Commons Attribution-Share Alike 4.0",
        "url":"https://creativecommons.org/licenses/by-sa/4.0/"
    })
    return lic.id

class OpenImageCreditManager(models.Manager):
    def deserialize(self,ser):
        defaults={
            "title": ser["title"],
            "description": ser["description"],
            "author": ser["author"],
            "url": ser["url"],
            "license": OpenLicense.objects.deserialize(ser["license"])
        }
        thumb_path=os.path.join(settings.CREDITS_THUMBNAILS_DIR,ser["thumb_path"])
        obj,created=self.update_or_create(thumb_path=thumb_path,defaults=defaults)
        return obj

# https://code.djangoproject.com/ticket/29529
def openimagecredit_image_path():
    return settings.CREDITS_THUMBNAILS_DIR

class OpenImageCredit(models.Model):
    thumb_path = models.FilePathField(max_length=4096,path=openimagecredit_image_path,unique=True)
    title = models.CharField(max_length=4096,default="",blank=True)
    license = models.ForeignKey(OpenLicense,on_delete=models.PROTECT,default=get_default_open_license,blank=True)
    description = models.CharField(max_length=4096,default="",blank=True)
    author = models.CharField(max_length=4096,default="",blank=True)
    url = models.URLField(max_length=4096,default="",blank=True)

    objects=OpenImageCreditManager()

    def __str__(self):
        return self.thumb_path

    def __serialize__(self):
        ret= {
            "thumb_path": functions.relative_path(self.thumb_path,settings.CREDITS_THUMBNAILS_DIR),
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "url": self.url,
            "license": self.license.__serialize__()
        }
        return ret

    @cached_property
    def thumb_url(self):
        thumb_path=functions.relative_path(self.thumb_path,settings.CREDITS_THUMBNAILS_DIR)
        thumb_path=os.path.join(settings.CREDITS_THUMBNAILS_CONTEXT,thumb_path)
        return thumb_path

    @cached_property
    def thumb_name(self):
        return os.path.basename(self.thumb_path) 
