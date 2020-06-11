import urllib.request,urllib.error,urllib.parse
import collections
import http.cookiejar
import os.path
import string
import json
import random
import mimetypes
import rsa
import base64
import time

#from . import parsers as wdparsers

def clean_url(url):
    encoding="utf-8"
    url = urllib.parse.quote(url, encoding=encoding, safe=string.punctuation)
    return url

class ErrorPageException(Exception):
    def __init__(self,response):
        self.response=response

    def __str__(self):
        return "Page Error on url %s" % self.response.url

class ResponseHeaders(collections.OrderedDict): pass

class Response(object):
    def __init__(self,fresponse,request=None,decode_text=True):
        self.request=request
        self.status=fresponse.status
        self.reason=fresponse.reason
        self.url=fresponse.geturl()
        self.set_headers(fresponse.getheaders())
        if decode_text:
            self.text=fresponse.read().decode('utf-8')
        else:
            self.text=fresponse.read()

    def __str__(self):
        return "%s %s %s" % (self.status,self.reason,self.url)

    def set_headers(self,headers):
        self.headers=ResponseHeaders()
        for key,val in headers:
            if key not in self.headers.keys():
                self.headers[key]=val
                continue
            if type(self.headers[key])==list:
                self.headers[key].append(val)
                continue
            self.headers[key]=[ self.headers[key],val ]

class CookieRedirectHandler(urllib.request.HTTPRedirectHandler):

    def __init__(self,navigator,*args,**kwargs):
        self._navigator=navigator
        urllib.request.HTTPRedirectHandler.__init__(self,*args,**kwargs)

    def _clean_new_url(self,request,newurl):
        u=[ ord(i) for i in newurl ]
        newurl=bytes(u).decode("utf-8")

        urlparts = urllib.parse.urlparse(newurl)

        # For security reasons we don't allow redirection to anything other
        # than http, https or ftp.

        if urlparts.scheme not in ('http', 'https', 'ftp', ''):
            raise HTTPError(
                newurl, code,
                "%s - Redirection to url '%s' is not allowed" % (msg, newurl),
                headers, fp)

        if not urlparts.path and urlparts.netloc:
            urlparts = list(urlparts)
            urlparts[2] = "/"
        newurl = urllib.parse.urlunparse(urlparts)
 
        # http.client.parse_headers() decodes as ISO-8859-1. Recover the
        # original bytes and percent-encode non-ASCII bytes, and any special
        # characters such as the space.
        newurl = clean_url(newurl)
        newurl = urllib.parse.urljoin(request.full_url, newurl)
        return newurl

    def redirect_request(self,req, fp, code, msg, hdrs, newurl):
        self._navigator.update_cookies(fp,req)
        newurl=self._clean_new_url(req,newurl)
        req=urllib.request.HTTPRedirectHandler.redirect_request(self,req, fp, code, msg, hdrs, newurl)
        self._navigator.add_cookies_to_request(req)
        return req

class CookiePolicy(http.cookiejar.DefaultCookiePolicy):
    def return_ok(self,cookie,request):
        ret=http.cookiejar.DefaultCookiePolicy.return_ok(self,cookie,request)
        if ret: return True
        if not cookie.secure: return False
        if not cookie.domain.startswith("localhost"): return False
        if not self.domain_return_ok(cookie.domain,request): return False
        if not self.path_return_ok(cookie.path,request): return False
        return True

class Navigator(object):
    encoding="utf-8"
    timeout=600

    def __init__(self,cookiefile,handlers=[]):
        self.url=""
        handlers=handlers[:]
        self._cookiejar=None
        if cookiefile:
            if not os.path.isfile(cookiefile):
                dname=os.path.dirname(cookiefile)
                os.makedirs(dname, exist_ok=True)
                fd=open(cookiefile,'w')
                fd.write('#LWP-Cookies-2.0\n')
                fd.close()
            policy = CookiePolicy()
            self._cookiejar=http.cookiejar.LWPCookieJar(cookiefile,policy=policy)
            self._cookiejar.load(ignore_discard=True,ignore_expires=True)
            handlers.insert(0,CookieRedirectHandler(self))
        self._opener=urllib.request.build_opener(*handlers)

        #self.print_cookies()

    def get_cookie(self,name):
        for cookie in self._cookiejar:
            if cookie.name==name: return cookie
        return None

    def get_cookies(self):
        return { cookie.name: cookie for cookie in self._cookiejar }

    def print_cookies(self):
        print("Cookies:")
        for cookie in self._cookiejar:
            print(cookie.name,cookie.value,cookie.domain,cookie.port,cookie.path)

    def add_cookie(self,name,value,version=0,port=None,
                   domain=None, path=None, secure=False, expires=None, is_session=False, 
                   comment=None, comment_url=None, rest={}):
        if self._cookiejar is None: return
        port_specified=False
        domain_specified=False
        path_specified=False
        domain_initial_dot=False 
        
        if port!=None: port_specified=True
        if domain!=None: 
            domain_specified=True
            if domain.startswith("."): domain_initial_dot=True 
        if path!=None: path_specified=True

        self._cookiejar.set_cookie(http.cookiejar.Cookie(version, name, value, port, port_specified, 
                                                         domain,domain_specified, domain_initial_dot, 
                                                         path, path_specified,
                                                         secure, expires, is_session, 
                                                         comment, comment_url,rest))
        self._cookiejar.save(ignore_discard=True,ignore_expires=True)

    def add_cookies_to_request(self,request):
        if self._cookiejar is None: return
        self._cookiejar.add_cookie_header(request)

    def update_cookies(self,response,request):
        if self._cookiejar is None: return
        self._cookiejar.extract_cookies(response,request)
        self._cookiejar.save(ignore_discard=True,ignore_expires=True)
        #self.print_cookies()

    def clear_cookies(self):
        self._cookiejar.clear()

    # fields={ name: value, name: value }
    # files={
    #     name: {
    #         "filename": filename,
    #         "mimetype": mimetype, (optional)
    #         "content":  content,
    #     },
    #     ...
    # }
    def _encode_data(self, fields, files):
        def escape_quote(s):
            return s.replace('"', '\\"')

        headers={}

        if not files:
            body=urllib.parse.urlencode(fields)
            body=body.encode()
            return body,headers.items()

        boundary = ''.join(random.choice(string.digits + string.ascii_letters) for i in range(30))
        headers['Content-Type']= 'multipart/form-data; boundary='+boundary

        lines = []
        boundary="--"+boundary
        hdr_field_fmt='Content-Disposition: form-data; name="%s"'
        for name, value in fields.items():
            lines+=[
                boundary,
                hdr_field_fmt % escape_quote(name),
                '',
                str(value),
            ]

        hdr_file_fmt='Content-Disposition: form-data; name="%s"; filename="%s"'
        mime_file_fmt='Content-Type: %s'
        for name, value in files.items():
            filename = value['filename']
            if 'mimetype' in value:
                mimetype = value['mimetype']
            else:
                mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            lines+=[
                boundary,
                hdr_file_fmt % (escape_quote(name), escape_quote(filename)),
                mime_file_fmt % mimetype,
                '',
                value['content'],
            ]

        lines.append(boundary+"--")
        lines.append("")

        body='\r\n'.join(lines)
        body=body.encode()

        return (body, headers.items())


    def _open(self,url,method='GET',data={},files={},headers=[],decode_text=True):
        url = clean_url(url)

        data_headers=[]
        if data or files:
            data,data_headers=self._encode_data(data,files)
            #data = urllib.parse.urlencode(data)
            #data = data.encode('ascii')
            # print(data)
            request=urllib.request.Request(url=url,data=data,method=method)
        else:
            request=urllib.request.Request(url=url,method=method)

        self.add_cookies_to_request(request)

        request.add_header("User-agent", "Django UrlLib Tester 0.1")
        for k,v in data_headers:
            request.add_header(k,v)
        for k,v in headers:
            request.add_header(k,v)

        try:
            f=self._opener.open(request,timeout=self.timeout)
            response=Response(f,request,decode_text=decode_text)
            self.update_cookies(f,request)
            f.close()
        except urllib.error.HTTPError as e:
            response=Response(e,request)

        self.url=response.url
        return response

    def get(self,url,data={},headers=[],decode_text=True):
        return self._open(url,data=data,method="GET",headers=headers,decode_text=decode_text)

    def post(self,url,data={},files={},headers=[],decode_text=True):
        return self._open(url,data=data,files=files,method='POST',headers=headers,decode_text=decode_text)

class JwtRedirectHandler(urllib.request.HTTPRedirectHandler):

    def __init__(self,navigator,*args,**kwargs):
        self._navigator=navigator
        urllib.request.HTTPRedirectHandler.__init__(self,*args,**kwargs)

    def _clean_new_url(self,request,newurl):
        u=[ ord(i) for i in newurl ]
        newurl=bytes(u).decode("utf-8")

        urlparts = urllib.parse.urlparse(newurl)

        # For security reasons we don't allow redirection to anything other
        # than http, https or ftp.

        if urlparts.scheme not in ('http', 'https', 'ftp', ''):
            raise HTTPError(
                newurl, code,
                "%s - Redirection to url '%s' is not allowed" % (msg, newurl),
                headers, fp)

        if not urlparts.path and urlparts.netloc:
            urlparts = list(urlparts)
            urlparts[2] = "/"
        newurl = urllib.parse.urlunparse(urlparts)
 
        # http.client.parse_headers() decodes as ISO-8859-1. Recover the
        # original bytes and percent-encode non-ASCII bytes, and any special
        # characters such as the space.
        newurl = clean_url(newurl)
        newurl = urllib.parse.urljoin(request.full_url, newurl)
        return newurl

    def redirect_request(self,req, fp, code, msg, hdrs, newurl):
        newurl=self._clean_new_url(req,newurl)
        req=self._navigator.reset_jwt(req)
        req=urllib.request.HTTPRedirectHandler.redirect_request(self,req, fp, code, msg, hdrs, newurl)
        return req

class JwtNavigator(Navigator):
    def __init__(self):
        Navigator.__init__(self,None)
        handlers=[]
        handlers.append(JwtRedirectHandler(self))
        self._opener=urllib.request.build_opener(*handlers)
        self._private_key=None
        self._username=None

    def set_auth_data(self,username,keydata):
        self._username=username
        if keydata:
            self._private_key=rsa.PrivateKey.load_pkcs1(keydata)
        else:
            self._private_key=None

    def reset_jwt(self,req):
        if req.has_header("Authorization"):
            req.remove_header("Authorization")
        jwt=self._add_jwt()
        if jwt:
            key,val=jwt[0]
            req.add_header(key,val)
        return req

    def _add_jwt(self):
        if not self._username or not self._private_key: return []
        header = '{"alg":"HS512","typ":"JWT"}'
        payload = '{"iss":"'+self._username+'","iat":'+str(time.time())+'}'
        token = base64.urlsafe_b64encode(header.encode('utf-8'))
        token+= b'.' + base64.urlsafe_b64encode(payload.encode('utf-8'))
        signature = rsa.sign(token,self._private_key,"SHA-512")
        token += b'.' + base64.urlsafe_b64encode(signature)
        return [ ("Authorization", b"Bearer "+token) ]

    def _open(self,*args,headers=[],**kwargs):
        headers=headers[:]
        headers+=self._add_jwt()
        return Navigator._open(self,*args,headers=headers,**kwargs)

class JwtJsonNavigator(JwtNavigator):
    def _open(self,*args,headers=[],**kwargs):
        headers=headers[:]
        headers+=[("Accept","application/json")]
        return JwtNavigator._open(self,*args,headers=headers,**kwargs)

class CDMNavigator(Navigator):
    def _open(self,*args,set_csrftoken=True,headers=[],**kwargs):
        if not set_csrftoken:
            return Navigator._open(self,*args,headers=headers,**kwargs)
        headers=headers[:]
        csrftoken=self.get_cookie("csrftoken")
        if csrftoken is not None:
            headers.append( ("X-CSRFToken", csrftoken.value) )
        return Navigator._open(self,*args,headers=headers,**kwargs)

    def get(self,url,data={},headers=[],decode_text=True,set_csrftoken=True):
        return self._open(url,data=data,method="GET",headers=headers,
                          decode_text=decode_text,set_csrftoken=set_csrftoken)

    def post(self,url,data={},files={},headers=[],decode_text=True,set_csrftoken=True):
        return self._open(url,data=data,files=files,method='POST',headers=headers,
                          decode_text=decode_text,set_csrftoken=set_csrftoken)

class JsonNavigator(CDMNavigator):
    def __init__(self,cookiefile):
        CDMNavigator.__init__(self,cookiefile)

    def _open(self,*args,headers=[],**kwargs):
        headers=headers[:]
        headers+=[("Accept","application/json")]
        response=CDMNavigator._open(self,*args,headers=headers,**kwargs)
        return response

class JwtJsonTokenNavigator(CDMNavigator):
    def __init__(self,cookiefile,token=None):
        CDMNavigator.__init__(self,cookiefile,handlers=[JwtRedirectHandler(self)])
        self.token=token 

    def reset_jwt(self,req):
        return req

    def _open(self,*args,headers=[],**kwargs):
        headers=headers[:]
        headers+=[
            ("Accept","application/json"),
        ]
        if self.token is not None:
            headers+=[
                ("Authorization", b"Bearer "+self.token),
            ]
        return CDMNavigator._open(self,*args,headers=headers,**kwargs)
