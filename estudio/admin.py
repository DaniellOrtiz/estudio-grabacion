from django.contrib import admin

from .models import (
    Artista,
    PerfilArtista,
    Equipo,
    Ingeniero,
    Sala,
    Proyecto,
    Sesion,
    Instrumento,
    Cancion,
    Mezcla,
)

admin.site.register(Artista)
admin.site.register(PerfilArtista)
admin.site.register(Equipo)
admin.site.register(Ingeniero)
admin.site.register(Sala)
admin.site.register(Proyecto)
admin.site.register(Sesion)
admin.site.register(Instrumento)
admin.site.register(Cancion)
admin.site.register(Mezcla)
