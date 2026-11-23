"""Schnelle Tests ohne Internet: pytest tests/"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import evaluation as ev
import validation as val
import models.rules as rules


def _frame(n=200):
    idx = pd.bdate_range("2024-01-01", periods=n)
    close = pd.Series(100 + np.cumsum(np.random.default_rng(0).normal(0, 1, n)), index=idx)
    df = pd.DataFrame({"Close": close})
    df["Return_Today"] = df["Close"].diff()
    df["SMA_10"] = df["Close"].rolling(10).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["Target"] = df["Close"].diff().shift(-1)
    return df.dropna()


def test_persistence_predicts_zero():
    assert (rules.persistence_rule(_frame()) == 0).all()


def test_sma_rule_direction():
    df = _frame()
    p = rules.sma_crossover_rule(df, 2.0)
    assert set(np.unique(p)) <= {-2.0, 2.0}
    assert ((p > 0) == (df["SMA_10"] > df["SMA_50"])).all()


def test_metrics_persistence_has_no_direction():
    m = ev.compute_metrics([1.0, -2.0, 3.0], [0, 0, 0])
    assert np.isnan(m["Trefferquote"]) and m["MAE"] == pytest.approx(2.0)


def test_validation_passes_on_clean_data():
    df = _frame()
    train, test = df.iloc[:50], df.iloc[50:]
    assert len(val.run_all_checks(df, train, test, ["Close", "SMA_10", "SMA_50", "Return_Today"])) == 4


def test_validation_catches_target_as_feature():
    df = _frame()
    with pytest.raises(AssertionError):
        val.check_features_vs_target(df, ["Close", "Target"])


def test_validation_catches_shuffled_split():
    df = _frame()
    shuffled = df.sample(frac=1, random_state=1)
    with pytest.raises(AssertionError):
        val.check_chronological_split(shuffled.iloc[:80], shuffled.iloc[80:])


def test_validation_catches_overlap():
    df = _frame()
    with pytest.raises(AssertionError):
        val.check_chronological_split(df.iloc[:80], df.iloc[60:])
