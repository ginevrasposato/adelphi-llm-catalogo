import pandas as pd
df = pd.read_csv("dataset_completo.csv")
print("Totale libri:", len(df))
for c in ["anno", "data_nascita_autore", "genere_autore", "genere_letterario", "ebook_disponibile"]:
    print(c, "->", df[c].notna().sum(), "con dato")
print()
print(df["genere_autore"].value_counts(dropna=False))
print()
print(df["ebook_disponibile"].value_counts(dropna=False))
