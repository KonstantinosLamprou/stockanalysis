# Aktienanalyse: Können einfache Modelle den GOOGL-Kurs vertrauenswürdig vorhersagen?

Projekt im Kurs *Projekt: Programmierung mit Python* (Aufgabe 3: Modellbildung).

**Leitfrage:** Können einfache Standardmodelle den Kurs der Google-Aktie (GOOGL) vertrauenswürdig vorhersagen, also besser als eine simple Faustregel?

Verglichen werden Lineare Regression, Random Forest und Gradient Boosting mit drei Regeln (Persistenz-Regel, SMA-Crossover, "Immer steigend").
"Vertrauenswürdig" ist über drei Kriterien definiert (siehe `docs/run-process.md`).

## Schnellstart

```bash
pip install -r requirements.txt
python src/main.py
```

Ergebnisse: `results/` (Kennzahlen, Diagramme, `run_report.md`). Folien: `python presentation/build_deck.py`.

## Inhalt

- [Run-Prozess und Befehle](docs/run-process.md)
- [Architektur](docs/architecture.md)
- [Gliederung der Präsentation](docs/presentation.md)
- Notebook: `notebooks/stock-market-analysis.ipynb`
