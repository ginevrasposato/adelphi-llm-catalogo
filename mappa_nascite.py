import json
import ssl
import sys
import time
from collections import defaultdict
from pathlib import Path

import certifi
import folium
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

INPUT = "dataset_completo.json"
CACHE = "cache_geocoding.json"
OUTPUT = "mappa_nascite.html"
MAX_ERRORI_DI_FILA = 5

# Correzioni a mano per luoghi che il geocoder colloca nel posto sbagliato
# (nomi ambigui). Coordinate approssimative [lat, lon].
CORREZIONI = {
    "Castries": [14.01, -60.99],         # Santa Lucia (Caraibi), Derek Walcott
    "Kuling": [29.56, 115.99],           # Lushan (Cina), Mervyn Peake
    "Rutherford": [40.83, -74.11],       # New Jersey, William Carlos Williams
    "Lancaster": [54.05, -2.80],         # Lancashire (Inghilterra), Leonora Carrington
    "Reading": [40.34, -75.93],          # Pennsylvania, Wallace Stevens
    "Winchester": [39.19, -78.16],       # Virginia, Willa Cather
    "Florida": [39.50, -91.79],          # Florida (Missouri), Mark Twain
    "New Albany": [34.49, -89.01],       # Mississippi, William Faulkner
    "Gorochovo": [52.97, 36.06],         # villaggio vicino a Orel, Nikolaj Leskov (approssimativo)
}

contesto_ssl = ssl.create_default_context(cafile=certifi.where())
geolocatore = Nominatim(user_agent="progetto-universitario-biblioteca-adelphi",
                        ssl_context=contesto_ssl)
errori_di_fila = 0


def carica_cache():
    if Path(CACHE).exists():
        return json.loads(Path(CACHE).read_text(encoding="utf-8"))
    return {}


def salva_cache(cache):
    Path(CACHE).write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def pulisci_luogo(nome):
    return nome.split(";")[-1].strip()


def raggruppa_per_citta(libri):
    citta = defaultdict(lambda: {"autori": set(), "volumi": 0})
    for l in libri:
        c = l.get("luogo_nascita_autore")
        if c:
            c = pulisci_luogo(c)
            citta[c]["autori"].add(l["autore"])
            citta[c]["volumi"] += 1
    return citta


def geocodifica(nome, cache):
    global errori_di_fila
    if nome in cache:
        return cache[nome]
    try:
        risultato = geolocatore.geocode(nome, timeout=10)
        time.sleep(1.0)
        errori_di_fila = 0
    except (GeocoderTimedOut, GeocoderServiceError) as errore:
        errori_di_fila += 1
        print(f"   errore di rete: {type(errore).__name__}: {errore}")
        if errori_di_fila >= MAX_ERRORI_DI_FILA:
            print("Troppi errori di fila: mi fermo. Controlla la connessione.")
            sys.exit(1)
        return None
    coordinate = [risultato.latitude, risultato.longitude] if risultato else None
    cache[nome] = coordinate
    return coordinate


def main():
    libri = json.loads(Path(INPUT).read_text(encoding="utf-8"))
    citta = raggruppa_per_citta(libri)
    print(f"Citta' distinte da geocodificare: {len(citta)}")

    cache = carica_cache()
    cache.update(CORREZIONI)
    mappabili = {}
    for i, (nome, dati) in enumerate(citta.items(), start=1):
        if nome not in cache:
            print(f"[{i}/{len(citta)}] {nome}")
        coord = geocodifica(nome, cache)
        if coord:
            mappabili[nome] = (coord, dati)
        else:
            print(f"   non trovata: {nome}")
        if i % 10 == 0:
            salva_cache(cache)
    salva_cache(cache)

    mappa = folium.Map(location=[45, 15], zoom_start=4)
    for nome, (coord, dati) in mappabili.items():
        n_autori = len(dati["autori"])
        folium.CircleMarker(
            location=coord,
            radius=4 + n_autori * 2,
            popup=f"{nome}: {n_autori} autori, {dati['volumi']} volumi",
            tooltip=nome,
            color="#1f5fae",
            weight=1.5,
            fill=True,
            fill_color="#2a78d6",
            fill_opacity=0.6,
        ).add_to(mappa)

    mappa.save(OUTPUT)
    autori_tot = len({l["autore"] for l in libri if l.get("luogo_nascita_autore")})
    print(f"Mappa salvata in {OUTPUT}")
    print(f"Citta' mappate: {len(mappabili)}/{len(citta)} ({autori_tot} autori con luogo di nascita)")


if __name__ == "__main__":
    main()
