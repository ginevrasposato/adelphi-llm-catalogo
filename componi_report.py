import json
from collections import Counter
from pathlib import Path

from analisi_donne import genere_dal_nome, persone

INPUT = "dataset_completo.json"
OUTPUT = "report.html"

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       max-width: 800px; margin: 2em auto; padding: 0 1em; line-height: 1.6; color: #222; }
h1 { color: #b03a68; }
h2 { color: #b03a68; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; margin-top: 2em; }
img { max-width: 100%; border: 1px solid #ccc; margin: 1em 0; }
.didascalia { font-size: 0.9em; color: #555; margin-top: -0.5em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ccc; padding: 0.5em; text-align: left; }
th { background: #fbe9f0; }
a { color: #b03a68; }
.limiti li { margin-bottom: 0.4em; }
"""


def calcola_numeri(libri):
    autori = {l["autore"] for l in libri}
    ebook = sum(1 for l in libri if str(l.get("ebook_disponibile")).lower() in ("true", "1"))
    gen = [l["genere_autore"] for l in libri if l.get("genere_autore") in ("M", "F")]
    donne = sum(1 for g in gen if g == "F")
    autrici = {l["autore"] for l in libri if l.get("genere_autore") == "F"}
    crediti = [genere_dal_nome(n) for l in libri for n in persone(l.get("curatore"))]
    crediti = [g for g in crediti if g]
    citta = Counter(
        l["luogo_nascita_autore"].split(";")[-1].strip()
        for l in libri if l.get("luogo_nascita_autore"))
    top = citta.most_common(1)[0]
    anni = [int(l["anno"]) for l in libri if str(l.get("anno", "")).isdigit()]
    return {
        "Volumi nel catalogo": len(libri),
        "Periodo (anno dell'edizione Adelphi)": f"{min(anni)}-{max(anni)}",
        "Autori distinti": len(autori),
        "Volumi anche in eBook": f"{ebook} ({ebook / len(libri) * 100:.0f}%)",
        "Volumi di autrici (genere noto)": f"{donne} su {len(gen)} ({donne / len(gen) * 100:.1f}%)",
        "Autrici distinte": len(autrici),
        "Curatrici e traduttrici (crediti classificati)":
            f"{sum(1 for g in crediti if g == 'F')} su {len(crediti)} "
            f"({sum(1 for g in crediti if g == 'F') / len(crediti) * 100:.0f}%)",
        "Città di nascita più rappresentata": f"{top[0]} ({top[1]} volumi)",
        "Schede qualitative (LLM)": sum(1 for l in libri if l.get("genere_letterario")),
    }


def riga(k, v):
    return f"<tr><th>{k}</th><td>{v}</td></tr>"


def blocco_grafici(lista):
    out = []
    for src, did in lista:
        if not Path(src).exists():
            print(f"  attenzione: manca {src}")
        out.append(f'<img src="{src}" alt="{did}">\n<p class="didascalia">{did}</p>')
    return "\n".join(out)


def main():
    libri = json.loads(Path(INPUT).read_text(encoding="utf-8"))
    righe = "\n".join(riga(k, v) for k, v in calcola_numeri(libri).items())

    grafici = blocco_grafici([
        ("generi.png", "Generi letterari più rappresentati (etichette prodotte dal modello)."),
        ("generi_per_decennio.png", "Generi letterari per decennio di edizione."),
        ("classici_contemporanei.png", "Epoca di nascita degli autori: classici e contemporanei."),
        ("formati.png", "Volumi disponibili anche in eBook, secondo l'edizione Adelphi."),
    ])
    donne = blocco_grafici([
        ("presenza_femminile.png", "Presenza femminile per decennio: autrici e curatrici/traduttrici."),
        ("autrici_epoche.png", "Quota di autrici per epoca di nascita (autori distinti)."),
        ("generi_donne.png", "Generi letterari: autrici e autori a confronto."),
        ("chi_traduce_chi.png", "Chi traduce e cura: le autrici sono affidate più spesso a traduttrici."),
    ])

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>Biblioteca Adelphi: un piccolo dossier</title>
<style>{CSS}</style>
</head>
<body>

<h1>Alla ricerca del libro perduto</h1>
<p><em>Interrogare un catalogo, analizzarne la biblioteca ed esplorare il mondo Adelphi
con modelli generativi.</em></p>
<p>Questa pagina raccoglie le analisi sulla Biblioteca Adelphi. I dati sono stati raccolti
da adelphi.it con uno scraping automatico e arricchiti con Wikipedia (biografie degli autori)
e con un modello linguistico (genere letterario e temi di ogni volume). Lo scopo pratico
è aiutare a orientarsi in un catalogo e a trovare dove procurarsi le opere.</p>

<h2>Numeri</h2>
<table>
{righe}
</table>

<h2>Il catalogo</h2>
{grafici}

<h2>La presenza femminile</h2>
<p>Le donne sono poche tra chi scrive, ma più della metà tra chi traduce e cura. Tra gli autori
nati più tardi la quota di donne cresce, ma il catalogo Adelphi, guardando agli anni di
pubblicazione, non registra questa crescita: Adelphi attinge molto ai classici consacrati,
in maggioranza uomini (è un'ipotesi, non un risultato).</p>
{donne}

<h2>Mappe</h2>
<ul>
<li><a href="mappa_nascite.html" target="_blank">Luoghi di nascita degli autori</a> (mappa interattiva)</li>
<li><a href="mappa_autrici.html" target="_blank">Luoghi di nascita delle autrici</a> (mappa interattiva)</li>
</ul>

<h2>Percorso al femminile</h2>
<p>Elenco di tutti i volumi di autrici, con link alla scheda su adelphi.it:
<a href="percorso_autrici.html" target="_blank">percorso_autrici.html</a>.</p>

<h2>Metodo e limiti</h2>
<ul class="limiti">
<li>Genere e luogo di nascita degli autori vengono da Wikipedia: gli autori senza voce sono esclusi
(199 autori su 275 hanno dati biografici).</li>
<li>Genere letterario e temi sono prodotti da un modello linguistico; in un controllo a campione
il genere coincide con la mia annotazione nel 78% dei casi (47 libri su 60) e il 94% dei temi verificati è pertinente (38 libri).</li>
<li>Il genere dei curatori è dedotto dal nome di battesimo, in modo binario; 26 crediti su 810
non sono classificabili.</li>
<li>L'anno è quello dell'edizione Adelphi, non della prima pubblicazione dell'opera.</li>
<li>La disponibilità eBook riflette l'edizione Adelphi al momento della raccolta (ottobre 2026).</li>
<li>Nessun autore nato dopo il 1945 ha dati biografici: i contemporanei sono sotto-rappresentati.</li>
<li>Numeri piccoli (per esempio 79 volumi di autrici) rendono incerte le differenze di pochi punti.</li>
</ul>

<hr>
<p style="font-size: 0.85em; color: #777;">
Generato automaticamente dallo script <code>componi_report.py</code>.
I dati sono stati raccolti per finalità didattiche e potrebbero contenere imprecisioni.
La verifica e l'interpretazione dei risultati restano responsabilità del lettore.
</p>

</body>
</html>"""
    Path(OUTPUT).write_text(html, encoding="utf-8")
    print(f"Report salvato in {OUTPUT}")


if __name__ == "__main__":
    main()
