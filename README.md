# Pruebas Geoespaciales

Laboratorio para explorar el ecosistema geoespacial de Google: Earth Engine, Google Maps Platform, BigQuery y datos abiertos como OpenStreetMap.

Proyecto de Google Cloud: `mateo-experimenta-con-earth`.

## Notebooks

| Notebook | Qué hace | Abrir |
|---|---|---|
| [00 · Mega exploración](notebooks/00_mega_exploracion_google.ipynb) | 16 secciones: Sentinel-2, Dynamic World, relieve, crecimiento urbano, población y edificios, luces nocturnas, NO₂ y aerosoles, clima, incendios, embeddings satelitales, Landsat 1985 vs. hoy, islas de calor, radar, OSM, Google Maps APIs y BigQuery | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Mmateo101/Pruebas-Geoespaciales-Mateitos/blob/main/notebooks/00_mega_exploracion_google.ipynb) |

El lugar de ejemplo es la Ciudad de México; se cambia en la celda 0.

## Uso local

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
gcloud auth application-default login
.\.venv\Scripts\jupyter lab
```

Para las secciones de Google Maps hace falta una llave en la variable de entorno `GOOGLE_MAPS_API_KEY` (en Colab, en *Secrets*). Nunca la subas al repo.

## Otros

- `docs/literatura/`: bibliografía sobre pasos peatonales, imágenes y seguridad peatonal (OpenAlex).
- `scripts/build_mega_notebook.py`: genera el notebook 00.
- `scripts/openalex_search.py`: repite la búsqueda bibliográfica.
