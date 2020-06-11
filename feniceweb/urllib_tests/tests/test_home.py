from unittest import skip

from urllib_tests import base
from urllib_tests import configdicts as cfg
from django.test import override_settings

from mybrowser import parsers

@override_settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),))
class HomeTest(base.SingleUserTestCase):

    def test_home_page_welcome_users(self):
        # Random user goes to the awesome writing site
        # and notices a "Welcome" title in the page.

        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["home"])))
        parser.has_win_title(cfg.WIN_TITLES["home"])
        #parser.has_title(cfg.TITLES["home"] )
        parser.has_anonymous_mainbar()

@override_settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),))
class StaticPagesTest(base.SingleUserTestCase):

    def _test_static(self,label):
        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS[label])))
        parser.has_win_title(cfg.WIN_TITLES[label])
        parser.has_title(cfg.TITLES[label] )
        parser.has_anonymous_mainbar()

    def test_credits(self): 
        self._test_static("credits")

    def test_prolicy(self): 
        self._test_static("policy")
