from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

def train_random_forest_model(X_train, y_train):
    """
    Trainiert einen Random Forest Regressor.
    """
    print("Trainiere Random Forest Modell...")
    
    # Wir instanziieren das Modell mit ein paar Standard-Parametern
    # n_estimators = Anzahl der Bäume im "Wald"
    # max_depth = Wie tief die Bäume verschachtelt sein dürfen (schützt vor Auswendiglernen)
    # random_state = 42 (Eine feste Seed, damit bei jedem Durchlauf dasselbe Ergebnis rauskommt)
    model = RandomForestRegressor(
        n_estimators=100, 
        max_depth=5, 
        random_state=42
    )
    
    # Das Interface ist exakt dasselbe wie bei der Linearen Regression!
    model.fit(X_train, y_train)
    
    return model

def train_gradient_boosting_model(X_train, y_train):
    """
    Trainiert einen Gradient Boosting Regressor.
    """
    print("Trainiere Gradient Boosting Modell...")
    
    # learning_rate: Bestimmt, wie stark jeder einzelne Baum den Fehler korrigieren darf. 
    # Ein kleinerer Wert macht das Modell robuster, braucht aber mehr Bäume (n_estimators).
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3, 
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    return model