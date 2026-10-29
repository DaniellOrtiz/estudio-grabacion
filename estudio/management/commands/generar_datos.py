import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

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
    """Devuelve un valor aleatorio de una lista de choices [(valor, etiqueta), ...]."""
    return random.choice([valor for valor, _ in opciones])


def dinero(minimo, maximo):
    """Genera un Decimal con 2 decimales entre minimo y maximo."""
    return Decimal(str(round(random.uniform(minimo, maximo), 2)))


class Command(BaseCommand):
    # Texto que aparece con: python manage.py help generar_datos
    help = "Genera 10 registros aleatorios de cada modelo usando Faker"

    def handle(self, *args, **options):
        # 'es_ES' hace que los datos (nombres, textos...) salgan en español
        fake = Faker("es_ES")
        N = 10

        # 1) Artistas y sus perfiles (1:1)
        artistas = []
        for _ in range(N):
            artista = Artista.objects.create(
                nombre_artistico=fake.unique.user_name()[:100],
                email=fake.unique.email(),
                telefono=fake.phone_number()[:20],
                activo=random.choice([True, False]),
            )
            artistas.append(artista)
            PerfilArtista.objects.create(
                artista=artista,
                biografia=fake.paragraph(nb_sentences=3),
                anios_experiencia=random.randint(0, 30),
                genero_principal=elegir(PerfilArtista.GENEROS),
                web=fake.url(),
            )

        # 2) Ingenieros
        ingenieros = []
        for _ in range(N):
            ingenieros.append(
                Ingeniero.objects.create(
                    nombre=fake.name(),
                    especialidad=elegir(Ingeniero.ESPECIALIDADES),
                    tarifa_hora=dinero(15, 90),
                    fecha_contratacion=fake.date_between(start_date="-8y", end_date="today"),
                    disponible=random.choice([True, False]),
                )
            )

        # 3) Salas: random.sample elige ingenieros sin repetir (porque la relación es 1:1)
        salas = []
        responsables = random.sample(ingenieros, N)
        for i in range(N):
            salas.append(
                Sala.objects.create(
                    nombre=f"Sala {i + 1} - {fake.word().capitalize()}",
                    tipo=elegir(Sala.TIPOS),
                    capacidad=random.randint(2, 20),
                    metros_cuadrados=round(random.uniform(10, 80), 1),
                    tiene_cabina=random.choice([True, False]),
                    ingeniero_responsable=responsables[i],
                )
            )

        # 4) Equipos (N:1 con Sala) y certificaciones de ingenieros (N:M simple)
        nombres_equipo = ["Micrófono de condensador", "Preamplificador", "Monitor de estudio",
                          "Interfaz de audio", "Compresor", "Mesa de mezclas"]
        marcas = ["Neumann", "Shure", "Focusrite", "Yamaha", "Behringer", "Audio-Technica"]
        equipos = []
        for _ in range(N):
            equipos.append(
                Equipo.objects.create(
                    nombre=random.choice(nombres_equipo),
                    marca=random.choice(marcas),
                    estado=elegir(Equipo.ESTADOS),
                    fecha_compra=fake.date_between(start_date="-6y", end_date="today"),
                    valor=dinero(80, 3500),
                    sala=random.choice(salas),
                )
            )
        for ingeniero in ingenieros:
            ingeniero.equipos_certificados.add(*random.sample(equipos, 3))

        # 5) Proyectos (N:1 con Artista)
        proyectos = []
        for _ in range(N):
            inicio = fake.date_between(start_date="-1y", end_date="today")
            proyectos.append(
                Proyecto.objects.create(
                    titulo=fake.catch_phrase()[:150],
                    descripcion=fake.paragraph(nb_sentences=2),
                    tipo=elegir(Proyecto.TIPOS),
                    fecha_inicio=inicio,
                    fecha_entrega_estimada=inicio + timedelta(days=random.randint(30, 180)),
                    presupuesto=dinero(300, 15000),
                    artista=random.choice(artistas),
                )
            )

        # 6) Sesiones: tabla intermedia Proyecto <-> Sala con atributos extra
        for _ in range(N):
            Sesion.objects.create(
                proyecto=random.choice(proyectos),
                sala=random.choice(salas),
                ingeniero=random.choice(ingenieros),
                fecha=fake.date_between(start_date="-6m", end_date="+3m"),
                hora_inicio=fake.time_object(),
                duracion_horas=round(random.uniform(1, 8), 1),
                notas=fake.sentence(),
            )

        # 7) Instrumentos
        instrumentos = []
        nombres_instrumento = ["Guitarra eléctrica", "Bajo", "Batería", "Piano", "Violín",
                               "Saxofón", "Sintetizador", "Cajón flamenco", "Trompeta", "Guitarra española"]
        for nombre in nombres_instrumento[:N]:
            instrumentos.append(
                Instrumento.objects.create(
                    nombre=nombre,
                    familia=elegir(Instrumento.FAMILIAS),
                    es_electrico=random.choice([True, False]),
                    anio_fabricacion=random.randint(1960, 2024),
                    descripcion=fake.sentence(),
                )
            )

        # 8) Canciones (N:1 con Proyecto, N:M con Instrumento) y 9) Mezclas (1:1 con Canción)
        for _ in range(N):
            cancion = Cancion.objects.create(
                titulo=fake.sentence(nb_words=3).rstrip("."),
                duracion_segundos=random.randint(120, 420),
                bpm=random.randint(60, 180),
                letra=fake.text(max_nb_chars=200),
                grabada=random.choice([True, False]),
                proyecto=random.choice(proyectos),
            )
            cancion.instrumentos.add(*random.sample(instrumentos, 3))
            Mezcla.objects.create(
                cancion=cancion,
                fecha_master=fake.date_between(start_date="-6m", end_date="today"),
                formato=elegir(Mezcla.FORMATOS),
                loudness_lufs=round(random.uniform(-16, -8), 1),
                aprobada=random.choice([True, False]),
                observaciones=fake.sentence(),
            )

        self.stdout.write(self.style.SUCCESS(f"Se han creado {N} registros de cada modelo."))
