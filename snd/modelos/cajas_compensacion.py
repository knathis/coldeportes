#encoding:utf-8

from entidades.models import *
from django.db import models
from django.conf import settings
import os


class CajaCompensacion(models.Model):

    def foto_caja(instance, filename):
        ruta = 'fotos_cajas/' + str(instance.id) + filename[-4:]
        ruta_delete = settings.MEDIA_ROOT + "/" + ruta
        if(os.path.exists(ruta_delete)):
            os.remove(ruta_delete)
        return ruta


    tipo_estado = ((0,'ACTIVO'), (1,'INACTIVO'),)
    clases = ( ('G', 'Grande'), ('M', 'Mediana'), ('P', 'Pequeña'), )
    tipo_region = ( ('U', 'Urbano'), ('R', 'Rural'), )
    tipo_infraesctructura = ( ('P', 'Propia'), ('C', 'Convenio'), )
    tipo_publicos = ( ('A', 'Afiliados'), ('N', 'No Afiliados'), )
    tipo_instituciones = ( ('Pr', 'Privada'), ('Pu', 'Pública'), )

    nombre =  models.CharField(max_length=100)    
    nombre_contacto =  models.CharField(max_length=50)
    clasificacion = models.CharField(choices=clases, max_length=1, verbose_name='clasificación')
    region = models.CharField(choices=tipo_region, max_length=1, verbose_name='región')
    tipo_institucion = models.CharField(choices=tipo_instituciones, max_length=2, verbose_name='tipo de institución')
    telefono_contacto = models.CharField(max_length=20, verbose_name='teléfono de contacto')
    publico = models.CharField(choices=tipo_publicos, max_length=1, verbose_name='público')
    email = models.EmailField()
    ciudad = models.ForeignKey(Ciudad)
    infraestructura = models.CharField(choices=tipo_infraesctructura, max_length=1)
    foto = models.ImageField(upload_to=foto_caja, null=True, blank=True)
    servicios = models.ManyToManyField(TipoServicioCajaCompensacion)
    entidad = models.ForeignKey(Entidad)    
    estado = models.IntegerField(choices=tipo_estado)
    descripcion = models.TextField(verbose_name='descripción', null=True, blank=True)
    #fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
                ("view_cajacompensacion", "Permite ver caja compensacion"),
            )


class HorarioDisponibilidadCajas(models.Model):
    caja_compensacion = models.ForeignKey(CajaCompensacion)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    dias = models.ManyToManyField(Dias)
    descripcion = models.CharField(max_length=1024, verbose_name='descripción')

class Tarifa(models.Model):
    caja_compensacion = models.ForeignKey(CajaCompensacion)
    titulo = models.CharField(max_length=100)
    precio = models.PositiveIntegerField()
    descripcion = models.TextField(verbose_name='descripción', null=True)
