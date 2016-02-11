import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from entidades.models import *
from entidades.forms import *
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from snd.modelos.personal_apoyo import *
from snd.modelos.escenarios import *
from snd.modelos.deportistas import *
from snd.modelos.cafs import *
from snd.modelos.cajas_compensacion import *
from snd.modelos.dirigentes import *
from coldeportes.utilities import calculate_age, add_actores, superuser_only
from reportes.crear_vistas_actores import *
from django.forms import modelformset_factory, modelform_factory

@login_required
def tipo(request):
    return render(request, 'entidad_tipo.html', {
    })

def obtenerFormularioTenant(tipo, post=None, files=None, instance=None):
    if tipo == '1':
        nombre = 'Liga'
        form = LigaForm(post, files, instance=instance)
    elif tipo == '2':
        nombre = 'Federación'
        form = FederacionForm(post, files, instance=instance)
    elif tipo == '3':
        nombre = 'Club'
        form = ClubForm(post, files, instance=instance)
    elif tipo == '4':
        nombre = 'Caja de Compensación'
        form = CajaDeCompensacionForm(post, files, instance=instance)
    elif tipo == '5':
        nombre = 'Ente'
        form = EnteForm(post, files, instance=instance)
    elif tipo == '6':
        nombre = 'Comité'
        form = ComiteForm(post, files, instance=instance)
    elif tipo == '7':
        nombre = 'Federación Paralimpica'
        form = FederacionParalimpicaForm(post, files, instance=instance)
    elif tipo == '8':
        nombre = 'Liga Paralimpica'
        form = LigaParalimpicaForm(post, files, instance=instance)
    elif tipo == '9':
        nombre = 'Club Paralimpico'
        form = ClubParalimpicoForm(post, files, instance=instance)
    elif tipo == '10':
        nombre = 'Centro de Acondicionamiento Físico'
        form = CafForm(post, files, instance=instance)
    elif tipo == '11':
        nombre = 'Escuela de Formación Deportiva'
        form = EscuelaDeportivaForm(post, files, instance=instance)

    return [nombre, form]

@login_required
def obtenerTenant(request, idEntidad, tipo):
    if tipo == '1':
        return Liga.objects.get(id=idEntidad)
    elif tipo == '2':
        return Federacion.objects.get(id=idEntidad)
    elif tipo == '3':
        return Club.objects.get(id=idEntidad)
    elif tipo == '4':
        return CajaDeCompensacion.objects.get(id=idEntidad)
    elif tipo == '5':
        return Ente.objects.get(id=idEntidad)
    elif tipo == '6':
        return Comite.objects.get(id=idEntidad)
    elif tipo == '7':
        return FederacionParalimpica.objects.get(id=idEntidad)
    elif tipo == '8':
        return LigaParalimpica.objects.get(id=idEntidad)
    elif tipo == '9':
        return ClubParalimpico.objects.get(id=idEntidad)
    elif tipo == '10':
        return Caf.objects.get(id=idEntidad)
    elif tipo == '11':
        return EscuelaDeportiva_.objects.get(id=idEntidad)
    raise Exception

@login_required
def generar_vistas_actores(request):
    from reportes.crear_vistas_actores.creacion_vistas import generar_vistas
    generar_vistas()

@login_required
def cambiar_tipo_campo(request):
    from reportes.crear_vistas_actores.creacion_vistas import alter_campo_escenarios
    alter_campo_escenarios()

@login_required
def registro(request, tipo, tipoEnte=None):
    nombre, form = obtenerFormularioTenant(tipo)

    permisos = Permisos.objects.get(entidad=tipo,tipo=tipoEnte if tipoEnte else 0)
    ActoresForm = modelform_factory(Actores,fields=permisos.get_actores('X'))
    form2 = ActoresForm()

    dominio = settings.SUBDOMINIO_URL

    if request.method == 'POST':
        nombre, form = obtenerFormularioTenant(tipo, post=request.POST, files=request.FILES)
        form2 = ActoresForm(request.POST)
        if form.is_valid() and form2.is_valid():
            actores = form2.save(commit=False)
            add_actores(actores,permisos.get_actores('O'))
            actores = form2.save()

            pagina = form.cleaned_data['pagina']
            obj = form.save(commit=False)
            obj.schema_name = pagina
            obj.domain_url = pagina + dominio
            obj.actores = actores
            obj.tipo = tipo
            if tipo == '5':
                obj.tipo_ente = tipoEnte
            if tipo == '6':
                obj.tipo_comite = tipoEnte

            try:
                obj.save()
                messages.success(request, ("%s registrado correctamente.")%(nombre))
                from reportes.crear_vistas_actores.creacion_vistas import generar_vistas
                generar_vistas(obj, obj.obtener_padre())
                if tipoEnte:
                    return redirect('entidad_registro', tipo, tipoEnte)
                else:
                    return redirect('entidad_registro', tipo)
            except Exception as e:
                form.add_error('pagina', "Por favor ingrese otro URL dentro del SIND")
                actores.delete()

    return render(request, 'entidad_registro.html', {
        'nombre': nombre,
        'form': form,
        'form2': form2,
        'dominio': dominio
    })

@login_required
def editar(request, idEntidad, tipo):
    try:
        instance = obtenerTenant(request, idEntidad, tipo)
    except Exception:
        return redirect('entidad_listar')

    nombre, form = obtenerFormularioTenant(tipo, instance=instance)

    if tipo == '5':
        tipoEnte = instance.tipo_ente
    elif tipo == '6':
        tipoEnte = instance.tipo_comite
    else:
        tipoEnte = 0
    permisos = Permisos.objects.get(entidad=tipo,tipo=tipoEnte)
    ActoresForm = modelform_factory(Actores,fields=permisos.get_actores('X'))
    form2 = ActoresForm(instance=instance.actores)

    if request.method == 'POST':
        padre = instance.obtener_padre()
        nombre, form = obtenerFormularioTenant(tipo, post=request.POST, files=request.FILES, instance=instance)
        form2 = ActoresForm(request.POST, instance=instance.actores)
        if form.is_valid() and form2.is_valid():
            actores = form2.save(commit=False)
            add_actores(actores,permisos.get_actores('O'))
            actores.save()
            obj = form.save()
            messages.success(request, ("%s editado correctamente.")%(nombre))
            from reportes.crear_vistas_actores.creacion_vistas import generar_vistas
            generar_vistas(instance, padre)
            return redirect('entidad_listar')

    return render(request, 'entidad_editar.html', {
        'nombre': nombre,
        'form': form,
        'form2': form2,
    })

@login_required
def listar(request):
    entidades = Entidad.objects.exclude(schema_name="public")

    return render(request, 'entidad_listar.html', {
        'entidades': entidades,
    })


from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection

@csrf_exempt
def appMovilLogin(request):
    from django.contrib.auth.models import User
    from django.contrib.auth import authenticate, login

    if request.method == 'GET':
        username = request.GET['name']
        password = request.GET['pw']
        entidad = request.GET['entidad']

        entidad = Entidad.objects.get(schema_name=entidad)
        connection.set_tenant(entidad)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                return JsonResponse({'id': user.id})

    return JsonResponse({'id': None})

from snd.modelos.cafs import *
from snd.modelos.escenarios import *
def appMovilObtenerActores(request):
    datos = {'escenarios':[], 'cafs':[]} # [Escenarios, CAFS]
    if request.method == 'GET':
        entidad = request.GET.get('entidad')
        entidad = Entidad.objects.get(schema_name=entidad)
        connection.set_tenant(entidad)
        centros = CentroAcondicionamiento.objects.all().order_by("nombre")
        
        for i in centros:
            dato = {
                'id': i.id,
                'nombre': i.nombre,
                'latitud': i.latitud,
                'longitud': i.longitud,
                'altura': i.altura,
                'sincronizar': False,
            }
            datos['cafs'].append(dato)

        escenarios = Escenario.objects.all().order_by("nombre")
        for i in escenarios:
            dato = {
                'id': i.id,
                'nombre': i.nombre,
                'latitud': i.latitud,
                'longitud': i.longitud,
                'altura': i.altura,
                'sincronizar': False,
            }
            datos['escenarios'].append(dato)

    return JsonResponse(datos)

def actualizarLocalizacionActor(actor, modelo):
    instancia = modelo.objects.get(id=actor['id'])
    instancia.latitud = actor['latitud']
    instancia.longitud = actor['longitud']
    instancia.save()

import json
def appMovilActualizarLocalizacion(request):
    if request.method == 'GET':
        entidad = request.GET['entidad']
        entidad = Entidad.objects.get(schema_name=entidad)
        connection.set_tenant(entidad)

        tipoActor = request.GET['tipoActor']
        actor = json.loads(request.GET['actor'])

        if tipoActor == '1':
            actualizarLocalizacionActor(actor, CentroAcondicionamiento)
            return JsonResponse({'response': True})

        if tipoActor == '0':
            actualizarLocalizacionActor(actor, Escenario)
            return JsonResponse({'response': True})

def appMovilSincronizar(request):
    if request.method == 'GET':
        entidad = request.GET.get('entidad')
        entidad = Entidad.objects.get(schema_name=entidad)
        connection.set_tenant(entidad)

        escenarios = json.loads(request.GET.get('escenarios', '[]'))
        cafs = json.loads(request.GET.get('cafs', '[]'))

        for i in cafs:
            actualizarLocalizacionActor(i, CentroAcondicionamiento)

        for i in escenarios:
            actualizarLocalizacionActor(i, Escenario)

        return JsonResponse({'response': True})


#==================================================================
# Filtrado de datos para listar
#==================================================================

def cargar_datos_tenantnacional(request, modelo):
    from entidades.cargado_datos_tenantnacional import obtenerDatos
    from django.http import JsonResponse

    try:
        datos = obtenerDatos(request, int(modelo))
    except Exception as e:
        print(e)

    return JsonResponse(datos)


def cargar_columnas_tenantnacional(request, modelo):
    from entidades.cargado_datos_tenantnacional import obtenerCantidadColumnas
    from django.http import JsonResponse

    datos = obtenerCantidadColumnas(request, int(modelo))

    return JsonResponse(datos)


def listar_personal_apoyo_nacionales(request):
    return render(request,'tenant_nacional/personal_apoyo_listar.html',{})


def listar_dirigentes_nacionales(request):
    return render(request,'tenant_nacional/dirigentes_listar.html',{})


def listar_deportistas_nacionales(request):
    return render(request,'tenant_nacional/deportistas_listar.html',{})


def listar_escenarios_nacionales(request):
    return render(request,'tenant_nacional/escenarios_listar.html',{})


def listar_cafs_nacionales(request):
    return render(request,'tenant_nacional/cafs_listar.html',{})


def ver_personal_apoyo_tenantnacional(request,id_personal_apoyo,id_entidad):
    """
    Junio 23 /2015
    Autor: Milton Lenis

    Ver Personal de apoyo

    Se obtiene la informacion general del personal de apoyo desde la base de datos y se muestra

    Edición: Septiembre 1 /2015
    NOTA: Para esta funcionalidad se empezó a pedir la entidad para conectarse y obtener la información de un objeto
    desde la entidad correcta, esto para efectos de consulta desde una liga o una federación.

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_personal_apoyo: Llave primaria del personal de apoyo
    :type id_personal_apoyo: String
    :param id_entidad: Llave primaria de la entidad a la que pertenece el personal de apoyo
    :type id_entidad: String
    """
    tenant = Entidad.objects.get(id=id_entidad).obtenerTenant()
    connection.set_tenant(tenant)
    ContentType.objects.clear_cache()
    try:
        personal_apoyo = PersonalApoyo.objects.get(id=id_personal_apoyo)
    except:
        messages.error(request, "Error: No existe el personal de apoyo solicitado o su información es incompleta")
        return redirect('personal_apoyo_listar')
    formacion_deportiva = FormacionDeportiva.objects.filter(personal_apoyo=personal_apoyo)
    experiencia_laboral = ExperienciaLaboral.objects.filter(personal_apoyo=personal_apoyo)
    personal_apoyo.edad = calculate_age(personal_apoyo.fecha_nacimiento)
    return render(request,'personal_apoyo/ver_personal_apoyo.html',{
            'personal_apoyo':personal_apoyo,
            'formacion_deportiva':formacion_deportiva,
            'experiencia_laboral':experiencia_laboral
        })


def ver_dirigente_tenantnacional(request,dirigente_id,id_entidad):
    """
    Junio 21 / 2015
    Autor: Cristian Leonardo Ríos López

    ver dirigente

    Se obtienen toda la información registrada del dirigente dado y se muestra.

    Edición: Septiembre 1 /2015
    NOTA: Para esta funcionalidad se empezó a pedir la entidad para conectarse y obtener la información de un objeto
    desde la entidad correcta, esto para efectos de consulta desde una liga o una federación.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param dirigente_id:   Identificador del dirigente
    :type dirigente_id:    String
    :param id_entidad: Llave primaria de la entidad a la que pertenece el personal de apoyo
    :type id_entidad: String
    """
    tenant = Entidad.objects.get(id=id_entidad).obtenerTenant()
    connection.set_tenant(tenant)
    ContentType.objects.clear_cache()
    try:
        dirigente = Dirigente.objects.get(id=dirigente_id)
    except Dirigente.DoesNotExist:
        messages.error(request, 'El dirigente que desea ver no existe')
        return redirect('dirigentes_listar')

    cargos = DirigenteCargo.objects.filter(dirigente=dirigente)
    for cargo in cargos:
        cargo.funciones = DirigenteFuncion.objects.filter(dirigente=dirigente, cargo=cargo.id)

    return render(request, 'dirigentes/dirigentes_ver.html', {
        'dirigente': dirigente,
        'cargos': cargos
    })


def ver_deportista_tenantnacional(request,id_depor,id_entidad,estado):
    """
    Junio 22 /2015
    Autor: Daniel Correa

    ##Editado por Milton Lenis el 05 de octubre de 2015

    Ver Deportista

    Se obtiene la informacion general del deportista desde la base de datos y se muestra

    Edición: Septiembre 1 /2015
    NOTA: Para esta funcionalidad se empezó a pedir la entidad para conectarse y obtener la información de un objeto
    desde la entidad correcta, esto para efectos de consulta desde una liga o una federación.

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    :param id_entidad: Llave primaria de la entidad a la que pertenece el personal de apoyo
    :type id_entidad: String
    """

    if estado != 'TRANSFERIDO':
        tenant = Entidad.objects.get(id=id_entidad).obtenerTenant()
        connection.set_tenant(tenant)
        ContentType.objects.clear_cache()
    try:
        deportista = Deportista.objects.get(id=id_depor)
    except:
        messages.error(request, "Error: No existe el deportista solicitado")
        return redirect('deportista_listar')
    composicion = ComposicionCorporal.objects.filter(deportista=deportista)
    if len(composicion) != 0:
        composicion = composicion[0]
    info_adicional = InformacionAdicional.objects.filter(deportista=deportista)
    if len(info_adicional) != 0:
        info_adicional = info_adicional[0]
    historial_lesiones = HistorialLesiones.objects.filter(deportista=deportista)
    historial_doping = HistorialDoping.objects.filter(deportista=deportista)
    historial_deportivo = HistorialDeportivo.objects.filter(deportista=deportista,estado='Aprobado')
    informacion_academica = InformacionAcademica.objects.filter(deportista=deportista)
    return render(request,'deportistas/ver_deportista.html',{
            'deportista':deportista,
            'composicion':composicion,
            'info_adicional':info_adicional,
            'historial_deportivo':historial_deportivo,
            'historial_lesiones':historial_lesiones,
            'historial_doping':historial_doping,
            'informacion_academica':informacion_academica
    })


def ver_escenario_tenantnacional(request,escenario_id,id_entidad):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales

    ver escenario

    Se obtienen toda la información registrada del escenario dado y se muestra.

    Edición: Septiembre 1 /2015
    NOTA: Para esta funcionalidad se empezó a pedir la entidad para conectarse y obtener la información de un objeto
    desde la entidad correcta, esto para efectos de consulta desde una liga o una federación.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    :param id_entidad: Llave primaria de la entidad a la que pertenece el personal de apoyo
    :type id_entidad: String
    """

    tenant = Entidad.objects.get(id=id_entidad).obtenerTenant()
    connection.set_tenant(tenant)
    ContentType.objects.clear_cache()
    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except ObjectDoesNotExist:
        messages.warning(request, "El escenario que intenta acceder no existe.")
        return redirect('listar_escenarios')

    caracteristicas = CaracterizacionEscenario.objects.filter(escenario=escenario)
    horarios = HorarioDisponibilidad.objects.filter(escenario=escenario)
    fotos = Foto.objects.filter(escenario=escenario)
    videos =  Video.objects.filter(escenario=escenario)
    historicos =  DatoHistorico.objects.filter(escenario=escenario)
    mantenimientos =  Mantenimiento.objects.filter(escenario=escenario)
    contactos = Contacto.objects.filter(escenario=escenario)

    return render(request, 'escenarios/ver_escenario.html', {
        'escenario': escenario,
        'caracteristicas': caracteristicas,
        'horarios': horarios,
        'historicos': historicos,
        'fotos': fotos,
        'videos': videos,
        'mantenimientos': mantenimientos,
        'escenario_id': escenario_id,
        'contactos': contactos
    })


def ver_caf_tenantnacional(request,idCAF,id_entidad):
    """
    Junio 23 / 2015
    Autor: Andrés Serna

    Ver CAF

    Se obtienen toda la información registrada del CAF dado y se muestra.

    Edición: Septiembre 1 /2015
    NOTA: Para esta funcionalidad se empezó a pedir la entidad para conectarse y obtener la información de un objeto
    desde la entidad correcta, esto para efectos de consulta desde una liga o una federación.

    :param request:        Petición realizada
    :type request:         WSGIRequest
    :param escenario_id:   Identificador del CAF
    :type escenario_id:    String
    :param id_entidad: Llave primaria de la entidad a la que pertenece el personal de apoyo
    :type id_entidad: String
    """
    tenant = Entidad.objects.get(id=id_entidad).obtenerTenant()
    connection.set_tenant(tenant)
    ContentType.objects.clear_cache()
    try:
        centro = CentroAcondicionamiento.objects.get(id=idCAF)
        planes = CAPlan.objects.filter(centro=centro)
        fotos = CAFoto.objects.filter(centro=centro)
    except Exception:
        return redirect('listar_cafs')

    return render(request, 'cafs/ver_caf.html', {
        'centro': centro,
        'planes': planes,
        'fotos': fotos,
        'contenidoSinPadding': True,
    })


@login_required
@superuser_only
def permisos(request):
    PermisosFormSet = modelformset_factory(Permisos, form = PermisosForm, max_num=1)

    if request.method == 'POST':
        formset = PermisosFormSet(request.POST)
        if formset.is_valid():
            instancies = formset.save(commit=False)
            for index,instancie in enumerate(instancies):
                entidades = formset[index].cleaned_data['entidades'].replace('[','').replace(']','').split(',')
                instancie.entidad = int(entidades[0])
                instancie.tipo = int(entidades[1])
            try:
                formset.save()
                messages.success(request, "Permisos editados correctamente.")
                return redirect('permisos')
            except Exception as e:
                print(e)
                messages.error(request,"Ha ocurrido un error al actualizar los permisos. Revise que la entidad no está repetida")
                return redirect('permisos')
        else:
            form_errors = formset.errors
            messages.error(request, "El formulario no es válido.")
            return render(request, 'entidad_permisos.html',{
                'forms': formset,
                'form_errors': form_errors
                })
    else:
        formset = PermisosFormSet(queryset=Permisos.objects.all())
        return render(request, 'entidad_permisos.html',{
            'forms': formset
            })

@login_required
def refresh_public(request):
    from coldeportes.utilities import refresh_public
    refresh_public()
