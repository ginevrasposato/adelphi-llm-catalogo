import pandas as pd
df = pd.read_csv("dataset_completo.csv")
df["ebook"] = df["ebook_disponibile"].astype(bool)
g = df.groupby("autore").agg(
    volumi=("titolo", "count"),
    dal=("anno", "min"),
    al=("anno", "max"),
    genere=("genere_letterario", lambda s: s.mode().iloc[0]),
    ebook=("ebook", "sum"),
).sort_values(["volumi", "autore"], ascending=[False, True])
g = g.drop('Anonimo')
top = g.head(10)
for a, r in top.iterrows():
    print(f"{a} | {r['volumi']} | {r['dal']}-{r['al']} | {r['genere']} | {r['ebook']} su {r['volumi']}")
print()
print("Autori distinti:", len(g))
print("Primi 10 autori: %d volumi su %d (%.0f%%)" % (top["volumi"].sum(), len(df), 100 * top["volumi"].sum() / len(df)))
print("Autori con un solo volume:", (g["volumi"] == 1).sum())
