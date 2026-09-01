from django.db import models
from django.conf import settings
from django.utils import timezone

class Diario(models.Model):
    paciente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    estado_animo = models.IntegerField(blank=True, null=True)
    fecha_entrada = models.DateField(default=timezone.localdate)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    leido = models.BooleanField(default=False)

class HistorialSesiones(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sesion_doctor')
    paciente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sesion_paciente')
    fecha_sesion = models.DateField(default=timezone.localdate)
    resumen_sesion = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

class RelacionTareas(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tarea_doctor')
    paciente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tarea_paciente')
    observacion_doctor = models.TextField(blank=True)
    fecha_tareas = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

class Tareas(models.Model):
    relacion = models.ForeignKey(RelacionTareas, on_delete=models.CASCADE)
    descripcion_tarea = models.TextField()
    estado_tarea  = models.CharField(max_length=20, choices=[("sin_hacer","Sin Hacer"),("hecha","Hecha"),("no_hecha","No Hecha")], default="sin_hacer")
    comentario_paciente = models.TextField(blank=True)

class Mensaje(models.Model):
    emisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    fecha_mensaje = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

def rutaArchivos(instance, filename):
    if instance.sesion:
        return f'sesiones/{instance.sesion.id}/{filename}'
    elif instance.entrada:
        return f'entradas/{instance.entrada.id}/{filename}'
    return f'otros/{filename}'

class Archivos(models.Model):
    archivo = models.FileField(upload_to=rutaArchivos)
    tipo_archivo = models.CharField(max_length=20, choices=[("imagen","Imagen"), ("audio","Audio"),("video","Video"),("documento","Documento"),("otro","Otro")])
    nombre_archivo = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    sesion = models.ForeignKey(HistorialSesiones, on_delete=models.CASCADE, null=True, blank=True, related_name='archivos')
    entrada = models.ForeignKey(Diario, on_delete=models.CASCADE, null=True, blank=True, related_name='archivos')