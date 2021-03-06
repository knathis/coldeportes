from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from snd.formularios.escenarios  import *
from snd.models import *
from entidades.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from coldeportes.utilities import *
import json


@login_required
@all_permission_required('snd.view_escenario')
def listar_escenarios(request):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    listar los escenarios del tenant respectivo

    Se obtienen los escenario que ha registrado el tenant que realiza la petición

    :param request:   Petición realizada
    :type request:    WSGIRequest
    """
    return render(request, 'escenarios/escenarios_lista.html', {
        'tipo_tenant':request.tenant.tipo
    })

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def finalizar_escenario(request, opcion):
    """
    Junio 10 / 2015
    Autor: Karent Narvaez Grisales
    
    enviar mensaje de finalizada la creación de escenario


    :param request:   Petición realizada
    :type request:    WSGIRequest
    """
    messages.success(request, "Escenario registrado correctamente.")
    if opcion == 'nuevo':
        return redirect('wizard_nuevo_identificacion')
    else:
        return redirect('listar_escenarios')

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def desactivar_escenario(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    desactivar escenario

    Se obtienen el estado actual del escenario y se invierte.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """
    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except ObjectDoesNotExist:
        messages.warning(request, "El escenario que intenta acceder no existe.")
        return redirect('listar_escenarios')

    estado_actual = escenario.estado
    escenario.estado = not(estado_actual)
    escenario.save()

    if estado_actual == 0:
        messages.warning(request, "Escenario desactivado correctamente.")
    elif estado_actual == 1:
        messages.warning(request, "Escenario activado correctamente.")  
        
    return redirect('listar_escenarios')

@login_required
@all_permission_required('snd.view_escenario')
def ver_escenario(request, escenario_id, id_entidad):
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
    mantenimientos =  Mantenimiento.objects.filter(escenario=escenario).order_by("-fecha_ultimo_mantenimiento")
    contactos = Contacto.objects.filter(escenario=escenario)

    datos_georreferenciacion = escenario.obtener_atributos()
    posicion_inicial = escenario.posicionInicialMapa()

    #print(datos_georreferenciacion[0])

    return render(request, 'escenarios/ver_escenario.html', {
        'escenario': escenario,
        'caracteristicas': caracteristicas,
        'horarios': horarios,
        'historicos': historicos,
        'fotos': fotos,
        'videos': videos,
        'mantenimientos': mantenimientos,
        'escenario_id': escenario_id,
        'contactos': contactos,
        'datosMostrar': json.dumps(datos_georreferenciacion),
        'posicionInicial': json.dumps(posicion_inicial),
    })

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_nuevo_identificacion(request):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Crear un Escenario

    Se obtienen los formularios de información del escenario con los datos diligenciados y se guardan.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    """
    from django.db import IntegrityError

    identificacion_form = IdentificacionForm( )

    if request.method == 'POST':

        identificacion_form = IdentificacionForm(request.POST)

        if identificacion_form.is_valid():
            try:
                escenario = identificacion_form.save(commit=False)
                escenario.entidad =  request.tenant
                escenario.nombre = escenario.nombre.upper()
                escenario.direccion = escenario.direccion.upper()
                escenario.barrio = escenario.barrio.upper()
                escenario.nombre_administrador = escenario.nombre_administrador.upper()
                escenario.save()
                return redirect('wizard_caracterizacion', escenario.id)

            except IntegrityError as e:
                if 'unique constraint' in str(e):
                    escenario = identificacion_form.save(commit=False)
                    identificacion_form = IdentificacionForm(instance=escenario)
                    messages.error(request, "El nombre del escenario que intenta crear ya fue registrado.")


    return render(request, 'escenarios/wizard/wizard_escenario.html', {
        'titulo': 'Identificación del Escenario',
        'titulo_panel': 'Registro de Escenarios Deportivos',
        'wizard_stage': 1,
        'form': identificacion_form,
    })

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_identificacion(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Editar un Escenario: Paso datos de identificación escenario

    Se obtienen los formularios de información del escenario con los datos diligenciados y se guardan.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """
    from django.db import IntegrityError
    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except Exception:
        escenario = None

    identificacion_form = IdentificacionEditarForm(instance=escenario)

    if request.method == 'POST':

        identificacion_form = IdentificacionEditarForm(request.POST, instance=escenario)

        if identificacion_form.is_valid():

            try:
                escenario = identificacion_form.save(commit=False)
                escenario.entidad =  request.tenant            
                escenario.nombre = escenario.nombre.upper()
                escenario.direccion = escenario.direccion.upper()
                escenario.barrio = escenario.barrio.upper()
                escenario.nombre_administrador = escenario.nombre_administrador.upper()
                escenario.save()
                return redirect('wizard_caracterizacion', escenario_id)
            except IntegrityError as e:
                if 'unique constraint' in str(e):
                    escenario = identificacion_form.save(commit=False)
                    identificacion_form = IdentificacionForm(request.POST, instance=escenario)
                    messages.error(request, "El nombre del escenario que intenta crear ya fue registrado.")


    return render(request, 'escenarios/wizard/wizard_escenario.html', {
        'titulo': 'Identificación del Escenario',
        'titulo_panel': 'Edición de Escenarios Deportivos',
        'wizard_stage': 1,
        'form': identificacion_form,
        'escenario_id': escenario_id,
    })

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_caracterizacion(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Paso de caracterización de un escenario

    Se obtienen el formulario de las características del escenario con la información actual y se guardan las modificaciones, si hay.
    Si el escenario es nuevo se inicializa en nulo.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """

    try:
        caracteristicas = CaracterizacionEscenario.objects.get(escenario=escenario_id)
    except Exception:
        caracteristicas = None

    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except:
        messages.error(request, 'El escenario que intenta acceder no existe')
        return redirect('wizard_nuevo_identificacion')

    caracterizacion_form = CaracterizacionForm(instance=caracteristicas)
    
    if request.method == 'POST':
        
        caracterizacion_form = CaracterizacionForm(request.POST, request.FILES, instance=caracteristicas)

        if caracterizacion_form.is_valid():
            caracteristicas = caracterizacion_form.save(commit=False)
            caracteristicas.escenario = escenario
            caracteristicas.save()
            caracterizacion_form.save()
            return redirect('wizard_horarios', escenario_id)

    
    return render(request, 'escenarios/wizard/wizard_caracteristicas.html', {
        'titulo': 'Caracterización del Escenario',
        'wizard_stage': 2,
        'form': caracterizacion_form,
        'escenario_id': escenario_id,
    })

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_horarios(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Horarios de disponibilidad de un escenario

    Se obtienen el formulario de los horarios y se muestran los horarios actualmente añadidos al escenario
    y si hay modificaciones se guardan.
    Si el escenario es nuevo se inicializa en nulo.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """

    try:
        horarios = HorarioDisponibilidad.objects.filter(escenario=escenario_id)
    except Exception:
        horarios = None

    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except:
        messages.error(request, 'El escenario que intenta acceder no existe')
        return redirect('wizard_nuevo_identificacion')

    horarios_form = HorariosDisponibleForm()

    if request.method == 'POST':
        horarios_form = HorariosDisponibleForm(request.POST)

        if horarios_form.is_valid():
            horario_nuevo = horarios_form.save(commit=False)
            horario_nuevo.escenario = escenario
            horario_nuevo.save()
            horarios_form.save()
            return redirect('wizard_horarios', escenario_id)


    return render(request, 'escenarios/wizard/wizard_horarios.html', {
        'titulo': 'Horarios de Disponibilidad del Escenario',
        'wizard_stage': 3,
        'form': horarios_form,
        'horarios': horarios,
        'escenario_id': escenario_id,
    })

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_historicos(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Datos históricos de un Escenario

    Se obtienen el formulario de los datos históricos y se muestran los datos actualmente añadidos al escenario
    y si hay modificaciones se guardan.
    Si el escenario es nuevo se inicializa en nulo.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """

    try:
        historicos = DatoHistorico.objects.filter(escenario=escenario_id)
    except Exception:
        historicos = None

    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except:
        messages.error(request, 'El escenario que intenta acceder no existe')
        return redirect('wizard_nuevo_identificacion')

    historico_form = DatoHistoricoForm()

    if request.method == 'POST':
        historico_form = DatoHistoricoForm(request.POST)

        if historico_form.is_valid():
            historico_nuevo = historico_form.save(commit=False)
            historico_nuevo.escenario = escenario
            historico_nuevo.save()
            return redirect('wizard_historicos', escenario_id)


    return render(request, 'escenarios/wizard/wizard_historicos.html', {
        'titulo': 'Datos Históricos del Escenario',
        'wizard_stage': 4,
        'form': historico_form,
        'historicos': historicos,
        'escenario_id': escenario_id,
    })


@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_fotos(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Fotos de un Escenario

    Se obtienen el formulario para subir fotos y se muestran las que actualmente hay añadidos al escenario
    y si hay modificaciones se guardan.
    Si el escenario es nuevo se inicializa en nulo.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """

    try:
        fotos = Foto.objects.filter(escenario=escenario_id)
    except Exception:
        fotos = None

    try:
        videos = Video.objects.filter(escenario=escenario_id)
    except Exception:
        videos = None

    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except:
        messages.error(request, 'El escenario que intenta acceder no existe')
        return redirect('wizard_nuevo_identificacion')

    fotos_form = FotoEscenarioForm()
    videos_form = VideoEscenarioForm()

    if request.method == 'POST':
        fotos_form = FotoEscenarioForm(request.POST, request.FILES)
        videos_form = VideoEscenarioForm(request.POST)

        if fotos_form.is_valid():
            foto_nueva = fotos_form.save(commit=False)
            foto_nueva.escenario = escenario
            foto_nueva.save()
            return redirect('wizard_fotos', escenario_id)


    return render(request, 'escenarios/wizard/wizard_multimedia.html', {
        'titulo': 'Fotos del Escenario',
        'titulo_videos': 'Videos del Escenario',
        'wizard_stage': 5,
        'form': fotos_form,
        'form_videos': videos_form,
        'fotos': fotos,
        'videos': videos,
        'escenario_id': escenario_id,
    })

    
@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_videos(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Videos de un escenario

    Se obtienen el formulario para subir videos y se muestran loss que actualmente hay añadidos al escenario
    y si hay modificaciones se guardan.
    Si el escenario es nuevo se inicializa en nulo.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """
    try:
        fotos = Foto.objects.filter(escenario=escenario_id)
    except Exception:
        fotos = None

    try:
        videos = Video.objects.filter(escenario=escenario_id)
    except Exception:
        videos = None
        
    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except:
        messages.error(request, 'El escenario que intenta acceder no existe')
        return redirect('wizard_nuevo_identificacion')

    fotos_form = FotoEscenarioForm()
    videos_form = VideoEscenarioForm()

    if request.method == 'POST':
        fotos_form = FotoEscenarioForm(request.POST, request.FILES)
        videos_form = VideoEscenarioForm(request.POST)


        if videos_form.is_valid():
            video_nuevo = videos_form.save(commit=False)            

            video = extraer_codigo_video(video_nuevo.url)

            video_nuevo.url = video
            video_nuevo.escenario = escenario
            video_nuevo.save()
            return redirect('wizard_videos', escenario_id)


    return render(request, 'escenarios/wizard/wizard_multimedia.html', {
        'titulo': 'Fotos del Escenario',
        'titulo_videos': 'Videos del Escenario',
        'wizard_stage': 5,
        'form': fotos_form,
        'form_videos': videos_form,
        'fotos': fotos,
        'videos': videos,
        'escenario_id': escenario_id,
    })

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def wizard_mantenimiento(request, escenario_id):
    """
    Octubre 13 / 2015
    Autor: Karent Narvaez Grisales

    Marzo 28 / 2016
    Modificado por: Diego Monsalve
    Se podrán registrar y visualizar todos los mantenimientos del escenario
    
    Mantenimiento de un escenario

    Se obtienen el formulario para ingresar la información del último mantenimiento del escenario.
    Si el escenario es nuevo se inicializa en nulo la información.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """
    
    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except:
        messages.error(request, 'El escenario que intenta acceder no existe')
        return redirect('wizard_nuevo_identificacion')

    try:
        mantenimientos = Mantenimiento.objects.filter(escenario=escenario_id).order_by('-fecha_ultimo_mantenimiento')
    except Exception:
        mantenimientos = None

    mantenimiento_form = MantenimientoEscenarioForm()

    if request.method == 'POST':
        mantenimiento_form = MantenimientoEscenarioForm(request.POST)

        if mantenimiento_form.is_valid():
            mantenimiento = mantenimiento_form.save(commit=False)
            mantenimiento.escenario = escenario
            mantenimiento.save()
            return redirect('wizard_mantenimiento', escenario_id)

    return render(request, 'escenarios/wizard/wizard_mantenimiento.html', {
        'titulo': 'Mantenimientos del Escenario',
        'wizard_stage': 6,
        'form': mantenimiento_form,
        'mantenimientos': mantenimientos,
        'escenario_id': escenario_id,
    })


@login_required
@all_permission_required('snd.add_escenario')
def wizard_contactos(request, escenario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Contactos de un escenario

    Se obtienen el formulario para subir contactos y se muestran los que actualmente hay añadidos al escenario
    y si hay modificaciones se guardan.
    Si el escenario es nuevo se inicializa en nulo.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """

    try:
        contactos = Contacto.objects.filter(escenario=escenario_id)
    except Exception:
        contactos = None

    try:
        escenario = Escenario.objects.get(id=escenario_id)
    except:
        messages.error(request, 'El escenario que intenta acceder no existe')
        return redirect('wizard_nuevo_identificacion')

    contactos_form = ContactoForm()

    if request.method == 'POST':
        contactos_form = ContactoForm(request.POST)

        if contactos_form.is_valid():
            contacto_nuevo = contactos_form.save(commit=False)
            contacto_nuevo.escenario = escenario
            contacto_nuevo.nombre = contacto_nuevo.nombre.upper()
            contacto_nuevo.save()
            #messages.success(request, "¡Escenario guardado exitósamente!")
            return redirect('wizard_contactos', escenario_id)


    return render(request, 'escenarios/wizard/wizard_contactos.html', {
        'titulo': 'Contactos del Escenario',
        'wizard_stage': 7,
        'form': contactos_form,
        'contactos': contactos,
        'escenario_id': escenario_id,
    })


@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def eliminar_horario(request, escenario_id, horario_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Eliminar horario

    Se obtienen el horario de la base de datos y se elimina

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    """

    try:
        horario = HorarioDisponibilidad.objects.get(id=horario_id, escenario=escenario_id)
        horario.delete()
        return redirect('wizard_horarios', escenario_id)

    except Exception:
        return redirect('wizard_horarios', escenario_id)


@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def eliminar_historico(request, escenario_id, historico_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Eliminar histórico

    Se obtienen el dato histórico de la base de datos y se elimina

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    :param historico_id:   Identificador del dato historico
    :type historico_id:    String
    """

    try:
        historico = DatoHistorico.objects.get(id=historico_id, escenario=escenario_id)
        historico.delete()
        return redirect('wizard_historicos', escenario_id)

    except Exception:
        return redirect('wizard_historicos', escenario_id)

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def eliminar_mantenimiento(request, escenario_id, mantenimiento_id):
    """
    Marzo 28 / 2016
    Autor: Diego Monsalve

    Eliminar mantenimiento

    Se obtiene el mantenimiento de la base de datos y se elimina

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    :param mantenimiento_id:   Identificador del dato historico
    :type mantenimiento_id:    String
    """

    try:
        mantenimiento = Mantenimiento.objects.get(id=mantenimiento_id, escenario=escenario_id)
        mantenimiento.delete()
        return redirect('wizard_mantenimiento', escenario_id)

    except Exception:
        return redirect('wizard_mantenimiento', escenario_id)

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def eliminar_foto(request, escenario_id, foto_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Eliminar foto

    Se obtienen la foto de la base de datos y se elimina

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    :param foto_id:   Identificador de la foto
    :type foto_id:    String
    """

    try:
        foto = Foto.objects.get(id=foto_id, escenario=escenario_id)
        foto.delete()
        return redirect('wizard_fotos', escenario_id)
    except Exception:
        return redirect('wizard_fotos', escenario_id)

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def eliminar_video(request, escenario_id, video_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Eliminar foto

    Se obtienen el video de la base de datos y se elimina

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    :param video_id:   Identificador del video
    :type video_id:    String
    """

    try:
        video = Video.objects.get(id=video_id, escenario=escenario_id)
        video.delete()
        return redirect('wizard_videos', escenario_id)
    except Exception:
        return redirect('wizard_videos', escenario_id)

@login_required
#@tenant_required
@all_permission_required('snd.add_escenario')
def eliminar_contacto(request, escenario_id, contacto_id):
    """
    Mayo 30 / 2015
    Autor: Karent Narvaez Grisales
    
    Eliminar contacto

    Se obtienen el contacto de la base de datos y se elimina

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param escenario_id:   Identificador del escenario
    :type escenario_id:    String
    :param contacto_id:   Identificador del contacto
    :type contacto_id:    String
    """

    try:
        contacto = Contacto.objects.get(id=contacto_id, escenario=escenario_id)
        contacto.delete()
        return redirect('wizard_contactos', escenario_id)
    except Exception:
        return redirect('wizard_contactos', escenario_id)


@login_required
def georreferenciacion_escenario(request):
    import json
    from reportes.utilities import atributos_actor_vista
    from reportes.models import TenantEscenarioView

    tipoTenant = request.tenant.obtenerTenant()
    #Mejorado con uso de vista
    escenarios = atributos_actor_vista(TenantEscenarioView)
    posicionInicial = tipoTenant.posicionInicialMapa()
    
    return render(request, 'escenarios/georreferenciacion.html', {
        'escenarios': json.dumps(escenarios),
        'posicionInicial': json.dumps(posicionInicial),
    })