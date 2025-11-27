# model_comparison.py

"""
Moduł do porównania różnych architektur neuronowych:
- LSTM (2 warstwy)
- GRU (2 warstwy)
- Hybrid LSTM+GRU
- Simple Dense model (baseline)
"""

import numpy as np
import pandas as pd
import datetime as dt
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout
from tensorflow.keras.optimizers import Adam


class ModelComparator:
    """Klasa do tworzenia, trenowania i porównywania modeli."""

    def __init__(self, lookback, horizon):
        self.lookback = lookback
        self.horizon = horizon
        self.results = {}

    def build_lstm_model(self):
        """Standard LSTM z 2 warstwami."""
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(self.lookback, 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(self.horizon))
        model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")
        return model

    def build_gru_model(self):
        """GRU (Gated Recurrent Unit) – szybszy niż LSTM."""
        model = Sequential()
        model.add(GRU(50, return_sequences=True, input_shape=(self.lookback, 1)))
        model.add(Dropout(0.2))
        model.add(GRU(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(self.horizon))
        model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")
        return model

    def build_hybrid_model(self):
        """Hybryda LSTM + GRU."""
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(self.lookback, 1)))
        model.add(Dropout(0.2))
        model.add(GRU(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(self.horizon))
        model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")
        return model

    def build_dense_baseline(self):
        """Prosty model Dense (baseline dla porównania)."""
        model = Sequential()
        model.add(Dense(64, activation='relu', input_shape=(self.lookback,)))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(self.horizon))
        model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")
        return model

    def train_model(self, model, X_train, y_train, epochs=20, batch_size=32, verbose=0):
        """Trenuj model i zwróć historię treningu."""
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=verbose
        )
        return history

    def evaluate_model(self, model, X_test, y_test, model_name):
        """Ewaluuj model i oblicz metryki."""
        y_pred = model.predict(X_test, verbose=0)

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        
        # MAPE – średni procentowy błąd absolutny
        # (wymaga zmiany jednostek z wartości znormalizowanych)
        try:
            mape = mean_absolute_percentage_error(y_test, y_pred)
        except:
            mape = np.nan

        self.results[model_name] = {
            "RMSE": rmse,
            "MAE": mae,
            "MAPE": mape,
            "MSE": mse
        }

        return {"RMSE": rmse, "MAE": mae, "MAPE": mape}

    def compare_all_models(self, X_train, y_train, X_test, y_test, epochs=20, verbose=False):
        """Porównaj wszystkie 4 modele."""
        models_to_test = {
            "LSTM (2-warstwy)": self.build_lstm_model(),
            "GRU (2-warstwy)": self.build_gru_model(),
            "LSTM+GRU (hybrid)": self.build_hybrid_model(),
            "Dense (baseline)": self.build_dense_baseline()
        }

        results_summary = {}

        for model_name, model in models_to_test.items():
            print(f"\n🔄 Trenuję {model_name}...")
            self.train_model(model, X_train, y_train, epochs=epochs, verbose=(1 if verbose else 0))
            
            metrics = self.evaluate_model(model, X_test, y_test, model_name)
            results_summary[model_name] = metrics
            
            print(f"   ✅ {model_name}")
            print(f"      RMSE: {metrics['RMSE']:.6f}")
            print(f"      MAE:  {metrics['MAE']:.6f}")
            print(f"      MAPE: {metrics['MAPE']:.4f}%")

        return results_summary

    def get_results_dataframe(self):
        """Zwróć wyniki jako DataFrame."""
        df = pd.DataFrame(self.results).T
        return df.sort_values("RMSE", ascending=True)

    def save_comparison_report(self, filepath):
        """Zapisz raport porównania do CSV."""
        df = self.get_results_dataframe()
        df.to_csv(filepath)
        print(f"📊 Raport porównania modeli zapisany do: {filepath}")
        return df


# Funkcja pomocnicza do reshapowania dla Dense modelu
def reshape_for_dense(X):
    """Flatten sekwencje do formatu (samples, features) dla Dense modelu."""
    return X.reshape(X.shape[0], -1)
