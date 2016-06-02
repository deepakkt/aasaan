"""
Django settings for aasaan project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from .config import *
from unipath import Path
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

# important note: to facilitate keeping settings in configuration as well, all
# sensitive settings like secret key, server and db passwords are factored
# into a separate config.py file.
#
# This base.py imports all config.py variables in the import above. What the
# config.py file must contain in minimum:
#
# SECRET_KEY variable set
# DB_NAME,
# DB_USER,
# DB_PASSWORD,
# DB_HOST,
# DB_PORT,
# DB_TEST
#
# Put any other sensitive items. Remember to keep config.py in .gitignore
#



BASE_DIR = Path(__file__).parent.parent.parent
STATIC_PATH = os.path.join(BASE_DIR, 'static')
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/


# see dev*.py for debug settings and allowed_hosts settings

# Application definition

# core django apps
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.admindocs',)

# apps built for this application
INSTALLED_APPS += (
    'contacts',
    'AasaanUser',
    'materials',
    'communication',
    'schedulemaster',
    'iconnect',
    'gsync',
    'brochures',
)

# third party apps
INSTALLED_APPS += (
    'django_markdown',
    'import_export',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'ajax_select',
    # 'allauth.socialaccount.providers.facebook',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend"
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
)

# auth and allauth settings
LOGIN_REDIRECT_URL = '/admin/'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'google':
        {'SCOPE': ['profile', 'email'],
         'AUTH_PARAMS': {'access_type': 'online'}},

    'facebook': {
        'SCOPE': ['email', 'publish_stream'],
        'METHOD': 'js_sdk'  # instead of 'oauth2'
    },
}

# Override allauth adapter to auto-login the user
# We are overriding logic in allauth.socialaccount.adapter.DefaultSocialAccountAdapter
# under adapter.py in django-allauth
SOCIALACCOUNT_ADAPTER = 'AasaanUser.social_login.SocialAccountAdapter'

ROOT_URLCONF = 'aasaan.urls'

WSGI_APPLICATION = 'aasaan.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'TEST': {
            'NAME': DB_TEST
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)
STATICFILES_DIRS = (STATIC_PATH,)

# django_markdown settings
MARKDOWN_EDITOR_SKIN = 'simple'
MARKDOWN_SET_NAME = 'markdown'
