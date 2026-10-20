import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

INPUT = "dataset_completo.json"
ROSA = "#d55181"
INCHIOSTRO = "#222222"
INCHIOSTRO_SOFT = "#52514e"

FEMMINILI = set("""Ada Adriana Agnese Alessandra Amelia Amina Angela Anita Anna Annalisa Annamaria
Aurora Barbara Benedetta Bianca Carla Christine Cinzia Clara Claudia Cristina Daniela Daria Diana
Donata Ebe Ela Elena Eliana Elisabetta Eva Fabrizia Federica Flaminia Fleur Franca Francesca
Gabriella Germana Giacoma Gigliola Ginevra Gioia Gisèle Giulia Giuliana Giusi Grazia Graziella Ida
Idolina Ilide Isabella Katia Katinka Kathleen Kristin Krisztina Laura Lelia Lia Liliana Lina Linda
Lorenza Lucia Luciana Luigia Luisa Lydia Maia Mara Margherita Maria Mariagrazia Mariarosa Mariella
Marina Marinella Marlis Maurizia Melisenda Melita Monica Nadia Nancy Ornella Paola Patrizia Pia
Raffaella Renata Rita Rosalba Rosanna Rosella Sabina Saskia Serena Silvia Simona Sonia Susanna Tea
Teresa Tullia Valentina Valeria Vanda Vincenzina Vittoria""".split())

MASCHILI = set("""Alberto Albino Aldo Alessandro Alvise Andrea Angelo Antonio Arturo Bruno Carlo Cesare
Claudio Damiano Daniele Dario David Davide Dmitri Donato Edgardo Emilio Enrico Ernesto Ervino
Ettore Fabio Fabrizio Felice Flavio Francesco Franco Fulvio Furio Gaetano Gaspare Georg Gershom
Giacomo Giancarlo Giandonato Giannetto Gianni Gianroberto Gilberto Gioachino Giorgio Giovanni
Giulio Giuseppe Glauco Guido Heikki Henry Jacopo James Jean-Paul Jürgen Kenneth Lauro Leonardo
Leone Leopoldo Lionello Livio Lodovico Luca Luciano Luigi Manfredo Marco Marianello Mario Masolino
Massimo Matteo Maurizio Michele Nicola Nilo Ottavio Paolo Piergiulio Piero Pietro Richard Riccardo
Roberto Rodolfo Rolando Romano Romeo Ruggero Salvatore Sergio Shalom Silvio Simon Sven Svevo
Thomas Tommaso Ugo Umberto Vanni Vincenzo Willi""".split())


def persone(testo):
    testo = re.sub(r"(?i)\b(a cura di|traduzione di|traduzioni di)\b", ";", testo or "")
    nomi = []
    for blocco in testo.split(";"):
        for p in re.split(r",| e (?=[A-ZÀ-Ý])", blocco):
            p = p.strip(" .")
            if p:
                nomi.append(p)
    return nomi


def genere_dal_nome(nome):
    primo = nome.split()[0].strip(".")
    if primo in FEMMINILI:
        return "F"
    if primo in MASCHILI:
        return "M"
    return None


def percentuali(df, colonna):
    tab = df.groupby("decennio")[colonna].agg(
        donne=lambda s: (s == "F").sum(), noti=lambda s: s.isin(["M", "F"]).sum())
    tab["pct"] = tab["donne"] / tab["noti"] * 100
    return tab


def pannello(ax, tab, titolo):
    x = range(len(tab))
    ax.bar(x, tab["pct"], color=ROSA, width=0.7)
    for i, p in enumerate(tab["pct"]):
        ax.text(i, p + 1.5, f"{p:.0f}%", ha="center", color=INCHIOSTRO, fontsize=10)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{d}s\n(n={n})" for d, n in zip(tab.index, tab["noti"])], fontsize=8)
    ax.set_ylim(0, 80)
    ax.set_title(titolo, loc="left", color=INCHIOSTRO, fontsize=12)
    for lato in ("top", "right"):
        ax.spines[lato].set_visible(False)
    for lato in ("left", "bottom"):
        ax.spines[lato].set_color("#cccccc")
    ax.tick_params(colors=INCHIOSTRO_SOFT)


def main():
    libri = json.loads(Path(INPUT).read_text(encoding="utf-8"))
    df = pd.DataFrame(libri)
    df["anno"] = pd.to_numeric(df["anno"], errors="coerce")
    df = df.dropna(subset=["anno"]).copy()
    df["decennio"] = (df["anno"] // 10 * 10).astype(int)

    crediti = []
    for _, r in df.iterrows():
        for nome in persone(r["curatore"]):
            crediti.append({"decennio": r["decennio"], "persona": nome,
                            "genere": genere_dal_nome(nome)})
    cr = pd.DataFrame(crediti)

    aut = percentuali(df.rename(columns={"genere_autore": "g"}), "g")
    cur = percentuali(cr, "genere")

    fig, assi = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    pannello(assi[0], aut, "Autrici (% dei volumi con genere noto)")
    pannello(assi[1], cur, "Curatrici e traduttrici (% dei crediti)")
    assi[0].set_ylabel("% di donne", color=INCHIOSTRO_SOFT)
    fig.suptitle("Biblioteca Adelphi: presenza femminile per decennio", x=0.01, ha="left",
                 color=INCHIOSTRO, fontsize=14)
    fig.tight_layout()
    fig.savefig("presenza_femminile.png", dpi=150, facecolor="white")

    na, da = aut["noti"].sum(), aut["donne"].sum()
    nc, dc = cur["noti"].sum(), cur["donne"].sum()
    print(f"Autrici: {da} su {na} ({da / na * 100:.1f}%)")
    print(f"Curatrici e traduttrici: {dc} su {nc} ({dc / nc * 100:.1f}%); "
          f"non determinabili: {cr['genere'].isna().sum()} su {len(cr)}")
    print("Salvato: presenza_femminile.png")


if __name__ == "__main__":
    main()
