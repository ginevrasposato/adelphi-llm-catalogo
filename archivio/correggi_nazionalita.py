import pandas as pd, json
corr = {
 "Jorge Luis Borges": "Argentino",
 "Alexander Lernet-Holenia": "Austriaco",
 "Anton Čechov": "Russo",
 "Louis Ginzberg": "Statunitense",
 "Alexander Pope": "Britannico",
 "Sergio Quinzio": "Italiano",
 "Colette": "Francese",
 "Ludwig Wittgenstein": "Austriaco",
 "John Aubrey": "Britannico",
}
df = pd.read_csv("dataset_completo.csv")
for autore, naz in corr.items():
    df.loc[df["autore"] == autore, "nazionalita_autore"] = naz
df.to_csv("dataset_completo.csv", index=False)
righe = json.load(open("dataset_completo.json", encoding="utf-8"))
for r in righe:
    if r["autore"] in corr:
        r["nazionalita_autore"] = corr[r["autore"]]
json.dump(righe, open("dataset_completo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("Secolo rimasti:", (df["nazionalita_autore"] == "Secolo").sum())
