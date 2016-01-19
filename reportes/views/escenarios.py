#encoding:utf-8
from django.shortcuts import render, redirect
from django.http import JsonResponse
import ast
from datetime import datetime
from django.db.models import F, Count
from entidades.modelos_vistas_reportes import PublicEscenarioView
from reportes.formularios.escenarios import FiltrosEscenariosDMDForm, FiltrosEscenariosComunasForm
from reportes.models import TenantEscenarioView
from snd.modelos.escenarios import *

'''
Reportes:
    1. Dona
    2. Comparativa Horizontal
    3. Comparativa Vertical
    4. Tree Map
    5. Gráfica de cilindros
    6. Gráfica de cono
    7. Gráfica de radar
'''
def verificar_seleccion_reporte(opcion_reporte):
    categoria = 'clase_acceso'
    if opcion_reporte == 'ES':
        categoria = 'estrato'
    elif opcion_reporte == 'CA':
        categoria = 'clase_acceso'
    elif opcion_reporte == 'DT':
        categoria = 'ciudad__departamento__nombre'
    elif opcion_reporte == 'EF':
        categoria = 'estado_fisico'
    elif opcion_reporte == 'TE':
        categoria = 'tipo_escenario__descripcion'
    elif opcion_reporte == 'TS':
        categoria = 'tiposuperficie__descripcion'
    elif opcion_reporte == 'TP':
        categoria = 'tipo_propietario'
    elif opcion_reporte == 'CE':
        categoria = 'capacidad_espectadores'

    return categoria

def obtener_choices(opcion_reporte):
    #clases_choices = CaracterizacionEscenario.ACCESOS
    if opcion_reporte == 'ES':
        clases_choices = Escenario.estratos
    elif opcion_reporte == 'CA':
        clases_choices = CaracterizacionEscenario.ACCESOS
    elif opcion_reporte == 'EF':
        clases_choices = CaracterizacionEs0cenario.ESTADOS_FISICOS
    elif opcion_reporte == 'TP':
        clases_choices = CaracterizacionEscenario.PROPIETARIOS
    else:
        clases_choices = None

    return clases_choices


def ejecutar_consulta_segun_filtro(categoria, cantidad, departamentos,municipios, disciplinas,tipoTenant, tabla, choices):
    """
    Noviembre 19, 2015
    Autor: Karent Narvaez

    Permite ejecutar una consulta con base en los filtros que se están enviando en la petición.
    """
    from reportes.utilities import sumar_datos_diccionario#, convert_choices_to_array, crear_diccionario_inicial

    #Departamentos, municipios y disciplinas
    if departamentos and municipios and disciplinas:
        escenarios = tabla.objects.filter(estado=0, ciudad__departamento__id__in=departamentos, ciudad__in=municipios,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))
    #Departamentos, municipios
    elif departamentos and municipios:
        escenarios = tabla.objects.filter(estado=0,ciudad__departamento__id__in=departamentos,ciudad__in=municipios).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))
    #Departamentos, disciplinas
    elif departamentos and disciplinas:
        escenarios = tabla.objects.filter(estado=0,ciudad__departamento__id__in=departamentos,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))
    #Municipios y disciplinas
    elif municipios and disciplinas:
        escenarios = tabla.objects.filter(estado=0,ciudad__in=municipios,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))
    #Departamentos
    elif departamentos:
        escenarios = tabla.objects.filter(estado=0,ciudad__departamento__id__in=departamentos).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))

    #Municipios
    elif municipios:
        escenarios = tabla.objects.filter(estado=0,ciudad__in=municipios).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))
    #Disciplina
    elif disciplinas:
        escenarios = tabla.objects.filter(estado=0,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))
    #Sin filtros
    else:
        escenarios =  tabla.objects.filter(estado=0).annotate(descripcion=F(categoria)).values('id','descripcion').annotate(cantidad=Count(cantidad, distinct=True))
    print(escenarios.query)
    if choices:
        escenarios = sumar_datos_diccionario(escenarios,choices)
        return escenarios

    escenarios = tipoTenant.ajustar_resultado(escenarios)
    return escenarios



def generador_reporte_escenario(request, tabla, cantidad, categoria=None, choices=None):
    from coldeportes.utilities import get_request_or_none
    tipoTenant = request.tenant.obtenerTenant()

    departamentos = None
    municipios = None
    disciplinas = None
    reporte = None

    if request.is_ajax():
        departamentos = get_request_or_none(request.GET, 'departamentos')
        municipios = get_request_or_none(request.GET, 'municipios')
        disciplinas = get_request_or_none(request.GET, 'disciplinas')
        reporte = get_request_or_none(request.GET, 'reporte')
    
    if not categoria and not request.is_ajax():
        #por default carga el reporte de Clase de accesos
        reporte = 'CA'
    if not categoria:
    #si categoria es none es el reporte características escenarios        
        categoria = verificar_seleccion_reporte(reporte)

    choices = obtener_choices(reporte)
    escenarios = ejecutar_consulta_segun_filtro(categoria, cantidad, departamentos, municipios, disciplinas, tipoTenant, tabla, choices)

    if '' in escenarios:
        escenarios['Ninguna'] = escenarios['']
        del escenarios['']

    return escenarios


def caracteristicas_escenarios(request):
    """
    Noviembre 19, 2015
    Autor: Karent Narvaez

    Permite conocer el numero de escenarios por cada tipo de escenarios.
    """
    tipoTenant = request.tenant.obtenerTenant()

    if tipoTenant.schema_name == 'public':
        tabla = PublicEscenarioView
    else:
        tabla = TenantEscenarioView
    
    cantidad = 'tipo_escenario'
    escenarios = generador_reporte_escenario(request, tabla, cantidad)

    if request.is_ajax():
        return JsonResponse(escenarios)
        
    visualizaciones = [1, 5 , 6]
    form = FiltrosEscenariosDMDForm(visualizaciones=visualizaciones)
    return render(request, 'escenarios/base_escenario.html', {
        'nombre_reporte' : 'Clase de Acceso Escenarios',
        'url_data' : 'reportes_caracteristicas_escenarios',
        'datos': escenarios,
        'visualizaciones': visualizaciones,
        'form': form,
        'actor': 'Escenarios',
        'fecha_generado': datetime.now()
    })

def periodicidad_mantenimiento(request):
    """
    Noviembre 22, 2015
    Autor: Cristian Leonardo Ríos López

    Permite conocer el numero de escenarios por su periodicidad de mantenimiento
    """
    tipoTenant = request.tenant.obtenerTenant()

    if tipoTenant.schema_name == 'public':
        tabla = PublicEscenarioView
    else:
        tabla = TenantEscenarioView

    categoria = 'periodicidad'
    cantidad = 'periodicidad'

    escenarios = generador_reporte_escenario(request, tabla, cantidad, categoria, Mantenimiento.PERIODICIDADES)

    if request.is_ajax():
        return JsonResponse(escenarios)

    visualizaciones = [1, 5 , 6]

    form = FiltrosEscenariosDMDForm(visualizaciones=visualizaciones, eliminar='reporte')
    return render(request, 'escenarios/base2_escenario.html', {
        'nombre_reporte' : 'Periodicidad de mantenimiento de Escenarios',
        'url_data' : 'reportes_escenarios_periodicidad_mantenimiento',
        'datos': escenarios,
        'visualizaciones': visualizaciones,
        'form': form,
        'actor': 'Escenarios',
        'fecha_generado': datetime.now()
    })

def disponibilidad_escenarios(request):
    """
    Noviembre 21, 2015
    Autor: Milton Lenis

    Permite conocer los días de disponibilidad de los escenarios
    """
    tipoTenant = request.tenant.obtenerTenant()

    if tipoTenant.schema_name == 'public':
        tabla = PublicEscenarioView
    else:
        tabla = TenantEscenarioView

    categoria = 'dias__nombre'
    cantidad = 'dias'

    escenarios = generador_reporte_escenario(request, tabla, cantidad, categoria)

    if request.is_ajax():
        return JsonResponse(escenarios)

    visualizaciones = [1,2,3,5,6,7]
    form = FiltrosEscenariosDMDForm(visualizaciones=visualizaciones, eliminar='reporte')
    return render(request, 'escenarios/base2_escenario.html', {
        'nombre_reporte' : 'Días de disponibilidad de los escenarios',
        'url_data' : 'reportes_disponibilidad_escenarios',
        'datos': escenarios,
        'visualizaciones': visualizaciones,
        'form': form,
        'actor': 'Escenarios',
        'fecha_generado': datetime.now()
    })



def clase_escenarios(request):
    """
    Enero 15, 2015
    Autor: Karent Narvaez

    Permite conocer la cantidad de escenarios en cada clase determinada.
    """
    tipoTenant = request.tenant.obtenerTenant()

    if tipoTenant.schema_name == 'public':
        tabla = PublicEscenarioView
    else:
        tabla = TenantEscenarioView

    categoria = 'caracteristicas__descripcion'
    cantidad = 'caracteristicas'

    escenarios = generador_reporte_escenario(request, tabla, cantidad, categoria)

    if request.is_ajax():
        return JsonResponse(escenarios)

    visualizaciones = [1,2,3,5,6,7]
    form = FiltrosEscenariosDMDForm(visualizaciones=visualizaciones, eliminar='reporte')
    return render(request, 'escenarios/base2_escenario.html', {
        'nombre_reporte' : 'Clases de Escenario',
        'url_data' : 'reportes_clase_escenarios',
        'datos': escenarios,
        'visualizaciones': visualizaciones,
        'form': form,
        'actor': 'Escenarios',
        'fecha_generado': datetime.now()
    })

def comunas_escenarios(request):
    from coldeportes.utilities import get_request_or_none

    tipoTenant = request.tenant.obtenerTenant()

    if tipoTenant.schema_name == 'public':
        tabla = PublicEscenarioView
    else:
        tabla = TenantEscenarioView

    municipios = None
    disciplinas = None

    if request.is_ajax():
        municipios = get_request_or_none(request.GET, 'municipios')
        if municipios != None:
            municipios = [municipios]
        disciplinas = get_request_or_none(request.GET, 'disciplinas')

    escenarios = ejecutar_consulta_segun_filtro('comuna', 'comuna', None, municipios, disciplinas, tipoTenant, tabla, None)
    aux_esc = dict()
    for k, v in escenarios.items():
        aux_esc[("%s %s")%("Comuna ", k)] = v
    escenarios = aux_esc

    if request.is_ajax():
        return JsonResponse(escenarios)

    visualizaciones = [1,2,3,5,6,7]
    form = FiltrosEscenariosComunasForm(visualizaciones=visualizaciones)
    return render(request, 'escenarios/base_escenario.html', {
        'nombre_reporte' : 'Escenarios por comunas',
        'url_data' : 'reportes_escenarios_comunas',
        'datos': escenarios,
        'visualizaciones': visualizaciones,
        'form': form,
        'actor': 'Escenarios',
        'fecha_generado': datetime.now()
    })