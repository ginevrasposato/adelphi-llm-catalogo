import pandas as pd, json
uomini = ["Apollodoro", "Artemidoro", "Filostrato", "Fozio", "Igino",
          "Kenko", "Robert Kirk", "Nonno di Panopoli", "Sto", "Palinuro"]
df = pd.read_csv("dataset_completo.csv")
df.loc[df["autore"].isin(uomini), "genere_autore"] = "M"
df.to_csv("dataset_completo.csv", index=False)
righe = json.load(open("dataset_completo.json", encoding="utf-8"))
for r in righe:
    if r["autore"] in uomini:
        r["genere_autore"] = "M"
json.dump(righe, open("dataset_completo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
f = df[df["genere_autore"] == "F"]
print("Volumi di autrici:", len(f), "| autrici distinte:", f["autore"].nunique())
