import binascii
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .forms import *
from .models import Evento
from noticias.models import Noticia
from noticias.forms import NoticiaForm
from snd.formularios.deportistas import VerificarExistenciaForm
from snd.views.deportistas import existencia_deportista
import datetime


def dashboard(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
        if evento.estado == 0:
            messages.error(request, 'El evento al que trata de acceder no está disponible!')
            return redirect('listar_eventos')
    except Exception:
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')
    user = request.user
    if user.has_perm("gestion_eventos.view_evento"):
        actividades = evento.actividades.all()
    else:
        actividades = evento.actividades.filter(estado=1)
    participantes = evento.participantes

    evento.cancelados = participantes.filter(estado=0).count()
    evento.pendientes = participantes.filter(estado=2).count()
    evento.rechazado = participantes.filter(estado=4).count()
    evento.aprobado = participantes.filter(estado=3).count()
    evento.aceptado = evento.pendientes + evento.rechazado + evento.aprobado

    return render(request, "dashboard_evento.html", {"evento": evento, "actividades": actividades,
                                                     "participantes": participantes.all()})


# Create your views here.
@login_required
@permission_required('gestion_eventos.add_evento')
def registrar_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)

        if form.is_valid():
            evento = form.save(commit=False)
            nueva_foto = request.POST.get('imagen-crop')

            if nueva_foto == "No":
                evento.imagen = ""
            else:
                evento.imagen = nueva_foto

            if evento.video:
                evento.video = evento.video.replace("watch?v=", "embed/")

            evento.latitud = float(request.POST.get('lat'))
            evento.longitud = float(request.POST.get('lng'))
            evento.cupo_disponible = evento.cupo_participantes
            evento.cupo_candidatos = evento.cupo_participantes

            evento.save()
            messages.success(request, 'Se ha registrado el evento correctamente')
            return redirect('listar_eventos')
    else:
        form = EventoForm()
    return render(request, 'registrar_evento.html', {'form': form})


def listar_eventos(request):
    user = request.user
    if user.has_perm("gestion_eventos.view_evento"):
        eventos = Evento.objects.all()
    else:
        eventos = Evento.objects.filter(estado=1)

    return render(request, 'listar_eventos.html', {'eventos': eventos})


@login_required
@permission_required('gestion_eventos.change_evento')
def editar_evento(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
        if evento.estado == 0:
            messages.error(request, 'El evento al que trata de acceder no está disponible!')
            return redirect('listar_eventos')
    except Exception:
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')
    if evento.video:
        evento.video = evento.video.replace("embed/", "watch?v=")
    form = EventoForm(instance=evento)

    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        nueva_foto = request.POST.get("imagen-crop")
        if form.has_changed or nueva_foto != "No":
            if form.is_valid():
                evento_form = form.save(commit=False)
                nueva_foto = request.POST.get('imagen-crop')

                if nueva_foto == "No":
                    evento_form.imagen = ""
                elif nueva_foto != "si":
                    evento_form.imagen = nueva_foto

                if evento_form.video:
                    evento_form.video = evento_form.video.replace("watch?v=", "embed/")

                evento.latitud = float(request.POST.get('lat'))
                evento.longitud = float(request.POST.get('lng'))
                evento_form.cupo_disponible = evento_form.cupo_participantes - evento.participantes.count()

                evento_form.save()

                messages.success(request, 'El evento se ha editado correctamente')
                return redirect('dashboard', evento.id)
        else:
            messages.success(request, 'El evento se ha editado correctamente')
            return redirect('dashboard', evento.id)

    lat = evento.latitud
    lng = evento.longitud
    return render(request, 'registrar_evento.html', {'form': form, 'edicion': True, "foto": evento.imagen,
                                                     'lat': lat, 'lng': lng})


@login_required
@permission_required('gestion_eventos.change_evento')
def cambiar_estado_evento(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
        evento.estado = not evento.estado
        evento.save()
    except Exception:
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')

    messages.success(request, 'Evento '+evento.get_estado()+' correctamente')
    return redirect('listar_eventos')


@login_required
@permission_required('gestion_eventos.view_evento')
def listar_participantes(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
        participantes = evento.participantes
        forms_p = []
        for participante in participantes.all():
            forms_p.append(ParticipantePagoForm(instance=participante,
                                                initial={"pago_registrado": participante.pago_registrado}))
        participantes_form = zip(participantes.all(), forms_p)
    except Exception as e:
        print(e)
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')
    return render(request, 'listar_participantes.html', {'participantes': participantes_form,
                                                         'cupo': evento.cupo_candidatos, 'evento': evento})


def preinscripcion_evento(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')
    if request.method == 'POST':
        participante_form = ParticipanteForm(request.POST)
        if participante_form.is_valid():
            participante = participante_form.save(commit=False)
            participante.nombre = participante.nombre.upper()
            participante.apellido = participante.apellido.upper()
            participante.evento_participe = evento.id
            token = binascii.hexlify(os.urandom(25))
            participante.token_email = token
            participante.save()
            evento.participantes.add(participante)
            evento.cupo_disponible -= 1
            evento.save()

            correo = render_to_string("correo_participante_preinscripcion.html", {"participante": participante,
                                                                                  "evento": evento,
                                                                                  "token": participante.token_email,
                                                                                  "request": request})
            email = EmailMessage('Información de inscripción', correo, to=[str(participante.email)])
            email.send()

            messages.success(request, "Has sido preinscrito con exito!")
            return redirect('dashboard', evento.id)
        else:
            return render(request, 'registrar_preinscrito.html', {'form': participante_form})
    try:
        datos = request.session["datos"]
    except Exception:
        return redirect('verificar_participante', id_evento)

    participante_form = ParticipanteForm(initial=datos)
    del request.session["datos"]
    return render(request, 'registrar_preinscrito.html', {'form': participante_form})


def editar_participante(request, id_participante):
    try:
        participante = Participante.objects.get(id=id_participante)
        token = request.GET.get("token")
        if participante.token_email != token:
            messages.error(request, 'No está autorizado para ingresar!')
            return redirect('listar_eventos')
    except Exception:
        messages.error(request, 'El participante al que trata de acceder no existe!')
        return redirect('listar_eventos')

    if request.method == 'POST':
        participante_form = ParticipanteForm(request.POST, instance=participante)
        if participante_form.has_changed():
            if participante_form.is_valid():
                participante_form.save()

                messages.success(request, "El participante ha sido editado con exito!")
                return redirect('dashboard', participante.evento_participe)
        else:
            messages.success(request, "El participante ha sido editado con exito!")
            return redirect('dashboard', participante.evento_participe)

    participante_form = ParticipanteForm(instance=participante)
    return render(request, 'registrar_preinscrito.html', {'form': participante_form, 'edicion': True})


def verificar_participante(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
        hoy = datetime.date.today()
        if evento.fecha_inicio_preinscripcion > hoy:
            messages.error(request, 'El evento aún no se encuentra en etapa de preinscripcion')
            return redirect('listar_eventos')
        elif evento.fecha_finalizacion_preinscripcion < hoy:
            messages.error(request, 'La etapa de preinscripcion del evento ya finalizó')
            return redirect('listar_eventos')

        if evento.cupo_disponible == 0:
            messages.error(request, 'No hay cupos disponibles para el evento!')
            return redirect('listar_eventos')
    except Exception:
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')

    if request.method == 'POST':
        form = VerificarExistenciaForm(request.POST)

        if form.is_valid():
            datos = {
                'identificacion': form.cleaned_data['identificacion'],
                'tipo_id': form.cleaned_data['tipo_id']
            }
            try:
                participante = evento.participantes.get(tipo_id=datos['tipo_id'],
                                                        identificacion=datos['identificacion'])
                if participante:
                    messages.error(request, 'El participante ya se encuentra inscrito')
                    form = VerificarExistenciaForm()
                    return render(request, 'deportistas/verificar_deportista.html', {'form': form,
                                                                                     'existe': False})

            except Exception:
                pass
            deportista, tenant_existencia, existe = existencia_deportista(datos)

            if existe:
                datos = {
                    'identificacion': form.cleaned_data['identificacion'],
                    'tipo_id': form.cleaned_data['tipo_id'],
                    'nombre': deportista.nombres,
                    'apellido': deportista.apellidos,
                    'fecha_nacimiento': deportista.fecha_nacimiento.strftime("%Y-%m-%d")
                }
                request.session['datos'] = datos
                return redirect('preinscripcion_evento', id_evento)
            else:
                request.session['datos'] = datos
                return redirect('preinscripcion_evento', id_evento)
        else:
            form = VerificarExistenciaForm()
            messages.error(request, 'El evento al que trata de acceder no existe!')
            return render(request, 'deportistas/verificar_deportista.html', {'form': form,
                                                                             'existe': False})

    else:
        form = VerificarExistenciaForm()
    return render(request, 'deportistas/verificar_deportista.html', {'form': form,
                                                                     'existe': False})


@login_required
@permission_required('gestion_eventos.change_evento')
def aceptar_candidato(request, id_participante):
    from django.db import transaction
    try:
        participante = Participante.objects.get(id=id_participante)
    except Exception:
        messages.error(request, 'El participante al que trata de acceder no existe!')
        return redirect('listar_eventos')

    evento = Evento.objects.get(id=participante.evento_participe)
    if evento.cupo_candidatos == 0:
        messages.error(request, 'No hay cupos disponible!')
        return redirect('listar_participantes', evento.id)
    with transaction.atomic():
        participante.estado = 2
        participante.save()

        evento.cupo_candidatos -= 1
        evento.save()

        correo = render_to_string("correo_participante_confirmacion.html", {"participante": participante,
                                                                            "evento": evento,
                                                                            "token": participante.token_email,
                                                                            "request": request})

        email = EmailMessage('Inscripción Aceptada', correo, to=[str(participante.email)])
        email.send()
        messages.success(request, 'Se ha enviado la peticion de confirmación')
        return redirect('listar_participantes', evento.id)

    messages.error(request, 'Ha ocurrido un error')
    return redirect('listar_participantes', evento.id)


def confirmar_participacion(request, id_participante):
    try:
        participante = Participante.objects.get(id=id_participante)
        if participante.estado == 1:
            messages.error(request, 'El participante se encuentra en etapa de preinscripción')
            return redirect('listar_eventos')

        if participante.estado == 3 or participante.estado == 4:
            messages.error(request, 'El participante ya ha respondido la confirmación de participación')
            return redirect('listar_eventos')

        if participante.estado == 0:
            messages.error(request, 'La inscripción del participante ha sido cancelado')
            return redirect('listar_eventos')

    except Exception:
        messages.error(request, 'El participante al que trata de acceder no existe!')
        return redirect('listar_eventos')

    try:
        token = request.GET.get("token")
        if participante.token_email != token:
            messages.error(request, 'No está autorizado para ingresar!')
            return redirect('listar_eventos')

        aceptar = request.GET.get("acp")
        if aceptar == '1':
            participante.estado = 3
            participante.save()
            messages.success(request, 'Has aceptado la inscripción satisfactoriamente')
            return redirect('dashboard', participante.evento_participe)
        elif aceptar == '2':
            participante.estado = 4
            participante.save()
            evento = Evento.objects.get(id=participante.evento_participe)
            evento.cupo_candidatos += 1
            evento.save()
            messages.success(request, 'Has rechazado la inscripción satisfactoriamente')
            return redirect('dashboard', participante.evento_participe)
        else:
            messages.error(request, 'No está autorizado para ingresar!')
            return redirect('listar_eventos')

    except Exception:
        messages.error(request, 'Ha ocurrido un error')
        return redirect('listar_eventos')


@login_required
@permission_required('gestion_eventos.change_evento')
def gestion_pago(request, id_participante):
    try:
        participante = Participante.objects.get(id=id_participante)
    except Exception:
        messages.error(request, 'El participante al que trata de acceder no existe!')
        return redirect('listar_eventos')
    print(participante)
    if request.method == "POST":
        form_pago = ParticipantePagoForm(request.POST, instance=participante)
        if form_pago.is_valid():
            form_pago.save()

        print(participante.pago_registrado)
        messages.success(request, 'Se ha registrado el estado del pago correctamente')
        return redirect('listar_participantes', participante.evento_participe)

    return redirect('listar_eventos')


@login_required
@permission_required('gestion_eventos.change_evento')
def generar_entrada(request, id_participante):
    from reportlab.pdfgen import canvas
    from io import BytesIO
    from django.http import HttpResponse
    try:
        participante = Participante.objects.get(id=id_participante)
        evento = Evento.objects.get(id=participante.evento_participe)
    except Exception:
        messages.error(request, 'El participante al que trata de acceder no existe!')
        return redirect('listar_eventos')
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="entrada-' + participante.nombre + '.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(buffer, pagesize=(300, 320))

    import locale
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # p.drawImage('static/img/LogoSND.png', 20, 290, 90, 20)
    p.rect(20, 140, 70, 80)
    p.setFontSize(12)
    p.drawCentredString(150, 270, str(evento.titulo_evento.capitalize()))
    p.setFontSize(10)
    p.drawString(100, 200, "Tipo ID: " + str(participante.get_tipo_id_display()))
    p.drawString(100, 180, "Número ID: " + str(participante.identificacion))
    p.drawString(100, 160, "Nombre: " + str(participante.nombre) + " " + str(participante.apellido))
    p.drawCentredString(150, 100, (evento.fecha_inicio.strftime("%B %d ") + "al " +
                        evento.fecha_finalizacion.strftime("%d de %Y")).upper())
    p.setFontSize(14)
    p.drawCentredString(150, 20, "PARTICIPANTE")
    p.setFontSize(6)
    p.drawString(5, 5, "Generado: " + str(datetime.datetime.today()))

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


@login_required
@permission_required('gestion_eventos.view_evento')
def registrar_actividad(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')

    actividad_form = ActividadForm()

    if request.method == 'POST':
        actividad_form = ActividadForm(request.POST)
        if actividad_form.is_valid():
            actividad = actividad_form.save(commit=False)
            actividad.evento_perteneciente = evento.id
            actividad.save()
            evento.actividades.add(actividad)
            evento.save()
            messages.success(request, "La actividad ha sido creada con exito!")
            return redirect('registrar_actividad', id_evento)
    lista_actividades = evento.actividades.all()
    return render(request, 'gestion_actividades.html', {'form': actividad_form, 'lista_actividades': lista_actividades,
                                                        'evento': evento})


@login_required
@permission_required('gestion_eventos.change_evento')
def editar_actividad(request, id_actividad):
    try:
        actividad = Actividad.objects.get(id=id_actividad)
        if actividad.estado == 0:
            messages.error(request, 'La actividad a la que trata de acceder no está disponbible')
            return redirect('listar_eventos')

    except Exception:
        messages.error(request, 'La actividad a la que trata de acceder no existe!')
        return redirect('listar_eventos')

    actividad_form = ActividadForm(instance=actividad)

    if request.method == "POST":
        actividad_form = ActividadForm(request.POST, instance=actividad)
        if actividad_form.has_changed():
            if actividad_form.is_valid():
                actividad = actividad_form.save(commit=False)
                actividad.save()
                messages.success(request, "La actividad ha sido editada con éxito!")
                return redirect('registrar_actividad', actividad.evento_perteneciente)
        else:
            messages.success(request, "La actividad ha sido editada con éxito!")
            return redirect('registrar_actividad', actividad.evento_perteneciente)

    evento = Evento.objects.get(id=actividad.evento_perteneciente)
    lista_actividades = evento.actividades.all()
    return render(request, 'gestion_actividades.html', {'form': actividad_form, 'lista_actividades': lista_actividades,
                                                        'evento': evento, 'edicion': True})


def ver_actividades(request, id_evento):
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        messages.error(request, 'El evento al que trata de acceder no existe!')
        return redirect('listar_eventos')

    user = request.user
    if user.has_perm("gestion_eventos.view_evento"):
        actividades = evento.actividades.all()
    else:
        actividades = evento.actividades.filter(estado=1)

    return render(request, 'ver_actividades.html', {'actividades': actividades,
                                                    'evento': evento})


@login_required
@permission_required('gestion_eventos.change_evento')
def cambio_fecha_actividad(request):
    if request.is_ajax():
        response = {
            'status': 'error',
            'message': 'actividad no existe'
        }
        try:
            actividad = Actividad.objects.get(id=request.POST.get("id"))
        except Exception:
            return JsonResponse(response)

        dias = request.POST.get("delta_dias")
        mins = request.POST.get("delta_minutos")
        if not mins:
            actividad.dia_actividad = actividad.dia_actividad + datetime.timedelta(days=int(dias))
            actividad.save()
            message = "ok"
        else:
            try:
                actividad.hora_inicio = (
                datetime.datetime.combine(actividad.dia_actividad, actividad.hora_inicio) + datetime.timedelta(
                    minutes=int(mins))).time()
                actividad.hora_fin = (
                datetime.datetime.combine(actividad.dia_actividad, actividad.hora_fin) + datetime.timedelta(
                    minutes=int(mins))).time()
                actividad.dia_actividad = actividad.dia_actividad + datetime.timedelta(days=int(dias))
                actividad.save()
                message = "ok"
            except Exception as e:
                print(e)
                message = e
        response = {
            'status': 'ok',
            'message': message
        }
        return JsonResponse(response)

    return redirect('listar_eventos')


@login_required
@permission_required('gestion_eventos.change_evento')
def cambiar_estado_actividad(request, id_actividad):
    try:
        actividad = Actividad.objects.get(id=id_actividad)
        actividad.estado = not actividad.estado
        actividad.save()
    except Exception:
        messages.error(request, 'La actividad a la que trata de acceder no existe!')
        return redirect('listar_eventos')

    messages.success(request, 'Actividad '+actividad.get_estado()+' correctamente')
    return redirect('registrar_actividad', actividad.evento_perteneciente)


@login_required
@permission_required('gestion_eventos.view_evento')
def registrar_resultado(request, id_actividad):
    try:
        actividad = Actividad.objects.get(id=id_actividad)
        if actividad.estado == 0:
            messages.error(request, 'La actividad a la que trata de acceder no está disponbible')
            return redirect('listar_eventos')
    except Exception:
        messages.error(request, 'La actividad a la que trata de acceder no existe!')
        return redirect('listar_eventos')

    resultado_form = ResultadoForm()

    if request.method == 'POST':
        resultado_form = ResultadoForm(request.POST)
        if resultado_form.is_valid():
            resultado = resultado_form.save(commit=False)
            resultado.actividad_perteneciente = actividad.id
            resultado.save()
            actividad.resultado.add(resultado)
            actividad.save()
            messages.success(request, "El resultado ha sido registrado con exito!")
            return redirect('registrar_resultado', actividad.id)

    participantes_evento = Participante.objects.filter(evento_participe=actividad.evento_perteneciente)
    resultado_form.fields["paticipante_reconocido"].queryset = participantes_evento
    lista_resultados = actividad.resultado.all()

    return render(request, 'gestion_resultados.html', {'form': resultado_form, 'lista_resultados': lista_resultados,
                                                       'actividad': actividad})


@login_required
@permission_required('gestion_eventos.change_evento')
def editar_resultado(request, id_resultado):
    try:
        resultado = Resultado.objects.get(id=id_resultado)
    except Exception:
        messages.error(request, 'El resultado al que trata de acceder no existe!')
        return redirect('listar_eventos')

    resultado_form = ResultadoForm(instance=resultado)
    actividad = Actividad.objects.get(id=resultado.actividad_perteneciente)
    if request.method == "POST":
        resultado_form = ResultadoForm(request.POST, instance=resultado)
        if resultado_form.has_changed():
            if resultado_form.is_valid():
                resultado = resultado_form.save(commit=False)
                resultado.save()
                messages.success(request, "El resultado ha sido editado con exito!")
                return redirect('registrar_resultado', actividad.id)
        else:
            messages.success(request, "El resultado ha sido editado con exito!")
            return redirect('registrar_resultado', actividad.id)

    participantes_evento = Participante.objects.filter(evento_participe=actividad.evento_perteneciente)
    resultado_form.fields["paticipante_reconocido"].queryset = participantes_evento
    lista_resultados = actividad.resultado.all()
    return render(request, 'gestion_resultados.html', {'form': resultado_form, 'lista_resultados': lista_resultados,
                                                       'actividad': actividad, 'edicion': True})


@login_required
@permission_required('gestion_eventos.change_evento')
def cambiar_estado_resultado(request, id_resultado):
    try:
        resultado = Resultado.objects.get(id=id_resultado)
        resultado.estado = not resultado.estado
        resultado.save()
    except Exception:
        messages.error(request, 'El resultado al que trata de acceder no existe!')
        return redirect('listar_eventos')

    messages.success(request, 'Se ha cambiado el estado del resultado correctamente')
    return redirect('registrar_resultado', resultado.actividad_perteneciente)
