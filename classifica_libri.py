import csv
import json
import os
import time
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

INPUT_DESCRIZIONI = "descrizioni_adelphi.csv"
INPUT_LIBRI = "biblioteca_adelphi_pulito.csv"
OUTPUT = "schede_qualitative.json"
LIMITE = None         # None = tutti i libri
PAUSA = 0.5
MODELLO = "claude-haiku-5-5"

GENERI = ["romanzo", "racconti", "poesia", "teatro", "saggio", "biografia/memorie",
          "filosofia", "religione/spiritualita", "storia", "scienze", "altro"]

load_dotenv()
client = Anthropic(timeout=60.0, max_retries=3)

PROMPT_SISTEMA = """Sei un assistente di analisi letteraria. Ti vengono dati autore,
titolo e una breve descrizione di un libro della collana Biblioteca Adelphi.
Produci una scheda qualitativa basandoti sul testo fornito; puoi usare il
titolo e l'autore per orientarti, ma non inventare dettagli di trama.

Rispondi sempre e solo con un oggetto JSON con questo schema:

{
  "genere": una sola stringa scelta tra: romanzo, racconti, poesia, teatro, saggio, biografia/memorie, filosofia, religione/spiritualita, storia, scienze, altro,
  "temi": [lista di 2-4 stringhe brevi; temi di contenuto specifici al libro (mai giudizi sullo stile o sulla qualita' della scrittura), non generici (meglio 'la maternita' in tempo di guerra' che 'guerra')],
  "affidabilita": "alta" se la descrizione dice di cosa parla il libro, "media" se dice poco e hai integrato con titolo e autore, "bassa" solo se la descrizione e' fatta esclusivamente di giudizi o citazioni di recensioni senza dire di cosa parla il libro
}

Non aggiungere altro testo prima o dopo il JSON."""


def carica_libri():
    anagrafica = {}
    if Path(INPUT_LIBRI).exists():
        with open(INPUT_LIBRI, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                anagrafica[str(r.get("numero_collana", "")).strip()] = r
    with open(INPUT_DESCRIZIONI, encoding="utf-8", newline="") as f:
        libri = list(csv.DictReader(f))
    for l in libri:
        l["autore"] = anagrafica.get(l["numero_collana"].strip(), {}).get("autore", "")
    return libri


def estrai_json_da_risposta(testo):
    inizio = testo.find("{")
    fine = testo.rfind("}")
    if inizio == -1 or fine == -1:
        return None
    try:
        return json.loads(testo[inizio:fine + 1])
    except json.JSONDecodeError:
        return None


def scheda_valida(s):
    return (isinstance(s, dict) and s.get("genere") in GENERI
            and isinstance(s.get("temi"), list)
            and s.get("affidabilita") in ("alta", "media", "bassa"))


def analizza(libro):
    prompt = (f"Autore: {libro['autore'] or 'non indicato'}\n"
              f"Titolo: {libro['titolo']}\n"
              f"Descrizione: {libro['descrizione']}")
    try:
        r = client.messages.create(model=MODELLO, max_tokens=2000,
                                   system=PROMPT_SISTEMA,
                                   messages=[{"role": "user", "content": prompt}])
        scheda = estrai_json_da_risposta("".join(b.text for b in r.content if b.type == "text"))
        return scheda if scheda_valida(scheda) else None
    except Exception as errore:
        print(f"   errore: {errore}")
        return None


def main():
    libri = carica_libri()
    if LIMITE is not None:
        libri = libri[:LIMITE]

    gia = {}
    if Path(OUTPUT).exists():
        for r in json.loads(Path(OUTPUT).read_text(encoding="utf-8")):
            if r.get("scheda"):
                gia[r["numero_collana"]] = r

    risultati = []
    for i, libro in enumerate(libri, start=1):
        n = libro["numero_collana"]
        if n in gia:
            risultati.append(gia[n])
            continue
        print(f"[{i}/{len(libri)}] {libro['autore']} - {libro['titolo']}")
        scheda = analizza(libro)
        risultati.append({"numero_collana": n, "autore": libro["autore"],
                          "titolo": libro["titolo"], "scheda": scheda})
        Path(OUTPUT).write_text(json.dumps(risultati, ensure_ascii=False, indent=2),
                                encoding="utf-8")
        time.sleep(PAUSA)

    ok = sum(1 for r in risultati if r["scheda"])
    print(f"\nSalvati {len(risultati)} libri in {OUTPUT}")
    print(f"  - {ok} schede valide, {len(risultati) - ok} mancanti")


if __name__ == "__main__":
    main()
