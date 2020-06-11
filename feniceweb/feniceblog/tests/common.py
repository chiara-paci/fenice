from testlib import utility
from django.conf import settings

from django.views.generic import ListView, DetailView
from django.views.generic.dates import ArchiveIndexView

import os.path
import testlib.mixins
import abc
import random

from django.contrib.auth import get_user_model
User=get_user_model()

from .. import models

get_url=utility.GetUrl(other_urls=[ 
    ("article_archive","feniceblog:article_archive"),
    ("article_detail","feniceblog:article_detail"),
])

TEMPLATES={
    "article_archive": "feniceblog/article_archive.html",             
    "article_detail": "feniceblog/article_detail.html",             
}

VIEWS={
    "article_archive": ArchiveIndexView,
    "article_detail": DetailView,
}

FORMS={
}


class FeniceBlogMixin(testlib.mixins.TestCommonMixin,testlib.mixins.SerializationMixin,abc.ABC): 

    def random_blog_category(self):
        name=self.random_string()
        return models.BlogCategory.objects.create(name=name)

    def random_tag(self):
        name=self.random_string()
        return models.Tag.objects.create(name=name)

    def random_article(self):
        data= {
            "title": self.random_string(),
            "content": self.random_string(),
            "publishing_date": self.random_datetime_utc(),
        }
        data["visible"]=self.random_boolean()
        return models.Article.objects.create(**data)

    def random_user(self):
        return User.objects.clean_and_create_user(username=self.random_string(max_size=30,min_size=4),
                                                  password=self.random_string(max_size=30,min_size=8),
                                                  email=self.random_email())
  

