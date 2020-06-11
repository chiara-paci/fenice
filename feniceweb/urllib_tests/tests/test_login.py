from unittest import skip

from urllib_tests import base
from urllib_tests import configdicts as cfg
from django.test import override_settings

from mybrowser import parsers

@override_settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),))
class LoginTest(base.SingleUserTestCase):

    def test_login_page_has_login_form(self):
        # Random user goes to the awesome writing site
        # and notices a "Welcome" title in the page.

        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["login"])))

        parser.has_win_title(cfg.WIN_TITLES["login"])
        parser.has_title(cfg.TITLES["login"] )
        parser.has_form(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")
        parser.has_input(name="username",type="text")
        parser.has_input(name="password",type="password")
        parser.has_input(type="submit",value="login")

    def test_random_user_login_logout(self):
        user=self.create_random_user()

        # Random user goes to the awesome writing site
        # and notices a "Log in" form
        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["login"])))

        elem=parser.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")

        # Form is telling Random to enter his user and password, so he does.
        # And he goes to the working page.
        parser=self.get_parser(self.form_submit(elem,username=user.username,password=user.password))

        parser.has_win_title(cfg.WIN_TITLES["profile"] % { "user": user.username })
        parser.has_title(cfg.TITLES["profile"] % { "user": user.username })
        parser.has_mainbar()
        elem=parser.has_link.get(cfg.URLS["logout"])

        # Random looks for a logout button and click
        parser=self.get_parser(self.click_link(elem))

        parser.has_win_title(cfg.WIN_TITLES["logout"])
        parser.has_title(cfg.TITLES["logout"] )

    def test_random_user_login_profile(self):
        user=self.create_random_user()

        # Random user goes to the awesome writing site
        # and notices a "Log in" form
        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["login"])))

        elem=parser.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")

        # Form is telling Random to enter his user and password, so he does.
        # And he goes to the working page.
        parser=self.get_parser(self.form_submit(elem,username=user.username,password=user.password))

        parser.has_win_title(cfg.WIN_TITLES["profile"] % { "user": user.username })
        parser.has_title(cfg.TITLES["profile"] % { "user": user.username })
        parser.has_mainbar()


    def test_wrong_password(self):
        user=self.create_random_user()

        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["login"])))
        elem=parser.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")

        parser=self.get_parser(self.form_submit(elem,username=user.username,password="wrongpassword"))
        parser.has_win_title(cfg.WIN_TITLES["login"])
        parser.has_title(cfg.TITLES["login"] )
        parser.has_errors_box()

    def test_wrong_user(self):
        user=self.create_random_user()

        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["login"])))
        elem=parser.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")

        parser=self.get_parser(self.form_submit(elem,username="wronguser",password=user.password))
        parser.has_win_title(cfg.WIN_TITLES["login"])
        parser.has_title(cfg.TITLES["login"] )
        parser.has_errors_box()

    def test_no_user(self):
        user=self.create_random_user()

        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["login"])))
        elem=parser.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")

        parser=self.get_parser(self.form_submit(elem,username="wronguser",password="wrongpassword"))
        parser.has_win_title(cfg.WIN_TITLES["login"])
        parser.has_title(cfg.TITLES["login"] )
        parser.has_errors_box()

    def test_anonymous_profile_redirect_to_login(self):
        parser=self.get_parser(self.assert_url_exists(self.full_url(cfg.URLS["profile"])))
        parser.has_win_title(cfg.WIN_TITLES["login"])
        parser.has_title(cfg.TITLES["login"] )
        
        
        
@override_settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),))
class MultiuserLoginTest(base.MultiUserTestCase):

    def test_random_two_users_login_logout(self):
        user_a=self.create_random_user()
        user_b=self.create_random_user()

        ind_a=0
        ind_b=1

        # Random user_a goes to the awesome writing site
        # and notices a "Log in" form.
        parser_a=self.get_parser(self.assert_url_exists(ind_a,self.full_url(ind_a,cfg.URLS["login"])))
        elem_a=parser_a.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")

        # Random user_b goes to the awesome writing site
        # and notices a "Log in" form.
        parser_b=self.get_parser(self.assert_url_exists(ind_b,self.full_url(ind_b,cfg.URLS["login"])))
        elem_b=parser_b.has_form.get(id=cfg.FORMS["login"],action=cfg.URLS["login"],method="post")

        # Form is telling A to enter his user and password, so he does.
        # And he goes to the profile page.
        parser_a=self.get_parser(self.form_submit(ind_a,elem_a,username=user_a.username,password=user_a.password))
        parser_a.has_win_title(cfg.WIN_TITLES["profile"] % { "user": user_a.username })
        parser_a.has_title(cfg.TITLES["profile"] % { "user": user_a.username })
        parser_a.has_mainbar()
        elem_a=parser_a.has_link.get(cfg.URLS["logout"])

        # Form is telling B to enter his user and password, so he does.
        # And he goes to the profile page.
        parser_b=self.get_parser(self.form_submit(ind_b,elem_b,username=user_b.username,password=user_b.password))
        parser_b.has_win_title(cfg.WIN_TITLES["profile"] % { "user": user_b.username })
        parser_b.has_title(cfg.TITLES["profile"] % { "user": user_b.username })
        parser_b.has_mainbar()
        elem_b=parser_b.has_link.get(cfg.URLS["logout"])

        # A looks for a logout button and click
        parser_a=self.get_parser(self.click_link(ind_a,elem_a))
        parser_a.has_win_title(cfg.WIN_TITLES["logout"])
        parser_a.has_title(cfg.TITLES["logout"] )

        # B looks for a logout button and click
        parser_b=self.get_parser(self.click_link(ind_b,elem_b))
        parser_b.has_win_title(cfg.WIN_TITLES["logout"])
        parser_b.has_title(cfg.TITLES["logout"] )


