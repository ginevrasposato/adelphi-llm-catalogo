import json
from math import erfc, sqrt
from pathlib import Path

import pandas as pd

import analisi_donne as ad


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    h = z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return c - h, c + h


def confronta(titolo, k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p2 - p1
    lo = d - sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2)
    hi = d + sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2)
    pool = (k1 + k2) / (n1 + n2)
    z = d / sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    p = erfc(abs(z) / sqrt(2))
    print(f"\n{titolo}")
    print(f"  Autrici:                {k1}/{n1} = {p1:.1%}  (IC95% {l1:.1%}-{u1:.1%})")
    print(f"  Curatrici/traduttrici:  {k2}/{n2} = {p2:.1%}  (IC95% {l2:.1%}-{u2:.1%})")
    print(f"  Differenza: {d * 100:.1f} punti percentuali, IC95% {lo * 100:.1f} / {hi * 100:.1f}, p = {p:.1e}")


libri = json.loads(Path("dataset_completo.json").read_text(encoding="utf-8"))
df = pd.DataFrame(libri)
df["anno"] = pd.to_numeric(df["anno"], errors="coerce")
df = df.dropna(subset=["anno"]).copy()

crediti = []
for _, r in df.iterrows():
    for nome in ad.persone(r["curatore"]):
        crediti.append({"persona": nome, "genere": ad.genere_dal_nome(nome)})
cr = pd.DataFrame(crediti)

# per volume e per credito
a = df["genere_autore"]
k1, n1 = (a == "F").sum(), a.isin(["M", "F"]).sum()
k2, n2 = (cr["genere"] == "F").sum(), cr["genere"].isin(["M", "F"]).sum()
confronta("PER VOLUME / PER CREDITO", k1, n1, k2, n2)

# per persone distinte
pa = df[a.isin(["M", "F"])].drop_duplicates("autore")["genere_autore"]
pc = cr[cr["genere"].isin(["M", "F"])].drop_duplicates("persona")["genere"]
confronta("PER PERSONE DISTINTE", (pa == "F").sum(), len(pa), (pc == "F").sum(), len(pc))
