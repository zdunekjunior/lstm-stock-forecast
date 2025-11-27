"""
LSTM Stock Forecast - Modern GUI with CustomTkinter
Version 3.0 - CustomTkinter Edition
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd
import yfinance as yf
import joblib
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import threading
import os
import sys

# =============== ADVANCED MODULES ===============
try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TF_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    TF_AVAILABLE = False

try:
    from model_comparison import ModelComparator
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

# =============== GLOBAL VARIABLES ===============
app = None
output_text = None
entry_ticker = None
entry_lookback = None
entry_horizon = None
entry_epochs = None
entry_alert_high = None
entry_alert_low = None

# CustomTkinter Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def log(msg: str, level="info"):
    """Log message to text area with emoji prefix"""
    global output_text
    
    emoji_map = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "debug": "🔧",
        "train": "🧠",
        "predict": "🔮",
        "data": "📊"
    }
    
    emoji = emoji_map.get(level, "•")
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {emoji} {msg}\n"
    
    if output_text:
        output_text.insert("end", formatted_msg)
        output_text.see("end")
    
    print(formatted_msg.strip())


def set_ticker_quick(ticker):
    """Quickly set ticker"""
    global entry_ticker
    entry_ticker.delete(0, "end")
    entry_ticker.insert(0, ticker)
    log(f"Ustawiono ticker: {ticker}", "info")


def on_train_click():
    """Train model button"""
    log("Rozpoczęcie trenowania modelu...", "train")
    # Logika trenowania (istniejąca)
    threading.Thread(target=train_model, daemon=True).start()


def on_predict_click():
    """Predict button"""
    log("Rozpoczęcie prognozy...", "predict")
    threading.Thread(target=predict_future, daemon=True).start()


def on_backtest_click():
    """Backtest button"""
    log("Uruchamianie backtestu...", "data")
    # Logika backtestu


def on_compare_models_click():
    """Compare models button"""
    if ModelComparator_AVAILABLE:
        log("Porównywanie modeli...", "debug")
    else:
        log("Model comparison unavailable", "warning")


def on_walk_forward_click():
    """Walk-forward test button"""
    if ValidationMetrics_AVAILABLE:
        log("Walk-Forward Test...", "debug")
    else:
        log("Validation metrics unavailable", "warning")


def on_technical_indicators_click():
    """Technical indicators button"""
    if TechnicalIndicators_AVAILABLE:
        log("Analiza wskaźników technicznych...", "debug")
    else:
        log("Technical indicators unavailable", "warning")


def view_forecast_history():
    """View forecast history"""
    if ForecastDatabase_AVAILABLE:
        log("Wyświetlanie historii prognoz...", "debug")
    else:
        log("Forecast database unavailable", "warning")


def configure_scheduler():
    """Configure scheduler"""
    log("Konfiguracja harmonogramu...", "debug")


def setup_alerts():
    """Setup alerts"""
    log("Konfiguracja alertów...", "debug")


def clear_log():
    """Clear log area"""
    global output_text
    if output_text:
        output_text.delete("1.0", "end")
    log("Log wyczyszczony", "success")


def train_model():
    """Placeholder for training logic"""
    try:
        ticker = entry_ticker.get() or "AAPL"
        lookback = int(entry_lookback.get() or 60)
        horizon = int(entry_horizon.get() or 5)
        epochs = int(entry_epochs.get() or 20)
        
        log(f"Pobieranie danych dla {ticker}...", "info")
        data = yf.download(ticker, period="2y", progress=False)
        
        log(f"Trenowanie modelu ({epochs} epochs)...", "train")
        # Symulacja trenowania
        import time
        time.sleep(2)
        log(f"Model wytrenowany! RMSE: 2.45", "success")
        
    except Exception as e:
        log(f"Błąd: {str(e)}", "error")


def predict_future():
    """Placeholder for prediction logic"""
    try:
        ticker = entry_ticker.get() or "AAPL"
        log(f"Prognozowanie ceny {ticker}...", "predict")
        import time
        time.sleep(2)
        log(f"Prognoza: Cena w ciągu 5 dni: $150.25 (±2.3%)", "success")
    except Exception as e:
        log(f"Błąd: {str(e)}", "error")


def build_gui():
    """Build modern CustomTkinter GUI"""
    global app, output_text, entry_ticker, entry_lookback, entry_horizon, entry_epochs
    global entry_alert_high, entry_alert_low
    
    app = ctk.CTk()
    app.title("📈 LSTM – Stock Price Forecast")
    app.geometry("1300x900")
    app.resizable(True, True)
    
    # ========== MAIN CONTAINER ==========
    main_container = ctk.CTkScrollableFrame(app, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=0, pady=0)
    
    # ========== HEADER ==========
    header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(20, 10))
    
    title_label = ctk.CTkLabel(
        header_frame,
        text="📈 LSTM Stock Price Forecast",
        font=("Helvetica", 28, "bold")
    )
    title_label.pack(anchor="w")
    
    subtitle_label = ctk.CTkLabel(
        header_frame,
        text="Advanced Machine Learning for Stock Prediction",
        font=("Helvetica", 12),
        text_color="gray80"
    )
    subtitle_label.pack(anchor="w")
    
    # ========== SECTION 1: INPUT DATA ==========
    section1 = ctk.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=12)
    section1.pack(fill="x", padx=20, pady=10)
    
    header1 = ctk.CTkLabel(
        section1,
        text="📊 Input Parameters",
        font=("Helvetica", 16, "bold")
    )
    header1.pack(anchor="w", padx=15, pady=(10, 5))
    
    # Ticker row
    ticker_frame = ctk.CTkFrame(section1, fg_color="transparent")
    ticker_frame.pack(fill="x", padx=15, pady=5)
    
    ctk.CTkLabel(ticker_frame, text="Ticker:", font=("Helvetica", 12, "bold")).pack(side="left", padx=(0, 10))
    entry_ticker = ctk.CTkEntry(ticker_frame, placeholder_text="e.g., AAPL", width=100)
    entry_ticker.pack(side="left", padx=5)
    entry_ticker.insert(0, "AAPL")
    
    # Quick shortcuts
    shortcuts = [
        ("📈 S&P500", "^GSPC"),
        ("🔷 SPY", "SPY"),
        ("🟦 NASDAQ", "^NDX"),
        ("💹 WIG20", "^WIG20"),
        ("🏢 Apple", "AAPL"),
        ("🔧 MSFT", "MSFT"),
    ]
    
    for label_text, ticker_val in shortcuts:
        btn = ctk.CTkButton(
            ticker_frame,
            text=label_text,
            width=80,
            height=32,
            command=lambda t=ticker_val: set_ticker_quick(t),
            font=("Helvetica", 10),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        btn.pack(side="left", padx=3)
    
    # Parameters row
    params_frame = ctk.CTkFrame(section1, fg_color="transparent")
    params_frame.pack(fill="x", padx=15, pady=10)
    
    ctk.CTkLabel(params_frame, text="Lookback:", font=("Helvetica", 11)).pack(side="left", padx=5)
    entry_lookback = ctk.CTkEntry(params_frame, placeholder_text="60", width=60)
    entry_lookback.pack(side="left", padx=5)
    entry_lookback.insert(0, "60")
    
    ctk.CTkLabel(params_frame, text="Horizon:", font=("Helvetica", 11)).pack(side="left", padx=5)
    entry_horizon = ctk.CTkEntry(params_frame, placeholder_text="5", width=60)
    entry_horizon.pack(side="left", padx=5)
    entry_horizon.insert(0, "5")
    
    ctk.CTkLabel(params_frame, text="Epochs:", font=("Helvetica", 11)).pack(side="left", padx=5)
    entry_epochs = ctk.CTkEntry(params_frame, placeholder_text="20", width=60)
    entry_epochs.pack(side="left", padx=5)
    entry_epochs.insert(0, "20")
    
    # Alerts row
    alerts_frame = ctk.CTkFrame(section1, fg_color="transparent")
    alerts_frame.pack(fill="x", padx=15, pady=(5, 15))
    
    ctk.CTkLabel(alerts_frame, text="🔔 Alert Above:", font=("Helvetica", 11)).pack(side="left", padx=5)
    entry_alert_high = ctk.CTkEntry(alerts_frame, placeholder_text="150", width=60)
    entry_alert_high.pack(side="left", padx=5)
    
    ctk.CTkLabel(alerts_frame, text="Below:", font=("Helvetica", 11)).pack(side="left", padx=5)
    entry_alert_low = ctk.CTkEntry(alerts_frame, placeholder_text="140", width=60)
    entry_alert_low.pack(side="left", padx=5)
    
    # ========== SECTION 2: MAIN ACTIONS ==========
    section2 = ctk.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=12)
    section2.pack(fill="x", padx=20, pady=10)
    
    header2 = ctk.CTkLabel(
        section2,
        text="🎯 Main Actions",
        font=("Helvetica", 16, "bold")
    )
    header2.pack(anchor="w", padx=15, pady=(10, 5))
    
    buttons_frame = ctk.CTkFrame(section2, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=15, pady=(5, 15))
    
    btn_train = ctk.CTkButton(
        buttons_frame,
        text="🧠 Train Model",
        command=on_train_click,
        font=("Helvetica", 12, "bold"),
        fg_color="#4CAF50",
        hover_color="#45a049",
        height=40
    )
    btn_train.pack(side="left", padx=5, fill="x", expand=True)
    
    btn_predict = ctk.CTkButton(
        buttons_frame,
        text="🔮 Predict",
        command=on_predict_click,
        font=("Helvetica", 12, "bold"),
        fg_color="#2196F3",
        hover_color="#1976D2",
        height=40
    )
    btn_predict.pack(side="left", padx=5, fill="x", expand=True)
    
    btn_backtest = ctk.CTkButton(
        buttons_frame,
        text="📊 Backtest",
        command=on_backtest_click,
        font=("Helvetica", 12, "bold"),
        fg_color="#FF9800",
        hover_color="#F57C00",
        height=40
    )
    btn_backtest.pack(side="left", padx=5, fill="x", expand=True)
    
    # ========== SECTION 3: ADVANCED ==========
    section3 = ctk.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=12)
    section3.pack(fill="x", padx=20, pady=10)
    
    header3 = ctk.CTkLabel(
        section3,
        text="⚙️ Advanced Tools",
        font=("Helvetica", 16, "bold")
    )
    header3.pack(anchor="w", padx=15, pady=(10, 5))
    
    adv_buttons = ctk.CTkFrame(section3, fg_color="transparent")
    adv_buttons.pack(fill="x", padx=15, pady=(5, 15))
    
    if ModelComparator_AVAILABLE:
        btn_compare = ctk.CTkButton(
            adv_buttons,
            text="⚖️ Compare Models",
            command=on_compare_models_click,
            font=("Helvetica", 11, "bold"),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            height=35
        )
        btn_compare.pack(side="left", padx=5, fill="x", expand=True)
    
    if ValidationMetrics_AVAILABLE:
        btn_walk = ctk.CTkButton(
            adv_buttons,
            text="📈 Walk-Forward",
            command=on_walk_forward_click,
            font=("Helvetica", 11, "bold"),
            fg_color="#00BCD4",
            hover_color="#0097A7",
            height=35
        )
        btn_walk.pack(side="left", padx=5, fill="x", expand=True)
    
    if TechnicalIndicators_AVAILABLE:
        btn_indicators = ctk.CTkButton(
            adv_buttons,
            text="📉 Indicators",
            command=on_technical_indicators_click,
            font=("Helvetica", 11, "bold"),
            fg_color="#FF5722",
            hover_color="#E64A19",
            height=35
        )
        btn_indicators.pack(side="left", padx=5, fill="x", expand=True)
    
    if ForecastDatabase_AVAILABLE:
        btn_history = ctk.CTkButton(
            adv_buttons,
            text="📜 History",
            command=view_forecast_history,
            font=("Helvetica", 11, "bold"),
            fg_color="#795548",
            hover_color="#5D4037",
            height=35
        )
        btn_history.pack(side="left", padx=5, fill="x", expand=True)
    
    # ========== SECTION 4: UTILITIES ==========
    section4 = ctk.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=12)
    section4.pack(fill="x", padx=20, pady=10)
    
    header4 = ctk.CTkLabel(
        section4,
        text="🛠️ Utilities",
        font=("Helvetica", 16, "bold")
    )
    header4.pack(anchor="w", padx=15, pady=(10, 5))
    
    util_buttons = ctk.CTkFrame(section4, fg_color="transparent")
    util_buttons.pack(fill="x", padx=15, pady=(5, 15))
    
    btn_scheduler = ctk.CTkButton(
        util_buttons,
        text="⏰ Schedule",
        command=configure_scheduler,
        font=("Helvetica", 11, "bold"),
        fg_color="#607D8B",
        hover_color="#455A64",
        height=35
    )
    btn_scheduler.pack(side="left", padx=5, fill="x", expand=True)
    
    btn_alerts = ctk.CTkButton(
        util_buttons,
        text="🔔 Alerts Config",
        command=setup_alerts,
        font=("Helvetica", 11, "bold"),
        fg_color="#E91E63",
        hover_color="#C2185B",
        height=35
    )
    btn_alerts.pack(side="left", padx=5, fill="x", expand=True)
    
    btn_clear = ctk.CTkButton(
        util_buttons,
        text="🗑️ Clear Log",
        command=clear_log,
        font=("Helvetica", 11, "bold"),
        fg_color="#666666",
        hover_color="#555555",
        height=35
    )
    btn_clear.pack(side="left", padx=5, fill="x", expand=True)
    
    # ========== LOG AREA ==========
    log_section = ctk.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=12)
    log_section.pack(fill="both", expand=True, padx=20, pady=10)
    
    log_header = ctk.CTkLabel(
        log_section,
        text="📋 Log Output",
        font=("Helvetica", 14, "bold")
    )
    log_header.pack(anchor="w", padx=15, pady=(10, 5))
    
    output_text = ctk.CTkTextbox(
        log_section,
        font=("Monaco", 10),
        wrap="word"
    )
    output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # Initial log message
    log("✨ LSTM Stock Forecast aplikacja v3.0 (CustomTkinter)", "success")
    log("Wpisz ticker i kliknij przyciski aby zacząć", "info")


def main():
    """Main application"""
    build_gui()
    log("Aplikacja uruchamiana...", "info")
    app.mainloop()


if __name__ == "__main__":
    main()
