from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError
from django.utils import timezone

from fenicemisc import functions
from fenicemisc import models as misc_models
from fenicemisc import fields as misc_fields

# Create your models here.

class GDPRPolicyManager(models.Manager):
    def deserialize(self,ser):
        defaults={
            "text": ser["text"],
            "created": functions.date_deserialize(ser["created"]),
        }
        obj,created=self.update_or_create(version=ser["version"],
                                          defaults=defaults)
        if created:
            obj.created=defaults["created"]
            obj.save()
        return obj

    def current(self):
        return self.latest("created")

class GDPRPolicy(models.Model):
    text = misc_fields.CleanHtmlRichTextField()
    #text = models.CharField(max_length=8192)
    version = models.CharField(max_length=1024,unique=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects=GDPRPolicyManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(created__lte=models.F('last_modified')),
                name='gdprpolicy_correct_datetime'
            ),
        ]

    def clean(self):
        if self.created is None: return
        if self.last_modified is None: 
            if self.created >  timezone.now():
                raise ValidationError({
                    'created': ValidationError("'created' can't be in the future"),
                })
            return

        if self.created > self.last_modified:
            raise ValidationError({
                'created': ValidationError("'created' should be smaller than 'last_modified'"),
            })

    def __str__(self):
        return "%s" % self.version

    def __serialize__(self):
        return {
            "text": self.text,
            "version": self.version,
            "created": functions.date_serialize(self.created),
            "last_modified": functions.date_serialize(self.last_modified),
        }

class GDPRAgreementManager(models.Manager):
    def deserialize(self,ser):
        defaults={
            "text": ser["text"],
            "created": functions.date_deserialize(ser["created"]),
        }
        obj,created=self.update_or_create(name=ser["name"],version=ser["version"],
                                          defaults=defaults)
        if created:
            obj.created=defaults["created"]
            obj.save()
        return obj

class GDPRAgreement(models.Model):
    name = models.CharField(max_length=4096)
    text = misc_fields.CleanHtmlField(max_length=8192)
    version = models.CharField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects=GDPRAgreementManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'version'], 
                                    name='unique_name_version'),
            models.CheckConstraint(
                check=models.Q(created__lte=models.F('last_modified')),
                name='gdpragreement_correct_datetime'
            ),
        ]

    def clean(self):
        if self.created is None: return
        if self.last_modified is None: 
            if self.created >  timezone.now():
                raise ValidationError({
                    'created': ValidationError("'created' can't be in the future"),
                })
            return

        if self.created > self.last_modified:
            raise ValidationError({
                'created': ValidationError("'created' should be smaller than 'last_modified'"),
            })

    def __str__(self):
        return "%s %s" % (self.name,self.version)

    def __serialize__(self):
        return {
            "name": self.name,
            "text": self.text,
            "version": self.version,
            "created": functions.date_serialize(self.created),
            "last_modified": functions.date_serialize(self.last_modified),
        }

