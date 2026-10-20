import os
import pandas as pd
from math import comb

def wilson(p, N, z=1.96):
    c = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    h = z * ((p * (1 - p) / N + z**2 / (4 * N**2)) ** 0.5) / (1 + z**2 / N)
    return c - h, c + h

t = pd.read_csv("temi_giudicati.csv")
print("Giudizi mancanti:", t["giudizio"].isna().sum())
t["pert"] = (t["giudizio"] == "pertinente")

# 1) esche
e = t[t["esca"] == 1]
print(f"\nEsche accettate come pertinenti: {e['pert'].sum()}/{len(e)}")
print(e[e["pert"]][["numero_collana", "tema"]].to_string(index=False))

# 2) temi veri, escludendo i libri giudicati per esclusione
r = t[t["esca"] == 0].copy()
nv = set()
if os.path.exists("temi_non_verificati.txt"):
    nv = {int(x) for x in open("temi_non_verificati.txt").read().split()}
print(f"\nLibri non verificati (esclusi dal calcolo): {len(nv)}")
v = r[~r["numero_collana"].isin(nv)]
N = len(v); p = v["pert"].mean(); lo, hi = wilson(p, N)
print(f"Precisione dei temi: {p:.0%} ({v['pert'].sum()}/{N}), IC95% {lo:.0%}-{hi:.0%}")

# 3) per libro: scheda adeguata se almeno meta' dei temi e' pertinente
b = v.groupby("numero_collana")["pert"].mean().rename("quota").reset_index()
b["temi_ok"] = b["quota"] >= 0.5
M = len(b); q = b["temi_ok"].mean(); lo, hi = wilson(q, M)
print(f"Schede adeguate: {q:.0%} ({b['temi_ok'].sum()}/{M}), IC95% {lo:.0%}-{hi:.0%}")
b.to_csv("temi_per_libro.csv", index=False)

# 4) confronto con il genere sugli stessi libri
a = pd.read_csv("campione_annotato.csv")
n = pd.read_csv("campione_nascosto.csv")[["numero_collana", "genere_letterario"]]
rv = pd.read_csv("campione_rivisto.csv")
g = a.merge(n, on="numero_collana").merge(rv, on="numero_collana", how="left")
g["finale"] = g["genere_finale"].fillna(g["genere_tuo"])
g["genere_ok"] = g["finale"] == g["genere_letterario"]
c = b.merge(g[["numero_collana", "genere_ok"]], on="numero_collana")
print(f"\nStessi {len(c)} libri: genere corretto {c['genere_ok'].mean():.0%}, temi adeguati {c['temi_ok'].mean():.0%}")
print(pd.crosstab(c["genere_ok"], c["temi_ok"], rownames=["genere ok"], colnames=["temi ok"]))
x = ((c["temi_ok"]) & (~c["genere_ok"])).sum()
y = ((~c["temi_ok"]) & (c["genere_ok"])).sum()
if x + y > 0:
    print(f"Solo temi ok: {x}, solo genere ok: {y}, McNemar esatto p = {min(1, 2 * sum(comb(x + y, k) for k in range(min(x, y) + 1)) / 2 ** (x + y)):.3f}")

# 5) per trasparenza: stessa precisione includendo anche i libri per esclusione
pa = r["pert"].mean()
print(f"\nPer confronto, con anche i libri per esclusione: {pa:.0%} ({r['pert'].sum()}/{len(r)}) - valore gonfiato, non e' quello di riferimento")
