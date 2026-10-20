import json
from pathlib import Path

import matplotlib.pyplot as plt

from analisi_donne import genere_dal_nome, persone

ROSA, ROSA_SC = "#d55181", "#f2c4d4"
libri = json.loads(Path("dataset_completo.json").read_text(encoding="utf-8"))
c = {"F": [0, 0], "M": [0, 0]}
for l in libri:
    ga = l.get("genere_autore")
    if ga not in c:
        continue
    for nome in persone(l.get("curatore")):
        g = genere_dal_nome(nome)
        if g:
            c[ga][0 if g == "F" else 1] += 1

fig, ax = plt.subplots(figsize=(8, 4.2))
for i, ga in enumerate(["F", "M"]):
    d, u = c[ga]
    p = d / (d + u) * 100
    ax.barh(i, 100, color=ROSA_SC, height=0.55)
    ax.barh(i, p, color=ROSA, height=0.55)
    ax.text(p / 2, i, f"{p:.0f}% donne\n({d} crediti)", ha="center", va="center", color="white", fontsize=10)
    ax.text(p + (100 - p) / 2, i, f"{100 - p:.0f}% uomini\n({u})", ha="center", va="center", color="#52514e", fontsize=10)
ax.set_yticks([0, 1]); ax.set_yticklabels(["Libri di autrici", "Libri di autori"]); ax.invert_yaxis()
ax.set_xlim(0, 100); ax.set_xticks([])
ax.set_title("Chi traduce e cura: curatrici e traduttrici per genere dell'autore", loc="left", fontsize=12)
for lato in ("top", "right", "bottom"):
    ax.spines[lato].set_visible(False)
fig.tight_layout()
fig.savefig("chi_traduce_chi.png", dpi=150, facecolor="white")
for ga in "FM":
    d, u = c[ga]
    print(f"Autore {ga}: {d} donne su {d + u} crediti ({d / (d + u) * 100:.0f}%)")
