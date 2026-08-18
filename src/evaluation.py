from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np


def evaluate_model(model, X_test):
    """Nimmt ein beliebiges trainiertes Modell und generiert Vorhersagen."""
    predictions = model.predict(X_test)

    return predictions

# y_test = Deine echten Zielwerte aus dem Test-Split
# predictions = Die Ausgabe deines Modells
def evaluate_model_performance(y_test, predictions):
    """Berechnet und gibt die Leistungskennzahlen des Modells aus."""
    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)  # Zieht die Wurzel aus dem MSE für bessere Interpretierbarkeit
    r2 = r2_score(y_test, predictions)

    # --- Trefferquote (Directional Accuracy) ---
    # np.sign() macht aus negativen Zahlen -1, aus positiven 1 und aus 0 eine 0.
    # Wir vergleichen, ob das Vorzeichen bei Realität und Vorhersage identisch ist.
    correct_directions = (np.sign(y_test) == np.sign(predictions))
    hit_rate = correct_directions.mean() * 100

    print("=== Modell-Evaluation ===")
    print(f"MAE (Mittlerer absoluter Fehler): {mae:.2f} $")
    print(f"RMSE (Wurzel der mittleren Fehlerquadrate): {rmse:.2f} $")
    print(f"R^2 Score (Bestimmtheitsmaß): {r2:.2f}")
    print(f"Trefferquote (Directional Accuracy): {hit_rate:.2f} %")    
    print("=========================")

    return hit_rate, rmse, mae, r2


def plot_predictions(dates, y_test, predictions):
    plt.figure(figsize=(12, 8))

    plt.plot(dates, y_test.values, color='blue', label='Tatsächliche Werte')
    
    plt.plot(dates, predictions, color='orange', linestyle='--', label='Vorhersagen')

    plt.xlabel('Datum')
    plt.ylabel('Aktienkurs in $')
    plt.title('GOOGL Aktienkurs: Realität vs. Vorhersage')
    plt.legend()
    plt.grid(True)
    
    # dreht die Datums-Texte auf der X-Achse leicht schräg, 
    # damit sie sich nicht überlappen, wenn es viele Tage sind
    plt.gcf().autofmt_xdate()

    plt.show()
