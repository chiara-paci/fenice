# -*- coding: utf-8 -*-

from django.shortcuts import render,redirect
from django.conf import settings
from django.urls import reverse_lazy

from django.http import JsonResponse,HttpResponse
import csv

# Create your views here.
from django.views.generic import TemplateView,CreateView,ListView,View

import math

from . import models

class HomePageView(TemplateView): 
    template_name="fenicemisc/index.html"

    def get_context_data(self,*args,**kwargs):
        context=TemplateView.get_context_data(self,*args,**kwargs)
        return context

    def get(self,request,*args,**kwargs):
        content_accepted=request.META.get('HTTP_ACCEPT')
        print(content_accepted)
        return TemplateView.get(self,request,*args,**kwargs)

class CreditsView(TemplateView): 
    template_name="fenicemisc/credits.html"

    def get_context_data(self,*args,**kwargs):
        context=TemplateView.get_context_data(self,*args,**kwargs)
        context["openimagecredit_list"]=models.OpenImageCredit.objects.all()
        return context

class InnerListView(ListView):
    form_class = None

    def get_context_data(self,**kwargs):
        ctx=ListView.get_context_data(self,**kwargs)
        ctx["form"]=self.form_class()
        return ctx
        
class InnerCreateView(CreateView):
    context_object_name= None
    success_url = None

    def get_queryset(self): # pragma: no cover
        return self.model.objects.all()

    def get_success_url(self):
        return self.success_url

    def post(self,request,*args,**kwargs):
        self.request=request
        form = self.form_class(**self.get_form_kwargs())
        content_accepted=request.META.get('HTTP_ACCEPT')

        if form.is_valid():
            self.object=form.save()
            if content_accepted is not None:
                if content_accepted.startswith("application/json"):
                    response=JsonResponse({},status=201)
                    return response
            return redirect(self.get_success_url())
        if content_accepted is not None:
            if content_accepted.startswith("application/json"):
                response=JsonResponse({"errors": "invalid data"},status=400)
                return response
        context={
            "form": form, 
            self.context_object_name: self.get_queryset()
        }
        return render(request,self.template_name,context)


class DelegateAbstractView(View):
    model = None
    form_class = None
    template_name = ""
    success_url = ""
    context_object_name = "object_list"

    def get(self,request, *args, **kwargs):
        view=self.InnerGetView.as_view(model=self.model,form_class=self.form_class,template_name=self.template_name)
        response=view(request,*args,**kwargs)
        return response

    def post(self,request, *args, **kwargs):
        view=self.InnerPostView.as_view(model=self.model,form_class=self.form_class,
                                        context_object_name=self.context_object_name,
                                        success_url=self.success_url,
                                        template_name=self.template_name)
        response=view(request,*args,**kwargs)
        return response

class AdminExportCsvView(ListView):
    model_admin=None

    def get_table(self):
        return self.model.objects.table()

    def get(self,request):
        meta = self.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        tab=self.get_table()
        for row in tab:
            writer.writerow(row)
        return response
