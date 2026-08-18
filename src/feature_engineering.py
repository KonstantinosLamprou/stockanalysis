import pandas_ta as ta
import pandas as pd
from pathlib import Path


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Erstellt Finanz-Features für das Machine Learning Modell.
    """
    df_features = df.copy()

    # --- Basis-Rendite berechnen (Wird für Lags und Volatilität gebraucht) ---
    df_features['Return_Today'] = df_features['Close'].diff()

    # --- 1. Lags (Verzögerungen) ---
    # Wir verschieben die Rendite von heute in die Zukunft, damit das Modell 
    # die vergangenen Tage sehen kann (Momentum-Effekt).
    df_features['Return_Lag_1'] = df_features['Return_Today'].shift(1)
    df_features['Return_Lag_2'] = df_features['Return_Today'].shift(2)
    df_features['Return_Lag_3'] = df_features['Return_Today'].shift(3)

    # --- 2. Gleitende Durchschnitte (SMA) ---
    df_features['SMA_10'] = df_features['Close'].rolling(window=10).mean()
    df_features['SMA_50'] = df_features['Close'].rolling(window=50).mean()

    # --- 3. Volatilität (Risiko) ---
    # Die Standardabweichung (std) der täglichen Renditen der letzten 20 Tage.
    # Ein hoher Wert bedeutet, die Aktie schwankt gerade extrem stark.
    df_features['Volatility_20'] = df_features['Return_Today'].rolling(window=20).std()

    # --- 4. Momentum (RSI) ---
    # Der Relative Strength Index (klassischerweise über 14 Tage).
    # pandas-ta übernimmt hier die komplexe mathematische Berechnung.
    df_features['RSI_14'] = df_features.ta.rsi(close='Close', length=14)
    # --- TARGET ---
    # Die Preisveränderung von heute auf morgen (Unser y)
    df_features['Target'] = df_features['Close'].diff().shift(-1)

    # -----
    # Ordner automatisch erstellen (falls nicht vorhanden)
    data_dir = Path("../data/featured")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Dateiname mit Ticker
    filename = data_dir / f"GOOGL_featured_data.csv"
    
    # Speichern
    df_features.to_csv(filename)
    print(f"Featured Daten gespeichert unter: {filename}")
    # -----

    # --- Bereinigung ---
    # ACHTUNG: Durch den SMA_50 brauchen wir 50 Tage Anlaufzeit, bis alle 
    # Daten für einen Tag berechnet werden können. Die ersten 50 Zeilen 
    # enthalten also NaNs und werden hier rigoros gelöscht.
    df_features = df_features.dropna()

    return df_features

