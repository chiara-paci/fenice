# -*- coding: utf-8 -*-

import os
import urllib
import PIL
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from fenicemisc import models

class Image(object):
    base_url='https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=extmetadata&format=json&titles=File%3a'

    def __init__(self,dirname,name,dirthumb):
        self._dirname=dirname
        self._name=name
        self._dirthumb=dirthumb
        self._url=self.base_url+urllib.parse.quote(self._name)

    def _get_info(self):
        data={}
        with urllib.request.urlopen(self._url) as f:
            obj=json.loads(f.read().decode())
            k=list(obj["query"]["pages"].keys())[0]
            data["license"]={}
            data["url"]="https://commons.wikimedia.org/wiki/%s" % obj["query"]["pages"][k]["title"]
            if "imageinfo" in obj["query"]["pages"][k]:
                obj=obj["query"]["pages"][k]["imageinfo"][0]["extmetadata"]
                data["license"]={
                    "short_name": obj["LicenseShortName"]["value"],
                    "long_name": obj["UsageTerms"]["value"],
                }
                if "LicenseUrl" in obj:
                    data["license"]["url"]= obj["LicenseUrl"]["value"]
                data["title"]=obj["ObjectName"]["value"]
                data["description"]=obj["ImageDescription"]["value"]
                data["author"]=obj["Artist"]["value"]
        return data
    
    def _create_thumbnail(self):
        os.makedirs(self._dirthumb,exist_ok=True)
        fname,ext=os.path.splitext(self._name)
        full_path=os.path.join(self._dirname,self._name)
        thumb_name="%s.thumb.webp" % fname
        thumb_path=os.path.join(self._dirthumb,thumb_name)
        try:
            im = PIL.Image.open(full_path)
            im.thumbnail( (64,64) )
            im.save(thumb_path, "WEBP")
            im.close()
        except IOError:
            print("cannot create thumbnail for", full_path)
            return None
        return thumb_path

    def _create_obj(self,thumb_path,data):
        defaults={}
        for k in [ "title","description","author","url" ]:
            if k in data:
                defaults[k]=data[k]
        deflicense={}
        for k in [ "long_name", "url" ]:
            if k in data["license"]:
                deflicense[k]=data["license"][k]
        lic,created=models.OpenLicense.objects.get_or_create(short_name=data["license"]["short_name"],
                                                             defaults=deflicense)
        defaults["license"]=lic

        models.OpenImageCredit.objects.update_or_create(thumb_path=thumb_path,defaults=defaults)



    def __call__(self):
        thumb_path=self._create_thumbnail()
        data=self._get_info()
        self._create_obj(thumb_path,data)

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Look for credit info for images in directory <dir> in WikiMedia Commons'

    def add_arguments(self, parser):
        parser.add_argument(
            'dirname',
            help='Directory of images',
        )

    def handle(self, *args, **options):
        dirname = options["dirname"]

        for entry in os.scandir(dirname):
            if entry.is_dir(): continue
            print(entry.name)
            img=Image(dirname,entry.name,settings.CREDITS_THUMBNAILS_DIR)
            img()
