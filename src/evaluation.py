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
