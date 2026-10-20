import numpy as np
import pandas as pd

d = pd.read_csv("dataset_completo.csv")
d["anno"] = pd.to_numeric(d["anno"], errors="coerce")
d["nascita"] = pd.to_numeric(d["data_nascita_autore"].astype(str).str.extract(r"^(\d{4})")[0], errors="coerce")
d["distanza"] = d["anno"] - d["nascita"]
s = d.dropna(subset=["anno", "nascita"])
n = len(s)
print(f"Libri con anno e data di nascita: {n} su {len(d)}")
print(f"Distanza minima e massima: {s['distanza'].min():.0f} - {s['distanza'].max():.0f} anni")

a = s["anno"].to_numpy()
b = s["distanza"].to_numpy()
pend = np.polyfit(a, b, 1)[0] * 10
rho = np.corrcoef(pd.Series(a).rank(), pd.Series(b).rank())[0, 1]

rng = np.random.default_rng(42)
pends, rhos = [], []
for _ in range(5000):
    i = rng.integers(0, n, n)
    pends.append(np.polyfit(a[i], b[i], 1)[0] * 10)
    rhos.append(np.corrcoef(pd.Series(a[i]).rank(), pd.Series(b[i]).rank())[0, 1])

print(f"\nPendenza: +{pend:.1f} anni di distanza ogni 10 anni di calendario, IC95% {np.percentile(pends, 2.5):.1f} / {np.percentile(pends, 97.5):.1f}")
print(f"Correlazione di Spearman: {rho:.2f}, IC95% {np.percentile(rhos, 2.5):.2f} / {np.percentile(rhos, 97.5):.2f}")
