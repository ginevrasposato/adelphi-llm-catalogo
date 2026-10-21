# Classificare un catalogo editoriale con un LLM: la Biblioteca Adelphi

Progetto finale del corso *Tecnologie dei dati e del linguaggio* (prof. Alfio Ferrara) — Ginevra Sposato, ottobre 2026.

## Domanda di ricerca

Un LLM, partendo dalle descrizioni, può classificare in modo affidabile genere e temi dei volumi di un catalogo editoriale? E cosa mostra il catalogo Adelphi così arricchito?

## Ipotesi

- **H1** — I temi assegnati dal modello sono più affidabili del genere.
- **H2** — Le donne sono molto meno presenti come autrici che come curatrici e traduttrici.
- **H3** — La distanza tra la nascita dell'autore e l'edizione cresce nel tempo.

H1 è legata a un'aspettativa precedente ai dati. **H2 e H3 sono esplorative**: le ho formulate dopo aver visto i grafici.

## Risultati in breve

| | Risultato | Verdetto |
|---|---|---|
| Genere: il modello è affidabile? | 78% di accordo con la mia annotazione (47/60), kappa di Cohen 0,76; 73% pesato sulla composizione del catalogo | Abbastanza |
| H1: temi più affidabili del genere | criterio prefissato: 100% contro 79% (McNemar esatto, p = 0,008); criterio severo: 82% contro 79% | Confermata, fragile |
| H2: poche autrici, molte curatrici e traduttrici | 9,2% autrici (64/694 volumi) contro 53,3% dei crediti; differenza 44 punti (IC 95% 40–48); per persone distinte 10% contro 48% | Confermata (esplorativa) |
| H3: la distanza dall'autore cresce | +7,1 anni a decennio (IC 95% 5,4–8,9), Spearman 0,46 (IC 95% 0,40–0,52), 658 libri | Confermata, moderata (esplorativa) |

Osservazione aggiuntiva, non parte di H2: i libri di autrici sono curati e tradotti da donne nel 78% dei crediti (52/67), contro il 51% dei libri di autori (314/612); test esatto di Fisher, p = 3·10⁻⁵ (`test_chi_traduce_chi.py`).

## Dati

- **792 volumi** della Biblioteca Adelphi (1965–2026), raccolti con scraping dal sito adelphi.it (`scraper_adelphi.py`, `scraper_descrizioni.py`).
- **275 autori** arricchiti con informazioni biografiche da Wikipedia (`arricchisci_autori.py`): genere, nazionalità, date e luoghi di nascita e morte. Il genere di curatori e traduttori è dedotto dal nome.
- Dati mancanti: genere dell'autore noto per 694 volumi su 792; anno di edizione e data di nascita per 658; dati biografici da Wikipedia per 199 autori su 275 (quelli con una voce).
- Gli errori trovati nei dati (età, nazionalità, genere di alcuni autori) sono stati corretti con gli script nella cartella `archivio/`. I file `autori_arricchiti_vecchio.json` e `cache_prima.json` conservano lo stato precedente alle correzioni.
- **Le descrizioni dei volumi (`descrizioni_adelphi.csv`) non sono incluse**, perché sono testi dell'editore. Per ricostruirle si usa `scraper_descrizioni.py`. Sono escluse, per lo stesso motivo, le pagine di annotazione che le contengono (`annotazione.html`, `revisione.html`, `temi.html`, `campione_da_annotare.csv`): si rigenerano con gli script `crea_*`.

## Classificazione con il modello

Script: `classifica_libri.py`. Schema: `schema_classificazione.png`.

- **Modello:** `claude-haiku-5-5`, tramite API Anthropic. Nessuno strumento, nessuna ricerca esterna.
- **Input per ogni volume:** autore, titolo, descrizione breve. Stesso prompt di sistema per tutti i volumi.
- **Output (JSON):** `genere` scelto da una **lista chiusa di 11** (romanzo, racconti, poesia, teatro, saggio, biografia/memorie, filosofia, religione/spiritualità, storia, scienze, altro); `temi` (da 2 a 4, specifici del contenuto); `affidabilita` (alta, media, bassa). Una scheda con genere fuori lista è scartata.
- **Impostazioni:** `max_tokens` 2000; temperatura non impostata (valore predefinito); nessun seed. Una nuova esecuzione può dare risultati leggermente diversi: **l'artefatto riproducibile sono le risposte salvate** in `schede_qualitative.json`.

## Validazione

### Genere (60 libri)

1. `crea_campione.py`: campione stratificato per genere (fino a 5 volumi per genere, il resto casuale, seed 42).
2. Annotazione **alla cieca** con una pagina HTML (`annotazione_modello.html` → `crea_pagina.py`): le etichette del modello sono nascoste (`campione_nascosto.csv`); le mie in `campione_annotato.csv`.
3. `valuta_genere.py`: primo confronto, 45% (l'unico valore pienamente indipendente).
4. Revisione dei disaccordi (`revisione_modello.html` → `crea_revisione.py`, seed 7): per ogni disaccordo scelgo tra due etichette (A/B) in ordine casuale. Risultato in `campione_rivisto.csv`.
5. `valuta_finale.py`: accordo 78% (47/60), kappa 0,76, accuratezza pesata sul catalogo 73%, matrice di confusione (`matrice_confusione.png`), errori in `errori_finali.csv`.

### Temi (38 libri verificati su 60)

1. `crea_pagina_temi.py` (seed 11): per ogni libro i temi del modello più **un tema-esca** preso da un altro libro, per misurare la tendenza ad approvare tutto.
2. Giudizio di pertinenza di ogni tema (`temi_giudicati.csv`). Per 22 libri non sono riuscita a verificare con certezza e li ho esclusi (`temi_non_verificati.txt`).
3. `valuta_temi.py`: 94% dei temi pertinenti; esche accettate come pertinenti 18%.
4. Criterio **fissato prima di vedere i risultati**: scheda adeguata se almeno metà dei temi è pertinente (100% contro 79% del genere, McNemar esatto p = 0,008). Il criterio non distingue (effetto soffitto), quindi ho aggiunto in seguito un'**analisi di sensibilità** (≥ 75%: 84%; tutti i temi: 82%) senza sostituire il risultato originale.

## Analisi delle ipotesi

- `ipotesi_h2.py` (usa `analisi_donne.py`): confronto tra percentuali, intervalli di Wilson e di Newcombe, controllo per persone distinte.
- `ipotesi_h3.py`: pendenza della regressione e correlazione di Spearman con bootstrap (5000 ricampionamenti, seed 42).
- Altre analisi esplorative non presentate al colloquio: `analisi_*.py`, epoche, decenni, formati, mappe, percorso al femminile.

## Prodotti consultabili

- `catalogo_adelphi.html`: catalogo con ricerca per autore, titolo, genere e tema (generato da `percorso_catalogo.py` con i modelli `parte1.html` e `parte2.html`).
- `percorso_autrici.html`: i volumi delle autrici, generato da `percorso_autrici.py`.
- `report.html` (`componi_report.py`), `mappa_nascite.html` (`mappa_nascite.py`).

## Per riprodurre

1. Python 3 e le librerie importate in testa agli script (principalmente `pandas`, `matplotlib`, `anthropic`).
2. Raccolta e pulizia: `scraper_adelphi.py`, `scraper_descrizioni.py`, `pulisci_dati.py`, `arricchisci_autori.py`, `unisci_dati.py` (produce `dataset_completo.csv`/`.json`).
3. Classificazione: `classifica_libri.py` (richiede la variabile d'ambiente `ANTHROPIC_API_KEY`). Non serve rilanciarla: le risposte sono già in `schede_qualitative.json`.
4. Validazione e analisi: gli script indicati nelle sezioni precedenti, nell'ordine in cui compaiono.

## Limiti

- Il modello vede solo autore, titolo e descrizione breve: con un testo più ricco i temi potrebbero diventare più specifici.
- 22 libri su 60 non sono stati verificabili per i temi: forse sono proprio i casi più difficili.
- Il 18% dei temi-esca è stato accettato come pertinente: "pertinente" non vuol dire "specifico", e il 94% è un limite superiore.
- La soglia severa per H1 è stata aggiunta dopo aver visto i risultati.
- H2 e H3 sono esplorative.
- Il genere di curatori e traduttori è dedotto dal nome.
- Dati mancanti (vedi sezione Dati).
- Nessun autore nato dopo il 1945 ha dati biografici: i contemporanei sono sotto-rappresentati. Per H3 significa che nei decenni recenti la distanza è calcolata solo su autori nati fino al 1945, e questo potrebbe sovrastimare la crescita.
- Genere e temi sono una classificazione automatica sperimentale.

## Uso dell'IA

Il codice è stato scritto con il supporto di un modello linguistico (Claude), come consentito dalle linee guida del corso. Le scelte di progetto sono mie: la domanda di ricerca, il campione e le procedure di validazione, i criteri (compresi i limiti dichiarati) e la lettura dei risultati. Il modello `claude-haiku-5-5` è anche l'oggetto dello studio.

## Fonti

- Catalogo e descrizioni: adelphi.it.
- Informazioni biografiche sugli autori: Wikipedia (licenza CC BY-SA); luoghi di nascita geocodificati con Nominatim (OpenStreetMap).