import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

ROSA, GRIGIO = "#d55181", "#9a9a96"
libri = json.loads(Path("dataset_completo.json").read_text(encoding="utf-8"))
F = [l for l in libri if l.get("genere_autore") == "F"]
M = [l for l in libri if l.get("genere_autore") == "M"]
cf = Counter(l["genere_letterario"] for l in F)
cm = Counter(l["genere_letterario"] for l in M)
generi = sorted(set(cf) | set(cm), key=lambda g: -(cf[g] + cm[g]))
generi = [g for g in generi if cf[g] + cm[g] >= 10]

y = range(len(generi))
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.barh([i + 0.2 for i in y], [cf[g] / len(F) * 100 for g in generi], height=0.38, color=ROSA,
        label=f"Autrici ({len(F)} volumi)")
ax.barh([i - 0.2 for i in y], [cm[g] / len(M) * 100 for g in generi], height=0.38, color=GRIGIO,
        label=f"Autori ({len(M)} volumi)")
for i, g in enumerate(generi):
    ax.text(cf[g] / len(F) * 100 + 0.5, i + 0.2, f"{cf[g] / len(F) * 100:.0f}% ({cf[g]})", va="center", fontsize=9)
    ax.text(cm[g] / len(M) * 100 + 0.5, i - 0.2, f"{cm[g] / len(M) * 100:.0f}% ({cm[g]})", va="center", fontsize=9, color="#52514e")
ax.set_yticks(list(y)); ax.set_yticklabels(generi); ax.invert_yaxis()
ax.set_xlabel("% dei volumi di ciascun gruppo")
ax.set_xlim(0, 48)
ax.set_title("Generi letterari: autrici e autori a confronto", loc="left", fontsize=13)
ax.legend(frameon=False, loc="lower right")
for lato in ("top", "right"):
    ax.spines[lato].set_visible(False)
fig.tight_layout()
fig.savefig("generi_donne.png", dpi=150, facecolor="white")
print("Salvato: generi_donne.png")
