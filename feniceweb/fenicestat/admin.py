from django.contrib import admin

# Register your models here.

from . import models

class BrowserAdmin(admin.ModelAdmin):
    list_display = [ "iso_timestamps","session_key","timezone","user_agent","screen_width","screen_height","viewport_width","viewport_height" ]

admin.site.register(models.Browser,BrowserAdmin)
