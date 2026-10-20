import pandas as pd
df = pd.read_csv("dataset_completo.csv")
a = df.drop_duplicates("autore")
print("Autori distinti:", len(a))
print("Con luogo di nascita:", a["luogo_nascita_autore"].notna().sum())
print()
print(a["nazionalita_autore"].value_counts().head(8))
print()
print(a["luogo_nascita_autore"].value_counts().head(8))
