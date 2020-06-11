import json
import abc

class AssertUrlStatus(object):
    def __init__(self,test,accept,status):
        self.test=test
        self.accept=accept
        self.status=status

    def __call__(self,nav,url,decode_text=True):
        response=nav.get(url,headers=[("Accept",self.accept)],decode_text=decode_text)
        self.test.assertEqual(response.status,self.status,
                              msg="Expected status %d, returned %d" % (self.status,response.status))
        return response

class AssertContentType(object):
    def __init__(self,test,accept):
        self.test=test
        self.accept=accept

    def __call__(self,nav,url,content_type,decode_text=True):
        response=nav.get(url,headers=[("Accept",self.accept)],decode_text=decode_text)
        self.test.assertTrue(response.headers["Content-Type"].startswith(content_type))
        return response

class AssertRawContent(object):
    def __init__(self,test,accept):
        self.test=test
        self.accept=accept

    def __call__(self,nav,url,data,decode_text=False):
        response=nav.get(url,headers=[("Accept",self.accept)],decode_text=decode_text)
        self.test.assertEqual(response.text,data)
        return response

class AssertJsonContent(object):
    def __init__(self,test):
        self.test=test
        self.accept="application/json"

    def __call__(self,nav,url,json_verifier,decode_text=True):
        response=nav.get(url,headers=[("Accept",self.accept)],decode_text=decode_text)
        obj=json.loads(response.text)
        json_verifier(obj)
        return response

class AssertApiStatus(abc.ABC):
    def __init__(self,test):
        self.test=test

    @abc.abstractmethod
    def _verb(self,nav,url,**kwargs): return None

    def __call__(self,nav,url,status,json_verifier=None,cookies_verifier=None,**kwargs): #decode_text=True,data={},files={}
        response=self._verb(nav,url,**kwargs)
        self.test.assertTrue(response.headers["Content-Type"].startswith("application/json"))
        error_msg="Expected status %d, returned %d\n%s" % (status,response.status,response.text)
        self.test.assertEqual(response.status,status,msg=error_msg)
        if response.text:
            obj=json.loads(response.text)
        else:
            obj={}
        if json_verifier is not None:
            json_verifier(obj)
        if cookies_verifier is not None:
            cookies_verifier(nav.get_cookies())
        return response

class AssertApiVerb(abc.ABC):
    def __init__(self,test,status):
        self.test=test
        self.status=status

    @abc.abstractmethod
    def _verb(self,nav,url,**kwargs): return None

    def __call__(self,nav,url,json_verifier=None,cookies_verifier=None,**kwargs): #decode_text=True,data={},files={}
        response=self._verb(nav,url,**kwargs)
        self.test.assertTrue(response.headers["Content-Type"].startswith("application/json"))
        error_msg="Expected status %d, returned %d\n%s" % (self.status,response.status,response.text)
        self.test.assertEqual(response.status,self.status,
                              msg=error_msg)
        if response.text:
            obj=json.loads(response.text)
        else:
            obj={}
        if json_verifier is not None:
            json_verifier(obj)
        if cookies_verifier is not None:
            cookies_verifier(nav.get_cookies())
        return response

class AssertApiPost(AssertApiVerb):
    def _verb(self,nav,url,**kwargs): #decode_text=True,data={},files={}
        response=nav.post(url,**kwargs)
        return response
    
class AssertApiGet(AssertApiVerb):
    def _verb(self,nav,url,**kwargs): #decode_text=True
        response=nav.get(url,**kwargs)
        return response

class AssertApiPostStatus(AssertApiStatus):
    def _verb(self,nav,url,**kwargs): #decode_text=True,data={},files={}
        response=nav.post(url,**kwargs)
        return response
    
class AssertApiGetStatus(AssertApiStatus):
    def _verb(self,nav,url,**kwargs): #decode_text=True
        response=nav.get(url,**kwargs)
        return response
    
