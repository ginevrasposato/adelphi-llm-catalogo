import html
import json
from pathlib import Path

libri = json.loads(Path("dataset_completo.json").read_text(encoding="utf-8"))
donne = [l for l in libri if l.get("genere_autore") == "F"]
donne.sort(key=lambda l: (l["autore"].split()[-1], int(l["anno"] or 0)))

righe = []
for l in donne:
    eb = "sì" if str(l.get("ebook_disponibile")).lower() in ("true", "1") else "no"
    righe.append(
        f"<tr><td>{html.escape(l['autore'])}</td>"
        f"<td><a href=\"{html.escape(l['url_libro'])}\" target=\"_blank\">{html.escape(l['titolo'])}</a></td>"
        f"<td>{html.escape(l.get('genere_letterario') or '')}</td>"
        f"<td>{html.escape(str(l['anno']))}</td><td>{eb}</td></tr>")

pagina = f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<title>Percorso al femminile</title><style>
body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#222}}
h1{{color:#d55181}} table{{border-collapse:collapse;width:100%}}
th{{background:#d55181;color:#fff;text-align:left;padding:.5rem}}
td{{padding:.45rem;border-bottom:1px solid #f2c4d4}} tr:hover{{background:#fdf0f5}}
a{{color:#b03a68}}</style></head><body>
<h1>Percorso al femminile nella Biblioteca Adelphi</h1>
<p>{len({l['autore'] for l in donne})} autrici, {len(donne)} volumi. Clicca sul titolo per aprire la scheda su adelphi.it.</p>
<table><tr><th>Autrice</th><th>Titolo</th><th>Genere</th><th>Anno</th><th>eBook</th></tr>
{''.join(righe)}</table></body></html>"""
Path("percorso_autrici.html").write_text(pagina, encoding="utf-8")
print(f"Salvato: percorso_autrici.html ({len(donne)} volumi)")
