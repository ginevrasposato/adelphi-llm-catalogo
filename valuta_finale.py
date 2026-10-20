import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

a = pd.read_csv("campione_annotato.csv")
n = pd.read_csv("campione_nascosto.csv")[["numero_collana", "genere_letterario"]]
d = pd.read_csv("dataset_completo.csv")[["numero_collana", "autore", "titolo"]]
r = pd.read_csv("campione_rivisto.csv")
m = a.merge(n, on="numero_collana").merge(d, on="numero_collana").merge(r, on="numero_collana", how="left")
m = m.rename(columns={"genere_letterario": "genere_llm"})
m["finale"] = m["genere_finale"].fillna(m["genere_tuo"])
N = len(m)

def wilson(p, N, z=1.96):
    c = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    h = z * ((p * (1 - p) / N + z**2 / (4 * N**2)) ** 0.5) / (1 + z**2 / N)
    return c - h, c + h

# 1) confronto tra primo giro e dopo la revisione
ok1 = (m["genere_tuo"] == m["genere_llm"])
ok2 = (m["finale"] == m["genere_llm"])
for nome, ok in [("PRIMO GIRO (cieco)", ok1), ("DOPO LA REVISIONE", ok2)]:
    p = ok.mean(); lo, hi = wilson(p, N)
    print(f"{nome}: {p:.0%} ({ok.sum()}/{N}), IC95% {lo:.0%}-{hi:.0%}")

# 2) come si sono risolti i disaccordi
dis = m[~ok1]
print(f"\nDisaccordi: {len(dis)}  (senza decisione: {dis['genere_finale'].isna().sum()})")
print("  ragione l'LLM      :", (dis["finale"] == dis["genere_llm"]).sum())
print("  ragione la prima annotazione:", (dis["finale"] == dis["genere_tuo"]).sum())
print("  nessuno dei due    :", ((dis["finale"] != dis["genere_llm"]) & (dis["finale"] != dis["genere_tuo"])).sum())

# 3) precisione per genere e accuratezza pesata (dopo la revisione)
m["ok"] = ok2
prec = m.groupby("genere_llm")["ok"].agg(["sum", "count"])
prec["precisione"] = prec["sum"] / prec["count"]
cat = pd.read_csv("dataset_completo.csv")["genere_letterario"].value_counts()
prec["peso_catalogo"] = (cat / cat.sum()).reindex(prec.index)
print(f"\nAccuratezza pesata sul catalogo: {(prec['peso_catalogo'] * prec['precisione']).sum():.0%}")
print(prec.round(2))
prec.to_csv("metriche_per_genere_finali.csv")

# 4) kappa di Cohen
gen = sorted(set(m["finale"]) | set(m["genere_llm"]))
ct = pd.crosstab(m["finale"], m["genere_llm"]).reindex(index=gen, columns=gen, fill_value=0)
po = ct.values.trace() / N
pe = (ct.sum(axis=1).values * ct.sum(axis=0).values).sum() / N**2
print(f"\nKappa di Cohen: {(po - pe) / (1 - pe):.2f}")

# 5) errori rimasti
err = m[~ok2][["numero_collana", "autore", "titolo", "genere_llm", "finale"]]
err.to_csv("errori_finali.csv", index=False)
print("\nErrori rimasti:\n", err.to_string(index=False))

# 6) matrice di confusione
fig, ax = plt.subplots(figsize=(8, 7))
ax.imshow(ct.values, cmap="Blues")
ax.set_xticks(range(len(gen))); ax.set_xticklabels(gen, rotation=60, ha="right")
ax.set_yticks(range(len(gen))); ax.set_yticklabels(gen)
for i in range(len(gen)):
    for j in range(len(gen)):
        if ct.values[i, j]:
            ax.text(j, i, ct.values[i, j], ha="center", va="center")
ax.set_xlabel("Genere assegnato dall'LLM"); ax.set_ylabel("Genere di riferimento (dopo revisione)")
ax.set_title("Matrice di confusione dopo la revisione (60 libri)")
plt.tight_layout(); plt.savefig("matrice_confusione_finale.png", dpi=150)
