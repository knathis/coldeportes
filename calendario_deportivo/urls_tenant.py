from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('calendario_deportivo.views',
    url(r'^registro$', 'registro_calendario', name='registro_calendario_nacional'),
    url(r'^editar/(\d+)', 'registro_calendario', name='editar_calendario_nacional'),
    url(r'^listar', 'listar_eventos', name='listado_calendario_nacional'),
    url(r'^cancelar/(\d+)', 'cancelar_evento', name='cancelar_calendario_nacional'),
    url(r'^ver-evento/(\d+)', 'ver_evento', name='ver_evento_calendario_nacional'),


)
