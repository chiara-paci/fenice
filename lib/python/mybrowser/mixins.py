from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings

import testlib.asserts,testlib.mixins

import urllib.parse

from . import parsers,asserts
import random
import string
import re
import json

class UnitTestMixin(testlib.mixins.TestCommonMixin):
    _base_css_list=[ ]
    _base_js_list=[ ]
    _base_icon_file=''

    def get_parser(self,response):
        parser=parsers.PageParser(self)
        parser.feed(response.text)
        return parser

    def find_csrf(self,response):
        csrftoken=""
        if "Set-Cookie" not in response.headers:
            #print(response.headers)
            return ""
        if type(response.headers["Set-Cookie"]) is str:
            if response.headers["Set-Cookie"].startswith("csrftoken"):
                csrftoken=response.headers["Set-Cookie"].strip()
        else:
            for cookie in response.headers["Set-Cookie"]:
                if cookie.startswith("csrftoken"):
                    csrftoken=cookie.strip()
                    break
        if not csrftoken: return ""
        return csrftoken.split(";")[0][10:]

    def _static(self,path):
        return settings.STATIC_URL+path

    ###

    def __init__(self):
        self._assert_html_url_exists   = asserts.AssertUrlStatus(self,"text/html; charset=utf-8",200)
        self._assert_html_404          = asserts.AssertUrlStatus(self,"text/html; charset=utf-8",404)
        self._assert_html_302          = asserts.AssertUrlStatus(self,"text/html; charset=utf-8",302)
        self._assert_html_content_type = asserts.AssertContentType(self,"text/html; charset=utf-8")
        self._assert_html_raw_content  = asserts.AssertRawContent(self,"text/html; charset=utf-8")

        self._assert_json_url_exists   = asserts.AssertUrlStatus(self,"application/json; indent=4",200)
        self._assert_json_404          = asserts.AssertUrlStatus(self,"application/json; indent=4",404)
        self._assert_json_405          = asserts.AssertUrlStatus(self,"application/json; indent=4",405)
        self._assert_json_content_type = asserts.AssertContentType(self,"application/json; indent=4")
        self._assert_json_raw_content  = asserts.AssertRawContent(self,"application/json; indent=4")
        self._assert_json_content      = asserts.AssertJsonContent(self)

        self.assert_url_exists        = self._decor_nav(self._assert_url_exists)
        self.assert_content_type      = self._decor_nav(self._assert_content_type)
        self.assert_raw_content       = self._decor_nav(self._assert_raw_content)
        self.assert_404               = self._decor_nav(self._assert_404)
        self.assert_405               = self._decor_nav(self._assert_405)
        self.assert_302               = self._decor_nav(self._assert_302)
        self.assert_html_url_exists   = self._decor_nav(self._assert_html_url_exists)
        self.assert_html_404          = self._decor_nav(self._assert_html_404)
        self.assert_html_302          = self._decor_nav(self._assert_html_302)
        self.assert_html_content_type = self._decor_nav(self._assert_html_content_type)
        self.assert_html_raw_content  = self._decor_nav(self._assert_html_raw_content)
        self.assert_json_url_exists   = self._decor_nav(self._assert_json_url_exists)
        self.assert_json_404          = self._decor_nav(self._assert_json_404)
        self.assert_json_405          = self._decor_nav(self._assert_json_405)
        self.assert_json_content_type = self._decor_nav(self._assert_json_content_type)
        self.assert_json_raw_content  = self._decor_nav(self._assert_json_raw_content)
        self.assert_json_content      = self._decor_nav(self._assert_json_content)
        self.form_submit              = self._decor_nav(self._form_submit)
        self.form_submit_with_files   = self._decor_nav(self._form_submit_with_files)
        self.click_link               = self._decor_nav(self._click_link)
        self.full_url                 = self._decor_nav(self._full_url)
        self.post_link                = self._decor_nav(self._post_link)
        self.json_post                = self._decor_nav(self._json_post)
        self.html_post                = self._decor_nav(self._html_post)
        self.any_post                 = self._decor_nav(self._any_post)
        self.json_get                 = self._decor_nav(self._json_get)
        self.html_get                 = self._decor_nav(self._html_get)
        self.any_get                  = self._decor_nav(self._any_get)

    #def _decor_nav(self,function): return function

    def _post_link(self,nav,url,decode_text=True,csrf_token=""):
        data={}
        if csrf_token:
            data["csrfmiddlewaretoken"]=csrf_token
        response=nav.post(url,data=data,decode_text=decode_text)
        return response

    def _json_post(self,nav,url,data={},files={},decode_text=True):
        accept="application/json"
        headers=[("Accept",accept)]
        return nav.post(url,data=data,files=files,
                        headers=headers,decode_text=decode_text)

    def _html_post(self,nav,url,data={},files={},decode_text=True):
        accept="text/html"
        headers=[("Accept",accept)]
        return nav.post(url,data=data,files=files,
                        headers=headers,decode_text=decode_text)

    def _any_post(self,nav,url,data={},files={},decode_text=True):
        return nav.post(url,data=data,files=files,
                        decode_text=decode_text)

    def _json_get(self,nav,url,decode_text=True):
        accept="application/json"
        headers=[("Accept",accept)]
        return nav.get(url,headers=headers,decode_text=decode_text)

    def _html_get(self,nav,url,decode_text=True):
        accept="text/html"
        headers=[("Accept",accept)]
        return nav.get(url,headers=headers,decode_text=decode_text)

    def _any_get(self,nav,url,decode_text=True):
        return nav.get(url,decode_text=decode_text)

    def _click_link(self,nav,a_elem): 
        url=a_elem.attrs_d["href"]
        return self._assert_url_exists(nav,self._full_url(nav,url))

    def _full_url(self,nav,url):
        base_url=urllib.parse.urljoin(self.live_server_url,nav.url)
        return urllib.parse.urljoin(base_url,url)

    def _assert_content_type(self,nav,url,content_type,decode_text=True):
        response=nav.get(url,decode_text=decode_text)
        self.assertTrue(response.headers["Content-Type"].startswith(content_type))
        return response

    def _assert_url_exists(self,nav,url,decode_text=True):
        response=nav.get(url,decode_text=decode_text)
        self.assertEqual(response.status,200,
                          msg="url=%s expected=%d result=%d %s" % (url,200,response.status,response.reason) )
        return response

    def _assert_raw_content(self,nav,url,data,decode_text=True):
        response=nav.get(url,decode_text=decode_text)
        self.assertEqual(response.text,data)
        return response

    def _assert_404(self,nav,url):
        response=nav.get(url,decode_text=True)
        self.assertEqual(response.status,404)
        return response

    def _assert_405(self,nav,url):
        response=nav.get(url,decode_text=True)
        self.assertEqual(response.status,405)
        return response

    def _assert_302(self,nav,url):
        response=nav.get(url,decode_text=True)
        self.assertEqual(response.status,302)
        return response
    
    def _assert_has_annexes(self,parser,css_list=[],js_list=[]):
        parser.has_meta(charset="utf-8")
        if self._base_icon_file:
            parser.has_icon(self._static(self._base_icon_file))

        for css in self._base_css_list:
            parser.has_css(self._static(css))
        for css in css_list:
            parser.has_css(self._static(css))

        for js in self._base_js_list:
            parser.has_js(self._static(js))
        for js in js_list:
            parser.has_js(self._static(js))

    def _form_submit(self,nav,form_elem,**kwargs): 
        method="get"
        action=""
        if "method" in form_elem.attrs_d:
            method=form_elem.attrs_d["method"].lower()
        if "action" in form_elem.attrs_d:
            action=form_elem.attrs_d["action"]
        action=self._full_url(nav,action)

        data={}
        files={}
        for elem in form_elem.search_all('input'):
            if "type" in elem.attrs_d:
                input_type=elem.attrs_d["type"]
            else:
                input_type="text"
            if input_type in ["submit","reset"]: continue
            name=elem.attrs_d["name"]
            if name in kwargs:
                value=kwargs[name]
            elif "value" in elem.attrs_d:
                value=elem.attrs_d["value"]
            else:
                value=""
            data[name]=value

        for elem in form_elem.search_all('textarea'):
            name=elem.attrs_d["name"]
            if name in kwargs:
                value=kwargs[name]
            else:
                value=elem.text
            data[name]=value

        for elem in form_elem.search_all('select'):
            name=elem.attrs_d["name"]
            if name in kwargs:
                value=kwargs[name]
            else:
                value=""
                for opt in elem.search_all("option"):
                    if "selected" in opt.attrs_d:
                        value=opt.attrs_d["value"]
            data[name]=value

        if method=="get":
            return nav.get(action,data=data)
        else:
            return nav.post(action,data=data)

    def _form_submit_with_files(self,nav,form_elem,files,**kwargs): 
        method="post"
        action=""
        if "method" in form_elem.attrs_d:
            method=form_elem.attrs_d["method"].lower()
        if "action" in form_elem.attrs_d:
            action=form_elem.attrs_d["action"]
        action=self._full_url(nav,action)

        data={}
        data_files={}
        for elem in form_elem.search_all('input'):
            if "type" in elem.attrs_d and elem.attrs_d["type"] in ["submit","reset"]: continue
            name=elem.attrs_d["name"]
            if "type" in elem.attrs_d and elem.attrs_d["type"]!="file":
                if name in kwargs:
                    value=kwargs[name]
                elif "value" in elem.attrs_d:
                    value=elem.attrs_d["value"]
                else:
                    value=""
                data[name]=value
                continue
            if name not in files: continue
            if type(files[name]) is dict:
                data_files[name]=files[name]
                continue
            fd=open(files[name],"r")
            content=fd.read()
            fd.close()
            filename=os.path.basename(files[name])
            data_files[name]={
                "filename": filename,
                "content": content
            }

        for elem in form_elem.search_all('textarea'):
            name=elem.attrs_d["name"]
            if name in kwargs:
                value=kwargs[name]
            else:
                value=elem.text
            data[name]=value

        for elem in form_elem.search_all('select'):
            name=elem.attrs_d["name"]
            if name in kwargs:
                value=kwargs[name]
            else:
                value=""
                for opt in elem.search_all("option"):
                    if "selected" in opt.attrs_d:
                        value=opt.attrs_d["value"]
            data[name]=value

        return nav.post(action,data=data,files=data_files)

    def assertStatusAndContentType(self,response,expected_status,expected_content_type):
        error_msg="Expected status %d, returned %d" % (expected_status,response.status)
        self.assertEqual(response.status,expected_status,
                         msg=error_msg)
        error_msg="Expected content type %s, returned %s" % (expected_content_type,
                                                             response.headers["Content-Type"])
        self.assertTrue(response.headers["Content-Type"].startswith(expected_content_type),
                              msg=error_msg)

    def assertHTMLEqualWithCsrf(self,html_a,html_b):
        html_a=re.sub(r"name='csrfmiddlewaretoken' value='.*?'",
                      "name='csrfmiddlewaretoken' value=''",html_a)
        html_b=re.sub(r"name='csrfmiddlewaretoken' value='.*?'",
                      "name='csrfmiddlewaretoken' value=''",html_b)
        self.assertHTMLEqual(html_a,html_b)

    def assertLocation(self,response,regexp):
        self.assertIn("Location",response.headers)
        self.assertTrue(regexp.match(response.headers["Location"]))

    def assertStatus(self,response,status):
        error_msg="Expected status %d, returned %d\n%s" % (status,response.status,response.text)
        self.assertEqual(response.status,status,
                         msg=error_msg)
        
    def assertContentType(self,response,content_type):
        error_msg="Expected content type %s, returned %s" % (content_type,
                                                             response.headers["Content-Type"])
        self.assertTrue(response.headers["Content-Type"].startswith(content_type),
                        msg=error_msg)

class HeaderAuthUnitTestMixin(UnitTestMixin):
    pass

class ApiUnitTestMixin(UnitTestMixin):
    _assert_api_post_200 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,200)
    _assert_api_post_201 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,201)
    _assert_api_post_202 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,202)
    _assert_api_post_204 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,204)
    _assert_api_post_401 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,401)
    _assert_api_post_403 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,403)
    _assert_api_post_404 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,404)
    _assert_api_post_409 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,409)
    _assert_api_post_415 = testlib.asserts.AssertionMethod(asserts.AssertApiPost,415)
    _assert_api_get_200  = testlib.asserts.AssertionMethod(asserts.AssertApiGet,200)
    _assert_api_get_204  = testlib.asserts.AssertionMethod(asserts.AssertApiGet,204)
    _assert_api_get_401  = testlib.asserts.AssertionMethod(asserts.AssertApiGet,401)
    _assert_api_get_403  = testlib.asserts.AssertionMethod(asserts.AssertApiGet,403)
    _assert_api_get_404  = testlib.asserts.AssertionMethod(asserts.AssertApiGet,404)

    _assert_api_post_status = testlib.asserts.AssertionMethod(asserts.AssertApiPostStatus)
    _assert_api_get_status = testlib.asserts.AssertionMethod(asserts.AssertApiGetStatus)
