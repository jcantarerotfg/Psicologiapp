from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from . import forms 
from usuarios.models import Paciente_Doctor, Usuario, PerfilPaciente, EvolucionPaciente
from psicologiapp.models import Diario, HistorialSesiones, Mensaje, RelacionTareas, Tareas, Archivos

import json

# Create your views here.

#View de consulta y edición de los datos del usuario
@login_required(login_url="/usuarios/login/")
def perfil(request):
    req_usuario = request.user
    foto_antigua = req_usuario.foto_perfil.name if req_usuario.foto_perfil else None

    if request.method == 'POST':
        form = forms.EditarPerfilForm(request.POST, request.FILES, instance=req_usuario)
        if form.is_valid():
            usuario = form.save()
            if 'foto_perfil' in form.changed_data:
                if foto_antigua and foto_antigua != usuario.foto_perfil.name:
                    try:
                        usuario.foto_perfil.storage.delete(foto_antigua)
                    except Exception as e:
                        print("Error borrando la foto anterior", e)
            update_session_auth_hash(request, usuario)
            messages.success(request, 'Se han actualizado los datos del usuario correctamente')
            return redirect('psicologiapp:perfil')
        else: 
            print("ERRORES:", form.errors)
    else:
        form = forms.EditarPerfilForm(instance=req_usuario)
    return render(request, 'psicologiapp/perfil.html', {'form': form})

#View de creación de nuevos usuarios

@login_required(login_url="/usuarios/login/")
def crear(request):
    if request.user.rol not in ['admin', 'doctor']:
        return redirect('psicologiapp:perfil')
    
    if request.method == 'POST':
        form = forms.CrearUsuarioForm(request.POST, request.FILES, usuario = request.user)
        if form.is_valid():
            usuario = form.save(commit=False)

            if request.user.rol == 'doctor':
                usuario.rol = 'paciente'
                doctor = request.user
            else:
                doctor = form.cleaned_data.get('doctor')
            if usuario.rol == 'paciente' and not form.cleaned_data.get('doctor'):
                form.add_error('doctor', 'Debe asignar un psicólogo al paciente')
            else:
                usuario.save()
                if usuario.rol == 'paciente':
                    doctor = form.cleaned_data.get('doctor')
                    if doctor:
                        Paciente_Doctor.objects.create(paciente=usuario, doctor=doctor)
                messages.success(request, 'Se ha creado al usuario correctamente')
                return redirect('psicologiapp:listarUsuarios')
    else:
        form = forms.CrearUsuarioForm(usuario = request.user)
    return render(request, 'psicologiapp/crearUsuario.html', {'form': form})

@login_required(login_url="/usuarios/login/")
def listar(request):
    if request.user.rol not in ['admin', 'doctor']:
        return redirect('psicologiapp:perfil')
    busqueda = request.GET.get('usuario', '')
    if request.user.rol == 'doctor':
        todos_usuarios = Usuario.objects.filter(eliminado=False, relacion_paciente__doctor=request.user).order_by('first_name')
        usuarios_eliminados = Usuario.objects.filter(eliminado=True, relacion_paciente__doctor=request.user).order_by('first_name')
        # Se filtran los mensajes sin leer para poder notificarlo en la tabla de listado de usuarios

        sinLeer = set(Mensaje.objects.filter(receptor=request.user, leido=False).values_list('emisor', flat=True))
    else:
        todos_usuarios = Usuario.objects.filter(eliminado=False).order_by('first_name')
        usuarios_eliminados = usuarios = Usuario.objects.filter(eliminado=True).order_by('first_name')

        sinLeer= set()
    
    usuarios = todos_usuarios


    if busqueda:
        usuarios = usuarios.filter(Q(username=busqueda))
    paginator = Paginator(usuarios, 10)
    num_pagina = request.GET.get('pagina')
    obj_pagina = paginator.get_page(num_pagina)
    paginator2 = Paginator(usuarios_eliminados, 10)
    num_pagina2 = request.GET.get('pagina')
    obj_pagina2 = paginator2.get_page(num_pagina2)
    return render(request, 'psicologiapp/listarUsuarios.html', {'obj_pagina': obj_pagina, 'obj_pagina2': obj_pagina2, 'sinLeer': sinLeer, 'busqueda': busqueda, 'todos_usuarios': todos_usuarios,})

def eliminarUsuario(request, id_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=id_usuario)
        usuario.eliminado=True
        usuario.save()
        messages.success(request, 'Se ha eliminado al usuario correctamente')
        return redirect('psicologiapp:listarUsuarios')
    
def restaurarUsuario(request, id_usuario):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=id_usuario)
        usuario.eliminado=False
        usuario.save()
        messages.success(request, 'Se ha restaurado al usuario correctamente')
        return redirect('psicologiapp:listarUsuarios')

def editarUsuario(request, id_usuario):
    usuario_editar = get_object_or_404(Usuario, id=id_usuario)
    foto_antigua = usuario_editar.foto_perfil.name if usuario_editar.foto_perfil else None

    if request.method == 'POST':
        form = forms.EditarUsuarioForm(request.POST, request.FILES, instance=usuario_editar, usuario=request.user)
        if form.is_valid():
            usuario = form.save()
            passw = form.cleaned_data.get('password')

            if passw:
                usuario.set_password(passw)
                usuario.pass_temporal = True
            if 'foto_perfil' in form.changed_data:
                if foto_antigua and foto_antigua != usuario.foto_perfil.name:
                    try:
                        usuario.foto_perfil.storage.delete(foto_antigua)
                    except Exception as e:
                        print("Error borrando la foto anterior", e)
            if usuario.rol == 'paciente':
                doctor = form.cleaned_data.get('doctor')
                if doctor:
                    Paciente_Doctor.objects.update_or_create(
                        paciente=usuario,
                        defaults={'doctor': doctor}
                    )
            usuario.save()
            update_session_auth_hash(request, usuario)
            messages.success(request, 'Se han actualizado los datos del usuario correctamente')
            return redirect('psicologiapp:listarUsuarios')
    else:
        form = forms.EditarUsuarioForm(instance=usuario_editar, usuario=request.user)
    return render(request, 'psicologiapp/editarUsuario.html', {'form': form, 'id_usuario': id_usuario, 'usuario_editar': usuario_editar})

@login_required(login_url="/usuarios/login/")
def calendario(request):
     if request.user.rol not in ['paciente']:
        return redirect('psicologiapp:perfil')
     entradas = Diario.objects.filter(paciente=request.user).values('fecha_entrada','estado_animo')
     entradas_json = [{'fecha_entrada': str(i['fecha_entrada']), 'estado_animo': i['estado_animo']} for i in entradas]
     return render(request, 'psicologiapp/calendario.html', {'entradas': entradas_json})

@login_required(login_url="/usuarios/login/")
def diario(request, fecha_entrada):
    if request.user.rol not in ['paciente']:
        return redirect('psicologiapp:perfil')
    entrada, creado = Diario.objects.get_or_create(paciente=request.user, fecha_entrada=fecha_entrada)
    form = forms.DiarioForm(request.POST or None, instance=entrada)
    archivos = entrada.archivos.all()
    form_archivo = forms.ArchivosForm()

    if request.method == 'POST':
        if form.is_valid():
            entrada.save()
            messages.success(request, 'Entrada del diario creada correctamente.')
            return redirect('psicologiapp:calendario')
    
    return render(request, 'psicologiapp/diario.html', {'form': form, 'fecha_entrada': entrada.fecha_entrada, 'archivos': archivos, 'form_archivo': form_archivo, 'url_subida': reverse('psicologiapp:subirArchivoDiario', kwargs={'id_diario': entrada.id})})

@login_required(login_url="/usuarios/login/")
def listarDiarios(request):
    if request.user.rol not in ['doctor']:
        return redirect('psicologiapp:perfil')
    pacientes = Usuario.objects.filter(eliminado=False, relacion_paciente__doctor=request.user).order_by('id')
    entradas = Diario.objects.filter(paciente_id__in=pacientes, estado_animo__isnull=False).select_related('paciente').order_by('-fecha_entrada')
    
    id_usuario = request.GET.get('usuario')
    leido = request.GET.get('leido')

    if id_usuario and id_usuario != 'None':
        entradas = entradas.filter(paciente__id=id_usuario)
    if leido is not None and leido != '' and leido != 'None':
        entradas = entradas.filter(leido=leido == 'True')
    
    paginator = Paginator(entradas, 10)
    num_pagina = request.GET.get('pagina')
    obj_pagina = paginator.get_page(num_pagina)
    

    return render(request, 'psicologiapp/listarDiarios.html', {'obj_pagina': obj_pagina, 'pacientes': pacientes, 'id_usuario_sel': id_usuario,'leido_sel': leido})

def leido(request, id_entrada):
    if request.method == 'POST':
        try:
            entrada = get_object_or_404(Diario, id=id_entrada)
            if entrada.leido == True:
                entrada.leido=False
            else:
                entrada.leido=True
            entrada.save()
            print("Entrada guardada:", entrada.id, entrada.leido)
        except Exception as e:
            print("ERROR: ", e)

        usuario = request.POST.get('usuario', '')
        leido_sel = request.POST.get('leido', '')

        params = {}
        if usuario:
            params['usuario'] = usuario
        if leido_sel:
            params['leido'] = leido_sel

        url = reverse('psicologiapp:listarDiarios')
        if params:
            from urllib.parse import urlencode
            url += '?' + urlencode(params)

        return redirect(url)


@login_required(login_url="/usuarios/login/")
def leerDiario(request, id_entrada):
    entrada = get_object_or_404(Diario, id=id_entrada)
    archivos = entrada.archivos.all()
    form = forms.LeerDiarioForm(instance=entrada)
    return render(request, 'psicologiapp/diario.html', {'form': form, 'id_entrada': id_entrada, 'fecha_entrada': entrada.fecha_entrada, 'archivos': archivos})

@login_required(login_url="/usuarios/login/")
def perfilPaciente(request, id_usuario):
    if request.user.rol not in ['doctor']:
        return redirect('psicologiapp:perfil')
    
    paciente = get_object_or_404(Usuario, id=id_usuario)
    perfil, creado = PerfilPaciente.objects.get_or_create(paciente=paciente)

    form = forms.PerfilPacienteForm(request.POST, instance=perfil)
    evolucion_form = forms.EvolucionPacienteForm(request.POST or None)
    comentarios = EvolucionPaciente.objects.filter(perfil=perfil).order_by('-fecha_comentario')

    if request.method == 'POST':
        if 'guardar_perfil' in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil de paciente actualizado correctamente')
                return redirect('psicologiapp:listarUsuarios')
        elif 'guardar_evolucion' in request.POST:
            evolucion_form = forms.EvolucionPacienteForm(request.POST)
            form = forms.PerfilPacienteForm(instance=perfil)
            if evolucion_form.is_valid():
                comentario = evolucion_form.save(commit=False)
                comentario.perfil = perfil
                comentario.save()
                messages.success(request, 'Comentario añadido correctamente')
                return redirect('psicologiapp:perfilPaciente', id_usuario=id_usuario)
    else:
        form = forms.PerfilPacienteForm(instance=perfil)
    return render(request, 'psicologiapp/perfilPaciente.html', {'form': form, 'evolucion_form': evolucion_form, 'comentarios': comentarios, 'id_usuario': id_usuario, 'paciente': paciente})

@login_required(login_url="/usuarios/login/")
def historialSesiones(request, id_usuario):
    if request.user.rol not in ['doctor']:
        return redirect('psicologiapp:perfil')

    paciente = get_object_or_404(Usuario, id=id_usuario)
    sesiones = HistorialSesiones.objects.filter(doctor=request.user, paciente=paciente).order_by('-fecha_sesion')
    paginator = Paginator(sesiones, 10)
    num_pagina = request.GET.get('pagina')
    obj_pagina = paginator.get_page(num_pagina)


    return render(request, 'psicologiapp/historialSesiones.html', {'obj_pagina': obj_pagina, 'paciente': paciente})

@login_required(login_url="/usuarios/login/")
def nuevaSesion(request, id_usuario):
    if request.user.rol not in ['doctor']:
        return redirect('psicologiapp:perfil')

    paciente = get_object_or_404(Usuario, id=id_usuario)
    if request.method == 'POST':
        form = forms.NuevaSesionForm(request.POST)
        if form.is_valid():
            sesion = form.save(commit=False)
            sesion.doctor = request.user
            sesion.paciente = paciente
            sesion.save()
            messages.success(request, 'Sesión creada correctamente')
            return redirect('psicologiapp:consultarSesion', id_sesion=sesion.id)
    else:
        form = forms.NuevaSesionForm(initial={'fecha_sesion': timezone.localdate()})
    return render(request, 'psicologiapp/nuevaSesion.html', {'form': form, 'paciente': paciente})

@login_required(login_url="/usuarios/login/")
def consultarSesion(request, id_sesion):
    if request.user.rol not in ['doctor']:
        return redirect('psicologiapp:perfil')
    sesion = get_object_or_404(HistorialSesiones, id=id_sesion)
    form = forms.NuevaSesionForm(request.POST, instance=sesion)
    archivos= sesion.archivos.all()
    form_archivo = forms.ArchivosForm()

    if request.method == 'POST':
        if form.is_valid():
            sesion = form.save()
            messages.success(request, 'Se han actualizado los datos de la sesión correctamente')
            return redirect('psicologiapp:consultarSesion', id_sesion=sesion.id)
    else:
        form = forms.NuevaSesionForm(instance=sesion)
    return render(request, 'psicologiapp/consultarSesion.html', {'form': form, 'sesion': sesion, 'paciente': sesion.paciente, 'archivos': archivos, 'form_archivo': form_archivo, 'url_subida': reverse('psicologiapp:subirArchivoSesion', kwargs={'id_sesion': sesion.id})})

@login_required(login_url="/usuarios/login/")
def conversacion(request, id_usuario):
    if request.user.rol not in ['doctor']:
        return redirect('psicologiapp:perfil')
    conversador = get_object_or_404(Usuario, id=id_usuario)
    form = forms.MensajeForm(request.POST or None)

    Mensaje.objects.filter(emisor=conversador, receptor=request.user, leido=False).update(leido=True)

    mensajes = Mensaje.objects.filter(emisor=request.user, receptor=conversador) | Mensaje.objects.filter(emisor=conversador, receptor=request.user)
    mensajes = mensajes.order_by('fecha_mensaje')

    if request.method == 'POST':
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.emisor = request.user
            mensaje.receptor = conversador
            mensaje.save()
            return redirect('psicologiapp:conversacion', id_usuario=id_usuario)
    
    return render(request, 'psicologiapp/conversacion.html', {'mensajes': mensajes, 'conversador': conversador,'form': form})

@login_required(login_url="/usuarios/login/")
def conversacionPaciente(request):
    relacion = get_object_or_404(Paciente_Doctor, paciente=request.user)
    doctor=relacion.doctor
    form = forms.MensajeForm(request.POST or None)

    Mensaje.objects.filter(emisor=doctor, receptor=request.user, leido=False).update(leido=True)

    mensajes = Mensaje.objects.filter(emisor=request.user, receptor=doctor) | Mensaje.objects.filter(emisor=doctor, receptor=request.user)
    mensajes = mensajes.order_by('fecha_mensaje')

    if request.method == 'POST':
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.emisor = request.user
            mensaje.receptor = doctor
            mensaje.save()
            return redirect('psicologiapp:conversacionPaciente')
    
    return render(request, 'psicologiapp/conversacionPaciente.html', {'mensajes': mensajes, 'doctor': doctor,'form': form})

@login_required(login_url="/usuarios/login/")
def listadoTareas(request, id_usuario):
    paciente = get_object_or_404(Usuario, id=id_usuario)
    registros_tareas = RelacionTareas.objects.filter(doctor=request.user, paciente=paciente).order_by('-fecha_tareas')
    paginator = Paginator(registros_tareas, 10)
    num_pagina = request.GET.get('pagina')
    obj_pagina = paginator.get_page(num_pagina)
    return render(request, 'psicologiapp/listadoTareas.html', {
        'obj_pagina': obj_pagina,
        'paciente': paciente
    })

@login_required(login_url="/usuarios/login/")
def nuevasTareas(request, id_usuario):
    if request.user.rol not in ['doctor']:
        return redirect('psicologiapp:perfil')
    paciente = get_object_or_404(Usuario, id=id_usuario)
    form = forms.RelacionTareasForm(request.POST, initial={'fecha_tareas': timezone.localdate()})

    if request.method == 'POST':
        if form.is_valid():
            registroTareas = form.save(commit=False)
            registroTareas.doctor = request.user
            registroTareas.paciente = paciente
            registroTareas.save()

            tareas = request.POST.getlist('tareas')
            for descripcion_tarea in tareas:
                if descripcion_tarea.strip():
                    Tareas.objects.create(relacion=registroTareas, descripcion_tarea=descripcion_tarea, estado_tarea='sin_hacer')
            messages.success(request, 'Se han creado las tareas correctamente')
            return redirect('psicologiapp:listadoTareas', id_usuario=id_usuario)
        
    return render(request, 'psicologiapp/nuevasTareas.html', {'form': form,'paciente': paciente})

def kanbanTareas(request, id_registro):
    registroTareas = get_object_or_404(RelacionTareas, id=id_registro)
    sin_hacer = registroTareas.tareas_set.filter(estado_tarea='sin_hacer')
    hechas = registroTareas.tareas_set.filter(estado_tarea='hecha')
    no_hechas = registroTareas.tareas_set.filter(estado_tarea='no_hecha')
    return render(request, 'psicologiapp/kanbanTareas.html', {'registroTareas': registroTareas,'sin_hacer': sin_hacer,'hechas': hechas,'no_hechas': no_hechas}) 

@login_required(login_url="/usuarios/login/")
def listadoTareasPaciente(request):
    registros_tareas = RelacionTareas.objects.filter(paciente=request.user).order_by('-fecha_tareas')
    paginator = Paginator(registros_tareas, 10)
    num_pagina = request.GET.get('pagina')
    obj_pagina = paginator.get_page(num_pagina)
    return render(request, 'psicologiapp/listadoTareasPaciente.html', {'obj_pagina': obj_pagina})
@login_required(login_url="/usuarios/login/")
def actualizarTarea(request, id_tarea):
    tarea = get_object_or_404(Tareas, id=id_tarea)

    if request.method == 'POST':
        tarea.estado_tarea = request.POST.get('estado_tarea')
        tarea.comentario_paciente = request.POST.get('comentario_paciente', '')
        tarea.save()

        registroTareas = tarea.relacion
        incompletas = registroTareas.tareas_set.filter(estado_tarea='sin_hacer').exists()
        registroTareas.completado = not incompletas
        registroTareas.save()
        return redirect('psicologiapp:kanbanTareas', id_registro=tarea.relacion.id)

    return render(request, 'psicologiapp/actualizarTarea.html', {'tarea': tarea})

def tipoArchivo(nombre_archivo):
    extension = nombre_archivo.split('.')[-1].lower()
    if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        return 'imagen'
    elif extension in ['mp3', 'wav','ogg', 'm4a']:
        return 'audio'
    elif extension in ['mp4', 'avi', 'mov', 'webm']:
        return 'video'
    elif extension in ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx']:
        return 'documento'
    else:
        return 'otro'

@login_required(login_url="/usuarios/login/")
def subirArchivoSesion(request, id_sesion):
    sesion = get_object_or_404(HistorialSesiones, id=id_sesion)

    if request.method == 'POST':
        form = forms.ArchivosForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.sesion = sesion
            archivo.nombre_archivo = request.FILES['archivo'].name
            archivo.tipo_archivo = tipoArchivo(request.FILES['archivo'].name)
            archivo.save()
        return redirect('psicologiapp:consultarSesion', id_sesion=id_sesion)
    return redirect('psicologiapp:consultarSesion', id_sesion=id_sesion)

@login_required(login_url="/usuarios/login/")
def subirArchivoDiario(request, id_diario):
    diario = get_object_or_404(Diario, id=id_diario)

    if request.method == 'POST':
        form = forms.ArchivosForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.entrada = diario
            archivo.nombre_archivo = request.FILES['archivo'].name
            archivo.tipo_archivo = tipoArchivo(request.FILES['archivo'].name)
            archivo.save()
        return redirect('psicologiapp:diario', fecha_entrada=diario.fecha_entrada)
    return redirect('psicologiapp:diario', fecha_entrada=diario.fecha_entrada)

@login_required(login_url="/usuarios/login/")
def borrarArchivo(request, id_archivo):
    archivo = get_object_or_404(Archivos, id=id_archivo)

    if archivo.sesion:
        url = reverse('psicologiapp:consultarSesion', kwargs={'id_sesion': archivo.sesion.id})
    elif archivo.entrada:
        url = reverse('psicologiapp:diario', kwargs={'fecha_entrada': archivo.entrada.fecha_entrada})

    if archivo.archivo:
        archivo.archivo.delete()

    archivo.delete()

    return redirect(url)