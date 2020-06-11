# -*- coding: utf-8 -*-

import re,time
import tarfile,json,io
import os,pwd,grp

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from fenicemisc import models as misc_models
from fenicegdpr import models as gdpr_models
from fenicegames import models as games_models
from feniceauth import models as auth_models

def build_tarinfo(fname,data):
    data = data.encode('utf8')
    info = tarfile.TarInfo(name=fname)
    info.size = len(data)
    info.uid=os.getuid()
    info.gid=os.getgid()
    info.mode=0o644
    info.uname=pwd.getpwuid(os.getuid())[0] 
    info.gname=grp.getgrgid(os.getgid())[0]
    info.mtime=time.time()
    return info, io.BytesIO(data)

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Export data to file <fname.cdar>'

    def add_arguments(self, parser):
        parser.add_argument(
            'cdarname',
            help='filename',
        )

    def handle(self, *args, **options):
        cdarname = options["cdarname"]

        archive=tarfile.open(name=cdarname,mode="r:bz2")

        for model,fname in [ 
                (misc_models.OpenLicense, "./credits/open_licenses.json"),
                (gdpr_models.GDPRAgreement, "./gdpr/agreements.json"),
                (misc_models.OpenImageCredit, "./credits/open_image_credits.json"),
                (games_models.ProductCategory, "./games/product_categories.json"),
                (games_models.Product, "./games/products.json"),
                (auth_models.Group, "./auth/groups.json"),
        ]:
            zobj=archive.getmember(fname)
            print(fname)
            fd=archive.extractfile(zobj)
            D=json.loads(fd.read().decode())
            for ser in D:
                print(ser)
                obj=model.objects.deserialize(ser)
                print(obj)

        for tarinfo in archive.getmembers():
            if tarinfo.name.startswith('./gdpr/policies/'): 
                fd=archive.extractfile(tarinfo)
                D=json.loads(fd.read().decode())
                gdpr_models.GDPRPolicy.objects.deserialize(D)
                continue
            if tarinfo.name.startswith('./auth/users/'): 
                fd=archive.extractfile(tarinfo)
                D=json.loads(fd.read().decode())
                auth_models.User.objects.deserialize(D)
                continue

        archive.close()
