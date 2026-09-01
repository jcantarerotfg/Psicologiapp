from psicologiapp.models import Mensaje

#Funcion que comprueba si el usuario tiene mensajes pendientes

def mensajesPendientes(request):
    if request.user.is_authenticated:
        totalMensajes = Mensaje.objects.filter(receptor=request.user, leido=False).count()
        return {'mensajesPendientes': totalMensajes}
    return {'mensajesPendientes': 0}