from django.conf.urls import patterns, url
from brochures import views

urlpatterns = patterns('',
                       url(r'^get_brochure_list', views.get_brochure_list, name='brochure_list'),
                       url(r'^get_brochure_set', views.get_brochure_set, name='brochure_set'),
                       )
