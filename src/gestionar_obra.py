import pandas as pd
from abc import ABC, abstractmethod
from peewee import SqliteDatabase
from modelo_orm import (
    BaseModel, Obra, Entorno, Etapa, TipoIntervencion, AreaResponsable,
    Comuna, Barrio, Empresa, Contratacion, Financiamiento, Ubicacion
)
from datetime import datetime

class GestionarObra(ABC):
    DB_PATH = "obras_urbanas2.db"
    CSV_PATH = "data/observatorio-de-obras-urbanas.csv"
    SEP = ";"
    ENCODING = "latin1"

    @classmethod
    def extraer_datos(cls) -> pd.DataFrame:
        return pd.read_csv(cls.CSV_PATH, sep=cls.SEP, encoding=cls.ENCODING)

    @classmethod
    def conectar_db(cls) -> SqliteDatabase:
        db = SqliteDatabase(cls.DB_PATH)
        BaseModel._meta.database = db
        return db

    @classmethod
    def mapear_orm(cls, db):
        db = cls.conectar_db()
        db.connect()
        modelos = [
            Entorno, Etapa, TipoIntervencion, AreaResponsable,
            Comuna, Barrio, Empresa, Contratacion, Financiamiento,
            Obra, Ubicacion
        ]
        db.create_tables(modelos)
        db.close()

    @classmethod
    def limpiar_datos(cls, df: pd.DataFrame) -> pd.DataFrame:

            # 1. Eliminar columnas innecesarias y normalizar nombres de columnas
        cols_a_eliminar = [c for c in df.columns if c.startswith("Unnamed")]
        df = df.drop(columns=cols_a_eliminar)
        df.columns = df.columns.str.strip()

        # 2. Limpieza y transformación de columnas clave

        # → Normalizar 'destacada' como booleano
        df["destacada"] = df["destacada"].astype(str).str.lower().str.strip()
        df["destacada"] = df["destacada"].map(lambda x: x in ["si", "1", "true", "verdadero", "yes"])

        # → Convertir fechas
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'], dayfirst=True, errors='coerce')
        df['fecha_fin_inicial'] = pd.to_datetime(df['fecha_fin_inicial'], dayfirst=True, errors='coerce')

        # → Eliminar registros con datos fundamentales faltantes
        df.dropna(subset=["nombre", "etapa", "fecha_inicio", "fecha_fin_inicial"], inplace=True)

        # 3. Limpieza de monto_contrato (símbolos, formatos europeos, etc.)
        if "monto_contrato" in df.columns:
            df["monto_contrato"] = (
                df["monto_contrato"]
                .astype(str)
                .str.replace(r"[^\d,.-]", "", regex=True)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df["monto_contrato"] = pd.to_numeric(df["monto_contrato"], errors="coerce")

        # 4. Conversión y completado de valores numéricos
        df["plazo_meses"] = pd.to_numeric(df["plazo_meses"], errors="coerce")
        df["plazo_meses"] = df["plazo_meses"].fillna(round(df["plazo_meses"].mean()))

        df["mano_obra"] = pd.to_numeric(df["mano_obra"], errors="coerce").fillna(0)

        # 5. Reemplazo de nulos por valores por defecto (texto)
        texto_por_defecto = {
            "expediente-numero": "Sin especificar",
            "nro_contratacion": "Sin especificar",
            "tipo": "Sin especificar",
            "comuna": "Sin especificar",
            "barrio": "Sin especificar",
        }

        for col, valor in texto_por_defecto.items():
            if col in df.columns:
                df[col] = df[col].replace(".", valor).replace("", valor).fillna(valor)

        # 6. Limpieza especial de 'barrio'
        if "barrio" in df.columns:
            df = df[df["barrio"] != "."]
            df["barrio"] = (
                df["barrio"]
                .astype(str)
                .str.replace("Ã±", "ñ")
                .str.replace(r",|/| y | e ", "|", regex=True)
                .str.strip()
            )

        # 7. Limpieza de caracteres especiales en 'nombre'
        df["nombre"] = df["nombre"].str.replace("Â", "A")

        # 8. Normalización de valores categóricos
        categorias = [
            'entorno', 'etapa', 'tipo', 'area_responsable',
            'comuna', 'barrio', 'contratacion_tipo', 'financiamiento'
        ]
        for cat in categorias:
            if cat in df.columns:
                df[cat] = df[cat].astype(str).str.strip().str.title()

        return df

    @classmethod
    def cargar_datos(cls, df: pd.DataFrame):
        db = cls.conectar_db()
        db.connect()

        for idx, row in df.iterrows():
            try:
                entorno_obj, _ = Entorno.get_or_create(entorno=row['entorno'])
                etapa_obj, _ = Etapa.get_or_create(etapa=row['etapa'])
                tipo_int_obj, _ = TipoIntervencion.get_or_create(tipo=row['tipo'])
                area_obj, _ = AreaResponsable.get_or_create(area_nombre=row['area_responsable'])
                comuna_obj, _ = Comuna.get_or_create(comuna=row['comuna'])
                barrio_obj, _ = Barrio.get_or_create(barrio=row['barrio'])
                ubicacion_obj, _ = Ubicacion.get_or_create(
                    direccion=row.get('direccion'),
                    lat=row.get('lat'),
                    long=row.get('lng')
                )
                empresa_obj, _ = Empresa.get_or_create(
                    nombre=row['licitacion_oferta_empresa'],
                    cuit=row.get('cuit_contratista') or ""
                )
                contratacion_obj, _ = Contratacion.get_or_create(
                    tipo=row['contratacion_tipo'],
                )
                financ_obj, _ = Financiamiento.get_or_create(fuente=row['financiamiento'])

                Obra.create(
                    nombre=row['nombre'],
                    descripcion=row['descripcion'],
                    monto_contrato=row['monto_contrato'],
                    plazo_meses=row['plazo_meses'],
                    fecha_inicio=pd.to_datetime(row['fecha_inicio'], errors='coerce').date() if pd.notna(row['fecha_inicio']) else None,
                    fecha_fin_inicial=pd.to_datetime(row['fecha_fin_inicial'], errors='coerce').date() if pd.notna(row['fecha_fin_inicial']) else None,
                    porcentaje_avance=row['porcentaje_avance'],
                    mano_obra=row['mano_obra'],
                    nro_expediente=row.get('expediente-numero'),
                    nro_contratacion=row.get('nro_contratacion'),
                    esDestacada=bool(row['destacada']) if pd.notna(row['destacada']) else None,

                    id_contratacion=contratacion_obj.id_contratacion if contratacion_obj else None,
                    id_entorno=entorno_obj.id_entorno if entorno_obj else None,
                    id_tipo_intervencion=tipo_int_obj.id_tipo_intervencion if tipo_int_obj else None,
                    id_etapa=etapa_obj.id_etapa if etapa_obj else None,
                    id_area_responsable=area_obj.id_area if area_obj else None,
                    id_ubicacion=ubicacion_obj.id_ubicacion if ubicacion_obj else None,
                    id_empresa=empresa_obj.id_empresa if empresa_obj else None,
                    id_barrio=barrio_obj.id_barrio if barrio_obj else None,
                    id_financiamiento=financ_obj.id_financiamiento if financ_obj else None
        )
            except Exception as e:
                print(f"Error fila {idx}: {e}")

        db.close()
        print("🏁 Proceso de carga finalizado")



    @classmethod
    def nueva_obra(cls):
        db = cls.conectar_db()
        db.connect()

        def pedir_instancia(modelo, campo):
            while True:
                valor = input(f"Ingrese {campo}: ").strip().title()
                try:
                    return modelo.get(getattr(modelo, campo) == valor)
                except modelo.DoesNotExist:
                    print(f"No se encontró {valor} en la tabla {modelo.__name__}. Intente de nuevo.")

        # Relaciones foráneas
        entorno = pedir_instancia(Entorno, 'entorno')
        tipo_intervencion = pedir_instancia(TipoIntervencion, 'tipo')
        area_responsable = pedir_instancia(AreaResponsable, 'area_nombre')
        contratacion = pedir_instancia(Contratacion, 'tipo')  # Cambiar si usás otro campo
        financiamiento = pedir_instancia(Financiamiento, 'fuente')
        barrio = pedir_instancia(Barrio, 'barrio')
        ubicacion = pedir_instancia(Ubicacion, 'direccion')

        # Campos simples
        nombre = input("Nombre de la obra: ").strip()
        descripcion = input("Descripción: ").strip()
        monto_contrato = float(input("Monto del contrato: ") or 0)
        plazo_meses = int(input("Plazo (meses): ") or 0)
        fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("Fecha fin estimada (YYYY-MM-DD): ").strip()
        porcentaje_avance = int(input("Avance (%): ") or 0)
        mano_obra = int(input("Mano de obra: ") or 0)
        destacada = input("¿Es destacada? (s/n): ").lower().strip() == 's'

        obra = Obra.create(
            nombre=nombre,
            descripcion=descripcion,
            monto_contrato=monto_contrato,
            plazo_meses=plazo_meses,
            fecha_inicio=fecha_inicio if fecha_inicio else None,
            fecha_fin_inicial=fecha_fin if fecha_fin else None,
            porcentaje_avance=porcentaje_avance,
            mano_obra=mano_obra,
            nro_expediente=None,
            nro_contratacion=None,
            esDestacada=destacada,

            id_contratacion=contratacion.id_contratacion,
            id_entorno=entorno,
            id_tipo_intervencion=tipo_intervencion,
            id_etapa=None,
            id_area_responsable=area_responsable,
            id_ubicacion=ubicacion,
            id_empresa=None,
            id_barrio=barrio,
            id_financiamiento=financiamiento
        )

        db.close()
        print(f"✅ Obra creada con ID: {obra.id_obra}")
        return obra


    @classmethod
    def obtener_indicadores(cls):
        db = cls.conectar_db()
        db.connect()

        print("\n Indicadores:")

        print("\nÁreas responsables:")
        for area in AreaResponsable.select():
            print("-", area.area_nombre)

        print("\nTipos de obra:")
        for tipo in TipoIntervencion.select():
            print("-", tipo.tipo)

        print("\nCantidad de obras por etapa:")
        for etapa in Etapa.select():
            cantidad = Obra.select().where(Obra.id_etapa == etapa).count()
            print(f"{etapa.etapa}: {cantidad} obras")

        print("\nCantidad de obras y monto total por tipo de obra:")
        for tipo in TipoIntervencion.select():
            obras = Obra.select().where(Obra.id_tipo_intervencion == tipo)
            total = sum([obra.monto_contrato or 0 for obra in obras])
            print(f"{tipo.tipo}: {obras.count()} obras - Total monto: ${total:.2f}")

        for barrio in (
            Barrio.select()
            .join(Obra, on=(Barrio.id_barrio == Obra.id_barrio))
            .switch(Barrio)
            .join(Comuna, on=(Barrio.id_comuna == Comuna.id_comuna))
            .where(Comuna.comuna.in_(['1', '2', '3']))
            .distinct()
        ):
            print("-", barrio.barrio)


        print("\nObras finalizadas en 24 meses o menos:")
        finalizadas = Etapa.get_or_none(Etapa.etapa == "Finalizada")

        if finalizadas:
            obras_finalizadas = Obra.select().where(
                (Obra.plazo_meses <= 24) & (Obra.id_etapa == finalizadas)
            )
            print(f"{obras_finalizadas.count()} obras")
        else:
            print("No se encontró la etapa 'Finalizada'")

        print("\nMonto total de inversión estimado mostrado arriba.")
        db.close()


