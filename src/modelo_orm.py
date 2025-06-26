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
            print("El tipo de intervención ingresada no existe.")

        try:
            barrioObra = Barrio.get(Barrio.barrio == barrio)
            self.id_barrio = barrioObra.id_barrio
        except DoesNotExist:
            print("El tipo de intervención ingresada no existe.")

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
         
    def rescindir_obra(self):
        etapa = Etapa.get(Etapa.etapa == "Rescisión")
        self.id_etapa = etapa.id_etapa 
       
    def dibujar_mapa(self):
        df = pd.read_csv('data/observatorio-de-obras-urbanas.csv')

        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df['lng'], df['lat']),
            crs='EPSG:4326'  # Sistema WGS84 (lat/lon)
        )

        gdf = gdf.to_crs(epsg=3857)

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 10))

        # Dibujar puntos
        gdf.plot(ax=ax, color='red', markersize=50)

        # Agregar mapa base (OpenStreetMap)
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

        # Opcional: ajustar vista al extento de tus datos
        ax.set_axis_off()
        plt.show()

    def __str__(self):
        return f"Obra {self.nombre}"

    class Meta:
        db_table = "obras"


def main():
    print("Ejecutandose el programa")

    if not db.is_closed():
        db.close()


#     db.connect()
#     db.create_tables([
#         Entorno,
#         Etapa,
#         TipoIntervencion,
#         AreaResponsable,
#         Comuna,
#         Barrio,
#         Empresa,
#         Contratacion,
#         Financiamiento,
#         Ubicacion,
#         Obra
#     ])

    # obra = Obra(
    #     nombre="Ampliación del Hospital Central",
    #     descripcion="Obra de ampliación y remodelación del área de emergencias y quirófanos.",
    #     monto_contrato=14500000.50,
    #     plazo_meses=18,
    #     porcentaje_avance=45,
    #     mano_obra=120,
    #     id_entorno=1
    # )

# #     # Suponiendo que ya tienes:
# # # bd = sqlite3.connect("obras_urbanas.db")
    # cur = db.cursor()

#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Finalizada',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Rescisión',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En licitación',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Neutralizada',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En obra',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Desestimada',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Finalizada/desestimada',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En ejecución',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En curso',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Paralizada',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Proyecto finalizado',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En Ejecución ',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Adjudicada',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En proyecto',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En armado de pliegos',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('En Obra',))
#     cur.execute("INSERT INTO etapas (etapa) VALUES (?)", ('Anteproyecto',))

#     # Lista limpia y normalizada
#     barrios_unicos = [
#         "Villa Urquiza",
#         "Montserrat",
#         "San Nicolás",
#         "Villa Lugano",
#         "Villa Soldati",
#         "Puerto Madero",
#         "Recoleta",
#         "Liniers",
#         "Villa Riachuelo",
#         "Coghlan",
#         "La Boca",
#         "Belgrano",
#         "Parque Patricios",
#         "Barracas",
#         "Palermo",
#         "Saavedra",
#         "Villa del Parque",
#         "Almagro",
#         "Villa Devoto",
#         "Villa Pueyrredón",
#         "Agronomía",
#         "San Cristóbal",
#         "Balvanera",
#         "Flores",
#         "Villa Luro",
#         "Chacarita",
#         "Parque Avellaneda",
#         "Mataderos",
#         "Paternal",
#         "Caballito",
#         "Monte Castro",
#         "Floresta",
#         "Parque Chacabuco",
#         "Constitución",
#         "Nueva Pompeya",
#         "Villa General Mitre",
#         "Boedo",
#         "Nuñez",
#         "Villa Crespo",
#         "Colegiales",
#         "Retiro",
#         "San Telmo",
#         "Vélez Sarsfield",
#         "Villa Real",
#         "Villa Santa Rita",
#         "Versalles",
#         "Parque Chas",
#         "Villa Ortúzar",
#         "Marcos Paz"
#     ]

#     # Insertar en bloque
#     with db.atomic():
#         Barrio.insert_many([{'barrio': b} for b in barrios_unicos]).execute()

#     print("✅ Barrios insertados correctamente.")

#     # Lista normalizada
#     areas_responsables = [
#         "Ministerio de Educación",
#         "Secretaría de Transporte y Obras Públicas",
#         "Corporación Buenos Aires Sur",
#         "Instituto de la Vivienda",
#         "Ministerio de Salud",
#         "Subsecretaría de Gestión Comunal",
#         "Ministerio de Cultura",
#         "Ministerio de Espacio Público e Higiene Urbana",
#         "Ministerio de Desarrollo Humano y Hábitat",
#         "Subsecretaría de Proyectos y Obras",
#         "Ministerio de Seguridad",
#         "Ministerio de Infraestructura"
#     ]

#     # Insertar en bloque
#     with db.atomic():
#         AreaResponsable.insert_many([{'area_nombre': a} for a in areas_responsables]).execute()

#     print("✅ Áreas responsables insertadas correctamente.")

# #Lista limpia de tipos de intervención
#     tipos = [
#         "Escuelas",
#         "Espacio Público",
#         "Vivienda",
#         "Hidráulica e Infraestructura",
#         "Arquitectura",
#         "Transporte",
#         "Salud",
#         "Vivienda Nueva",
#         "Instalaciones",
#         "Ingenieria",
#         "Patio de Juegos",
#         "Infraestructura",
#         "Hidraulica"
#     ]

#     # Abre conexión segura
#     if db.is_closed():
#         db.connect()

#     # Inserta cada tipo si no existe ya
#     for tipo in tipos:
#         TipoIntervencion.get_or_create(tipo=tipo)



#     # Lista limpia
#     valores_validos = [
#         "Licitación Pública",
#         "Contratación Directa",
#         "Licitación Privada",
#         "Licitación Privada de Obra Menor",
#         "Obra menor",
#         "Sin efecto",
#         "Adicional de Mantenimiento",
#         "Anexo contratación mantenimiento",
#         "Contratacion Menor",
#         "Licitación Pública Nacional",
#         "Compulsa privada de precios",
#         "Licitación Pública Internacional",
#         "Obra Publica",
#         "Contratación de varias empresas",
#         "Contratacion",
#         "Licitación Pública de etapa múltiple",
#         "LPU",
#         "Convenio",
#         "Obra de emergencia",
#         "Licitación Pública Abreviada",
#         "Donación",
#         "Desestimada",
#         "Reconocimiento de Servicio",
#         "LICITACIÓN PÚBLICA BAC"
#     ]

#     # Insertar uno a uno
#     for valor in valores_validos:
#         Contratacion.create(tipo=valor)

#     # Lista depurada de nombres únicos
#     nombres_empresas = [
#         "Criba S.A.",
#         "Altote S.A.",
#         "Rol Ingenieria S.A.",
#         "Dal Construcciones S.A.",
#         "EMACO S.A.",
#         "Bricons S.A.I.C.F.I.",
#         "Dycasa S.A.",
#         "Cunumi S.A.",
#         "Constructora Sudamericana S.A.",
#         "Vidogar Construcciones S.A.",
#         "Cavcon S.A.",
#         "Calello Hermanos S.A.",
#         "Salvatori S.A. Parques y Jardines",
#         "Tecma S.A.",
#         "Conorvial S.A.",
#         "Niro Construcciones S.A.",
#         "Bosquimano S.A.",
#         "CM Construcciones S.A.",
#         "MIAVASA S.A.",
#         "Urban Baires S.A.",
#         "Corsan Corviam Construcción S.A.",
#         "Green S.A.",
#         "Iecsa - Fontana Nicastro UTE",
#         "SES S.A.",
#         "Teximco S.A.",
#         "Riva S.A.",
#         "Construcciones Ingevial S.A.",
#         "Eleprint S.A.",
#         "Construcciones, Infraestructura y Servicios S.A.",
#         "Sunil S.A.",
#         "Fontana Nicastro S.A.C.",
#         "Jose Chediack S.A.I.C.A.",
#         "Benito Roggio S.A.",
#         "Constructora Premart S.R.L.",
#         "Mercovial S.A.",
#         "Ingecons S.A.",
#         "Naku Construcciones S.R.L.",
#         "Instalectro S.A.",
#         "Ecosan S.A.",
#         "Dragonair S.A.",
#         "Villarex S.A.",
#         "Alupal Aberturas S.A.",
#         "Incesanit",
#         "CA Group S.A.",
#         "Construcciones Industriales Avellaneda S.A.",
#         "Kir S.R.L.",
#         "Inapcon S.A.",
#         "Ernesto Tarnousky S.A.",
#         "Listo Soluciones S.R.L.",
#         "Cahem S.A.",
#         "Warlet S.A.",
#         "Lanusse",
#         "Silk Tech S.R.L.",
#         "Tala Construcciones S.A.",
#         "Creazy S.A.",
#         "Kion S.A.",
#         "Mejoramiento Hospitalario S.A.",
#         "Mig S.A.",
#         "Grupo Viarsa S.A.",
#         "Indaltec S.A.",
#         "Cooperativa de Trabajo La Unica Ltda.",
#         "Casa Macchi S.A.",
#         "Vap Construcciones S.R.L.",
#         "Rassa Construcciones S.R.L.",
#         "Eduardo Caramian S.A.C.I.C.I.F.Y.A.",
#         "Ajimez",
#         "Pecam",
#         "Sol Yewen Ltda.",
#         "Obra realizada con personal propio",
#         "Ediser S.R.L.",
#         "Prodmobi S.A.",
#         "Punto H S.A.",
#         "Industrias Mas S.R.L.",
#         "Sergio Marcelo Bolzan",
#         "Lemme Obras Civiles S.R.L.",
#         "Rs Montajes y Obras S.R.L.",
#         "Ingenor S.A.",
#         "Pelque S.A.",
#         "Avinco Construcciones S.A.",
#         "Da Fré Obras Civiles S.A.",
#         "Desarrolladora Los Tilos S.A.",
#         "Hit Construcciones S.A.",
#         "Teximco S.A.",
#         "Ilubaires S.A.",
#         "Dasa S.A.",
#         "Ricavial S.A.",
#         "Philips Argentina S.A.",
#         "Sehos S.A.",
#         "Cooperativa de Trabajo Greti Ltda.",
#         "Algieri S.A.",
#         "Restec Argentina S.A.",
#         "Varsovia S.A.",
#         "Construmex S.A.",
#         "Sur Construcciones y Cía S.A.",
#         "Pose S.A.",
#         "Logistical S.A.",
#         "Garbin S.A.",
#         "Blue Steel S.A.",
#         "Salvatori S.A.",
#         "Urbaser Argentina S.A.",
#         "Construcciones de Hormigón S.A.",
#         "Construcciones Infraestructura y Servicios S.A."
#     ]

#     # Insertar de forma segura
#     with db.atomic():
#         for nombre in nombres_empresas:
#             Empresa.create(nombre=nombre, cuit="")  # Agrega CUIT si lo tienes, aquí se deja vacío


#     # Lista de fuentes de financiamiento (limpia)
#     fuentes = [
#         "Fuente 11",
#         "Préstamo BIRF 8706-AR",
#         "Préstamo BID AR-L1260",
#         "Nación",
#         "F11",
#         "PPI",
#         "Nación-GCBA",
#         "GCBA",
#         "CAF-Nación-GCBA",
#         "Fuente 14",
#         "FODUS"
#     ]

#     # Insertar de forma atómica
#     with db.atomic():
#         for fuente in fuentes:
#             Financiamiento.create(fuente=fuente)
#         obra = Obra.get(Obra.id_obra == 1)

    # queryDelete = Obra.delete().where(Obra.id_obra == 3)
    # queryDelete.execute()

    obra = Obra.get_by_id(1)

    # obra.nuevo_proyecto("Vivienda", "Instituto de la Vivienda", "Caballito")

    # obra.iniciar_contratacion("Obra menor", "LP-12345-2025")

    obra.dibujar_mapa()






    

if __name__ == "__main__":
    main()