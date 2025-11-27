# gielda_lstm_gui.py

import datetime as dt
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
import pandas as pd
import yfinance as yf
import joblib
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler

# Nowoczesny UI theme
try:
    from modern_ui_theme import ModernTheme, ModernUIHelper, IconSet, ColorPalette
    UI_MODERN = True
except ImportError:
    UI_MODERN = False

# TensorFlow - importuj później jeśli potrzebny
try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    Sequential = load_model = LSTM = Dense = Dropout = None

# Importy z nowych modułów - OPCJONALNE (mogą być niedostępne)
try:
    from model_comparison import ModelComparator, reshape_for_dense
    ModelComparator_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    ModelComparator = None
    ModelComparator_AVAILABLE = False

try:
    from validation_metrics import ValidationMetrics, WalkForwardValidator, UncertaintyIntervals
    ValidationMetrics_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    ValidationMetrics = WalkForwardValidator = UncertaintyIntervals = None
    ValidationMetrics_AVAILABLE = False

try:
    from technical_indicators import TechnicalIndicators, FeatureEngineer
    TechnicalIndicators_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    TechnicalIndicators = FeatureEngineer = None
    TechnicalIndicators_AVAILABLE = False

try:
    from forecast_database import ForecastDatabase, ForecastAnalyzer
    ForecastDatabase_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    ForecastDatabase = ForecastAnalyzer = None
    ForecastDatabase_AVAILABLE = False

try:
    from advanced_visualization import AdvancedVisualizer, PDFExporter
    AdvancedVisualizer_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    AdvancedVisualizer = PDFExporter = None
    AdvancedVisualizer_AVAILABLE = False


# =============== LOGOWANIE DO OKNA ===============
root = None
output_text = None
current_theme = {}

entry_ticker = None
entry_lookback = None
entry_horizon = None
entry_epochs = None
entry_alert_high = None
entry_alert_low = None


def log(msg: str, level="info"):
    """Wypisuje tekst do pola tekstowego i do konsoli."""
    # Format wiadomości z emoji
    if UI_MODERN:
        formatted_msg = ModernUIHelper.format_log_message(msg, level)
    else:
        formatted_msg = msg
    
    print(formatted_msg)
    if output_text is not None:
        output_text.insert(tk.END, formatted_msg + "\n")
        output_text.see(tk.END)
        output_text.update_idletasks()


# =============== FUNKCJE POMOCNICZE ===============
def create_sequences_multi(dataset, lookback, horizon):
    """
    Tworzy sekwencje dla wielodniowej predykcji:
    X: sekwencje o długości lookback
    y: wektor długości horizon (kolejne dni)
    """
    X, y = [], []
    for i in range(lookback, len(dataset) - horizon + 1):
        X.append(dataset[i - lookback:i, 0])        # wejście: lookback dni
        y.append(dataset[i:i + horizon, 0])         # wyjście: horizon dni naprzód
    X = np.array(X)
    y = np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # (samples, timesteps, features)
    return X, y


def get_file_paths(ticker, lookback, horizon):
    ticker_clean = ticker.upper().replace(".", "_")
    model_path = f"model_{ticker_clean}_L{lookback}_H{horizon}.keras"
    scaler_path = f"scaler_{ticker_clean}_L{lookback}_H{horizon}.pkl"
    return model_path, scaler_path


# =============== TRENING MODELU ===============
def train_model(ticker, lookback=60, horizon=5, epochs=20, batch_size=32):
    try:
        if not TF_AVAILABLE:
            log("❌ TensorFlow nie załadowany. Sprawdź instalację.")
            log("Uruchom: pip install tensorflow")
            messagebox.showerror("Błąd", "TensorFlow nie jest zainstalowany.")
            return
            
        log(f"\n[1/5] Pobieram dane z Yahoo Finance dla {ticker} (ostatnie 5 lat)...")
        end = dt.date.today()
        start = end - dt.timedelta(days=5 * 365)

        df = yf.download(ticker, start=start, end=end)

        if df.empty:
            log("❌ Brak danych. Sprawdź symbol (np. AAPL, MSFT, PKN.WA, ^GSPC).")
            messagebox.showerror("Błąd", "Brak danych z Yahoo Finance dla podanego tickera.")
            return

        df = df.reset_index()
        df = df[["Date", "Close"]].dropna()

        log("[2/5] Przygotowuję dane...")
        data = df[["Close"]].values  # (N, 1)

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        TEST_SIZE = 0.2
        train_size = int((1 - TEST_SIZE) * len(scaled_data))
        train_data = scaled_data[:train_size]
        test_data = scaled_data[train_size - lookback:]

        X_train, y_train = create_sequences_multi(train_data, lookback, horizon)
        X_test, y_test = create_sequences_multi(test_data, lookback, horizon)

        log(f"X_train shape: {X_train.shape}")
        log(f"y_train shape: {y_train.shape}")
        log(f"X_test shape : {X_test.shape}")
        log(f"y_test shape : {y_test.shape}")

        log("[3/5] Buduję model LSTM...")
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(lookback, 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(horizon))  # tyle dni do przodu

        model.compile(optimizer="adam", loss="mean_squared_error")

        log("[4/5] Trenuję model (to może chwilę potrwać)...")
        model.fit(
            X_train,
            y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=1
        )

        model_path, scaler_path = get_file_paths(ticker, lookback, horizon)

        log("[5/5] Zapisuję model i scaler...")
        model.save(model_path)
        joblib.dump(scaler, scaler_path)

        log("\n✅ Zakończono trening.")
        log(f"Model zapisany jako:  {model_path}")
        log(f"Scaler zapisany jako: {scaler_path}")
        messagebox.showinfo("Sukces", "Trening zakończony i zapisany.")
    except Exception as e:
        log(f"❌ Błąd podczas treningu: {e}")
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas treningu:\n{e}")


# =============== PROGNOZA Z ZAPISANEGO MODELU ===============
def predict_future(ticker, lookback=60, horizon=5, alert_high=None, alert_low=None):
    try:
        model_path, scaler_path = get_file_paths(ticker, lookback, horizon)

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            log("\n❌ Nie znaleziono modelu lub scalera dla tych parametrów.")
            log(f"Szukane pliki: {model_path}, {scaler_path}")
            messagebox.showwarning(
                "Brak modelu",
                "Nie znaleziono modelu dla tych ustawień.\n"
                "Najpierw uruchom trening z tym samym tickerem / LOOKBACK / HORIZON."
            )
            return

        log(f"\n[1/4] Wczytuję model i scaler dla {ticker}...")
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)

        log("[2/4] Pobieram najnowsze dane z Yahoo Finance...")
        end = dt.date.today()
        start = end - dt.timedelta(days=365 * 2)  # ostatnie 2 lata

        df = yf.download(ticker, start=start, end=end).reset_index()
        if df.empty:
            log("❌ Brak danych. Sprawdź symbol.")
            messagebox.showerror("Błąd", "Brak danych z Yahoo Finance dla podanego tickera.")
            return

        df = df[["Date", "Close"]].dropna()
        data = df[["Close"]].values
        scaled_data = scaler.transform(data)

        if len(scaled_data) < lookback:
            log("❌ Za mało danych, żeby zbudować sekwencję wejściową.")
            messagebox.showerror("Błąd", "Za mało danych do prognozy.")
            return

        last_seq = scaled_data[-lookback:]
        last_seq = last_seq.reshape(1, lookback, 1)

        log("[3/4] Liczę prognozę...")
        pred_scaled = model.predict(last_seq)  # (1, horizon)
        pred_scaled = pred_scaled.reshape(-1, 1)
        pred_prices = scaler.inverse_transform(pred_scaled).flatten()

        log(f"\n📈 Prognoza na kolejne {len(pred_prices)} dni dla {ticker.upper()}:")
        for i, price in enumerate(pred_prices, start=1):
            log(f"D+{i}: {price:.2f}")

        # ======== UNCERTAINTY INTERVALS =========
        try:
            # Dla uncertainty intervals: używamy ostatnich 30 dni jako proxy na błędy
            last_30_prices = data[-min(30, len(data)):]
            recent_errors = np.diff(last_30_prices).flatten()
            # Jeśli mamy bardzo mało danych, używamy średniej z pełnych danych
            if len(recent_errors) < 5:
                recent_errors = np.random.normal(0, np.std(data) * 0.01, 30)
            
            lower_interval, upper_interval = UncertaintyIntervals.calculate_prediction_intervals(
                pred_prices, recent_errors, confidence=0.95
            )
            
            log(f"\n🎯 Przedziały ufności (95%):")
            for i, (price, lower, upper) in enumerate(zip(pred_prices, lower_interval, upper_interval), start=1):
                log(f"D+{i}: {price:.2f} [{lower:.2f}, {upper:.2f}]")
        except Exception as e_interval:
            log(f"⚠️ Nie udało się obliczyć przedziałów ufności: {e_interval}")

        # ======== ALERT NA OSTATNI DZIEŃ (D+HORYZONT) =========
        last_day_index = len(pred_prices)  # np. 5 przy horyzoncie 5
        last_day_price = pred_prices[-1]

        if alert_high is not None and last_day_price > alert_high:
            msg = (f"🔔 ALERT: prognoza D+{last_day_index} "
                   f"({last_day_price:.2f}) jest POWYŻEJ progu {alert_high:.2f}")
            log(msg)
            messagebox.showinfo("Alert – próg górny przekroczony", msg)

        if alert_low is not None and last_day_price < alert_low:
            msg = (f"🔔 ALERT: prognoza D+{last_day_index} "
                   f"({last_day_price:.2f}) jest PONIŻEJ progu {alert_low:.2f}")
            log(msg)
            messagebox.showinfo("Alert – próg dolny przekroczony", msg)

        # ======== WYLICZENIE DAT PRZYSZŁYCH =========
        last_n = min(100, len(df))
        hist_dates = df["Date"].values[-last_n:]
        hist_prices = df["Close"].values[-last_n:]

        start_future = df["Date"].iloc[-1] + pd.Timedelta(days=1)
        future_dates = pd.date_range(start_future, periods=len(pred_prices))

        # ======== ZAPIS PROGNOZY DO CSV =========
        try:
            output_dir_csv = os.path.join(os.path.dirname(__file__), "prognozy")
            os.makedirs(output_dir_csv, exist_ok=True)

            now = dt.datetime.now()
            now_str = now.strftime("%Y%m%d_%H%M%S")
            today_str = dt.date.today().isoformat()

            filename_csv = f"{ticker.upper()}_{today_str}_{len(pred_prices)}dni_{now_str}.csv"
            filepath_csv = os.path.join(output_dir_csv, filename_csv)

            df_forecast = pd.DataFrame({
                "ticker": [ticker.upper()] * len(pred_prices),
                "date": future_dates,
                "day_offset": list(range(1, len(pred_prices) + 1)),
                "forecast": pred_prices
            })

            df_forecast.to_csv(filepath_csv, index=False)
            log(f"📄 Prognoza zapisana do CSV: {filepath_csv}")
        except Exception as e_csv:
            log(f"⚠️ Nie udało się zapisać prognozy do CSV: {e_csv}")
        
        # ======== ZAPIS DO BAZY DANYCH =========
        try:
            if ForecastDatabase is not None:
                db_path = os.path.join(os.path.dirname(__file__), "forecast_history.db")
                with ForecastDatabase(db_path) as db:
                    # Przygotuj dane dla bazy
                    forecast_prices_list = pred_prices.tolist()
                    try:
                        lower_list = lower_interval.tolist()
                        upper_list = upper_interval.tolist()
                    except:
                        lower_list = None
                        upper_list = None
                    
                    forecast_id = db.add_forecast(
                        ticker=ticker.upper(),
                        days_ahead=len(pred_prices),
                        forecast_prices=forecast_prices_list,
                        lower_bounds=lower_list,
                        upper_bounds=upper_list,
                        model_type="LSTM",
                        lookback=lookback,
                        horizon=horizon
                    )
                    log(f"💾 Prognoza zapisana w bazie danych (ID: {forecast_id})")
            else:
                log("⚠️ Moduł forecast_database niedostępny - baza danych nie wrzyta")
        except Exception as e_db:
            log(f"⚠️ Nie udało się zapisać prognozy w bazie danych: {e_db}")

        # ======== WYKRES + ZAPIS DO PLIKU PNG =========
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(hist_dates, hist_prices, label="Historia (Close)", color="blue", linewidth=2)
            plt.plot(future_dates, pred_prices, label="Prognoza", color="red", marker="o", linewidth=2)
            
            # Dodaj uncertainty intervals jeśli są dostępne
            try:
                plt.fill_between(future_dates, lower_interval, upper_interval, 
                               alpha=0.2, color="red", label="95% przedział ufności")
            except:
                pass

            plt.title(f"Prognoza kursu {ticker.upper()} na {len(pred_prices)} dni naprzód")
            plt.xlabel("Data")
            plt.ylabel("Cena")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            output_dir_png = os.path.join(os.path.dirname(__file__), "wykresy")
            os.makedirs(output_dir_png, exist_ok=True)

            today_str = dt.date.today().isoformat()
            filename_png = f"{ticker.upper()}_{today_str}_{len(pred_prices)}dni.png"
            filepath_png = os.path.join(output_dir_png, filename_png)

            plt.savefig(filepath_png, dpi=150)
            log(f"💾 Wykres zapisany jako: {filepath_png}")

            plt.show()
        except Exception as e_plot:
            log(f"⚠️ Nie udało się narysować lub zapisać wykresu: {e_plot}")

        messagebox.showinfo(
            "Prognoza gotowa",
            "Prognoza została policzona.\n"
            "Zapisano CSV (folder 'prognozy') i wykres (folder 'wykresy')."
        )
    except Exception as e:
        log(f"❌ Błąd podczas prognozy: {e}")
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas prognozy:\n{e}")


# =============== ANALIZA WSKAŹNIKÓW TECHNICZNYCH ===============
def analyze_technical_indicators(ticker):
    """Oblicz i wyświetl wskaźniki techniczne."""
    try:
        if TechnicalIndicators is None:
            log("❌ Moduł technical_indicators nie załadowany.")
            messagebox.showerror("Błąd", "Brak modułu technical_indicators.")
            return
            
        log(f"\n================ ANALIZA WSKAŹNIKÓW TECHNICZNYCH ================")
        log(f"Pobieranie danych dla {ticker}...")
        
        end = dt.date.today()
        start = end - dt.timedelta(days=365)  # ostatni rok
        
        df = yf.download(ticker, start=start, end=end).reset_index()
        if df.empty:
            log("❌ Brak danych.")
            return
        
        df = df[["Date", "Close"]].dropna()
        close_prices = df["Close"].values
        
        # Oblicz wskaźniki
        log("\nObliczam wskaźniki techniczne...")
        
        rsi = TechnicalIndicators.calculate_rsi(close_prices, period=14)
        macd, signal, hist = TechnicalIndicators.calculate_macd(close_prices)
        bb_upper, bb_mid, bb_lower = TechnicalIndicators.calculate_bollinger_bands(close_prices)
        sma20 = TechnicalIndicators.calculate_sma(close_prices, period=20)
        sma50 = TechnicalIndicators.calculate_sma(close_prices, period=50)
        
        # Ostatnie wartości
        last_close = close_prices[-1]
        last_rsi = rsi[-1]
        last_macd = macd[-1]
        last_sma20 = sma20[-1]
        last_sma50 = sma50[-1]
        
        log(f"\n📊 Bieżące wskaźniki dla {ticker.upper()}:")
        log(f"   Cena zamknięcia: {last_close:.2f}")
        log(f"   RSI(14): {last_rsi:.2f}", end="")
        if last_rsi < 30:
            log(" ⚠️ OVERSOLD")
        elif last_rsi > 70:
            log(" ⚠️ OVERBOUGHT")
        else:
            log(" (neutralny)")
        
        log(f"   MACD: {last_macd:.6f}")
        log(f"   SMA(20): {last_sma20:.2f}")
        log(f"   SMA(50): {last_sma50:.2f}")
        log(f"   Bollinger Bands: [{bb_lower[-1]:.2f}, {bb_upper[-1]:.2f}]")
        
        # Sygnały
        log(f"\n🎯 Sygnały techniczne:")
        if last_close > last_sma20 > last_sma50:
            log("   ✅ Trend wzrostu (Close > SMA20 > SMA50)")
        elif last_close < last_sma20 < last_sma50:
            log("   ⚠️ Trend spadku (Close < SMA20 < SMA50)")
        
        if last_rsi < 30:
            log("   ✅ Sygnał kupna: Oversold (RSI < 30)")
        elif last_rsi > 70:
            log("   ⚠️ Sygnał sprzedaży: Overbought (RSI > 70)")
        
        # Zapis do CSV
        try:
            output_dir = os.path.join(os.path.dirname(__file__), "wskazniki")
            os.makedirs(output_dir, exist_ok=True)
            
            df_ind = pd.DataFrame({
                "Date": df["Date"],
                "Close": close_prices,
                "RSI": rsi,
                "MACD": macd,
                "MACD_Signal": signal,
                "SMA20": sma20,
                "SMA50": sma50,
                "BB_Upper": bb_upper,
                "BB_Lower": bb_lower
            })
            
            today_str = dt.date.today().isoformat()
            filepath = os.path.join(output_dir, f"wskazniki_{ticker}_{today_str}.csv")
            df_ind.to_csv(filepath, index=False)
            log(f"\n📄 Wskaźniki zapisane do: {filepath}")
        except Exception as e_save:
            log(f"⚠️ Nie udało się zapisać wskaźników: {e_save}")
        
        messagebox.showinfo("Wskaźniki techniczne", 
                           f"RSI: {last_rsi:.2f}\nSMA20: {last_sma20:.2f}\nSMA50: {last_sma50:.2f}")
        
    except Exception as e:
        log(f"❌ Błąd podczas analizy wskaźników: {e}")
        messagebox.showerror("Błąd", f"Błąd: {e}")


# =============== PORÓWNANIE MODELI ===============
def compare_models_command(ticker, lookback=60, horizon=5, epochs=10):
    """Porównaj różne architektury modeli."""
    try:
        if ModelComparator is None:
            log("❌ Moduł model_comparison nie załadowany.")
            messagebox.showerror("Błąd", "Brak modułu model_comparison.")
            return
            
        log("\n================ PORÓWNANIE MODELI ================")
        log(f"Pobieranie danych dla {ticker}...")
        
        end = dt.date.today()
        start = end - dt.timedelta(days=5 * 365)
        
        df = yf.download(ticker, start=start, end=end)
        if df.empty:
            log("❌ Brak danych z Yahoo Finance.")
            messagebox.showerror("Błąd", "Brak danych dla podanego tickera.")
            return
        
        df = df.reset_index()
        df = df[["Date", "Close"]].dropna()
        data = df[["Close"]].values
        
        # Normalizacja
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        
        # Podział
        TEST_SIZE = 0.2
        train_size = int((1 - TEST_SIZE) * len(scaled_data))
        train_data = scaled_data[:train_size]
        test_data = scaled_data[train_size - lookback:]
        
        X_train, y_train = create_sequences_multi(train_data, lookback, horizon)
        X_test, y_test = create_sequences_multi(test_data, lookback, horizon)
        
        log(f"Dane przygotowane: X_train={X_train.shape}, X_test={X_test.shape}")
        
        # Porównanie modeli
        comparator = ModelComparator(lookback, horizon)
        results = comparator.compare_all_models(X_train, y_train, X_test, y_test, epochs=epochs)
        
        # Zapis raportu
        output_dir = os.path.join(os.path.dirname(__file__), "porownania")
        os.makedirs(output_dir, exist_ok=True)
        
        today_str = dt.date.today().isoformat()
        report_path = os.path.join(output_dir, f"porownanie_modeli_{ticker}_{today_str}.csv")
        
        df_results = comparator.get_results_dataframe()
        df_results.to_csv(report_path)
        
        log(f"\n✅ Raport porównania modeli:")
        log(df_results.to_string())
        log(f"📄 Zapisano do: {report_path}")
        
        messagebox.showinfo("Porównanie modeli", 
                           f"Porównanie ukończone.\nNajlepszy model: {df_results.index[0]}\n"
                           f"RMSE: {df_results.iloc[0]['RMSE']:.6f}")
        
    except Exception as e:
        log(f"❌ Błąd podczas porównania modeli: {e}")
        messagebox.showerror("Błąd", f"Błąd: {e}")


# =============== WALK-FORWARD TESTING ===============
def walk_forward_test(ticker, lookback=60, horizon=5, epochs=5):
    """Wykonaj walk-forward testing."""
    try:
        if WalkForwardValidator is None:
            log("❌ Moduł validation_metrics nie załadowany.")
            messagebox.showerror("Błąd", "Brak modułu validation_metrics.")
            return
            
        log("\n================ WALK-FORWARD TESTING ================")
        log(f"Pobieranie danych dla {ticker}...")
        
        end = dt.date.today()
        start = end - dt.timedelta(days=5 * 365)
        
        df = yf.download(ticker, start=start, end=end)
        if df.empty:
            log("❌ Brak danych.")
            return
        
        df = df.reset_index()
        df = df[["Date", "Close"]].dropna()
        data = df[["Close"]].values
        
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        
        X_full, y_full = create_sequences_multi(scaled_data, lookback, horizon)
        
        log(f"Dane przygotowane: {len(X_full)} sekwencji")
        
        # Funkcja do budowania modelu
        def build_model():
            m = Sequential()
            m.add(LSTM(50, return_sequences=True, input_shape=(lookback, 1)))
            m.add(Dropout(0.2))
            m.add(LSTM(50, return_sequences=False))
            m.add(Dropout(0.2))
            m.add(Dense(25))
            m.add(Dense(horizon))
            m.compile(optimizer="adam", loss="mean_squared_error")
            return m
        
        # Walk-forward validator
        validator = WalkForwardValidator(build_model, scaler)
        result = validator.run_walk_forward(X_full, y_full, lookback, horizon, 
                                           initial_train_size=0.7, step_size=1, 
                                           epochs=epochs, verbose=True)
        
        metrics = result["metrics"]
        log(f"\n✅ Walk-Forward Testing wyniki:")
        log(f"   RMSE: {metrics['RMSE']:.6f}")
        log(f"   MAE: {metrics['MAE']:.6f}")
        log(f"   MAPE: {metrics['MAPE']:.2f}%")
        log(f"   Directional Accuracy: {metrics['Directional_Accuracy']*100:.1f}%")
        
        # Zapis wyników
        output_dir = os.path.join(os.path.dirname(__file__), "walk_forward")
        os.makedirs(output_dir, exist_ok=True)
        
        today_str = dt.date.today().isoformat()
        wf_path = os.path.join(output_dir, f"walk_forward_{ticker}_{today_str}.csv")
        
        df_wf = validator.get_results_dataframe()
        df_wf.to_csv(wf_path, index=False)
        log(f"📄 Szczegóły zapisane do: {wf_path}")
        
        messagebox.showinfo("Walk-Forward Testing", 
                           f"Testowanie ukończone.\n"
                           f"Directional Accuracy: {metrics['Directional_Accuracy']*100:.1f}%")
        
    except Exception as e:
        log(f"❌ Błąd podczas walk-forward testing: {e}")
        messagebox.showerror("Błąd", f"Błąd: {e}")


# =============== BACKTEST: PROGNOZA vs RZECZYWISTOŚĆ ===============
def backtest_from_csv():
    """
    Wybiera plik CSV z prognozą, pobiera rzeczywiste dane z Yahoo,
    dopasowuje po dacie, liczy błędy i rysuje wykres prognoza vs real.
    """
    try:
        log("\n================ BACKTEST ================")
        file_path = filedialog.askopenfilename(
            title="Wybierz plik CSV z prognozą",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            log("Backtest przerwany – nie wybrano pliku.")
            return

        log(f"📂 Wybrano plik: {file_path}")
        df_forecast = pd.read_csv(file_path)

        # oczekiwane kolumny z naszego generatora prognoz
        required_cols = {"ticker", "date", "forecast"}
        if not required_cols.issubset(df_forecast.columns):
            log("❌ Plik nie wygląda na prognozę z tego programu (brak wymaganych kolumn).")
            messagebox.showerror(
                "Błędny plik",
                "Plik nie zawiera wymaganych kolumn: 'ticker', 'date', 'forecast'."
            )
            return

        # konwersja dat
        df_forecast["date"] = pd.to_datetime(df_forecast["date"]).dt.date

        # zakładamy jeden ticker w pliku
        ticker = str(df_forecast["ticker"].iloc[0]).upper()
        log(f"🔍 Ticker z pliku prognozy: {ticker}")

        # bierzemy tylko te daty, które już minęły (lub są dziś)
        today = dt.date.today()
        df_past = df_forecast[df_forecast["date"] <= today].copy()
        if df_past.empty:
            log("❌ Żadna data prognozy jeszcze nie nastąpiła – brak danych do porównania.")
            messagebox.showinfo(
                "Brak danych do backtestu",
                "prognoza jest całkowicie w przyszłości.\n"
                "Spróbuj za kilka dni."
            )
            return

        start_date = df_past["date"].min()
        end_date = df_past["date"].max()
        log(f"📆 Zakres dat do porównania: {start_date} – {end_date}")

        # pobieramy rzeczywiste dane z Yahoo Finance
        log("⬇️ Pobieram rzeczywiste dane z Yahoo Finance...")
        df_real = yf.download(
            ticker,
            start=start_date,
            end=end_date + dt.timedelta(days=1)  # end w yfinance jest ekskluzywne
        ).reset_index()

        if df_real.empty:
            log("❌ Brak rzeczywistych danych z Yahoo Finance.")
            messagebox.showerror("Błąd", "Nie udało się pobrać rzeczywistych danych z Yahoo Finance.")
            return

        df_real["Date"] = pd.to_datetime(df_real["Date"]).dt.date
        df_real = df_real[["Date", "Close"]].rename(columns={"Date": "date", "Close": "real"})

        # łączymy prognozę z realnymi danymi po dacie
        df_merge = pd.merge(df_past, df_real, on="date", how="inner")

        if df_merge.empty:
            log("❌ Brak wspólnych dat między prognozą a danymi rzeczywistymi.")
            messagebox.showerror("Błąd", "Nie znaleziono wspólnych dat do porównania.")
            return

        # liczymy błędy
        df_merge["diff"] = df_merge["real"] - df_merge["forecast"]
        df_merge["abs_diff"] = df_merge["diff"].abs()
        df_merge["pct_error"] = df_merge["diff"] / df_merge["real"] * 100.0
        df_merge["abs_pct_error"] = df_merge["pct_error"].abs()

        avg_abs_pct_error = df_merge["abs_pct_error"].mean()
        max_abs_pct_error = df_merge["abs_pct_error"].max()

        log("\n📊 Podsumowanie backtestu:")
        log(f"   Liczba punktów porównania: {len(df_merge)}")
        log(f"   Średni bezwzględny błąd procentowy: {avg_abs_pct_error:.2f}%")
        log(f"   Maksymalny bezwzględny błąd procentowy: {max_abs_pct_error:.2f}%")

        # Zapis wyników backtestu do pliku
        try:
            output_dir_bt = os.path.join(os.path.dirname(__file__), "backtesty")
            os.makedirs(output_dir_bt, exist_ok=True)

            now_str = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_bt = f"BACKTEST_{ticker}_{now_str}.csv"
            filepath_bt = os.path.join(output_dir_bt, filename_bt)

            df_merge.to_csv(filepath_bt, index=False)
            log(f"📄 Szczegóły backtestu zapisane do: {filepath_bt}")
        except Exception as e_bt_save:
            log(f"⚠️ Nie udało się zapisać szczegółów backtestu do CSV: {e_bt_save}")

        # wykres prognoza vs real
        try:
            plt.figure(figsize=(10, 5))
            plt.plot(df_merge["date"], df_merge["real"], label="Rzeczywiste", color="blue")
            plt.plot(df_merge["date"], df_merge["forecast"], label="Prognoza", color="red", marker="o")

            plt.title(f"Backtest prognozy dla {ticker}\n"
                      f"Śr. abs. błąd %: {avg_abs_pct_error:.2f}")
            plt.xlabel("Data")
            plt.ylabel("Cena")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        except Exception as e_plot:
            log(f"⚠️ Nie udało się narysować wykresu backtestu: {e_plot}")

        messagebox.showinfo(
            "Backtest zakończony",
            f"Backtest dla {ticker} zakończony.\n"
            f"Średni bezwzględny błąd procentowy: {avg_abs_pct_error:.2f}%.\n"
            "Szczegóły w logu i w folderze 'backtesty'."
        )

    except Exception as e:
        log(f"❌ Błąd podczas backtestu: {e}")
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas backtestu:\n{e}")


# =============== OBSŁUGA PRZYCISKÓW GUI ===============
def on_train_click():
    ticker = entry_ticker.get().strip()
    if not ticker:
        messagebox.showwarning("Brak tickera", "Wpisz symbol, np. AAPL, MSFT, PKN.WA.")
        return
    try:
        lookback = int(entry_lookback.get().strip() or "60")
        horizon = int(entry_horizon.get().strip() or "5")
        epochs = int(entry_epochs.get().strip() or "20")
    except ValueError:
        messagebox.showerror("Błąd danych", "LOOKBACK, HORYZONT i EPOCHS muszą być liczbami całkowitymi.")
        return

    log("\n================ TRENING MODELU ================")
    train_model(ticker, lookback=lookback, horizon=horizon, epochs=epochs)


def on_predict_click():
    ticker = entry_ticker.get().strip()
    if not ticker:
        messagebox.showwarning("Brak tickera", "Wpisz symbol, np. AAPL, MSFT, PKN.WA.")
        return
    try:
        lookback = int(entry_lookback.get().strip() or "60")
        horizon = int(entry_horizon.get().strip() or "5")
    except ValueError:
        messagebox.showerror("Błąd danych", "LOOKBACK i HORYZONT muszą być liczbami całkowitymi.")
        return

    # progi alertów (opcjonalne)
    alert_high = None
    alert_low = None
    high_str = entry_alert_high.get().strip()
    low_str = entry_alert_low.get().strip()

    if high_str:
        try:
            alert_high = float(high_str)
        except ValueError:
            messagebox.showerror("Błąd danych", "Alert 'powyżej' musi być liczbą.")
            return

    if low_str:
        try:
            alert_low = float(low_str)
        except ValueError:
            messagebox.showerror("Błąd danych", "Alert 'poniżej' musi być liczbą.")
            return

    log("\n================ PROGNOZA ================")
    predict_future(
        ticker,
        lookback=lookback,
        horizon=horizon,
        alert_high=alert_high,
        alert_low=alert_low
    )


def on_backtest_click():
    log("\n================ START BACKTESTU ================")
    backtest_from_csv()


def on_compare_models_click():
    """Porównaj modele."""
    ticker = entry_ticker.get().strip()
    if not ticker:
        messagebox.showwarning("Brak tickera", "Wpisz symbol.")
        return
    try:
        lookback = int(entry_lookback.get().strip() or "60")
        horizon = int(entry_horizon.get().strip() or "5")
        epochs = int(entry_epochs.get().strip() or "10")
    except ValueError:
        messagebox.showerror("Błąd danych", "Parametry muszą być liczbami.")
        return
    
    compare_models_command(ticker, lookback, horizon, epochs)


def on_walk_forward_click():
    """Uruchom walk-forward testing."""
    ticker = entry_ticker.get().strip()
    if not ticker:
        messagebox.showwarning("Brak tickera", "Wpisz symbol.")
        return
    try:
        lookback = int(entry_lookback.get().strip() or "60")
        horizon = int(entry_horizon.get().strip() or "5")
        epochs = int(entry_epochs.get().strip() or "5")
    except ValueError:
        messagebox.showerror("Błąd danych", "Parametry muszą być liczbami.")
        return
    
    walk_forward_test(ticker, lookback, horizon, epochs)


def on_technical_indicators_click():
    """Uruchom analizę wskaźników technicznych."""
    ticker = entry_ticker.get().strip()
    if not ticker:
        messagebox.showwarning("Brak tickera", "Wpisz symbol.")
        return
    
    analyze_technical_indicators(ticker)


def view_forecast_history():
    """Wyświetl historię prognoz z bazy danych."""
    try:
        if ForecastDatabase is None:
            log("❌ Moduł forecast_database nie załadowany.")
            messagebox.showerror("Błąd", "Brak modułu forecast_database.")
            return
            
        ticker = entry_ticker.get().strip()
        if not ticker:
            messagebox.showwarning("Brak tickera", "Wpisz symbol.")
            return
        
        log(f"\n================ HISTORIA PROGNOZ - {ticker.upper()} ================")
        
        db_path = os.path.join(os.path.dirname(__file__), "forecast_history.db")
        with ForecastDatabase(db_path) as db:
            # Historia prognoz
            history = db.get_forecast_history(ticker, limit=20)
            
            if history.empty:
                log(f"❌ Brak historii prognoz dla {ticker}.")
                messagebox.showinfo("Historia", f"Brak prognoz dla {ticker} w bazie danych.")
                return
            
            log("\n📊 Ostatnie prognozy:")
            for idx, row in history.iterrows():
                log(f"   {row['created_at']} | {row['days_ahead']} dni | Model: {row['model_type']}")
            
            # Statystyki backtestu
            stats = db.get_backtest_stats(ticker)
            if stats:
                log(f"\n✅ Statystyki backtestu:")
                log(f"   Liczba testów: {stats['total_tests']}")
                log(f"   Średni błąd: {stats['avg_error']:.2f}%")
                log(f"   Najlepszy błąd: {stats['best_error']:.2f}%")
                log(f"   Najgorszy błąd: {stats['worst_error']:.2f}%")
            
            # Analiza wydajności modeli
            analyzer = ForecastAnalyzer(db_path)
            model_perf = analyzer.compare_models_performance(ticker)
            
            if not model_perf.empty:
                log(f"\n📈 Porównanie modeli:")
                log(model_perf.to_string())
        
        messagebox.showinfo("Historia prognoz", 
                           "Historia wyświetlona w oknie logu.\nZobacz szczegóły powyżej.")
        
    except Exception as e:
        log(f"❌ Błąd podczas przeglądania historii: {e}")
        messagebox.showerror("Błąd", f"Błąd: {e}")


# =============== SCHEDULER I MONITORING ===============
def configure_scheduler():
    """Skonfiguruj harmonogram prognoz."""
    try:
        log("\n================ KONFIGURACJA HARMONOGRAMU ================")
        
        # Proste konfigurowanie – można rozszerzyć
        log("Aby używać harmonogramu, zainstaluj: pip install schedule")
        log("Przykład: scheduler.schedule_daily_forecast(['AAPL', 'MSFT'], '09:30', predict_future)")
        
        messagebox.showinfo("Scheduler", 
                           "Moduł schedulera jest dostępny.\n"
                           "Dokumentacja: forecast_scheduler.py")
        
    except Exception as e:
        log(f"❌ Błąd: {e}")


def setup_alerts():
    """Skonfiguruj alerty cenowe."""
    try:
        ticker = entry_ticker.get().strip()
        if not ticker:
            messagebox.showwarning("Brak tickera", "Wpisz symbol.")
            return
        
        log(f"\n================ KONFIGURACJA ALERTÓW - {ticker.upper()} ================")
        log("Wprowadź ceny w polach 'Alert':")
        log(f"  Powyżej: {entry_alert_high.get() or 'nie ustawiony'}")
        log(f"  Poniżej: {entry_alert_low.get() or 'nie ustawiony'}")
        
        messagebox.showinfo("Alerty", 
                           f"Alerty ustawione dla {ticker}.\n"
                           "Będą aktywne przy następnej prognozie.")
        
    except Exception as e:
        log(f"❌ Błąd: {e}")


# =============== SZYBKIE USTAWIANIE TICKERA ===============
def set_ticker_quick(symbol: str):
    """Ustawia szybciej ticker w polu wejściowym."""
    global entry_ticker
    entry_ticker.delete(0, tk.END)
    entry_ticker.insert(0, symbol)
    log(f"🔁 Ustawiono ticker na: {symbol}")


# =============== BUDOWA OKNA ===============
def build_gui():
    global root, output_text, current_theme
    global entry_ticker, entry_lookback, entry_horizon, entry_epochs
    global entry_alert_high, entry_alert_low

    root = tk.Tk()
    root.title("📈 LSTM – Prognoza Kursu Akcji i Indeksów")
    root.geometry("1200x800")
    
    # Motyw ciemny jeśli dostępny
    if UI_MODERN:
        current_theme = ModernTheme.DARK_MODE
        root.configure(bg=current_theme["bg_primary"])
    else:
        current_theme = {"bg_primary": "#f0f0f0", "text_primary": "black"}
        root.configure(bg=current_theme["bg_primary"])

    # Główna ramka z scrollingiem
    canvas = tk.Canvas(root, bg=current_theme["bg_primary"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # === HEADER ===
    header_frame = ttk.Frame(scrollable_frame)
    header_frame.pack(fill="x", padx=20, pady=15)
    
    title_label = ttk.Label(
        header_frame, 
        text="📈 Prognoza Kursu Akcji z LSTM",
        font=ModernTheme.FONTS["title_lg"] if UI_MODERN else ("Helvetica", 18, "bold")
    )
    title_label.pack(anchor="w")
    
    subtitle_label = ttk.Label(
        header_frame,
        text="System uczenia maszynowego do prognozowania cen akcji",
        font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)
    )
    subtitle_label.pack(anchor="w")

    # === SEKCJA 1: DANE WEJŚCIOWE ===
    section1_frame = ttk.LabelFrame(scrollable_frame, text=" 📊 Dane Wejściowe ", padding=15)
    section1_frame.pack(fill="x", padx=20, pady=10)
    
    # Ticker
    ttk.Label(section1_frame, text="Ticker:", font=ModernTheme.FONTS["title_sm"] if UI_MODERN else ("Helvetica", 11, "bold")).grid(row=0, column=0, sticky="w", pady=5)
    entry_ticker = ttk.Entry(section1_frame, width=15, font=ModernTheme.FONTS["body_md"] if UI_MODERN else ("Helvetica", 10))
    entry_ticker.grid(row=0, column=1, sticky="w", padx=10)
    entry_ticker.insert(0, "AAPL")
    
    # Skróty tickerów
    ttk.Label(section1_frame, text="Szybkie skróty:", font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)).grid(row=1, column=0, sticky="w", pady=5)
    
    shortcuts_frame = ttk.Frame(section1_frame)
    shortcuts_frame.grid(row=1, column=1, columnspan=3, sticky="w")
    
    shortcuts = [
        ("📈 S&P500", "^GSPC"),
        ("🔷 SPY", "SPY"),
        ("🟦 NASDAQ", "^NDX"),
        ("💹 WIG20", "^WIG20"),
        ("🏢 Apple", "AAPL"),
        ("🔧 MSFT", "MSFT"),
    ]
    
    for i, (label, ticker) in enumerate(shortcuts):
        btn = ttk.Button(
            shortcuts_frame,
            text=label,
            command=lambda t=ticker: set_ticker_quick(t),
            width=12
        )
        btn.grid(row=0, column=i, padx=3, pady=3)
    
    # Parametry
    params_frame = ttk.Frame(section1_frame)
    params_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=10)
    
    ttk.Label(params_frame, text="LOOKBACK:", font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)).grid(row=0, column=0, sticky="w", padx=5)
    entry_lookback = ttk.Entry(params_frame, width=8)
    entry_lookback.grid(row=0, column=1, padx=5)
    entry_lookback.insert(0, "60")
    
    ttk.Label(params_frame, text="HORYZONT:", font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)).grid(row=0, column=2, sticky="w", padx=5)
    entry_horizon = ttk.Entry(params_frame, width=8)
    entry_horizon.grid(row=0, column=3, padx=5)
    entry_horizon.insert(0, "5")
    
    ttk.Label(params_frame, text="EPOCHS:", font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)).grid(row=0, column=4, sticky="w", padx=5)
    entry_epochs = ttk.Entry(params_frame, width=8)
    entry_epochs.grid(row=0, column=5, padx=5)
    entry_epochs.insert(0, "20")
    
    # Alerty
    alerts_frame = ttk.Frame(section1_frame)
    alerts_frame.grid(row=3, column=0, columnspan=4, sticky="w", pady=10)
    
    ttk.Label(alerts_frame, text="🔔 Alert D+ostatni:", font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)).grid(row=0, column=0, sticky="w", padx=5)
    ttk.Label(alerts_frame, text="Powyżej:", font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)).grid(row=0, column=1, sticky="w", padx=5)
    entry_alert_high = ttk.Entry(alerts_frame, width=10)
    entry_alert_high.grid(row=0, column=2, padx=3)
    
    ttk.Label(alerts_frame, text="Poniżej:", font=ModernTheme.FONTS["body_sm"] if UI_MODERN else ("Helvetica", 9)).grid(row=0, column=3, sticky="w", padx=5)
    entry_alert_low = ttk.Entry(alerts_frame, width=10)
    entry_alert_low.grid(row=0, column=4, padx=3)

    # === SEKCJA 2: AKCJE GŁÓWNE ===
    section2_frame = ttk.LabelFrame(scrollable_frame, text=" 🎯 Akcje Główne ", padding=15)
    section2_frame.pack(fill="x", padx=20, pady=10)
    
    main_buttons_frame = ttk.Frame(section2_frame)
    main_buttons_frame.pack(fill="x")
    
    btn_train = ttk.Button(main_buttons_frame, text="🧠 Trenuj Model", command=on_train_click, width=18)
    btn_train.pack(side="left", padx=5, pady=5)
    
    btn_predict = ttk.Button(main_buttons_frame, text="🔮 Prognozuj", command=on_predict_click, width=18)
    btn_predict.pack(side="left", padx=5, pady=5)
    
    btn_backtest = ttk.Button(main_buttons_frame, text="📊 Backtest", command=on_backtest_click, width=18)
    btn_backtest.pack(side="left", padx=5, pady=5)

    # === SEKCJA 3: ZAAWANSOWANE ===
    section3_frame = ttk.LabelFrame(scrollable_frame, text=" ⚙️ Zaawansowane ", padding=15)
    section3_frame.pack(fill="x", padx=20, pady=10)
    
    adv_buttons_frame = ttk.Frame(section3_frame)
    adv_buttons_frame.pack(fill="x")
    
    if ModelComparator_AVAILABLE:
        btn_compare = ttk.Button(adv_buttons_frame, text="⚖️ Porównaj Modele", command=on_compare_models_click, width=18)
        btn_compare.pack(side="left", padx=5, pady=5)
    
    if ValidationMetrics_AVAILABLE:
        btn_walk_forward = ttk.Button(adv_buttons_frame, text="📈 Walk-Forward", command=on_walk_forward_click, width=18)
        btn_walk_forward.pack(side="left", padx=5, pady=5)
    
    if TechnicalIndicators_AVAILABLE:
        btn_technical = ttk.Button(adv_buttons_frame, text="📉 Wskaźniki", command=on_technical_indicators_click, width=18)
        btn_technical.pack(side="left", padx=5, pady=5)
    
    if ForecastDatabase_AVAILABLE:
        btn_history = ttk.Button(adv_buttons_frame, text="📜 Historia", command=view_forecast_history, width=18)
        btn_history.pack(side="left", padx=5, pady=5)

    # === SEKCJA 4: NARZĘDZIA ===
    section4_frame = ttk.LabelFrame(scrollable_frame, text=" 🛠️ Narzędzia ", padding=15)
    section4_frame.pack(fill="x", padx=20, pady=10)
    
    tools_buttons_frame = ttk.Frame(section4_frame)
    tools_buttons_frame.pack(fill="x")
    
    btn_scheduler = ttk.Button(tools_buttons_frame, text="⏰ Harmonogram", command=configure_scheduler, width=18)
    btn_scheduler.pack(side="left", padx=5, pady=5)
    
    btn_alerts_setup = ttk.Button(tools_buttons_frame, text="🔔 Konfiguruj Alerty", command=setup_alerts, width=18)
    btn_alerts_setup.pack(side="left", padx=5, pady=5)
    
    btn_clear_log = ttk.Button(tools_buttons_frame, text="🗑️ Wyczyść Log", command=lambda: clear_log(), width=18)
    btn_clear_log.pack(side="left", padx=5, pady=5)

    # === LOG ===
    log_frame = ttk.LabelFrame(scrollable_frame, text=" 📋 Log / Wyniki ", padding=10)
    log_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    output_text = tk.Text(
        log_frame,
        height=15,
        width=100,
        font=ModernTheme.FONTS["mono"] if UI_MODERN else ("Monaco", 10),
        bg=current_theme.get("bg_secondary", "#f5f5f5"),
        fg=current_theme.get("text_primary", "black"),
        wrap="word",
        insertbackground=current_theme.get("accent_blue", "blue")
    )
    output_text.pack(side="left", fill="both", expand=True)
    
    scrollbar_log = ttk.Scrollbar(log_frame, orient="vertical", command=output_text.yview)
    scrollbar_log.pack(side="right", fill="y")
    output_text.configure(yscrollcommand=scrollbar_log.set)

    return root


def clear_log():
    """Wyczyść okno logu"""
    global output_text
    if output_text:
        output_text.delete(1.0, tk.END)
        log("✨ Log wyczyszczony")


def set_ticker_quick(symbol: str):
    """Ustawia szybciej ticker w polu wejściowym."""
    global entry_ticker
    entry_ticker.delete(0, tk.END)
    entry_ticker.insert(0, symbol)
    log(f"🔄 Ustawiono ticker na: {symbol}")


if __name__ == "__main__":
    root = build_gui()
    log("Program LSTM do prognozy kursu akcji – gotowy.")
    log("Wpisz ticker albo użyj przycisków skrótów, ustaw parametry i kliknij 'Trenuj model' lub 'Prognozuj'.")
    log("Do backtestu użyj przycisku 'Backtest z pliku CSV' i wybierz zapisany wcześniej plik prognozy.")
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n✅ Program zamknięty.")
    except Exception as e:
        print(f"❌ Błąd: {e}")
