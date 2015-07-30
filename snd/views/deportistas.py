from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from formtools.wizard.views import SessionWizardView
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
import os
from snd.formularios.deportistas  import *
from snd.models import *
from entidades.models import *
from django.contrib import messages
from coldeportes.utilities import calculate_age,all_permission_required
from snd.formularios.deportistas import VerificarExistenciaForm


@login_required
@all_permission_required('snd.add_deportista')
def wizard_deportista_nuevo(request):
    """
    Junio 7 / 2015
    Autor: Daniel Correa

    Crear un Deportista

    A partir de POST se obtiene la información basica del deportista y se almacena en la base de datos, en caso se no haber POST se muestra el formulario vacio

    :param request: Petición Realizada
    :type request:    WSGIRequest
    """


    try:
        datos = request.session['datos']
        del request.session['datos']
    except Exception:
        return redirect('verificar_deportista')

    deportista_form = DeportistaForm(initial=datos)


    #deportista_form = DeportistaForm()

    if request.method == 'POST':

        deportista_form = DeportistaForm(request.POST, request.FILES)

        if deportista_form.is_valid():
            deportista = deportista_form.save(commit=False)
            deportista.entidad = request.tenant
            deportista.nombres = deportista.nombres.upper()
            deportista.apellidos = deportista.apellidos.upper()
            deportista.barrio = deportista.barrio.upper()
            deportista.comuna = deportista.comuna.upper()
            deportista.direccion = deportista.direccion.upper()
            deportista.save()
            deportista_form.save()
            return redirect('wizard_corporal', deportista.id)


    return render(request, 'deportistas/wizard/wizard_deportista.html', {
        'titulo': 'Información del Deportista',
        'wizard_stage': 1,
        'form': deportista_form,
    })

@login_required
@all_permission_required('snd.add_deportista')
def wizard_deportista(request,id_depor):
    """
    Junio 7 / 2015
    Autor: Daniel Correa

    Editar un Deportista: Primer paso, información de identifiación del deportista

    Se obtiene el id del deportista, se busca y se almacenan los cambios

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    """

    try:
        deportista = Deportista.objects.get(id=id_depor)
    except Exception:
        deportista = None

    deportista_form = DeportistaForm( instance=deportista)

    if request.method == 'POST':

        deportista_form = DeportistaForm(request.POST, request.FILES, instance=deportista)

        if deportista_form.is_valid():
            deportista = deportista_form.save(commit=False)
            deportista.nombres = deportista.nombres.upper()
            deportista.apellidos = deportista.apellidos.upper()
            deportista.barrio = deportista.barrio.upper()
            deportista.comuna = deportista.comuna.upper()
            deportista.direccion = deportista.direccion.upper()
            deportista.save()
            deportista_form.save()
            return redirect('wizard_corporal', id_depor)


    return render(request, 'deportistas/wizard/wizard_deportista.html', {
        'titulo': 'Información del Deportista',
        'wizard_stage': 1,
        'form': deportista_form,
    })

@login_required
@all_permission_required('snd.add_deportista')
def wizard_corporal(request,id_depor):
    """

    Junio 7 / 2015
    Autor: Daniel Correa

    Paso 2: Datos de composicion corporal del deportista

    Se obtiene la información de la peticion, se intenta buscar un objeto ComposicionCorporal y en caso de haber modificaciones se guardan.
    Si la informacion para la ComposicionCorporal del deportista es nueva se inicializa en nulo

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    """

    try:
        corporal = ComposicionCorporal.objects.get(deportista=id_depor)
    except Exception:
        corporal = None

    deportista = Deportista.objects.get(id=id_depor)
    mujer = False
    if deportista.genero == 'Mujer':
        mujer=True

    corporal_form = ComposicionCorporalForm(mujer,instance=corporal)

    if request.method == 'POST':
        corporal_form = ComposicionCorporalForm(request.POST, instance=corporal)

        if corporal_form.is_valid():
            corporal = corporal_form.save(commit=False)
            corporal.deportista = deportista
            corporal.save()
            corporal_form.save()
            return redirect('wizard_historia_deportiva', id_depor)

    return render(request, 'deportistas/wizard/wizard_corporal.html', {
        'titulo': 'Composición Corporal del Deportista',
        'wizard_stage': 2,
        'form': corporal_form,
        'mujer' : mujer
    })

@login_required
@all_permission_required('snd.add_deportista')
def wizard_historia_deportiva(request,id_depor):
    """
    Junio 8 / 2015
    Autor: Daniel Correa

    Paso 3: Ingreso de historias deportivas, en caso se haber se muestran, en caso de ser una nueva se adiciona a la base de datos
    Si no hay Historial Deportivo se inicializa en nulo

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    """

    try:
        hist_depor = HistorialDeportivo.objects.filter(deportista=id_depor)
    except Exception:
        hist_depor = None

    hist_depor_form = HistorialDeportivoForm()

    if request.method == 'POST':
        hist_depor_form = HistorialDeportivoForm(request.POST)

        if hist_depor_form.is_valid():
            hist_depor_nuevo = hist_depor_form.save(commit=False)
            hist_depor_nuevo.deportista = Deportista.objects.get(id=id_depor)
            hist_depor_nuevo.nombre = hist_depor_nuevo.nombre.upper()
            hist_depor_nuevo.marca = hist_depor_nuevo.marca.upper()
            hist_depor_nuevo.modalidad = hist_depor_nuevo.modalidad.upper()
            hist_depor_nuevo.division = hist_depor_nuevo.division.upper()
            hist_depor_nuevo.prueba = hist_depor_nuevo.prueba.upper()
            hist_depor_nuevo.categoria = hist_depor_nuevo.categoria.upper()
            hist_depor_nuevo.institucion_equipo = hist_depor_nuevo.institucion_equipo.upper()
            hist_depor_nuevo.save()
            hist_depor_form.save()
            return redirect('wizard_historia_deportiva', id_depor)


    return render(request, 'deportistas/wizard/wizard_historia_deportiva.html', {
        'titulo': 'Historia Deportiva del Deportista',
        'wizard_stage': 3,
        'form': hist_depor_form,
        'historicos': hist_depor,
        'id_depor': id_depor
    })

#Eliminacion Historia Deportiva
@login_required
@all_permission_required('snd.add_deportista')
def eliminar_historia_deportiva(request,id_depor,id_historia):
    """
    Junio 8 / 2015
    Autor: Daniel Correa

    Eliminar Historial Deportivo

    Se obtiene el historial requerido y se elimina de la base de datos

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    :param id_historia: Llave primaria del historial deportivo
    :type id_historia: String
    """

    try:
        hist_depor = HistorialDeportivo.objects.get(id=id_historia, deportista=id_depor)
        hist_depor.delete()
        return redirect('wizard_historia_deportiva', id_depor)

    except Exception:
        return redirect('wizard_historia_deportiva', id_depor)
#Fin eliminacion historia deportiva


@login_required
@all_permission_required('snd.add_deportista')
def wizard_historia_academica(request,id_depor):
    """
    8 Junio / 2015
    Autor: Daniel Correa

    Paso 4: Información academica, se obtiene un historial academico, se almacena y asigna al deportista.
    Si no hay historial se inicializa en nulo

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    """

    try:
        inf_academ = InformacionAcademica.objects.filter(deportista=id_depor)
    except Exception:
        inf_academ = None

    inf_academ_form = InformacionAcademicaForm()

    if request.method == 'POST':
        inf_academ_form = InformacionAcademicaForm(request.POST)

        if inf_academ_form.is_valid():
            inf_academ_nuevo = inf_academ_form.save(commit=False)
            inf_academ_nuevo.deportista = Deportista.objects.get(id=id_depor)
            inf_academ_nuevo.institucion = inf_academ_nuevo.institucion.upper()
            inf_academ_nuevo.profesion = inf_academ_nuevo.profesion.upper()
            inf_academ_nuevo.save()
            inf_academ_form.save()
            return redirect('wizard_historia_academica', id_depor)


    return render(request, 'deportistas/wizard/wizard_historia_academica.html', {
        'titulo': 'Historia Academica del Deportista',
        'wizard_stage': 4,
        'form': inf_academ_form,
        'historicos': inf_academ,
        'id_depor': id_depor
    })

#Eliminacion Historia Academica
@login_required
@all_permission_required('snd.add_deportista')
def eliminar_historia_academica(request,id_depor,id_historia):
    """
    Junio 8 / 2015
    Autor: Daniel Correa

    Eliminar Historial Academico

    Se obtiene el id del hisotorial y el de deportista, se busca y se elimina de la base de datos

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    :param id_historia: Llave primaria del historial deportivo
    :type id_historia: String
    """
    try:
        inf_academ = InformacionAcademica.objects.get(id=id_historia, deportista=id_depor)
        inf_academ.delete()
        return redirect('wizard_historia_academica', id_depor)

    except Exception:
        return redirect('wizard_historia_academica', id_depor)
#Fin eliminacion historia academica

@login_required
@all_permission_required('snd.add_deportista')
def desactivar_deportista(request,id_depor):
    """
    Junio 8 / 2015
    Autor: Daniel Correa

    Desactivar deportista

    Se cambia el estado actual a activo en caso de estar inactivo o inactivo en caso de estar activo

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    """
    try:
        deportista = Deportista.objects.get(id=id_depor)
        estado_actual = deportista.estado
        deportista.estado = not estado_actual
        deportista.save()
        messages.warning(request, "Deportista desactivado/activado correctamente.")
        return redirect('deportista_listar')
    except:
        messages.error(request, "Error: No existe el deportista solicitado")
        return redirect('deportista_listar')

@login_required
def listar_deportista(request):
    """
    Junio 8 / 2015
    Autor: Daniel Correa

    Listar deportistas de un tenant

    Se obtienen todos los deportistas del respectivo tenant y se listan

    :param request: Petición Realizada
    :type request: WSGIRequest
    """

    deportistas = Deportista.objects.all()
    for dep in deportistas:
        dep.edad = calculate_age(dep.fecha_nacimiento)
        dep.disciplinas_deportivas = ",".join(str(x) for x in dep.disciplinas.all())

    return render(request, 'deportistas/deportistas_lista.html', {
        'deportistas':deportistas,
    })

@login_required
def ver_deportista(request,id_depor):
    """
    Junio 22 /2015
    Autor: Daniel Correa

    Ver Deportista

    Se obtiene la informacion general del deportista desde la base de datos y se muestra

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_depor: Llave primaria del deportista
    :type id_depor: String
    """
    try:
        deportista = Deportista.objects.get(id=id_depor)
    except:
        messages.error(request, "Error: No existe el deportista solicitado")
        return redirect('deportista_listar')
    composicion = ComposicionCorporal.objects.filter(deportista=deportista)
    if len(composicion) != 0:
        composicion = composicion[0]
    historial_deportivo = HistorialDeportivo.objects.filter(deportista=deportista)
    informacion_academica = InformacionAcademica.objects.filter(deportista=deportista)
    deportista.edad = calculate_age(deportista.fecha_nacimiento)
    return render(request,'deportistas/ver_deportista.html',{
            'deportista':deportista,
            'composicion':composicion,
            'historial_deportivo':historial_deportivo,
            'informacion_academica':informacion_academica
        })

@login_required
@all_permission_required('snd.add_deportista')
def finalizar_deportista(request,opcion):
    """
    Junio 10 / 2015
    Autor: Daniel Correa

    enviar mensaje de finalizada la creación de deportista, dependiendo del caso redireccionar


    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param opcion: Caso a redireccionar
    :type opcion: String
    """
    messages.success(request, "Deportista registrado correctamente.")
    if opcion=='nuevo':
        return redirect('deportista_nuevo')
    elif opcion =='listar':
        return redirect('deportista_listar')


@login_required
@all_permission_required('snd.add_deportista')
def verificar_deportista(request):
    """
    Julio 28 /2015
    Autor: Milton Lenis

    Verificación de la existencia de un deportista
    Se verifica si existe el deportista en la entidad actual, si existe en otra entidad o si no existe.
    Dependiendo del caso se muestra una respuesta diferente al usuario

    :param request: Petición Realizada
    :type request: WSGIRequest
    """
    if request.method=='POST':
        form = VerificarExistenciaForm(request.POST)

        if form.is_valid():
            datos = {
                'identificacion': form.cleaned_data['identificacion']
            }

            #Verificación de existencia dentro del tenant actual
            try:
                deportista = Deportista.objects.get(identificacion=datos['identificacion'])
            except Exception:
                deportista = None

            if deportista:
                #Si se encuentra el deportista se carga el template con la existe=True para desplegar el aviso al usuario
                return render(request,'deportistas/verificar_deportista.html',{'existe':True,
                                                                               'deportista':deportista})

            if not deportista:
                #Si no se encuentra en el tenant actual se debe verificar en otros tenants
                #Verificación de existencia en otros tenants
                #Estas dos variables son para ver si existe en otro tenant (True, False) y saber en cual Tenant se encontró
                existencia = False
                tenant_existencia = None
                tenant_actual = connection.tenant
                entidades = Entidad.objects.all()
                for entidad in entidades:
                    connection.set_tenant(entidad)
                    ContentType.objects.clear_cache()
                    try:
                        deportista = Deportista.objects.get(identificacion=datos['identificacion'])
                        existencia = True
                        tenant_existencia = entidad
                        break
                    except Exception:
                        pass

                connection.set_tenant(tenant_actual)


                if existencia:
                    return render(request,'deportistas/verificar_deportista.html',{'existe':True,
                                                                                   'deportista':deportista,
                                                                                   'tenant_existencia':tenant_existencia})
                else:
                    #Si no se encuentra el deportista entonces se redirecciona a registro de deportista con los datos iniciales en una sesión
                    request.session['datos'] = datos
                    return redirect('deportista_nuevo')

    else:
        form = VerificarExistenciaForm()
    return render(request,'deportistas/verificar_deportista.html',{'form':form,
                                                                   'existe':False})