# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from fenicemisc import models as misc_models
from fenicegdpr import models as gdpr_models
from fenicegames import models as games_models

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Change format of images'

    def handle(self, *args, **options):
        for obj in misc_models.OpenImageCredit.objects.all():
            obj.thumb_path=obj.thumb_path.replace(".webp",".jpg")
            obj.save()

        for obj in games_models.Product.objects.all():
            obj.image_path=obj.image_path.replace(".webp",".jpg")
            obj.save()
