from testlib import utility
from django.views.generic import TemplateView,ListView
from django.conf import settings

import os.path
import testlib.mixins
import abc
import random

from .. import models
from .. import views

get_url=utility.GetUrl(other_urls=[ 
    ("policy","fenicegdpr:policy"),
])

TEMPLATES={
    "policy": "fenicegdpr/policy.html",             
}

VIEWS={
    "policy": views.PolicyView,
}

class FeniceGdprMixin(testlib.mixins.TestCommonMixin,testlib.mixins.SerializationMixin,abc.ABC):
    def random_gdprpolicy(self):
        text=self.random_string()
        version=self.random_string(max_size=10,min_size=1)
        return models.GDPRPolicy.objects.create(text=text,version=version)
    
    def random_gdpragreement(self):
        name=self.random_string()
        text=self.random_string()
        version=self.random_string(max_size=10,min_size=1)
        return models.GDPRAgreement.objects.create(text=text,version=version,name=name)

