from django import forms
from django.forms import ModelForm
from snd.models import *
from datetimewidget.widgets import DateWidget
from coldeportes.utilities import adicionarClase


class DirigenteVerificarExistenciaForm(forms.Form):
    """TIPO_IDENTIDAD = (
        ('CED', 'CÉDULA DE CIUDADANÍA'),
        ('CEDEX', 'CÉDULA DE EXTRANJERO'),
        ('PAS', 'PASAPORTE'),
    )
    tipo_id = forms.ChoiceField(choices=TIPO_IDENTIDAD)"""
    identificacion = forms.CharField(label="Identificación del dirigente")

class DirigenteForm(ModelForm):

    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(DirigenteForm, self).__init__(*args, **kwargs)
        self.fields['nacionalidad'] = adicionarClase(self.fields['nacionalidad'], 'many')
        self.fields['ciudad_residencia'] = adicionarClase(self.fields['ciudad_residencia'], 'one')
        self.fields['perfil'].widget.attrs['rows'] = 3


    class Meta:
        model = Dirigente
        #fields = '__all__'
        exclude = ('entidad', 'estado',)

class DirigenteCargosForm(ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        dirigente_id = kwargs.pop('dirigente_id', False)
        super(DirigenteCargosForm, self).__init__(*args, **kwargs)
        self.fields['superior'] = adicionarClase(self.fields['superior'], 'one')
        self.fields['fecha_retiro'] = adicionarClase(self.fields['fecha_retiro'], 'fecha')
        self.fields['fecha_posesion'] = adicionarClase(self.fields['fecha_posesion'], 'fecha')
        if dirigente_id:
            self.fields['superior'].queryset = Dirigente.objects.exclude(id=dirigente_id)

    class Meta:
        model = DirigenteCargo
        exclude = ('dirigente',)

class DirigenteFuncionesForm(ModelForm):

    required_css_class = 'required'
    dirigente = forms.CharField()

    def __init__(self, *args, **kwargs):
        dirigente_id = kwargs.pop('dirigente_id', False)
        super(DirigenteFuncionesForm, self).__init__(*args, **kwargs)
        if dirigente_id:
            self.fields['cargo'].queryset=DirigenteCargo.objects.filter(dirigente=dirigente_id)
            self.fields['dirigente'].widget = forms.HiddenInput()
            self.fields['dirigente'].initial = dirigente_id

    class Meta:
        model = DirigenteFuncion
        exclude = ('dirigente',)