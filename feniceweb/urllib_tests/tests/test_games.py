from unittest import skip

from urllib_tests import base
from urllib_tests import configdicts as cfg
from django.test import override_settings

from mybrowser import parsers

@override_settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),))
class GamesTest(base.SingleUserTestCase):

    def _test_static(self,label):
        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS[label])))
        parser.has_win_title(cfg.WIN_TITLES[label])
        parser.has_title(cfg.TITLES[label] )
        parser.has_anonymous_mainbar()

    def test_family_on_field(self): 
        self._test_static("familyonfield")

    # [list]   GET: 404
    # [create] POST html: 404
    # [create] POST json: 201

    # def test_family_list(self): 
    #     self._test_static("family_list")

    # def test_family_create(self): 
    #     self._test_static("family_create")

    # def test_email_list(self): 
    #     self._test_static("email_list")

    # def test_email_create(self): 
    #     self._test_static("email_create")
