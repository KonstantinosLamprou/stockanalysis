# Funktionabfolge kann in dem Notebook nachvollzogen werden 
import data_loader as dl
import preprocessing as pp 
  
def main():
    # Daten laden 
    ticker_symbol = "GOOGL"
    df = dl.load_stock_data(ticker_symbol)

    # Daten bereinigen
    df_clean = pp.clean_data(df, ticker_symbol)

    # Daten splitten
    train_data, test_data = pp.split_data(df_clean)

    # Modelltraining und -bewertung können hier hinzugefügt werden




if __name__ == "__main__":
    main()