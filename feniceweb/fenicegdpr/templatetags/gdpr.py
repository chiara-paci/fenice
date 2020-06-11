from django import template

from django.utils.safestring import mark_safe

register = template.Library()

from .. import models

@register.simple_tag
def gdpr_agreement_text(name):
    L=models.GDPRAgreement.objects.filter(name=name)
    if L.exists():
        agreement=L.latest('created')
    else:
        agreement=models.GDPRAgreement.objects.create(name=name,version="0.1")    
    return mark_safe(agreement.text)

@register.simple_tag
def gdpr_agreement_pk(name):
    L=models.GDPRAgreement.objects.filter(name=name)
    if L.exists():
        agreement=L.latest('created')
    else:
        agreement=models.GDPRAgreement.objects.create(name=name,version="0.1")    
    return str(agreement.pk)
