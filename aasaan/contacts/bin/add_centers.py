__author__ = 'dpack'

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aasaan.settings.dev-deepak')

import django
django.setup()

from contacts.models import Zone, Center

filename = r"c:/deepakkt/temp/centers.txt"
centers = open(filename, "r").readlines()

myzone = Zone.objects.all()[0]

for eachcenter in centers:
    newcenter = Center()
    newcenter.center_name = eachcenter.strip()
    newcenter.zone = myzone
    newcenter.save()
    print(newcenter, newcenter.id)

