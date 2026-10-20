import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()

nuova_posizione = '''ANCORA_BIO = re.compile(
    r"\\bè\\s+(?:(stato|uno|un)(?![a-zàèéìòù'’])|(stata|una)(?![a-zàèéìòù])|(un['’]))",
    re.IGNORECASE,
)


def trova_posizione_bio(testo):
    """Trova la frase 'X è stato/a ...' (persone morte) o 'X è un/una/uno ...' (viventi)."""
    match = ANCORA_BIO.search(testo)
    if not match:
        return None, None
    genere = "M" if match.group(1) else "F"
    return match.start(), genere


'''
nuova_nazionalita = '''def estrai_nazionalita(testo, posizione_bio):
    finestra = testo[posizione_bio:posizione_bio + 300]
    frase_match = re.search(r"è\\s+(?:stat[oa]|uno|una|un['’]|un)\\b(.*?)\\.", finestra, re.IGNORECASE)
    if not frase_match:
        return None
    parole = re.findall(r"[A-Za-zàèéìòù]+", frase_match.group(1))
    return parole[-1].capitalize() if parole else None


'''
s, n1 = re.subn(r"def trova_posizione_bio\(testo\):.*?(?=def estrai_nazionalita)", lambda m: nuova_posizione, s, flags=re.S)
s, n2 = re.subn(r"def estrai_nazionalita\(testo, posizione_bio\):.*?(?=MESI_ITALIANI = \{)", lambda m: nuova_nazionalita, s, flags=re.S)
n3 = s.count(r"(\d{1,2})\s+(\w+)\s+(\d{4})")
s = s.replace(r"(\d{1,2})\s+(\w+)\s+(\d{4})", r"(\d{1,2})[º°]?\s+(\w+)\s+(\d{4})")
open(p, "w", encoding="utf-8").write(s)
print("sostituzioni:", n1, n2, "date:", n3)
