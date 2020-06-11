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
        context["save_email_url"]=reverse_lazy("fenicegames:email_create")

        context["product_list"]=[]

        for image_url,color,name,description,quote,measure,num_quote,num_target in [
                ("q_olio.jpg","orange",
                 "Olio extra vergine del Garda D.O.P.",
                 "L'olio extra vergine del Garda ha un gusto delicato e fruttato con una nota di mandorla dolce, bassa acidità e ottima digeribilità.",
                 5,"kg",17,20),
                ("q_asparagi.jpg","green",
                 "Asparagi bianchi di Bassano D.O.P.",
                 "Gli asparagi bianchi di Bassano sono spessi e teneri e hanno un gusto dolce-amaro. Ricchi di vitamine, sono depurativi per fegato e reni.",
                 1,"kg",4,20),
                ("q_carote.jpg","magenta",
                 "Carote di Chioggia",
                 "La carota è ricca di vitamine e sali minerali, tonica e rinfrescante. Molto versatile in cucina, può essere usata anche per lenire scottature e altre piaghe della pelle.",
                 1,"kg",40,50),
                ("q_formaggio2.jpg","blue",
                 "Bastardo del Grappa P.A.T.",
                 "Il Bastardo del Grappa è un formaggio semigrasso, a pasta semidura, dal sapore preciso ma delicato. Ideale con la polenta.",
                 1,"kg",12,40),
                ("q_aglio.jpg","green",
                 "Aglio bianco polesano D.O.P.",
                 "L'aglio del Polesine ha un aroma intenso, ma non pungente, e un profumo delicato. Si conserva facilmente grazie al suo basso tenore d'acqua.",
                 150,"g",16,30),
                ("q_formaggio1.jpg","orange",
                 "Monte veronese D.O.P.",
                 "Il Monte veronese è un formaggio dal sapore delicato e gradevole, di fermenti lattici e di panna, che tende a diventare piccante con la stagionatura.",
                 1,"kg",12,60),
        ]:
            percent=int(100*num_quote/num_target)

            alpha=math.pi*percent/100.0
            x=100*math.cos(alpha)
            y=100*math.sin(alpha)
            arc={
                "start_x": x,
                "start_y": -y, # y axis is reversed
                "end_x": x,
                "end_y": y,
                "large_arc": int(percent>50),
            }
            context["product_list"].append({
                "name": name,
                "description": description,
                "quote": quote,
                "target": quote*num_target,
                "achievement": quote*num_quote,
                "measure": measure,
                "image_url": "images/products/%s" % image_url,
                "arc": arc,
                "color": color,
                "percent": percent
            })

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
