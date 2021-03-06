from django.contrib import messages
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from .forms import ClasificadoForm
from .forms import CropForm
from .models import Clasificado
from django.http import JsonResponse
import random

import datetime
from PIL import Image
from io import BytesIO
import base64
import re


# Create your views here.
@login_required
@permission_required('publicidad.add_clasificado')
def registrar_clasificado(request):

    if request.method == 'POST':
        form = ClasificadoForm(request.POST)
        if form.is_valid():
            clasificado = form.save(commit=False)
            nueva_foto = request.POST.get('imagen-crop')

            clasificado.titulo = clasificado.titulo.upper()

            if nueva_foto == "No":
                clasificado.foto = "clasificados/clasificados-default.png"
            else:
                clasificado.foto = nueva_foto
            clasificado.etiquetas = clasificado.etiquetas.upper()
            form.save()

            messages.success(request, 'Se ha registrado el clasiificado correctamente')
            return redirect('listar_clasificados')
    else:
        form = ClasificadoForm()
    return render(request, 'registrar_clasificado.html', {'form': form})


def listar_clasificados(request):

    clasificados = Clasificado.objects.filter(estado=1, fecha_expiracion__gte=datetime.date.today()).order_by("-fecha_publicacion")[:10]

    for clasificado in clasificados:
        clasificado.clase_inclinacion = random.randint(1, 3)

    form = ClasificadoForm()

    return render(request, 'listar_clasificados.html', {'clasificados': clasificados, "form": form})


@login_required
def gestionar_clasificados(request):

    clasificados = Clasificado.objects.all()

    return render(request, 'gestionar_clasificados.html', {'clasificados': clasificados})


@login_required
@permission_required('publicidad.change_clasificado')
def editar_clasificado(request, id_clasificado):
    try:
        clasificado = Clasificado.objects.get(id=id_clasificado)
    except Exception:
        messages.error(request, 'El clasificado que está intentando editar no existe')
        return redirect('listar_clasificados')

    form = ClasificadoForm(instance=clasificado)
    foto = clasificado.foto
    if request.method == 'POST':
        nueva_foto = request.POST.get("imagen-crop")
        form = ClasificadoForm(request.POST, instance=clasificado)
        if form.has_changed or nueva_foto != "No":
            if form.is_valid():
                clasificado_form = form.save(commit=False)
                if nueva_foto == "No":
                    clasificado_form.foto = "clasificados/clasificados-default.png"
                elif nueva_foto != "si":
                    clasificado_form.foto = nueva_foto

                clasificado_form.titulo = clasificado_form.titulo.upper()
                clasificado.etiquetas = clasificado.etiquetas.upper()
                form.save()
                messages.success(request, 'El clasificado se ha editado correctamente')
                return redirect('gestionar_clasificados')
    return render(request, 'registrar_clasificado.html', {'form': form, 'edicion': True, "foto": foto})


@login_required
@permission_required('publicidad.change_clasificado')
def cambiar_estado_clasificado(request, id_clasificado):
    try:
        clasificado = Clasificado.objects.get(id=id_clasificado)
    except Exception:
        messages.error(request, 'El clasificado al que está intentando cambiar su estado no existe')
        return redirect('listar_clasificados')

    clasificado.estado = not clasificado.estado
    clasificado.save()

    messages.success(request, 'Clasificado ' + clasificado.get_estado_accion() + ' correctamente')
    return redirect('gestionar_clasificados')


@csrf_exempt
@login_required
def crop_pic(request):
    from django.conf import settings
    response_data = {"status": "error", 'message': 'Only Post Accepted'}
    if request.method == 'POST':

        form = CropForm(request.POST)
        if form.is_valid():

            try:
                # get the url of the working image i.e. www.example.com/media/pictures/uploaded_image.png
                image_url = form.cleaned_data['imgUrl']
                rotation = form.cleaned_data.get("rotation") * -1
                if ";base64" in image_url:
                    image_path = re.sub('^data:image/.+;base64,', '', image_url)
                    original = Image.open(BytesIO(base64.b64decode(image_path)))
                else:
                    image_path = image_url.replace("media/", "")

                    original = Image.open(settings.MEDIA_ROOT+image_path)

                newim = original.resize(
                            (int(form.cleaned_data['imgW']), int(form.cleaned_data['imgH'])),
                            Image.ANTIALIAS
                            )
                newim = newim.rotate(rotation)

                x1 = int(form.cleaned_data['imgX1'])
                y1 = int(form.cleaned_data['imgY1'])
                x2 = int(form.cleaned_data['cropW']) + x1
                y2 = int(form.cleaned_data['cropH']) + y1

                newim = newim.crop((x1, y1, x2, y2))
                nombre_tiempo = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
                url_media = request.POST.get("url_media")
                print(settings.MEDIA_ROOT)
                nombre_imagen = url_media+str(nombre_tiempo)+".png"
                newim.save(settings.MEDIA_ROOT+nombre_imagen, "PNG")

                response_data = {
                    "status": "success",
                    "url": nombre_imagen,
                    "message": "ok",
                    }

            except Exception as e:
                response_data = {"status": "error", 'message': str(e)}
        else:
            response_data = {"status": "error", 'message': form.errors}

    # Croppic will parse the information returned into json. content_type needs
    # to be set as 'text/plain'
    return JsonResponse(response_data)


def filtro_clasificados(request):
    from django.db.models import Q
    if request.is_ajax():
        try:
            categoria = request.POST.get("seleccion")
            palabra = request.POST.get("palabra").upper()

            if categoria == "" and palabra == "":
                clasificados = Clasificado.objects.all()[:10]
            else:
                clasificados = Clasificado.objects.filter(Q(etiquetas__contains=palabra) |
                                                          Q(descripcion__icontains=palabra) |
                                                          Q(titulo__icontains=palabra),
                                                          categoria__contains=categoria, estado=1,
                                                          fecha_expiracion__gte=datetime.date.today())

            for clasificado in clasificados:
                clasificado.clase_inclinacion = random.randint(1, 3)

            return render(request, 'tarjeta_clasificado.html', {"clasificados_filtrados": clasificados})
        except Exception as e:
            print(e)
            messages.error(request, 'Ocurrió un error en el filtro de clasificados')
            JsonResponse({'status': 'error'})
    else:
        return render(request, "403.html", {})


def adicionar_clasificados(request):
    from django.template.loader import render_to_string
    if request.is_ajax():
        try:
            count = int(request.POST["count"])
            clasificados = Clasificado.objects.all()[count:count+9]

            print(clasificados.count())
            for clasificado in clasificados:
                clasificado.clase_inclinacion = random.randint(1, 3)

            plantilla = render_to_string('tarjeta_clasificado.html', {"clasificados_filtrados": clasificados},
                                         context_instance=RequestContext(request))
            if clasificados.count() == 0:
                count = -1
            return JsonResponse({"plantilla": plantilla, "counter": count})
        except Exception as e:
            print(e)
            JsonResponse({'status': 'error'})
    else:
        return redirect("listar_clasificados")
