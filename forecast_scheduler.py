# forecast_scheduler.py

"""
Moduł do scheduling i automatycznego monitoringu prognoz.
- Harmonogram uruchamiania prognoz
- Powiadomienia (email, desktop)
- Automatyczne alerty cenowe
"""

import schedule
import time
import threading
from datetime import datetime, time as dt_time
from typing import Callable, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class ForecastScheduler:
    """Klasa do planowania prognoz."""
    
    def __init__(self):
        self.jobs = []
        self.is_running = False
        self.scheduler_thread = None
    
    def schedule_daily_forecast(self, ticker_list, time_of_day, forecast_func, 
                               lookback=60, horizon=5, **kwargs):
        """
        Zaplanuj dzienną prognozę.
        
        Args:
            ticker_list: lista tickerów do prognozowania
            time_of_day: godzina (format "HH:MM", np. "09:30")
            forecast_func: funkcja do generowania prognozy
            lookback, horizon: parametry modelu
            **kwargs: dodatkowe argumenty dla funkcji
        """
        def run_forecasts():
            for ticker in ticker_list:
                try:
                    forecast_func(ticker, lookback=lookback, horizon=horizon, **kwargs)
                except Exception as e:
                    print(f"❌ Błąd podczas prognozy {ticker}: {e}")
        
        schedule.every().day.at(time_of_day).do(run_forecasts)
        self.jobs.append({
            'tickers': ticker_list,
            'time': time_of_day,
            'type': 'daily'
        })
        
        print(f"✅ Zaplanowano dzienną prognozę o {time_of_day} dla: {ticker_list}")
    
    def schedule_recurring_forecast(self, ticker_list, interval_minutes, forecast_func,
                                   lookback=60, horizon=5, **kwargs):
        """
        Zaplanuj periodyczne prognozy.
        
        Args:
            ticker_list: lista tickerów
            interval_minutes: interwał w minutach
            forecast_func: funkcja prognozy
            lookback, horizon: parametry modelu
        """
        def run_forecasts():
            for ticker in ticker_list:
                try:
                    forecast_func(ticker, lookback=lookback, horizon=horizon, **kwargs)
                except Exception as e:
                    print(f"❌ Błąd podczas prognozy {ticker}: {e}")
        
        schedule.every(interval_minutes).minutes.do(run_forecasts)
        self.jobs.append({
            'tickers': ticker_list,
            'interval_minutes': interval_minutes,
            'type': 'recurring'
        })
        
        print(f"✅ Zaplanowano periodyczną prognozę co {interval_minutes} minut dla: {ticker_list}")
    
    def start_scheduler(self):
        """Uruchom harmonogram w osobnym wątku."""
        if self.is_running:
            print("⚠️ Harmonogram już jest uruchomiony.")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        print("✅ Harmonogram prognoz uruchomiony.")
    
    def _scheduler_loop(self):
        """Główna pętla harmonogramu."""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Sprawdzaj co minutę
    
    def stop_scheduler(self):
        """Zatrzymaj harmonogram."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        print("⏹️  Harmonogram zatrzymany.")
    
    def get_scheduled_jobs(self):
        """Pobierz listę zaplanowanych zadań."""
        return self.jobs


class AlertManager:
    """Zarządzanie alertami cenowymi."""
    
    def __init__(self, check_interval_seconds=300):
        """
        Inicjalizuj menedżer alertów.
        
        Args:
            check_interval_seconds: interwał sprawdzania cen w sekundach
        """
        self.alerts = {}  # {ticker: {'above': price, 'below': price}}
        self.check_interval = check_interval_seconds
        self.is_monitoring = False
        self.monitor_thread = None
    
    def set_price_alert(self, ticker, above_price=None, below_price=None):
        """
        Ustaw alert na cenę.
        
        Args:
            ticker: symbol akcji
            above_price: alert gdy cena będzie powyżej
            below_price: alert gdy cena będzie poniżej
        """
        if ticker not in self.alerts:
            self.alerts[ticker] = {}
        
        if above_price:
            self.alerts[ticker]['above'] = above_price
        if below_price:
            self.alerts[ticker]['below'] = below_price
        
        print(f"✅ Alert ustawiony dla {ticker.upper()}")
    
    def start_monitoring(self, price_check_func):
        """
        Uruchom monitoring cen.
        
        Args:
            price_check_func: funkcja pobierająca aktualną cenę (ticker -> price)
        """
        if self.is_monitoring:
            print("⚠️ Monitoring już jest aktywny.")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(price_check_func,),
            daemon=True
        )
        self.monitor_thread.start()
        print("✅ Monitoring cen uruchomiony.")
    
    def _monitor_loop(self, price_check_func):
        """Główna pętla monitoringu."""
        while self.is_monitoring:
            for ticker, alert_levels in self.alerts.items():
                try:
                    current_price = price_check_func(ticker)
                    
                    if 'above' in alert_levels and current_price > alert_levels['above']:
                        msg = f"🔔 ALERT: {ticker} powyżej {alert_levels['above']:.2f} (aktualnie: {current_price:.2f})"
                        self._trigger_alert(ticker, msg)
                    
                    if 'below' in alert_levels and current_price < alert_levels['below']:
                        msg = f"🔔 ALERT: {ticker} poniżej {alert_levels['below']:.2f} (aktualnie: {current_price:.2f})"
                        self._trigger_alert(ticker, msg)
                
                except Exception as e:
                    print(f"⚠️ Błąd podczas sprawdzenia {ticker}: {e}")
            
            time.sleep(self.check_interval)
    
    def _trigger_alert(self, ticker, message):
        """Wyzwól alert."""
        print(message)
        # Tutaj można dodać powiadomienia email lub desktop
    
    def stop_monitoring(self):
        """Zatrzymaj monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️  Monitoring zatrzymany.")


class NotificationManager:
    """Zarządzanie powiadomienimi."""
    
    def __init__(self, email_config=None):
        """
        Inicjalizuj menedżer powiadomień.
        
        Args:
            email_config: dict {'sender': email, 'password': pwd, 'smtp_server': server, 'port': port}
        """
        self.email_config = email_config
        self.notification_log = []
    
    def send_email_notification(self, recipient, subject, body):
        """
        Wyślij powiadomienie email.
        
        Args:
            recipient: email odbiorcy
            subject: temat
            body: treść wiadomości
        """
        if not self.email_config:
            print("⚠️ Email nie skonfigurowany.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['port'])
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.notification_log.append({
                'type': 'email',
                'recipient': recipient,
                'subject': subject,
                'timestamp': datetime.now()
            })
            
            print(f"📧 Email wysłany do {recipient}")
            return True
        
        except Exception as e:
            print(f"❌ Błąd przy wysyłaniu emaila: {e}")
            return False
    
    def send_desktop_notification(self, title, message):
        """
        Wyślij powiadomienie pulpitu.
        
        Args:
            title: tytuł
            message: treść
        """
        try:
            # Dla macOS
            import os
            os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
            
            self.notification_log.append({
                'type': 'desktop',
                'title': title,
                'timestamp': datetime.now()
            })
            
            print(f"🔔 Powiadomienie pulpitu: {title}")
            return True
        
        except Exception as e:
            print(f"⚠️ Błąd przy wysyłaniu powiadomienia: {e}")
            return False
    
    def get_notification_log(self):
        """Pobierz log powiadomień."""
        return self.notification_log


class MonitoringDashboard:
    """Dashboard do monitorowania prognoz."""
    
    def __init__(self):
        self.active_forecasts = {}
        self.alerts = {}
        self.performance_metrics = {}
    
    def add_forecast(self, ticker, forecast_data):
        """Dodaj prognozę do dashboardu."""
        self.active_forecasts[ticker] = {
            'data': forecast_data,
            'timestamp': datetime.now()
        }
    
    def add_alert(self, ticker, alert_type, value):
        """Dodaj alert do dashboardu."""
        if ticker not in self.alerts:
            self.alerts[ticker] = []
        
        self.alerts[ticker].append({
            'type': alert_type,
            'value': value,
            'timestamp': datetime.now()
        })
    
    def update_metrics(self, ticker, metrics):
        """Aktualizuj metryki modelu."""
        self.performance_metrics[ticker] = {
            'metrics': metrics,
            'timestamp': datetime.now()
        }
    
    def get_dashboard_summary(self):
        """Pobierz podsumowanie dashboardu."""
        return {
            'active_forecasts': len(self.active_forecasts),
            'active_alerts': sum(len(a) for a in self.alerts.values()),
            'monitored_tickers': list(self.active_forecasts.keys()),
            'last_update': datetime.now()
        }
