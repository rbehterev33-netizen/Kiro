#!/usr/bin/env python3
"""
Визуализация данных о курсах валют
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from database import Database

class CurrencyVisualizer:
    def __init__(self):
        self.db = Database()
        self.db.connect()
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_rate_history(self, base_currency, target_currency, days=30, save_path=None):
        """График истории курса"""
        query = """
            SELECT rate_date, rate
            FROM exchange_rates
            WHERE base_currency = %s 
              AND target_currency = %s
              AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY rate_date
        """
        self.db.cursor.execute(query, (base_currency, target_currency, days))
        results = self.db.cursor.fetchall()
        
        if not results:
            print("Нет данных для визуализации")
            return
        
        dates = [row[0] for row in results]
        rates = [float(row[1]) for row in results]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, rates, marker='o', linewidth=2, markersize=4)
        
        ax.set_title(f'{base_currency}/{target_currency} - История курса ({days} дней)', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Курс', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"График сохранен: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_comparison(self, pairs, days=30, save_path=None):
        """Сравнение нескольких валютных пар"""
        fig, ax = plt.subplots(figsize=(14, 7))
        
        for pair in pairs:
            base, target = pair.split('/')
            
            query = """
                SELECT rate_date, rate
                FROM exchange_rates
                WHERE base_currency = %s 
                  AND target_currency = %s
                  AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY rate_date
            """
            self.db.cursor.execute(query, (base, target, days))
            results = self.db.cursor.fetchall()
            
            if results:
                dates = [row[0] for row in results]
                rates = [float(row[1]) for row in results]
                
                # Нормализация к первому значению
                normalized = [r / rates[0] * 100 for r in rates]
                ax.plot(dates, normalized, marker='o', label=pair, linewidth=2, markersize=3)
        
        ax.set_title(f'Сравнение валютных пар (нормализовано, {days} дней)', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Изменение (%)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=100, color='r', linestyle='--', alpha=0.5)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"График сохранен: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_volatility(self, days=7, save_path=None):
        """График волатильности"""
        query = """
            SELECT 
                base_currency || '/' || target_currency AS pair,
                STDDEV(rate) AS volatility
            FROM exchange_rates
            WHERE rate_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY base_currency, target_currency
            HAVING COUNT(*) >= 5
            ORDER BY volatility DESC
            LIMIT 10
        """
        self.db.cursor.execute(query, (days,))
        results = self.db.cursor.fetchall()
        
        if not results:
            print("Нет данных для визуализации")
            return
        
        pairs = [row[0] for row in results]
        volatilities = [float(row[1]) for row in results]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(pairs, volatilities, color='steelblue')
        
        ax.set_title(f'Топ-10 волатильных пар ({days} дней)', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Волатильность (σ)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"График сохранен: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def close(self):
        """Закрытие соединения"""
        self.db.disconnect()
