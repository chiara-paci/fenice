import random

from unittest import skip

from urllib_tests import base
from urllib_tests import configdicts as cfg

from django.test import override_settings

class ObjectParser(base.CPageParser):
    def get_object(self,title_on_list,href,**data):
        return self.object_class(title_on_list,href,**data)

    def has_projectbar(self,project_id):
        self.has_navbar(id=cfg.NAVBARS["project"])
        self.has_link(cfg.URLS["project_detail"] % {"id": project_id})
        self.has_link(cfg.URLS["outline_list"] % {"project_id": project_id})
        self.has_link(cfg.URLS["content_list"] % {"project_id": project_id})

    def has_worldbar(self,world_id):
        self.has_navbar(id=cfg.NAVBARS["world"])
        # self.has_link(cfg.URLS["world_detail"] % {"id": world_id})
        # self.has_link(cfg.URLS["outline_list"] % {"world_id": world_id})
        # self.has_link(cfg.URLS["content_list"] % {"world_id": world_id})

    def has_outlinebar(self,project_id,outline_id):
        # self.has_navbar(id=cfg.NAVBARS["project"])
        # self.has_link(cfg.URLS["project_detail"] % {"id": project_id})
        # self.has_link(cfg.URLS["outline_detail"] % {"id": outline_id})
        # self.has_link(cfg.URLS["outline_list"] % {"project_id": project_id})
        # self.has_link(cfg.URLS["content_list"] % {"project_id": project_id})
        
        # self.has_navbar(id=cfg.NAVBARS["outline"])
        self.has_link(cfg.URLS["section_list"] % {"outline_id": outline_id})

    def has_object_list(self):
        self.has_section(id=cfg.SECTIONS[self.list_label])
        css_parent=self.has_section.css_sel(id=cfg.SECTIONS[self.list_label])
        parent=self.has_section.get(id=cfg.SECTIONS[self.list_label])
        self.has_title(self.object_list_title,parent=css_parent)

    def has_object_in_list(self,title_on_list,**data):
        #obj=self.has_section.get(**{"class":"object-list"})
        self.has_link_text(title_on_list)
        href=self.has_link_text.href(title_on_list)
        obj=self.get_object(title_on_list,href,**data)
        self.has_link(cfg.URLS[self.delete_label] % {"id": obj.id})
        return obj

    def has_no_object_in_list(self,obj):
        self.has_link_text.no(obj.title_on_list())
        self.has_link.no(cfg.URLS[self.delete_label] % {"id": obj.id})
        return obj

    def _proto_has_form(self,form_id,action,form_fields,button,next=False):
        self.has_form(id=form_id,action=action,method="post")
        css_parent=self.has_form.css_sel(id=form_id,
                                         action=action,method="post")

        for field_type,field_args in form_fields:
            if field_type=="input":
                self.has_input(parent=css_parent,**field_args)
            if field_type=="textarea":
                self.has_textarea(parent=css_parent,**field_args)
            if field_type=="select":
                self.has_select(parent=css_parent,**field_args)

        self.has_input(type="submit",value=button,parent=css_parent)
        if next:
            self.has_input(name="next",type="hidden",parent=css_parent)

    def action_create_form(self,params):
        return cfg.URLS[self.create_label] % params

    def has_create_form(self,next=False,action_params={}):
        self.has_form(id=cfg.FORMS[self.create_label],action=self.action_create_form(action_params),method="post")
        css_parent=self.has_form.css_sel(id=cfg.FORMS[self.create_label],
                                         action=self.action_create_form(action_params),method="post")

        for field_type,field_args in self.create_form_fields:
            if field_type=="input":
                self.has_input(parent=css_parent,**field_args)
            if field_type=="textarea":
                self.has_textarea(parent=css_parent,**field_args)
            if field_type=="select":
                self.has_select(parent=css_parent,**field_args)

        self.has_input(type="submit",value=cfg.BUTTONS[self.create_label])
        if next:
            self.has_input(name="next",type="hidden",parent=css_parent)

    def has_delete_form(self,obj):
        self.has_form(id=cfg.FORMS[self.delete_label] % {"id": obj.id},method="post",
                      action=cfg.URLS[self.delete_label] % {"id": obj.id})
        css_parent=self.has_form.css_sel(id=cfg.FORMS[self.delete_label] % {"id": obj.id},
                                         method="post",
                                         action=cfg.URLS[self.delete_label] % {"id": obj.id})
        
        self.has_input(type="submit",value=self.delete_form_submit_value(obj),
                       id=cfg.FORMS[self.delete_label] % {"id": obj.id}+"_submit")

    def has_update_form(self,obj):
        self.has_form(id=cfg.FORMS[self.update_label] % {"id": obj.id},method="post",
                      action=cfg.URLS[self.update_label] % {"id": obj.id})
        css_parent=self.has_form.css_sel(id=cfg.FORMS[self.update_label] % {"id": obj.id},method="post",
                                         action=cfg.URLS[self.update_label] % {"id": obj.id})

        for field_type,field_args in self.create_form_fields:
            value=self.update_form_field_value(obj,**field_args)
            if field_type=="input":
                self.has_input(parent=css_parent,
                               value=value,
                               **field_args)
            if field_type=="textarea":
                self.has_textarea(parent=css_parent,
                                  **field_args)
                self.has_textarea.has_text(value,parent=css_parent,
                                           **field_args)
            if field_type=="select":
                self.has_select(parent=css_parent,
                                  **field_args)
                self.has_select.is_selected(value,parent=css_parent,
                                            **field_args)
                
                

        #self.has_input(name="name",type="text",value=obj.name)
        self.has_input(type="submit",value=cfg.BUTTONS[self.update_label],
                       id=cfg.FORMS[self.update_label] % {"id": obj.id}+"_submit")


#@override_settings(DEBUG=True)
class ObjectSingleBaseTest(base.SingleUserTestCase):
    num_objects=5

    def setUp(self):
        base.SingleUserTestCase.setUp(self)
        self._user,self._parser=self.login(self.parser_class)

    def tearDown(self):
        self.logout(self._parser)
        base.SingleUserTestCase.tearDown(self)

    def update_parser(self,response):
        parser=self.parser_class(self)
        parser.feed(response.text)
        self._parser=parser

    def has_annexes(self,**kwargs):
        self._assert_has_annexes(self._parser,**kwargs)

    def action_create_form(self):
        return cfg.URLS[self.create_label]

    def has_create_form(self):
        self._parser.has_create_form()

    def submit_create_form(self,**kwargs):
        form=self._parser.has_form.get(id=cfg.FORMS[self.create_label],
                                       action=self.action_create_form(),method="post")
        self.update_parser(self.form_submit(form,**kwargs))

        args={}
        for k in kwargs:
            if k==self.title_field: continue
            args[k]=kwargs[k]

        return kwargs[self.title_field],args

    def submit_update_form(self,obj,**kwargs):
        form=self._parser.has_form.get(id=cfg.FORMS[self.update_label] % {"id": obj.id},method="post",
                                      action=cfg.URLS[self.update_label] % {"id": obj.id})
        self.update_parser(self.form_submit(form,**kwargs))
        newobj=obj.duplicate(**kwargs)
        return newobj

    def submit_delete_form(self,obj,**kwargs):
        form=self._parser.has_form.get(id=cfg.FORMS[self.delete_label] % {"id": obj.id},
                                       method="post",
                                       action=cfg.URLS[self.delete_label] % {"id": obj.id})
        self.update_parser(self.form_submit(form,**kwargs))
        return #kwargs[self.title_field]

    def list_url(self):
        return self.build_url(self.list_label)


class ObjectMultiUserBaseTest(base.MultiUserTestCase):
    num_objects=5

    def setUp(self):
        base.MultiUserTestCase.setUp(self)
        self._user_list=[]
        self._parser_list=[]
        for n in range(0,self.num_navigators):
            user,parser=self.login(n,self.parser_class)
            self._user_list.append(user)
            self._parser_list.append(parser)

    def tearDown(self):
        for n in range(0,self.num_navigators):
            self.logout(n,self._parser_list[n])
        base.MultiUserTestCase.tearDown(self)

    def update_parser(self,ind,response):
        parser=self.parser_class(self)
        parser.feed(response.text)
        self._parser_list[ind]=parser

    def has_annexes(self,ind,**kwargs):
        self._assert_has_annexes(self._parser_list[ind],**kwargs)

    def action_create_form(self,ind):
        return cfg.URLS[self.create_label]

    def has_create_form(self,ind):
        self._parser_list[ind].has_create_form()

    def submit_create_form(self,ind,**kwargs):
        form=self._parser_list[ind].has_form.get(id=cfg.FORMS[self.create_label],
                                                 action=self.action_create_form(ind),method="post")
        self.update_parser(ind,self.form_submit(ind,form,**kwargs))
        args={}
        for k in kwargs:
            if k==self.title_field: continue
            args[k]=kwargs[k]

        return kwargs[self.title_field],args

    def submit_update_form(self,ind,obj,**kwargs):
        form=self._parser_list[ind].has_form.get(id=cfg.FORMS[self.update_label] % {"id": obj.id},method="post",
                                                 action=cfg.URLS[self.update_label] % {"id": obj.id})
        self.update_parser(ind,self.form_submit(ind,form,**kwargs))
        newobj=obj.duplicate(**kwargs)
        return newobj

    def submit_delete_form(self,ind,obj,**kwargs):
        form=self._parser_list[ind].has_form.get(id=cfg.FORMS[self.delete_label] % {"id": obj.id},method="post",
                                                 action=cfg.URLS[self.delete_label] % {"id": obj.id})
        self.update_parser(ind,self.form_submit(ind,form,**kwargs))
        return 


class ObjectCreateTest(ObjectSingleBaseTest):

    def has_menubar(self,parent): pass

    def _proto_test_object_list_look(self,parent):
        self.update_parser(self.assert_url_exists(self.list_url()))
        self.has_annexes()
        self.has_menubar(parent)

    def _proto_test_create_ok(self,base_url,page_titles_label,page_titles_args,
                              test_object_list_title=False,data={}):
        ## on obj list page, Random sees the "create a new obj" form
        ## he writes a random name and then submit

        if base_url:
            self.update_parser(self.assert_url_exists(base_url))

        self.has_create_form()
        if not data:
            data=self.create_valid_data()

        title_on_list,args=self.submit_create_form(**data)


        ## he returns to the previous page
        self._parser.has_page_titles(page_titles_label,**page_titles_args)

        ## and now there is a obj list:
        if test_object_list_title:
            self._parser.has_object_list()
        self._parser.has_object_in_list(title_on_list,**args)

    def _proto_test_create_fail(self,invalid_data,base_url,
                                page_titles_label,page_titles_args,
                                error_page_titles_label="",error_page_titles_args={},
                                test_object_list_title=False):
        ## on obj list page, Random sees the "create a new obj" form
        ## he writes an empty name and then submit

        if not error_page_titles_label:
            error_page_titles_label=page_titles_label
        if not error_page_titles_args:
            error_page_titles_args=page_titles_args
        if base_url:
            self.update_parser(self.assert_url_exists(base_url))

        self.has_create_form()
        title_on_list,args=self.submit_create_form(**invalid_data)

        ## he go to the obj list page
        ## and see errors
        self._parser.has_page_titles(error_page_titles_label,**error_page_titles_args)
        self._parser.has_errors_box()

        ## he looks for a new form with an hidden next field
        ## he writes a random name and then submit
        self.has_create_form()
        data=self.create_valid_data()
        title_on_list,args=self.submit_create_form(**data)

        ## he returns to the obj list page
        self._parser.has_page_titles(page_titles_label,**page_titles_args)

        ## and now there is a obj list:
        if test_object_list_title:
            self._parser.has_object_list()
        self._parser.has_object_in_list(title_on_list,**args)

class ObjectDetailTest(ObjectSingleBaseTest):
    def setUp(self):
        ObjectSingleBaseTest.setUp(self)
        self.update_parser(self.assert_url_exists(self.build_url(self.list_label)))
        self._object_list=[]
        for n in range(0,self.num_objects):
            self.update_parser(self.assert_url_exists(self.build_url(self.list_label)))
            self._object_list.append(self.create_object())
        
    def create_object(self):
        self.has_create_form()
        data=self.create_valid_data()
        title_on_list,args=self.submit_create_form(**data)
        return self._parser.has_object_in_list(title_on_list,**args)

    def has_menubar(self,obj,next_url=""): pass

class MultiUserObjectDetailTest(ObjectMultiUserBaseTest):

    def setUp(self):
        ObjectMultiUserBaseTest.setUp(self)
        self._object_list=[]
        for ind in range(0,self.num_navigators):
            self.update_parser(ind,self.assert_url_exists(ind,self.build_url(ind,self.list_label)))
            self._object_list.append([])
            for n in range(0,self.num_objects):
                self._object_list[ind].append(self.create_object(ind))
        
    def create_object(self,ind):
        self.has_create_form(ind)
        #self._parser_list[ind].has_create_form()
        data=self.create_valid_data(ind)
        title_on_list,args=self.submit_create_form(ind,**data)
        return self._parser_list[ind].has_object_in_list(title_on_list,**args)

class ObjectDetailUpdateTest(ObjectDetailTest):

    def _proto_test_object_list_detail_links(self):
        ## Random goes to obj detail page
        ## and clicks on every link
        for n in range(0,self.num_objects):
            self.update_parser(self.assert_url_exists(self.list_url()))
            title_on_list=self._object_list[n].title_on_list()
            self._parser.has_link_text(title_on_list)
            href=self._parser.has_link_text.get(title_on_list)
            self.update_parser(self.click_link(href))
            detail_args=self.detail_args(self._object_list[n])
            self._parser.has_page_titles(self.detail_label,**detail_args)

    def _proto_test_object_detail_uses_next(self):
        ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[ind]

        t=[ self.random_string(with_spaces=False) for n in range(random.randint(0,5)) ]
        next_url="/"+"/".join(t)

        url=self.build_url(self.detail_label,id=obj.id)+"?next="+next_url

        ## Random goes to obj detail page
        self.update_parser(self.assert_url_exists(url))
        detail_args=self.detail_args(obj)
        self._parser.has_page_titles(self.detail_label,**detail_args)

        ## He sees the object bar menu with next as default back
        self.has_menubar(obj,next_url=next_url)
        self.has_annexes()

    def _proto_test_object_extra_page(self,page_label):
        ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[ind]

        ## Random goes to obj extra page
        self.update_parser(self.assert_url_exists(self.build_url(page_label,id=obj.id)))
        page_args=self.page_args(obj)
        self._parser.has_page_titles(page_label,**page_args)

        ## He sees the object bar menu
        self.has_menubar(obj)
        self.has_annexes()
        return obj

    def _proto_test_object_detail(self):
        ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[ind]

        ## Random goes to obj detail page
        self.update_parser(self.assert_url_exists(self.build_url(self.detail_label,id=obj.id)))
        detail_args=self.detail_args(obj)
        self._parser.has_page_titles(self.detail_label,**detail_args)

        ## He sees the object bar menu
        self.has_menubar(obj)
        self.has_annexes()

        ## He sees a delete button
        self._parser.has_link(cfg.URLS[self.delete_label] % {"id": obj.id})

        ## He sees an update form
        self._parser.has_update_form(obj)

    def _proto_test_object_update_ok(self,data={}):
        ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[ind]

        ## Random goes to obj detail page
        self.update_parser(self.assert_url_exists(self.build_url(self.detail_label,id=obj.id)))
        detail_args=self.detail_args(obj)
        self._parser.has_page_titles(self.detail_label,**detail_args)

        #self._parser.has_page_titles(self.detail_label,obj=obj.name,user=self._user.username)

        ## He sees an edit form
        self._parser.has_update_form(obj)

        ## He modifies the name and submit
        if not data:
            data=self.update_valid_data()
        newobj=self.submit_update_form(obj,**data)

        ## He returns to the obj detail page, with a new name
        detail_args=self.detail_args(newobj)
        self._parser.has_page_titles(self.detail_label,**detail_args)

    def _proto_test_object_update_fail(self,invalid_data):
        ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[ind]

        ## Random goes to obj detail page
        self.update_parser(self.assert_url_exists(self.build_url(self.detail_label,id=obj.id)))
        detail_args=self.detail_args(obj)
        self._parser.has_page_titles(self.detail_label,**detail_args)
        #self._parser.has_page_titles(self.detail_label,obj=obj.name,user=self._user.username)

        ## He sees an edit form
        self._parser.has_update_form(obj)

        ## He deletes the name and submit
        newobj=self.submit_update_form(obj,**invalid_data)

        ## He returns to the obj detail page, with the old name and errors
        detail_args=self.detail_args(obj)
        self._parser.has_page_titles(self.detail_label,**detail_args)
        self._parser.has_errors_box()

class MultiUserObjectDetailUpdateTest(MultiUserObjectDetailTest):
    def _proto_test_usera_can_see_usera_objects(self):
        n_ind=random.randint(0,self.num_navigators-1)
        p_ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[n_ind][p_ind]

        self.update_parser(n_ind,self.assert_url_exists(n_ind,
                                                        self.build_url(n_ind,self.detail_label,id=obj.id)))
        detail_args=self.detail_args(n_ind,obj)
        self._parser_list[n_ind].has_page_titles(self.detail_label,**detail_args)

    def _proto_test_usera_can_not_see_userb_objects(self):
        n_ind=random.randint(0,self.num_navigators-1)
        b_ind=1-n_ind

        p_ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[b_ind][p_ind]

        self.assert_404(n_ind,self.build_url(n_ind,self.detail_label,id=obj.id))

class ObjectDeleteTest(ObjectDetailTest):

    def _proto_test_object_delete_uses_next(self):
        ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[ind]

        t=[ self.random_string(with_spaces=False) for n in range(random.randint(0,5)) ]
        next_url="/"+"/".join(t)

        url=self.build_url(self.delete_label,id=obj.id)+"?next="+next_url

        ## Random goes to obj detail page
        self.update_parser(self.assert_url_exists(url))
        delete_args=self.delete_args(obj)
        self._parser.has_page_titles(self.delete_label,**delete_args)

        ## He sees the object bar menu with next as default back
        self.has_menubar(obj,next_url=next_url)
        self.has_annexes()

    def _proto_test_object_delete(self):
        ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[ind]

        ## Random goes to obj delete page
        self.update_parser(self.assert_url_exists(self.build_url(self.delete_label,id=obj.id)))
        delete_args=self.delete_args(obj)
        self._parser.has_page_titles(self.delete_label,**delete_args)
        self._parser.has_delete_form(obj)
        self._parser.has_link(cfg.URLS[self.detail_label] % {"id": obj.id})

        ## He sees the object bar menu
        self.has_menubar(obj)
        self.has_annexes()

        ## He confirm the deletion
        self.submit_delete_form(obj)

        ## and goes to the obj list page
        list_args=self.list_args()
        self._parser.has_page_titles(self.list_label,**list_args)

        ## The first obj has disappeared
        self._parser.has_no_object_in_list(obj)
        self.assert_404(self.build_url(self.detail_label,id=obj.id))

class MultiUserObjectDeleteTest(MultiUserObjectDetailTest):
    def _proto_test_usera_can_delete_usera_objects(self):
        n_ind=random.randint(0,self.num_navigators-1)
        p_ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[n_ind][p_ind]

        ## Random A goes to obj delete page
        self.update_parser(n_ind,self.assert_url_exists(n_ind,self.build_url(n_ind,self.delete_label,id=obj.id)))
        delete_args=self.delete_args(n_ind,obj)
        self._parser_list[n_ind].has_page_titles(self.delete_label,**delete_args)
        self._parser_list[n_ind].has_delete_form(obj)
        self._parser_list[n_ind].has_link(cfg.URLS[self.detail_label] % {"id": obj.id})

        ## He confirm the deletion
        self.submit_delete_form(n_ind,obj)

        ## and goes to the obj list page
        list_args=self.list_args(n_ind)
        self._parser_list[n_ind].has_page_titles(self.list_label,**list_args)

        ## The first obj has disappeared
        self._parser_list[n_ind].has_no_object_in_list(obj)
        self.assert_404(n_ind,self.build_url(n_ind,self.detail_label,id=obj.id))

    def _proto_test_usera_can_not_delete_userb_objects(self):
        n_ind=random.randint(0,self.num_navigators-1)
        b_ind=1-n_ind
        p_ind=random.randint(0,self.num_objects-1)
        obj=self._object_list[b_ind][p_ind]

        ## Random A goes to obj delete page
        self.assert_404(n_ind,self.build_url(n_ind,self.delete_label,id=obj.id))
