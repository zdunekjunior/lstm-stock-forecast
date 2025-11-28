# 🧠 Market Sentiment Analysis – Setup Complete!

## ✅ Status

- ✅ API Key skonfigurowany: `11b87ab830ac4e61ac6b92066a5a578f`
- ✅ Moduł `market_sentiment.py` zainstalowany i testowany
- ✅ GUI `gielda_lstm_gui.py` zaktualizowany z nowym przyciskiem
- ✅ NewsAPI integracja działa

---

## 🚀 Jak Używać

### 1. Uruchom aplikację:

```bash
cd /Users/mateuszzdunek/Desktop/Gielda
export NEWSAPI_KEY="11b87ab830ac4e61ac6b92066a5a578f"
python gielda_lstm_gui.py
```

### 2. W aplikacji:
- Wpisz ticker (np. **AAPL**, **SPY**, **^GSPC**)
- Kliknij przycisk **🧠 Nastrój rynku** w sekcji "⚙️ Zaawansowane"

### 3. Wynik:
```
================ NASTRÓJ RYNKU - AAPL ================
Pobieram newsy i liczę sentyment...
🔎 Liczba newsów: 14
🧠 Średni sentyment (−1…+1): 0.143
   Pozytywne: 14.3% | Negatywne: 0.0% | Neutralne: 85.7%
📌 Wniosek: sentyment mieszany / neutralny

📰 Przykładowe nagłówki:
 - Apple shares hit new all-time closing high... (score=0.000)
 - Will AI stocks crash or surge? Dan Ives reveals top 10 picks... (score=0.000)
 - ... (score=0.000)
```

---

## 📊 Co Mówi Sentyment?

| Średni Sentyment | Interpretacja |
|------------------|---------------|
| **> +0.2** | 📈 Bullish – przewaga pozytywnych newsów |
| **+0.1 do +0.2** | ⬆️ Lekko pozytywny |
| **-0.1 do +0.1** | ➡️ Neutralny / Mieszany |
| **-0.2 do -0.1** | ⬇️ Lekko negatywny |
| **< -0.2** | 📉 Bearish – przewaga negatywnych newsów |

---

## 🔑 API Key Info

- **Źródło:** https://newsapi.org
- **Klucz:** `11b87ab830ac4e61ac6b92066a5a578f`
- **Limit:** Zwykle 100-500 requestów dziennie (free plan)
- **Języki:** Można zmienić w `market_sentiment.py` (domyślnie: EN)

### Zmiana Języka Newsów

W `market_sentiment.py`:
```python
analyzer = MarketSentimentAnalyzer(language="pl")  # Nowości po polsku
```

---

## 🧪 Test (Już Wykonany!)

```
✅ Ticker: AAPL
📰 Liczba newsów: 14
🧠 Średni sentyment: 0.143
📊 Pozytywne: 14.3%
📊 Negatywne: 0.0%
📊 Neutralne: 85.7%
```

---

## 🛠️ Troubleshooting

### Błąd: "Brak klucza NEWSAPI_KEY"
**Rozwiązanie:** Zmienne środowiskowe nie są przekazywane do Python. Ustaw na stałe:

```bash
# macOS / Linux
echo 'export NEWSAPI_KEY="11b87ab830ac4e61ac6b92066a5a578f"' >> ~/.zshrc
source ~/.zshrc

# Windows PowerShell
setx NEWSAPI_KEY "11b87ab830ac4e61ac6b92066a5a578f"
```

### Błąd: "No articles found"
**Przyczyny:**
- Ticker nie istnieje (spróbuj: AAPL, SPY, MSFT)
- NewsAPI limit osiągnięty (czekaj 24h)
- Brak internetu

---

## 📁 Pliki

- ✅ `market_sentiment.py` – Analiza sentimentu
- ✅ `gielda_lstm_gui.py` – GUI z nowym przyciskiem
- ✅ `requirements.txt` – Zawiera `requests>=2.28.0`

---

## 🎯 Następne Kroki

1. ✅ Uruchom aplikację z nowym przyciskiem sentiment
2. ✅ Przetestuj z kilkoma tickerami
3. ✅ Obserwuj korelację między sentymentem a ceną

---

**Gotowe do użytku!** 🚀
