from django.db import connection

def crear_vista_reportes_tenant_caf():
    sql_tenant = """
    CREATE OR REPLACE view reportes_tenantcafview AS 
    SELECT
        CAF.id, CAF.ciudad_id,
        CAF.comuna, CAF.estrato,
        CAF.latitud, CAF.longitud,
        CAF.altura, CAF.estado,
        CAF.entidad_id, CAF.fecha_creacion,
        CLASE.nombre as nombre_clase, SERVICIO.nombre as nombre_servicio
    FROM
    snd_centroacondicionamiento CAF
    LEFT JOIN snd_centroacondicionamiento_clases CLASES ON CLASES.centroacondicionamiento_id = CAF.id
    LEFT JOIN public.entidades_caclase CLASE ON CLASE.id = CLASES.caclase_id
    LEFT JOIN snd_centroacondicionamiento_servicios SERVICIOS ON SERVICIOS.centroacondicionamiento_id = CAF.id
    LEFT JOIN public.entidades_caservicio SERVICIO ON SERVICIO.id = SERVICIOS.caservicio_id;
    """

    cursor = connection.cursor()
    r=''
    r=cursor.execute(sql_tenant)
    r=connection.commit()
    return r


def generar_vista_caf(nuevo_tenant=None):
    from django.db import connection

    #Definiendo tenant actual
    tenant_actual = connection.tenant

    sql = """
        CREATE OR REPLACE VIEW public.entidades_publiccafview AS
    """

    from entidades.models import Entidad
    entidades = Entidad.objects.exclude(schema_name='public').order_by('id')
    primero = entidades[0]

    if nuevo_tenant:
        connection.set_tenant(nuevo_tenant)
        crear_vista_reportes_tenant_caf()

    for entidad in entidades:
        connection.set_tenant(entidad)
        if not nuevo_tenant:
            crear_vista_reportes_tenant_caf()

        aux = ("""
                SELECT * FROM %s.reportes_tenantcafview E
              """)%(entidad.schema_name)

        if primero == entidad:
            sql = ("%s %s")%(sql, aux)
        else:
            sql += (" UNION %s")%(aux)


    public = Entidad.objects.get(schema_name='public')
    connection.set_tenant(public)
        
    sql = ("%s %s")%(sql, ";")
    cursor = connection.cursor()
    r=''
    r=cursor.execute(sql)
    r=connection.commit()

    connection.set_tenant(tenant_actual)