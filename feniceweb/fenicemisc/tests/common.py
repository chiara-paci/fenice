from testlib import utility
from django.views.generic import TemplateView,ListView
from django.conf import settings

import os.path
import testlib.mixins
import abc
import random

from .. import models
from .. import views

#from fenicegdpr import models as gdpr_models

get_url=utility.GetUrl(other_urls=[ 
    ("home","home"),
    ("credits","credits"), 
])

TEMPLATES={
    "home": "fenicemisc/index.html",             
    "credits": "fenicemisc/credits.html", 
}

VIEWS={
    "home": views.HomePageView,
    "credits": views.CreditsView,
}


class FeniceMiscMixin(testlib.mixins.TestCommonMixin,abc.ABC):

    def random_openlicense(self):
        short_name=self.random_string()
        long_name=self.random_string()
        if random.choice([True,False]):
            url=self.random_url()
            return models.OpenLicense.objects.create(short_name=short_name,long_name=long_name,url=url)
        return models.OpenLicense.objects.create(short_name=short_name,long_name=long_name)
    
    def random_openimagecredit(self):
        data={
            "thumb_path": os.path.join(settings.CREDITS_THUMBNAILS_DIR,self.random_path())
        }

        if random.choice([True,False]):
            data["license"]=self.random_openlicense()
        if random.choice([True,False]):
            data["url"]=self.random_url()
        for k in [ 'title',
                   'description',
                   'author' ]:
            if random.choice([True,False]):
                data[k]=self.random_string()
        return models.OpenImageCredit.objects.create(**data)

