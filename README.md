Estudio de Grabación Musical
Daniel Ortiz Caraballo

DESCRIPCIÓN

Aplicación para gestionar un estudio de grabación. Los artistas encargan proyectos (maqueta, single, EP o álbum), cada proyecto tiene canciones, y se graban en sesiones dentro de las salas del estudio con un ingeniero de sonido.

ESQUEMA ENTIDAD-RELACIÓN

El esquema está en la imagen esquema_er.png

Relaciones:
- OneToOne: PerfilArtista-Artista, Sala-Ingeniero, Mezcla-Cancion
- ManyToOne: Proyecto-Artista, Cancion-Proyecto, Equipo-Sala, Sesion-Proyecto, Sesion-Sala, Sesion-Ingeniero
- ManyToMany: Proyecto-Sala (tabla intermedia Sesion, con atributos extra), Cancion-Instrumento, Ingeniero-Equipo

MODELOS

1. Artista: persona o grupo que graba en el estudio.
- nombre_artistico: CharField (max_length, unique, verbose_name)
- email: EmailField (unique, help_text)
- telefono: CharField (max_length, blank, db_column)
- fecha_registro: DateTimeField (default)
- activo: BooleanField (default)

2. PerfilArtista: datos extra del artista.
- artista: OneToOneField a Artista (on_delete, related_name)
- biografia: TextField (blank)
- anios_experiencia: PositiveIntegerField (default, verbose_name)
- genero_principal: CharField (max_length, choices, default)
- web: URLField (null, blank)

3. Equipo: material técnico del estudio.
- nombre: CharField (max_length)
- marca: CharField (max_length)
- estado: CharField (max_length, choices, default)
- fecha_compra: DateField
- valor: DecimalField (max_digits, decimal_places)
- sala: ForeignKey a Sala (on_delete, related_name)

4. Ingeniero: técnico de sonido.
- nombre: CharField (max_length)
- especialidad: CharField (max_length, choices)
- tarifa_hora: DecimalField (max_digits, decimal_places, help_text)
- fecha_contratacion: DateField
- disponible: BooleanField (default)
- equipos_certificados: ManyToManyField a Equipo (blank, related_name)

5. Sala: espacio físico del estudio.
- nombre: CharField (max_length)
- tipo: CharField (max_length, choices, default)
- capacidad: PositiveIntegerField (help_text)
- metros_cuadrados: FloatField (verbose_name)
- tiene_cabina: BooleanField (default)
- ingeniero_responsable: OneToOneField a Ingeniero (on_delete, null, blank, related_name)

6. Proyecto: encargo musical de un artista.
- titulo: CharField (max_length)
- descripcion: TextField (blank)
- tipo: CharField (max_length, choices, default)
- fecha_inicio: DateField
- fecha_entrega_estimada: DateField (null, blank)
- presupuesto: DecimalField (max_digits, decimal_places)
- fecha_creacion: DateField (auto_now_add)
- artista: ForeignKey a Artista (on_delete, related_name)
- salas: ManyToManyField a Sala (through, related_name)

7. Sesion: tabla intermedia entre Proyecto y Sala. Guarda cada sesión de grabación.
- proyecto: ForeignKey a Proyecto (on_delete, related_name)
- sala: ForeignKey a Sala (on_delete, related_name)
- ingeniero: ForeignKey a Ingeniero (on_delete, related_name)
- fecha: DateField
- hora_inicio: TimeField
- duracion_horas: FloatField (default)
- notas: TextField (blank)

8. Instrumento: instrumentos que suenan en las canciones.
- nombre: CharField (max_length)
- familia: CharField (max_length, choices)
- es_electrico: BooleanField (default)
- anio_fabricacion: PositiveIntegerField (null, blank, verbose_name)
- descripcion: TextField (blank)

9. Cancion: canciones de un proyecto.
- titulo: CharField (max_length)
- duracion_segundos: IntegerField (help_text)
- bpm: PositiveIntegerField (default)
- letra: TextField (blank)
- grabada: BooleanField (default)
- proyecto: ForeignKey a Proyecto (on_delete, related_name)
- instrumentos: ManyToManyField a Instrumento (blank, related_name)

10. Mezcla: versión final de una canción.
- cancion: OneToOneField a Cancion (on_delete, related_name)
- fecha_master: DateField
- formato: CharField (max_length, choices, default)
- loudness_lufs: FloatField (default, verbose_name)
- aprobada: BooleanField (default)
- observaciones: TextField (null, blank)

PARÁMETROS USADOS

- max_length: tamaño máximo de un campo de texto
- null: permite guardar el valor como nulo en la base de datos
- blank: permite dejar el campo vacío
- choices: el valor se elige de una lista de opciones
- unique: el valor no se puede repetir
- default: valor por defecto
- db_column: nombre de la columna en la base de datos
- verbose_name: nombre legible del campo
- help_text: texto de ayuda del campo
- auto_now_add: pone la fecha automáticamente al crear el registro
- max_digits: número total de dígitos de un DecimalField
- decimal_places: cuántos de esos dígitos son decimales
- on_delete: qué pasa si se borra el registro relacionado (CASCADE lo borra también, SET_NULL lo deja vacío)
- related_name: nombre para acceder a la relación desde el otro modelo
- through: indica la tabla intermedia de una relación ManyToMany

CÓDIGO QUE NO SE VIO EN CLASE

En generar_datos.py y seed_estudio.py (carpeta estudio/management/commands):
- BaseCommand y handle(): clase de Django para crear comandos propios; handle() es lo que se ejecuta al lanzar el comando
- add_arguments: crea la opción --number del comando seed_estudio
- Faker("es_ES"): crea datos falsos en español; fake.unique evita que se repitan
- random.choice: elige un elemento al azar de una lista
- random.sample(lista, n): elige n elementos distintos de una lista
- .add(): añade registros a una relación ManyToMany
- Decimal: tipo de número que usa Django en los DecimalField
- timedelta: sirve para sumar días a una fecha
- Seed.seeder() y add_entity(Modelo, n): preparan en django-seed la creación de n registros de un modelo
- seeder.orders: lista de pedidos del seeder; la uso para quitar las relaciones ManyToMany con tabla intermedia, que django-seed no sabe rellenar

BACKUP

La base de datos (db.sqlite3) está en el .gitignore. La copia de seguridad está en estudio/fixtures/datos.json
