import yfinance as yf
import pandas as pd
from pathlib import Path

def load_stock_data(ticker_symbol: str, period: str = "3y") -> pd.DataFrame:
    """
    Lädt historische Aktienkursdaten und speichert sie als CSV.
    
    Args:
        ticker_symbol (str): Das Ticker-Symbol (z.B. "GOOGL").
        period (str): Zeitraum (Standard: "6mo").
    
    Returns:
        pd.DataFrame: Die geladenen Daten.
    """
    print(f"Lade Daten für {ticker_symbol}...")
    
    # Daten herunterladen
    df = yf.download(ticker_symbol, period=period)
    
    # Prüfen, ob Daten geladen wurden
    if df.empty:
        raise ValueError(f"Keine Daten für {ticker_symbol} gefunden.")
    
    # Ordner automatisch erstellen (falls nicht vorhanden)
    data_dir = Path("../data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Dateiname mit Ticker
    filename = data_dir / f"{ticker_symbol}_raw_data.csv"
    
    # Speichern
    df.to_csv(filename)
    print(f"Daten gespeichert unter: {filename}")
    
    return df
