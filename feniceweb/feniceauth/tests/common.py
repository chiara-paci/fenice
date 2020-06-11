from testlib import utility
from django.conf import settings

from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.dates import ArchiveIndexView

import os.path
import testlib.mixins
import abc
import random

from .. import models
from django.contrib.auth import models as auth_models 

#from .. import views,forms

#from fenicegdpr import models as gdpr_models
#from fenicemisc import views as misc_views

get_url=utility.GetUrl(other_urls=[ 
    ("profile","feniceauth:profile"),
])

TEMPLATES={
    "profile": "feniceauth/profile.html",             
}

VIEWS={
    "profile": TemplateView,
}

FORMS={
}


class FeniceAuthMixin(testlib.mixins.TestCommonMixin,testlib.mixins.SerializationMixin,abc.ABC): 

    def random_permission(self): 
        perms=auth_models.Permission.objects.all()
        return random.choice(perms)

    def random_group(self):
        data= {
            "name": self.random_string(max_size=150),
        }
        data["description"]=self.random_string()
        return models.Group.objects.create(**data)

