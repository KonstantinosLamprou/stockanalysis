# Simple Architektur fuer dieses Projekt

```text
aktienanalyse-projekt/
├── .git/
├── .gitignore               # Ignoriert /data, __pycache__, .env etc.
├── README.md                # Projektbeschreibung und Setup-Guide
├── requirements.txt         # Oder Pipfile / pyproject.toml / environment.yml
├── Dockerfile               # (Optional) Für eine isolierte, reproduzierbare Umgebung
│
├── data/                    # Wird in der .gitignore komplett ausgeschlossen!
│   ├── raw/                 # Unveränderte Rohdaten (z.B. CSVs von Yahoo Finance)
│   └── processed/           # Bereinigte Daten, bereit fürs Training
│
├── docs/                    # Uni-Dokumente, Exposee, Notizen, Abgabe-PDFs, allgemeine Dokumentation
│
├── notebooks/               # Die Jupyter Notebooks
│   ├── 01_data_exploration.ipynb   # Dein Spielplatz
│   └── 99_uni_abgabe.ipynb         # Das saubere finale Notebook für den Prof
│
├── src/                     # Der eigentliche, modulare Code
│   ├── __init__.py
│   ├── config.py            # Pfade, API-Keys (geladen aus .env)
│   ├── data_loader.py       # API-Calls, CSVs einlesen
│   ├── preprocessing.py     # Missing Values füllen, Skalierung, Feature Engineering
│   ├── model.py             # ML-Modell Definition und Training
│   └── evaluation.py        # Metriken (RMSE, Accuracy), Plots generieren
│
└── tests/                   # Deine Test-Suite (pytest)
    ├── test_data_loader.py
    └── test_preprocessing.py
```