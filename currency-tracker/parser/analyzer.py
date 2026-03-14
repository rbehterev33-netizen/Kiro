"""
Модуль анализа валютных данных
"""

from database import Database
from datetime import datetime, timedelta

class CurrencyAnalyzer:
    def __init__(self):
        self.db = Database()
        self.db.connect()
    
    def get_trend_analysis(self, base_currency, target_currency, days=7):
        """Анализ тренда валютной пары"""
        query = """
            SELECT get_trend(%s, %s, %s) AS trend
        """
        self.db.cursor.execute(query, (base_currency, target_currency, days))
        result = self.db.cursor.fetchone()
        return result[0] if result else None
    
    def get_rsi(self, base_currency, target_currency, period=14):
        """Получение RSI индикатора"""
        query = """
            SELECT calculate_rsi(%s, %s, %s) AS rsi
        """
        self.db.cursor.execute(query, (base_currency, target_currency, period))
        result = self.db.cursor.fetchone()
        return float(result[0]) if result else None
    
    def predict_rate(self, base_currency, target_currency, days=7):
        """Прогноз курса на основе скользящего среднего"""
        query = """
            SELECT predict_rate_sma(%s, %s, %s) AS predicted_rate
        """
        self.db.cursor.execute(query, (base_currency, target_currency, days))
        result = self.db.cursor.fetchone()
        return float(result[0]) if result else None
    
    def find_arbitrage(self, date=None):
        """Поиск арбитражных возможностей"""
        if date is None:
            date = datetime.now().date()
        
        query = """
            SELECT * FROM find_arbitrage_opportunities(%s)
        """
        self.db.cursor.execute(query, (date,))
        results = self.db.cursor.fetchall()
        
        opportunities = []
        for row in results:
            opportunities.append({
                'currency_a': row[0],
                'currency_b': row[1],
                'currency_c': row[2],
                'profit_percent': float(row[3])
            })
        
        return opportunities
    
    def get_volatility_ranking(self, days=7):
        """Рейтинг валют по волатильности"""
        query = """
            SELECT 
                base_currency || '/' || target_currency AS currency_pair,
                STDDEV(rate) AS volatility,
                AVG(rate) AS avg_rate,
                COUNT(*) AS data_points
            FROM exchange_rates
            WHERE rate_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY base_currency, target_currency
            HAVING COUNT(*) >= 5
            ORDER BY volatility DESC
            LIMIT 10
        """
        self.db.cursor.execute(query, (days,))
        results = self.db.cursor.fetchall()
        
        ranking = []
        for row in results:
            ranking.append({
                'currency_pair': row[0],
                'volatility': float(row[1]) if row[1] else 0,
                'avg_rate': float(row[2]),
                'data_points': row[3]
            })
        
        return ranking
    
    def get_correlation(self, pair1, pair2, days=30):
        """Корреляция между двумя валютными парами"""
        base1, target1 = pair1.split('/')
        base2, target2 = pair2.split('/')
        
        query = """
            WITH pair1 AS (
                SELECT rate_date, rate AS rate1
                FROM exchange_rates
                WHERE base_currency = %s AND target_currency = %s
                  AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
            ),
            pair2 AS (
                SELECT rate_date, rate AS rate2
                FROM exchange_rates
                WHERE base_currency = %s AND target_currency = %s
                  AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
            )
            SELECT CORR(p1.rate1, p2.rate2) AS correlation
            FROM pair1 p1
            JOIN pair2 p2 ON p1.rate_date = p2.rate_date
        """
        self.db.cursor.execute(query, (base1, target1, days, base2, target2, days))
        result = self.db.cursor.fetchone()
        return float(result[0]) if result and result[0] else None
    
    def check_alerts(self):
        """Проверка алертов"""
        query = "SELECT * FROM check_alerts()"
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        
        alerts = []
        for row in results:
            alerts.append({
                'alert_id': row[0],
                'currency_pair': row[1],
                'alert_type': row[2],
                'message': row[3]
            })
        
        return alerts
    
    def generate_report(self, currency_pair, days=30):
        """Генерация аналитического отчета"""
        base, target = currency_pair.split('/')
        
        report = {
            'currency_pair': currency_pair,
            'period_days': days,
            'generated_at': datetime.now().isoformat()
        }
        
        # Тренд
        report['trend'] = self.get_trend_analysis(base, target, days)
        
        # RSI
        report['rsi'] = self.get_rsi(base, target)
        
        # Прогноз
        report['predicted_rate'] = self.predict_rate(base, target)
        
        # Статистика
        query = """
            SELECT 
                AVG(rate) AS avg_rate,
                MIN(rate) AS min_rate,
                MAX(rate) AS max_rate,
                STDDEV(rate) AS volatility
            FROM exchange_rates
            WHERE base_currency = %s 
              AND target_currency = %s
              AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
        """
        self.db.cursor.execute(query, (base, target, days))
        stats = self.db.cursor.fetchone()
        
        if stats:
            report['statistics'] = {
                'avg_rate': float(stats[0]) if stats[0] else None,
                'min_rate': float(stats[1]) if stats[1] else None,
                'max_rate': float(stats[2]) if stats[2] else None,
                'volatility': float(stats[3]) if stats[3] else None
            }
        
        return report
    
    def close(self):
        """Закрытие соединения"""
        self.db.disconnect()
