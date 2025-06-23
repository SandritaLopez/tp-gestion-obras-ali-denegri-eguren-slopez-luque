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
    CSV_PATH = "./data/observatorio-de-obras-urbanas.csv"

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
        print("Proceso de carga finalizado")



    '''
    4. f.	nueva_obra(), que debe incluir las sentencias necesarias para crear nuevas instancias de Obra. 
    Se deben considerar los siguientes requisitos: 
    •	Todos los valores requeridos para la creación de estas nuevas instancias deben ser ingresados por teclado. 
    •	Para los valores correspondientes a registros de tablas relacionadas (foreign key), 
    el valor ingresado debe buscarse en la tabla correspondiente mediante sentencia de búsqueda ORM, 
    para obtener la instancia relacionada, si el valor ingresado no existe en la tabla, 
    se le debe informar al usuario y solicitarle un nuevo ingreso por teclado. 
    •	Para persistir en la BD los datos de la nueva instancia de Obra debe usarse el método save() 
    de Model del módulo “peewee”. 
    •	Este método debe retornar la nueva instancia de obra. 
    '''
    @classmethod
    def nueva_obra(cls):
        db = cls.conectar_db()
        db.connect()

        def pedir_instancia(modelo, campo):
            while True:
                valor = input(f"Ingrese {campo}: ").strip().title()
                try:
                    instancia = modelo.get(getattr(modelo, campo) == valor)
                    return instancia
                except modelo.DoesNotExist:
                    print(f"No se encontró {valor} en la tabla {modelo.__name__}. Intente de nuevo.")

        entorno = pedir_instancia(Entorno, 'entorno')
        tipo_intervencion = pedir_instancia(TipoIntervencion, 'tipo')
        area_responsable = pedir_instancia(AreaResponsable, 'area_nombre')
        comuna = pedir_instancia(Comuna, 'comuna')
        barrio = pedir_instancia(Barrio, 'barrio')
        etapa = pedir_instancia(Etapa, 'etapa')
        licitacion = pedir_instancia(Licitacion, 'nro_contratacion')
        financiamiento = pedir_instancia(Financiamiento, 'fuente')

        nombre = input("Ingrese nombre de la obra: ").strip()
        descripcion = input("Ingrese descripción: ").strip()
        direccion = input("Ingrese dirección: ").strip()
        lat = float(input("Ingrese latitud: "))
        lng = float(input("Ingrese longitud: "))
        fecha_inicio = input("Ingrese fecha de inicio (YYYY-MM-DD): ")
        fecha_fin_inicial = input("Ingrese fecha fin estimada (YYYY-MM-DD): ")
        plazo_meses = int(input("Ingrese plazo estimado en meses: "))
        porcentaje_avance = int(input("Ingrese porcentaje de avance: "))
        beneficiarios = input("Ingrese beneficiarios: ").strip()
        mano_obra = int(input("Ingrese cantidad de mano de obra: "))
        compromiso = input("¿Tiene compromiso? (s/n): ").lower() == 's'
        destacada = input("¿Es destacada? (s/n): ").lower() == 's'
        ba_elige = input("¿Pertenece a BA Elige? (s/n): ").lower() == 's'
        link_interno = input("Link interno: ")
        pliego = input("Pliego descarga: ")
        estudio = input("Estudio ambiental descarga: ")

        obra = Obra(
            entorno=entorno,
            tipo_intervencion=tipo_intervencion,
            area_responsable=area_responsable,
            comuna=comuna,
            barrio=barrio,
            etapa=etapa,
            licitacion=licitacion,
            financiamiento=financiamiento,
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            lat=lat,
            lng=lng,
            fecha_inicio=fecha_inicio,
            fecha_fin_inicial=fecha_fin_inicial,
            plazo_meses=plazo_meses,
            porcentaje_avance=porcentaje_avance,
            beneficiarios=beneficiarios,
            mano_obra=mano_obra,
            compromiso=compromiso,
            destacada=destacada,
            ba_elige=ba_elige,
            link_interno=link_interno,
            pliego_descarga=pliego,
            estudio_ambiental_descarga=estudio
        )

        obra.save()
        db.close()
        print(f"Obra creada con ID: {obra.id_obra}")
        return obra
    

    '''
    4. g.	obtener_indicadores(), que debe incluir las sentencias necesarias para obtener 
    información de las obras existentes en la base de datos SQLite a través de sentencias ORM. 
    '''
    '''
    17.	Para finalizar la ejecución del programa, se debe invocar al método de 
    clase GestionarObra.obtener_indicadores() 
    para obtener y mostrar por consola la siguiente información: 
    '''
    @classmethod
    def obtener_indicadores(cls):
        db = cls.conectar_db()
        db.connect()

        print("\n Indicadores:")

        # a. Áreas responsables
        print("\nÁreas responsables:")
        for area in AreaResponsable.select():
            print("-", area.area_nombre)

        # b. Tipos de intervención
        print("\nTipos de obra:")
        for tipo in TipoIntervencion.select():
            print("-", tipo.tipo)

        # c. Cantidad por etapa
        print("\nCantidad de obras por etapa:")
        for etapa in Etapa.select():
            cantidad = Obra.select().where(Obra.etapa == etapa).count()
            print(f"{etapa.etapa}: {cantidad} obras")

        # d. Obras y monto total por tipo de obra
        print("\nCantidad de obras y monto total por tipo de obra:")
        for tipo in TipoIntervencion.select():
            obras = Obra.select().where(Obra.tipo_intervencion == tipo)
            total = sum([obra.licitacion.empresa.id_empresa for obra in obras if obra.licitacion])
            print(f"{tipo.tipo}: {obras.count()} obras - Total ID empresas (ejemplo): {total}")

        # e. Barrios de comunas 1, 2 y 3
        print("\nBarrios de las comunas 1, 2 y 3:")
        for barrio in Barrio.select().join(Obra).join(Comuna).where(Comuna.comuna.in_(['1', '2', '3'])).distinct():
            print("-", barrio.barrio)

        # f. Obras finalizadas en 24 meses o menos
        print("\nObras finalizadas en 24 meses o menos:")
        obras_finalizadas = Obra.select().where(
            (Obra.plazo_meses <= 24) & (Obra.etapa.etapa == "Finalizada")
        )
        print(f"{obras_finalizadas.count()} obras")

        # g. Monto total de inversión (simulado)
        print("\nMonto total de inversión: (no hay campo monto, reemplazar cuando esté disponible)")

        db.close()

# Nota: Este script asume que el archivo CSV y la base de datos están en las rutas especificadas.
if __name__ == "__main__":
    # 1) Crear (o actualizar) las tablas
    GestionarObra.mapear_orm()

    # 2) Leer y limpiar el CSV
    df = GestionarObra.extraer_datos()
    df_limpio = GestionarObra.limpiar_datos(df)

    # 3) Persistir en la BD (aquí es donde pusiste los prints)
    GestionarObra.cargar_datos(df_limpio)
