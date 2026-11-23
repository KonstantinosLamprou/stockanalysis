import yfinance as yf
import pandas as pd
import time
import config

def load_stock_data(ticker_symbol: str, period: str = config.PERIOD) -> pd.DataFrame:
    """
    Lädt historische Aktienkursdaten und speichert sie als CSV.
    
    Args:
        ticker_symbol (str): Das Ticker-Symbol (z.B. "GOOGL").
        period (str): Zeitraum (Standard: siehe config.PERIOD).
    
    Returns:
        pd.DataFrame: Die geladenen Daten.
    """
    print(f"Lade Daten für {ticker_symbol}...")
    
    # Daten herunterladen
    # Yahoo antwortet manchmal mit "Rate limited": bis zu 6 Versuche mit Wartezeit
    df = pd.DataFrame()
    for attempt in range(6):
        if config.START_DATE and config.END_DATE:
            df = yf.download(ticker_symbol, start=config.START_DATE, end=config.END_DATE)
        else:
            df = yf.download(ticker_symbol, period=period)
        if not df.empty:
            break
        print(f"Versuch {attempt + 1} ohne Daten, warte kurz...")
        time.sleep(30)
    
    # Prüfen, ob Daten geladen wurden
    if df.empty:
        raise ValueError(f"Keine Daten für {ticker_symbol} gefunden.")
    
    # Ordner automatisch erstellen (falls nicht vorhanden)
    data_dir = config.RAW_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Dateiname mit Ticker
    filename = data_dir / f"{ticker_symbol}_raw_data.csv"
    
    # Speichern
    df.to_csv(filename)
    print(f"Daten gespeichert unter: {filename}")
    
    return df


def snapshot_path(ticker_symbol: str):
    return config.SNAPSHOT_DIR / f"{ticker_symbol}_close_volume.csv"


def save_snapshot(df_clean: pd.DataFrame, ticker_symbol: str):
    """Friert die bereinigten Kursdaten (Close, Volume) ein.

    Yahoo liefert bei jedem Abruf minimal andere Werte, und Baummodelle reagieren
    darauf empfindlich. Mit dem Snapshot sind alle Zahlen reproduzierbar.
    """
    config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(snapshot_path(ticker_symbol))
    print(f"Snapshot gespeichert unter: {snapshot_path(ticker_symbol)}")


def load_snapshot(ticker_symbol: str) -> pd.DataFrame:
    return pd.read_csv(snapshot_path(ticker_symbol), index_col=0, parse_dates=True)
