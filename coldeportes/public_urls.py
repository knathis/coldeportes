from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'gestion_usuarios.views.inicio', name='inicio'),
    url(r'^inicio$', 'gestion_usuarios.views.inicio_public', name='inicio_public'),
    url(r'^inicio$', 'gestion_usuarios.views.inicio_tenant', name='inicio_tenant'), #Url para redireccion al index del tenant
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': 'inicio_public'}, name='logout'),
    url(r'^cambiar-pass/$', 'django.contrib.auth.views.password_change', {'template_name':'cambiar-pass.html', 'post_change_redirect':'inicio'}, name='cambiar_pass'),
    url(r'^entidades/', include('entidades.urls')),
    url(r'^clasificados/',include('publicidad.urls')),
    url(r'^noticias/',include('noticias.urls')),#urls del modulo de noticias
    url(r'^directorio-publico/',include('directorio.publico_urls')),
    url(r'^normograma/',include('normograma.urls')),
    url(r'^manual/',include('manual.urls')),
    url(r'^reportes/', include('reportes.urls.publico')),
    url(r'^buscador/', include('buscador.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^registro-resultados/juegos/', include('registro_resultados.urls.juegos')),
    url(r'^registro-resultados/reporte/', include('registro_resultados.urls.reportes')),
    url(r'^fix-actores-entidades$', 'gestion_usuarios.views.fix_actores_entidades', name='fix_actores_entidades'),
    url(r'^rest/', include('api_interoperable.urls', namespace='rest_framework')),
    url(r'^fix-solicitudes-escenarios$', 'gestion_usuarios.views.fix_solicitudes_escenarios', name='fix_solicitudes_escenarios'),
    url(r'^asignar-reconocimiento-deportivo$', 'gestion_usuarios.views.fix_reconocimiento_deportivo', name='fix_reconocimiento_deportivo'),
    url(r'^fix-calendario-deportivo$', 'gestion_usuarios.views.fix_calendario_deportivo', name='fix_calendario_deportivo'),
    #Calendario deportivo nacional
    url(r'^calendario-deportivo/', include('calendario_deportivo.urls_public')),
)+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)