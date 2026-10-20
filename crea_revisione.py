import json
import random
import pandas as pd

a = pd.read_csv("campione_annotato.csv")
n = pd.read_csv("campione_nascosto.csv")[["numero_collana", "genere_letterario"]]
d = pd.read_csv("dataset_completo.csv")[["numero_collana", "autore", "titolo", "url_libro"]]
desc = pd.read_csv("descrizioni_adelphi.csv")[["numero_collana", "descrizione"]]
m = a.merge(n, on="numero_collana").merge(d, on="numero_collana").merge(desc, on="numero_collana", how="left")

# solo i libri su cui tu e l'LLM non siete d'accordo
m = m[m["genere_tuo"] != m["genere_letterario"]].copy()

# etichette A/B in ordine casuale: non si vede quale e' dell'LLM
random.seed(7)
coppie = []
for _, r in m.iterrows():
    x = [r["genere_tuo"], r["genere_letterario"]]
    random.shuffle(x)
    coppie.append(x)
m["A"] = [c[0] for c in coppie]
m["B"] = [c[1] for c in coppie]

colonne = ["numero_collana", "autore", "titolo", "descrizione", "url_libro", "A", "B"]
dati = json.dumps(m[colonne].fillna("").astype(str).to_dict("records"), ensure_ascii=False)
generi = open("generi_ammessi.txt").read().split("\n")
html = open("revisione_modello.html").read()
html = html.replace("__DATI__", dati.replace("</", "<\\/"))
html = html.replace("__GENERI__", json.dumps(generi, ensure_ascii=False))
open("revisione.html", "w").write(html)
print(len(m), "libri da rivedere")
