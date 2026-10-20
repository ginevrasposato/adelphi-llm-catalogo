import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

INPUT = "dataset_completo.json"
ERE = ["nati prima del 1800", "nati nell'Ottocento (1800-1899)", "nati nel Novecento (1900-1945)"]
COLORI = ["#2a78d6", "#eb6834", "#1baf7a"]
INCHIOSTRO = "#222222"
INCHIOSTRO_SOFT = "#52514e"


def era(anno_nascita):
    if anno_nascita < 1800:
        return ERE[0]
    if anno_nascita < 1900:
        return ERE[1]
    return ERE[2]


def main():
    df = pd.DataFrame(json.loads(Path(INPUT).read_text(encoding="utf-8")))
    totale = len(df)
    df["nascita"] = pd.to_numeric(df["data_nascita_autore"].astype(str).str[:4], errors="coerce")
    df["anno"] = pd.to_numeric(df["anno"], errors="coerce")
    df = df.dropna(subset=["nascita", "anno"]).copy()
    df["era"] = df["nascita"].apply(era)
    df["decennio"] = (df["anno"] // 10 * 10).astype(int)

    tab = pd.crosstab(df["decennio"], df["era"]).reindex(columns=ERE, fill_value=0)
    quote = tab.div(tab.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 5.5))
    base = pd.Series(0.0, index=quote.index)
    x = range(len(quote.index))
    for colore, e in zip(COLORI, ERE):
        ax.bar(x, quote[e], bottom=base, color=colore, label=e, width=0.7,
               edgecolor="white", linewidth=1.5)
        base += quote[e]
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{d}s\n(n={tab.loc[d].sum()})" for d in quote.index])
    ax.set_ylabel("% dei volumi con anno di nascita noto", color=INCHIOSTRO_SOFT)
    ax.set_ylim(0, 100)
    ax.set_title("Biblioteca Adelphi: epoca di nascita degli autori, per decennio di pubblicazione",
                 loc="left", color=INCHIOSTRO, fontsize=13)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    for lato in ("top", "right"):
        ax.spines[lato].set_visible(False)
    for lato in ("left", "bottom"):
        ax.spines[lato].set_color("#cccccc")
    ax.tick_params(colors=INCHIOSTRO_SOFT)
    fig.tight_layout()
    fig.savefig("classici_contemporanei.png", dpi=150, facecolor="white")

    complessivo = df["era"].value_counts().reindex(ERE, fill_value=0)
    print(f"Volumi con anno di nascita dell'autore noto: {len(df)} su {totale}")
    for e in ERE:
        print(f"  - {e}: {complessivo[e]} ({complessivo[e] / len(df) * 100:.0f}%)")
    print("Salvato: classici_contemporanei.png")


if __name__ == "__main__":
    main()
