from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings

import urllib.parse
import random
import string
import os

from django.contrib.auth import get_user_model

User=get_user_model()

from mybrowser import navigator,parsers,mixins
from urllib_tests import configdicts as cfg

class CPageParser(parsers.PageParser):
    def has_anonymous_mainbar(self):
        self.has_navbar(id=cfg.NAVBARS["mainbar"])
        self.has_link(cfg.URLS["home"])
        self.has_link(cfg.URLS["login"])
        self.has_link(cfg.URLS["register"])
        
    def has_mainbar(self):
        self.has_navbar(id=cfg.NAVBARS["mainbar"])
        self.has_link(cfg.URLS["home"])
        self.has_link(cfg.URLS["logout"])
        self.has_link(cfg.URLS["profile"])

class UserDesc(object):
    def __init__(self,username,password,email,first_name,last_name):
        self.username=username
        self.password=password
        self.email=email
        self.first_name=first_name
        self.last_name=last_name
        self.django_object=None

    def insert_user_in_django(self):
        self.django_object  = User.objects.create_user(self.username,self.email,self.password)
        return self.django_object

class RandomUser(UserDesc):
    def _random_string(self,size=0):
        if not size:
            size=random.choice(range(3,10))
        chars=string.ascii_lowercase +string.ascii_uppercase + string.digits
        S=''.join(random.choice(chars) for _ in range(size))
        return S

    def __init__(self):
        username = "USR"+self._random_string()
        email =  self._random_string()+"@"+self._random_string()+"."+self._random_string(size=3)
        password = self._random_string(size=random.choice(range(10,20)))
        first_name = self._random_string()
        last_name = self._random_string()
        UserDesc.__init__(self,username,password,email,first_name,last_name)

class BaseTestCase(StaticLiveServerTestCase,mixins.UnitTestMixin):

    _base_css_list=[ #'css/font-awesome.min-4.7.0.css',
                     'fontawesome-free-5.1.0-web/css/all.css',
                     'js/jquery-ui-1.12.1.custom/jquery-ui.min.css',
                     'css/costruttori.css' ]

    _base_js_list=[ 'js/jquery/jquery-3.2.1.min.js',
                    'js/jquery-ui-1.12.1.custom/jquery-ui.min.js',
                    'js/ckeditor-4.7.2/ckeditor.js',
                    'js/ckeditor-4.7.2/adapters/jquery.js' ]

    _base_icon_file='brand/mondo-ico.png'

    def _static(self,path):
        return settings.STATIC_URL+path

    def create_random_user(self,create=True):
        user=RandomUser()
        if create:
            obj=user.insert_user_in_django()
        return user

    def _build_url(self,nav,label,**kwargs):
        return self._full_url(nav,cfg.URLS[label] % kwargs)

    def get_parser(self,response):
        parser=CPageParser(self)
        parser.feed(response.text)
        return parser

    def _login(self,nav,parser_class,user=None):
        if not user:
            user=self.create_random_user()
        response=self._assert_url_exists(nav,self._full_url(nav,cfg.URLS["login"]))
        parser=CPageParser(self)
        parser.feed(response.text)
        elem=parser.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")
        response=self._form_submit(nav,elem,username=user.username,password=user.password)
        parser=parser_class(self)
        parser.feed(response.text)
        parser.has_win_title(cfg.WIN_TITLES["profile"] % { "user": user.username })
        parser.has_title(cfg.TITLES["profile"] % { "user": user.username })
        parser.has_userbar()
        return user,parser

    def _logout(self,nav,parser): 
        parser.has_link(cfg.URLS["logout"])
        elem=parser.has_link.get(cfg.URLS["logout"])
        response=self._click_link(nav,elem)
        parser=CPageParser(self)
        parser.feed(response.text)
        parser.has_win_title(cfg.WIN_TITLES["login"])
        parser.has_title(cfg.TITLES["login"] )
        return parser

class SingleUserTestCase(BaseTestCase):
    def setUp(self):
        self._navigator=navigator.Navigator(".djangotest/cookiefile.%d" % os.getpid())

    def full_url(self,url):
        return self._full_url(self._navigator,url)

    def build_url(self,label,**kwargs):
        return self._build_url(self._navigator,label,**kwargs)

    def assert_url_exists(self,url,decode_text=True):
        return self._assert_url_exists(self._navigator,url,decode_text=decode_text)

    def assert_404(self,url):
        return self._assert_404(self._navigator,url)

    def form_submit(self,form_elem,**kwargs):
        return self._form_submit(self._navigator,form_elem,**kwargs)

    def form_submit_with_files(self,form_elem,files,**kwargs):
        return self._form_submit_with_files(self._navigator,form_elem,files,**kwargs)

    def click_link(self,a_elem): 
        return self._click_link(self._navigator,a_elem)

    def login(self,parser_class,user=None):
        return self._login(self._navigator,parser_class,user=user)

    def logout(self,parser): 
        return self._logout(self._navigator,parser)

class MultiUserTestCase(BaseTestCase):
    num_navigators=2

    def setUp(self):
        self._navigator_list=[ navigator.Navigator(".djangotest/cookiefile.%d.%d" % (os.getpid(),n)) for n in range(0,self.num_navigators) ]

    def full_url(self,ind,url):
        return self._full_url(self._navigator_list[ind],url)

    def build_url(self,ind,label,**kwargs):
        return self._build_url(self._navigator_list[ind],label,**kwargs)

    def assert_url_exists(self,ind,url,decode_text=True):
        return self._assert_url_exists(self._navigator_list[ind],url,decode_text=decode_text)

    def assert_404(self,ind,url):
        return self._assert_404(self._navigator_list[ind],url)

    def form_submit(self,ind,form_elem,**kwargs): 
        return self._form_submit(self._navigator_list[ind],form_elem,**kwargs)

    # def form_submit_with_files(self,ind,form_elem,files,**kwargs):
    #     return self._form_submit_with_files(self._navigator_list[ind],form_elem,files,**kwargs)

    def click_link(self,ind,a_elem): 
        return self._click_link(self._navigator_list[ind],a_elem)

    def login(self,ind,parser_class,user=None):
        return self._login(self._navigator_list[ind],parser_class,user=user)

    def logout(self,ind,parser): 
        return self._logout(self._navigator_list[ind],parser)

