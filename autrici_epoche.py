import json
import re
from pathlib import Path

import matplotlib.pyplot as plt

ROSA, ROSA_SC = "#d55181", "#f2c4d4"
EPOCHE = [("prima del 1800", 0, 1800), ("1800-1849", 1800, 1850), ("1850-1879", 1850, 1880),
          ("1880-1899", 1880, 1900), ("1900-1919", 1900, 1920), ("1920-1945", 1920, 1946)]

libri = json.loads(Path("dataset_completo.json").read_text(encoding="utf-8"))
autori = {}
for l in libri:
    m = re.search(r"(\d{4})", l.get("data_nascita_autore") or "")
    if l.get("genere_autore") in ("M", "F") and m:
        autori[l["autore"]] = (l["genere_autore"], int(m.group(1)))

etich, donne, tot = [], [], []
for nome, lo, hi in EPOCHE:
    g = [x for x, y in autori.values() if lo <= y < hi]
    etich.append(nome); tot.append(len(g)); donne.append(sum(x == "F" for x in g))
pct = [d / t * 100 if t else 0 for d, t in zip(donne, tot)]

fig, ax = plt.subplots(figsize=(10, 5.2))
ax.bar(range(len(pct)), [100] * len(pct), color=ROSA_SC, width=0.7)
ax.bar(range(len(pct)), pct, color=ROSA, width=0.7)
for i, (p, d, t) in enumerate(zip(pct, donne, tot)):
    ax.text(i, p + 2, f"{p:.0f}%\n({d} su {t})", ha="center", fontsize=10, color="#222222")
ax.set_xticks(range(len(pct)))
ax.set_xticklabels(etich, fontsize=9)
ax.set_ylim(0, 100)
ax.set_ylabel("% di autrici (barra piena) sul totale degli autori", color="#52514e", fontsize=9)
ax.set_title("Autrici per epoca di nascita (autori distinti)", loc="left", fontsize=13, color="#222222")
for lato in ("top", "right"):
    ax.spines[lato].set_visible(False)
fig.tight_layout()
fig.savefig("autrici_epoche.png", dpi=150, facecolor="white")
print(f"{sum(donne)} autrici su {sum(tot)} autori con data di nascita nota")
for e, p, d, t in zip(etich, pct, donne, tot):
    print(f"  {e}: {p:.0f}% ({d}/{t})")
