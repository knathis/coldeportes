from django import forms
from coldeportes.utilities import MyDateWidget

from .models import Clasificado


class ClasificadoForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Clasificado
        fields = ('categoria', 'fecha_publicacion', 'fecha_expiracion', 'titulo', 'descripcion', 'contacto', 'valor',
                  'archivo_adjunto', 'etiquetas')

        widgets = {
            'fecha_publicacion': MyDateWidget(),
            'fecha_expiracion': MyDateWidget()
        }


class CropForm(forms.Form):
    """Django form for accepting the information passed after cropping a loaded
    image
    """
    imgUrl = forms.CharField()               # your image path (the one we received after successful upload)
    imgInitW = forms.DecimalField()          # your image original width (the one we received after upload)
    imgInitH = forms.DecimalField()          # your image original height (the one we received after upload)
    imgW = forms.DecimalField()              # your new scaled image width
    imgH = forms.DecimalField()              # your new scaled image height
    imgX1 = forms.DecimalField()             # top left corner of the cropped image in relation to scaled image
    imgY1 = forms.DecimalField()             # top left corner of the cropped image in relation to scaled image
    cropW = forms.DecimalField()             # cropped image width
    cropH = forms.DecimalField()             # cropped image height
    rotation = forms.IntegerField()          # cropped image rotation
