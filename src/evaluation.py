from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy.stats import binomtest
import numpy as np
import pandas as pd

import config


def evaluate_model(model, X_test):
    """Nimmt ein beliebiges trainiertes Modell und generiert Vorhersagen."""
    return model.predict(X_test)


def compute_metrics(y_true, y_pred) -> dict:
    """MAE, RMSE, R² und Trefferquote (Directional Accuracy) in einem Dict.

    Trefferquote: Anteil der Tage, an denen das Vorzeichen der Vorhersage mit der
    echten Änderung übereinstimmt. Sagt eine Regel keine Richtung voraus
    (Vorhersage überall 0), ist die Trefferquote nicht definiert (NaN).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    has_direction = bool(np.any(y_pred != 0))
    hits = int((np.sign(y_true) == np.sign(y_pred)).sum()) if has_direction else None
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": r2_score(y_true, y_pred),
        "Trefferquote": hits / len(y_true) * 100 if has_direction else float("nan"),
        "Treffer": hits,
        "n": len(y_true),
    }


def evaluate_model_performance(y_test, predictions, name: str = ""):
    """Gibt die Leistungskennzahlen aus (wie bisher) und liefert sie als Dict."""
    m = compute_metrics(y_test, predictions)
    print(f"=== Modell-Evaluation {name} ===")
    print(f"MAE (Mittlerer absoluter Fehler): {m['MAE']:.2f} $")
    print(f"RMSE (Wurzel der mittleren Fehlerquadrate): {m['RMSE']:.2f} $")
    print(f"R^2 Score (Bestimmtheitsmaß): {m['R2']:.2f}")
    print(f"Trefferquote (Directional Accuracy): {m['Trefferquote']:.2f} %")
    print("=========================")
    return m


def direction_p_value(hits, n: int) -> float:
    """Einseitiger Binomialtest: Ist die Trefferquote signifikant besser als 50 %?"""
    if hits is None or (isinstance(hits, float) and np.isnan(hits)):
        return float("nan")
    return float(binomtest(int(hits), int(n), p=0.5, alternative="greater").pvalue)


def trust_criteria(test_metrics: dict, persistence_test: dict) -> dict:
    """Die drei Kriterien für "vertrauenswürdig" (siehe Leitfrage):

    1. MAE und RMSE sind kleiner als bei der Persistenz-Regel.
    2. R² im Testzeitraum ist größer als 0.
    3. Trefferquote ist signifikant besser als 50 % (einseitiger Binomialtest).
    """
    p = direction_p_value(test_metrics["Treffer"], test_metrics["n"])
    c1 = (test_metrics["MAE"] < persistence_test["MAE"]
          and test_metrics["RMSE"] < persistence_test["RMSE"])
    c2 = test_metrics["R2"] > 0
    c3 = bool(p < config.ALPHA) if not np.isnan(p) else False
    return {"K1_schlaegt_Persistenz": c1, "K2_R2_ueber_0": c2,
            "K3_Treffer_signifikant": c3, "p_Wert_Treffer": p,
            "vertrauenswuerdig": c1 and c2 and c3}


def metrics_table(rows: dict) -> pd.DataFrame:
    """rows: {(Name, Zeitraum): metrics-dict} -> DataFrame."""
    out = []
    for (name, period), m in rows.items():
        out.append({"Modell": name, "Zeitraum": period, "MAE": m["MAE"], "RMSE": m["RMSE"],
                    "R2": m["R2"], "Trefferquote": m["Trefferquote"], "n": m["n"]})
    return pd.DataFrame(out)
