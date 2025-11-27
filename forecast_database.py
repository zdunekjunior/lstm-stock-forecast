# forecast_database.py

"""
Moduł do zarządzania bazą danych prognoz.
Przechowuje historię wszystkich prognoz w SQLite.
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
import os


class ForecastDatabase:
    """Zarządzanie bazą danych prognoz SQLite."""
    
    def __init__(self, db_path="forecast_history.db"):
        """Inicjalizuj bazę danych."""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Utwórz tabele jeśli nie istnieją."""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Tabela prognoz
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                forecast_date DATE NOT NULL,
                days_ahead INTEGER NOT NULL,
                model_type TEXT DEFAULT 'LSTM',
                lookback INTEGER,
                horizon INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela szczegółów prognoz
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecast_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_id INTEGER NOT NULL,
                day_offset INTEGER NOT NULL,
                predicted_price REAL NOT NULL,
                lower_bound REAL,
                upper_bound REAL,
                FOREIGN KEY (forecast_id) REFERENCES forecasts(id)
            )
        ''')
        
        # Tabela backtest wyników
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                forecast_date DATE NOT NULL,
                actual_price REAL NOT NULL,
                predicted_price REAL NOT NULL,
                error REAL NOT NULL,
                abs_pct_error REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela metryk modeli
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                model_type TEXT NOT NULL,
                rmse REAL,
                mae REAL,
                mape REAL,
                directional_accuracy REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_forecast(self, ticker, days_ahead, forecast_prices, lower_bounds=None, upper_bounds=None,
                    model_type="LSTM", lookback=60, horizon=5):
        """
        Dodaj nową prognozę do bazy danych.
        
        Args:
            ticker: symbol akcji
            days_ahead: liczba dni prognozy
            forecast_prices: lista prognozowanych cen
            lower_bounds: lista dolnych przedziałów ufności (opcjonalnie)
            upper_bounds: lista górnych przedziałów ufności (opcjonalnie)
            model_type: typ modelu (LSTM, GRU, etc.)
            lookback: liczba dni wstecz (parametr modelu)
            horizon: liczba dni naprzód (parametr modelu)
        
        Returns:
            ID dodanej prognozy
        """
        cursor = self.conn.cursor()
        forecast_date = date.today()
        
        # Dodaj prognozę
        cursor.execute('''
            INSERT INTO forecasts (ticker, forecast_date, days_ahead, model_type, lookback, horizon)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, forecast_date, days_ahead, model_type, lookback, horizon))
        
        forecast_id = cursor.lastrowid
        
        # Dodaj szczegóły
        if lower_bounds is None:
            lower_bounds = [None] * len(forecast_prices)
        if upper_bounds is None:
            upper_bounds = [None] * len(forecast_prices)
        
        for i, (price, lower, upper) in enumerate(zip(forecast_prices, lower_bounds, upper_bounds), start=1):
            cursor.execute('''
                INSERT INTO forecast_details (forecast_id, day_offset, predicted_price, lower_bound, upper_bound)
                VALUES (?, ?, ?, ?, ?)
            ''', (forecast_id, i, price, lower, upper))
        
        self.conn.commit()
        return forecast_id
    
    def add_backtest_result(self, ticker, actual_price, predicted_price, error, abs_pct_error):
        """Dodaj wynik backtestu."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO backtest_results (ticker, forecast_date, actual_price, predicted_price, error, abs_pct_error)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, date.today(), actual_price, predicted_price, error, abs_pct_error))
        self.conn.commit()
    
    def add_model_metrics(self, ticker, model_type, rmse, mae, mape, directional_accuracy):
        """Dodaj metryki modelu."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO model_metrics (ticker, model_type, rmse, mae, mape, directional_accuracy)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, model_type, rmse, mae, mape, directional_accuracy))
        self.conn.commit()
    
    def get_forecast_history(self, ticker, limit=10):
        """Pobierz historię prognoz dla tickera."""
        query = '''
            SELECT id, ticker, forecast_date, days_ahead, model_type, created_at
            FROM forecasts
            WHERE ticker = ?
            ORDER BY created_at DESC
            LIMIT ?
        '''
        df = pd.read_sql_query(query, self.conn, params=(ticker, limit))
        return df
    
    def get_forecast_details(self, forecast_id):
        """Pobierz szczegóły prognozy."""
        query = '''
            SELECT day_offset, predicted_price, lower_bound, upper_bound
            FROM forecast_details
            WHERE forecast_id = ?
            ORDER BY day_offset
        '''
        df = pd.read_sql_query(query, self.conn, params=(forecast_id,))
        return df
    
    def get_backtest_stats(self, ticker):
        """Pobierz statystyki backtestu dla tickera."""
        query = '''
            SELECT 
                COUNT(*) as total_tests,
                AVG(abs_pct_error) as avg_error,
                MIN(abs_pct_error) as best_error,
                MAX(abs_pct_error) as worst_error
            FROM backtest_results
            WHERE ticker = ?
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (ticker,))
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            return {
                "total_tests": result[0],
                "avg_error": result[1],
                "best_error": result[2],
                "worst_error": result[3]
            }
        return None
    
    def get_model_performance(self, model_type=None):
        """Pobierz wydajność modeli."""
        if model_type:
            query = '''
                SELECT ticker, model_type, rmse, mae, mape, directional_accuracy, created_at
                FROM model_metrics
                WHERE model_type = ?
                ORDER BY created_at DESC
            '''
            df = pd.read_sql_query(query, self.conn, params=(model_type,))
        else:
            query = '''
                SELECT ticker, model_type, rmse, mae, mape, directional_accuracy, created_at
                FROM model_metrics
                ORDER BY created_at DESC
            '''
            df = pd.read_sql_query(query, self.conn)
        
        return df
    
    def get_trend_analysis(self, ticker, days=30):
        """Analiza trendu – porównaj średnie metryki z ostatnich N dni."""
        query = '''
            SELECT 
                strftime('%Y-%m-%d', forecast_date) as date,
                COUNT(*) as forecast_count,
                ROUND(AVG(CAST((SELECT ABS_PCT_ERROR FROM backtest_results 
                               WHERE ticker = ? LIMIT 1) AS FLOAT)), 2) as avg_error
            FROM forecasts
            WHERE ticker = ? AND forecast_date >= date('now', '-' || ? || ' days')
            GROUP BY strftime('%Y-%m-%d', forecast_date)
            ORDER BY date DESC
        '''
        df = pd.read_sql_query(query, self.conn, params=(ticker, ticker, days))
        return df
    
    def export_to_csv(self, ticker, output_path):
        """Eksportuj historię prognoz do CSV."""
        df = self.get_forecast_history(ticker, limit=1000)
        df.to_csv(output_path, index=False)
        print(f"📄 Historia prognoz eksportowana do: {output_path}")
    
    def close(self):
        """Zamknij połączenie z bazą danych."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ForecastAnalyzer:
    """Analiza prognoz z bazy danych."""
    
    def __init__(self, db_path="forecast_history.db"):
        self.db = ForecastDatabase(db_path)
    
    def get_forecast_accuracy_by_days(self, ticker):
        """Analiza dokładności w zależności od liczby dni do przodu."""
        query = '''
            SELECT 
                f.days_ahead,
                COUNT(*) as count,
                ROUND(AVG(b.abs_pct_error), 2) as avg_error
            FROM forecasts f
            LEFT JOIN backtest_results b ON b.ticker = f.ticker
            WHERE f.ticker = ?
            GROUP BY f.days_ahead
            ORDER BY f.days_ahead
        '''
        df = pd.read_sql_query(query, self.db.conn, params=(ticker,))
        return df
    
    def compare_models_performance(self, ticker):
        """Porównaj wydajność różnych modeli."""
        query = '''
            SELECT 
                model_type,
                COUNT(*) as count,
                ROUND(AVG(rmse), 6) as avg_rmse,
                ROUND(AVG(mae), 6) as avg_mae,
                ROUND(AVG(mape), 2) as avg_mape,
                ROUND(AVG(directional_accuracy), 3) as avg_directional_acc
            FROM model_metrics
            WHERE ticker = ?
            GROUP BY model_type
            ORDER BY avg_rmse ASC
        '''
        df = pd.read_sql_query(query, self.db.conn, params=(ticker,))
        return df
    
    def get_recent_forecast_summary(self, ticker, days=7):
        """Podsumowanie ostatnich prognoz."""
        query = '''
            SELECT 
                DATE(forecast_date) as date,
                COUNT(*) as num_forecasts,
                ROUND(AVG(days_ahead), 1) as avg_days_ahead
            FROM forecasts
            WHERE ticker = ? AND forecast_date >= DATE('now', '-' || ? || ' days')
            GROUP BY DATE(forecast_date)
            ORDER BY date DESC
        '''
        df = pd.read_sql_query(query, self.db.conn, params=(ticker, days))
        return df
    
    def close(self):
        self.db.close()
