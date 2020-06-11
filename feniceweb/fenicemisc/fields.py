from django.db import models
from html_sanitizer.django import get_sanitizer

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

class CleanHtmlField(models.CharField):
    def pre_save(self, model_instance, add):
        sanitizer = get_sanitizer()
        value=super().pre_save(model_instance, add)
        value=sanitizer.sanitize(value)
        setattr(model_instance, self.attname, value)
        return value

class CleanHtmlRichTextField(RichTextField):
    def pre_save(self, model_instance, add):
        sanitizer = get_sanitizer()
        value=super().pre_save(model_instance, add)
        value=sanitizer.sanitize(value)
        setattr(model_instance, self.attname, value)
        return value

class CleanHtmlRichTextUploadingField(RichTextUploadingField):
    def pre_save(self, model_instance, add):
        sanitizer = get_sanitizer()
        value=super().pre_save(model_instance, add)
        value=sanitizer.sanitize(value)
        setattr(model_instance, self.attname, value)
        return value
