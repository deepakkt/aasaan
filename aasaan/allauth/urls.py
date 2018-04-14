from importlib import import_module

from django.urls import include, path
from allauth.socialaccount import providers

from . import app_settings


urlpatterns = [path('', include('allauth.account.urls'), name='allauth')]

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += [path('social/', include('allauth.socialaccount.urls'), name='social')]

for provider in providers.registry.get_list():
    try:
        prov_mod = import_module(provider.get_package() + '.urls')
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
    if prov_urlpatterns:
        urlpatterns += prov_urlpatterns
