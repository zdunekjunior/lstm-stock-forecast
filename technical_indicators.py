# technical_indicators.py

"""
Moduł do obliczania wskaźników technicznych:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Moving Averages (SMA, EMA)
- Bollinger Bands
- ATR (Average True Range)
"""

import numpy as np
import pandas as pd


class TechnicalIndicators:
    """Klasa do obliczania wskaźników technicznych."""

    @staticmethod
    def calculate_rsi(prices, period=14):
        """
        Relative Strength Index.
        RSI mierzy siłę i kierunek zmiany ceny.
        Zakresy: < 30 (oversold), > 70 (overbought)
        """
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = 100.0 - 100.0 / (1.0 + rs)
        
        rsi_values = np.zeros_like(prices)
        rsi_values[:period] = rsi
        
        for i in range(period, len(prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.0
            else:
                upval = 0.0
                downval = -delta
            
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            
            rs = up / down if down != 0 else 0
            rsi_values[i] = 100.0 - 100.0 / (1.0 + rs)
        
        return rsi_values

    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """
        MACD (Moving Average Convergence Divergence).
        Returns: (macd_line, signal_line, histogram)
        """
        # EMA
        ema_fast = pd.Series(prices).ewm(span=fast).mean().values
        ema_slow = pd.Series(prices).ewm(span=slow).mean().values
        
        macd_line = ema_fast - ema_slow
        signal_line = pd.Series(macd_line).ewm(span=signal).mean().values
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_sma(prices, period=20):
        """Simple Moving Average."""
        return pd.Series(prices).rolling(window=period).mean().values

    @staticmethod
    def calculate_ema(prices, period=20):
        """Exponential Moving Average."""
        return pd.Series(prices).ewm(span=period).mean().values

    @staticmethod
    def calculate_bollinger_bands(prices, period=20, num_std=2):
        """
        Bollinger Bands.
        Returns: (upper_band, middle_band, lower_band)
        """
        sma = TechnicalIndicators.calculate_sma(prices, period)
        std = pd.Series(prices).rolling(window=period).std().values
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return upper_band, sma, lower_band

    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Average True Range – mierzy zmienność."""
        tr = np.maximum(
            np.maximum(high - low, np.abs(high - np.roll(close, 1))),
            np.abs(low - np.roll(close, 1))
        )
        atr = pd.Series(tr).rolling(window=period).mean().values
        return atr

    @staticmethod
    def calculate_stochastic(prices, period=14, smooth_k=3, smooth_d=3):
        """
        Stochastic Oscillator.
        Returns: (%K, %D)
        """
        lowest = pd.Series(prices).rolling(window=period).min().values
        highest = pd.Series(prices).rolling(window=period).max().values
        
        k_raw = 100 * (prices - lowest) / (highest - lowest + 1e-10)
        k = pd.Series(k_raw).rolling(window=smooth_k).mean().values
        d = pd.Series(k).rolling(window=smooth_d).mean().values
        
        return k, d


class FeatureEngineer:
    """Klasa do tworzenia features do modelu ML."""

    @staticmethod
    def add_technical_indicators(df, add_rsi=True, add_macd=True, add_bollinger=True, add_atr=False):
        """
        Dodaj wskaźniki techniczne do DataFrame.
        
        Args:
            df: DataFrame z kolumną 'Close'
            add_rsi: dodaj RSI
            add_macd: dodaj MACD
            add_bollinger: dodaj Bollinger Bands
            add_atr: dodaj ATR (wymaga High/Low)
        
        Returns:
            DataFrame z nowymi kolumnami
        """
        df_feat = df.copy()
        
        if add_rsi:
            df_feat['RSI'] = TechnicalIndicators.calculate_rsi(df_feat['Close'].values, period=14)
        
        if add_macd:
            macd, signal, hist = TechnicalIndicators.calculate_macd(df_feat['Close'].values)
            df_feat['MACD'] = macd
            df_feat['MACD_Signal'] = signal
            df_feat['MACD_Hist'] = hist
        
        if add_bollinger:
            upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
                df_feat['Close'].values, period=20
            )
            df_feat['BB_Upper'] = upper
            df_feat['BB_Middle'] = middle
            df_feat['BB_Lower'] = lower
            df_feat['BB_Width'] = upper - lower
        
        if add_atr and 'High' in df_feat.columns and 'Low' in df_feat.columns:
            df_feat['ATR'] = TechnicalIndicators.calculate_atr(
                df_feat['High'].values,
                df_feat['Low'].values,
                df_feat['Close'].values
            )
        
        return df_feat.dropna()

    @staticmethod
    def normalize_features(df, columns):
        """Normalizuj wybranie kolumny (0-1)."""
        from sklearn.preprocessing import MinMaxScaler
        
        scaler = MinMaxScaler()
        df_norm = df.copy()
        df_norm[columns] = scaler.fit_transform(df[columns])
        
        return df_norm, scaler

    @staticmethod
    def create_features_for_lstm(df, lookback, feature_columns):
        """
        Utwórz sekwencje z wieloma features.
        
        Args:
            df: DataFrame z feature columns
            lookback: długość sekwencji
            feature_columns: lista kolumn do użycia
        
        Returns:
            (X, y) gdzie X shape jest (samples, lookback, num_features)
        """
        data = df[feature_columns].values  # (N, num_features)
        X = []
        y = []
        
        # Używamy tylko Close jako target (ostatnia kolumna to Close)
        close_idx = feature_columns.index('Close') if 'Close' in feature_columns else 0
        
        for i in range(lookback, len(data)):
            X.append(data[i - lookback:i])  # (lookback, num_features)
            y.append(data[i, close_idx])     # próby Close dla tego dnia
        
        return np.array(X), np.array(y)
