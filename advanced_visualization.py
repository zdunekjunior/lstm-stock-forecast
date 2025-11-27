# advanced_visualization.py

"""
Moduł do zaawansowanej wizualizacji:
- Wykresy z przedziałami ufności
- Porównanie wielu tickerów
- Export do PDF
- Interaktywne wykresy
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os


class AdvancedVisualizer:
    """Klasa do zaawansowanej wizualizacji danych."""

    @staticmethod
    def plot_forecast_with_intervals(dates, actual, forecast, lower, upper, ticker, 
                                     title=None, figsize=(14, 7), save_path=None):
        """
        Narysuj prognozę z przedziałami ufności.
        
        Args:
            dates: daty dla osi x
            actual: rzeczywiste ceny (Historia)
            forecast: prognozowane ceny
            lower: dolny przedział ufności
            upper: górny przedział ufności
            ticker: symbol akcji
            title: tytuł wykresu
            figsize: rozmiar figury
            save_path: ścieżka do zapisania
        """
        plt.figure(figsize=figsize)
        
        # Historia
        plt.plot(dates[:len(actual)], actual, 'b-', linewidth=2, label='Historia (Close)', alpha=0.8)
        
        # Prognoza
        forecast_dates = dates[len(actual):]
        plt.plot(forecast_dates, forecast, 'r-o', linewidth=2, label='Prognoza', markersize=6)
        
        # Przedziały ufności
        plt.fill_between(forecast_dates, lower, upper, alpha=0.2, color='red', 
                         label='95% przedział ufności')
        
        if title is None:
            title = f"Prognoza kursu {ticker.upper()}"
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Data', fontsize=12)
        plt.ylabel('Cena', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Wykres zapisany: {save_path}")
        
        return plt

    @staticmethod
    def plot_multiple_tickers(ticker_data, figsize=(15, 8), save_path=None):
        """
        Porównaj wiele tickerów na jednym wykresie.
        
        Args:
            ticker_data: dict {ticker: prices}
            figsize: rozmiar figury
            save_path: ścieżka do zapisania
        """
        plt.figure(figsize=figsize)
        
        for ticker, prices in ticker_data.items():
            # Normalizuj ceny do zakresu 0-100 dla porównania
            normalized = (prices - np.min(prices)) / (np.max(prices) - np.min(prices)) * 100
            plt.plot(range(len(normalized)), normalized, marker='o', label=ticker, linewidth=2, alpha=0.8)
        
        plt.title('Porównanie tickerów (znormalizowane 0-100)', fontsize=14, fontweight='bold')
        plt.xlabel('Dni', fontsize=12)
        plt.ylabel('Znormalizowana cena', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Wykres porównawczy zapisany: {save_path}")
        
        return plt

    @staticmethod
    def plot_indicators(dates, close, rsi, macd, sma20, sma50, figsize=(14, 10), save_path=None):
        """
        Narysuj cenę z wskaźnikami technicznymi.
        
        Args:
            dates: daty
            close: ceny Close
            rsi: wartości RSI
            macd: wartości MACD
            sma20: SMA(20)
            sma50: SMA(50)
            figsize: rozmiar figury
            save_path: ścieżka do zapisania
        """
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
        
        # Panelom 1: Cena z SMA
        axes[0].plot(dates, close, 'b-', linewidth=2, label='Close', alpha=0.8)
        axes[0].plot(dates, sma20, 'r--', linewidth=1.5, label='SMA(20)', alpha=0.7)
        axes[0].plot(dates, sma50, 'g--', linewidth=1.5, label='SMA(50)', alpha=0.7)
        axes[0].set_ylabel('Cena', fontsize=11)
        axes[0].set_title('Cena z Moving Averages', fontsize=12, fontweight='bold')
        axes[0].legend(loc='best', fontsize=9)
        axes[0].grid(True, alpha=0.3)
        
        # Panel 2: RSI
        axes[1].plot(dates, rsi, 'purple', linewidth=2, label='RSI(14)', alpha=0.8)
        axes[1].axhline(y=70, color='r', linestyle='--', linewidth=1, label='Overbought (70)', alpha=0.5)
        axes[1].axhline(y=30, color='g', linestyle='--', linewidth=1, label='Oversold (30)', alpha=0.5)
        axes[1].fill_between(dates, 30, 70, alpha=0.1, color='gray')
        axes[1].set_ylabel('RSI', fontsize=11)
        axes[1].set_ylim([0, 100])
        axes[1].set_title('Relative Strength Index', fontsize=12, fontweight='bold')
        axes[1].legend(loc='best', fontsize=9)
        axes[1].grid(True, alpha=0.3)
        
        # Panel 3: MACD
        axes[2].plot(dates, macd, 'blue', linewidth=2, label='MACD', alpha=0.8)
        axes[2].axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.3)
        axes[2].fill_between(dates, 0, macd, where=(macd >= 0), alpha=0.3, color='green', label='Bullish')
        axes[2].fill_between(dates, 0, macd, where=(macd < 0), alpha=0.3, color='red', label='Bearish')
        axes[2].set_ylabel('MACD', fontsize=11)
        axes[2].set_xlabel('Data', fontsize=11)
        axes[2].set_title('MACD (Moving Average Convergence Divergence)', fontsize=12, fontweight='bold')
        axes[2].legend(loc='best', fontsize=9)
        axes[2].grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Wskaźniki zapisane: {save_path}")
        
        return fig

    @staticmethod
    def plot_backtest_results(dates, actual, forecast, figsize=(14, 7), save_path=None):
        """
        Narysuj wyniki backtestu.
        
        Args:
            dates: daty
            actual: rzeczywiste wartości
            forecast: wartości prognozowane
            figsize: rozmiar figury
            save_path: ścieżka do zapisania
        """
        plt.figure(figsize=figsize)
        
        plt.plot(dates, actual, 'b-o', linewidth=2, label='Rzeczywiste', markersize=4, alpha=0.8)
        plt.plot(dates, forecast, 'r--s', linewidth=2, label='Prognoza', markersize=4, alpha=0.8)
        
        # Zaznacz błędy
        errors = actual - forecast
        colors = ['green' if e > 0 else 'red' for e in errors]
        plt.scatter(dates, actual, c=colors, s=50, alpha=0.5)
        
        plt.title('Backtest: Prognoza vs Rzeczywistość', fontsize=14, fontweight='bold')
        plt.xlabel('Data', fontsize=12)
        plt.ylabel('Cena', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Backtest zapisany: {save_path}")
        
        return plt

    @staticmethod
    def plot_error_distribution(errors, figsize=(12, 5), save_path=None):
        """
        Narysuj rozkład błędów.
        
        Args:
            errors: błędy (actual - forecast)
            figsize: rozmiar figury
            save_path: ścieżka do zapisania
        """
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram
        axes[0].hist(errors, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Błąd', fontsize=11)
        axes[0].set_ylabel('Częstość', fontsize=11)
        axes[0].set_title('Rozkład błędów predykcji', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # QQ plot
        from scipy import stats
        stats.probplot(errors, dist="norm", plot=axes[1])
        axes[1].set_title('Q-Q Plot (normalność błędów)', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Rozkład błędów zapisany: {save_path}")
        
        return fig


class PDFExporter:
    """Eksport raportów do PDF (wymaga reportlab)."""
    
    @staticmethod
    def export_forecast_report(ticker, forecast_data, output_path):
        """
        Eksportuj raport prognozy do PDF.
        Wymaga: pip install reportlab
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Tytuł
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph(f"Raport prognozy kursu {ticker.upper()}", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Dane
            data = [
                ['Data wygenerowania', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ['Symbol', ticker.upper()],
                ['Liczba dni prognozy', str(len(forecast_data))],
            ]
            
            table = Table(data, colWidths=[2.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # Dane prognozy
            forecast_data_table = [['Dzień', 'Cena', 'Dolny przedział', 'Górny przedział']]
            for i, row in enumerate(forecast_data, start=1):
                forecast_data_table.append([
                    f"D+{i}",
                    f"{row.get('price', 0):.2f}",
                    f"{row.get('lower', 0):.2f}",
                    f"{row.get('upper', 0):.2f}",
                ])
            
            forecast_table = Table(forecast_data_table, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            forecast_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(forecast_table)
            
            doc.build(story)
            print(f"📄 Raport PDF zapisany: {output_path}")
            
        except ImportError:
            print("⚠️ ReportLab nie jest zainstalowany. Aby eksportować PDF, uruchom: pip install reportlab")
