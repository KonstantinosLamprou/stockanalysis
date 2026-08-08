from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt


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
    r2 = r2_score(y_test, predictions)

    print(f"MAE: {mae:.2f}")
    print(f"MSE: {mse:.2f}")
    print(f"R^2 Score: {r2:.2f}")    

    return mae, mse, r2


def plot_predictions(y_test, predictions):
    plt.figure(figsize=(8, 6))

    # Die Punkte plotten: X-Achse = Echte Werte, Y-Achse = Vorhersagen
    plt.scatter(y_test, predictions, alpha=0.5, color='blue', label='Vorhersagen')

    # Eine ideale diagonale Linie einzeichnen (Perfektes Modell)
    max_val = max(max(y_test), max(predictions))
    min_val = min(min(y_test), min(predictions))
    plt.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', label='Perfekte Vorhersage')

    # Plot strukturieren
    plt.xlabel('Tatsächliche Werte (y_test)')
    plt.ylabel('Vorhersagen (predictions)')
    plt.title('Modell-Auswertung: Realität vs. Vorhersage')
    plt.legend()
    plt.grid(True)

    # Graph anzeigen
    plt.show()
