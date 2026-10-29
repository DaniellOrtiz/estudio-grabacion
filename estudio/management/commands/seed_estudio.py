import random

from django.core.management.base import BaseCommand
from django_seed import Seed

from estudio.models import (
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


def elegir(opciones):
    """Devuelve una función que elige al azar un valor de las choices de un campo."""
    return lambda inserted: random.choice([valor for valor, _ in opciones])


class Command(BaseCommand):
    # Seeder propio con django-seed. El comando "seed estudio" normal falla con la
    # tabla intermedia Sesion, así que lo hacemos a mano, modelo por modelo.
    help = "Rellena todas las tablas con django-seed (30 registros por tabla)"

    def add_arguments(self, parser):
        # Opción --number: cuántos registros crear de cada modelo (por defecto 30)
        parser.add_argument("--number", type=int, default=30)

    def handle(self, *args, **options):
        n = options["number"]
        seeder = Seed.seeder()

        # El orden importa: primero los modelos de los que dependen los demás.
        # El tercer parámetro es un diccionario para decidir cómo se rellena un campo
        # (aquí, para que las opciones de los choices salgan variadas).
        seeder.add_entity(Artista, n)
        seeder.add_entity(PerfilArtista, n, {"genero_principal": elegir(PerfilArtista.GENEROS)})
        seeder.add_entity(Ingeniero, n)
        seeder.add_entity(Sala, n, {"tipo": elegir(Sala.TIPOS)})
        seeder.add_entity(Equipo, n, {"estado": elegir(Equipo.ESTADOS)})
        seeder.add_entity(Proyecto, n, {"tipo": elegir(Proyecto.TIPOS)})
        seeder.add_entity(Sesion, n)
        seeder.add_entity(Instrumento, n)
        seeder.add_entity(Cancion, n)
        seeder.add_entity(Mezcla, n, {"formato": elegir(Mezcla.FORMATOS)})

        # django-seed no sabe rellenar dos relaciones ManyToMany, así que las quitamos
        # y las rellenamos nosotros después:
        # - Proyecto.salas usa la tabla intermedia Sesion (ya se crean sesiones arriba)
        # - Ingeniero.equipos_certificados necesita que existan ya los equipos
        for orden in seeder.orders:
            if orden["klass"] == Proyecto:
                orden["entity"].many_relations.pop("salas", None)
            if orden["klass"] == Ingeniero:
                orden["entity"].many_relations.pop("equipos_certificados", None)

        seeder.execute()

        # Ahora sí, cada ingeniero recibe 3 equipos al azar
        equipos = list(Equipo.objects.all())
        for ingeniero in Ingeniero.objects.all():
            ingeniero.equipos_certificados.add(*random.sample(equipos, min(3, len(equipos))))

        self.stdout.write(self.style.SUCCESS(f"Seeder terminado: {n} registros de cada modelo."))
