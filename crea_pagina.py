import json
import pandas as pd

d = pd.read_csv("campione_da_annotare.csv").fillna("").astype(str)
generi = open("generi_ammessi.txt").read().split("\n")
html = open("annotazione_modello.html").read()
dati = json.dumps(d.to_dict("records"), ensure_ascii=False).replace("</", "<\\/")
html = html.replace("__DATI__", dati)
html = html.replace("__GENERI__", json.dumps(generi, ensure_ascii=False))
open("annotazione.html", "w").write(html)
print(len(d), "libri nella pagina")
