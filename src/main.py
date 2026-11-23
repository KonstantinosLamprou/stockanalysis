# Gesamter Ablauf in einem Lauf: Daten -> Features -> Prüfungen -> Split -> Baselines & Modelle
# -> Kennzahlen (Training und Test) -> Diagramme -> results/run_report.md
# Start:  python src/main.py     (von der Projektwurzel aus; funktioniert aber von überall)
import argparse
import json
import platform
from datetime import datetime

import pandas as pd

import config
import data_loader as dl
import preprocessing as pp
import feature_engineering as fe
import validation as val
import evaluation as ev
import plotting as pl
import models.linear as ml
import models.optimized as mo
import models.rules as rules


def main(refresh: bool = False):
    ticker = config.TICKER
    features = config.FEATURES

    # 1. Daten laden, bereinigen, Features bauen
    if not refresh and dl.snapshot_path(ticker).exists():
        # Standard: eingefrorene Daten -> identische Ergebnisse bei jedem Lauf
        print(f"Lade eingefrorene Daten: {dl.snapshot_path(ticker)}")
        df_clean = dl.load_snapshot(ticker)
        data_source = "Snapshot"
    else:
        # Neuer Abruf bei Yahoo Finance; überschreibt den Snapshot
        df = dl.load_stock_data(ticker)
        df_clean = pp.clean_data(df, ticker)
        dl.save_snapshot(df_clean, ticker)
        df_clean = dl.load_snapshot(ticker)  # immer über die CSV, damit Rundungen identisch sind
        data_source = "Neuer Abruf (Yahoo Finance)"
    df = df_clean  # ab hier: bereinigte Daten
    df_featured = fe.create_features(df_clean, ticker)

    # 2. Split (chronologisch: neueste Daten = Test)
    train_data, test_data = pp.split_data(df_featured)

    # 3. Leakage-Prüfungen (bricht mit AssertionError ab, wenn etwas nicht stimmt)
    passed_checks = val.run_all_checks(df_featured, train_data, test_data, features, config.TARGET)
    print(f"{len(passed_checks)} Leakage-Prüfungen bestanden.")

    X_train, y_train = train_data[features], train_data[config.TARGET]
    X_test, y_test = test_data[features], test_data[config.TARGET]
    typical_move = float(y_train.abs().mean())

    # 4. Regel-Baselines (keine Trainingsphase) und Modelle
    preds = {"train": {}, "test": {}}
    for period, part in (("train", train_data), ("test", test_data)):
        preds[period]["Persistenz-Regel"] = rules.persistence_rule(part)
        preds[period]["SMA-Crossover"] = rules.sma_crossover_rule(part, typical_move)
        preds[period]["Immer steigend"] = rules.always_up_rule(typical_move, len(part))

    models = {
        "Lineare Regression": ml.train_linear_regression_model(X_train, y_train),
        "Random Forest": mo.train_random_forest_model(X_train, y_train),
        "Gradient Boosting": mo.train_gradient_boosting_model(X_train, y_train),
    }
    for name, model in models.items():
        preds["train"][name] = ev.evaluate_model(model, X_train)
        preds["test"][name] = ev.evaluate_model(model, X_test)

    # 5. Kennzahlen für Training und Test
    rows = {}
    for period_key, period_name, part in (("train", "Training", train_data), ("test", "Test", test_data)):
        for name, p in preds[period_key].items():
            rows[(name, period_name)] = ev.compute_metrics(part[config.TARGET], p)
    for name in models:
        ev.evaluate_model_performance(y_test, preds["test"][name], name)
    table = ev.metrics_table(rows)

    # 6. Die drei Kriterien für "vertrauenswürdig" (nur Test)
    persistence_test = rows[("Persistenz-Regel", "Test")]
    crit_rows = []
    for name in list(models) + ["SMA-Crossover", "Immer steigend"]:
        c = ev.trust_criteria(rows[(name, "Test")], persistence_test)
        crit_rows.append({"Modell": name, **c})
    criteria = pd.DataFrame(crit_rows)

    # 7. Ergebnisse speichern
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(config.RESULTS_DIR / "metrics.csv", index=False, float_format="%.4f")
    criteria.to_csv(config.RESULTS_DIR / "criteria.csv", index=False, float_format="%.4f")
    pred_out = pd.DataFrame({"Datum": test_data.index, "Realität": y_test.values})
    for name, p in preds["test"].items():
        pred_out[name] = p
    pred_out.to_csv(config.RESULTS_DIR / "predictions_test.csv", index=False, float_format="%.4f")

    # 8. Diagramme
    split_date = test_data.index.min()
    model_names = list(models)
    pl.plot_price_with_split(df_featured, split_date)
    pl.plot_predictions_vs_actual(test_data.index, y_test.values, preds["test"],
                                  "Testzeitraum", "02_prognose_test", only=model_names)
    pl.plot_predictions_vs_actual(train_data.index, y_train.values, preds["train"],
                                  "Trainingszeitraum", "03_prognose_training", only=model_names)
    test_table = table[table["Zeitraum"] == "Test"]
    pl.plot_metric_bars(table, "MAE", "Test: mittlerer absoluter Fehler (kleiner ist besser)", "MAE in $",
                        "04_vergleich_mae", reference=persistence_test["MAE"], ref_label="Persistenz-Regel")
    pl.plot_metric_bars(table, "R2", "Test: Bestimmtheitsmaß R² (über 0 ist besser als der Mittelwert)", "R²",
                        "05_vergleich_r2", reference=0, ref_label="R² = 0")
    up_share = float((y_test > 0).mean() * 100)
    pl.plot_metric_bars(table, "Trefferquote", "Test: Trefferquote der Richtung (Ziel: über 50 %)", "Trefferquote in %",
                        "06_vergleich_trefferquote", reference=50, ref_label="Münzwurf 50 %")
    pl.plot_train_vs_test(table[table["Modell"].isin(model_names)], "R2",
                          "Training vs. Test: R² der Modelle", "R²", "07_train_vs_test_r2")

    # 9. Lauf-Protokoll
    write_run_report(df, df_featured, train_data, test_data, passed_checks, table, criteria, up_share, data_source)

    # Kennzahlen zu den Daten für die Folien (build_deck.py liest nur results/, nicht data/)
    info = {
        "ticker": ticker, "period": config.PERIOD,
        "raw_rows": len(df), "raw_start": f"{df.index.min():%d.%m.%Y}", "raw_end": f"{df.index.max():%d.%m.%Y}",
        "train_rows": len(train_data), "test_rows": len(test_data),
        "train_start": f"{train_data.index.min():%d.%m.%Y}", "train_end": f"{train_data.index.max():%d.%m.%Y}",
        "test_start": f"{test_data.index.min():%d.%m.%Y}", "test_end": f"{test_data.index.max():%d.%m.%Y}",
        "up_share_test": up_share,
        "close_train_max": float(train_data["Close"].max()), "close_test_max": float(test_data["Close"].max()),
        "target_std_train": float(y_train.std()), "target_std_test": float(y_test.std()),
        "n_features": len(features), "leakage_checks": len(passed_checks),
        "run_date": f"{datetime.now():%d.%m.%Y}",
    }
    (config.RESULTS_DIR / "run_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Fertig. Ergebnisse in {config.RESULTS_DIR}")


def _md(df: pd.DataFrame) -> str:
    """Kleine Markdown-Tabelle ohne zusätzliche Abhängigkeit (tabulate)."""
    d = df.copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: "–" if pd.isna(v) else f"{v:.2f}")
    head = "| " + " | ".join(map(str, d.columns)) + " |"
    sep = "|" + "|".join("---" for _ in d.columns) + "|"
    body = ["| " + " | ".join(map(str, r)) + " |" for r in d.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def write_run_report(df_raw, df_featured, train, test, passed_checks, table, criteria, up_share, data_source=""):
    """Schreibt results/run_report.md: was wurde wann mit welchen Daten gerechnet."""
    import numpy, sklearn, yfinance
    lines = [
        f"# Lauf-Protokoll {config.TICKER}",
        "",
        f"- Zeitpunkt: {datetime.now():%Y-%m-%d %H:%M}",
        f"- Python {platform.python_version()}, pandas {pd.__version__}, numpy {numpy.__version__}, "
        f"scikit-learn {sklearn.__version__}, yfinance {yfinance.__version__}",
        f"- Befehl: `python src/main.py` (Einstellungen in `src/config.py`; `--refresh` ruft neue Daten ab)",
        f"- Datenquelle dieses Laufs: {data_source}",
        "",
        "## Daten",
        f"- Quelle: Yahoo Finance via yfinance, Ticker `{config.TICKER}`, Fenster {config.START_DATE} bis {config.END_DATE} (exklusiv)" if config.START_DATE else f"- Quelle: Yahoo Finance via yfinance, Zeitraum `{config.PERIOD}`, Ticker `{config.TICKER}`",
        f"- Kursdaten: {len(df_raw)} Handelstage ({df_raw.index.min():%Y-%m-%d} bis {df_raw.index.max():%Y-%m-%d})",
        f"- Nach Feature-Engineering und Bereinigung: {len(df_featured)} Zeilen",
        f"- Training: {len(train)} Tage ({train.index.min():%Y-%m-%d} bis {train.index.max():%Y-%m-%d})",
        f"- Test: {len(test)} Tage ({test.index.min():%Y-%m-%d} bis {test.index.max():%Y-%m-%d})",
        f"- Anteil Aufwärtstage im Testzeitraum: {up_share:.1f} %",
        f"- Features: {', '.join(config.FEATURES)}",
        f"- Target: `{config.TARGET}` = Kursänderung in $ von heute auf morgen",
        "",
        "## Leakage-Prüfungen (alle bestanden)",
        *[f"- [x] {c}" for c in passed_checks],
        "",
        "## Kennzahlen",
        _md(table),
        "",
        "## Kriterien für \"vertrauenswürdig\" (Testzeitraum)",
        "1. MAE und RMSE kleiner als bei der Persistenz-Regel",
        "2. R² größer als 0",
        f"3. Trefferquote signifikant über 50 % (einseitiger Binomialtest, p < {config.ALPHA})",
        "",
        _md(criteria.assign(**{c: criteria[c].map({True: "ja", False: "nein"})
                               for c in criteria.columns if criteria[c].dtype == bool})),
        "",
        "## Ausgabedateien",
        "- `results/metrics.csv`, `results/criteria.csv`, `results/predictions_test.csv`",
        "- `results/figures/*.png`",
        "- Zwischenstände der Daten liegen in `data/` (nicht im Repository)",
        "",
    ]
    (config.RESULTS_DIR / "run_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aktienanalyse: kompletter Lauf")
    parser.add_argument("--refresh", action="store_true",
                        help="Kursdaten neu bei Yahoo Finance abrufen und den Snapshot überschreiben")
    main(refresh=parser.parse_args().refresh)
