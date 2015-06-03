from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('entidades.views',
	url(r'^tipo$', 'tipo', name='entidad_tipo'),
    url(r'^registro$', 'registro', name='entidad_registro'),
)
