from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

import contacts.urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aasaan.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^contacts/', include(contacts.urls, namespace='contacts')),
    url(r'^markdown/', include('django_markdown.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
                            (r'^media/(?P<path>.*)',
                            'serve',
                            {'document_root': settings.MEDIA_ROOT}),)

    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)