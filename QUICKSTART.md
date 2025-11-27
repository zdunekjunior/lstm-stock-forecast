# 🚀 SZYBKI START – LSTM Prognoza Kursu Akcji

## 1️⃣ Instalacja (5 minut)

### Krok 1: Zainstaluj zależności
```bash
cd ~/Desktop/Gielda
pip install -r requirements.txt
```

Jeśli masz problemy z TensorFlow:
```bash
pip install --upgrade tensorflow
```

### Krok 2: Sprawdź instalację
```bash
python -c "import tensorflow, yfinance, pandas; print('✅ OK')"
```

---

## 2️⃣ Pierwsze Uruchomienie (10 minut)

### Krok 1: Uruchom program
```bash
python gielda_lstm_gui.py
```

### Krok 2: Wpisz ticker
- Domyślnie jest **AAPL**
- Lub kliknij przycisk skrótu, np. "S&P 500 (^GSPC)"

### Krok 3: Trenuj model
- Kliknij **"Trenuj model"**
- Program pobierze ostatnie 5 lat danych
- Czekaj ~5-10 minut (zależy od komputera)
- Zobaczysz komunikat "✅ Zakończono trening"

### Krok 4: Prognozuj
- Kliknij **"Prognozuj"**
- Wynik pojawi się w logu + na wykresie
- **NOWE**: zobaczysz też przedziały ufności!

---

## 3️⃣ Najważniejsze Funkcje

| Przycisk | Co robi | Czas |
|----------|---------|------|
| **Trenuj model** | Uczy sieć LSTM | 5-10 min |
| **Prognozuj** | Generuje prognozę | 5 sek |
| **Porównaj modele** | Testuje 4 modele | 20 min |
| **Walk-Forward Test** | Realistyczna walidacja | 15 min |
| **Wskaźniki techniczne** | RSI, MACD, SMA | 10 sek |
| **Historia prognoz** | Przegląda bazę danych | 1 sek |
| **Backtest z CSV** | Sprawdza dokładność | 5 sek |

---

## 4️⃣ Przykład Sesji

### Sesja 1: Akcja Apple (AAPL)
```
1. Ticker: AAPL
2. LOOKBACK: 60
3. HORYZONT: 5
4. EPOCHS: 20
5. Kliknij "Trenuj model" → czekaj
6. Po treningu: kliknij "Prognozuj"
7. Wynik: "D+1: 195.43, D+2: 196.12, ..." (przykład)
8. Wykres: historia + prognoza + przedziały ufności
```

### Sesja 2: Porównanie Modeli
```
1. Ticker: AAPL
2. Kliknij "Porównaj modele"
3. Czekaj ~20 minut
4. Wynik: raport w folderze "porownania/"
5. Zawiera RMSE, MAE, MAPE dla każdego modelu
6. Przykład: GRU może być bardziej dokładny dla AAPL
```

### Sesja 3: Analiza Wskaźników
```
1. Ticker: ^WIG20 (WIG20)
2. Kliknij "Wskaźniki techniczne"
3. Zobaczysz: RSI, MACD, SMA(20), SMA(50)
4. Jeśli RSI < 30 → sygnał kupna
5. Jeśli RSI > 70 → sygnał sprzedaży
```

---

## 5️⃣ Parametry do Pamiętania

### LOOKBACK (domyślnie: 60)
- Liczba dni poprzednich do uczenia
- **60** = ostatnie 2 miesiące
- **30** = ostatnie miesiąc (szybciej)
- **90** = ostatnie 3 miesiące (dokładniej)

### HORYZONT (domyślnie: 5)
- Liczba dni do prognozowania
- **5** = prognoza na tydzień
- **20** = prognoza na miesiąc

### EPOCHS (domyślnie: 20)
- Iteracje treningu
- **5** = szybko (mniej dokładnie)
- **20** = standard
- **100** = dokładnie (długo)

---

## 6️⃣ Wyniki – Gdzie Szukać?

Po każdej operacji program tworzy foldery:

```
Gielda/
├── prognozy/           ← CSV z prognozami
├── wykresy/            ← PNG wykresy
├── backtesty/          ← Wyniki backtestu
├── wskazniki/          ← Wskaźniki techniczne
├── porownania/         ← Porównanie modeli
├── walk_forward/       ← Walk-Forward wyniki
└── forecast_history.db ← Baza danych
```

### Przykład
- **Prognoza CSV**: `AAPL_2025-11-27_5dni_20251127_143022.csv`
- **Wykres**: `AAPL_2025-11-27_5dni.png`
- **Backtest**: `BACKTEST_AAPL_20251127_143022.csv`

---

## 7️⃣ Alerty Cenowe

### Ustawianie
1. Wpisz ceny w polach:
   - **Alert D+ostatni: powyżej:** → np. `150.00`
   - **Alert D+ostatni: poniżej:** → np. `140.00`
2. Kliknij "Prognozuj"
3. Jeśli prognoza przekroczy → 🔔 Alert!

---

## 8️⃣ Metryki – Co Oznaczają?

### RMSE (Root Mean Squared Error)
- Średnia kwadratowa różnica między prognozą a rzeczywistością
- **Niska = dokładna**
- Jednostka: cena akcji

### MAE (Mean Absolute Error)
- Średni błąd absolutny
- Bardziej intuicyjny niż RMSE

### MAPE (Mean Absolute Percentage Error)
- Średni błąd procentowy
- **Idealna dla porównania różnych akcji**
- 5% MAPE = bardzo dobrze
- 10% MAPE = akceptowalnie

### Directional Accuracy
- % trafionych kierunków (wzrost/spadek)
- **50% = zgadywanie**
- **60%+ = warte uwagi**

---

## 9️⃣ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'tensorflow'"
**Rozwiązanie:**
```bash
pip install --upgrade tensorflow
```

### Problem: "Brak danych z Yahoo Finance"
**Rozwiązanie:**
- Sprawdź ticker (np. `AAPL` musi być duże litery)
- Spróbuj innego: `MSFT`, `PKN.WA`, `^GSPC`
- Yahoo Finance mogą być niedostępne – czekaj chwilę

### Problem: Program wysypuje się przy treningu
**Rozwiązanie:**
- Zmniejsz EPOCHS do 5
- Zmniejsz LOOKBACK do 30
- Ustaw HORIZON na 1 (zamiast 5)

### Problem: Prognoza jest zawsze "płaska"
**Rozwiązanie:**
- Zwiększ EPOCHS do 50
- Spróbuj innego modelu: kliknij "Porównaj modele"
- Model GRU może być lepszy dla Twojego tickera

---

## 🔟 Następne Kroki

### Dla Zaawansowanych
1. **Porównuj modele** → które są najlepsze dla każdego tickera?
2. **Walk-Forward Test** → najbardziej realistyczna walidacja
3. **Historia prognoz** → analiza wydajności w czasie
4. **Scheduling** → programowanie prognoz (edytuj kod)

### Dla Analityków
1. **Wskaźniki techniczne** → identyfikacja trendów
2. **Export raportów** → analiza w Excelu
3. **Backtest CSV** → porównanie z rzeczywistością

### Dla Inwestorów
1. Ustawiaj alerty → monituj ceny automatycznie
2. Porównuj tickery → którzy najlepiej się prognozują?
3. Historia prognoz → które modele Ci służyły?

---

## ✅ Checklist – Czy Gotowy?

- [ ] Python zainstalowany (3.8+)
- [ ] Zależności zainstalowane (`pip install -r requirements.txt`)
- [ ] Program uruchomiony (`python gielda_lstm_gui.py`)
- [ ] Model wytrenowany ("Trenuj model" ✅)
- [ ] Pierwsza prognoza wygenerowana ("Prognozuj" ✅)
- [ ] Wykresy i pliki CSV w folderach ✅

---

## 💡 Pro Tips

1. **Szybkie Testowanie**: EPOCHS=5, LOOKBACK=30 → szybko sprawdzisz czy działa
2. **Dokładne Prognozy**: EPOCHS=50, LOOKBACK=90 → bardziej dokładne ale wolne
3. **Porównanie Akcji**: Trenuj ten sam model dla różnych tickerów → która akacja najłatwiej się prognozuje?
4. **Analiza Trendów**: Wskaźniki techniczne → lepsze zrozumienie rynku
5. **Backup Danych**: Regularnie exportuj CSV → analiza w Excelu

---

## 📞 Pomoc

Jeśli coś nie działa:
1. Przeczytaj log w oknie "Log / wyniki"
2. Sprawdź foldery (prognozy/, wykresy/)
3. Sprawdź README.md w folderze
4. Zbadaj bazę danych SQLite

---

**Gotowy do zarabiania na akcjach?** 📈🚀

Pamiętaj: **Prognoza to nie gwarancja!** Zawsze rób własne badania przed inwestycją.

---

*Powodzenia! Wersja 2.0 – LSTM System z ML, Walidacją, Bazą Danych i Schedulingiem* 🎉
