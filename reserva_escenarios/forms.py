#-*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from coldeportes.utilities import adicionarClase
from reserva_escenarios.models import ReservaEscenario, ConfiguracionReservaEscenario


class SolicitarReservaForm(ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(SolicitarReservaForm, self).__init__(*args, **kwargs)
        self.fields['descripcion'].widget.attrs['rows'] = 3

    class Meta:
        model = ReservaEscenario
        exclude = ('escenario', 'aprobada', 'fecha_inicio', 'fecha_fin', 'estado', 'comentarios_respuesta', 'usuario_respuesta')


class ConfiguracionReservaEscenarioForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = ConfiguracionReservaEscenario
        exclude = ('escenario',)


class ResponderSolicitudReservaForm(ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(ResponderSolicitudReservaForm, self).__init__(*args, **kwargs)
        self.fields['comentarios_respuesta'].widget.attrs['rows'] = 3

    class Meta:
        model = ReservaEscenario
        fields = ('estado', 'comentarios_respuesta')