from .base import *

# for prod environments, the static items are served with
# Nginx from a hardcoded path instead of relative paths
# like in dev environments. So override the paths
# present in base.py
del STATIC_PATH
STATIC_ROOT = "/var/www/aasaan/static"
MEDIA_ROOT = "/var/www/aasaan/media"
# STATICFILES_DIRS = (STATIC_ROOT,)

DEBUG = False
TEMPLATE_DEBUG = False

# to be filled in during deployment
ALLOWED_HOSTS = ["188.166.245.115",
                 "52.72.197.233",
                 "aasaan.isha.in"]

# deploy on gunicorn on linux boxes
INSTALLED_APPS += (
    'gunicorn',
)
