import sys
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md("""
# 🌎 Mega exploración del ecosistema geoespacial de Google

Un recorrido para **ver** qué se puede hacer con Earth Engine, Google Maps Platform, OpenStreetMap y BigQuery, y **sacar ideas**.
El lugar de ejemplo es la Ciudad de México, pero **puedes cambiarlo en la celda 0** (coordenadas o caja) y todo se recalcula para cualquier parte del mundo.
Cada sección es independiente: corre solo las que te interesen.

| # | Sección | Fuente |
|---|---|---|
| 1 | Imagen Sentinel-2 sin nubes + NDVI | Earth Engine |
| 2 | Cobertura de suelo (Dynamic World) | Earth Engine |
| 3 | Relieve: la cuenca del Valle de México | Earth Engine |
| 4 | Crecimiento urbano 1975 → 2020 (GHSL) | Earth Engine |
| 5 | Población (WorldPop) y edificios (Open Buildings) | Earth Engine |
| 6 | Luces nocturnas (VIIRS) | Earth Engine |
| 7 | Contaminación: NO₂ (Sentinel-5P) y aerosoles (MODIS MAIAC) | Earth Engine |
| 8 | Clima: temperatura y lluvia 2015–2025 (ERA5-Land) | Earth Engine |
| 9 | Incendios (FIRMS) | Earth Engine |
| 10 | Embeddings satelitales + clustering (AlphaEarth) | Earth Engine |
| 11 | 40 años de Landsat: cambio urbano 1985 vs. hoy | Earth Engine |
| 12 | Temperatura superficial: islas de calor (Landsat) | Earth Engine |
| 13 | Radar Sentinel-1: ve a través de nubes y de noche | Earth Engine |
| 14 | Lo que hay en el mapa: servicios y transporte (OpenStreetMap) | Overpass API |
| 15 | Google Maps Platform: geocodificación, satélite, Street View, calidad del aire, Places, Solar, elevación | Maps APIs (requiere llave) |
| 16 | Big data: OSM del planeta en BigQuery, con estimación de costo | BigQuery |

> ⚠️ **Términos de Google Maps:** las imágenes y datos de Maps Platform (sección 15) se pueden **ver** aquí, pero no se deben guardar, descargar en masa ni usar para entrenar modelos. Los datos de Earth Engine sí se pueden exportar (con la licencia de cada dataset).
""")

md("## 0. Configuración")
code("""
PROJECT = "mateo-experimenta-con-earth"

try:
    import google.colab  # noqa: F401
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    %pip install -q geemap

import os
# Guardamos la llave de Maps para la sección 15 y la ocultamos de geemap:
# si geemap la ve, intenta usar los mosaicos de Google como mapa base y falla.
MAPS_KEY = os.environ.pop("GOOGLE_MAPS_API_KEY", None) or globals().get("MAPS_KEY")  # sobrevive si re-corres esta celda

import ee, geemap, requests, json
import pandas as pd
import matplotlib.pyplot as plt

if IN_COLAB:
    ee.Authenticate()
ee.Initialize(project=PROJECT)
print("Earth Engine listo · Colab:", IN_COLAB)
""")

code("""
# Área de estudio: Ciudad de México (FAO GAUL nivel 1), con respaldo de caja si no se encuentra
gaul = (ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.eq("ADM0_NAME", "Mexico"))          # ¡también hay un "Distrito Federal" en Brasil!
        .filter(ee.Filter.eq("ADM1_NAME", "Distrito Federal")))
if gaul.size().getInfo() > 0:
    CDMX = gaul.geometry()
else:
    CDMX = ee.Geometry.Rectangle([-99.36, 19.05, -98.94, 19.59])
VALLE = CDMX.buffer(25000).bounds()           # región más amplia (Valle de México)
CENTRO = ee.Geometry.Point([-99.1332, 19.4326])  # Zócalo
CENTRO_LATLON = (19.4326, -99.1332)
PUNTO = (19.4352, -99.1412)                       # Palacio de Bellas Artes (aprox.), para las pruebas de Maps
# 👉 Para explorar otro lugar: cambia CDMX (geometría), CENTRO/CENTRO_LATLON y PUNTO.

def mapa(zoom=10, center=(19.40, -99.13)):
    m = geemap.Map(center=list(center), zoom=zoom)
    m.addLayer(ee.Image().paint(CDMX, 0, 2), {"palette": "white"}, "Límite CDMX")
    return m

def serie_mensual(col, banda, region, escala, inicio, fin, factor=1.0):
    \"\"\"Promedio mensual de una banda sobre una región → DataFrame.\"\"\"
    meses = pd.date_range(inicio, fin, freq="MS")
    rows = []
    for k in range(0, len(meses), 12):          # de 12 en 12 para no saturar a Earth Engine
        feats = []
        for m in meses[k:k + 12]:
            d = ee.Date(m.strftime("%Y-%m-%d"))
            img = col.filterDate(d, d.advance(1, "month")).select(banda).mean()
            v = ee.Dictionary(img.reduceRegion(ee.Reducer.mean(), region, escala, maxPixels=1e10, bestEffort=True)).get(banda, -9999)
            feats.append(ee.Feature(None, {"fecha": m.strftime("%Y-%m"), "valor": v}))
        rows += [f["properties"] for f in ee.FeatureCollection(feats).getInfo()["features"]]
    df = pd.DataFrame(rows)
    df["valor"] = df["valor"].where(df["valor"] != -9999) * factor
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

print("Área CDMX (km²):", round(CDMX.area(1000).getInfo() / 1e6))
""")

md("""
## 1. Imagen Sentinel-2 sin nubes + NDVI
Sentinel-2 (10 m, cada ~5 días, desde 2017). Hacemos una mediana de la temporada seca 2025 para quitar nubes, y calculamos NDVI (vegetación).
💡 *Ideas:* áreas verdes por alcaldía, pérdida de vegetación en el suelo de conservación, islas de calor.
""")
code("""
s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(CDMX).filterDate("2025-01-01", "2025-04-30")
      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)))
print("Escenas usadas:", s2.size().getInfo())
compuesto = s2.median().clip(VALLE)
ndvi = compuesto.normalizedDifference(["B8", "B4"]).rename("NDVI")

m = mapa()
m.addLayer(compuesto, {"bands": ["B4", "B3", "B2"], "min": 0, "max": 2500}, "Sentinel-2 color real")
m.addLayer(ndvi, {"min": 0, "max": 0.7, "palette": ["#d9c6a5", "#a6d96a", "#1a9641"]}, "NDVI", False)
m
""")

md("""
## 2. Cobertura de suelo — Dynamic World
Clasificación con IA de Google, casi en tiempo real, 10 m: agua, árboles, pasto, cultivos, urbano, suelo desnudo…
💡 *Ideas:* cuánto suelo de conservación se urbaniza cada año; cambios tras lluvias o incendios.
""")
code("""
dw = (ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
      .filterBounds(CDMX).filterDate("2024-01-01", "2024-12-31"))
clase = dw.select("label").mode().clip(VALLE)
paleta = ["419bdf", "397d49", "88b053", "7a87c6", "e49635", "dfc35a", "c4281b", "a59b8f", "b39fe1"]
nombres = ["agua", "árboles", "pasto", "vegetación inundada", "cultivos", "arbustos", "urbano", "suelo desnudo", "nieve"]

hist = clase.reduceRegion(ee.Reducer.frequencyHistogram(), CDMX, 50, maxPixels=1e10).get("label").getInfo()
total = sum(hist.values())
print({nombres[int(k)]: f"{100*v/total:.1f}%" for k, v in sorted(hist.items(), key=lambda x: -x[1])})

m = mapa()
m.addLayer(clase, {"min": 0, "max": 8, "palette": paleta}, "Dynamic World 2024 (moda)")
m.add_legend(title="Dynamic World", legend_dict={n: "#" + c for n, c in zip(nombres, paleta)})
m
""")

md("""
## 3. Relieve — la cuenca del Valle de México
SRTM (30 m). La ciudad está en una cuenca a ~2,240 m rodeada de volcanes: eso atrapa la contaminación.
""")
code("""
dem = ee.Image("USGS/SRTMGL1_003").clip(VALLE)
sombra = ee.Terrain.hillshade(dem)
stats = dem.reduceRegion(ee.Reducer.minMax(), CDMX, 90, maxPixels=1e10).getInfo()
print("Elevación en CDMX (m):", stats)

m = mapa(zoom=9)
m.addLayer(sombra, {"min": 0, "max": 255}, "Sombreado")
m.addLayer(dem, {"min": 2200, "max": 4000, "palette": ["#2c7bb6", "#abd9e9", "#ffffbf", "#fdae61", "#d7191c"], "opacity": 0.6}, "Elevación")
m
""")

md("""
## 4. Crecimiento urbano 1975 → 2020 — GHSL
Global Human Settlement Layer (JRC): superficie construida cada 5 años.
💡 *Ideas:* hacia dónde creció la mancha urbana; relación con transporte o riesgo sísmico.
""")
code("""
ghsl = ee.ImageCollection("JRC/GHSL/P2023A/GHS_BUILT_S")
b1975 = ghsl.filter(ee.Filter.eq("system:index", "1975")).first().select("built_surface")
b2020 = ghsl.filter(ee.Filter.eq("system:index", "2020")).first().select("built_surface")

def km2(img):
    return ee.Number(img.reduceRegion(ee.Reducer.sum(), VALLE, 100, maxPixels=1e10).get("built_surface")).divide(1e6).getInfo()
print(f"Superficie construida en el Valle: 1975 = {km2(b1975):.0f} km² · 2020 = {km2(b2020):.0f} km²")

vis = {"min": 0, "max": 8000, "palette": ["000000", "ffeda0", "f03b20"]}
m = mapa(zoom=9)
m.addLayer(b1975.selfMask().clip(VALLE), vis, "Construido 1975")
m.addLayer(b2020.selfMask().clip(VALLE), vis, "Construido 2020", False)
m
""")

md("""
## 5. Población (WorldPop) y edificios (Open Buildings)
WorldPop estima personas por píxel de 100 m. Open Buildings (Google Research) son polígonos de edificios detectados con IA.
""")
code("""
pop = (ee.ImageCollection("WorldPop/GP/100m/pop")
       .filter(ee.Filter.eq("country", "MEX")).filter(ee.Filter.eq("year", 2020)).first())
total = pop.reduceRegion(ee.Reducer.sum(), CDMX, 100, maxPixels=1e10).get("population").getInfo()
print(f"Población estimada CDMX 2020 (WorldPop): {total:,.0f}")

m = mapa(zoom=10)
m.addLayer(pop.clip(VALLE), {"min": 0, "max": 300, "palette": ["#fff5eb", "#fd8d3c", "#7f2704"]}, "Población por 100 m")
m
""")
code("""
# Open Buildings: contornos de edificios detectados con IA, vistos de cerca sobre imagen satelital
zona = CENTRO.buffer(1500)
edif = (ee.FeatureCollection("GOOGLE/Research/open-buildings/v3/polygons")
        .filterBounds(zona).filter(ee.Filter.gte("confidence", 0.75)))
print("Edificios en 1.5 km alrededor del Zócalo:", edif.size().getInfo())
m = geemap.Map(center=list(CENTRO_LATLON), zoom=17)
m.add_basemap("Esri.WorldImagery")
m.addLayer(edif.style(color="00FFFF", fillColor="00FFFF22", width=1), {}, "Open Buildings")
m
""")

md("""
## 6. Luces nocturnas — VIIRS
Radiancia nocturna mensual (~500 m). Proxy de actividad económica y urbanización.
""")
code("""
viirs = (ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
         .filterDate("2024-01-01", "2024-12-31").select("avg_rad").median().clip(VALLE))
# Escala logarítmica: el centro llega a ~150 nW/cm²/sr y las afueras a <1; en escala lineal todo se satura.
viirs_log = viirs.max(0).add(1).log10()
m = mapa(zoom=9)
m.addLayer(viirs_log, {"min": 0, "max": 2.4, "palette": ["000000", "1d4877", "f68838", "fbde44", "ffffff"]}, "Luces nocturnas 2024 (log)")
m.add_colorbar({"min": 0, "max": 2.4, "palette": ["000000", "1d4877", "f68838", "fbde44", "ffffff"]}, label="log10(radiancia + 1)")
m
""")

md("""
## 7. Contaminación — NO₂ (Sentinel-5P) y aerosoles (MODIS MAIAC)
NO₂ troposférico: tráfico y combustión. AOD (espesor óptico de aerosoles, 1 km): partículas en la columna atmosférica.
💡 *Ideas:* efecto de la pandemia (abril 2020), estacionalidad, corredores viales.
""")
code("""
no2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
df_no2 = serie_mensual(no2, "tropospheric_NO2_column_number_density", CDMX, 1113, "2019-01-01", "2025-06-01", factor=1e6)

fig, ax = plt.subplots(figsize=(11, 3.5))
ax.plot(df_no2["fecha"], df_no2["valor"], marker=".", color="#7b3294")
ax.axvspan(pd.Timestamp("2020-04-01"), pd.Timestamp("2020-05-31"), color="grey", alpha=0.2, label="Confinamiento 2020")
ax.set_ylabel("NO₂ troposférico (µmol/m²)"); ax.set_title("NO₂ promedio mensual sobre CDMX"); ax.legend()
plt.show()
""")
code("""
no2_img = no2.filterDate("2024-01-01", "2024-12-31").select("tropospheric_NO2_column_number_density").mean().clip(VALLE)
aod = (ee.ImageCollection("MODIS/061/MCD19A2_GRANULES").filterDate("2024-01-01", "2024-05-31")
       .select("Optical_Depth_055").mean().multiply(0.001).clip(VALLE))
m = mapa(zoom=9)
vis_no2 = {"min": 0.00003, "max": 0.0003, "palette": ["black", "blue", "purple", "cyan", "green", "yellow", "red"]}
m.addLayer(no2_img, vis_no2, "NO₂ 2024")
m.add_colorbar(vis_no2, label="NO₂ troposférico (mol/m²)")
m.addLayer(aod, {"min": 0.1, "max": 0.6, "palette": ["#ffffcc", "#fd8d3c", "#800026"]}, "AOD ene–may 2024", False)
m
""")

md("""
## 8. Clima — ERA5-Land 2015–2025
Reanálisis climático mensual (~11 km): temperatura, lluvia, viento, humedad del suelo…
""")
code("""
era = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
t = serie_mensual(era, "temperature_2m", CDMX, 11132, "2015-01-01", "2025-06-01")
p = serie_mensual(era, "total_precipitation_sum", CDMX, 11132, "2015-01-01", "2025-06-01", factor=1000)
t["valor"] -= 273.15

fig, ax1 = plt.subplots(figsize=(11, 3.5))
ax1.bar(p["fecha"], p["valor"], width=25, color="#74a9cf", label="Lluvia (mm)")
ax1.set_ylabel("Lluvia mensual (mm)")
ax2 = ax1.twinx()
ax2.plot(t["fecha"], t["valor"], color="#d7301f", label="Temperatura (°C)")
ax2.set_ylabel("Temperatura media (°C)")
ax1.set_title("Clima mensual en CDMX (ERA5-Land)")
plt.show()
print("Mes más caluroso:", t.loc[t["valor"].idxmax(), "fecha"].strftime("%Y-%m"), f"{t['valor'].max():.1f} °C")
""")

md("""
## 9. Incendios — FIRMS
Detecciones de fuego activo (MODIS, 1 km). En la temporada seca hay incendios forestales alrededor del Valle.
""")
code("""
fuego = (ee.ImageCollection("FIRMS").filterBounds(VALLE).filterDate("2024-01-01", "2024-06-30")
         .select("T21").max().clip(VALLE))
dias = ee.ImageCollection("FIRMS").filterBounds(VALLE).filterDate("2024-01-01", "2024-06-30").size().getInfo()
print("Imágenes diarias FIRMS en el periodo:", dias)
m = mapa(zoom=9)
m.addLayer(fuego, {"min": 300, "max": 400, "palette": ["yellow", "orange", "red"]}, "Fuego ene–jun 2024")
m
""")

md("""
## 10. Embeddings satelitales + clustering (AlphaEarth Foundations)
Cada píxel de 10 m tiene un vector de 64 números que resume su apariencia y evolución en el año (modelo de Google DeepMind).
Con k-means, sin etiquetas, el modelo agrupa zonas parecidas: barrios, industria, bosque, agricultura…
💡 *Ideas:* "encuéntrame lugares parecidos a este"; clasificar con muy pocas etiquetas; detectar cambios año contra año.
""")
code("""
emb = (ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL")
       .filterDate("2024-01-01", "2025-01-01").filterBounds(CDMX).mosaic())
muestra = emb.sample(region=CDMX, scale=60, numPixels=5000, seed=42, geometries=False)
kmeans = ee.Clusterer.wekaKMeans(8).train(muestra)
clusters = emb.clip(CDMX).cluster(kmeans)

m = mapa()
m.addLayer(clusters.randomVisualizer(), {}, "8 clusters de embeddings 2024")
m
""")

md("""
## 11. 40 años de Landsat — 1985 vs. hoy
Landsat es el archivo satelital civil más largo (desde 1972, 30 m). Comparamos un compuesto de 1985 con uno de 2024.
💡 *Ideas:* expansión urbana, desecación de lagos, deforestación, cualquier cambio de décadas.
""")
code("""
def landsat_sr(img):
    opt = img.select("SR_B.").multiply(0.0000275).add(-0.2)
    return img.addBands(opt, None, True)

l5 = (ee.ImageCollection("LANDSAT/LT05/C02/T1_L2").filterBounds(VALLE)
      .filterDate("1984-11-01", "1986-04-30").filter(ee.Filter.lt("CLOUD_COVER", 20)).map(landsat_sr).median().clip(VALLE))
l9 = (ee.ImageCollection("LANDSAT/LC09/C02/T1_L2").filterBounds(VALLE)
      .filterDate("2023-11-01", "2024-04-30").filter(ee.Filter.lt("CLOUD_COVER", 20)).map(landsat_sr).median().clip(VALLE))

m = mapa(zoom=10)
m.split_map(
    left_layer=geemap.ee_tile_layer(l5, {"bands": ["SR_B3", "SR_B2", "SR_B1"], "min": 0, "max": 0.3}, "1985"),
    right_layer=geemap.ee_tile_layer(l9, {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 0, "max": 0.3}, "2024"))
m
""")

md("""
## 12. Temperatura superficial — islas de calor
Banda térmica de Landsat 8/9: temperatura de la superficie (no del aire), 30 m (re-muestreada de 100 m).
💡 *Ideas:* qué colonias son más calientes y si tienen menos árboles (compara con el NDVI de la sección 1).
""")
code("""
lst = (ee.ImageCollection("LANDSAT/LC09/C02/T1_L2").merge(ee.ImageCollection("LANDSAT/LC08/C02/T1_L2"))
       .filterBounds(CDMX).filterDate("2024-03-01", "2024-05-31").filter(ee.Filter.lt("CLOUD_COVER", 15))
       .select("ST_B10").map(lambda i: i.multiply(0.00341802).add(149.0).subtract(273.15)).median().clip(CDMX))
s = lst.reduceRegion(ee.Reducer.percentile([5, 50, 95]), CDMX, 100, maxPixels=1e10).getInfo()
print("Temperatura superficial primavera 2024 (°C) p5/p50/p95:", {k: round(v, 1) for k, v in s.items()})

m = mapa()
m.addLayer(lst, {"min": 25, "max": 50, "palette": ["#313695", "#74add1", "#ffffbf", "#f46d43", "#a50026"]}, "Temperatura superficial (°C)")
m
""")

md("""
## 13. Radar Sentinel-1
El radar (SAR) ve a través de nubes y de noche. Superficies lisas (agua, pistas) se ven oscuras; edificios, brillantes.
💡 *Ideas:* inundaciones en temporada de lluvias, hundimiento del suelo (con interferometría), mapear zonas construidas.
""")
code("""
s1 = (ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(CDMX).filterDate("2024-01-01", "2024-12-31")
      .filter(ee.Filter.eq("instrumentMode", "IW")).filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
      .select(["VV", "VH"]))
print("Escenas de radar 2024:", s1.size().getInfo())
rad = s1.median().clip(VALLE)
m = mapa()
m.addLayer(rad.addBands(rad.select("VV").subtract(rad.select("VH")).rename("ratio")),
           {"bands": ["VV", "VH", "ratio"], "min": [-20, -25, 0], "max": [0, -5, 15]}, "Sentinel-1 VV/VH (falso color)")
m
""")

md("""
## 14. Lo que hay en el mapa — OpenStreetMap
Consulta en vivo a la API Overpass: hospitales, escuelas, mercados y paradas de transporte alrededor del centro.
OSM es abierto (ODbL): se puede descargar, guardar y combinar con todo lo demás.
""")
code("""
lat, lon, radio = CENTRO_LATLON[0], CENTRO_LATLON[1], 2000
q = f'''[out:json][timeout:60];
(
  nwr["amenity"~"^(hospital|school|marketplace|library)$"](around:{radio},{lat},{lon});
  node["public_transport"="station"](around:{radio},{lat},{lon});
  node["highway"="bus_stop"](around:{radio},{lat},{lon});
);
out center;'''

def overpass(q):
    \"\"\"Prueba varios servidores públicos de Overpass (a veces están saturados).\"\"\"
    servidores = ["https://overpass-api.de/api/interpreter",
                  "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
                  "https://overpass.private.coffee/api/interpreter",
                  "https://overpass.kumi.systems/api/interpreter"]
    for url in servidores:
        try:
            r = requests.post(url, data={"data": q}, headers={"User-Agent": "pruebas-geoespaciales-notebook"}, timeout=30)
            r.raise_for_status()
            return r.json()["elements"]
        except Exception as e:
            print(f"  {url.split('/')[2]} falló ({str(e)[:60]}), probando otro…")
    return None

els = overpass(q)
if els is None:
    # No detenemos el notebook: el resto de las secciones no depende de OSM.
    print("⚠️ Ningún servidor público de Overpass respondió ahora. Re-corre esta celda en unos minutos.")
    els = []

def tipo(t):
    if t.get("public_transport") == "station":
        return "estación"
    if t.get("highway") == "bus_stop":
        return "parada de autobús"
    return {"hospital": "hospital", "school": "escuela", "marketplace": "mercado", "library": "biblioteca"}.get(t.get("amenity"), "otro")
rows = []
for e in els:
    la, lo = (e["lat"], e["lon"]) if "lat" in e else (e["center"]["lat"], e["center"]["lon"])
    rows.append({"lat": la, "lon": lo, "tipo": tipo(e.get("tags", {})), "nombre": e.get("tags", {}).get("name")})
df_osm = pd.DataFrame(rows, columns=["lat", "lon", "tipo", "nombre"])
print(f"Elementos en {radio/1000:.0f} km del centro:")
print(df_osm["tipo"].value_counts().to_string() if len(df_osm) else "  (sin datos)")

colores = {"hospital": "#e41a1c", "escuela": "#377eb8", "mercado": "#ff7f00", "biblioteca": "#984ea3",
           "estación": "#000000", "parada de autobús": "#4daf4a", "otro": "#999999"}
m = geemap.Map(center=list(CENTRO_LATLON), zoom=15)
for t, sub in df_osm.groupby("tipo"):
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([x.lon, x.lat]), {"tipo": t}) for x in sub.itertuples()])
    m.addLayer(fc.style(color=colores[t], pointSize=4, width=1), {}, f"{t} ({len(sub)})")
if len(df_osm):
    m.add_legend(title="OpenStreetMap", legend_dict={f"{t} ({n})": colores[t] for t, n in df_osm["tipo"].value_counts().items()})
m
""")

md("""
## 15. Google Maps Platform
Necesita una **llave de API** con estas APIs habilitadas en el proyecto: Geocoding, Maps Static, Street View Static, Air Quality, Places (New), Solar, Elevation.
- **Colab:** guárdala en 🔑 *Secrets* con el nombre `GOOGLE_MAPS_API_KEY`.
- **Local:** variable de entorno `GOOGLE_MAPS_API_KEY`.

Sin llave, estas celdas se saltan. Recuerda: **ver sí, guardar o entrenar no.**
""")
code("""
from IPython.display import Image, display
KEY = MAPS_KEY
if IN_COLAB and not KEY:
    try:
        from google.colab import userdata
        KEY = userdata.get("GOOGLE_MAPS_API_KEY")
    except Exception:
        KEY = None
print("Llave de Maps:", "encontrada" if KEY else "NO encontrada → se saltan las celdas de Maps")

def ver_imagen(url, params):
    \"\"\"Descarga y muestra la imagen sin dejar la URL (con la llave) guardada en el notebook.\"\"\"
    r = requests.get(url, params={**params, "key": KEY}, timeout=30)
    if r.ok and r.headers.get("content-type", "").startswith("image"):
        display(Image(data=r.content))
    else:
        print("Error", r.status_code, r.text[:200])
""")
code("""
if KEY:
    # Geocodificación: dirección → coordenadas
    g = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
                     params={"address": "Palacio de Bellas Artes, Ciudad de México", "key": KEY}).json()
    if g.get("results"):
        loc = g["results"][0]["geometry"]["location"]
        PUNTO = (loc["lat"], loc["lng"])
        print(g["results"][0]["formatted_address"], PUNTO)
    else:
        print(g.get("status"), g.get("error_message"))
""")
code("""
if KEY:
    # Vista satelital (solo visualización, no se guarda)
    ver_imagen("https://maps.googleapis.com/maps/api/staticmap",
               {"center": f"{PUNTO[0]},{PUNTO[1]}", "zoom": 18, "size": "640x640", "maptype": "satellite"})
""")
code("""
if KEY:
    # Street View: primero metadatos (gratis), luego 4 vistas
    meta = requests.get("https://maps.googleapis.com/maps/api/streetview/metadata",
                        params={"location": f"{PUNTO[0]},{PUNTO[1]}", "key": KEY}).json()
    print("Street View:", meta.get("status"), meta.get("date"))
    if meta.get("status") == "OK":
        for h in (0, 90, 180, 270):
            ver_imagen("https://maps.googleapis.com/maps/api/streetview",
                       {"size": "600x300", "location": f"{PUNTO[0]},{PUNTO[1]}", "heading": h, "fov": 90})
""")
code("""
if KEY:
    # Calidad del aire actual (índice + concentraciones, incluye PM10 y PM2.5)
    aq = requests.post(f"https://airquality.googleapis.com/v1/currentConditions:lookup?key={KEY}",
                       json={"location": {"latitude": CENTRO_LATLON[0], "longitude": CENTRO_LATLON[1]},
                             "extraComputations": ["POLLUTANT_CONCENTRATION", "LOCAL_AQI"]}).json()
    print("Hora (UTC):", aq.get("dateTime"))
    for i in aq.get("indexes", []):
        print(f"  {i['displayName']}: {i.get('aqiDisplay', '-')} · {i.get('category')} · contaminante dominante: {i.get('dominantPollutant')}")
    print("Concentraciones:")
    for p in aq.get("pollutants", []):
        print(f"  {p['displayName']:>6}: {p['concentration']['value']} {p['concentration']['units']}")
""")
code("""
if KEY:
    # Places (New): museos y restaurantes a 600 m, con calificación
    r = requests.post("https://places.googleapis.com/v1/places:searchNearby",
                      headers={"X-Goog-Api-Key": KEY, "X-Goog-FieldMask": "places.displayName,places.primaryType,places.rating,places.userRatingCount"},
                      json={"includedTypes": ["museum", "restaurant"], "maxResultCount": 15,
                            "locationRestriction": {"circle": {"center": {"latitude": PUNTO[0], "longitude": PUNTO[1]}, "radius": 600}}}).json()
    for pl in r.get("places", []):
        print(f"- {pl['displayName']['text']} · {pl.get('primaryType')} · ⭐ {pl.get('rating')} ({pl.get('userRatingCount')})")
    if "error" in r:
        print(r["error"]["message"])
""")
code("""
if KEY:
    # Solar API: potencial solar del edificio más cercano al Zócalo
    s = requests.get("https://solar.googleapis.com/v1/buildingInsights:findClosest",
                     params={"location.latitude": CENTRO_LATLON[0], "location.longitude": CENTRO_LATLON[1], "key": KEY}).json()
    sp = s.get("solarPotential", {})
    print("Paneles máx.:", sp.get("maxArrayPanelsCount"), "· Horas de sol/año:", sp.get("maxSunshineHoursPerYear"))
    if "error" in s:
        print(s["error"]["message"])
""")
code("""
if KEY:
    # Elevation API: perfil de elevación del Zócalo al Ajusco
    e = requests.get("https://maps.googleapis.com/maps/api/elevation/json",
                     params={"path": f"{CENTRO_LATLON[0]},{CENTRO_LATLON[1]}|19.2086,-99.2584", "samples": 60, "key": KEY}).json()
    if e.get("results"):
        el = [x["elevation"] for x in e["results"]]
        plt.figure(figsize=(10, 3)); plt.plot(el, color="#8c510a"); plt.ylabel("m"); plt.title("Perfil Zócalo → Ajusco (Elevation API)"); plt.show()
    else:
        print(e.get("status"), e.get("error_message"))
""")

md("""
## 16. Big data — OpenStreetMap del planeta en BigQuery
BigQuery tiene OSM completo como dataset público. Primero hacemos un **dry run** (gratis) para saber cuántos datos leería la consulta y cuánto costaría.
Solo se ejecuta si está por debajo de `MAX_GB`. (Hay 1 TB/mes gratis de consultas; después ~6 USD por TB.)
""")
code("""
from google.cloud import bigquery
bq = bigquery.Client(project=PROJECT)
sql = '''
SELECT
  (SELECT value FROM UNNEST(all_tags) WHERE key = 'amenity') AS amenity,
  COUNT(*) AS n
FROM `bigquery-public-data.geo_openstreetmap.planet_nodes`
WHERE ST_INTERSECTSBOX(geometry, -99.36, 19.05, -98.94, 19.59)
  AND EXISTS (SELECT 1 FROM UNNEST(all_tags) t WHERE t.key = 'amenity')
GROUP BY amenity ORDER BY n DESC
LIMIT 25
'''
dry = bq.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
gb = dry.total_bytes_processed / 1e9
print(f"La consulta leería {gb:,.1f} GB  ≈ {gb/1000*6.25:,.2f} USD fuera del nivel gratuito")

MAX_GB = 0  # súbelo (p. ej. 500) para ejecutarla de verdad
if gb <= MAX_GB:
    display(bq.query(sql).to_dataframe())
else:
    print(f"No se ejecuta (MAX_GB = {MAX_GB}). Cambia MAX_GB si quieres correrla.")
""")

md("""
## 💡 Ideas para seguir
- **Cambia de lugar:** pon otra ciudad, un volcán, una selva o una costa en la celda 0 y vuelve a correr todo.
- **Buscador de lugares parecidos:** elige un píxel y encuentra los más similares en el mundo con los embeddings (sección 10).
- **Islas de calor vs. árboles:** temperatura superficial (12) contra NDVI (1) por colonia.
- **Expansión urbana:** Dynamic World año por año, o Landsat 1985→hoy (11), sobre el suelo de conservación.
- **Contaminación y relieve:** NO₂ (7) + viento de ERA5 (8) + la cuenca (3) → por qué se acumula.
- **Inundaciones:** radar (13) antes y después de una tormenta.
- **Datos + servicios:** cruzar población (5) con hospitales o transporte de OSM (14) para ver quién queda lejos.
- **Exportar:** cualquier capa de Earth Engine → Cloud Storage o BigQuery con `ee.batch.Export`.
- **Más datasets:** hay más de 900 en el catálogo: https://developers.google.com/earth-engine/datasets
""")

nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"},
                  "colab": {"provenance": []}}
nbf.write(nb, sys.argv[1])
print("ok", len(cells), "celdas")
