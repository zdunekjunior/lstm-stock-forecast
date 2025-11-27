# 🔧 NAPRAWA BŁĘDU – ModuleNotFoundError

## Błąd
```
ModuleNotFoundError: No module named 'schedule'
ModuleNotFoundError: No module named 'numpy'
```

## Rozwiązanie

### Krok 1: Zainstaluj wszystkie zależności

```bash
cd ~/Desktop/Gielda
pip install -r requirements.txt
```

Lub ręcznie:
```bash
pip install yfinance tensorflow scikit-learn joblib matplotlib pandas numpy scipy reportlab schedule python-dateutil
```

### Krok 2: Sprawdź instalację

```bash
python -c "import numpy, pandas, yfinance, tensorflow, matplotlib; print('✅ OK')"
```

### Krok 3: Uruchom program

```bash
python gielda_lstm_gui.py
```

---

## Alternatywa: Użyj Requirements

```bash
pip install -r requirements.txt
python gielda_lstm_gui.py
```

---

## Jeśli TensorFlow ma problemy

Jeśli TensorFlow się nie ładuje szybko, użyj wersji CPU:

```bash
pip install tensorflow-cpu
```

Lub zainstaluj bardziej stabilną wersję:

```bash
pip install tensorflow==2.11.0
```

---

## Sprawdzenie Wersji Python

```bash
python --version
# Wymagane: Python 3.8+
```

---

## Jeśli Dalej Nie Działa

1. Usuń venv i stwórz nowy:
```bash
rm -rf ~/Desktop/Gielda/.venv
python3 -m venv ~/Desktop/Gielda/.venv
source ~/Desktop/Gielda/.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Uruchom program:
```bash
python gielda_lstm_gui.py
```

---

## Pomoc

Jeśli błąd nadal występuje, plik logs zawiera szczegóły (patrz okno aplikacji).

Program powinien uruchomić się bez moduł`ów zaawansowanych (porównanie, analiza, baza danych) ale podstawowe funkcje (trenuj, prognozuj) będą dostępne.

---

**Powodzenia!** 🚀
