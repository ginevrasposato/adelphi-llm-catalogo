from math import comb, sqrt, erfc

# crediti di curatrici/traduttrici (donne, uomini) per genere dell'autore
a, b = 52, 15     # libri di autrici
c, d = 314, 298   # libri di autori

n1, n2 = a + b, c + d
donne = a + c
N = n1 + n2
tot = comb(N, donne)

def prob(k):
    return comb(n1, k) * comb(n2, donne - k) / tot

p_oss = prob(a)
lo, hi = max(0, donne - n2), min(n1, donne)
p_fisher = sum(prob(k) for k in range(lo, hi + 1) if prob(k) <= p_oss * (1 + 1e-9))

p1, p2 = a / n1, c / n2
pp = donne / N
z = (p1 - p2) / sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
p_z = erfc(abs(z) / sqrt(2))

print(f"Libri di autrici: {a}/{n1} = {p1:.1%} donne")
print(f"Libri di autori:  {c}/{n2} = {p2:.1%} donne")
print(f"Fisher esatto, due code: p = {p_fisher:.2e}")
print(f"Controllo z-test:        p = {p_z:.2e}")
