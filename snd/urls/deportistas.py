from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from snd.views.deportistas import *


urlpatterns = patterns('snd.views.deportistas',
    #Urls de Wizard
    url(r'^wizard/identificacion$', 'wizard_deportista_nuevo', name='deportista_nuevo'),
    url(r'^wizard/identificacion/(\d+)$', 'wizard_deportista', name='edicion_deportista'),
    url(r'^wizard/composicion-corporal/(\d+)$', 'wizard_corporal', name='wizard_corporal'),
    url(r'^wizard/informacion-adicional/(\d+)$', 'wizard_informacion_adicional', name='wizard_informacion_adicional'),
    url(r'^wizard/historia-deportiva/(\d+)$', 'wizard_historia_deportiva', name='wizard_historia_deportiva'),
    url(r'^wizard/historia-academica/(\d+)$', 'wizard_historia_academica', name='wizard_historia_academica'),
    url(r'^wizard/historia-lesiones/(\d+)$', 'wizard_historia_lesiones', name='wizard_historia_lesiones'),

    #Urls de eliminacion de muchos en el wizard
    url(r'^eliminar/historia-deportiva/(\d+)/(\d+)$', 'eliminar_historia_deportiva', name='eliminar_historia_deportiva'),
    url(r'^eliminar/historia-academica/(\d+)/(\d+)$', 'eliminar_historia_academica', name='eliminar_historia_academica'),
    url(r'^eliminar/historia-lesion/(\d+)/(\d+)$', 'eliminar_historia_lesion', name='eliminar_historia_lesion'),

    #Urls generales
    url(r'^listar$', 'listar_deportista', name='deportista_listar'),
    url(r'^verificar$', 'verificar_deportista', name='verificar_deportista'),
    url(r'^desactivar/(\d+)$', 'desactivar_deportista', name='deportista_desactivar'),
    url(r'^finalizar/(?P<opcion>.+)$', 'finalizar_deportista', name='finalizar_deportista'),
    url(r'^ver/(\d+)/(\d+)/(.+)$','ver_deportista',name='ver_deportista'),
    url(r'^cambio-documento/(\d+)$','cambio_tipo_documento_deportista',name='cambio_documento_deportista'),

    #Urls de aval
    url(r'^avalar-record$','avalar_logros_deportivos',name='avalar_logros_deportivos'),
    url(r'^avalar-record/aceptar/(\d+)/(\d+)$','aceptar_logros_deportivos',name='aceptar_logros_deportivos'),
    url(r'^avalar-record/rechazar/(\d+)/(\d+)$','rechazar_logros_deportivos',name='rechazar_logros_deportivos'),

    #Urls ajax para categoria y modalidad
    url(r'^modalidades/get/(\d+)$','get_modalidades',name='get_modalidades'),
    url(r'^categorias/get/(\d+)$','get_categorias',name='get_categorias'),
)
