from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from snd.views.escenarios import *


urlpatterns = patterns('snd.views.escenarios',
    #urls tabla interactiva
    url(r'^listar$', 'listar_escenarios', name='listar_escenarios'), 
    url(r'^desactivar/(\d+)$', 'desactivar_escenario', name='desactivar_escenario'),
    url(r'^ver/(\d+)/(\d+)$', 'ver_escenario', name='ver_escenario'),
    url(r'^finalizar/(?P<opcion>.+)$', 'finalizar_escenario', name='finalizar_escenario'),

    url(r'^georreferenciacion$', 'georreferenciacion_escenario', name='georreferenciacion_escenario'),


    #urls wizard
    url(r'^wizard/identificacion$', 'wizard_nuevo_identificacion', name='wizard_nuevo_identificacion'), 
    url(r'^wizard/identificacion/(\d+)$', 'wizard_identificacion', name='wizard_identificacion'), 
    url(r'^wizard/caracterizacion/(\d+)$', 'wizard_caracterizacion', name='wizard_caracterizacion'), 
    url(r'^wizard/horarios/(\d+)$', 'wizard_horarios', name='wizard_horarios'), 
    url(r'^wizard/fotos/(\d+)$', 'wizard_fotos', name='wizard_fotos'), 
    url(r'^wizard/videos/(\d+)$', 'wizard_videos', name='wizard_videos'), 
    url(r'^wizard/mantenimiento/(\d+)$', 'wizard_mantenimiento', name='wizard_mantenimiento'), 
    url(r'^wizard/historicos/(\d+)$', 'wizard_historicos', name='wizard_historicos'), 
    url(r'^wizard/contactos/(\d+)$', 'wizard_contactos', name='wizard_contactos'), 
    
    #urls para eliminar los pasos de los que se pueden registrar muchos en el wizard
    url(r'^eliminar/horario/(\d+)/(\d+)$', 'eliminar_horario', name='eliminar_horario'), 
    url(r'^eliminar/historico/(\d+)/(\d+)$', 'eliminar_historico', name='eliminar_historico'), 
    url(r'^eliminar/foto/(\d+)/(\d+)$', 'eliminar_foto', name='eliminar_foto'), 
    url(r'^eliminar/video/(\d+)/(\d+)$', 'eliminar_video', name='eliminar_video'), 
    url(r'^eliminar/contacto/(\d+)/(\d+)$', 'eliminar_contacto', name='eliminar_contacto'),
    url(r'^eliminar/mantenimiento/(\d+)/(\d+)$', 'eliminar_mantenimiento', name='eliminar_mantenimiento'),
)