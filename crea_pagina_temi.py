import json
import random
import pandas as pd

n = pd.read_csv("campione_nascosto.csv")[["numero_collana", "temi"]]
d = pd.read_csv("dataset_completo.csv")[["numero_collana", "autore", "titolo", "url_libro"]]
desc = pd.read_csv("descrizioni_adelphi.csv")[["numero_collana", "descrizione"]]
m = n.merge(d, on="numero_collana").merge(desc, on="numero_collana", how="left")

# temi veri di ogni libro (separati da ";")
temi = {r.numero_collana: [t.strip() for t in str(r.temi).split(";") if t.strip()]
        for r in m.itertuples()}

random.seed(11)
records = []
for r in m.itertuples():
    k = r.numero_collana
    altri = [t for kk, lista in temi.items() if kk != k for t in lista]
    esca = random.choice(altri)  # tema di un ALTRO libro: sicuramente sbagliato
    items = [{"t": t, "e": 0} for t in temi[k]] + [{"t": esca, "e": 1}]
    random.shuffle(items)
    records.append({"numero_collana": str(k), "autore": str(r.autore), "titolo": str(r.titolo),
                    "descrizione": "" if pd.isna(r.descrizione) else str(r.descrizione),
                    "url_libro": str(r.url_libro), "items": items})

html = open("temi_modello.html").read()
html = html.replace("__DATI__", json.dumps(records, ensure_ascii=False).replace("</", "<\\/"))
open("temi.html", "w").write(html)
print(len(records), "libri,", sum(len(x["items"]) for x in records), "temi da giudicare")
