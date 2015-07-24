from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from snd.formularios.entrenadores import EntrenadorForm, FormacionDeportivaForm, ExperienciaLaboralForm, VerificarExistenciaForm
from snd.models import Entrenador, FormacionDeportiva, ExperienciaLaboral
from coldeportes.utilities import calculate_age
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from entidades.models import Entidad


@login_required
@permission_required('snd.add_entrenador')
def wizard_entrenador_nuevo(request):
    """
    Junio 9 / 2015
    Autor: Milton Lenis

    Crear un Entrenador

    Si se envió un formulario a través del método POST, se hace el registro del entrenador y se pasa a la siguiente fase del wizard
    de lo contrario se muestra la primera etapa con el formulario vacío sin guardar nada en la base de datos.

    :param request: Petición Realizada
    :type request:    WSGIRequest
    """

    entrenador_form = EntrenadorForm()

    if request.method == 'POST':

        entrenador_form = EntrenadorForm(request.POST, request.FILES)

        if entrenador_form.is_valid():
            entrenador = entrenador_form.save(commit=False)
            entrenador.entidad_vinculacion = request.tenant
            entrenador.nombres = entrenador.nombres.upper()
            entrenador.apellidos = entrenador.apellidos.upper()
            entrenador.tipo_id = entrenador.tipo_id.upper()
            entrenador.save()
            entrenador_form.save()
            return redirect('wizard_formacion_deportiva', entrenador.id)


    return render(request, 'entrenadores/wizard/wizard_entrenador.html', {
        'titulo': 'Información básica',
        'wizard_stage': 1,
        'form': entrenador_form,
    })

@login_required
@permission_required('snd.add_entrenador')
def finalizar_entrenador(request, opcion):
    """
    Junio 16 / 2015
    Autor: Milton Lenis

    enviar mensaje de finalizada la creación de entrenador


    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param opcion: Opción para redireccionamiento
    :type opcion: String
    """
    messages.success(request, "Entrenador registrado correctamente.")
    if opcion=='nuevo':
        return redirect('entrenador_nuevo')
    elif opcion =='listar':
        return redirect('entrenador_listar')


@login_required
@permission_required('snd.change_entrenador')
def wizard_entrenador(request,id_entrenador):
    """
    Junio 9 / 2015
    Autor: Milton Lenis

    Editar un Entrenador: Primer paso, información de identifiación del entrenador

    Se obtiene el id del entrenador, se busca, se verifica que se hayan realizado cambios y se almacenan los cambios realizados.

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entrenador: Llave primaria del entrenador
    :type id_entrenador: String
    """

    try:
        entrenador = Entrenador.objects.get(id=id_entrenador)
    except Exception:
        entrenador = None

    entrenador_form = EntrenadorForm(instance=entrenador)

    if request.method == 'POST':

        entrenador_form = EntrenadorForm(request.POST, request.FILES, instance=entrenador)

        if entrenador_form.is_valid():
            entrenador = entrenador_form.save(commit=False)
            entrenador.nombres = entrenador.nombres.upper()
            entrenador.apellidos = entrenador.apellidos.upper()
            entrenador.tipo_id = entrenador.tipo_id.upper()
            entrenador.save()
            entrenador_form.save()
            return redirect('wizard_formacion_deportiva', id_entrenador)


    return render(request, 'entrenadores/wizard/wizard_entrenador.html', {
        'titulo': 'Información básica',
        'wizard_stage': 1,
        'form': entrenador_form,
    })


@login_required
@permission_required('snd.change_entrenador')
def wizard_formacion_deportiva(request,id_entrenador):
    """

    Junio 9 / 2015
    Autor: Milton Lenis

    Paso 2 del wizard: Datos de formación deportiva para un entrenador

    Se obtiene la información de la peticion, se intenta buscar un objeto FormacionDeportiva para verificar si existe (se desea modificar)
    En caso de haber modificaciones se guardan.
    Si la informacion para la FormacionDeportiva del entrenador es nueva se inicializa en nulo para que los formularios estén vacíos.

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entrenador: Llave primaria del entrenador
    :type id_entrenador: String
    """

    try:
        formacion_deportiva = FormacionDeportiva.objects.filter(entrenador=id_entrenador)
    except Exception:
        formacion_deportiva = None
    formaciondep_form = FormacionDeportivaForm()

    if request.method == 'POST':
        formaciondep_form = FormacionDeportivaForm(request.POST)
        if formaciondep_form.is_valid():
            formacion_deportiva = formaciondep_form.save(commit=False)
            formacion_deportiva.entrenador = Entrenador.objects.get(id=id_entrenador)
            formacion_deportiva.denominacion_diploma = formacion_deportiva.denominacion_diploma.upper()
            formacion_deportiva.nivel = formacion_deportiva.nivel.upper()
            formacion_deportiva.institucion_formacion = formacion_deportiva.institucion_formacion.upper()
            formacion_deportiva.save()
            formaciondep_form.save()
            return redirect('wizard_formacion_deportiva', id_entrenador)

    return render(request, 'entrenadores/wizard/wizard_formacion_deportiva.html', {
        'titulo': 'Información sobre la formación deportiva',
        'wizard_stage': 2,
        'form': formaciondep_form,
        'historicos': formacion_deportiva,
        'id_entrenador': id_entrenador
    })

@login_required
@permission_required('snd.change_entrenador')
def eliminar_formacion_deportiva(request,id_entrenador,id_formacion):
    """
    Junio 9 / 2015
    Autor: Milton Lenis

    Eliminar un registro de formación deportiva

    Se obtiene el registro de la formación deportiva que se desea eliminar y se procede a eliminarlo de la base de datos.

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entrenador: Llave primaria del entrenador
    :type id_entrenador: String
    :param id_formacion: Llave primaria de la formación deportiva
    :type id_formacion: String
    """

    try:
        formacion_deportiva = FormacionDeportiva.objects.get(id=id_formacion, entrenador=id_entrenador)
        formacion_deportiva.delete()
        return redirect('wizard_formacion_deportiva', id_entrenador)

    except Exception:
        return redirect('wizard_formacion_deportiva', id_entrenador)


@login_required
@permission_required('snd.change_entrenador')
def wizard_experiencia_laboral(request,id_entrenador):
    """
    Junio 9 / 2015
    Autor: Milton Lenis

    Paso 3: Ingreso de la experiencia laboral de un entrenador, en caso se haber experiencias laborales registradas, se muestran,
    en caso de ser una nueva experiencia laboral a registrar, se adiciona a la base de datos.
    Si no hay Experiencia laboral registrada se inicializa en nulo para que se muestren los formularios vacíos

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entrenador: Llave primaria del entrenador
    :type id_entrenador: String
    """

    try:
        experiencia_laboral = ExperienciaLaboral.objects.filter(entrenador=id_entrenador)
    except Exception:
        experiencia_laboral = None

    experiencia_laboral_form = ExperienciaLaboralForm()

    if request.method == 'POST':
        experiencia_laboral_form = ExperienciaLaboralForm(request.POST)

        if experiencia_laboral_form.is_valid():
            experiencia_laboral_nuevo = experiencia_laboral_form.save(commit=False)
            experiencia_laboral_nuevo.entrenador = Entrenador.objects.get(id=id_entrenador)
            experiencia_laboral_nuevo.nombre_cargo = experiencia_laboral_nuevo.nombre_cargo.upper()
            experiencia_laboral_nuevo.institucion = experiencia_laboral_nuevo.institucion.upper()
            experiencia_laboral_nuevo.save()
            experiencia_laboral_form.save()
            return redirect('wizard_experiencia_laboral', id_entrenador)


    return render(request, 'entrenadores/wizard/wizard_experiencia_laboral.html', {
        'titulo': 'Información sobre la experiencia laboral',
        'wizard_stage': 3,
        'form': experiencia_laboral_form,
        'historicos': experiencia_laboral,
        'id_entrenador': id_entrenador
    })

@login_required
@permission_required('snd.change_entrenador')
def eliminar_experiencia_laboral(request,id_entrenador,id_experiencia):
    """
    Junio 9 / 2015
    Autor: Milton Lenis

    Eliminar un registro de experiencia laboral

    Se obtiene el registro de la experiencia laboral que se desea eliminar y se procede a eliminarlo de la base de datos.

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entrenador: Llave primaria del entrenador
    :type id_entrenador: String
    :param id_experiencia: Llave primaria de la experiencia deportiva
    :type id_experiencia: String
    """

    try:
        experiencia_laboral = ExperienciaLaboral.objects.get(id=id_experiencia, entrenador=id_entrenador)
        experiencia_laboral.delete()
        return redirect('wizard_experiencia_laboral', id_entrenador)

    except Exception:
        return redirect('wizard_experiencia_laboral', id_entrenador)



@login_required
@permission_required('snd.change_entrenador')
def desactivar_entrenador(request,id_entrenador):
    """
    Junio 9 / 2015
    Autor: Milton Lenis

    Cambiar estado de un entrenador

    Se obtiene el estado actual y se invierte su valor

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entrenador: Llave primaria del entrenador
    :type id_entrenador: String
    """
    entrenador = Entrenador.objects.get(id=id_entrenador)
    estado_actual = entrenador.estado
    entrenador.estado = not(estado_actual)
    entrenador.save()
    messages.warning(request, "Entrenador desactivado correctamente.")
    return redirect('entrenador_listar')

@login_required
def listar_entrenador(request):
    """
    Junio 9 / 2015
    Autor: Milton Lenis

    Listar entrenadores de un tenant

    Se obtienen los entrenadores y se listan

    :param request: Petición Realizada
    :type request: WSGIRequest
    """

    entrenadores = Entrenador.objects.all()
    return render(request, 'entrenadores/entrenadores_lista.html', {
        'entrenadores':entrenadores,
    })

@login_required
def ver_entrenador(request,id_entrenador):
    """
    Junio 23 /2015
    Autor: Milton Lenis

    Ver Entrenador

    Se obtiene la informacion general del entrenador desde la base de datos y se muestra

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entrenador: Llave primaria del entrenador
    :type id_entrenador: String
    """
    try:
        entrenador = Entrenador.objects.get(id=id_entrenador)
    except:
        messages.error(request, "Error: No existe el entrenador solicitado o su información es incompleta")
        return redirect('entrenador_listar')
    formacion_deportiva = FormacionDeportiva.objects.filter(entrenador=entrenador)
    experiencia_laboral = ExperienciaLaboral.objects.filter(entrenador=entrenador)
    entrenador.edad = calculate_age(entrenador.fecha_nacimiento)
    print(entrenador.edad)
    return render(request,'entrenadores/ver_entrenador.html',{
            'entrenador':entrenador,
            'formacion_deportiva':formacion_deportiva,
            'experiencia_laboral':experiencia_laboral
        })

@login_required
def verificar_entrenador(request):
    """
    Julio 24 /2015
    Autor: Milton Lenis

    Verificación de la existencia de un entrenador
    Se verifica si existe el entrenador en la entidad actual, si existe en otra entidad o si no existe.
    Dependiendo del caso se muestra una respuesta diferente al usuario

    :param request: Petición Realizada
    :type request: WSGIRequest
    """
    if request.method=='POST':
        form = VerificarExistenciaForm(request.POST)

        if form.is_valid():
            datos = {
                'tipo_id': form.cleaned_data['tipo_id'],
                'identificacion': form.cleaned_data['identificacion']
            }

            #Verificación de existencia dentro del tenant actual
            try:
                entrenador = Entrenador.objects.get(identificacion=datos['identificacion'])
            except Exception:
                entrenador = None

            if entrenador:
                #Si se encuentra el entrenador se carga el template con la existe=True para desplegar el aviso al usuario
                return render(request,'entrenadores/verificar_entrenador.html',{'existe':True,
                                                                   'entrenador':entrenador})

            if not entrenador:
                #Si no se encuentra el entrenador entonces se redirecciona a registro de entrenador con los datos iniciales en una sesión
                request.session['datos'] = datos
                return redirect('entrenador_nuevo')

            #Verificación de existencia en otros tenants
            #Estas dos variables son para ver si existe en otro tenant (True, False) y saber en cual Tenant se encontró
            existencia = False
            tenant_existencia = None
            entidades = Entidad.objects.all()
            for entidad in entidades:
                connection.set_tenant(entidad)
                ContentType.objects.clear_cache()
                try:
                    entrenador = Entrenador.objects.get(identificacion=datos['identificacion'])
                    existencia = True
                    tenant_existencia = entidad
                    break
                except Exception:
                    pass

            if existencia:
                return render(request,'entrenadores/verificar_entrenador.html',{'existe':True,
                                                                   'entrenador':entrenador,
                                                                   'tenant_existencia':tenant_existencia})
            else:
                #Si no se encuentra el entrenador entonces se redirecciona a registro de entrenador con los datos iniciales en una sesión
                request.session['datos'] = datos
                return redirect('entrenador_nuevo')

    else:
        form = VerificarExistenciaForm()
    return render(request,'entrenadores/verificar_entrenador.html',{'form':form,
                                                       'existe':False})