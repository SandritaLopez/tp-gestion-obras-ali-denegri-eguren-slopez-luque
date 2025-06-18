# gestionar_obras.py

# Importamos la librería pandas, que se usa para trabajar con estructuras de datos como DataFrames (especialmente CSVs)
import pandas as pd

# Importamos herramientas para definir clases abstractas en Python
# ABC = Abstract Base Class (clase base abstracta)
# abstractmethod = decorador para obligar a las subclases a implementar ciertos métodos
from abc import ABC, abstractmethod

# Importamos SqliteDatabase de peewee, que nos permite conectarnos a bases de datos SQLite
from peewee import SqliteDatabase

# Importamos los modelos ORM que definimos en el archivo modelo_orm.py
# Estas clases representan las tablas de tu base de datos
from modelo_orm import (
    BaseModel,         # Clase base de la que heredan todos los modelos
    Obra,              # Tabla principal: información de obras urbanas
    Entorno,           # Tabla de características del entorno de la obra
    Etapa,             # Etapa del proyecto (por ejemplo: planificación, ejecución, etc.)
    TipoIntervencion,  # Tipo de intervención (construcción, mejora, mantenimiento, etc.)
    AreaResponsable,   # Área del gobierno u organización responsable de la obra
    Comuna,            # Comuna donde se realiza la obra
    Barrio,            # Barrio correspondiente
    Empresa,           # Empresa que ejecuta la obra
    Licitacion,        # Datos sobre licitaciones asociadas
    Financiamiento,    # Fuente de financiamiento de la obra
    ImagenObra         # Imágenes asociadas a la obra (si hay)
)

# Definimos una clase abstracta que servirá como base para implementar la lógica de carga/gestión de obras
class GestionarObra(ABC):
    # Ruta al archivo de la base de datos SQLite
    DB_PATH = "obras_urbanas.db"

    # Ruta al archivo CSV que contiene el dataset original
    CSV_PATH = "../data/observatorio-de-obras-urbanas.csv"

    # Separador usado en el CSV (en este caso punto y coma, porque es un CSV "europeo/latino")
    SEP = ";"

    # Codificación de caracteres del archivo CSV (latin1 admite tildes, ñ, etc.)
    ENCODING = "latin1"


    @classmethod
    def extraer_datos(cls) -> pd.DataFrame:
        """
        Carga el CSV en un DataFrame de pandas.
        """
        df = pd.read_csv(cls.CSV_PATH, sep=cls.SEP, encoding=cls.ENCODING)
        return df

    @classmethod
    def conectar_db(cls) -> SqliteDatabase:
        """
        Conecta con la base de datos SQLite y la retorna.
        """
        db = SqliteDatabase(cls.DB_PATH)
        BaseModel._meta.database = db
        return db

    @classmethod
    def mapear_orm(cls):
        """
        Crea las tablas en la base, según los modelos de Peewee.
        """
        db = cls.conectar_db()
        db.connect()
        # Lista todas las clases de modelos que queremos crear
        modelos = [
            Entorno, Etapa, TipoIntervencion, AreaResponsable,
            Comuna, Barrio, Empresa, Licitacion, Financiamiento,
            Obra, ImagenObra
        ]
        db.create_tables(modelos)
        db.close()

    @classmethod
    def limpiar_datos(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza limpieza básica del DataFrame:
          - Elimina columnas 'Unnamed'
          - Quita espacios en nombres de columna
          - Convierte tipos de datos básicos
        """
        # 1) Eliminar columnas vacías
        cols_a_eliminar = [c for c in df.columns if c.startswith("Unnamed")]
        df = df.drop(columns=cols_a_eliminar)

        # 2) Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # 3) Conversión de tipos
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'], dayfirst=True, errors='coerce')
        df['fecha_fin_inicial'] = pd.to_datetime(df['fecha_fin_inicial'], dayfirst=True, errors='coerce')
        for col in ['monto_contrato', 'plazo_meses', 'porcentaje_avance', 'mano_obra']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 4) Limpieza de texto en categorías
        for cat in ['entorno', 'etapa', 'tipo', 'area_responsable',
                    'comuna', 'barrio', 'contratacion_tipo', 'financiamiento']:
            if cat in df.columns:
                df[cat] = df[cat].astype(str).str.strip().str.title()

        return df



    @classmethod
    def cargar_datos(cls, df: pd.DataFrame):
        db = cls.conectar_db()
        db.connect()

        for idx, row in df.iterrows():
           # print(f"→ Fila {idx}: nombre={row['nombre']!r}")   # muestra cada intento
            try:
                entorno_obj, _ = Entorno.get_or_create(entorno=row['entorno'])
                etapa_obj, _   = Etapa.get_or_create(etapa=row['etapa'])
                tipo_int_obj,_ = TipoIntervencion.get_or_create(tipo=row['tipo'])
                area_obj, _    = AreaResponsable.get_or_create(area_nombre=row['area_responsable'])
                comuna_obj, _  = Comuna.get_or_create(comuna=row['comuna'])
                barrio_obj, _  = Barrio.get_or_create(barrio=row['barrio'])
                empresa_obj,_  = Empresa.get_or_create(
                    nombre=row['licitacion_oferta_empresa'],
                    cuit=row.get('cuit_contratista') or ""
                )
                licit_obj, _   = Licitacion.get_or_create(
                    nro_contratacion=row['nro_contratacion'],
                    anio=row['licitacion_anio'],
                    tipo=row['contratacion_tipo'],
                    expediente_numero=row['expediente-numero'],
                    empresa=empresa_obj
                )
                financ_obj, _  = Financiamiento.get_or_create(fuente=row['financiamiento'])

                obra = Obra.create(
                    entorno=entorno_obj,
                    nombre=row['nombre'],
                    descripcion=row.get('descripcion') or "",
                    direccion=row.get('direccion') or "",
                    lat=row.get('lat'),
                    lng=row.get('lng'),
                    fecha_inicio=row.get('fecha_inicio'),
                    fecha_fin_inicial=row.get('fecha_fin_inicial'),
                    plazo_meses=row.get('plazo_meses'),
                    porcentaje_avance=row.get('porcentaje_avance'),
                    beneficiarios=row.get('beneficiarios') or "",
                    mano_obra=row.get('mano_obra'),
                    compromiso=bool(row.get('compromiso')),
                    destacada=bool(row.get('destacada')),
                    ba_elige=bool(row.get('ba_elige')),
                    link_interno=row.get('link_interno') or "",
                    pliego_descarga=row.get('pliego_descarga') or "",
                    estudio_ambiental_descarga=row.get('estudio_ambiental_descarga') or "",
                    etapa=etapa_obj,
                    tipo_intervencion=tipo_int_obj,
                    area_responsable=area_obj,
                    comuna=comuna_obj,
                    barrio=barrio_obj,
                    licitacion=licit_obj,
                    financiamiento=financ_obj
                )
              #  print(f"   Insertada Obra id={obra.id_obra}")
            except Exception as e:
                print(f"Error fila {idx}: {e}")

        db.close()
        print("🏁 Proceso de carga finalizado")



# Nota: Este script asume que el archivo CSV y la base de datos están en las rutas especificadas.
if __name__ == "__main__":
    # 1) Crear (o actualizar) las tablas
    GestionarObra.mapear_orm()

    # 2) Leer y limpiar el CSV
    df = GestionarObra.extraer_datos()
    df_limpio = GestionarObra.limpiar_datos(df)

    # 3) Persistir en la BD (aquí es donde pusiste los prints)
    GestionarObra.cargar_datos(df_limpio)
