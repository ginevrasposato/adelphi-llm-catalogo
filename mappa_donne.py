import json
from pathlib import Path

import folium

from mappa_nascite import carica_cache, geocodifica, raggruppa_per_citta, salva_cache

libri = json.loads(Path("dataset_completo.json").read_text(encoding="utf-8"))
donne = [l for l in libri if l.get("genere_autore") == "F"]
citta = raggruppa_per_citta(donne)
cache = carica_cache()

mappa = folium.Map(location=[45, 15], zoom_start=4)
n_mappate = 0
for nome, dati in citta.items():
    coord = geocodifica(nome, cache)
    if not coord:
        print(f"non trovata: {nome}")
        continue
    n_mappate += 1
    autrici = sorted(dati["autori"])
    folium.CircleMarker(
        location=coord,
        radius=5 + len(autrici) * 3,
        popup=f"{nome}: {', '.join(autrici)} ({dati['volumi']} volumi)",
        tooltip=nome,
        color="#b03a68",
        weight=1.5,
        fill=True,
        fill_color="#e87ba4",
        fill_opacity=0.7,
    ).add_to(mappa)
salva_cache(cache)

mappa.save("mappa_autrici.html")
tot = len({l["autore"] for l in donne if l.get("luogo_nascita_autore")})
print("Salvata: mappa_autrici.html")
print(f"{len({l['autore'] for l in donne})} autrici in tutto; {tot} con luogo di nascita; {n_mappate}/{len(citta)} citta' mappate")
