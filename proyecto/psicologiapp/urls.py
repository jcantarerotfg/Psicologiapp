from django.urls import path
from . import views

app_name = 'psicologiapp'

urlpatterns = [
    path('perfil/', views.perfil, name="perfil"),
    path('crearUsuario/', views.crear, name="crearUsuario"),
]