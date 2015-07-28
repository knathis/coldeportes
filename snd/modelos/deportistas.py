#encoding:utf-8

from entidades.models import *
from django.db import models


class Deportista(models.Model):
    #Datos personales
        #Identificacion
    tipo_sexo = (
        ('Hombre','Hombre'),
        ('Mujer','Mujer'),
        ('LGTBI', 'LGTBI'),
    )
    TIPO_IDENTIDAD = (
        ('TI', 'Tarjeta de Identidad'),
        ('CC', 'Cédula de ciudadanía'),
        ('CCEX', 'Cédula de extranjero'),
        ('PASS', 'Pasaporte'),
    )
    ESTADOS = (
        (0,'ACTIVO'),
        (1,'INACTIVO'),
        (2,'EN TRANSFERENCIA'),
        (3,'TRANSFERIDO'),
    )

    ETNIAS = (
        ('MESTIZO','MESTIZO'),
        ('AFROCOLOMBIANO','AFROCOLOMBIANO'),
        ('BLANCOS','BLANCOS'),
        ('COLOMBOINDIGENA','COLOMBOINDIGENA'),
        ('GITANO','GITANO'),
    )

    nombres = models.CharField(max_length=100, verbose_name='Nombres *')
    apellidos = models.CharField(max_length=100,verbose_name='Apellidos *')
    genero = models.CharField(choices=tipo_sexo,max_length=11, verbose_name='Genero del Deportista *',default='Hombre')
    tipo_id = models.CharField(max_length=10, choices=TIPO_IDENTIDAD, default='CC',verbose_name='Tipo de Identificación *')
    identificacion = models.CharField(max_length=100,unique=True,verbose_name='Identificación *')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de nacimiento *')
    ciudad_residencia = models.ForeignKey(Ciudad, verbose_name='Ciudad en donde esta residiendo *')
    barrio = models.CharField(max_length=100,verbose_name='Barrio *')
    comuna = models.CharField(max_length=100,verbose_name='Comuna *')
    email = models.EmailField(null=True,blank=True)
    telefono = models.CharField(max_length=100,verbose_name='Telefono *')
    direccion = models.CharField(max_length=100,verbose_name='Direccion *')
    entidad = models.ForeignKey(Entidad)

    estado = models.IntegerField(choices=ESTADOS, default=0, verbose_name="estado del Deportista")
    etnia = models.CharField(max_length=20, choices=ETNIAS,blank=True)

    video = models.URLField(max_length=1024, verbose_name='Video', null=True, blank=True)
    disciplinas = models.ManyToManyField(TipoDisciplinaDeportiva,verbose_name='Disciplinas Deportivas *')
    nacionalidad = models.ManyToManyField(Nacionalidad,verbose_name='Nacionalidad *')
    foto = models.ImageField(upload_to='fotos_deportistas', null=True, blank=True)
    etnia = models.CharField(max_length=20, choices=ETNIAS,blank=True)

    def __str__(self):
        return self.nombres+" "+self.apellidos

    def __str__(self):
        return self.nombres+" "+self.apellidos

#Composicion corporal
class ComposicionCorporal(models.Model):
    tipos_rh =(
        ('A+','A+'),
        ('A-','A-'),
        ('B+','B+'),
        ('B-','B-'),
        ('AB+','AB+'),
        ('AB-','AB-'),
        ('O+','O+'),
        ('O-','O-'),
    )
    tipos_talla_choices = (
        ('Niño','Niño'),
        ('Adulto','Adulto'),
    )
    tallas_choices = (
        ('XS','XS'),
        ('S','S'),
        ('M','M'),
        ('L','L'),
        ('XL','XL'),
        ('XXL','XXL'),
    )
    deportista = models.ForeignKey(Deportista)
    peso = models.FloatField(help_text="En kg", verbose_name="Peso (kg) *")
    estatura = models.IntegerField(help_text="En cm", verbose_name="Estatura (cm) *")
    RH = models.CharField(max_length=4,choices=tipos_rh,default='O+',verbose_name='Tipo de sangre *')
    tipo_talla = models.CharField(max_length=7,choices=tipos_talla_choices,default='Adulto',verbose_name='Talla para *')
    talla_camisa = models.CharField(max_length=3, choices=tallas_choices,verbose_name='Talla Camisa *')
    talla_pantaloneta = models.CharField(max_length=3, choices=tallas_choices,verbose_name='Talla Pantaloneta *')
    talla_zapato = models.CharField(max_length=2,verbose_name='Talla Zapato *')
    porcentaje_grasa = models.CharField(max_length=7,verbose_name='Porcentaje Grasa *')
    porcentaje_musculo = models.CharField(max_length=7,verbose_name='Porcentaje Musculo *')


#Hitorial deportivo
class HistorialDeportivo(models.Model):
    tipo_his_deportivo=(
        ('Competencia','Competencia'),
        ('Logro Deportivo','Logro Deportivo'),
        ('Participacion en Equipo','Participacion en Equipo'),
        ('Premio','Premio'),
    )
    fecha_inicial = models.DateField(verbose_name='Fecha Iniciación *')
    fecha_final = models.DateField(blank=True, null=True,verbose_name='Fecha Finalización ')
    actual = models.BooleanField(verbose_name='¿Actualmente?',default=False)
    lugar = models.CharField(max_length=100,verbose_name='Lugar de desarrollo *')
    descripcion = models.CharField(max_length=1024, verbose_name='Descripción', null=True,blank=True)
    institucion_equipo = models.CharField(max_length=100,blank=True,null=True, verbose_name='Club deportivo')
    tipo = models.CharField(choices=tipo_his_deportivo,max_length=100,verbose_name='Tipo Historial *',default='Competencia')
    deportista = models.ForeignKey(Deportista)

#Informacion academica
class InformacionAcademica(models.Model):
    tipo_academica = (
        ('Jardin','Jardin'),
        ('Primaria','Primaria'),
        ('Bachillerato','Bachillerato'),
        ('Pregrado','Pregrado'),
        ('Postgrado','Postgrado'),
    )
    tipo_estado = (
        ('Actual','Actual'),
        ('Finalizado','Finalizado'),
        ('Incompleto','Incompleto'),
    )
    pais = models.ForeignKey(Nacionalidad,verbose_name='País *')
    institucion = models.CharField(max_length=100,verbose_name='Institución *')
    nivel = models.CharField(choices=tipo_academica,max_length=20,verbose_name='Nivel *')
    estado = models.CharField(choices=tipo_estado,max_length=20,verbose_name='Estado *')
    profesion =  models.CharField(max_length=100,blank=True,null=True)
    grado_semestre = models.IntegerField(verbose_name='Grado, Año o Semestre', null=True, blank=True)
    fecha_finalizacion = models.IntegerField(blank=True,null=True,verbose_name='Año Finalización')
    deportista = models.ForeignKey(Deportista)

