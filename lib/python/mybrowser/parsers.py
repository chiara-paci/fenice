from html.parser import HTMLParser
from html.entities import name2codepoint
import re

from mybrowser import htmltests
from urllib_tests import configdicts as cfg

ISOLATED_TAGS=["area", "base", "br", "col", "embed", "hr", "img", 
               "input", "keygen", "link", "menuitem",
               "meta", "param", "source", "track", "wbr"]

class AnnexesParser(HTMLParser):
    _tag_list=["link","script"]

    def __init__(self,debug=False,*args,**kwargs):
        self._debug=debug
        HTMLParser.__init__(self,*args,**kwargs)
        self._objects=[]
        self._current=None
        self._debug_indent=""

    def _to_dict(self,attrs):
        if not attrs: return {}
        ret={}
        for k,v in attrs:
            ret[k]=v
        return ret

    def get_urls(self):
        urls=[]
        for tag,attrs in self._objects:
            if tag=="script":
                if "src" in attrs:
                    urls.append(attrs["src"])
                continue
            if tag=="link":
                if "href" in attrs:
                    urls.append(attrs["href"])
                continue
        return urls

    def handle_starttag(self, tag, attrs):
        if tag not in self._tag_list: return
        self._debug_indent+=" "
        if self._debug:
            print(self._debug_indent,"S",len(self._debug_indent),tag,attrs)
        self._objects.append( (tag,self._to_dict(attrs)) )

    def handle_startendtag(self,tag, attrs):
        if tag not in self._tag_list: return
        self._debug_indent+=" "
        if self._debug:
            print(self._debug_indent,"S",len(self._debug_indent),tag,attrs)
        self._objects.append( (tag,self._to_dict(attrs)) )


class Element(object):
    #isolated_tags=ISOLATED_TAGS

    def __init__(self,tag,attrs,isolated=False):
        self.tag=tag.lower()
        self.attrs=attrs
        self.attrs_d={}
        self.dom_id=None
        self.classes=[]
        self.isolated=isolated
        for key,val in self.attrs:
            self.attrs_d[key.lower()]=val
            if key=="class":
                self.classes=list(filter(bool,val.lower().split(" ")))
            if key=="id":
                self.dom_id=val.lower()
        self.objects=[]
        self.parent=None

        w=r'[\w-]+'
        re_tag=r'(?P<tag>('+w+r')?)'
        re_id=r'(?P<id>(\#'+w+r')?)'
        re_class=r'(?P<class>(\.'+w+r')*)'
        re_attr=r'(?P<attr>(\['+w+r'="?.*?"?\])*)'
        re_tot=re_tag+re_id+re_class+re_attr
        self.css_regex=re.compile(re_tot)

        re_tag=r'('+w+r')?'
        re_id=r'(\#'+w+r')?'
        re_class=r'(\.'+w+r')*'
        re_attr=r'(\['+w+r'="?.*?"?\])*'
        re_tot=re_tag+re_id+re_class+re_attr
        re_tot=r'(?P<parent>'+re_tot+r')(?P<child>( +'+re_tot+r')*)'
        self.css_parent_regex=re.compile(re_tot)

    @property
    def text(self):
        S=""
        for obj in self.objects:
            if type(obj)==str:
                S+=obj
                continue
            S+=obj.text
        return S

    def html(self,with_tag=True):
        pre=""
        post=""
        if with_tag:
            pre="<"+self.tag
            attrs=" ".join([str(x)+"='"+str(y)+"'" for x,y in self.attrs_d.items()])
            if attrs: pre+=" "+attrs
            #if self.tag in self.isolated_tags:
            if self.isolated:
                return pre+"/>"
            pre+=">"
            post="</"+self.tag+">"
        html=""
        for obj in self.objects:
            if type(obj)==str: 
                html+=obj
                continue
            html+=obj.html()
        html=html.strip()
        return pre+html+post

    def __str__(self):
        return self.tag

    def __eq__(self,obj):
        if type(obj)!=str:
            #print("E1")
            return object.__eq__(self,obj)
        #print("E2",obj)
        obj=obj.lower()

        m=self.css_regex.fullmatch(obj)
        if not m:
            print("NO REGEXP",obj)
            return False

        D=m.groupdict()

        if D["tag"] and D["tag"]!=self.tag:
            return False

        if D["id"]:
            test_id=D["id"][1:]
            if self.dom_id!=test_id: 
                return False

        if D["class"]:
            test_classes=D["class"][1:].split(".")
            for c in test_classes:
                if c not in self.classes: 
                    return False

        if D["attr"]:
            t=D["attr"].split("]")
            for q in t:
                if not q: continue
                t=q.split("=")
                k=t[0]
                v="=".join(t[1:])
                k=k[1:]
                v=v.replace('"','')
                if k not in self.attrs_d: return False
                if self.attrs_d[k].lower()!=v: return False
        
        return True

    def add_child(self,elem):
        self.objects.append(elem)
        elem.parent=self

    def add_data(self,data):
        if self.objects and type(self.objects[-1])==str:
            self.objects[-1]+=data
            return
        self.objects.append(data)

    def print_summary(self,indent=""):
        print(indent,"+",self.tag,self.attrs)

    def print_tree(self,indent=""):
        print(indent,"+",self.tag,self.attrs)
        indent+="  "
        for elem in self.objects:
            if type(elem)!=str:
                elem.print_tree(indent=indent)
                continue
            elem=elem.replace("\n"," ").strip()
            if not elem: continue
            print(indent,elem)

    def get_children_by_tag(self,tag):
        ret=[]
        #if self.tag==tag: ret.append(self)
        if self==tag: ret.append(self)
        for elem in self.objects:
            if type(elem)==str: continue
            ret+=elem.get_children_by_tag(tag)
        return ret

    def search_all(self,condition):
        if type(condition)==str:
            def f(x):
                return x==condition
            condition_call=f
        else:
            condition_call=condition
        ret=[]
        #if self.tag==tag: ret.append(self)
        if condition_call(self): ret.append(self)
        for elem in self.objects:
            if type(elem)==str: continue
            ret+=elem.search_all(condition)
        return ret

    def search_elem(self,condition):
        if type(condition)!=str:
            condition_call=condition
        else:
            m=self.css_parent_regex.fullmatch(condition)
            #print(m)
            if m:
                gdict=m.groupdict()
                cond_parent=gdict["parent"]
                cond_child=gdict["child"].strip()
                if cond_child:
                    elem=self.search_elem(cond_parent)
                    #print("P:",elem)
                    if not elem: return None
                    #elem.print_tree(indent="   ")
                    return elem.search_elem(cond_child)
                condition=cond_parent
            def f(x):
                return x==condition
            condition_call=f

        if condition_call(self):
            #print("A",self) #,condition_call(elem))
            return self
        for elem in self.objects:
            if type(elem)==str: continue
            #print("B",elem) #,condition_call(elem))
            obj=elem.search_elem(condition_call)
            #print("C",elem) #,condition_call(elem))
            if obj!=None: 
                return obj
        return None

class PageParser(HTMLParser):
    def __init__(self,test,debug=False,*args,**kwargs):
        HTMLParser.__init__(self,*args,**kwargs)
        self._debug=debug
        self._objects=[]
        self._current=None
        self._debug_indent=""

        self.has_head=htmltests.TestElement(test,self,"head")
        self.has_body=htmltests.TestElement(test,self,"body")
        self.has_form=htmltests.TestElement(test,self,"form")
        self.has_input=htmltests.TestElement(test,self,"input")
        self.has_textarea=htmltests.TestElement(test,self,"textarea")
        self.has_section=htmltests.TestElement(test,self,"section")
        self.has_navbar=htmltests.TestElement(test,self,"nav")
        self.has_a=htmltests.TestElement(test,self,"a")
        self.has_meta=htmltests.TestElement(test,self,"meta")
        self.has_section=htmltests.TestElement(test,self,"section")

        self.has_css=htmltests.TestCss(test,self)
        self.has_icon=htmltests.TestIcon(test,self)
        self.has_js=htmltests.TestJs(test,self)

        self.has_select=htmltests.TestSelect(test,self)
        self.has_title=htmltests.TestTitle(test,self)
        self.has_win_title=htmltests.TestWinTitle(test,self)
        self.has_link_text=htmltests.TestLinkText(test,self)
        self.has_link=htmltests.TestLink(test,self)
        self.has_button_link=htmltests.TestButtonLink(test,self)
        self.has_errors_box=htmltests.TestErrorsBox(test,self)

    ### Parsing

    def handle_starttag(self, tag, attrs):
        self._debug_indent+=" "
        if self._debug:
            print(self._debug_indent,"S",len(self._debug_indent),tag,attrs)
        elem=Element(tag,attrs)
        if self._current:
            self._current.add_child(elem)
        self._current=elem

    def handle_startendtag(self,tag, attrs):
        if self._debug:
            print(self._debug_indent,"T",len(self._debug_indent),tag,attrs)
        elem=Element(tag,attrs,isolated=True)
        if self._current:
            self._current.add_child(elem)
        else:
            self._objects.append(elem)

    # def _close_current(self):
    #     if not self._current: return
    #     if not self._current.parent:
    #         self._objects.append(self._current)
    #     elif self._current.tag=="html":
    #         self._objects.append(self._current)
    #     self._current=self._current.parent

    def handle_endtag(self, tag):
        if self._debug:
            print(self._debug_indent,"E",len(self._debug_indent),tag,self._current.tag)
        if tag==self._current.tag:
            self._debug_indent=self._debug_indent[:-1]
            if not self._current.parent:
                self._objects.append(self._current)
                self._current=None
                return
            if tag=="html":
                self._objects.append(self._current)
            self._current=self._current.parent
            return
        current=self._current
        debug_indent=self._debug_indent
        while current.tag!=tag:
            debug_indent=debug_indent[:-1]
            current=current.parent
            if not current: return
        self._current=current
        self._debug_indent=debug_indent
        self.handle_endtag(tag)

    def handle_data(self, data):
        if not self._current: return
        self._current.add_data(data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        if not self._current: return
        self._current.add_data(c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        if not self._current: return
        self._current.add_data(c)

    def handle_comment(self, data): return

    def handle_decl(self, data): return

    ### Parser base functions

    def print_tree(self):
        print(self._objects)
        for elem in self._objects:
            elem.print_tree()

    def get_all_by_tag(self,tag):
        ret=[]
        #if self.tag==tag: ret.append(self)
        if self==tag: ret.append(self)
        for elem in self._objects:
            if type(elem)==str: continue
            ret+=elem.get_children_by_tag(tag)
        return ret

    def search_elem(self,condition_call):
        for elem in self._objects:
            if type(elem)==str: continue
            obj=elem.search_elem(condition_call)
            if obj!=None: return obj
        return None

    def search_elem_by_link_text(self,text):
        def cond(obj):
            return obj.tag=="a" and obj.text.strip()==text.strip()
        return self.search_elem(cond)

    ### Other functions

    def has_page_titles(self,page_label,**kwargs):
        self.has_win_title(cfg.WIN_TITLES[page_label] % kwargs )
        self.has_title(cfg.TITLES[page_label] % kwargs )



