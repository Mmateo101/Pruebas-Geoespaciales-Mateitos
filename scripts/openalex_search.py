"""Busca literatura en OpenAlex por temas y guarda resultados en JSON.

Uso:
    python scripts/openalex_search.py docs/literatura/openalex_raw.json
"""
import json
import sys
import time
import urllib.parse
import urllib.request

TEMAS = {
    "deteccion_pasos_imagen_aerea": [
        "crosswalk detection aerial imagery deep learning",
        "zebra crossing detection satellite images",
        "pedestrian crossing extraction remote sensing",
    ],
    "imagen_y_riesgo_de_choque": [
        "satellite imagery traffic crash risk deep learning",
        "aerial imagery road safety assessment machine learning",
    ],
    "street_view_y_atropellamientos": [
        "street view images pedestrian crash built environment",
        "computer vision street imagery pedestrian collisions",
    ],
    "muertes_peatones_entorno_construido": [
        "pedestrian fatality built environment intersection",
        "fatal pedestrian crashes case-control location",
    ],
    "efecto_pasos_marcados": [
        "marked crosswalks pedestrian crash risk",
        "pedestrian crossing treatments safety effectiveness",
    ],
    "mexico_latinoamerica": [
        "pedestrian deaths Mexico City",
        "atropellamientos peatones Ciudad de Mexico",
        "pedestrian road traffic injuries Latin America intersections",
    ],
}

FIELDS = "id,doi,title,publication_year,cited_by_count,authorships,primary_location,abstract_inverted_index"


def abstract(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def buscar(q, n=15):
    params = {"search": q, "per-page": n, "select": FIELDS}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "pruebas-geoespaciales-lit-search"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    out = []
    for w in data.get("results", []):
        src = (w.get("primary_location") or {}).get("source") or {}
        out.append({
            "id": w["id"],
            "doi": w.get("doi"),
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "cited_by": w.get("cited_by_count"),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", [])][:4],
            "venue": src.get("display_name"),
            "abstract": abstract(w.get("abstract_inverted_index"))[:700],
        })
    return out


def main(dest):
    resultados = {}
    for tema, queries in TEMAS.items():
        vistos, lista = set(), []
        for q in queries:
            for w in buscar(q):
                if w["id"] not in vistos:
                    vistos.add(w["id"])
                    w["query"] = q
                    lista.append(w)
            time.sleep(0.3)
        resultados[tema] = lista
        print(f"{tema}: {len(lista)} trabajos")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
