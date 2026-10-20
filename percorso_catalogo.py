import pandas as pd, html
df = pd.read_csv("dataset_completo.csv")
df["num"] = pd.to_numeric(df["numero_collana"], errors="coerce")
df = df.sort_values("num")
def t(v):
    return "" if pd.isna(v) else str(v)
righe = []
for _, r in df.iterrows():
    num = "" if pd.isna(r["num"]) else str(int(r["num"]))
    autore = html.escape(t(r["autore"]))
    titolo = html.escape(t(r["titolo"]))
    url = html.escape(t(r["url_libro"]), quote=True)
    genere = html.escape(t(r["genere_letterario"]))
    temi = html.escape(t(r["temi"]))
    anno = "" if pd.isna(r["anno"]) else str(int(r["anno"]))
    ebook = "sì" if bool(r["ebook_disponibile"]) else "no"
    link = f'<a href="{url}" target="_blank" rel="noopener">{titolo}</a>' if url else titolo
    txt = html.escape(f"{num} {autore} {titolo} {genere} {temi} {anno}".lower(), quote=True)
    righe.append(f'<tr data-txt="{txt}" data-g="{genere}" data-e="{ebook}"><td data-s="{num or 0}">{num}</td><td>{autore}</td><td>{link}</td><td>{genere}</td><td>{temi}</td><td data-s="{anno or 0}">{anno}</td><td>{ebook}</td></tr>')
generi = sorted(set(html.escape(t(g)) for g in df["genere_letterario"] if t(g)))
opz = "".join(f'<option value="{g}">{g}</option>' for g in generi)
a = open("parte1.html", encoding="utf-8").read()
b = open("parte2.html", encoding="utf-8").read()
a = a.replace("%%N%%", str(len(df))).replace("%%OPZ%%", opz)
open("catalogo_adelphi.html", "w", encoding="utf-8").write(a + "\n".join(righe) + b)
print("Salvato: catalogo_adelphi.html |", len(df), "volumi")
