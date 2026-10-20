# scraper_adelphi.py
# Scarica il catalogo online della collana "Biblioteca Adelphi"
# ed estrae, per ciascun libro: autore, titolo, curatore/traduttore,
# numero nella collana, anno di pubblicazione.
# Il catalogo è distribuito su 25 pagine; lo script le visita una per una.

import csv
import time
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.adelphi.it/catalogo/collana/1"
NUM_PAGINE = 25
OUTPUT = "biblioteca_adelphi.csv"


def url_pagina(numero):
    """Costruisce l'URL della pagina N del catalogo.
    La prima pagina non ha suffisso, le altre hanno /pN in fondo."""
    if numero == 1:
        return BASE_URL
    return f"{BASE_URL}/p{numero}"


def estrai_libri_da_pagina(html):
    """Restituisce una lista di dizionari con i dati dei libri
    trovati in una singola pagina del catalogo.

    La struttura reale (vista con Ispeziona sul sito adelphi.it) è:
    ogni libro è contenuto in un blocco <div class="box box-type-book-line ...">,
    con autore in <div class="book-author...">, titolo in <h1 class="book-title...">,
    e più sotto un testo che contiene "A cura di" / "Traduzione di", e un blocco
    con "Biblioteca Adelphi, NUMERO" seguito dall'anno."""
    soup = BeautifulSoup(html, "html.parser")
    libri = []

    schede = soup.find_all("div", class_=re.compile(r"\bbox-type-book-line\b"))

    for scheda in schede:
        testo_scheda = scheda.get_text("\n", strip=True)

        tag_titolo = scheda.find(class_=re.compile("book-title"))
        titolo = tag_titolo.get_text(strip=True) if tag_titolo else ""

        tag_autore = scheda.find(class_=re.compile("book-author"))
        autore = tag_autore.get_text(strip=True) if tag_autore else ""

        # Curatore o traduttore: cerchiamo la prima occorrenza di una
        # di queste due diciture nel testo della scheda.
        curatore_match = re.search(
            r"(A cura di|Traduzione di)[^\n]*", testo_scheda
        )
        curatore = curatore_match.group(0).strip() if curatore_match else ""

        # Numero in collana: "Biblioteca Adelphi, 791"
        numero_match = re.search(r"Biblioteca Adelphi,\s*(\d+)", testo_scheda)
        numero_collana = numero_match.group(1) if numero_match else ""

        # Anno: un numero a 4 cifre subito dopo il numero di collana,
        # tipicamente nella forma "2026 / pp. 265"
        anno_match = re.search(r"\b(19|20)\d{2}\b(?=\s*/\s*pp\.)", testo_scheda)
        anno = anno_match.group(0) if anno_match else ""

        # Salviamo solo se abbiamo trovato almeno un titolo:
        # evita di salvare blocchi vuoti o pubblicitari.
        if titolo:
            libri.append({
                "autore": autore,
                "titolo": titolo,
                "curatore": curatore,
                "numero_collana": numero_collana,
                "anno": anno,
            })

    return libri


def salva_csv(libri, percorso):
    with open(percorso, "w", encoding="utf-8", newline="") as f:
        scrittore = csv.DictWriter(
            f, fieldnames=["autore", "titolo", "curatore", "numero_collana", "anno"]
        )
        scrittore.writeheader()
        scrittore.writerows(libri)


def main():
    tutti_i_libri = []

    for numero in range(1, NUM_PAGINE + 1):
        url = url_pagina(numero)
        print(f"Scarico pagina {numero}/{NUM_PAGINE}: {url}")

        risposta = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        libri_pagina = estrai_libri_da_pagina(risposta.text)
        tutti_i_libri.extend(libri_pagina)

        print(f"  -> trovati {len(libri_pagina)} libri in questa pagina")

        # Pausa breve per non sovraccaricare il sito
        time.sleep(1)

    salva_csv(tutti_i_libri, OUTPUT)
    print(f"\nSalvati {len(tutti_i_libri)} libri in {OUTPUT}")


if __name__ == "__main__":
    main()
    