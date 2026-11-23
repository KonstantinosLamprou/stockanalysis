"""Prüfungen gegen Data Leakage (wie Unit-Tests, per assert).

Data Leakage heißt: Das Modell sieht beim Training Informationen, die es in der
Praxis zum Prognosezeitpunkt noch nicht hätte (z. B. Zukunftswerte oder
Testdaten). Jede Prüfung hier schlägt mit einer klaren Meldung fehl, wenn das
passiert.
"""
import numpy as np
import pandas as pd


def check_features_vs_target(df: pd.DataFrame, features: list, target: str = "Target"):
    """Das Target ist die Änderung von heute auf *morgen* und kein Feature."""
    assert target not in features, "Leakage: Target ist selbst als Feature enthalten."
    # Target(t) muss genau Return_Today(t+1) sein, also erst morgen bekannt
    expected = df["Return_Today"].shift(-1)
    both = df[target].notna() & expected.notna()
    assert np.allclose(df.loc[both, target], expected[both]), \
        "Leakage: Target stimmt nicht mit der Änderung des Folgetags überein."


def check_features_use_only_past(df: pd.DataFrame):
    """Rolling-Features dürfen nur Werte bis einschließlich heute nutzen."""
    idx = df.index[10:]  # ab hier liegt das 10-Tage-Fenster komplett im DataFrame
    for t in idx[:: max(1, len(idx) // 20)]:
        pos = df.index.get_loc(t)
        manual = df["Close"].iloc[pos - 9: pos + 1].mean()  # nur t-9 ... t
        assert np.isclose(df["SMA_10"].iloc[pos], manual), \
            f"Leakage: SMA_10 am {t.date()} nutzt andere Tage als t-9..t."


def check_chronological_split(train: pd.DataFrame, test: pd.DataFrame):
    """Training liegt komplett vor dem Test; keine Überschneidung, kein Mischen."""
    assert len(train) > 0 and len(test) > 0, "Split: leere Menge."
    assert train.index.is_monotonic_increasing and test.index.is_monotonic_increasing, \
        "Split: Daten sind nicht chronologisch sortiert."
    assert train.index.max() < test.index.min(), \
        "Leakage: Trainingsdaten reichen in den Testzeitraum hinein."
    assert len(train.index.intersection(test.index)) == 0, \
        "Leakage: Zeilen sind in Training und Test gleichzeitig."


def check_no_missing(train: pd.DataFrame, test: pd.DataFrame, features: list, target: str = "Target"):
    for name, part in (("Training", train), ("Test", test)):
        assert not part[features + [target]].isna().any().any(), f"{name}: fehlende Werte."


def run_all_checks(df_featured, train, test, features, target="Target"):
    """Führt alle Prüfungen aus und gibt eine Liste bestandener Checks zurück."""
    checks = [
        ("Target ist die Änderung von morgen und kein Feature",
         lambda: check_features_vs_target(df_featured, features, target)),
        ("Rolling-Features (SMA) nutzen nur Vergangenheit bis heute",
         lambda: check_features_use_only_past(df_featured)),
        ("Split ist chronologisch, ohne Überschneidung",
         lambda: check_chronological_split(train, test)),
        ("Keine fehlenden Werte in Training/Test",
         lambda: check_no_missing(train, test, features, target)),
    ]
    passed = []
    for name, fn in checks:
        fn()  # wirft AssertionError bei Fehler
        passed.append(name)
    return passed
