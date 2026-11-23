"""Regel-Baselines: einfache, bekannte Faustregeln statt gelernter Modelle.

Alle Regeln sagen – wie die ML-Modelle – die Preisänderung von heute auf
morgen ($) voraus (Spalte 'Target'). Sie werden auf denselben Daten und mit
denselben Kennzahlen bewertet wie die Modelle.
"""
import numpy as np
import pandas as pd


def persistence_rule(df: pd.DataFrame) -> np.ndarray:
    """Persistenz-Regel / Random Walk: "Der Kurs von morgen ist der Kurs von heute".

    Prognostizierte Preisänderung ist daher immer 0 $. Sie ist der
    Standard-Benchmark der Zeitreihenprognose und folgt aus der Hypothese
    effizienter Märkte (Fama, 1970). Eine Richtung sagt sie nicht voraus.
    """
    return np.zeros(len(df))


def sma_crossover_rule(df: pd.DataFrame, typical_move: float) -> np.ndarray:
    """SMA-Crossover (Golden/Death Cross, hier 10/50 Tage).

    Liegt der kurze Durchschnitt (SMA_10) über dem langen (SMA_50), erwartet die
    Regel einen steigenden Kurs, sonst einen fallenden. Die Größe der Bewegung
    ist nicht Teil der Regel; wir nehmen die mittlere absolute Tagesänderung der
    Trainingsdaten (typical_move) als Betrag.
    """
    direction = np.where(df["SMA_10"] > df["SMA_50"], 1.0, -1.0)
    return direction * typical_move


def always_up_rule(typical_move: float, n: int) -> np.ndarray:
    """"Immer steigend" (Buy-and-Hold-Haltung): Referenz für die Trefferquote.

    Die Trefferquote dieser Regel ist der Anteil der Aufwärtstage im Testzeitraum
    und damit die ehrliche Vergleichsmarke – nicht pauschal 50 %.
    """
    return np.full(n, typical_move)
