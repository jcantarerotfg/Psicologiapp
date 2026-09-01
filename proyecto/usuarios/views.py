from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, update_session_auth_hash
from . import forms
from . import models
from django.contrib import messages

# Create your views here.

def login_view(request): 
    temporal = False
    eliminado = False
    form = AuthenticationForm()
    password_form = forms.CambiarPasswordForm()
    if request.method == "POST": 
        if "boton_login" in request.POST:
            form = AuthenticationForm(data=request.POST)
            if form.is_valid(): 
                usuario = form.get_user()
                login(request, form.get_user())
                temporal = usuario.pass_temporal
                eliminado = usuario.eliminado
                print("Eliminado: ", eliminado)
                if not eliminado:
                    if temporal:
                        return render(request, "usuarios/login.html", { "form": form, "temporal": temporal, "password_form": password_form })
                    else:
                        next = request.POST.get('next')
                        return redirect(next if next else "psicologiapp:perfil")
                else:
                    return redirect("usuarios:login")
        elif "boton_pass" in request.POST:
            password_form = forms.CambiarPasswordForm(request.POST)
            if password_form.is_valid():
                usuario = request.user
                usuario.set_password(password_form.cleaned_data['nuevo_pass'])
                usuario.pass_temporal = False
                usuario.save()
                update_session_auth_hash(request, usuario)
                messages.success(request, 'Contraseña actualizada correctamente')
                next = request.POST.get('next')
                return redirect(next if next else "psicologiapp:perfil")
            else:
                return render(request, "usuarios/login.html", {'form': form, 'temporal': True, 'password_form': password_form})
    
    else: 
        form = AuthenticationForm()
    return render(request, "usuarios/login.html", { "form": form, "temporal": temporal, "password_form": password_form })

def logout_view (request):
    if request.method == "POST":
        logout(request)
        return redirect("usuarios:login")