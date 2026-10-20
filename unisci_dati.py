import csv
import json
from pathlib import Path

LIBRI = "biblioteca_adelphi_arricchito.json"
AUTORI = "autori_arricchiti.json"
DESCRIZIONI = "descrizioni_adelphi.csv"
SCHEDE = "schede_qualitative.json"
OUT_JSON = "dataset_completo.json"
OUT_CSV = "dataset_completo.csv"


def chiave(numero, titolo):
    t = "".join(c for c in str(titolo).lower() if c.isalnum())
    return f"{numero}|{t}"


def main():
    libri = json.loads(Path(LIBRI).read_text(encoding="utf-8"))
    autori = json.loads(Path(AUTORI).read_text(encoding="utf-8"))
    schede = {chiave(s["numero_collana"], s["titolo"]): s["scheda"]
              for s in json.loads(Path(SCHEDE).read_text(encoding="utf-8"))}
    with open(DESCRIZIONI, encoding="utf-8", newline="") as f:
        desc = {chiave(r["numero_collana"], r["titolo"]): r for r in csv.DictReader(f)}

    righe = []
    for b in libri:
        n = str(b.get("numero_collana", ""))
        a = autori.get(b.get("autore", ""), {}) or {}
        k = chiave(n, b.get("titolo", ""))
        d = desc.get(k, {})
        s = schede.get(k) or {}
        righe.append({
            "numero_collana": n,
            "autore": b.get("autore", ""),
            "titolo": b.get("titolo", ""),
            "curatore": b.get("curatore", ""),
            "editore": "Adelphi",
            "luogo_pubblicazione": "Milano",
            "anno": b.get("anno"),
            "ebook_disponibile": d.get("ebook_disponibile") == "True",
            "url_libro": d.get("url_libro", ""),
            "genere_autore": b.get("genere_autore"),
            "nazionalita_autore": b.get("nazionalita_autore"),
            "data_nascita_autore": a.get("data_nascita"),
            "luogo_nascita_autore": a.get("luogo_nascita"),
            "data_morte_autore": a.get("data_morte"),
            "luogo_morte_autore": a.get("luogo_morte"),
            "genere_letterario": s.get("genere"),
            "temi": s.get("temi"),
            "affidabilita_scheda": s.get("affidabilita"),
        })

    Path(OUT_JSON).write_text(json.dumps(righe, ensure_ascii=False, indent=2), encoding="utf-8")
    campi = list(righe[0].keys())
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        for r in righe:
            r2 = dict(r)
            r2["temi"] = "; ".join(r["temi"]) if r["temi"] else ""
            w.writerow(r2)

    print(f"Salvati {len(righe)} libri in {OUT_JSON} e {OUT_CSV}")
    print(f"  - {sum(1 for r in righe if r['genere_letterario'])} con scheda qualitativa")
    print(f"  - {sum(1 for r in righe if r['ebook_disponibile'])} con eBook")
    print(f"  - {sum(1 for r in righe if r['luogo_nascita_autore'])} con luogo di nascita dell'autore")
    print(f"  - {sum(1 for r in righe if r['curatore'])} con curatore/traduttore")


if __name__ == "__main__":
    main()
