# Lauf-Protokoll GOOGL

- Zeitpunkt: 2026-11-23 13:41
- Python 3.13.18, pandas 3.0.5, numpy 2.2.6, scikit-learn 1.9.0, yfinance 1.5.2
- Befehl: `python src/main.py` (Einstellungen in `src/config.py`; `--refresh` ruft neue Daten ab)
- Datenquelle dieses Laufs: Snapshot

## Daten
- Quelle: Yahoo Finance via yfinance, Ticker `GOOGL`, Fenster 2023-11-21 bis 2026-11-21 (exklusiv)
- Kursdaten: 753 Handelstage (2023-11-21 bis 2026-11-20)
- Nach Feature-Engineering und Bereinigung: 703 Zeilen
- Training: 562 Tage (2024-02-02 bis 2026-04-30)
- Test: 141 Tage (2026-05-01 bis 2026-11-19)
- Anteil Aufwärtstage im Testzeitraum: 46.8 %
- Features: Close, Volume, Return_Today, Return_Lag_1, Return_Lag_2, Return_Lag_3, SMA_10, SMA_50, Volatility_20, RSI_14
- Target: `Target` = Kursänderung in $ von heute auf morgen

## Leakage-Prüfungen (alle bestanden)
- [x] Target ist die Änderung von morgen und kein Feature
- [x] Rolling-Features (SMA) nutzen nur Vergangenheit bis heute
- [x] Split ist chronologisch, ohne Überschneidung
- [x] Keine fehlenden Werte in Training/Test

## Kennzahlen
| Modell | Zeitraum | MAE | RMSE | R2 | Trefferquote | n |
|---|---|---|---|---|---|---|
| Persistenz-Regel | Training | 2.86 | 4.16 | -0.01 | – | 562 |
| SMA-Crossover | Training | 3.70 | 4.85 | -0.37 | 54.63 | 562 |
| Immer steigend | Training | 3.65 | 4.80 | -0.34 | 55.52 | 562 |
| Lineare Regression | Training | 2.85 | 4.13 | 0.01 | 54.63 | 562 |
| Random Forest | Training | 2.51 | 3.38 | 0.33 | 67.97 | 562 |
| Gradient Boosting | Training | 1.86 | 2.45 | 0.65 | 79.18 | 562 |
| Persistenz-Regel | Test | 5.42 | 7.68 | -0.01 | – | 141 |
| SMA-Crossover | Test | 6.02 | 8.11 | -0.13 | 47.52 | 141 |
| Immer steigend | Test | 6.05 | 8.49 | -0.24 | 46.81 | 141 |
| Lineare Regression | Test | 5.52 | 7.82 | -0.05 | 46.81 | 141 |
| Random Forest | Test | 11.47 | 13.60 | -2.17 | 46.10 | 141 |
| Gradient Boosting | Test | 18.18 | 20.67 | -6.34 | 43.97 | 141 |

## Kriterien für "vertrauenswürdig" (Testzeitraum)
1. MAE und RMSE kleiner als bei der Persistenz-Regel
2. R² größer als 0
3. Trefferquote signifikant über 50 % (einseitiger Binomialtest, p < 0.05)

| Modell | K1_schlaegt_Persistenz | K2_R2_ueber_0 | K3_Treffer_signifikant | p_Wert_Treffer | vertrauenswuerdig |
|---|---|---|---|---|---|
| Lineare Regression | nein | nein | nein | 0.80 | nein |
| Random Forest | nein | nein | nein | 0.84 | nein |
| Gradient Boosting | nein | nein | nein | 0.94 | nein |
| SMA-Crossover | nein | nein | nein | 0.75 | nein |
| Immer steigend | nein | nein | nein | 0.80 | nein |

## Ausgabedateien
- `results/metrics.csv`, `results/criteria.csv`, `results/predictions_test.csv`
- `results/figures/*.png`
- Zwischenstände der Daten liegen in `data/` (nicht im Repository)
