# gielda_lstm_gui.py

import datetime as dt
import os
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import pandas as pd
import yfinance as yf
import joblib

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout


# =============== LOGOWANIE DO OKNA ===============
root = None
output_text = None


def log(msg: str):
    """Wypisuje tekst do pola tekstowego i do konsoli."""
    print(msg)
    if output_text is not None:
        output_text.insert(tk.END, msg + "\n")
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
        log(f"\n[1/5] Pobieram dane z Yahoo Finance dla {ticker} (ostatnie 5 lat)...")
        end = dt.date.today()
        start = end - dt.timedelta(days=5 * 365)

        df = yf.download(ticker, start=start, end=end)

        if df.empty:
            log("❌ Brak danych. Sprawdź symbol (np. AAPL, MSFT, PKN.WA).")
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
def predict_future(ticker, lookback=60, horizon=5):
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

        log(f"\n[1/3] Wczytuję model i scaler dla {ticker}...")
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)

        log("[2/3] Pobieram najnowsze dane z Yahoo Finance...")
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

        log("[3/3] Liczę prognozę...")
        pred_scaled = model.predict(last_seq)  # (1, horizon)
        pred_scaled = pred_scaled.reshape(-1, 1)
        pred_prices = scaler.inverse_transform(pred_scaled).flatten()

        log(f"\n📈 Prognoza na kolejne {len(pred_prices)} dni dla {ticker.upper()}:")
        for i, price in enumerate(pred_prices, start=1):
            log(f"D+{i}: {price:.2f}")

        messagebox.showinfo("Prognoza gotowa", "Prognoza została policzona. Zobacz wyniki w oknie.")
    except Exception as e:
        log(f"❌ Błąd podczas prognozy: {e}")
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas prognozy:\n{e}")


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

    log("\n================ PROGNOZA ================")
    predict_future(ticker, lookback=lookback, horizon=horizon)


# =============== BUDOWA OKNA ===============
def build_gui():
    global root, output_text
    global entry_ticker, entry_lookback, entry_horizon, entry_epochs

    root = tk.Tk()
    root.title("LSTM – prognoza kursu akcji")

    # Główna ramka
    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Pola wejściowe
    ttk.Label(main_frame, text="Ticker (np. AAPL, MSFT, PKN.WA):").grid(row=0, column=0, sticky="w")
    entry_ticker = ttk.Entry(main_frame, width=20)
    entry_ticker.grid(row=0, column=1, sticky="w", pady=2)
    entry_ticker.insert(0, "AAPL")

    ttk.Label(main_frame, text="LOOKBACK (dni wstecz):").grid(row=1, column=0, sticky="w")
    entry_lookback = ttk.Entry(main_frame, width=10)
    entry_lookback.grid(row=1, column=1, sticky="w", pady=2)
    entry_lookback.insert(0, "60")

    ttk.Label(main_frame, text="HORYZONT (dni naprzód):").grid(row=2, column=0, sticky="w")
    entry_horizon = ttk.Entry(main_frame, width=10)
    entry_horizon.grid(row=2, column=1, sticky="w", pady=2)
    entry_horizon.insert(0, "5")

    ttk.Label(main_frame, text="EPOCHS (tylko dla treningu):").grid(row=3, column=0, sticky="w")
    entry_epochs = ttk.Entry(main_frame, width=10)
    entry_epochs.grid(row=3, column=1, sticky="w", pady=2)
    entry_epochs.insert(0, "10")

    # Przyciski
    btn_train = ttk.Button(main_frame, text="Trenuj model", command=on_train_click)
    btn_train.grid(row=4, column=0, pady=8, sticky="we")

    btn_predict = ttk.Button(main_frame, text="Prognozuj", command=on_predict_click)
    btn_predict.grid(row=4, column=1, pady=8, sticky="we")

    # Pole tekstowe na logi
    ttk.Label(main_frame, text="Log / wyniki:").grid(row=5, column=0, columnspan=2, sticky="w")

    output_text = tk.Text(main_frame, height=20, width=80)
    output_text.grid(row=6, column=0, columnspan=2, pady=5, sticky="nsew")

    main_frame.rowconfigure(6, weight=1)
    main_frame.columnconfigure(1, weight=1)

    return root


if __name__ == "__main__":
    root = build_gui()
    log("Program LSTM do prognozy kursu akcji – gotowy.")
    log("Wpisz ticker, ustaw parametry i kliknij 'Trenuj model' lub 'Prognozuj'.")
    root.mainloop()
