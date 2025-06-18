# Importamos todo lo necesario del módulo peewee
from peewee import *

# Conexión a la base de datos SQLite llamada "obras_urbanas.db"
# usamos SqliteDatabase para manejar la base de datos
# esto también crea la base de datos si no existe
db = SqliteDatabase("obras_urbanas.db")

# Clase base para todos los modelos: define que usarán la misma base de datos
# BaseModel es una clase que hereda de Model de peewee
# y establece la conexión a la base de datos
class BaseModel(Model):
    class Meta:
        database = db

# La estructura sigue el modelo relacional, pero adaptada a clases y atributos en Python con Peewee.

# Tabla "Entorno": describe el entorno de una obra (por ejemplo, urbano, rural)
class Entorno(BaseModel):
    id_entorno = AutoField()  # Clave primaria autoincremental
    entorno = CharField()     # Nombre del entorno

# Tabla "Etapa": indica en qué etapa está la obra (proyecto, ejecución, finalizada, etc.)
class Etapa(BaseModel):
    id_etapa = AutoField()
    etapa = CharField()

# Tabla "TipoIntervencion": tipo de intervención que se hace en la obra (mantenimiento, construcción, etc.)
class TipoIntervencion(BaseModel):
    id_tipo_intervencion = AutoField()
    tipo = CharField()

# Tabla "AreaResponsable": área del gobierno responsable de la obra
class AreaResponsable(BaseModel):
    id_area = AutoField()
    area_nombre = CharField()

# Tabla "Comuna": comuna donde se ubica la obra (1 a 15 en CABA)
class Comuna(BaseModel):
    id_comuna = AutoField()
    comuna = CharField()

# Tabla "Barrio": barrio donde se encuentra la obra
class Barrio(BaseModel):
    id_barrio = AutoField()
    barrio = CharField()

# Tabla "Empresa": empresas que se presentaron en las licitaciones
class Empresa(BaseModel):
    id_empresa = AutoField()
    nombre = CharField()
    cuit = CharField()

# Tabla "Licitacion": información sobre la contratación de la obra
class Licitacion(BaseModel):
    id_licitacion = AutoField()
    nro_contratacion = CharField()
    anio = IntegerField()
    tipo = CharField()
    expediente_numero = CharField()
    empresa = ForeignKeyField(Empresa, backref="licitaciones")  # Relación con Empresa

# Tabla "Financiamiento": fuente de financiamiento de la obra (nacional, internacional, etc.)
class Financiamiento(BaseModel):
    id_financiamiento = AutoField()
    fuente = CharField()

# Tabla principal "Obra": representa una obra urbana con sus datos y relaciones
class Obra(BaseModel):
    id_obra = AutoField()
    entorno = ForeignKeyField(Entorno, backref="obras")
    nombre = CharField()
    descripcion = TextField(null=True)
    direccion = CharField(null=True)
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    fecha_inicio = DateField(null=True)
    fecha_fin_inicial = DateField(null=True)
    plazo_meses = IntegerField(null=True)
    porcentaje_avance = IntegerField(null=True)
    tipo_intervencion = ForeignKeyField(TipoIntervencion, backref="obras")
    area_responsable = ForeignKeyField(AreaResponsable, backref="obras")
    comuna = ForeignKeyField(Comuna, backref="obras")
    barrio = ForeignKeyField(Barrio, backref="obras")
    licitacion = ForeignKeyField(Licitacion, backref="obras")
    financiamiento = ForeignKeyField(Financiamiento, backref="obras")
    beneficiarios = TextField(null=True)
    mano_obra = IntegerField(null=True)
    compromiso = BooleanField(default=False)
    destacada = BooleanField(default=False)
    ba_elige = BooleanField(default=False)
    link_interno = CharField(null=True)
    pliego_descarga = CharField(null=True)
    estudio_ambiental_descarga = CharField(null=True)

# Tabla "ImagenObra": guarda las URLs de imágenes asociadas a una obra
class ImagenObra(BaseModel):
    id_imagen = AutoField()
    obra = ForeignKeyField(Obra, backref="imagenes")
    url = CharField()

# Bloque principal de ejecución (opcional): crea las tablas se ejecuta este archivo directamente
if __name__ == "__main__":
    db.connect()
    db.create_tables([
        Entorno, Etapa, TipoIntervencion, AreaResponsable,
        Comuna, Barrio, Empresa, Licitacion,
        Financiamiento, Obra, ImagenObra
    ])
    db.close()
