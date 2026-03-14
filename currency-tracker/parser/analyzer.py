"""
Модуль анализа валютных данных
"""

from database import Database
from datetime import datetime


class CurrencyAnalyzer:
    def __init__(self):
        self.db = Database()
        self.db.connect()

    def get_trend_analysis(self, base_currency, target_currency, days=7):
        """Анализ тренда валютной пары"""
        self.db.cursor.execute(
            "SELECT get_trend(%s, %s, %s)", (base_currency, target_currency, days)
        )
        result = self.db.cursor.fetchone()
        return result[0] if result else None

    def get_rsi(self, base_currency, target_currency, period=14):
        """RSI индикатор"""
        self.db.cursor.execute(
            "SELECT calculate_rsi(%s, %s, %s)", (base_currency, target_currency, period)
        )
        result = self.db.cursor.fetchone()
        return float(result[0]) if result and result[0] else None

    def predict_rate(self, base_currency, target_currency, days=7):
        """Прогноз курса на основе SMA"""
        self.db.cursor.execute(
            "SELECT predict_rate_sma(%s, %s, %s)", (base_currency, target_currency, days)
        )
        result = self.db.cursor.fetchone()
        return float(result[0]) if result and result[0] else None

    def find_arbitrage(self, date=None):
        """Поиск арбитражных возможностей"""
        if date is None:
            date = datetime.now().date()
        self.db.cursor.execute("SELECT * FROM find_arbitrage_opportunities(%s)", (date,))
        return [
            {'currency_a': r[0], 'currency_b': r[1], 'currency_c': r[2], 'profit_percent': float(r[3])}
            for r in self.db.cursor.fetchall()
        ]

    def get_volatility_ranking(self, days=7):
        """Рейтинг валют по волатильности"""
        self.db.cursor.execute(
            """SELECT base_currency || '/' || target_currency,
                      COALESCE(STDDEV(rate), 0),
                      AVG(rate),
                      COUNT(*)
               FROM exchange_rates
               WHERE rate_date >= CURRENT_DATE - (%s || ' days')::INTERVAL
               GROUP BY base_currency, target_currency
               HAVING COUNT(*) >= 3
               ORDER BY 2 DESC
               LIMIT 10""",
            (days,)
        )
        return [
            {'currency_pair': r[0], 'volatility': float(r[1]), 'avg_rate': float(r[2]), 'data_points': r[3]}
            for r in self.db.cursor.fetchall()
        ]

    def get_correlation(self, pair1, pair2, days=30):
        """Корреляция между двумя валютными парами"""
        base1, target1 = pair1.split('/')
        base2, target2 = pair2.split('/')
        self.db.cursor.execute(
            """WITH p1 AS (
                   SELECT rate_date, rate FROM exchange_rates
                   WHERE base_currency=%s AND target_currency=%s
                     AND rate_date >= CURRENT_DATE - (%s||' days')::INTERVAL
               ), p2 AS (
                   SELECT rate_date, rate FROM exchange_rates
                   WHERE base_currency=%s AND target_currency=%s
                     AND rate_date >= CURRENT_DATE - (%s||' days')::INTERVAL
               )
               SELECT CORR(p1.rate, p2.rate) FROM p1 JOIN p2 USING (rate_date)""",
            (base1, target1, days, base2, target2, days)
        )
        result = self.db.cursor.fetchone()
        return float(result[0]) if result and result[0] else None

    def check_alerts(self):
        """Проверка алертов"""
        self.db.cursor.execute("SELECT * FROM check_alerts()")
        return [
            {'alert_id': r[0], 'currency_pair': r[1], 'alert_type': r[2], 'message': r[3]}
            for r in self.db.cursor.fetchall()
        ]

    def generate_report(self, currency_pair, days=30):
        """Генерация аналитического отчёта"""
        base, target = currency_pair.split('/')
        report = {
            'currency_pair': currency_pair,
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'trend': self.get_trend_analysis(base, target, days),
            'rsi': self.get_rsi(base, target),
            'predicted_rate': self.predict_rate(base, target),
        }
        self.db.cursor.execute(
            """SELECT AVG(rate), MIN(rate), MAX(rate), STDDEV(rate),
                      COUNT(*), MIN(rate_date), MAX(rate_date)
               FROM exchange_rates
               WHERE base_currency=%s AND target_currency=%s
                 AND rate_date >= CURRENT_DATE - (%s||' days')::INTERVAL""",
            (base, target, days)
        )
        s = self.db.cursor.fetchone()
        report['statistics'] = {
            'avg_rate':   float(s[0]) if s[0] else None,
            'min_rate':   float(s[1]) if s[1] else None,
            'max_rate':   float(s[2]) if s[2] else None,
            'volatility': float(s[3]) if s[3] else None,
            'data_points': s[4],
            'date_from':  s[5].isoformat() if s[5] else None,
            'date_to':    s[6].isoformat() if s[6] else None,
        }
        return report

    def close(self):
        self.db.disconnect()
