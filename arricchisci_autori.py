import csv
import json
import re
import time
import requests
from bs4 import BeautifulSoup

INPUT = "biblioteca_adelphi_pulito.csv"
OUTPUT = "autori_arricchiti.json"

LIMITE = None
PAUSA = 1.0


def estrai_autori_unici(percorso):
    with open(percorso, encoding="utf-8") as f:
        righe = list(csv.DictReader(f))
    autori = {r["autore"] for r in righe if r["autore"] != "Anonimo"}
    return sorted(autori)


def url_wikipedia(nome):
    return "https://it.wikipedia.org/wiki/" + nome.replace(" ", "_")


def scarica_pagina(url):
    try:
        risposta = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if risposta.status_code == 200:
            return risposta.text
        return None
    except requests.RequestException:
        return None


ANCORA_BIO = re.compile(
    r"\bè\s+(?:(stato|uno|un)(?![a-zàèéìòù'’])|(stata|una)(?![a-zàèéìòù])|(un['’]))",
    re.IGNORECASE,
)


def trova_posizione_bio(testo):
    """Trova la frase di presentazione dell'autore (es. X è stato/a ..., X è un/una ...).
    Salta gli avvisi di Wikipedia ('Questa voce ...') e preferisce la frase
    preceduta da una data (anno di 4 cifre)."""
    candidati = []
    for m in ANCORA_BIO.finditer(testo[:6000]):
        if "Questa voce" in testo[max(0, m.start() - 120):m.start()]:
            continue
        candidati.append(m)
    if not candidati:
        return None, None
    con_data = [m for m in candidati
                if re.search(r"\d{4}", testo[max(0, m.start() - 400):m.start()])]
    m = (con_data or candidati)[0]
    genere = "M" if m.group(1) else "F"
    return m.start(), genere


def estrai_nazionalita(testo, posizione_bio):
    finestra = testo[posizione_bio:posizione_bio + 300]
    frase_match = re.search(r"è\s+(?:stat[oa]|uno|una|un['’]|un)\b(.*?)\.", finestra, re.IGNORECASE)
    if not frase_match:
        return None
    parole = re.findall(r"[A-Za-zàèéìòù]+", frase_match.group(1))
    return parole[-1].capitalize() if parole else None


MESI_ITALIANI = {
    "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
    "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
    "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12",
}


def data_italiana_a_iso(giorno, mese_nome, anno):
    mese = MESI_ITALIANI.get(mese_nome.lower())
    if not mese:
        return None
    return f"{anno}-{mese}-{giorno.zfill(2)}"


def estrai_nascita_morte(testo, posizione_bio):
    testo = testo[max(0, posizione_bio - 300):posizione_bio]
    data = r"(\d{1,2})[º°]?\s+(\w+)(?:\s*\[[^\]]*\])?\s+(\d{4})(?:\s*\[[^\]]*\])*"
    pattern_completo = re.search(
        r"(?:\(|;)\s*([^,;()]+?)\s*,\s*" + data + r"\s*[–\-]\s*"
        r"([^,;()]+?)\s*,\s*" + data + r"\s*\)",
        testo,
    )
    if pattern_completo:
        luogo_n, g_n, m_n, a_n, luogo_m, g_m, m_m, a_m = pattern_completo.groups()
        return (
            data_italiana_a_iso(g_n, m_n, a_n), luogo_n.strip(),
            data_italiana_a_iso(g_m, m_m, a_m), luogo_m.strip(),
        )
    pattern_solo_nascita = re.search(
        r"(?:\(|;)\s*([^,;()]+?)\s*,\s*" + data + r"\s*\)", testo
    )
    if pattern_solo_nascita:
        luogo_n, g_n, m_n, a_n = pattern_solo_nascita.groups()
        return data_italiana_a_iso(g_n, m_n, a_n), luogo_n.strip(), None, None
    return None, None, None, None


def contenuto_articolo(soup):
    corpo = soup.find(id="mw-content-text")
    return corpo if corpo else soup


def arricchisci_autore(nome):
    url = url_wikipedia(nome)
    html = scarica_pagina(url)
    if html is None:
        return {"data_nascita": None, "luogo_nascita": None, "data_morte": None,
                "luogo_morte": None, "genere": None, "nazionalita": None, "trovato": False}
    soup_completo = BeautifulSoup(html, "html.parser")
    soup = contenuto_articolo(soup_completo)
    testo = soup.get_text(" ", strip=True)
    posizione_bio, genere = trova_posizione_bio(testo)
    if posizione_bio is None:
        nazionalita = None
        data_nascita = luogo_nascita = data_morte = luogo_morte = None
    else:
        nazionalita = estrai_nazionalita(testo, posizione_bio)
        data_nascita, luogo_nascita, data_morte, luogo_morte = estrai_nascita_morte(testo, posizione_bio)
    return {
        "data_nascita": data_nascita,
        "luogo_nascita": luogo_nascita,
        "data_morte": data_morte,
        "luogo_morte": luogo_morte,
        "genere": genere,
        "nazionalita": nazionalita,
        "trovato": True,
    }


def main():
    autori = estrai_autori_unici(INPUT)
    print(f"Trovati {len(autori)} autori unici nel catalogo")
    if LIMITE is not None:
        autori = autori[:LIMITE]
        print(f"Modalita' test: elaboro solo i primi {LIMITE}")
    risultati = {}
    for i, autore in enumerate(autori, start=1):
        print(f"[{i}/{len(autori)}] {autore}...")
        risultati[autore] = arricchisci_autore(autore)
        time.sleep(PAUSA)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(risultati, f, ensure_ascii=False, indent=2)
    trovati = sum(1 for v in risultati.values() if v["trovato"])
    completi = sum(1 for v in risultati.values() if v["trovato"] and v["genere"] and v["data_nascita"])
    print(f"\nSalvati {len(risultati)} autori in {OUTPUT}")
    print(f"  - {trovati} trovati su Wikipedia")
    print(f"  - {completi} con genere e data di nascita presenti")


if __name__ == "__main__":
    main()
