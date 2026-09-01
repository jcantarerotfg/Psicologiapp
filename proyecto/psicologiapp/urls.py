from django.urls import path
from . import views

app_name = 'psicologiapp'

urlpatterns = [
    path('perfil/', views.perfil, name="perfil"),
    path('crearUsuario/', views.crear, name="crearUsuario"),
    path('listarUsuarios/', views.listar, name="listarUsuarios"),
    path('eliminarUsuario/<int:id_usuario>/', views.eliminarUsuario, name="eliminarUsuario"),
    path('restaurarUsuario/<int:id_usuario>/', views.restaurarUsuario, name="restaurarUsuario"),
    path('editarUsuario/<int:id_usuario>/', views.editarUsuario, name="editarUsuario"),
    path('calendario/', views.calendario, name='calendario'),
    path('diario/<str:fecha_entrada>/', views.diario, name='diario'),
    path('listarDiarios/', views.listarDiarios, name="listarDiarios"),
    path('leido/<int:id_entrada>/', views.leido, name="leido"),
    path('leerDiario/<int:id_entrada>/', views.leerDiario, name="leerDiario"),
    path('perfilPaciente/<int:id_usuario>/', views.perfilPaciente, name='perfilPaciente'),
    path('historialSesiones/<int:id_usuario>/', views.historialSesiones, name='historialSesiones'),
    path('historialSesiones/<int:id_usuario>/nuevaSesion/', views.nuevaSesion, name='nuevaSesion'),
    path('consultarSesion/<int:id_sesion>/', views.consultarSesion, name='consultarSesion'),
    path('conversacion/<int:id_usuario>/', views.conversacion, name='conversacion'),
    path('conversacionPaciente', views.conversacionPaciente, name='conversacionPaciente'),
    path('listadoTareas/<int:id_usuario>/', views.listadoTareas, name='listadoTareas'),
    path('nuevasTareas/<int:id_usuario>', views.nuevasTareas, name='nuevasTareas'),
    path('kanbanTareas/<int:id_registro>/', views.kanbanTareas, name='kanbanTareas'),
    path('actualizarTarea/<int:id_tarea>/', views.actualizarTarea, name='actualizarTarea'),
    path('listadoTareasPaciente/', views.listadoTareasPaciente, name='listadoTareasPaciente'),
    path('diario/<str:id_diario>/archivo/', views.subirArchivoDiario, name='subirArchivoDiario'),
    path('consultarSesion/<int:id_sesion>/archivo/', views.subirArchivoSesion, name='subirArchivoSesion'),
    path('borrarArchivo/<int:id_archivo>/', views.borrarArchivo, name='borrarArchivo'),

]