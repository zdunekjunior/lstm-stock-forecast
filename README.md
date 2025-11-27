# LSTM – System Prognozy Kursów Akcji

Zaawansowany system do prognozowania kursów akcji i indeksów przy użyciu sieci neuronowych LSTM, z pełnym arsen zalem analitycznym i monitoringiem.

> **✨ v2.1:** Nowy nowoczesny interfejs z ciemnym motywem, emoji ikonkami i responsywnym layoutem!

## 🚀 Funkcjonalności

### 1. **Podstawowe Prognozowanie** 
- Trenowanie modelu LSTM na historycznych danych z Yahoo Finance
- Prognozowanie cen na 1-30 dni naprzód
- Automatyczne pobieranie danych dla dowolnego tickera (AAPL, MSFT, PKN.WA, ^GSPC, etc.)
- Alerty cenowe (powyżej/poniżej wybranej ceny)

### 2. **Porównanie Modeli** ⭐ NOWE
- **LSTM** (2-warstwy) – standardowy model
- **GRU** – szybsza alternatywa
- **LSTM+GRU hybrid** – mieszany model
- **Dense baseline** – prosty baseline dla porównania
- Automatyczne raportowanie RMSE, MAE, MAPE

### 3. **Zaawansowana Walidacja** ⭐ NOWE
- **Walk-Forward Testing** – realistyczna symulacja czasowa
- **Metryki**: RMSE, MAE, MAPE, Directional Accuracy
- **Uncertainty Intervals** – 95% przedziały ufności dla każdej prognozy

### 4. **Wskaźniki Techniczne** ⭐ NOWE
- **RSI(14)** – Relative Strength Index (oversold/overbought)
- **MACD** – Moving Average Convergence Divergence
- **Bollinger Bands** – górny/dolny przedział
- **SMA(20) / SMA(50)** – średnie kroczące
- **ATR** – Average True Range (zmienność)
- Automatyczne analizy i sygnały handlowe

### 5. **Baza Danych Prognoz** ⭐ NOWE
- **SQLite** – pełna historia wszystkich prognoz
- Przechowywanie wyników backtestu
- Metryki wydajności modeli
- Analiza trendów i historii
- Export do CSV

### 6. **Zaawansowana Wizualizacja** ⭐ NOWE
- Wykresy z **confidence bands** (przedziały ufności)
- **Porównanie wielu tickerów** na jednym wykresie
- Wskaźniki techniczne (RSI, MACD, Bollinger Bands)
- **Export do PDF** (raporty)
- Rozkład błędów predykcji (histogram, Q-Q plot)

### 7. **Scheduling i Monitoring** ⭐ NOWE
- Harmonogram prognoz (dziennie o określonej godzinie)
- Periodyczne prognozy (co N minut)
- Monitoring cen w tyle rzeczywistym
- Alerty email i powiadomienia pulpitu
- Dashboard statusu

### 8. **Backtest**
- Porównanie rzeczywistych cen z prognozami
- Obliczanie błędów procentowych
- Wizualizacja wyników

---

## 📦 Instalacja

### Wymagania
- Python 3.8+
- pip

### Pakiety do zainstalowania
```bash
pip install yfinance tensorflow scikit-learn joblib matplotlib pandas numpy schedule scipy reportlab
```

Lub zainstaluj wszystko na raz:
```bash
pip install yfinance tensorflow scikit-learn joblib matplotlib pandas numpy schedule scipy reportlab
```

### Struktura Katalogów
Po pierwszym uruchomieniu program automatycznie utworzy:
```
Gielda/
├── gielda_lstm_gui.py              # Główny program GUI
├── model_comparison.py             # Porównanie modeli
├── validation_metrics.py           # Walidacja i Walk-Forward
├── technical_indicators.py         # Wskaźniki techniczne
├── forecast_database.py            # Baza danych SQLite
├── advanced_visualization.py       # Zaawansowane wykresy
├── forecast_scheduler.py           # Scheduling i monitoring
├── forecast_history.db             # Baza danych (autom. utworzona)
├── prognozy/                       # Prognozy (CSV)
├── wykresy/                        # Wykresy (PNG)
├── backtesty/                      # Wyniki backtestu
├── wskazniki/                      # Wskaźniki techniczne
├── porownania/                     # Porównanie modeli
├── walk_forward/                   # Wyniki Walk-Forward
└── README.md                       # Ten plik
```

---

## 🎯 Szybki Start

### 1. Uruchom program
```bash
python gielda_lstm_gui.py
```

### 2. Wpisz ticker
- Np. `AAPL`, `MSFT`, `PKN.WA`, `^GSPC`
- Lub kliknij przycisk skrótu (S&P 500, NASDAQ, WIG20, etc.)

### 3. Ustaw parametry
- **LOOKBACK**: liczba dni wstecz dla wejścia (domyślnie 60)
- **HORYZONT**: liczba dni do prognozy (domyślnie 5)
- **EPOCHS**: iteracje treningu (domyślnie 10-20)

### 4. Trenuj model
- Kliknij **"Trenuj model"**
- Program pobierze ostatnie 5 lat danych
- Wytrenuje sieć LSTM
- Zapisze model i scaler

### 5. Prognozuj
- Kliknij **"Prognozuj"**
- Program wyświetli prognozę na następnych dni
- **Nowe**: pokaże też przedziały ufności!
- Automatycznie zapisze w bazie danych

### 6. Analiza Wskaźników
- Kliknij **"Wskaźniki techniczne"**
- Zobaczysz RSI, MACD, SMA, Bollinger Bands
- Automatyczne sygnały handlowe

---

## 🔧 Zaawansowane Funkcje

### Porównanie Modeli
```
"Porównaj modele" → testuje LSTM, GRU, Hybrid, Dense
→ wyświetla RMSE, MAE, MAPE dla każdego
→ zapisuje raport w 'porownania/'
```

### Walk-Forward Testing
```
"Walk-Forward Test" → realistyczna symulacja
→ uczy na przeszłości, testuje na przyszłości
→ zawiera Directional Accuracy (% trafionych kierunków)
```

### Historia Prognoz
```
"Historia prognoz" → przegląda bazę danych SQLite
→ liczba testów, średni błąd, wydajność modeli
```

### Backtest
```
"Backtest z pliku CSV" → porównuje stare prognozy z rzeczywistością
→ oblicza błędy i wyświetla wykres
```

---

## 📊 Metryki Walidacji

| Metryka | Opis | Najlepsza wartość |
|---------|------|-------------------|
| **RMSE** | Root Mean Squared Error | ↓ niżej = lepiej |
| **MAE** | Mean Absolute Error | ↓ niżej = lepiej |
| **MAPE** | Mean Absolute % Error | ↓ niżej = lepiej |
| **Directional Accuracy** | % trafionych kierunków | ↑ wyżej = lepiej |
| **Confidence Bands** | 95% przedział ufności | ✓ rzeczywista cena w przedziale |

---

## 🎨 Wizualizacja

### 1. Prognoza z Confidence Bands
```
Klikaj "Prognozuj" → automatycznie rysuje wykres
+ historia (niebieska linia)
+ prognoza (czerwona linia)
+ 95% przedział ufności (szara strefa)
```

### 2. Wskaźniki Techniczne
```
3 panele:
1. Cena + SMA(20) + SMA(50)
2. RSI(14) z poziomami 30 (oversold) i 70 (overbought)
3. MACD z histogramem
```

### 3. Backtest
```
Rzeczywiste vs Prognozowane
+ zaznaczenie błędów (zielony = powyżej, czerwony = poniżej)
```

---

## 🔔 Alerty i Monitoring

### Ustawianie Alertów
1. Wpisz ceny w polach:
   - **Alert D+ostatni: powyżej:** (opcjonalnie)
   - **Alert D+ostatni: poniżej:** (opcjonalnie)
2. Kliknij "Prognozuj"
3. Jeśli prognoza przekroczy próg → automatyczne powiadomienie

### Scheduling (Zaawansowane)
```python
# Przykład – dodaj do kodu:
from forecast_scheduler import ForecastScheduler

scheduler = ForecastScheduler()
scheduler.schedule_daily_forecast(
    ticker_list=['AAPL', 'MSFT'],
    time_of_day='09:30',
    forecast_func=predict_future
)
scheduler.start_scheduler()
```

---

## 📈 Przykłady Użycia

### Scenariusz 1: Prognoza na akcję
```
1. Ticker: AAPL
2. LOOKBACK: 60, HORYZONT: 5, EPOCHS: 20
3. "Trenuj model" → czeka ~5 minut
4. "Prognozuj" → wynik dla 5 dni do przodu
5. "Backtest z pliku CSV" → weryfikacja dokładności
```

### Scenariusz 2: Analiza Indeksu
```
1. Ticker: ^WIG20 (WIG20)
2. "Wskaźniki techniczne" → czy trend wzrostu/spadku?
3. "Porównaj modele" → który model najlepszy dla tego indeksu?
4. "Historia prognoz" → jak dokładny był ostatnio?
```

### Scenariusz 3: Monitorowanie Ceny
```
1. Ustaw Alert: powyżej 150.00
2. Kliknij "Prognozuj"
3. Jeśli prognoza > 150 → alert wyświetlony
```

---

## 💡 Tips & Tricks

1. **Lepsze Prognozy**
   - Zwiększ EPOCHS do 50-100 dla bardziej dokładnego modelu
   - LOOKBACK=90 i HORIZON=10 dla długoterminowych trendów
   - Porównaj różne modele – GRU może być szybszy dla pewnych danych

2. **Szybkie Testowanie**
   - Użyj EPOCHS=5 dla szybkiej iteracji
   - Walk-Forward Test – najbardziej realistyczne wyniki

3. **Analiza Ryzyka**
   - Spraw Confidence Bands – jeśli przedział bardzo szeroki = wysoka niepewność
   - RSI < 30 → sygnał kupna, RSI > 70 → sygnał sprzedaży

4. **Efektywne Przechowywanie**
   - Historia prognoz w SQLite → łatwo szukać i analizować
   - Export do CSV dla dalszej analizy w Excel

---

## ⚠️ Ograniczenia

- Prognozy LSTM są ogólnie niedoskonałe dla rynków finansowych (RMSE ~2-5%)
- Dane Yahoo Finance mogą mieć opóźnienia
- Model uczy się z przeszłości – nie przewiduje czarnych łabędzi
- Tickery muszą być poprawne (sprawdź na Yahoo Finance)

---

## 🛠️ Rozwiązywanie Problemów

### Problem: "Brak danych z Yahoo Finance"
**Rozwiązanie**: Sprawdź, czy ticker jest poprawny. Testuj na: AAPL, MSFT, PKN.WA, ^GSPC

### Problem: Model trenuje bardzo długo
**Rozwiązanie**: Zmniejsz EPOCHS (np. z 20 na 5-10) lub LOOKBACK (z 60 na 30)

### Problem: Prognoza jest zawsze "płaska"
**Rozwiązanie**: Zwiększ EPOCHS, spróbuj innego modelu (GRU, Hybrid)

### Problem: Baza danych nie działa
**Rozwiązanie**: Usuń `forecast_history.db` i uruchom program ponownie

---

## 📝 Struktura Pliku głównego

```
gielda_lstm_gui.py
├── LOGOWANIE                  # Wyświetlanie komunikatów w GUI
├── FUNKCJE POMOCNICZE         # create_sequences_multi, get_file_paths
├── TRENING MODELU             # train_model()
├── PROGNOZA                   # predict_future() + UNCERTAINTY INTERVALS
├── PORÓWNANIE MODELI          # compare_models_command() [NOWE]
├── WALK-FORWARD TESTING       # walk_forward_test() [NOWE]
├── WSKAŹNIKI TECHNICZNE       # analyze_technical_indicators() [NOWE]
├── HISTORIA PROGNOZ           # view_forecast_history() [NOWE]
├── BACKTEST                   # backtest_from_csv()
├── OBSŁUGA PRZYCISKÓW         # on_*_click()
└── GUI                        # build_gui(), mainloop
```

---

## 🎓 O LSTM i Sieciach Neuronowych

**LSTM** (Long Short-Term Memory) to zaawansowana architektura RNN, która:
- Pamiętą długoterminowe zależności
- Rozwiązują problem zanikającego gradientu
- Doskonałe dla szeregów czasowych

**Alternatywy testowane w programie**:
- **GRU** – szybsza, mniej parametrów
- **Dense** – baseline, szybko
- **Hybrid** – łączy różne warstwy

---

## 📞 Wsparcie

Dla problemów lub sugestii, sprawdź:
- Logi w oknie programu (Log / wyniki)
- Pliki CSV w folderach (prognozy/, wykresy/)
- Bazę danych SQLite (forecast_history.db)

---

## 🎨 Interfejs Użytkownika (v2.1)

Aplikacja posiada **nowoczesny, responsywny interfejs** z následującymi cechami:

- **Ciemny motyw (Dark Mode)** – Domyślnie włączony
- **Emoji ikonki** – Wszystkie przyciski mają odpowiednie symbole
- **Responsywny layout** – Automatic scrolling dla długich interfejsów
- **Card-based sections** – Logicznie pogrupowane funcjonalności:
  - 📊 Dane Wejściowe (ticker, parametry, alerty)
  - 🎯 Akcje Główne (trenuj, prognozuj, backtest)
  - ⚙️ Zaawansowane (porównanie, walk-forward, wskaźniki)
  - 🛠️ Narzędzia (harmonogram, alerty, logi)

**Nowy moduł:** `modern_ui_theme.py` – Kompletny system motywów z predefiniowanymi paletami kolorów.

Szczegóły techniczne: [UI_MODERNIZATION.md](UI_MODERNIZATION.md)

---

## 📄 Licencja

Ten projekt jest demonstracją zaawansowanego systemu prognozowania. Użytkownik ponosi odpowiedzialność za decyzje handlowe.

---

**Wersja**: 2.1 (z nowoczesnym UI)  
**Poprzednia**: 2.0 (ML, Walidacja, Baza Danych, Scheduling)  
**Ostatnia aktualizacja**: Grudzień 2025  
**Autor**: LSTM Forecast System

Powodzenia! 🚀📈
