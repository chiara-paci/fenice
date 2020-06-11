class TestElement(object):
    def __init__(self,test,parser,tag): 
        self._test=test
        self._parser=parser
        self._tag=tag

    def _selector(self,*args,**kwargs):
        ret={}
        if not args and not kwargs: return ret
        if "class" in kwargs and type(kwargs["class"]) == str:
            kwargs["class"]=kwargs["class"].split()
        if not args: return kwargs
        ret=kwargs
        ## add args parsing
        return ret

    def _attr_to_css_sel(self,attrs):
        css_sel=""
        if "parent" in attrs:
            css_sel+=attrs["parent"]+" "
        css_sel+=self._tag
        if "id" in attrs:
            css_sel+="#"+attrs["id"]
        if "class" in attrs:
            css_sel+="."+".".join(attrs["class"])
        a=list(filter(lambda x: x[0] not in ["id","class","parent"],attrs.items()))
        if a:
            a=[ '[%s="%s"]' % (k,v) for (k,v) in a ]
            css_sel+="".join(a)
        return css_sel

    def css_sel(self,*args,**kwargs):
        selector=self._selector(*args,**kwargs)
        css_sel=self._attr_to_css_sel(selector)
        return css_sel

    def get(self,*args,**kwargs):
        selector=self._selector(*args,**kwargs)
        if "link" in selector:
            return self._parser.search_elem_by_link_text(selector["link"])
        if not selector:
            return self._parser.search_elem(self._tag)
        css_sel=self._attr_to_css_sel(selector)
        return self._parser.search_elem(css_sel)

    def has_text(self,text,*args,**kwargs):
        body=self.get(*args,**kwargs)
        return body.text.strip()==text.strip()

    def assert_has_text(self,text,*args,**kwargs):
        ret=self.has_text(text,*args,**kwargs)
        msg="text is not %s" % str(text)
        self._test.assertTrue(ret,msg=msg)

    def has(self,*args,**kwargs): 
        body=self.get(*args,**kwargs)
        return bool(body)

    def no(self,*args,**kwargs):
        return not self.has(*args,**kwargs)

    def _msg(self,*args,**kwargs): 
        selector=self._selector(*args,**kwargs)
        if not selector:
            return "Page has no element %s" % self._tag
        css_sel=self._attr_to_css_sel(selector)
        return "Page has no element %s" % (css_sel)

    def __call__(self,*args,timeout=-1,**kwargs):
        self._test.assertTrue(self.has(*args,**kwargs),
                              msg=self._msg(*args,**kwargs))

class TestSelect(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"select")
    
    def is_selected(self,value,*args,**kwargs):
        body=self.get(*args,**kwargs)
        for opt in body.search_all("option"):
            if "selected" in opt.attrs_d:
                return value==opt.attrs_d["value"]
        return False

    def assert_is_selected(self,value,*args,**kwargs):
        ret=self.is_selected(value,*args,**kwargs)
        msg="%s is not selected"
        self._test.assertTrue(ret,msg=msg)

    def has_options(self,option_list,*args,**kwargs):
        body=self.get(*args,**kwargs)
        opt_found=[]
        for opt in body.search_all("option"):
            opt_t=opt.attrs_d["value"]
            if opt_t not in option_list: 
                if not opt_t: continue
                return False
            opt_found.append(opt_t)
        return len(opt_found)==len(option_list)

    def assert_has_options(self,option_list,*args,**kwargs):
        ret=self.has_options(option_list,*args,**kwargs)
        msg="option list is not %s" % str(option_list)
        self._test.assertTrue(ret,msg=msg)
        
            
class TestWinTitle(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"title")

    def has(self,win_title,*args,**kwargs): 
        wt=self._parser.search_elem("head").search_elem("title").text.strip()
        return win_title==wt

    def _msg(self,win_title,*args,**kwargs): 
        wt=self._parser.search_elem("head").search_elem("title").text.strip()
        return "Browser window has title \"%s\", expected \"%s\"" % (wt,win_title)

# class TestTitle(TestElement):
#     def __init__(self,test,parser):
#         TestElement.__init__(self,test,parser,"h1")

#     def has(self,title,*args,**kwargs): 
#         kwargs["parent"]="header"
#         h1=self.get(*args,**kwargs)
#         if not h1: return False
#         return title==h1.text

#     def _msg(self,title,*args,**kwargs): 
#         kwargs["parent"]="header"
#         h1=self.get(*args,**kwargs)
#         return "Page has title \"%s\", expected \"%s\"" % (h1.text,title)

#     def get(self,*args,**kwargs):
#         kwargs["parent"]="header"
#         return TestElement.get(self,*args,**kwargs)

class TestTitle(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"h1")

    def has(self,title,*args,**kwargs): 
        if "parent" not in kwargs:
            kwargs["parent"]="header"
        h1=self.get(*args,**kwargs)
        if not h1: return False
        return title==h1.text

    def _msg(self,title,*args,**kwargs): 
        if "parent" not in kwargs:
            kwargs["parent"]="header"
        h1=self.get(*args,**kwargs)
        return "Page has title \"%s\", expected \"%s\"" % (h1.text,title)

    def get(self,*args,**kwargs):
        if "parent" not in kwargs:
            kwargs["parent"]="header"
        return TestElement.get(self,*args,**kwargs)

class TestLink(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"a")

    def has(self,link,*args,**kwargs): 
        kwargs["href"]=link
        return TestElement.has(self,*args,**kwargs)

    def _msg(self,link,*args,**kwargs): 
        kwargs["href"]=link
        return TestElement._msg(self,*args,**kwargs)

    def get(self,*args,**kwargs):
        if args:
            kwargs["href"]=args[0]
        return TestElement.get(self,*args,**kwargs)


class TestButtonLink(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"button")

    def has(self,link,*args,**kwargs): 
        kwargs["formaction"]=link
        return TestElement.has(self,*args,**kwargs)

    def _msg(self,link,*args,**kwargs): 
        kwargs["formaction"]=link
        return TestElement._msg(self,*args,**kwargs)

    def get(self,*args,**kwargs):
        if args:
            kwargs["formaction"]=args[0]
        return TestElement.get(self,*args,**kwargs)

class TestErrorsBox(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"section")

    def has(self,*args,**kwargs): 
        if "class" not in kwargs: kwargs["class"]=[]
        kwargs["class"].append("errors")
        return TestElement.has(self,*args,**kwargs)

    def _msg(self,*args,**kwargs): 
        if "class" not in kwargs: kwargs["class"]=[]
        kwargs["class"].append("errors")
        return TestElement._msg(self,*args,**kwargs)

class TestLinkText(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"a")

    def href(self,link,*args,**kwargs):
        kwargs["link"]=link
        elem=self.get(*args,**kwargs)
        if not elem: return None
        return elem.attrs_d["href"]

    def get(self,*args,**kwargs):
        if args:
            kwargs["link"]=args[0]
        return TestElement.get(self,*args,**kwargs)

    def has(self,link,*args,**kwargs): 
        kwargs["link"]=link
        return TestElement.has(self,*args,**kwargs)

    def _msg(self,link,*args,**kwargs): 
        return 'Page has no element "%s" with link text "%s"' % (self._tag,link)

class TestCss(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"link")

    def has(self,css,*args,**kwargs): 
        kwargs["rel"]="stylesheet"
        kwargs["type"]="text/css"
        kwargs["href"]=css
        return TestElement.has(self,*args,**kwargs)

    def _msg(self,css,*args,**kwargs): 
        kwargs["rel"]="stylesheet"
        kwargs["type"]="text/css"
        kwargs["href"]=css
        return TestElement._msg(self,*args,**kwargs)

    def get(self,*args,**kwargs):
        if args:
            kwargs["href"]=args[0]
        kwargs["rel"]="stylesheet"
        kwargs["type"]="text/css"
        return TestElement.get(self,*args,**kwargs)

class TestIcon(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"link")

    def has(self,img,*args,**kwargs): 
        kwargs["rel"]="icon"
        kwargs["type"]="image/png"
        kwargs["href"]=img
        return TestElement.has(self,*args,**kwargs)

    def _msg(self,img,*args,**kwargs): 
        kwargs["rel"]="icon"
        kwargs["type"]="image/png"
        kwargs["href"]=img
        return TestElement._msg(self,*args,**kwargs)

    def get(self,*args,**kwargs):
        if args:
            kwargs["href"]=args[0]
        kwargs["rel"]="icon"
        kwargs["type"]="image/png"
        return TestElement.get(self,*args,**kwargs)

class TestJs(TestElement):
    def __init__(self,test,parser):
        TestElement.__init__(self,test,parser,"script")

    def has(self,js,*args,**kwargs): 
        kwargs["src"]=js
        return TestElement.has(self,*args,**kwargs)

    def _msg(self,js,*args,**kwargs): 
        kwargs["src"]=js
        return TestElement._msg(self,*args,**kwargs)

    def get(self,*args,**kwargs):
        if args:
            kwargs["src"]=args[0]
        return TestElement.get(self,*args,**kwargs)

