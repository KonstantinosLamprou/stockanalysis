# Funktionabfolge kann in dem Notebook nachvollzogen werden 
import data_loader as dl
import preprocessing as pp 
import evaluation as ev
import models.baselines as mb
import models.optimized as mo
import feature_engineering as fe
  
def main():
    # Daten laden 
    ticker_symbol = "GOOGL"
    df = dl.load_stock_data(ticker_symbol)

    # Daten bereinigen
    df_clean = pp.clean_data(df, ticker_symbol)

    df_featured = fe.create_features(df_clean)

    # Daten splitten
    train_data, test_data = pp.split_data(df_featured)

    features = [
        'Close', 'Volume', 'Return_Today', 
        'Return_Lag_1', 'Return_Lag_2', 'Return_Lag_3', 
        'SMA_10', 'SMA_50', 
        'Volatility_20', 'RSI_14'
    ]
    
    # Modelltraining und -bewertung können hier hinzugefügt werden
    # model = mb.train_linear_regression_model(train_data[features], train_data['Target'])
    # model = mo.train_random_forest_model(train_data[features], train_data['Target'])
    model = mo.train_gradient_boosting_model(train_data[features], train_data['Target'])

    predictions = ev.evaluate_model(model, test_data[features])

    ev.evaluate_model_performance(test_data['Target'], predictions)
    
    ev.plot_predictions(test_data.index, test_data['Target'], predictions)
  
if __name__ == "__main__":
    main()