"""Zentrale Einstellungen: Pfade, Ticker, Zeitraum, Split und Feature-Liste."""
from pathlib import Path

# Projektwurzel unabhängig davon, von wo aus das Skript gestartet wird
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"          # liegt in .gitignore
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURED_DIR = DATA_DIR / "featured"
RESULTS_DIR = PROJECT_ROOT / "results"    # wird mit eingecheckt (klein)
FIGURES_DIR = RESULTS_DIR / "figures"
SNAPSHOT_DIR = RESULTS_DIR / "snapshot"   # eingefrorene Kursdaten (klein, wird mit eingecheckt)

TICKER = "GOOGL"       # Alphabet Inc. (Class A)
PERIOD = "3y"          # Zeitraum der yfinance-Abfrage, wenn kein festes Fenster gesetzt ist
# Festes Datenfenster für reproduzierbare Ergebnisse (END_DATE ist exklusiv).
# Beide auf None setzen, um stattdessen immer die letzten PERIOD abzurufen.
START_DATE = "2023-11-21"
END_DATE = "2026-11-21"
SPLIT_RATIO = 0.8      # die ältesten 80 % sind Training, die neuesten 20 % Test

FEATURES = [
    "Close", "Volume", "Return_Today",
    "Return_Lag_1", "Return_Lag_2", "Return_Lag_3",
    "SMA_10", "SMA_50",
    "Volatility_20", "RSI_14",
]
TARGET = "Target"      # Preisänderung in $ von heute auf morgen

# Schwelle für Kriterium 3 ("Trefferquote besser als Münzwurf"): einseitiger Binomialtest
ALPHA = 0.05

# Welches Modell gilt als "bestes" (für den Zusatz-Plot im Training)?
# None = automatisch das Modell mit dem kleinsten RMSE im Testzeitraum.
# Alternativ ein Name: "Lineare Regression", "Random Forest" oder "Gradient Boosting".
BEST_MODEL = None
