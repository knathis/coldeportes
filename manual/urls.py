from django.conf.urls import patterns, include, url

urlpatterns = patterns('manual.views',
    url(r'^nueva-entrada$', 'nueva_entrada', name='nueva_entrada_manual'),
    url(r'^listar/(\d+)$', 'listar_articulo', name='listar_articulo_manual'),
    url(r'^listar/$', 'listar', name='listar_manual'),
)