import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

INPUT = "dataset_completo.json"
BLU = "#2a78d6"
GRIGIO_CHIARO = "#d9d9d6"
INCHIOSTRO = "#222222"
INCHIOSTRO_SOFT = "#52514e"


def main():
    df = pd.DataFrame(json.loads(Path(INPUT).read_text(encoding="utf-8")))
    df["anno"] = pd.to_numeric(df["anno"], errors="coerce")
    df = df.dropna(subset=["anno"]).copy()
    df["decennio"] = (df["anno"] // 10 * 10).astype(int)
    tab = df.groupby("decennio")["ebook_disponibile"].agg(["sum", "count"])
    tab["pct"] = tab["sum"] / tab["count"] * 100

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = range(len(tab))
    ax.bar(x, [100] * len(tab), color=GRIGIO_CHIARO, width=0.7, label="solo cartaceo")
    ax.bar(x, tab["pct"], color=BLU, width=0.7, label="anche eBook")
    for i, (pct, n) in enumerate(zip(tab["pct"], tab["count"])):
        ax.text(i, pct + 2, f"{pct:.0f}%", ha="center", color=INCHIOSTRO, fontsize=11)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{d}s\n(n={n})" for d, n in zip(tab.index, tab["count"])])
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("% dei volumi del decennio", color=INCHIOSTRO_SOFT)
    totale = int(tab["sum"].sum())
    ax.set_title(f"Biblioteca Adelphi: volumi disponibili anche in eBook ({totale} su {int(tab['count'].sum())})",
                 loc="left", color=INCHIOSTRO, fontsize=13)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    for lato in ("top", "right"):
        ax.spines[lato].set_visible(False)
    for lato in ("left", "bottom"):
        ax.spines[lato].set_color("#cccccc")
    ax.tick_params(colors=INCHIOSTRO_SOFT)
    fig.tight_layout()
    fig.savefig("formati.png", dpi=150, facecolor="white")
    print(f"Volumi con eBook: {totale} su {int(tab['count'].sum())} ({totale / tab['count'].sum() * 100:.0f}%)")
    print("Salvato: formati.png")


if __name__ == "__main__":
    main()
