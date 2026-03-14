#!/usr/bin/env python3
"""
Экспорт данных в различные форматы
"""

import csv
import json
from datetime import datetime
from database import Database

class DataExporter:
    def __init__(self):
        self.db = Database()
        self.db.connect()
    
    def export_to_csv(self, base_currency, target_currency, days=30, filename=None):
        """Экспорт в CSV"""
        if filename is None:
            filename = f"{base_currency}_{target_currency}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        query = """
            SELECT 
                rate_date,
                rate,
                rate - LAG(rate) OVER (ORDER BY rate_date) AS change,
                ROUND(
                    ((rate - LAG(rate) OVER (ORDER BY rate_date)) / 
                    LAG(rate) OVER (ORDER BY rate_date) * 100)::NUMERIC, 
                    4
                ) AS change_percent
            FROM exchange_rates
            WHERE base_currency = %s 
              AND target_currency = %s
              AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY rate_date
        """
        self.db.cursor.execute(query, (base_currency, target_currency, days))
        results = self.db.cursor.fetchall()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Rate', 'Change', 'Change %'])
            
            for row in results:
                writer.writerow([
                    row[0].isoformat(),
                    float(row[1]),
                    float(row[2]) if row[2] else '',
                    float(row[3]) if row[3] else ''
                ])
        
        print(f"Данные экспортированы в {filename}")
        return filename
    
    def export_to_json(self, base_currency, target_currency, days=30, filename=None):
        """Экспорт в JSON"""
        if filename is None:
            filename = f"{base_currency}_{target_currency}_{datetime.now().strftime('%Y%m%d')}.json"
        
        query = """
            SELECT get_rate_history_json(%s, %s, %s)
        """
        self.db.cursor.execute(query, (base_currency, target_currency, days))
        result = self.db.cursor.fetchone()
        
        data = {
            'currency_pair': f"{base_currency}/{target_currency}",
            'period_days': days,
            'exported_at': datetime.now().isoformat(),
            'data': result[0] if result else []
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Данные экспортированы в {filename}")
        return filename
    
    def export_statistics(self, filename=None):
        """Экспорт статистики"""
        if filename is None:
            filename = f"statistics_{datetime.now().strftime('%Y%m%d')}.json"
        
        query = "SELECT * FROM v_weekly_statistics"
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        
        statistics = []
        for row in results:
            statistics.append({
                'currency_pair': row[0],
                'days_count': row[1],
                'avg_rate': float(row[2]) if row[2] else None,
                'min_rate': float(row[3]) if row[3] else None,
                'max_rate': float(row[4]) if row[4] else None,
                'rate_spread': float(row[5]) if row[5] else None,
                'volatility': float(row[6]) if row[6] else None,
                'period_start': row[7].isoformat() if row[7] else None,
                'period_end': row[8].isoformat() if row[8] else None
            })
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'statistics': statistics
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Статистика экспортирована в {filename}")
        return filename
    
    def close(self):
        """Закрытие соединения"""
        self.db.disconnect()
