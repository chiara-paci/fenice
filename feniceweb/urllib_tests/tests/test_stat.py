from unittest import skip

from urllib_tests import base
from urllib_tests import configdicts as cfg
from django.test import override_settings

from mybrowser import parsers

@override_settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),))
class StatTest(base.SingleUserTestCase):

    def _test_static(self,label):
        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS[label])))
        parser.has_win_title(cfg.WIN_TITLES[label])
        parser.has_title(cfg.TITLES[label] )
        parser.has_anonymous_mainbar()

    # GET: 404
    # POST html: 404
    # POST json: 201


    # def test_browser_list(self): 
    #     self._test_static("browser_list")

    # def test_browser_create(self): 
    #     self._test_static("browser_create")
