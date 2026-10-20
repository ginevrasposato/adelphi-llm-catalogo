import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

a = pd.read_csv("campione_annotato.csv")
n = pd.read_csv("campione_nascosto.csv")
d = pd.read_csv("dataset_completo.csv")
m = a.merge(n, on="numero_collana").merge(d[["numero_collana", "autore", "titolo"]], on="numero_collana")
m = m.rename(columns={"genere_letterario": "genere_llm"})
print("Senza annotazione:", m["genere_tuo"].isna().sum())
m["ok"] = m["genere_tuo"] == m["genere_llm"]

# accuratezza grezza + intervallo di Wilson al 95%
N = len(m); p = m["ok"].mean(); z = 1.96
centro = (p + z**2 / (2 * N)) / (1 + z**2 / N)
meta = z * ((p * (1 - p) / N + z**2 / (4 * N**2)) ** 0.5) / (1 + z**2 / N)
print(f"\nAccuratezza grezza: {p:.0%} ({m['ok'].sum()}/{N}), IC95% {centro-meta:.0%}-{centro+meta:.0%}")

# precisione per genere dell'LLM e accuratezza pesata sul catalogo
prec = m.groupby("genere_llm")["ok"].agg(["sum", "count"])
prec["precisione"] = prec["sum"] / prec["count"]
peso = d["genere_letterario"].value_counts()
peso = (peso / peso.sum()).reindex(prec.index)
prec["peso_catalogo"] = peso
print(f"Accuratezza pesata sul catalogo: {(peso * prec['precisione']).sum():.0%}")
print("\nPrecisione per genere:\n", prec.round(2))
prec.to_csv("metriche_per_genere.csv")

# kappa di Cohen
gen = sorted(set(m["genere_tuo"]) | set(m["genere_llm"]))
ct = pd.crosstab(m["genere_tuo"], m["genere_llm"]).reindex(index=gen, columns=gen, fill_value=0)
po = ct.values.trace() / N
pe = (ct.sum(axis=1).values * ct.sum(axis=0).values).sum() / N**2
print(f"\nKappa di Cohen: {(po - pe) / (1 - pe):.2f}")

# errori
err = m[~m["ok"]][["numero_collana", "autore", "titolo", "genere_llm", "genere_tuo"]]
err.to_csv("errori_validazione.csv", index=False)
print("\nErrori:\n", err.to_string(index=False))

# matrice di confusione
fig, ax = plt.subplots(figsize=(8, 7))
ax.imshow(ct.values, cmap="Blues")
ax.set_xticks(range(len(gen))); ax.set_xticklabels(gen, rotation=60, ha="right")
ax.set_yticks(range(len(gen))); ax.set_yticklabels(gen)
for i in range(len(gen)):
    for j in range(len(gen)):
        if ct.values[i, j]:
            ax.text(j, i, ct.values[i, j], ha="center", va="center")
ax.set_xlabel("Genere assegnato dall'LLM"); ax.set_ylabel("Genere assegnato da me")
ax.set_title("Matrice di confusione (60 libri)")
plt.tight_layout(); plt.savefig("matrice_confusione.png", dpi=150)
