from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from ajax_select import urls as ajax_select_urls
import contacts.urls, iconnect.urls
from brochures.views import HybridDetailView
from brochures.models import BrochureSetItem

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aasaan.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(admin.site.urls)),
    url(r'^contacts/', include(contacts.urls, namespace='contacts')),
    url(r'^markdown/', include('django_markdown.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^comm/', include('iconnect.urls')),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^brochuremaster/(?P<pk>\d)$', HybridDetailView.as_view(model=BrochureSetItem)),
)


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
                            (r'^media/(?P<path>.*)',
                            'serve',
                            {'document_root': settings.MEDIA_ROOT}),)

    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)