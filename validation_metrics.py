# validation_metrics.py

"""
Moduł do zaawansowanej walidacji modeli:
- Walk-forward testing (realistyczna symulacja czasowa)
- Metryki: RMSE, MAE, MAPE, Directional Accuracy
- Uncertainty intervals
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error


class ValidationMetrics:
    """Klasa do obliczania zaawansowanych metryk walidacji."""

    @staticmethod
    def calculate_rmse(y_true, y_pred):
        """Root Mean Squared Error."""
        return np.sqrt(mean_squared_error(y_true, y_pred))

    @staticmethod
    def calculate_mae(y_true, y_pred):
        """Mean Absolute Error."""
        return mean_absolute_error(y_true, y_pred)

    @staticmethod
    def calculate_mape(y_true, y_pred):
        """Mean Absolute Percentage Error."""
        # Unikamy dzielenia przez 0
        mask = y_true != 0
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

    @staticmethod
    def calculate_directional_accuracy(y_true, y_pred):
        """
        Dokładność kierunku ruchu ceny.
        Sprawdza, czy model prawidłowo przewiduje trend (wzrost/spadek).
        """
        if len(y_true) < 2 or len(y_pred) < 2:
            return 0.0

        # Kierunek rzeczywisty: porównanie ostatniej wartości z pierwszą
        real_direction = np.sign(y_true[-1] - y_true[0])
        pred_direction = np.sign(y_pred[-1] - y_pred[0])

        return 1.0 if real_direction == pred_direction else 0.0

    @staticmethod
    def calculate_all_metrics(y_true, y_pred):
        """Oblicz wszystkie metryki dla zbioru."""
        return {
            "RMSE": ValidationMetrics.calculate_rmse(y_true, y_pred),
            "MAE": ValidationMetrics.calculate_mae(y_true, y_pred),
            "MAPE": ValidationMetrics.calculate_mape(y_true, y_pred),
            "Directional_Accuracy": ValidationMetrics.calculate_directional_accuracy(y_true, y_pred)
        }


class WalkForwardValidator:
    """
    Walk-Forward Testing: uwalniającą symulacja czasowa.
    1. Trenuj na okresie T
    2. Prognozuj na okreś T+1
    3. Przesunięcie okna i powtórzenie
    """

    def __init__(self, model_builder, scaler):
        """
        Args:
            model_builder: funkcja, która zwraca nowy model (bez treningu)
            scaler: fitted MinMaxScaler do transformacji danych
        """
        self.model_builder = model_builder
        self.scaler = scaler
        self.forecasts = []
        self.actuals = []

    def run_walk_forward(self, X_full, y_full, lookback, horizon, initial_train_size=0.7, 
                        step_size=1, epochs=5, verbose=False):
        """
        Wykonaj walk-forward testing.
        
        Args:
            X_full: wszystkie dane wejściowe (samples, timesteps, features)
            y_full: wszystkie dane wyjściowe (samples, horizon)
            initial_train_size: procent danych do treningu w pierwszym kroku
            step_size: ile próbek przesuwać okno
            epochs: liczba epok do treningu na każdym kroku
            verbose: wydruk logów
        
        Returns:
            dict z metrykami walk-forward
        """
        n_samples = len(X_full)
        initial_split = int(n_samples * initial_train_size)
        current_pos = initial_split

        step_count = 0

        while current_pos + horizon <= n_samples:
            if verbose:
                print(f"\n[Krok {step_count}] Pozycja: {current_pos}/{n_samples}")

            # Dane treningowe: od początu do current_pos
            X_train = X_full[:current_pos]
            y_train = y_full[:current_pos]

            # Dane testowe: następne horizon próbek
            X_test = X_full[current_pos:current_pos + 1]
            y_test = y_full[current_pos:current_pos + 1]

            # Zbuduj i wytrenuj nowy model
            model = self.model_builder()
            model.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=0)

            # Prognoza
            y_pred = model.predict(X_test, verbose=0)

            self.forecasts.append(y_pred[0])
            self.actuals.append(y_test[0])

            if verbose:
                print(f"  Prognoza: {y_pred[0]}, Rzeczywisty: {y_test[0]}")

            current_pos += step_size
            step_count += 1

        # Oblicz metryki
        self.forecasts = np.array(self.forecasts)
        self.actuals = np.array(self.actuals)

        metrics = ValidationMetrics.calculate_all_metrics(self.actuals, self.forecasts)

        if verbose:
            print(f"\n✅ Walk-Forward Testing zakończony ({step_count} kroków)")
            print(f"   RMSE: {metrics['RMSE']:.6f}")
            print(f"   MAE:  {metrics['MAE']:.6f}")
            print(f"   MAPE: {metrics['MAPE']:.2f}%")
            print(f"   Directional Accuracy: {metrics['Directional_Accuracy']*100:.1f}%")

        return {
            "metrics": metrics,
            "steps": step_count,
            "forecasts": self.forecasts,
            "actuals": self.actuals
        }

    def get_results_dataframe(self):
        """Zwróć wyniki jako DataFrame."""
        return pd.DataFrame({
            "actual": self.actuals.flatten(),
            "forecast": self.forecasts.flatten(),
            "error": self.actuals.flatten() - self.forecasts.flatten()
        })


class UncertaintyIntervals:
    """Obliczanie przedziałów ufności dla prognoz."""

    @staticmethod
    def calculate_prediction_intervals(predictions, errors, confidence=0.95):
        """
        Oblicz górne i dolne przedziały ufności.
        
        Args:
            predictions: prognozowane wartości
            errors: błędy historyczne (actual - predicted)
            confidence: poziom ufności (0.95 = 95%)
        
        Returns:
            tuple (lower_bound, upper_bound)
        """
        std_error = np.std(errors)
        # Przybliżenie z-score dla 95% przedziału ufności
        z_score = 1.96 if confidence == 0.95 else 1.645  # dla 90%
        
        margin = z_score * std_error
        
        lower_bound = predictions - margin
        upper_bound = predictions + margin
        
        return lower_bound, upper_bound

    @staticmethod
    def calculate_interval_coverage(y_true, lower, upper):
        """Odsetek rzeczywistych wartości wpadających w przedział."""
        covered = np.sum((y_true >= lower) & (y_true <= upper))
        return covered / len(y_true) * 100
