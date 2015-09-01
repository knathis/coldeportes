from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from snd.formularios.selecciones import *
from django.contrib import messages
from snd.models import *
from entidades.models import *
from django.http import JsonResponse

@login_required
def registrar_base(request):
    """
    Agosto 29 / 2015
    Autor: Daniel Correa

    Permite guardar la primera seccion de la seleccion dando paso a la seleccion de deportistas y personal de apoyo

    :param request: Petición Realizada
    :type request: WSGIRequest
    """

    form = SeleccionForm(initial={'tipo':request.tenant.tipo})

    if request.method == 'POST':
        form = SeleccionForm(request.POST,initial={'tipo':request.tenant.tipo})
        if form.is_valid():
            sele = form.save()
            return redirect('registrar_deportistas',sele.id)

    return render(request,'selecciones/wizard/wizard_seleccion.html',{
        'titulo': 'Selección',
        'form': form,
        'wizard_stage': 1
    })

@login_required
def editar_base(request,id_s):
    """
    Agosot 31 /2015
    Autor: Daniel Correa

    Permite editar los datos basicos de una seleccion

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_s: id de la seleccion a editar
    """

    try:
        sele = Seleccion.objects.get(id=id_s)
    except:
        messages.error(request,'No existe la selección ingresada')
        return redirect('listar_seleccion')

    form = SeleccionForm(instance=sele,initial={'tipo':request.tenant.tipo})

    if request.method == 'POST':
        form = SeleccionForm(request.POST,instance=sele,initial={'tipo':request.tenant.tipo})
        if form.is_valid():
            form.save()
            return redirect('registrar_deportistas',sele.id)

    return render(request,'selecciones/wizard/wizard_seleccion.html',{
        'titulo': 'Selección',
        'form': form,
        'wizard_stage': 1
    })

@login_required
def registrar_deportistas(request,id_s):
    """
    Agosto 31 / 2015
    Autor: Daniel Correa

    Permite registrar los deportistas de una seleccion

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_s: id de la seleccion a la cual asignar deportistas
    :type id_s: string
    """

    try:
        sele = Seleccion.objects.get(id=id_s)
    except:
        messages.error(request,'No existe la selección solicitada')
        return redirect('listar_seleccion')

    deportistas = []
    if request.tenant.tipo == 1:
        #Liga
        clubes = Club.objects.filter(liga=request.tenant.id)
        for c in clubes:
            connection.set_tenant(c)
            ContentType.objects.clear_cache()
            deportistas += Deportista.objects.filter(estado=0)
        connection.set_tenant(request.tenant)
    elif request.tenant.tipo == 2:
        #Fede
        ligas = Liga.objects.filter(federacion=request.tenant.id)
        for l in ligas:
            clubes = Club.objects.filter(liga=l)
            for c in clubes:
                connection.set_tenant(c)
                ContentType.objects.clear_cache()
                deportistas += Deportista.objects.filter(estado=0)
        connection.set_tenant(request.tenant)
    else:
        messages.error(request,'Usted esta en una sección que no le corresponde')
        return redirect('inicio_tenant')

    depor_registrados = []
    for d in DeportistasSeleccion.objects.filter(seleccion=sele): #Obtener deportistas seleccionados al momento
        entidad = d.entidad
        depor = d.deportista
        connection.set_tenant(entidad)
        ContentType.objects.clear_cache()
        depor_registrados += [Deportista.objects.get(id=depor)]

    for depo in depor_registrados: #Quitar de la lista de deportistas los que ya estan registrados
        if depo in deportistas:
            deportistas.remove(depo)

    return render(request,'selecciones/wizard/wizard_seleccion_deportistas.html',{
        'titulo': 'Selección de Deportistas',
        'wizard_stage': 2,
        'deportistas': deportistas,
        'sele_id': sele.id,
        'depor_registrados': depor_registrados
    })

@login_required
def registrar_personal(request,id_s):
    """
    Agosto 31 / 2015
    Autor: Daniel Correa

    Permite seleccionar el personal de apoyo de la seleccion

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_s: id de la seleccion
    """
    try:
        sele = Seleccion.objects.get(id=id_s)
    except:
        messages.error(request,'No existe la selección solicitada')
        return redirect('listar_seleccion')

    personal = []
    if request.tenant.tipo == 1:
        #Liga
        clubes = Club.objects.filter(liga=request.tenant.id)
        for c in clubes:
            connection.set_tenant(c)
            ContentType.objects.clear_cache()
            personal += PersonalApoyo.objects.filter(estado=0)
        connection.set_tenant(request.tenant)
    elif request.tenant.tipo == 2:
        #Fede
        ligas = Liga.objects.filter(federacion=request.tenant.id)
        for l in ligas:
            clubes = Club.objects.filter(liga=l)
            for c in clubes:
                connection.set_tenant(c)
                ContentType.objects.clear_cache()
                personal += PersonalApoyo.objects.filter(estado=0)
        connection.set_tenant(request.tenant)
    else:
        messages.error(request,'Usted esta en una sección que no le corresponde')
        return redirect('inicio_tenant')

    personal_registrados = []
    for d in PersonalSeleccion.objects.filter(seleccion=sele): #Obtener personal seleccionado al momento
        entidad = d.entidad
        per = d.personal
        connection.set_tenant(entidad)
        ContentType.objects.clear_cache()
        personal_registrados += [PersonalApoyo.objects.get(id=per)]

    for person in personal_registrados: #Quitar de la lista de personal los que ya estan registrados
        if person in personal:
            personal.remove(person)

    return render(request,'selecciones/wizard/wizard_seleccion_personal.html',{
        'titulo': 'Selección de Personal de Apoyo',
        'wizard_stage': 3,
        'personal': personal,
        'sele_id': sele.id,
        'personal_registrados': personal_registrados
    })


@login_required
def listar_seleccion(request):
    """
    Agosto 30 / 2015
    Autor: Daniel Correa

    Permite listar todas las selecciones con la estrategia de cargue masivo

    :param request: Petición Realizada
    :type request: WSGIRequest
    """

    selecciones = Seleccion.objects.all()

    return render(request,'selecciones/listar_selecciones.html',{
        'selecciones': selecciones
    })

@login_required
def ver_seleccion(request,id_s):
    return redirect('listar_seleccion')

@login_required
def finalizar_registro_seleccion(request):
    """
    Agosto 31 / 2015
    Autor: Daniel Correa

    Permite hacer la redireccion con mensaje y posible redireccion a nueva seleccion

    :param request: Petición Realizada
    :type request: WSGIRequest
    """

    messages.success(request,'Selección registrada exitosamente')
    return redirect('listar_seleccion')
#AJAX SELECCIONES

#AJAX SELECCION DE DEPORTISTAS
@login_required
def vista_previa_deportista(request,id_entidad,id_depor):
    """
    Agosto 31 / 2015
    Autor: Daniel Correa

    Permite obtener la vista previa del deportista a seleccionar

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entidad: id entidad a traer deportista
    :param id_depor: id deportistas a mostrar
    """
    try:
        ent = Entidad.objects.get(id=id_entidad)
    except:
        messages.error(request,'Entidad no encontrada')
        return redirect('listar_seleccion')

    connection.set_tenant(ent)
    ContentType.objects.clear_cache()

    try:
        depor = Deportista.objects.get(id=id_depor)
    except:
        messages.error(request,'Deportista no existe')
        return redirect('listar_seleccion')

    return render(request,'selecciones/wizard/ajax_seleccion_deportistas/vista_previa.html',{
        'deportista': depor
    })

@login_required
def seleccionar_deportista(request,id_s,id_entidad,id_depor):
    """
    Agosto 31 / 2015
    Autor: Daniel Correa

    Permite guardar los deportistas seleccionados de la seleccion id_s

    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_s: id de la seleccion
    :param id_entidad: id de la entidad del deportista
    :param id_depor: id del deportista
    """
    try:
        ent = Entidad.objects.get(id=id_entidad)
    except:
        messages.error(request,'Entidad no encontrada')
        return redirect('listar_seleccion')

    connection.set_tenant(ent)
    ContentType.objects.clear_cache()

    try:
        depor = Deportista.objects.get(id=id_depor)
    except:
        messages.error(request,'Deportista no existe')
        return redirect('listar_seleccion')

    connection.set_tenant(request.tenant)

    try:
        sele = Seleccion.objects.get(id=id_s)
    except:
        messages.error(request,'No existe la seleccion solicitada')
        return redirect('listar_seleccion')

    depor_sele = DeportistasSeleccion(deportista=depor.id,entidad=ent,seleccion=sele)
    depor_sele.save()

    return JsonResponse({
        'respuesta': [depor.nombres + ' ' +depor.apellidos,depor.tipo_id,depor.identificacion,depor.edad(),depor.ciudad_residencia.__str__(),depor.entidad.nombre,]
    })

#AJAX SELECCION DE PERSONAL DE APOYO
@login_required
def vista_previa_personal(request,id_entidad,id_personal):
    """
    Agosto 31 / 2015
    Autor: Daniel Correa

    Permite visualizar una vista previa del personal de apoyo seleccionado
    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_entidad: id de la entidad donde esta el personal
    :param id_personal: id del personal de apoyo
    """

    try:
        ent = Entidad.objects.get(id=id_entidad)
    except:
        messages.error(request,'Entidad no encontrada')
        return redirect('listar_seleccion')

    connection.set_tenant(ent)
    ContentType.objects.clear_cache()

    try:
        per = PersonalApoyo.objects.get(id=id_personal)
    except:
        messages.error(request,'Personal no existe')
        return redirect('listar_seleccion')

    return render(request,'selecciones/wizard/ajax_seleccion_personalapoyo/vista_previa.html',{
        'per': per
    })

@login_required
def seleccionar_personal(request,id_s,id_entidad,id_personal):
    """
    Agosto 31 /2015
    Autor: Daniel Correa

    Permite guardar el personal de apoyo de la seleccion id_s
    :param request: Petición Realizada
    :type request: WSGIRequest
    :param id_s: id de la seleccion a guardar el personal
    :param id_entidad: id de la entidad a la cual pertente el personal
    :param id_personal: id del personal de apoyo
    """
    try:
        ent = Entidad.objects.get(id=id_entidad)
    except:
        messages.error(request,'Entidad no encontrada')
        return redirect('listar_seleccion')

    connection.set_tenant(ent)
    ContentType.objects.clear_cache()

    try:
        per = PersonalApoyo.objects.get(id=id_personal)
    except:
        messages.error(request,'Personal no existe')
        return redirect('listar_seleccion')

    connection.set_tenant(request.tenant)

    try:
        sele = Seleccion.objects.get(id=id_s)
    except:
        messages.error(request,'No existe la seleccion solicitada')
        return redirect('listar_seleccion')

    per_sele = PersonalSeleccion(personal=per.id,entidad=ent,seleccion=sele)
    per_sele.save()

    return JsonResponse({
        'respuesta': [per.nombres + ' ' +per.apellidos,per.tipo_id,per.identificacion,per.actividad,per.ciudad.__str__(),per.entidad.nombre]
    })
