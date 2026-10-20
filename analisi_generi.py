import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

INPUT = "dataset_completo.json"

BLU = "#2a78d6"
COLORI = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
GRIGIO = "#9a9a96"
INCHIOSTRO = "#222222"
INCHIOSTRO_SOFT = "#52514e"
ALTRI = "altri generi"


def stile(ax):
    for lato in ("top", "right"):
        ax.spines[lato].set_visible(False)
    for lato in ("left", "bottom"):
        ax.spines[lato].set_color("#cccccc")
    ax.tick_params(colors=INCHIOSTRO_SOFT)


def grafico_generi(df):
    conteggi = df["genere_letterario"].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, 0.45 * len(conteggi) + 1.5))
    barre = ax.barh(conteggi.index, conteggi.values, color=BLU, height=0.6)
    for barra, valore in zip(barre, conteggi.values):
        ax.text(valore + conteggi.max() * 0.01, barra.get_y() + barra.get_height() / 2,
                str(valore), va="center", color=INCHIOSTRO, fontsize=10)
    ax.set_title(f"Biblioteca Adelphi: generi letterari ({len(df)} volumi)",
                 loc="left", color=INCHIOSTRO, fontsize=13)
    ax.set_xlabel("Numero di volumi", color=INCHIOSTRO_SOFT)
    ax.set_xlim(0, conteggi.max() * 1.1)
    stile(ax)
    fig.tight_layout()
    fig.savefig("generi.png", dpi=150, facecolor="white")
    plt.close(fig)


def grafico_generi_per_decennio(df):
    top = df["genere_letterario"].value_counts().index[:5].tolist()
    df = df.copy()
    df["gruppo"] = df["genere_letterario"].where(df["genere_letterario"].isin(top), ALTRI)
    df["decennio"] = (df["anno"] // 10 * 10).astype(int)
    tab = pd.crosstab(df["decennio"], df["gruppo"])
    quote = tab.div(tab.sum(axis=1), axis=0) * 100
    ordine = top + [ALTRI]
    quote = quote.reindex(columns=[c for c in ordine if c in quote.columns])

    fig, ax = plt.subplots(figsize=(10, 5.5))
    base = pd.Series(0.0, index=quote.index)
    colori = dict(zip(top, COLORI))
    colori[ALTRI] = GRIGIO
    x = range(len(quote.index))
    for genere in quote.columns:
        ax.bar(x, quote[genere], bottom=base, color=colori[genere], label=genere,
               width=0.7, edgecolor="white", linewidth=1.5)
        base += quote[genere]
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{d}s\n(n={tab.loc[d].sum()})" for d in quote.index])
    ax.set_ylabel("% dei volumi del decennio", color=INCHIOSTRO_SOFT)
    ax.set_ylim(0, 100)
    ax.set_title("Biblioteca Adelphi: composizione per genere, per decennio",
                 loc="left", color=INCHIOSTRO, fontsize=13)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    stile(ax)
    fig.tight_layout()
    fig.savefig("generi_per_decennio.png", dpi=150, facecolor="white")
    plt.close(fig)


def main():
    df = pd.DataFrame(json.loads(Path(INPUT).read_text(encoding="utf-8")))
    df["anno"] = pd.to_numeric(df["anno"], errors="coerce")
    df = df.dropna(subset=["anno", "genere_letterario"])
    grafico_generi(df)
    grafico_generi_per_decennio(df)
    print(f"Volumi analizzati: {len(df)}")
    print("Salvati: generi.png, generi_per_decennio.png")


if __name__ == "__main__":
    main()
