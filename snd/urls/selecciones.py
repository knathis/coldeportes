from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from snd.views.selecciones import *

urlpatterns = patterns('snd.views.selecciones',
    url(r'^registro/base$', 'registrar_base', name='registrar_seleccion'),
    url(r'^registro/deportistas/(\d+)$', 'registrar_deportistas', name='registrar_deportistas'),
    url(r'^registro/personal/(\d+)$', 'registrar_personal', name='registrar_personal'),
    url(r'^listar$', 'listar_seleccion', name='listar_seleccion'),
)
