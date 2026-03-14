#!/usr/bin/env python3
"""
FastAPI сервер для Currency Tracker
Документация: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
from analyzer import CurrencyAnalyzer
from database import Database

app = FastAPI(
    title="Currency Tracker API",
    description="API для получения и анализа курсов валют",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Модели ответов ---

class RateItem(BaseModel):
    base_currency: str
    target_currency: str
    currency_pair: str
    rate: float
    rate_date: str
    source_name: str

class HistoryItem(BaseModel):
    date: str
    rate: float

class ConvertResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    result: Optional[float]

class VolatilityItem(BaseModel):
    currency_pair: str
    volatility: float
    avg_rate: float

class ArbitrageItem(BaseModel):
    currency_a: str
    currency_b: str
    currency_c: str
    profit_percent: float

# --- Эндпоинты ---

@app.get("/", tags=["Info"])
def root():
    return {"name": "Currency Tracker API", "version": "1.0.0", "docs": "/docs"}


@app.get("/api/rates/latest", response_model=list[RateItem], tags=["Rates"])
def get_latest_rates():
    """Последние курсы всех валютных пар"""
    db = Database()
    db.connect()
    db.cursor.execute("SELECT * FROM v_latest_rates")
    rows = db.cursor.fetchall()
    db.disconnect()
    return [
        RateItem(
            base_currency=r[0], target_currency=r[1], currency_pair=r[2],
            rate=float(r[3]), rate_date=r[4].isoformat(), source_name=r[5]
        ) for r in rows
    ]


@app.get("/api/rates/{pair}", response_model=list[HistoryItem], tags=["Rates"])
def get_rate_history(
    pair: str,
    days: int = Query(default=30, ge=1, le=365, description="Количество дней")
):
    """История курса валютной пары. Формат пары: USD-RUB"""
    if "-" not in pair:
        raise HTTPException(status_code=400, detail="Формат пары: BASE-TARGET, например USD-RUB")
    base, target = pair.upper().split("-", 1)
    db = Database()
    db.connect()
    db.cursor.execute(
        """SELECT rate_date, rate FROM exchange_rates
           WHERE base_currency = %s AND target_currency = %s
             AND rate_date >= CURRENT_DATE - INTERVAL '%s days'
           ORDER BY rate_date""",
        (base, target, days)
    )
    rows = db.cursor.fetchall()
    db.disconnect()
    if not rows:
        raise HTTPException(status_code=404, detail=f"Данные для {pair} не найдены")
    return [HistoryItem(date=r[0].isoformat(), rate=float(r[1])) for r in rows]


@app.get("/api/convert", response_model=ConvertResponse, tags=["Converter"])
def convert_currency(
    amount: float = Query(..., gt=0, description="Сумма"),
    from_curr: str = Query(..., description="Исходная валюта, например USD"),
    to_curr: str = Query(..., description="Целевая валюта, например RUB")
):
    """Конвертация валют по актуальному курсу"""
    db = Database()
    db.connect()
    db.cursor.execute("SELECT convert_currency(%s, %s, %s)", (amount, from_curr.upper(), to_curr.upper()))
    result = db.cursor.fetchone()
    db.disconnect()
    return ConvertResponse(
        amount=amount,
        from_currency=from_curr.upper(),
        to_currency=to_curr.upper(),
        result=float(result[0]) if result and result[0] else None
    )


@app.get("/api/analysis/{pair}", tags=["Analysis"])
def analyze_pair(
    pair: str,
    days: int = Query(default=30, ge=1, le=365)
):
    """Полный анализ валютной пары: тренд, RSI, прогноз, статистика. Формат: USD-RUB"""
    analyzer = CurrencyAnalyzer()
    report = analyzer.generate_report(pair.replace("-", "/").upper(), days)
    analyzer.close()
    return report


@app.get("/api/volatility", response_model=list[VolatilityItem], tags=["Analysis"])
def get_volatility(days: int = Query(default=7, ge=1, le=90)):
    """Рейтинг волатильности валютных пар"""
    analyzer = CurrencyAnalyzer()
    ranking = analyzer.get_volatility_ranking(days)
    analyzer.close()
    return [VolatilityItem(**item) for item in ranking]


@app.get("/api/arbitrage", response_model=list[ArbitrageItem], tags=["Analysis"])
def find_arbitrage():
    """Поиск арбитражных возможностей"""
    analyzer = CurrencyAnalyzer()
    opportunities = analyzer.find_arbitrage()
    analyzer.close()
    return [ArbitrageItem(**item) for item in opportunities]


@app.get("/api/alerts", tags=["Alerts"])
def check_alerts():
    """Проверка сработавших алертов"""
    analyzer = CurrencyAnalyzer()
    alerts = analyzer.check_alerts()
    analyzer.close()
    return alerts


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8000, reload=True)
