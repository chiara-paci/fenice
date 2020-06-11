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
    ("browser_list","fenicestat:browser_list"),
    ("browser_create","fenicestat:browser_create"),
])

TEMPLATES={
    "browser_list": "fenicestat/browser_list.html",             
}

VIEWS={
    "browser_list": views.BrowserListCreateView,
    "browser_create": views.BrowserListCreateView,
}

FORMS={
    "browser_create": views.BrowserCreateForm,
}

class FeniceStatMixin(testlib.mixins.TestCommonMixin,testlib.mixins.SerializationMixin,abc.ABC):
    def random_browser(self):

        data= {
            "session_key": self.random_string(),
        }

        for k in [ "code_name",
	           "name",
	           "version",
	           "language",
	           "platform",
	           "user_agent","timezone","iso_timestamps" ]:
            data[k]=self.random_string()

        for k in [ "screen_width", "screen_height", "screen_color_depth", "screen_pixel_depth", 
                   "screen_available_height", "screen_available_width",
                   "viewport_height", "viewport_width" ]:
            data[k]=random.randint(100,2000)

        for k in [ "cookies_enabled",
	           "luxon_intl",
	           "luxon_intl_tokens",
	           "luxon_zones",
	           "luxon_relative" ]:
            data[k]=self.random_boolean()

        return models.Browser.objects.create(**data)
