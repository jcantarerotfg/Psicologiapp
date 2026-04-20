from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from . import forms 
from usuarios.models import Paciente_Doctor

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
            if usuario.rol == 'paciente' and not form.cleaned_data.get('doctor'):
                form.add_error('doctor', 'Debe asignar un psicólogo al paciente')
            else:
                usuario.save()
                if usuario.rol == 'paciente':
                    doctor = form.cleaned_data.get('doctor')
                    if doctor:
                        Paciente_Doctor.objects.create(paciente=usuario, doctor=doctor)
                messages.success(request, 'Se ha creado al usuario correctamente')
                return redirect('psicologiapp:perfil')
    else:
        form = forms.CrearUsuarioForm(usuario = request.user)
    return render(request, 'psicologiapp/crearUsuario.html', {'form': form})
