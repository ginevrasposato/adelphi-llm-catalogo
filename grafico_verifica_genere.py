import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BLU = "#1f77b4"
INCHIOSTRO = "#222222"
INCHIOSTRO_SOFT = "#52514e"

m = pd.read_csv("metriche_per_genere_finali.csv")
m["genere_llm"] = m["genere_llm"].replace({"religione/spiritualita": "religione/spiritualità"})
m["pct"] = m["sum"] / m["count"] * 100
m = m.sort_values(["pct", "count"]).reset_index(drop=True)
totale = m["sum"].sum() / m["count"].sum() * 100

fig, ax = plt.subplots(figsize=(9, 6.2))
ax.barh(m["genere_llm"], m["pct"], color=BLU, height=0.6)
for i, r in m.iterrows():
    ax.text(r["pct"] + 1.5, i, f"{r['pct']:.0f}%  ({r['sum']}/{r['count']})",
            va="center", fontsize=11, color=INCHIOSTRO, zorder=3,
            bbox=dict(fc="white", ec="none", pad=1.5))
ax.axvline(totale, color=INCHIOSTRO_SOFT, ls="--", lw=1.2, zorder=2)
ax.text(totale + 1.2, len(m) - 0.45, f"totale {totale:.0f}%", ha="left", va="bottom",
        fontsize=10, color=INCHIOSTRO_SOFT)
ax.set_xlim(0, 125)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("Libri in cui il genere del modello coincide con quello di riferimento (%)",
              color=INCHIOSTRO_SOFT, fontsize=10)
ax.set_title("Verifica del genere: coincidenza per genere (60 libri)", loc="left",
             color=INCHIOSTRO, fontsize=13, pad=22)
for lato in ("top", "right"):
    ax.spines[lato].set_visible(False)
for lato in ("left", "bottom"):
    ax.spines[lato].set_color("#cccccc")
ax.tick_params(colors=INCHIOSTRO_SOFT, labelsize=11)
fig.text(0.01, 0.005, "5–7 libri per genere: le stime per singolo genere sono molto incerte.",
         fontsize=9, color=INCHIOSTRO_SOFT)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("verifica_genere.png", dpi=150, facecolor="white")
print("Salvato: verifica_genere.png")
