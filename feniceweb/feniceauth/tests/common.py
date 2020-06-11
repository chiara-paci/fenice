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


    # def random_blog_category(self):
    #     name=self.random_string()
    #     return models.BlogCategory.objects.create(name=name)

    # def random_tag(self):
    #     name=self.random_string()
    #     return models.Tag.objects.create(name=name)

    # def random_gdpragreement(self):
    #     name=self.random_string()
    #     text=self.random_string()
    #     version=self.random_string(max_size=10,min_size=1)
    #     return gdpr_models.GDPRAgreement.objects.create(text=text,version=version,name=name)

    # def random_gdprpolicy(self):
    #     text=self.random_string()
    #     version=self.random_string(max_size=10,min_size=1)
    #     return gdpr_models.GDPRPolicy.objects.create(text=text,version=version)

    # # def random_avatar_category(self):
    # #     name=self.random_string()
    # #     return models.AvatarCategory.objects.create(name=name)

    # def random_product_category(self):
    #     name=self.random_string()
    #     return models.ProductCategory.objects.create(name=name)

    # def random_product(self,cat=None):
    #     if cat is None:
    #         cat=self.random_product_category()
    #     data= {
    #         "name": self.random_string(),
    #         "category": cat,
    #         "image_path": os.path.join(settings.GAMES_PRODUCTS_DIR,self.random_path()),
    #         "description": self.random_string(),
    #     }
    #     return models.Product.objects.create(**data)


    # def random_family(self):
    #     data= {
    #         "cap": self.random_cap(),
    #         "session_key": self.random_string(),
    #     }
    #     return models.Family.objects.create(**data)

    # def random_email_obj(self):
    #     data= {
    #         "email": self.random_email(),
    #         "agreement": self.random_gdpragreement(),
    #         "policy": self.random_gdprpolicy(),
    #         "accept": self.random_boolean(),
    #     }
    #     return models.Email.objects.create(**data)

    # # def random_avatar(self):
    # #     data= {
    # #         "name": self.random_string(),
    # #         "category": self.random_avatar_category(),
    # #         "image_path": os.path.join(settings.GAMES_AVATARS_DIR,self.random_path())
    # #     }
    # #     return models.Avatar.objects.create(**data)
