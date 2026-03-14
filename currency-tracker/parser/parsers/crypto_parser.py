"""
Парсер криптовалют через CoinGecko API (бесплатный, без ключа)
"""
import requests
from datetime import date


CRYPTO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "TON": "the-open-network",
}

VS_CURRENCIES = ["usd", "rub", "eur"]


class CryptoParser:
    """Парсер курсов криптовалют через CoinGecko"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "CurrencyTracker/2.0"

    def fetch(self):
        """Получить текущие курсы всех крипто"""
        ids = ",".join(CRYPTO_IDS.values())
        vs = ",".join(VS_CURRENCIES)
        url = f"{self.BASE_URL}/simple/price"
        params = {"ids": ids, "vs_currencies": vs}
        resp = self.session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def parse(self, data):
        """Парсинг ответа CoinGecko"""
        rates = []
        today = date.today()

        # Обратный маппинг: coingecko_id -> ticker
        id_to_ticker = {v: k for k, v in CRYPTO_IDS.items()}

        for cg_id, prices in data.items():
            ticker = id_to_ticker.get(cg_id)
            if not ticker:
                continue
            for vs_curr, price in prices.items():
                if price is None:
                    continue
                rates.append({
                    "base_currency":   ticker,
                    "target_currency": vs_curr.upper(),
                    "rate":            float(price),
                    "rate_date":       today,
                })

        return rates
