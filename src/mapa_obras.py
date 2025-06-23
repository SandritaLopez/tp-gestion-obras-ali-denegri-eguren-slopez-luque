import pandas as pd
import folium

# descargar librería folium
# pip install folium

df = pd.read_csv("../data/observatorio-de-obras-urbanas.csv",
                 encoding="latin1", sep=";")

# Limpieza de coordenadas (como antes)
df['lat'] = df['lat'].astype(str).str.split('\n').str[0]
df['lng'] = df['lng'].astype(str).str.replace('.', '', regex=False)
df['lat'] = df['lat'].str.replace('.', '', regex=False)
df['lat'] = df['lat'].str.replace(',', '.', regex=False)
df['lng'] = df['lng'].str.replace(',', '.', regex=False)
df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
df = df.dropna(subset=['lat', 'lng'])

mapa = folium.Map(location=[-34.60, -58.44], zoom_start=12)

for _, fila in df.iterrows():
    lat = fila['lat']
    lon = fila['lng']
    nombre = fila['nombre']
    # Aquí armamos el popup para que incluya lat y lng
    popup_html = (
        f"<b>{nombre}</b><br>"
        f"Lat: {lat:.6f}<br>"
        f"Lng: {lon:.6f}"
    )
    folium.Marker(
        location=[lat, lon],
        popup=popup_html,
        tooltip=f"{nombre} ({lat:.4f}, {lon:.4f})"
    ).add_to(mapa)

mapa.save("mapa_obras.html")
