import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("dataset_completo.csv")
df["anno"] = df["anno"].astype(int)
df["decennio"] = (df["anno"] // 10) * 10
df["ebook"] = df["ebook_disponibile"].astype(bool)

print("Totale libri:", len(df))
print("Con eBook:", df["ebook"].sum(), "| Senza:", (~df["ebook"]).sum())
print("Percentuale con eBook: %.1f%%" % (100 * df["ebook"].mean()))
print()

t = df.groupby("decennio")["ebook"].agg(["count", "sum"])
t["perc"] = 100 * t["sum"] / t["count"]
t.columns = ["libri", "con_ebook", "perc"]
print(t.round(1).to_string())

fig, ax = plt.subplots(figsize=(10, 5))
barre = ax.bar([str(d) for d in t.index], t["perc"], color="#1f77b4")
for b, (d, r) in zip(barre, t.iterrows()):
    ax.text(b.get_x() + b.get_width() / 2, r["perc"] + 1.5,
            "%.0f%%\n(%d su %d)" % (r["perc"], r["con_ebook"], r["libri"]),
            ha="center", va="bottom", fontsize=9)
ax.set_ylim(0, 110)
ax.set_ylabel("% di libri con edizione eBook Adelphi")
ax.set_xlabel("Decennio di pubblicazione")
ax.set_title("Libri con edizione eBook Adelphi, per decennio")
fig.tight_layout()
fig.savefig("formati_decenni.png", dpi=150)
print()
print("Grafico salvato: formati_decenni.png")
