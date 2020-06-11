from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

from . import models

class PolicyView(TemplateView):
    template_name="fenicegdpr/policy.html"

    def get_context_data(self,*args,**kwargs):
        context=TemplateView.get_context_data(self,*args,**kwargs)
        try:
            context["policy"]=models.GDPRPolicy.objects.latest("created")
        except models.GDPRPolicy.DoesNotExist as e:
            context["policy"]=None
        return context
