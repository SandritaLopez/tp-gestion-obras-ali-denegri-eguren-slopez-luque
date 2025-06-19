# Importamos todo lo necesario del módulo peewee (ORM liviano para Python)
from peewee import *

# Definimos la base de datos SQLite que se usará
db = SqliteDatabase("obras_urbanas.db")

# Clase base de la que heredarán todos los modelos, asigna la base de datos
class BaseModel(Model):
    class Meta:
        database = db

# Tabla de entornos (urbano, natural, etc.)
class Entorno(BaseModel):
    id_entorno = AutoField()  # Clave primaria autoincremental
    entorno = CharField()     # Nombre del entorno

    # Este método especial define cómo se verá el objeto cuando se convierta en texto.
    # Por ejemplo, si hacés print(entorno), se mostrará "Entorno Espacio Público" (si entorno='Espacio Público').
    def __str__(self):
        return f"Entorno {self.entorno}"


    class Meta:
        db_table = "entornos"  # Nombre personalizado de la tabla en la BD

# Tabla de etapas de una obra (inicio, ejecución, finalización, etc.)
class Etapa(BaseModel):
    id_etapa = AutoField()
    etapa = CharField()

    def __str__(self):
        return f"Etapa {self.etapa}"

    class Meta:
        db_table = "etapas"

# Tabla con tipos de intervención (construcción, reparación, etc.)
class TipoIntervencion(BaseModel):
    id_tipo_intervencion = AutoField()
    tipo = CharField()

    def __str__(self):
        return f"Tipo Intervención {self.tipo}"

    class Meta:
        db_table = "tipos_intervenciones"

# Tabla de áreas responsables de las obras (organismos o dependencias)
class AreaResponsable(BaseModel):
    id_area = AutoField()
    area_nombre = CharField()

    def __str__(self):
        return f"Área responsable {self.area_nombre}"

    class Meta:
        db_table = "areas"

# Tabla de comunas (zonas geográficas amplias)
class Comuna(BaseModel):
    id_comuna = AutoField()
    comuna = CharField()

    def __str__(self):
        return f"Comuna {self.comuna}"

    class Meta:
        db_table = "comunas"

# Tabla de barrios (ubicación más específica)
class Barrio(BaseModel):
    id_barrio = AutoField()
    barrio = CharField()

    def __str__(self):
        return f"Barrio {self.barrio}"

    class Meta:
        db_table = "barrios"

# Tabla con información de empresas contratadas
class Empresa(BaseModel):
    id_empresa = AutoField()
    nombre = CharField()  # Nombre de la empresa
    cuit = CharField()    # CUIT de la empresa

    def __str__(self):
        return f"Empresa {self.nombre}"

    class Meta:
        db_table = "empresas"

# Tabla de licitaciones (procesos de contratación)
class Licitacion(BaseModel):
    id_licitacion = AutoField()
    nro_contratacion = CharField()       # Número de contratación
    anio = IntegerField()                # Año de la licitación
    tipo = CharField()                   # Tipo de licitación
    expediente_numero = CharField()      # Número de expediente
    empresa = ForeignKeyField(Empresa, backref="licitaciones")  # Relación con empresa contratada

    def __str__(self):
        return f"Licitación {self.nro_contratacion}"

    class Meta:
        db_table = "licitaciones"

# Tabla con fuentes de financiamiento (presupuesto, crédito, etc.)
class Financiamiento(BaseModel):
    id_financiamiento = AutoField()
    fuente = CharField()

    def __str__(self):
        return f"Financiamiento {self.fuente}"

    class Meta:
        db_table = "financiamientos"

# Tabla principal de obras
class Obra(BaseModel):
    id_obra = AutoField()
    entorno = ForeignKeyField(Entorno, backref="obras")  # Relación con entorno
    nombre = CharField()                                  # Nombre de la obra
    descripcion = TextField(null=True)                    # Descripción (opcional)
    direccion = CharField(null=True)                      # Dirección (opcional)
    lat = FloatField(null=True)                           # Latitud geográfica
    lng = FloatField(null=True)                           # Longitud geográfica
    fecha_inicio = DateField(null=True)                   # Fecha de inicio
    fecha_fin_inicial = DateField(null=True)              # Fecha estimada de fin
    plazo_meses = IntegerField(null=True)                 # Duración estimada en meses
    porcentaje_avance = IntegerField(null=True)           # Avance porcentual
    tipo_intervencion = ForeignKeyField(TipoIntervencion, backref="obras")  # Tipo de intervención
    area_responsable = ForeignKeyField(AreaResponsable, backref="obras")    # Área responsable
    comuna = ForeignKeyField(Comuna, backref="obras")                       # Ubicación: comuna
    barrio = ForeignKeyField(Barrio, backref="obras")                       # Ubicación: barrio
    licitacion = ForeignKeyField(Licitacion, backref="obras")              # Licitación asociada
    financiamiento = ForeignKeyField(Financiamiento, backref="obras")      # Financiamiento asociado
    beneficiarios = TextField(null=True)                    # Texto sobre los beneficiarios
    mano_obra = IntegerField(null=True)                     # Cantidad de personas empleadas
    compromiso = BooleanField(default=False)                # ¿Tiene compromiso asumido?
    destacada = BooleanField(default=False)                 # ¿Está destacada como importante?
    ba_elige = BooleanField(default=False)                  # ¿Forma parte del programa BA Elige?
    link_interno = CharField(null=True)                     # Link interno (opcional)
    pliego_descarga = CharField(null=True)                  # Link para descargar pliego
    estudio_ambiental_descarga = CharField(null=True)       # Link de estudio ambiental

    def __str__(self):
        return f"Obra {self.nombre}"

    class Meta:
        db_table = "obras"

# Tabla para guardar imágenes asociadas a una obra
class ImagenObra(BaseModel):
    id_imagen = AutoField()
    obra = ForeignKeyField(Obra, backref="imagenes")  # Cada imagen pertenece a una obra
    url = CharField()                                 # Dirección de la imagen

    def __str__(self):
        return f"Imagen: {self.url}"

    class Meta:
        db_table = "imagenes"

# Bloque principal: crea las tablas si se ejecuta este archivo directamente
if __name__ == "__main__":
    try:
        db.connect()  # Conexión a la base
        # Crear todas las tablas si no existen
        db.create_tables([
            Entorno, Etapa, TipoIntervencion, AreaResponsable,
            Comuna, Barrio, Empresa, Licitacion,
            Financiamiento, Obra, ImagenObra
        ])
    except OperationalError as e:
        print("No se pudo conectar a la base:", e)
    finally:
        db.close()  # Cierra la conexión
