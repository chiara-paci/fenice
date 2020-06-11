from django.db import models

from fenicemisc import functions

# Create your models here.

class BrowserManager(models.Manager):
    def deserialize(self,ser):
        ser_created=functions.date_deserialize(ser["created"])
        defaults={}
        for k in [ "code_name",
	           "name",
	           "version",
	           "language",
	           "platform",
	           "user_agent",
	           "cookies_enabled",
	           "timezone",
	           "iso_timestamps",
                   "screen_width",
                   "screen_height",
                   "screen_color_depth",
                   "screen_pixel_depth",
                   "screen_available_height",
                   "screen_available_width",
                   "viewport_height",
                   "viewport_width",
	           "luxon_intl",
	           "luxon_intl_tokens",
	           "luxon_zones",
	           "luxon_relative" ]:
            defaults[k]=ser[k]

        obj,created=self.update_or_create(session_key=ser["session_key"],
                                          created=ser_created,
                                          defaults=defaults)
        if created:
            obj.created=ser_created
            obj.save()
        return obj

class Browser(models.Model):
    session_key = models.CharField(max_length=8192)
    created = models.DateTimeField(auto_now_add=True)

    platform = models.CharField(max_length=8192,blank=True,default="")

    code_name = models.CharField(max_length=8192,blank=True,default="")
    name = models.CharField(max_length=8192,blank=True,default="")
    version = models.CharField(max_length=8192,blank=True,default="")
    language = models.CharField(max_length=8192,blank=True,default="")
    user_agent = models.CharField(max_length=8192,blank=True,default="")
    timezone = models.CharField(max_length=8192,blank=True,default="")
    iso_timestamps = models.CharField(max_length=8192,blank=True,default="")

    cookies_enabled = models.BooleanField(default=False)

    screen_width = models.IntegerField(blank=True,default=0)
    screen_height = models.IntegerField(blank=True,default=0)
    screen_color_depth = models.IntegerField(blank=True,default=0)
    screen_pixel_depth = models.IntegerField(blank=True,default=0)
    screen_available_height = models.IntegerField(blank=True,default=0)
    screen_available_width = models.IntegerField(blank=True,default=0)
    viewport_height = models.IntegerField(blank=True,default=0)
    viewport_width = models.IntegerField(blank=True,default=0)

    luxon_intl = models.BooleanField(default=False)
    luxon_intl_tokens = models.BooleanField(default=False)
    luxon_zones = models.BooleanField(default=False)
    luxon_relative = models.BooleanField(default=False)

    objects = BrowserManager()

    def __str__(self):
        return self.session_key

    def __serialize__(self):
        return {
            "session_key": self.session_key,
            "created": functions.date_serialize(self.created),
	    "code_name": self.code_name,
	    "name": self.name,
	    "version": self.version,
	    "language": self.language,
	    "platform": self.platform,
	    "user_agent": self.user_agent,
	    "cookies_enabled": self.cookies_enabled,
	    "timezone": self.timezone,
	    "iso_timestamps": self.iso_timestamps,
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "screen_color_depth": self.screen_color_depth,
            "screen_pixel_depth": self.screen_pixel_depth,
            "screen_available_height": self.screen_available_height,
            "screen_available_width": self.screen_available_width,
            "viewport_height": self.viewport_height,
            "viewport_width": self.viewport_width,
	    "luxon_intl": self.luxon_intl,
	    "luxon_intl_tokens": self.luxon_intl_tokens,
	    "luxon_zones": self.luxon_zones,
	    "luxon_relative": self.luxon_relative,
        }
