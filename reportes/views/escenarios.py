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
        categoria = 'caracteristicaescenario__descripcion'
    elif opcion_reporte == 'CO':
        categoria = 'comuna'
    elif opcion_reporte == 'PM':
        categoria = 'periodicidad'
    elif opcion_reporte == 'DIS':
        categoria = 'dias__nombre'

    return categoria

def obtener_choices(opcion_reporte):
    #clases_choices = CaracterizacionEscenario.ACCESOS
    if opcion_reporte == 'ES':
        clases_choices = Escenario.estratos
    elif opcion_reporte == 'CA':
        clases_choices = CaracterizacionEscenario.ACCESOS
    elif opcion_reporte == 'EF':
        clases_choices = CaracterizacionEscenario.ESTADOS_FISICOS
    elif opcion_reporte == 'TP':
        clases_choices = CaracterizacionEscenario.PROPIETARIOS
    elif opcion_reporte == 'PM':
        clases_choices = Mantenimiento.PERIODICIDADES
    else:
        clases_choices = None

    return clases_choices


def ejecutar_consulta_segun_filtro(categoria, cantidad, departamentos,municipios, disciplinas,tipoTenant, tabla, choices,ajustados=True):
    """
    Noviembre 19, 2015
    Autor: Karent Narvaez

    Permite ejecutar una consulta con base en los filtros que se están enviando en la petición.
    """
    from reportes.utilities import sumar_datos_diccionario#, convert_choices_to_array, crear_diccionario_inicial

    #Departamentos, municipios y disciplinas
    if departamentos and municipios and disciplinas:
        escenarios = tabla.objects.filter(estado=0, ciudad__departamento__id__in=departamentos, ciudad__in=municipios,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))
    #Departamentos, municipios
    elif departamentos and municipios:
        escenarios = tabla.objects.filter(estado=0,ciudad__departamento__id__in=departamentos,ciudad__in=municipios).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))
    #Departamentos, disciplinas
    elif departamentos and disciplinas:
        escenarios = tabla.objects.filter(estado=0,ciudad__departamento__id__in=departamentos,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))
    #Municipios y disciplinas
    elif municipios and disciplinas:
        escenarios = tabla.objects.filter(estado=0,ciudad__in=municipios,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))
    #Departamentos
    elif departamentos:
        escenarios = tabla.objects.filter(estado=0,ciudad__departamento__id__in=departamentos).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))

    #Municipios
    elif municipios:
        escenarios = tabla.objects.filter(estado=0,ciudad__in=municipios).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))
    #Disciplina
    elif disciplinas:
        escenarios = tabla.objects.filter(estado=0,tipodisciplinadeportiva__in=disciplinas).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))
    #Sin filtros
    else:
        escenarios =  tabla.objects.filter(estado=0).annotate(descripcion=F(categoria)).values('id','descripcion','entidad').annotate(cantidad=Count(cantidad, distinct=True))

    if choices:
        escenarios = sumar_datos_diccionario(escenarios,choices)
        return escenarios

    escenarios = tipoTenant.ajustar_resultado(escenarios) if ajustados == True else escenarios
    return escenarios



def generador_reporte_escenario(request, tabla, cantidad, categoria=None, choices=None,ajustados=True):
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
    escenarios = ejecutar_consulta_segun_filtro(categoria, cantidad, departamentos, municipios, disciplinas, tipoTenant, tabla, choices,ajustados)

    #verifica si es el reporte de comunas para escenarios y le agrega el label de comuna para el valor que muestra en la gráfica
    if reporte == 'CO':
        auxiliar_escenarios = dict()
        for key, value in escenarios.items():
            auxiliar_escenarios[("%s %s")%("Comuna ", key)] = value
        escenarios = auxiliar_escenarios

    #verifica si es el reporte de Características o por Departamentos para asignarles una visualización diferente
    #if reporte == 'CE' or reporte == 'DT':
    #    escenarios['visualizaciones'] = [1]
    #else:
    #    escenarios['visualizaciones'] = [1, 5, 6]

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

    cantidad = 'id'
    escenarios = generador_reporte_escenario(request, tabla, cantidad)
    
    

    if request.is_ajax():
        return JsonResponse(escenarios)


    visualizaciones = [1, 5 , 6]
    form = FiltrosEscenariosDMDForm(visualizaciones=visualizaciones)
    nombres_columnas = ["Clase", "Caracteristica", "Comuna", "Departamento", "Estrato", "Estado Físico", "Tipo", "Tipo Superficie", "Tipo de Propietario", "Periodicidad", "Día"]
    return render(request, 'escenarios/reporte_generador.html', {
        'nombre_reporte' : 'Clase de Acceso Escenarios',
        'nombre_generador': 'Características Escenarios',
        'url_data' : 'reportes_caracteristicas_escenarios',
        'datos': escenarios,
        'visualizaciones': visualizaciones,
        'form': form,
        'actor': 'Escenarios',
        'fecha_generado': datetime.now(),
        'nombres_columnas': nombres_columnas

    })

def cantidad_espectadores(request):
    """
    Enero 19, 2015
    Autor: Daniel Correa

    Permite mostrar la cantidad de espectadores de los escenarios categorizados por rangos
    """
    tipoTenant = request.tenant.obtenerTenant()

    if tipoTenant.schema_name == 'public':
        tabla = PublicEscenarioView
    else:
        tabla = TenantEscenarioView

    categoria = 'capacidad_espectadores'
    cantidad = 'tipo_escenario'

    escenarios = generador_reporte_escenario(request, tabla, cantidad, categoria,None,False)
    result = []
    de_uno_cien = {'id':1,'descripcion':'De 1 a 100 espectadores','cantidad':escenarios.filter(capacidad_espectadores__gte='1',capacidad_espectadores__lte='100').count()}
    result.append(de_uno_cien)
    de_cien_trecientos = {'id':2,'descripcion':'De 100 a 300 espectadores','cantidad':escenarios.filter(capacidad_espectadores__gte='101',capacidad_espectadores__lte='300').count()}
    result.append(de_cien_trecientos)
    de_trecientos_quinientos = {'id':3,'descripcion':'De 300 a 500 espectadores','cantidad': escenarios.filter(capacidad_espectadores__gte='301',capacidad_espectadores__lte='500').count()}
    result.append(de_trecientos_quinientos)
    de_quinientos_dosmil= {'id':4,'descripcion':'De 500 a 2000 espectadores','cantidad':escenarios.filter(capacidad_espectadores__gte='501',capacidad_espectadores__lte='2000').count()}
    result.append(de_quinientos_dosmil)
    de_dosmil_cincomil= {'id':5,'descripcion':'De 2000 a 5000 espectadores','cantidad':escenarios.filter(capacidad_espectadores__gte='2001',capacidad_espectadores__lte='5000').count()}
    result.append(de_dosmil_cincomil)
    mas_de_cincomil= {'id':6,'descripcion':'Mas de 5000 espectadores','cantidad':escenarios.filter(capacidad_espectadores__gte='5000').count()}
    result.append(mas_de_cincomil)
    result = tipoTenant.ajustar_resultado(result)
    if request.is_ajax():
        return JsonResponse(result)

    visualizaciones = [1, 5 , 6]

    form = FiltrosEscenariosDMDForm(visualizaciones=visualizaciones, eliminar='reporte')
    nombres_columnas = ["Cantidad Espectadores"]
    return render(request, 'escenarios/reporte_sencillo.html', {
        'nombre_reporte' : 'Número de escenarios deportivos por espectadores habituales',
        'url_data' : 'reporte_cantidad_espectadores',
        'datos': result,
        'visualizaciones': visualizaciones,
        'form': form,
        'actor': 'Escenarios',
        'fecha_generado': datetime.now(),
        'nombres_columnas': nombres_columnas
    })