import pandas as pd
from pathlib import Path

def clean_data(df: pd.DataFrame, ticker_symbol: str):

    if df.empty:
        raise ValueError("Der DataFrame ist leer. Bitte überprüfen Sie die Datenquelle.")

    # Bereinigung
    df_clean = df[['Close']].copy().dropna()

    data_dir = Path("../data/processed")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Dateiname mit Ticker
    filename = data_dir / f"{ticker_symbol}_cleaned_data.csv"
    
    # Speichern
    df_clean.to_csv(filename, index=False)
    print(f"Daten gespeichert unter: {filename}")

    return df_clean

def split_data(df: pd.DataFrame, split_ratio: float = 0.8):

    # Split
    split_index = int(len(df) * split_ratio)
    train_data = df.iloc[:split_index]
    test_data = df.iloc[split_index:]

    print("Datenvorverarbeitung abgeschlossen.")
    print(f"Trainingsdaten: {len(train_data)} Zeilen")
    print(f"Testdaten: {len(test_data)} Zeilen")
    
    return train_data, test_data