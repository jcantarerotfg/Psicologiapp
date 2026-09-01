from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

class Usuario (AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=[("paciente","Paciente"),("doctor","Doctor"),("admin","Administrador")])
    foto_perfil = models.ImageField(upload_to= 'perfil/', blank=True, null=True, default='perfil/defecto/default-avatar.jpg')
    pass_temporal = models.BooleanField(default=False)
    eliminado = models.BooleanField(default=False)
    chat = models.BooleanField(default=False)

class Paciente_Doctor (models.Model):
    paciente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="relacion_paciente")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="relacion_doctor")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['paciente', 'doctor'],
                name='unique_paciente_doctor'
            )
        ]

class PerfilPaciente (models.Model):
    paciente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evolucion = models.TextField(blank=True)
    puntos_fuertes = models.TextField(blank=True)
    puntos_debiles = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

class EvolucionPaciente (models.Model):
    perfil = models.ForeignKey(PerfilPaciente, on_delete=models.CASCADE)
    comentario = models.TextField()
    fecha_comentario = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)