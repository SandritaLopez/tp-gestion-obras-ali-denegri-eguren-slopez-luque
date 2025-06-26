# Importar las librerías necesarias
import pandas as pd            # Para manipular datos (como leer CSVs)
import folium                  # Para crear mapas interactivos con marcadores

# Instalar la librería folium con:
# pip install folium

# Leer el archivo CSV que contiene información de obras urbanas
df = pd.read_csv("../data/observatorio-de-obras-urbanas.csv",
                 encoding="latin1", sep=";")  # Se especifica el encoding y el separador ";"

# --- LIMPIEZA DE COORDENADAS ---

# Asegurar que los valores de latitud estén limpios: 
# a veces vienen con saltos de línea, nos quedamos con la primera parte
df['lat'] = df['lat'].astype(str).str.split('\n').str[0]

# Eliminar puntos usados como separadores de miles (ej: "1.234" → "1234")
df['lng'] = df['lng'].astype(str).str.replace('.', '', regex=False)
df['lat'] = df['lat'].str.replace('.', '', regex=False)

# Reemplazar las comas por puntos (pasa cuando los datos vienen con formato europeo)
df['lat'] = df['lat'].str.replace(',', '.', regex=False)
df['lng'] = df['lng'].str.replace(',', '.', regex=False)

# Convertir los valores de lat y lng a tipo numérico (float), forzando errores a NaN
df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lng'] = pd.to_numeric(df['lng'], errors='coerce')

# Eliminar las filas que no tienen coordenadas válidas
df = df.dropna(subset=['lat', 'lng'])

# --- CREACIÓN DEL MAPA ---

# Crear un mapa centrado en Buenos Aires con un zoom inicial de 12
mapa = folium.Map(location=[-34.60, -58.44], zoom_start=12)

# Recorrer cada fila del DataFrame para crear un marcador por obra
for _, fila in df.iterrows():
    lat = fila['lat']
    lon = fila['lng']
    nombre = fila['nombre']

    # Armar un popup (ventana emergente) con info de la obra
    popup_html = (
        f"<b>{nombre}</b><br>"
        f"Lat: {lat:.6f}<br>"
        f"Lng: {lon:.6f}"
    )

    # Agregar un marcador al mapa con ubicación, popup y tooltip (texto flotante)
    folium.Marker(
        location=[lat, lon],
        popup=popup_html,
        tooltip=f"{nombre} ({lat:.4f}, {lon:.4f})"
    ).add_to(mapa)

# Guardar el mapa generado como archivo HTML para verlo en un navegador
mapa.save("mapa_obras.html")
