# 🚀 INSTRUKCJA: Publikacja na GitHub

## ⚡ Szybka Ścieżka (3 kroki)

### **Krok 1: Stwórz repozytorium na GitHub**

```
1. Przejdź na: https://github.com/new
2. Nazwa: lstm-stock-forecast
3. Opis: "Advanced LSTM stock price prediction with modern GUI"
4. Public (opcjonalnie)
5. NIE wybieraj "Initialize with README" (już masz lokalnie)
6. Kliknij "Create repository"
```

### **Krok 2: Dodaj Remote i Push**

```bash
cd /Users/mateuszzdunek/Desktop/Gielda

# Dodaj GitHub jako origin
git remote add origin https://github.com/YOUR_USERNAME/lstm-stock-forecast.git

# Zmień branch na main (jeśli trzeba)
git branch -M main

# Wypchnij kod
git push -u origin main
```

**Zastąp `YOUR_USERNAME` swoją nazwą na GitHub!**

---

## 🔐 Autentykacja

### Opcja A: Token (Szybciej)
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generuj token (scope: `repo`)
3. Kopiuj token
4. Przy `git push` → wklej jako hasło

### Opcja B: SSH (Bezpieczniej)
```bash
# Jeśli NIE masz SSH keys:
ssh-keygen -t ed25519 -C "zdunekjunior@gmail.com"
cat ~/.ssh/id_ed25519.pub

# Dodaj klucz na GitHub (Settings → SSH and GPG keys)
# Potem użyj:
git remote add origin git@github.com:YOUR_USERNAME/lstm-stock-forecast.git
git push -u origin main
```

---

## 📊 Co Zostanie Zauploadowane

### ✅ Source Code (19 plików)
- `gielda_lstm_gui.py` – Główny program GUI
- 7 modułów ML (comparison, validation, indicators, itd.)
- Dokumentacja (5 markdown plików)
- `requirements.txt` – Zależności

### ❌ Ignorowane (`.gitignore`)
- `VirtualE/` – Virtual environment
- `*.keras`, `*.pkl` – Modele (za duże)
- `forecast_history.db` – Baza danych
- `prognozy/`, `wykresy/` – Generated files
- `__pycache__/` – Python cache

---

## 🎯 Po Opublikowaniu

1. **Dodaj Topics:**
   - lstm
   - stock-prediction
   - machine-learning
   - python
   - tkinter

2. **Opcjonalnie - Dodaj Badge do README:**
   ```markdown
   ![Python](https://img.shields.io/badge/Python-3.10+-blue)
   ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.11+-orange)
   ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
   ```

3. **Pinuj repozytorium** na profilu

---

## ✅ Status Lokalny

```
Repozytorium: ✅ Inicjalizowane
Pierwszy commit: ✅ Wykonany (4f096a2)
.gitignore: ✅ Dodany
Pliki: ✅ 19 tracked files
```

---

## 🎉 Gotowe!

Twój projekt jest gotowy do GitHub!

**Następny krok:** Wykonaj `git remote add origin ...` i `git push -u origin main`
