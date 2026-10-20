import csv
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.adelphi.it/catalogo/collana/1"
NUM_PAGINE = 25
OUTPUT = "descrizioni_adelphi.csv"


def url_pagina(numero):
    return BASE_URL if numero == 1 else f"{BASE_URL}/p{numero}"


def estrai_da_pagina(html):
    soup = BeautifulSoup(html, "html.parser")
    libri = []
    for scheda in soup.find_all("div", class_=re.compile(r"\bbox-type-book-line\b")):
        tag_titolo = scheda.find(class_=re.compile("book-title"))
        titolo = tag_titolo.get_text(strip=True) if tag_titolo else ""
        if not titolo:
            continue

        link = tag_titolo.find("a")
        url_libro = "https://www.adelphi.it" + link["href"] if link and link.get("href") else ""

        tag_abstract = scheda.find(class_=re.compile("box-book-line-abstract"))
        descrizione = ""
        if tag_abstract:
            descrizione = re.sub(r"\s+", " ", tag_abstract.get_text(" ", strip=True))

        testo = scheda.get_text("\n", strip=True)
        numero = re.search(r"Biblioteca Adelphi,\s*(\d+)", testo)

        edizioni = scheda.find(class_=re.compile("sideinfo-editions"))
        ebook = bool(edizioni and "ebook" in edizioni.get_text().lower())

        libri.append({
            "numero_collana": numero.group(1) if numero else "",
            "titolo": titolo,
            "descrizione": descrizione,
            "ebook_disponibile": ebook,
            "url_libro": url_libro,
        })
    return libri


def main():
    tutti = []
    for n in range(1, NUM_PAGINE + 1):
        print(f"Pagina {n}/{NUM_PAGINE}")
        r = requests.get(url_pagina(n), headers={"User-Agent": "Mozilla/5.0"})
        tutti.extend(estrai_da_pagina(r.text))
        time.sleep(1)

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["numero_collana", "titolo", "descrizione", "ebook_disponibile", "url_libro"])
        w.writeheader()
        w.writerows(tutti)

    con_descr = sum(1 for l in tutti if l["descrizione"])
    con_ebook = sum(1 for l in tutti if l["ebook_disponibile"])
    print(f"\nSalvati {len(tutti)} libri in {OUTPUT}")
    print(f"  - {con_descr} con descrizione")
    print(f"  - {con_ebook} con eBook")


if __name__ == "__main__":
    main()
