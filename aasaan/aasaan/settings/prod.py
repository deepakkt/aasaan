from .base import *

# for prod environments, the static items are served with
# Nginx from a hardcoded path instead of relative paths
# like in dev environments. So override the paths
# present in base.py
del STATIC_PATH
STATIC_ROOT = "/var/www/aasaan/static"
MEDIA_ROOT = "/var/www/aasaan/media"
BIN_ROOT = "/home/deepak/django/aasaan/.virtualenvs/aasaan/bin"
# STATICFILES_DIRS = (STATIC_ROOT,)

DEBUG = False
TEMPLATE_DEBUG = False

# setup a simple cache mechanism with memcached and pylibmc
# ensure server has dependencies setup
# install memcached server and library
# $ sudo apt-get install memcached libmemcached-dev

# install pylibmc
# $ pip install pylibmc
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# to be filled in during deployment
ALLOWED_HOSTS = ['*']

# setup asynchronous processing with rq and django-rq
ASYNC = True

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
}


# deploy on gunicorn and django_rq for prod
INSTALLED_APPS += (
    "django_rq",
    'gunicorn',
)
