from django.shortcuts import render,redirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic import TemplateView,CreateView,ListView,View

from . import models

from fenicemisc import views as misc_views
from fenicemisc import decorators as misc_decorators

class BrowserCreateForm(forms.ModelForm): 
    class Meta:
        model = models.Browser
        fields = [ 
            "platform",
            "code_name",
	    "name",
	    "version",
	    "language",
	    "user_agent",
            "timezone",
            "iso_timestamps",
            "cookies_enabled",
            "screen_width",
            "screen_height",
            "screen_color_depth",
            "screen_pixel_depth",
            "screen_available_height",
            "screen_available_width",
            "luxon_intl",
	    "luxon_intl_tokens",
	    "luxon_zones",
	    "luxon_relative",
            "viewport_height",
            "viewport_width",
        ]

    def __init__(self,*args,session_key="",**kwargs):
        self._session_key=session_key
        forms.ModelForm.__init__(self,*args,**kwargs)

    def save(self,*args,**kwargs):
        obj = forms.ModelForm.save(self,commit=False)
        obj.session_key=self._session_key
        if ("commit" not in kwargs) or (kwargs["commit"]):
            obj.save()
        return obj


@method_decorator(misc_decorators.debug_staff_or_404, name='get')
@method_decorator(misc_decorators.json_or_debug_staff_or_404, name='post')
class BrowserListCreateView(misc_views.DelegateAbstractView):
    model = models.Browser
    form_class = BrowserCreateForm
    template_name = "fenicestat/browser_list.html"
    context_object_name = "browser_list"
    success_url = "/stat/browser/"

    class InnerGetView(misc_views.InnerListView): pass
    class InnerPostView(misc_views.InnerCreateView):
        def get_form_kwargs(self):
            kwargs=misc_views.InnerCreateView.get_form_kwargs(self)
            kwargs["session_key"]=self.request.session.session_key
            return kwargs

        def post(self,request,*args,**kwargs):
            request.session["saved_browser_data"]=request.session.session_key
            request.session.save()
            return misc_views.InnerCreateView.post(self,request,*args,**kwargs)

