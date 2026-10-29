from django.db import models
from django.utils import timezone


class Artista(models.Model):
    nombre_artistico = models.CharField(max_length=100, unique=True, verbose_name="Nombre artístico")
    email = models.EmailField(unique=True, help_text="Correo de contacto del artista")
    telefono = models.CharField(max_length=20, blank=True, db_column="telefono_contacto")
    fecha_registro = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_artistico


class PerfilArtista(models.Model):
    GENEROS = [
        ("ROCK", "Rock"),
        ("POP", "Pop"),
        ("JAZZ", "Jazz"),
        ("HIPHOP", "Hip-hop"),
        ("ELEC", "Electrónica"),
        ("FLAM", "Flamenco"),
    ]

    # Relación 1:1 -> cada artista tiene un único perfil y cada perfil pertenece a un artista
    artista = models.OneToOneField(Artista, on_delete=models.CASCADE, related_name="perfil")
    biografia = models.TextField(blank=True)
    anios_experiencia = models.PositiveIntegerField(default=0, verbose_name="Años de experiencia")
    genero_principal = models.CharField(max_length=10, choices=GENEROS, default="POP")
    web = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.artista.nombre_artistico}"


class Equipo(models.Model):
    ESTADOS = [
        ("NUEVO", "Nuevo"),
        ("BUENO", "Bueno"),
        ("REPARAR", "En reparación"),
        ("BAJA", "Dado de baja"),
    ]

    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=60)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="BUENO")
    fecha_compra = models.DateField()
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    # Relación N:1 -> una sala tiene muchos equipos, un equipo está en una sola sala
    sala = models.ForeignKey("Sala", on_delete=models.CASCADE, related_name="equipos")

    def __str__(self):
        return f"{self.nombre} ({self.marca})"


class Ingeniero(models.Model):
    ESPECIALIDADES = [
        ("GRAB", "Grabación"),
        ("MEZC", "Mezcla"),
        ("MAST", "Masterización"),
    ]

    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=4, choices=ESPECIALIDADES)
    tarifa_hora = models.DecimalField(max_digits=6, decimal_places=2, help_text="Euros por hora")
    fecha_contratacion = models.DateField()
    disponible = models.BooleanField(default=True)
    # Relación N:M simple -> Django crea la tabla intermedia automáticamente
    equipos_certificados = models.ManyToManyField(Equipo, blank=True, related_name="ingenieros_certificados")

    def __str__(self):
        return self.nombre


class Sala(models.Model):
    TIPOS = [
        ("GRAB", "Sala de grabación"),
        ("ENSAYO", "Sala de ensayo"),
        ("CONTROL", "Sala de control"),
    ]

    nombre = models.CharField(max_length=60)
    tipo = models.CharField(max_length=10, choices=TIPOS, default="GRAB")
    capacidad = models.PositiveIntegerField(help_text="Número máximo de personas")
    metros_cuadrados = models.FloatField(verbose_name="Metros cuadrados")
    tiene_cabina = models.BooleanField(default=False)
    # Relación 1:1 -> un ingeniero es responsable como mucho de una sala
    ingeniero_responsable = models.OneToOneField(
        Ingeniero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sala_a_cargo",
    )

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    TIPOS = [
        ("MAQUETA", "Maqueta"),
        ("SINGLE", "Single"),
        ("EP", "EP"),
        ("ALBUM", "Álbum"),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=TIPOS, default="SINGLE")
    fecha_inicio = models.DateField()
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    presupuesto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_creacion = models.DateField(auto_now_add=True)
    # Relación N:1 -> un artista puede encargar muchos proyectos
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name="proyectos")
    # Relación N:M con tabla intermedia con atributos extra (modelo Sesion)
    salas = models.ManyToManyField(Sala, through="Sesion", related_name="proyectos")

    def __str__(self):
        return self.titulo


class Sesion(models.Model):
    """Tabla intermedia entre Proyecto y Sala, con datos propios de cada sesión."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="sesiones_proyecto")
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name="sesiones_sala")
    ingeniero = models.ForeignKey(Ingeniero, on_delete=models.CASCADE, related_name="sesiones_ingeniero")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    duracion_horas = models.FloatField(default=2.0)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Sesión de {self.proyecto} en {self.sala} ({self.fecha})"


class Instrumento(models.Model):
    FAMILIAS = [
        ("CUERDA", "Cuerda"),
        ("VIENTO", "Viento"),
        ("PERCU", "Percusión"),
        ("TECLADO", "Teclado"),
        ("ELECTRON", "Electrónico"),
    ]

    nombre = models.CharField(max_length=80)
    familia = models.CharField(max_length=10, choices=FAMILIAS)
    es_electrico = models.BooleanField(default=False)
    anio_fabricacion = models.PositiveIntegerField(null=True, blank=True, verbose_name="Año de fabricación")
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Cancion(models.Model):
    titulo = models.CharField(max_length=150)
    duracion_segundos = models.IntegerField(help_text="Duración total en segundos")
    bpm = models.PositiveIntegerField(default=120)
    letra = models.TextField(blank=True)
    grabada = models.BooleanField(default=False)
    # Relación N:1 -> un proyecto contiene muchas canciones
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="canciones")
    # Relación N:M simple -> instrumentos que suenan en la canción
    instrumentos = models.ManyToManyField(Instrumento, blank=True, related_name="canciones")

    def __str__(self):
        return self.titulo


class Mezcla(models.Model):
    FORMATOS = [
        ("WAV", "WAV"),
        ("FLAC", "FLAC"),
        ("MP3", "MP3"),
    ]

    # Relación 1:1 -> cada canción tiene como máximo una mezcla final
    cancion = models.OneToOneField(Cancion, on_delete=models.CASCADE, related_name="mezcla")
    fecha_master = models.DateField()
    formato = models.CharField(max_length=5, choices=FORMATOS, default="WAV")
    loudness_lufs = models.FloatField(default=-14.0, verbose_name="Volumen (LUFS)")
    aprobada = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Mezcla de {self.cancion}"
