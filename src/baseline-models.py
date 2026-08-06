import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# SCHRITT 1: Datenbeschaffung
# ==========================================
ticker_symbol = "GOOGL"

# yfinance macht es uns sehr leicht: "6m" steht für 6 Monate
print(f"Lade Daten für {ticker_symbol}...")
df = yf.download(ticker_symbol, period="6m")

# ==========================================
# SCHRITT 2: Datenbereinigung (Pandas)
# ==========================================
# Für unser Baseline-Modell brauchen wir nicht alle Spalten (High, Low, Open etc.).
# Wir isolieren den Schlusskurs ('Close'), da dieser meistens prognostiziert wird.
df_clean = df[['Close']].copy()

# Wir prüfen auf fehlende Werte (NaNs), die z.B. durch Feiertage entstehen können, 
# und werfen diese Zeilen sicherheitshalber raus, damit das Modell nicht abstürzt.
df_clean = df_clean.dropna()

print("\nDie ersten 3 Zeilen der bereinigten Daten:")
print(df_clean.head(3))

# ==========================================
# SCHRITT 3: Train-Test-Split
# ==========================================
# Bei Zeitreihen dürfen wir nicht zufällig mischen! Wir teilen streng chronologisch auf.
# Die neuesten Daten werden die Testdaten.
split_ratio = 0.8  # 80% der Daten zum Trainieren, 20% zum Testen
split_index = int(len(df_clean) * split_ratio)

train_data = df_clean.iloc[:split_index]
test_data = df_clean.iloc[split_index:]

print(f"\nDatenaufteilung abgeschlossen:")
print(f"-> Trainingsdaten: {len(train_data)} Tage")
print(f"-> Testdaten: {len(test_data)} Tage")