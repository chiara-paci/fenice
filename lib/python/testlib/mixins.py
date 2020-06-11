import random
import string
import abc
import math
import rsa
from django.conf import settings

from django.utils.translation import gettext_lazy as _
from django.test import override_settings

import datetime
import pytz
import os.path

class TestCommonMixin(abc.ABC):

    class RandomUser(object):
        def __init__(self,username,email,password=None):
            self.username=username
            self.email=email
            self.password=password

    def random_string(self,size=0,with_spaces=True,max_size=50,min_size=20,
                      only_chars="",add_chars=""):
        if not size:
            size=random.choice(range(min_size,max_size))
        if only_chars:
            chars=only_chars
        else:
            chars=string.ascii_lowercase +string.ascii_uppercase + string.digits
            chars+=add_chars
            if with_spaces:
                chars+="    "
        S=''.join([random.choice(chars) for n in range(size)])
        if with_spaces:
            S=S.strip()
            S=" ".join(S.split())
            if len(S)!=size:
                S+=self.random_string(with_spaces=False,size=size-len(S))
        return S

    def random_cap(self):
        return self.random_string(size=5,only_chars="0123456789")

    def random_boolean(self): return random.choice( [True,False] )

    def random_date(self,max_year=2020,min_year=1900):
        y=random.randint(min_year,max_year)
        m=random.randint(1,12)
        if m in [ 11,4,6,9 ]:
            d=random.randint(1,30)
        elif m==2:
            if y%4!=0:
                d=random.randint(1,28)
            elif y%100!=0:
                d=random.randint(1,29)
            elif y%400==0:
                d=random.randint(1,29)
            else:
                d=random.randint(1,28)
        else:
            d=random.randint(1,31)
        return "%.4d-%.2d-%.2d" % (y,m,d)

    def random_datetime_tuple(self,max_year=2020,min_year=1900):
        y=random.randint(min_year,max_year)
        m=random.randint(1,12)
        if m in [ 11,4,6,9 ]:
            d=random.randint(1,30)
        elif m==2:
            if y%4!=0:
                d=random.randint(1,28)
            elif y%100!=0:
                d=random.randint(1,29)
            elif y%400==0:
                d=random.randint(1,29)
            else:
                d=random.randint(1,28)
        else:
            d=random.randint(1,31)
        
        H=random.randint(0,23)
        M=random.randint(0,59)
        S=random.randint(0,59)

        return (y,m,d,H,M,S)

    def random_datetime_utc(self,max_year=2020,min_year=1900):
        dt_tuple=self.random_datetime_tuple(max_year=max_year,min_year=min_year)
        return pytz.utc.localize(datetime.datetime(*dt_tuple))

    def random_timedelta(self):
        return datetime.timedelta(random.randint(0,2000),random.randint(0,86400))

    def random_node(self,size):
        x=self.random_string(with_spaces=False,size=size,add_chars="-").strip("-")
        if len(x)==size: return x
        x+=self.random_string(with_spaces=False,size=size-len(x))
        x=x.lower()
        return x
            
    # domain must have at least 2 nodes
    # RFC 1034: domain node must be at maximum 63 chars long
    # last node must be 2 chars long
    # domain must be at least 4 chars long: b.cd
    def random_domain(self,max_size=150,min_size=10,size=0):

        if not size:
            min_size=max(4,min_size)
            max_size=max(4,max_size)
            size=random.randint(min_size,max_size)
        else:
            size=max(4,size)

        min_nodes=max(2,math.ceil(size/63))
        max_nodes=max(2,math.floor(size/2))
        num_nodes=random.randint(min_nodes,max_nodes)

        if num_nodes==2:
            dot_index=random.randint(max(1,size-63),min(63,size-3))
            l_left=dot_index
            l_right=size-dot_index-1
            left=self.random_node(l_left)
            right=self.random_node(l_right)
            right=right.replace("0","o")
            right=right.replace("1","i")
            right=right.replace("2","s")
            right=right.replace("3","e")
            right=right.replace("4","a")
            right=right.replace("5","f")
            right=right.replace("6","q")
            right=right.replace("7","t")
            right=right.replace("8","b")
            right=right.replace("9","g")
            return "%s.%s" % (left,right)

        dot_index=random.randint(1,min(63,size-5))
        l_left=dot_index
        l_right=size-dot_index-1
        left=self.random_node(l_left)
        right=self.random_domain(size=l_right)
        return "%s.%s" % (left,right)

    # email must be at least 6 chars: a@b.cd
    def random_email(self,size=0,min_size=10,max_size=200):
        if not size:
            min_size=max(6,min_size)
            max_size=max(6,max_size)
            size=random.randint(min_size,max_size)
        else:
            size=max(6,size)

        at_index=random.randint(1,size-5)
        l_left=at_index
        l_right=size-at_index-1
        left=self.random_node(l_left)
        right=self.random_domain(size=l_right)
        return "%s@%s" % (left,right)

    def random_path(self,max_size=150,min_size=10,size=0,absolute=False,trailing=False):
        if not size:
            min_size=max(1,min_size)
            max_size=max(1,max_size)
            size=random.randint(min_size,max_size)
        else:
            size=max(1,size)
        if size==1: return "/"
        if absolute:
            return "/%s" % self.random_context(size-1,trailing=trailing)
        return "%s" % self.random_context(size-1,trailing=trailing)

    def random_url(self,max_size=150,min_size=10,size=0):
        if not size:
            min_size=max(10,min_size)
            max_size=max(12,max_size)
            size=random.randint(min_size,max_size)
        else:
            size=max(10,size)

        if size==10:
            protocol="ftp"
        elif size==11:
            protocol=random.choice(["ftp","ftps","http"])
        else:
            protocol=random.choice(["ftp","ftps","http","https"])

        path_size=size-3-len(protocol)
        
        if path_size == 4:
            domain=self.random_domain(size=4)
            return "%s://%s" % (protocol,domain)
        if path_size == 5:
            domain=self.random_domain(min_size=4,max_size=5)
            if len(domain)==4: domain+="/"
            return "%s://%s" % (protocol,domain)
            
        at_index=random.randint(4,size-1)
        l_left=at_index
        domain=self.random_domain(size=l_left)
        l_right=size - at_index - 1
        context=self.random_context(l_right)
        return "%s://%s/%s" % (protocol,domain,context)

    def random_context(self,size,trailing=None):
        if size==0: return ""
        if size==1:
            return self.random_node(1)
        if trailing is None:
            trailing=random.choice( [True,False] )
        if size==2:
            if trailing:
                return "%s/" % self.random_node(size-1)
            return self.random_node(size)
        if size==3 and trailing:
            return "%s/" % self.random_node(size-1)
        need_split=random.choice( [True,False] )
        if not need_split:
            if trailing:
                return "%s/" % self.random_node(size-1)
            return self.random_node(size)
        
        if trailing:
            at_index=random.randint(1,size-3)
            l_left=at_index
            l_right=size - at_index - 2
        else:
            at_index=random.randint(1,size-2)
            l_left=at_index
            l_right=size - at_index - 1

        left=self.random_context(l_left,trailing=False)
        right=self.random_context(l_right,trailing=False)

        return "%s/%s" % (left,right)

    def assertLength(self,obj,length):
        msg="Wrong number of elements in object %s: expected %d, actual %d" % (obj,length,len(obj)) 
        self.assertEqual(len(obj),length,msg=msg)

    def assertIsPemKey(self,key):
        self.assertTrue(type(key) is bytes)
        self.assertTrue(key)
        try:
            key=rsa.PrivateKey.load_pkcs1(key)
        except ValueError as e: # pragma: no cover
            self.fail(str(e))

class SerializationMixin(abc.ABC):
    def assertJsonIsTimestamp(self,field):
        self.assertIn("timestamp",field)
        self.assertIn("timezone",field)
        self.assertIn("dst",field["timezone"])
        self.assertIn("utcoffset",field["timezone"])
        self.assertIn("name",field["timezone"])
        self.assertIn("year",field)
        self.assertIn("month",field)
        self.assertIn("day",field)
        self.assertIn("hour",field)
        self.assertIn("minute",field)
        self.assertIn("second",field)
        self.assertIn("microsecond",field)
        self.assertIn("weekday",field)

    def assertJsonIsFile(self,field):
        self.assertIn("filename",field)
        self.assertIn("mimetype",field)
        self.assertIn("url",field)

    def assertJsonIsPage(self,field):
        self.assertIn("number",field)
        self.assertIn("has_next",field)
        self.assertIn("has_previous",field)
        self.assertIn("next_number",field)
        self.assertIn("previous_number",field)
        self.assertIn("start_index",field)
        self.assertIn("end_index",field)
        self.assertIn("next_url",field)
        self.assertIn("previous_url",field)

    def assertJsonIsObjectLink(self,field):
        self.assertIn("id",field)
        self.assertIn("str",field)
        self.assertIn("url",field)

class JsonTestMixin(SerializationMixin):
    def assertJsonPassTest(self,json_text,test_function):
        obj=json.loads(json_text)
        test_function(obj)

    @property
    @abc.abstractmethod
    def errors(self): pass

    def assertJsonErrors(self,actual,expected,**kwargs):
        """ 
        Verify json errors vs. simplified expected errors (with error code but without error message).

        A field error in expected 

            { field: [ err_code1, err_code2, ... ]} 

        match an error in actual
 
            { field: [ { "code": err_code1, "message": err_msg1 }, 
                       { "code": err_code2, "message": err_msg2 }, ... ] }

        with err_msg# = self.errors[err_code#].

        Non field related errors go in kwargs as { "key": "message" } dictionary.

        """
        for field in expected:
            with self.subTest(field=field):
                self.assertIn(field,actual)
                for error in actual[field]:
                    self.assertIn("message",error)
                    self.assertIn("code",error)
                by_codes={ msg["code"]: msg for msg in actual[field] }
                for code in expected[field]:
                    self.assertIn(code,by_codes)
                    self.assertEqual(by_codes[code]["code"],code)
                    self.assertErrorMessage(code,by_codes[code]["message"])
                for code in by_codes:
                    self.assertIn(code,expected[field])
        for key in kwargs:
            with self.subTest(key=key):
                self.assertIn(key,actual)
                self.assertEqual(actual[key],kwargs[key])

    def assertErrorMessage(self,code,message):
        if type(self.errors[code]) is not list:
            self.assertEqual(message,self.errors[code])
        else:
            self.assertIn(message,self.errors[code])


class ViewTestMixin(abc.ABC):
    def assertStatus(self,response,status):
        self.assertEqual(response.status_code,status,
                         msg="Response status expected %d, actual %d:\n%s" % (status,
                                                                              response.status_code,
                                                                              response.content))
        
    def assertContentType(self,response,content_type):
        res_content_type=response["Content-Type"].split(';')[0]
        self.assertEqual(res_content_type,content_type,
                         msg="Response content type expected %s, actual %s" % (content_type,
                                                                               res_content_type))

    def assertUsesViewClass(self,response,view_class):
        exp_name=view_class.as_view().__name__
        res_name=response.resolver_match.func.__name__
        self.assertEqual(res_name,exp_name, 
                         msg="Expected view %s, used %s" % (exp_name,res_name) )


    def _test_post_ok(self,url,test_cases):
        #print(settings.AUTH_PASSWORD_VALIDATORS)
        for key in test_cases:
            with self.subTest(test_case=key):
                data=test_cases[key].data()
                response = self.client.post(url,
                                            data=data,
                                            HTTP_ACCEPT="application/json")
                fname=datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
                fname+="_%s.txt" % key
                fname=fname.replace(" ","_")
                with open(os.path.join(settings.TEST_SPOOL_DIR,fname),'w') as fd:
                    fd.write("testlib/mixins.py [ok]\n")
                    fd.write("%s\n" % key)
                    fd.write("status=%d\n" % response.status_code)
                    fd.write("response=%s\n" % str(response.content))
                    fd.write("data=%s\n" % str(data))
                test_cases[key].check(response)

    def _test_post_errors(self,url,test_cases):
        with self.settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),)):
            with self.subTest(debug=False):
                with self.settings(DEBUG=False):
                    for key in test_cases:
                        with self.subTest(test_case=key):
                            data=test_cases[key].data()
                            response = self.client.post(url,
                                                        data=data,
                                                        HTTP_ACCEPT="application/json")
                            fname=datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
                            fname+="_%s.txt" % key
                            fname=fname.replace(" ","_")
                            with open(os.path.join(settings.TEST_SPOOL_DIR,fname),'w') as fd:
                                fd.write("testlib/mixins.py [err]\n")
                                fd.write("%s\n" % key)
                                fd.write("status=%d\n" % response.status_code)
                                fd.write("response=%s\n" % str(response.content))
                                fd.write("data=%s\n" % str(data))
                            test_cases[key].check(response)
            with self.subTest(debug=True):
                with self.settings(DEBUG=True):
                    for key in test_cases:
                        with self.subTest(test_case=key):
                            data=test_cases[key].data()
                            response = self.client.post(url,
                                                        data=data,
                                                        HTTP_ACCEPT="application/json")
                            fname=datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
                            fname+="_debug_%s.txt" % key
                            fname=fname.replace(" ","_")
                            with open(os.path.join(settings.TEST_SPOOL_DIR,fname),'w') as fd:
                                fd.write("testlib/mixins.py [err]\n")
                                fd.write("%s\n" % key)
                                fd.write("status=%d\n" % response.status_code)
                                fd.write("response=%s\n" % str(response.content))
                                fd.write("data=%s\n" % str(data))
                            test_cases[key].check(response)

class FormTestMixin(JsonTestMixin,abc.ABC):
    required_fields=[]
    non_required_fields=[]

    @property
    @abc.abstractmethod
    def form_class(self): pass

    def _error_case_set(self): return []

    def test_form_has_fields(self):
        form=self.form_class()
        for label in self.required_fields:
            with self.subTest(field=label):
                self.assertIn(label,form.fields)
                self.assertTrue(form.fields[label].required,
                                "%s must be required" % label)
        for label in self.non_required_fields:
            with self.subTest(field=label):
                self.assertIn(label,form.fields)
                self.assertFalse(form.fields[label].required,
                                 "%s must be non required" % label)

    @override_settings(LANGUAGE_CODE='en-US',LANGUAGES=(('en', 'English'),))
    def test_form_errors(self):
        for label,data,errors in self._error_case_set():
            with self.subTest(error_case=label):
                form = self.form_class(data=data)
                self.assertFormErrors(form,errors)

    def assertFormErrors(self,form,errors_obj):
        self.assertFalse(form.is_valid())
        data=form.errors.get_json_data()
        self.assertJsonErrors(data,errors_obj)
