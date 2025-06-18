# Importamos la librería pandas para trabajar con datos tabulares (como CSVs)
import pandas as pd

# Leemos el archivo CSV con el dataset de obras urbanas:
# - El archivo está ubicado en una carpeta superior llamada "data"
# - Se usa encoding "latin1" porque probablemente contiene tildes y caracteres especiales
# - El separador de columnas es ";" en lugar de la coma tradicional
df = pd.read_csv(
    "../data/observatorio-de-obras-urbanas.csv",
    encoding="latin1",
    sep=";"
)

# 1) Mostramos una lista de los nombres de las columnas del DataFrame
# Esto puede servir para tener una vista general de qué campos trae el CSV
print("Columnas (raw):", df.columns.tolist())

# 2) Recorremos cada nombre de columna y lo imprimimos con repr()
# repr() permite ver espacios en blanco invisibles (como '\xa0' o BOMs)
# Esto es útil para limpiar o estandarizar los nombres antes de usarlos
for col in df.columns:
    print(repr(col))

