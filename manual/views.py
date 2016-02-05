from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from coldeportes.utilities import all_permission_required
from manual.models import Articulo
from manual.forms import ArticuloForm

# Create your views here.
@login_required
@all_permission_required('manual.add_articulo')
def nueva_entrada(request):
    """
    Enero 28 / 2016
    Autor: Karent Narvaez Grisales
    
    registro de la información de un artículo en el manual de usuario.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    """
    articulo_form = ArticuloForm( )

    if request.method == 'POST':

        articulo_form = ArticuloForm(request.POST, request.FILES)

        if articulo_form.is_valid():
            articulo_form.save()
            messages.success(request, ("Artículo registrado correctamente."))
            
            return redirect('nueva_entrada_manual')


    return render(request, 'nueva_entrada.html', {
        'form': articulo_form,
    })

"""
@login_required
def ver_articulo(request, articulo_id):
    """
"""   Enero 28 / 2016
    Autor: Karent Narvaez Grisales
    
    Ver el detalle de un artículo de manual de usuario.

    :param request:   Petición realizada
    :type request:    WSGIRequest
    :param articulo_id:   Petición realizada
    :type articulo_id:    String
    """
    
""""   try:
        articulo = Articulo.objects.get(id=articulo_id)

    return render(request, 'nueva_entrada.html', {
        'articulo': articulo,
        'mensaje': mensaje,
    })"""
