import csv
import json
import pandas as pd
import matplotlib.pyplot as plt

CSV_LIBRI = "biblioteca_adelphi_pulito.csv"
JSON_AUTORI = "autori_arricchiti.json"
OUTPUT_MERGE = "biblioteca_adelphi_arricchito.json"


def carica_e_unisci():
    with open(CSV_LIBRI, encoding="utf-8") as f:
        libri = list(csv.DictReader(f))
    with open(JSON_AUTORI, encoding="utf-8") as f:
        autori = json.load(f)
    for libro in libri:
        bio = autori.get(libro["autore"], {})
        libro["genere_autore"] = bio.get("genere")
        libro["anno_nascita_autore"] = (bio.get("data_nascita") or "")[:4] or None
        libro["nazionalita_autore"] = bio.get("nazionalita")
    with open(OUTPUT_MERGE, "w", encoding="utf-8") as f:
        json.dump(libri, f, ensure_ascii=False, indent=2)
    return libri


def tutorial1_decenni(df):
    df["decennio"] = (df["anno"].astype(int) // 10) * 10
    conteggi = df["decennio"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(conteggi.index.astype(str), conteggi.values)
    ax.set_title("Biblioteca Adelphi: libri pubblicati per decennio")
    ax.set_xlabel("Decennio")
    ax.set_ylabel("Numero di libri")
    plt.xticks(rotation=45)
    fig.tight_layout()
    fig.savefig("decenni.png", dpi=150)
    print(f"[1] decenni.png salvato — decennio con più libri: {conteggi.idxmax()} ({conteggi.max()} libri)")


def tutorial2_eta(df):
    df_eta = df[df["anno_nascita_autore"].notna()].copy()
    df_eta["anno_nascita_autore"] = df_eta["anno_nascita_autore"].astype(int)
    df_eta["eta"] = df_eta["anno"].astype(int) - df_eta["anno_nascita_autore"]
    df_eta = df_eta[df_eta["eta"] > 0]
    media_decennio = df_eta.groupby("decennio")["eta"].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    media_decennio.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Anni dalla nascita dell'autore all'edizione, media per decennio")
    ax.set_xlabel("Decennio")
    ax.set_ylabel("Anni dalla nascita (media)")
    fig.tight_layout()
    ax.set_ylim(0, 150)
    fig.savefig("eta_per_decennio.png", dpi=150)
    print(f"[2] eta_per_decennio.png salvato — su {len(df_eta)} libri con eta' calcolabile")


def tutorial3_genere(df):
    df_g = df[df["genere_autore"].isin(["M", "F"])].copy()
    totali = df_g["genere_autore"].value_counts()
    print(f"[3] Totali autori: M={totali.get('M', 0)}, F={totali.get('F', 0)}")
    pct_f = df_g.groupby("decennio")["genere_autore"].apply(lambda s: (s == "F").mean() * 100)
    fig, ax = plt.subplots(figsize=(10, 5))
    pct_f.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Percentuale di autrici donne per decennio (Biblioteca Adelphi)")
    ax.set_xlabel("Decennio")
    ax.set_ylabel("Percentuale femminile (%)")
    ax.set_ylim(0, 100)
    ax.axhline(50, color="gray", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig("genere_per_decennio.png", dpi=150)
    print("genere_per_decennio.png salvato")


def main():
    libri = carica_e_unisci()
    print(f"Uniti {len(libri)} libri con i dati biografici degli autori\n")
    df = pd.DataFrame(libri)
    df = df[df["anno"].notna() & (df["anno"] != "")]
    tutorial1_decenni(df)
    tutorial2_eta(df)
    tutorial3_genere(df)


if __name__ == "__main__":
    main()
