#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = patterns('reportes.views.escenarios',
    url(r'^caracteristicas-escenarios$', 'caracteristicas_escenarios', name='reportes_caracteristicas_escenarios'),

    url(r'^cantidad-espectadores','cantidad_espectadores',name='reporte_cantidad_espectadores')
)
