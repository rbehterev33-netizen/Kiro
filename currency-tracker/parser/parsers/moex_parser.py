"""
Парсер Московской биржи (MOEX)
Реальные биржевые курсы через ISS API
"""
import requests
from datetime import datetime, date


class MOEXParser:
    """Парсер данных Московской биржи через ISS API"""

    BASE_URL = "https://iss.moex.com/iss"

    # Тикеры валютных пар на MOEX
    PAIRS = {
        "USD000UTSTOM": ("USD", "RUB"),
        "EUR_RUB__TOM": ("EUR", "RUB"),
        "CNYRUB_TOM":   ("CNY", "RUB"),
        "GBPRUB_TOM":   ("GBP", "RUB"),
        "JPYRUB_TOM":   ("JPY", "RUB"),
        "CHFRUB_TOM":   ("CHF", "RUB"),
        "HKDRUB_TOM":   ("HKD", "RUB"),
        "TRYRUB_TOM":   ("TRY", "RUB"),
    }

    def __init__(self):
        self.base_currency = "RUB"
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "CurrencyTracker/2.0"

    def fetch(self):
        """Получить последние торги по всем парам"""
        url = f"{self.BASE_URL}/engines/currency/markets/selt/securities.json"
        params = {
            "securities": ",".join(self.PAIRS.keys()),
            "iss.meta": "off",
            "iss.only": "marketdata,securities",
        }
        resp = self.session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def parse(self, data):
        """Парсинг ответа ISS API"""
        rates = []
        today = date.today()

        try:
            # Индексы колонок в marketdata
            md = data.get("marketdata", {})
            cols = md.get("columns", [])
            rows = md.get("data", [])

            secid_idx = cols.index("SECID")
            last_idx  = cols.index("LAST")

            # Берём последнюю ненулевую цену по каждому тикеру
            best = {}
            for row in rows:
                secid = row[secid_idx]
                if secid not in self.PAIRS:
                    continue
                last = row[last_idx]
                if last is None or last == 0:
                    continue
                best[secid] = float(last)

            for secid, price in best.items():
                base, target = self.PAIRS[secid]
                rates.append({
                    "base_currency":   base,
                    "target_currency": target,
                    "rate":            price,
                    "rate_date":       today,
                    "ticker":          secid,
                })

        except Exception as e:
            raise Exception(f"Ошибка парсинга MOEX: {e}")

        return rates

    def fetch_history(self, ticker: str, date_from: date, date_till: date):
        """История торгов по тикеру за период"""
        url = (
            f"{self.BASE_URL}/engines/currency/markets/selt"
            f"/securities/{ticker}/candles.json"
        )
        params = {
            "from":      date_from.strftime("%Y-%m-%d"),
            "till":      date_till.strftime("%Y-%m-%d"),
            "interval":  24,   # дневные свечи
            "iss.meta":  "off",
        }
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        candles = data.get("candles", {})
        cols = candles.get("columns", [])
        rows = candles.get("data", [])

        close_idx = cols.index("close")
        begin_idx = cols.index("begin")

        result = []
        base, target = self.PAIRS.get(ticker, ("?", "?"))
        for row in rows:
            dt = datetime.strptime(row[begin_idx][:10], "%Y-%m-%d").date()
            result.append({
                "base_currency":   base,
                "target_currency": target,
                "rate":            float(row[close_idx]),
                "rate_date":       dt,
                "ticker":          ticker,
            })
        return result
