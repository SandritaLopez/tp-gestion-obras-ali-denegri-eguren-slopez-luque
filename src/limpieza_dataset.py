# Importar archivo archivo CSV con el uso de Pandas.

import pandas as pd

df = pd.read_csv("data/observatorio-de-obras-urbanas.csv")


#print(df.head(10))  # Muestra las primeras 10 filas
# print(df.columns)
# print(df.shape)  # (filas, columnas)
# print(df.info())



# Funciones para limpieza

df.fillna(0) # reemplaza los valores nulls por cero

df["Destacada"] = df["Destacada"].fillna("No") # Columna destacada, reemplaza los valores nulos por "No"

df.dropna(subset=["Nombre", "Etapa", "Fecha de Inicio", "Fecha de Finalización"], inplace=True) # Eliminar valores nulos en ciertas columnas

df["Nombre"] = df["Nombre"].str.replace("Â", "A")        # Reemplaza caracteres especiales en la columna Nombre 
df["tipo", "direccion", "lat", "Ing", "monto_contrato"] = df["tipo", "direccion", "lat", "Ing", "monto_contrato"].replace(".", "Sin especificar")       # para datos con puntos en las columnas, agrega "Sin especificar
df["tipo"] = df["tipo"].replace("", "Sin especificar")   # para strings vacíos en la columna tipo
df["comuna"] = df["comuna"].fillna("Sin especificar")    # para nulos en la columna comuna 
df["barrio"] = df["barrio"].fillna("Sin especificar")    # para nulos en la columna barrio 
df = df[df["Barrio"] != "."]                             # Elimina filas donde la columna Barrio sea igual a "."
df["Barrio"] = df["Barrio"].str.replace("Ã±", "ñ")       # Reemplaza caracteres especiales en la columna Barrio
df["Barrio"] = df["Barrio"].str.replace(r",|/| y | e ", "|", regex=True)
df["Barrio"] = df["Barrio"].str.strip()                  # Reemplaza caracteres especiales en la columna Barrio por un unico separador "|"




#Fechas
df["fecha_inicio"] = df["fecha_inicio"].replace("A/D", "np.nan")  # Reemplaza "A/D" por NaN en la columna fecha_inicio 
df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], format="%m/%y", errors="coerce") # Convierte la columna fecha_inicio a tipo datetime, ignorando errores