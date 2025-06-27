 # Importamos todo lo necesario del módulo peewee (ORM liviano para Python)
from peewee import *
import random
from datetime import datetime
import pandas as pd
#import geopandas as gpd
#import matplotlib.pyplot as plt
#import contextily as ctx

# Definimos la base de datos SQLite que se usará
db = SqliteDatabase("obras_urbanas2.db")

# Clase base de la que heredarán todos los modelos, asigna la base de datos
class BaseModel(Model):
    class Meta:
        database = db

# Tabla de entornos (urbano, natural, etc.)
class Entorno(BaseModel):
    id_entorno = AutoField()  # Clave primaria autoincremental
    entorno = CharField()     # Nombre del entorno

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
    id_comuna = ForeignKeyField(Comuna, null=True, backref="barrios")

    def __str__(self):
        return f"Barrio {self.barrio}"

    class Meta:
        db_table = "barrios"

# Tabla con información de empresas contratadas
class Empresa(BaseModel):
    id_empresa = AutoField()
    nombre = CharField()  # Nombre de la empresa
    cuit = CharField(null=True)    # CUIT de la empresa

    def __str__(self):
        return f"Empresa {self.nombre}"

    class Meta:
        db_table = "empresas"

# Tabla de licitaciones (procesos de contratación)
class Contratacion(BaseModel):
    id_contratacion = AutoField()
    tipo = CharField()                   # Tipo de contratacion

    def __str__(self):
        return f"Licitación {self.expediente_numero}"

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


class Ubicacion(BaseModel):
    id_ubicacion = AutoField()
    direccion = CharField(null=True)
    lat = FloatField(null=True)
    long = FloatField(null=True)

    def __str__(self):
      return f"Ubicación (Dirección) {self.direccion}"

    class Meta:
        db_table = "ubicacion"
    

# Tabla principal de obras
class Obra(BaseModel):
    id_obra = AutoField()
    nombre = CharField()
    descripcion = CharField(null=True)
    monto_contrato = FloatField(null=True)
    plazo_meses = IntegerField(null=True)
    fecha_inicio = DateField(null=True)
    fecha_fin_inicial = DateField(null=True)
    porcentaje_avance = IntegerField(null=True)
    mano_obra = IntegerField(null=True)
    nro_expediente = CharField(null=True)
    nro_contratacion = CharField(null=True)
    esDestacada = BooleanField(null=True)
    id_contratacion = ForeignKeyField(Contratacion, null=True, backref="obras")
    id_entorno = ForeignKeyField(Entorno, null=True, backref="obras")
    id_tipo_intervencion = ForeignKeyField(TipoIntervencion, null=True, backref="obras")
    id_etapa = ForeignKeyField(Etapa, null=True, backref="obras")
    id_area_responsable = ForeignKeyField(AreaResponsable, null=True, backref="obras")
    id_ubicacion = ForeignKeyField(Ubicacion, null=True, backref="obras")
    id_empresa = ForeignKeyField(Empresa, null=True, backref="obras")
    id_barrio = ForeignKeyField(Barrio, null = True, backref="obras")
    id_financiamiento = ForeignKeyField(Financiamiento, null=True, backref="obras")

    def nuevo_proyecto(self, tipoIntervencion, areaResponsable, barrio):

        existe = Etapa.select().where(Etapa.etapa == "Proyecto").first()
        if existe == None:
            Etapa.create(
                etapa="Proyecto"
            )

        etapa = Etapa.get(Etapa.etapa == "Proyecto")
        print(etapa.id_etapa)
        self.id_etapa = etapa.id_etapa

        try:
            intervencion = TipoIntervencion.get(TipoIntervencion.tipo == tipoIntervencion)
            self.id_tipo_intervencion = intervencion.id_tipo_intervencion
        except DoesNotExist:
            print("El tipo de intervención ingresada no existe.")

        try:
            area = AreaResponsable.get(AreaResponsable.area_nombre == areaResponsable)
            self.id_area_responsable = area.id_area
        except DoesNotExist:
            print("El area responsable ingresada no existe.")

        try:
            barrioObra = Barrio.get(Barrio.barrio == barrio)
            self.id_barrio = barrioObra.id_barrio
        except DoesNotExist:
            print("El barrio ingresado no existe.")

        self.save() 

    def iniciar_contratacion(self, contratacion, nroContratacion):
        print("Buscando tipo de contratación")
        try:
            contrat = Contratacion.get(Contratacion.tipo == contratacion)
            self.id_contratacion = contrat.id_contratacion
            self.nro_contratacion = nroContratacion
        except DoesNotExist:
            print("No se encontró el tipo de contratación")

        self.save()
    
    def generar_numExpediente (self):
        print("Generando número de expediente")
        expediente =[]
        expediente.append("EX")

        numeros = list(range(8))
        random.shuffle(numeros)
        num_a_str = [str(num) for num in numeros]
        numJoined = "".join(num_a_str)
        expediente.append(numJoined)

        iniciales = ""

        if self.id_area_responsable:
            nombre = self.id_area_responsable.area_nombre
            iniciales = ""
            for palabra in nombre.split():
                iniciales+=palabra[0]
        else:
            print("Sin área asignada")
        
        expediente.append(iniciales)
        nro_exp = "-".join(expediente)
        print(nro_exp)
        return nro_exp

    def adjudicar_obra(self, empresa):

        try:
            empresa_adjudicar = Empresa.get(Empresa.nombre == empresa)
            self.id_empresa = empresa_adjudicar.id_empresa
            self.nro_expediente = self.generar_numExpediente()
        except DoesNotExist:
            print("No se encontró la empresa")

        self.save()
        
    def iniciar_obra(self, esDestacada, fechaInicio, fechaFinInicial, fuenteFinanc, manoObra):

        self.esDestacada = esDestacada
        if isinstance(fechaInicio, str):
            fechaInicio = datetime.strptime(fechaInicio, "%Y-%m-%d").date()

        if isinstance(fechaFinInicial, str):
            fechaFinInicial = datetime.strptime(fechaFinInicial, "%Y-%m-%d").date()

        if fechaFinInicial < fechaInicio:
            print("La fecha estimada para el fin de la obra no puede ser menor a la fecha de inicio.")
        else:
            self.fechaInicio = fechaInicio
            self.fecha_fin = fechaFinInicial

        self.mano_obra = manoObra

        try:
            fuente = Financiamiento.get(Financiamiento.fuente == fuenteFinanc)
            self.id_financiamiento = fuente.id_financiamiento
        except DoesNotExist:
            print("La fuente de financiamiento no existe.")

        self.save()
 
    def actualizar_porcentaje_avance(self, nuevoPorcentaje):

        if self.porcentaje_avance > nuevoPorcentaje:
            print("El porcentaje de avance ingresado no puede ser menor al existente")
        else:
            self.porcentaje_avance = nuevoPorcentaje
 
    def incrementar_plazo(self, nuevoPlazo):

        if self.plazo_meses > nuevoPlazo:
            print("El plazo no puede ser menor al existente")
        else:
            self.plazo_meses = nuevoPlazo
            print("Se actualizó la mano de obra")
        
        self.save()
         
    def incrementar_mano_obra(self, incrementoManoObra):

        if incrementoManoObra <= 0:
            print("La cantidad de mano de obra a agregar no puede ser 0 ni menor a 0")
        else:
            self.mano_obra = incrementoManoObra
            print("Se actualizó la mano de obra")
        
        self.save()
 
    def finalizar_obra(self):
        etapa = Etapa.get(Etapa.etapa == "Finalizada")
        self.id_etapa = etapa.id_etapa

        self.porcentaje_avance = 100

        self.save()
         
    def rescindir_obra(self):
        etapa = Etapa.get(Etapa.etapa == "Rescisión")
        self.id_etapa = etapa.id_etapa 

        self.save()
       
    def __str__(self):
        return f"Obra {self.nombre}"

    class Meta:
        db_table = "obras"


