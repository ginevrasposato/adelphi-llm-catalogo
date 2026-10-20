# pulisci_dati.py
# Legge il CSV grezzo prodotto dallo scraper, applica una serie di
# correzioni e normalizzazioni, e salva un nuovo CSV pulito.
#
# Decisioni di modellazione prese consapevolmente (non delegate al modello):
# - curatori/traduttori multipli: restano in un unico campo, separati da virgola
# - libri senza autore singolo (opere anonime/collettive): il campo autore
#   viene impostato a "Anonimo" anziché lasciato vuoto

import csv
import re

INPUT = "biblioteca_adelphi.csv"
OUTPUT = "biblioteca_adelphi_pulito.csv"


def leggi_csv(percorso):
    """Legge il CSV grezzo e restituisce una lista di dizionari."""
    with open(percorso, encoding="utf-8") as f:
        lettore = csv.DictReader(f)
        return list(lettore)


def pulisci_testo(testo):
    """Rimuove spazi superflui a inizio/fine e spazi doppi interni."""
    testo = re.sub(r"\s+", " ", testo)
    return testo.strip()


def pulisci_anno(testo):
    """Restituisce l'anno come intero, estraendo le 4 cifre se presenti."""
    corrispondenza = re.search(r"\d{4}", testo)
    if corrispondenza:
        return int(corrispondenza.group(0))
    return None


def pulisci_riga(riga):
    """Applica tutte le correzioni a una singola riga grezza."""
    autore = pulisci_testo(riga["autore"])
    if not autore:
        autore = "Anonimo"

    return {
        "autore": autore,
        "titolo": pulisci_testo(riga["titolo"]),
        "curatore": pulisci_testo(riga["curatore"]),
        "numero_collana": riga["numero_collana"].strip(),
        "anno": pulisci_anno(riga["anno"]),
    }


def riordina_e_deduplica(libri):
    """Ordina i libri per numero di collana (decrescente) e rimuove
    eventuali righe perfettamente duplicate."""
    visti = set()
    libri_unici = []

    for libro in libri:
        firma = tuple(libro.values())
        if firma not in visti:
            visti.add(firma)
            libri_unici.append(libro)

    libri_unici.sort(
        key=lambda l: int(l["numero_collana"]) if l["numero_collana"].isdigit() else -1,
        reverse=True,
    )

    return libri_unici


def salva_csv(libri, percorso):
    with open(percorso, "w", encoding="utf-8", newline="") as f:
        scrittore = csv.DictWriter(
            f, fieldnames=["autore", "titolo", "curatore", "numero_collana", "anno"]
        )
        scrittore.writeheader()
        scrittore.writerows(libri)


def main():
    libri_grezzi = leggi_csv(INPUT)
    print(f"Letti {len(libri_grezzi)} libri da {INPUT}")

    libri_puliti = [pulisci_riga(r) for r in libri_grezzi]
    libri_puliti = riordina_e_deduplica(libri_puliti)

    anonimi = sum(1 for l in libri_puliti if l["autore"] == "Anonimo")
    print(f"Dopo pulizia: {len(libri_puliti)} libri ({anonimi} opere anonime/collettive)")

    salva_csv(libri_puliti, OUTPUT)
    print(f"Salvati in {OUTPUT}")


if __name__ == "__main__":
    main()
