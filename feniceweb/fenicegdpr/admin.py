from django.contrib import admin
from django.forms import widgets
from django_ace import AceWidget

# Register your models here.

from . import models

class GDPRPolicyAdmin(admin.ModelAdmin):
    list_display=[ "version","created","last_modified" ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'text':
            kwargs['widget'] = AceWidget(mode="html",theme='twilight')
        return admin.ModelAdmin.formfield_for_dbfield(self,db_field,**kwargs)

admin.site.register(models.GDPRPolicy,GDPRPolicyAdmin)

class GDPRAgreementAdmin(admin.ModelAdmin):
    list_display=[ "name","version","created","last_modified","text" ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'text':
            kwargs['widget'] = widgets.Textarea
        return admin.ModelAdmin.formfield_for_dbfield(self,db_field,**kwargs)

admin.site.register(models.GDPRAgreement,GDPRAgreementAdmin)

