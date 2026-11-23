# Run-Prozess: so entstehen die Ergebnisse

Diese Datei dokumentiert, wie das Projekt ausgeführt wird und was bei einem Lauf passiert.
Das jeweils letzte Lauf-Protokoll (Zeitpunkt, Daten, Kennzahlen) steht in `results/run_report.md`.

## Einrichtung (einmalig)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows;  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Befehle

| Befehl | Wirkung |
|---|---|
| `python src/main.py` | Kompletter Lauf mit den **eingefrorenen Daten** (`results/snapshot/`). Ergebnisse sind bei jedem Lauf identisch. |
| `python src/main.py --refresh` | Ruft die Kursdaten **neu bei Yahoo Finance** ab, überschreibt den Snapshot und rechnet alles neu. Die Zahlen ändern sich dann. |
| `python presentation/build_deck.py` | Baut `presentation/Aktienanalyse_Praesentation.pptx` aus `results/`. |
| `python -m pytest tests` | Schnelle Tests für Regeln und Leakage-Prüfungen (ohne Internet). |

Alle Skripte funktionieren von jedem Ordner aus, die Pfade kommen aus `src/config.py`.

## Was ein Lauf von `src/main.py` tut

1. **Daten laden**: Snapshot lesen oder (bei `--refresh`) bei Yahoo Finance abrufen (`data_loader.py`).
2. **Bereinigen** (`preprocessing.clean_data`): nur `Close` und `Volume`, fehlende Werte entfernen.
3. **Features bauen** (`feature_engineering.py`): 3 Lags, SMA 10/50, Volatilität (20 Tage), RSI (14). Target = Kursänderung von heute auf morgen in $.
4. **Chronologisch splitten** (`preprocessing.split_data`): die ältesten 80 % sind Training, die neuesten 20 % Test.
5. **Leakage-Prüfungen** (`validation.py`): vier `assert`-Prüfungen, der Lauf bricht bei einem Fehler ab:
   - Target ist die Änderung von *morgen* und kein Feature
   - Rolling-Features (SMA) nutzen nur Werte bis einschließlich heute
   - Split ist chronologisch und ohne Überschneidung
   - keine fehlenden Werte in Training und Test
6. **Regeln und Modelle** (`models/rules.py`, `models/linear.py`, `models/optimized.py`):
   - Regeln (Messlatte): Persistenz-Regel, SMA-Crossover, "Immer steigend"
   - Modelle: Lineare Regression, Random Forest, Gradient Boosting
7. **Kennzahlen** (`evaluation.py`) für Training **und** Test: MAE, RMSE, R², Trefferquote.
8. **Kriterien für "vertrauenswürdig"** (Leitfrage), nur auf dem Test:
   1. MAE und RMSE kleiner als bei der Persistenz-Regel
   2. R² größer als 0
   3. Trefferquote signifikant über 50 % (einseitiger Binomialtest, p < 0,05)
9. **Speichern** nach `results/`: `metrics.csv`, `criteria.csv`, `predictions_test.csv`, `run_info.json`, `run_report.md`, `figures/*.png`.

## Ausgabeordner

| Ordner/Datei | Inhalt | im Repository |
|---|---|---|
| `data/raw`, `data/processed`, `data/featured` | Zwischenstände der Daten | nein (`.gitignore`) |
| `results/snapshot/` | eingefrorene Kursdaten (Close, Volume) | **ja** |
| `results/` | Kennzahlen, Kriterien, Protokoll, Diagramme | **ja** |
| `presentation/` | Skript und fertige `.pptx` | **ja** |

## Warum der Snapshot?

Yahoo Finance liefert bei jedem Abruf minimal andere Werte, und die Baummodelle (vor allem Gradient Boosting) reagieren darauf spürbar
(z. B. schwankte das Test-R² von Gradient Boosting zwischen −5,5 und −6,3, ohne dass sich Code oder Zeitraum änderten).
Die Aussage bleibt gleich, aber die Zahlen auf den Folien, im Notebook und im Lauf-Protokoll sollen identisch sein. Deshalb wird mit festen Daten gerechnet.
Das Datenfenster steht in `src/config.py` (`START_DATE`, `END_DATE`).

## Notebook

`notebooks/stock-market-analysis.ipynb` ist die Abgabe für die Hochschule (zusammen mit dem Präsentations-PDF als ZIP).
Es nutzt denselben Snapshot (`USE_SNAPSHOT = True`) und liefert dieselben Zahlen wie `results/metrics.csv`.
