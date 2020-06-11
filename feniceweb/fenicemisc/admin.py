from django.contrib import admin
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.urls import path
from django.contrib.auth.decorators import permission_required


# Register your models here.

from . import models,views

##### Common admin objects

class ExportAdmin(admin.ModelAdmin):
    change_list_template = "fenicemisc/admin/change_list_export.html"

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super().get_urls()
        perm = "%s.view_%s" % info
        my_urls = [
            path(
                'export/', 
                self.admin_site.admin_view( 
                    permission_required(perm,raise_exception=True)(views.AdminExportCsvView.as_view(model=self.model,model_admin=self))
                ),
                name="%s_%s_export" % info
            ),
        ]
        return my_urls + urls

##### FeniceMisc admin objects

class OpenLicenseAdmin(admin.ModelAdmin):
    list_display=[ "short_name","long_name","url" ]

admin.site.register(models.OpenLicense,OpenLicenseAdmin)

class OpenImageCreditAdmin(admin.ModelAdmin):
    list_display=[ "thumb_name","thumbnail","_license","_author","title","_url" ]
    save_as=True

    def thumbnail(self,obj):
        return mark_safe('<a href="%(url)s"><img src="%(url)s" height="50"/></a>' % { "url": obj.thumb_url })

    def _author(self,obj):
        return mark_safe(obj.author)

    def _url(self,obj):
        return mark_safe('<a href="%(url)s">%(url)s</a>' % { "url": obj.url })

    def _license(self,obj):
        if not obj.license.url: return obj.license
        return mark_safe('<a href="%(url)s">%(license)s</a>' % { "url": obj.license.url, "license": str(obj.license) })
        

admin.site.register(models.OpenImageCredit,OpenImageCreditAdmin)


from django.contrib.sessions.models import Session

class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']
    exclude = ['session_data']

    def _session_data(self, obj):
        D=obj.get_decoded()
        ret="<br/>".join( [ "%s: %s" % (k,D[k]) for k in D ] )
        return mark_safe(ret)
            

admin.site.register(Session, SessionAdmin)
