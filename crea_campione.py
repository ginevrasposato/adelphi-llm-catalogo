import pandas as pd

df = pd.read_csv("dataset_completo.csv")
desc = pd.read_csv("descrizioni_adelphi.csv")[["numero_collana", "descrizione"]]
df = df.dropna(subset=["genere_letterario"])

# 5 libri per ogni genere (o tutti, se ce ne sono meno di 5)
per_genere = pd.concat(
    [g.sample(min(len(g), 5), random_state=42) for _, g in df.groupby("genere_letterario")]
)
# si completa a 60 con libri casuali tra quelli rimasti
resto = df.drop(per_genere.index).sample(60 - len(per_genere), random_state=42)
campione = pd.concat([per_genere, resto]).sort_values("numero_collana")
campione = campione.merge(desc, on="numero_collana", how="left")

# file CIECO: senza etichette dell'LLM
cieco = campione[["numero_collana", "autore", "titolo", "descrizione", "url_libro"]].copy()
cieco["genere_tuo"] = ""
cieco.to_csv("campione_da_annotare.csv", index=False)

# file NASCOSTO: le etichette dell'LLM, da non guardare finché non finisci
campione[["numero_collana", "genere_letterario", "temi", "affidabilita_scheda"]].to_csv(
    "campione_nascosto.csv", index=False
)

# elenco dei generi ammessi
generi = sorted(df["genere_letterario"].unique())
open("generi_ammessi.txt", "w").write("\n".join(generi))

print("Libri nel campione:", len(campione))
print(campione["genere_letterario"].value_counts())
print("\nGeneri ammessi:\n" + "\n".join(generi))
