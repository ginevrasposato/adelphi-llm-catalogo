import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()

nuova_posizione = '''def trova_posizione_bio(testo):
    """Trova la frase di presentazione dell'autore (es. X è stato/a ..., X è un/una ...).
    Salta gli avvisi di Wikipedia ('Questa voce ...') e preferisce la frase
    preceduta da una data (anno di 4 cifre)."""
    candidati = []
    for m in ANCORA_BIO.finditer(testo[:6000]):
        if "Questa voce" in testo[max(0, m.start() - 120):m.start()]:
            continue
        candidati.append(m)
    if not candidati:
        return None, None
    con_data = [m for m in candidati
                if re.search(r"\\d{4}", testo[max(0, m.start() - 400):m.start()])]
    m = (con_data or candidati)[0]
    genere = "M" if m.group(1) else "F"
    return m.start(), genere


'''

nuova_nascita = '''def estrai_nascita_morte(testo, posizione_bio):
    testo = testo[max(0, posizione_bio - 300):posizione_bio]
    data = r"(\\d{1,2})[º°]?\\s+(\\w+)\\s+(\\d{4})"
    pattern_completo = re.search(
        r"(?:\\(|;)\\s*([^,;()]+?)\\s*,\\s*" + data + r"\\s*[–\\-]\\s*"
        r"([^,;()]+?)\\s*,\\s*" + data + r"\\s*\\)",
        testo,
    )
    if pattern_completo:
        luogo_n, g_n, m_n, a_n, luogo_m, g_m, m_m, a_m = pattern_completo.groups()
        return (
            data_italiana_a_iso(g_n, m_n, a_n), luogo_n.strip(),
            data_italiana_a_iso(g_m, m_m, a_m), luogo_m.strip(),
        )
    pattern_solo_nascita = re.search(
        r"(?:\\(|;)\\s*([^,;()]+?)\\s*,\\s*" + data + r"\\s*\\)", testo
    )
    if pattern_solo_nascita:
        luogo_n, g_n, m_n, a_n = pattern_solo_nascita.groups()
        return data_italiana_a_iso(g_n, m_n, a_n), luogo_n.strip(), None, None
    return None, None, None, None


'''

s, n1 = re.subn(r"def trova_posizione_bio\(testo\):.*?(?=def estrai_nazionalita)", lambda m: nuova_posizione, s, flags=re.S)
s, n2 = re.subn(r"def estrai_nascita_morte\(testo, posizione_bio\):.*?(?=def contenuto_articolo)", lambda m: nuova_nascita, s, flags=re.S)
open(p, "w", encoding="utf-8").write(s)
print("sostituzioni:", n1, n2)
