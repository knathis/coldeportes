from django import forms
from entidades.models import Departamento, Ciudad
from coldeportes.utilities import adicionarClase
from reportes.utilities import add_visualizacion


class EscuelasForm(forms.Form):
    def __init__(self, *args, **kwargs):
        visualizaciones_definidas = kwargs.pop('visualizaciones', None)
        super(EscuelasForm, self).__init__(*args, **kwargs)
        self.fields['departamentos'] = adicionarClase(self.fields['departamentos'], 'many')
        self.fields['municipios'] = adicionarClase(self.fields['municipios'], 'many')
        self.fields['visualizacion'] = adicionarClase(self.fields['visualizacion'], 'one')

        add_visualizacion(self.fields['visualizacion'], visualizaciones_definidas)

    departamentos = forms.ModelMultipleChoiceField(queryset=Departamento.objects.all(), required=False)
    municipios = forms.ModelMultipleChoiceField(queryset=Ciudad.objects.all(), required=False)
    visualizacion = forms.ChoiceField(label='Visualización')