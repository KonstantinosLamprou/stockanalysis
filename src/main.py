# Funktionabfolge kann in dem Notebook nachvollzogen werden 
import data_loader as dl
import preprocessing as pp 
import evaluation as ev
import models.baselines as mb
  
def main():
    # Daten laden 
    ticker_symbol = "GOOGL"
    df = dl.load_stock_data(ticker_symbol)

    # Daten bereinigen
    df_clean = pp.clean_data(df, ticker_symbol)

    # Daten splitten
    train_data, test_data = pp.split_data(df_clean)

    # Modelltraining und -bewertung können hier hinzugefügt werden
    model = mb.train_linear_regression_model(train_data[['Close']], train_data['Target'])

    predictions = ev.evaluate_model(model, test_data[['Close']])

    # ev.evaluate_model_performance(test_data['Target'], predictions)
    
    ev.plot_predictions(test_data.index, test_data['Target'], predictions)
  
if __name__ == "__main__":
    main()