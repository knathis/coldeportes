from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('entidades.views',
	url(r'^tipo$', 'tipo', name='entidad_tipo'),
    url(r'^registro/(\d+)$', 'registro', name='entidad_registro'),
    url(r'^registro/(\d+)/(\d+)$', 'registro', name='entidad_registro'),
    #url(r'^test/$', 'test', name='test'),
    #url(r'^cafs/$', 'cafs', name='cafs'),
    #url(r'^sincronizar/$', 'sincronizar', name='sincronizar'),
    #url(r'^localizacion/$', 'actualizarLocalizacion', name='actualizarLocalizacion'),
    url(r'^editar/(\d+)/(\d+)$', 'editar', name='entidad_editar'),
    url(r'^listar$', 'listar', name='entidad_listar'),
    url(r'^appMovil/login/$', 'appMovilLogin', name='app_movil_login'),
    url(r'^appMovil/obtenerActores/$', 'appMovilObtenerActores', name='app_movil_obtener_actores'),
    url(r'^appMovil/sincronizar/$', 'appMovilSincronizar', name='app_movil_sincronizar'),
    url(r'^appMovil/actualizarLocalizacion/$', 'appMovilActualizarLocalizacion', name='app_movil_actualizar_localizacion'),
    url(r'^personal-apoyo$', 'listar_personal_apoyo_nacionales', name='personal_apoyo_listar'),
	url(r'^personal-apoyo/ver/(\d+)/(\d+)$', 'ver_personal_apoyo_tenantnacional', name='ver_personal_apoyo_tenantnacional'),
	url(r'^deportistas$', 'listar_deportistas_nacionales', name='deportista_listar'),
	url(r'^deportistas/ver/(\d+)/(\d+)/(.+)$', 'ver_deportista_tenantnacional', name='ver_deportista_tenantnacional'),
	url(r'^escenarios$', 'listar_escenarios_nacionales', name='listar_escenarios'),
	url(r'^escenarios/ver/(\d+)/(\d+)$', 'ver_escenario_tenantnacional', name='ver_escenario_tenantnacional'),
	url(r'^dirigentes$', 'listar_dirigentes_nacionales', name='dirigentes_listar'),
	url(r'^dirigentes/ver/(\d+)/(\d+)$', 'ver_dirigente_tenantnacional', name='ver_dirigente_tenantnacional'),
	url(r'^cafs$', 'listar_cafs_nacionales', name='listar_cafs'),
	url(r'^cafs/ver/(\d+)/(\d+)$', 'ver_caf_tenantnacional', name='ver_caf_tenantnacional'),
    url(r'^cargar-columnas/(\d+)$', 'cargar_columnas_tenantnacional', name='cargar_columnas_tenantnacional'),
    url(r'^cargar-datos/(\d+)$', 'cargar_datos_tenantnacional', name='cargar_datos_tenantnacional'),

    url(r'^permisos/$', 'permisos', name='permisos'),

    # funciones especiales
    url(r'^actualizar-todas-las-vistas$', 'generar_vistas_actores', name='actualizar_todas_las_vistas'),
    url(r'^cambiar-campo-espectadores$', 'cambiar_tipo_campo', name='cambiar_tipo_campo'),
    url(r'^refresh-public$', 'refresh_public', name='refresh_public'),
)
