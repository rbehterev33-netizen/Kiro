#!/usr/bin/env python3
"""
FastAPI сервер для Currency Tracker
Веб-интерфейс: http://localhost:8000
Документация:  http://localhost:8000/docs
"""

import os, sys, subprocess, threading, time, logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from analyzer import CurrencyAnalyzer
from database import Database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger("scheduler")

# --- Фоновый планировщик ---

def _scheduler_loop():
    """Запускает парсер каждый день в 9:00 и проверяет алерты каждый час"""
    from main import main as parse_main
    last_parse_day = None
    last_alert_hour = None

    logger.info("Планировщик запущен")
    while True:
        now = datetime.now()

        # Парсинг раз в день в 9:00
        if now.hour == 9 and now.date() != last_parse_day:
            logger.info("Автопарсинг: запуск...")
            try:
                parse_main()
                last_parse_day = now.date()
                logger.info("Автопарсинг: завершён")
            except Exception as e:
                logger.error(f"Автопарсинг: ошибка — {e}")

        # Проверка алертов раз в час
        if now.hour != last_alert_hour:
            try:
                from analyzer import CurrencyAnalyzer
                a = CurrencyAnalyzer()
                alerts = a.check_alerts()
                a.close()
                if alerts:
                    logger.info(f"Алерты: сработало {len(alerts)}")
                last_alert_hour = now.hour
            except Exception as e:
                logger.error(f"Алерты: ошибка — {e}")

        time.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем планировщик в фоновом потоке
    t = threading.Thread(target=_scheduler_loop, daemon=True, name="scheduler")
    t.start()
    logger.info("Фоновый планировщик запущен")
    yield
    logger.info("Сервер остановлен")

app = FastAPI(
    title="Currency Tracker API",
    description="API для получения и анализа курсов валют",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Pydantic модели ---

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
    data_points: int

class ArbitrageItem(BaseModel):
    currency_a: str
    currency_b: str
    currency_c: str
    profit_percent: float

# --- Хелперы ---

def _db():
    db = Database()
    db.connect()
    return db

def _pair(pair: str):
    if "-" not in pair:
        raise HTTPException(400, "Формат пары: BASE-TARGET, например USD-RUB")
    return tuple(pair.upper().split("-", 1))


# --- HTML страницы ---

@app.get("/", include_in_schema=False)
def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/rates", include_in_schema=False)
def page_rates(request: Request):
    return templates.TemplateResponse("rates.html", {"request": request})

@app.get("/converter", include_in_schema=False)
def page_converter(request: Request):
    return templates.TemplateResponse("converter.html", {"request": request})

@app.get("/analysis", include_in_schema=False)
def page_analysis(request: Request):
    return templates.TemplateResponse("analysis.html", {"request": request})

@app.get("/logs", include_in_schema=False)
def page_logs(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

@app.get("/compare", include_in_schema=False)
def page_compare(request: Request):
    return templates.TemplateResponse("compare.html", {"request": request})

@app.get("/crypto", include_in_schema=False)
def page_crypto(request: Request):
    return templates.TemplateResponse("crypto.html", {"request": request})


# --- API ---

@app.get("/api", tags=["Info"])
def api_root():
    return {"name": "Currency Tracker API", "version": "2.0.0", "docs": "/docs", "ui": "/"}


@app.get("/api/scheduler/status", tags=["Info"])
def scheduler_status():
    """Статус планировщика и время следующего парсинга"""
    now = datetime.now()
    next_parse = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now.hour >= 9:
        from datetime import timedelta
        next_parse += timedelta(days=1)
    return {
        "scheduler": "running",
        "next_parse": next_parse.strftime("%Y-%m-%d %H:%M"),
        "next_alert_check": now.replace(minute=0, second=0).strftime("%Y-%m-%d %H:%M"),
        "server_time": now.strftime("%Y-%m-%d %H:%M:%S")
    }


@app.get("/api/status", tags=["Info"])
def status():
    """Статус БД"""
    db = _db()
    db.cursor.execute("""
        SELECT (SELECT COUNT(*) FROM currencies),
               (SELECT COUNT(*) FROM exchange_rates),
               (SELECT COUNT(*) FROM data_sources),
               (SELECT MAX(rate_date) FROM exchange_rates)
    """)
    r = db.cursor.fetchone()
    db.disconnect()
    return {"db": "connected", "currencies": r[0], "exchange_rates": r[1],
            "data_sources": r[2], "last_update": r[3].isoformat() if r[3] else None}


@app.get("/api/currencies", tags=["Currencies"])
def list_currencies():
    """Список всех валют"""
    db = _db()
    rows = db.fetchall_dict("SELECT code, name, symbol FROM currencies ORDER BY code")
    db.disconnect()
    return rows


@app.get("/api/rates/latest", response_model=list[RateItem], tags=["Rates"])
def get_latest_rates(source: Optional[str] = Query(None)):
    """Последние курсы всех пар"""
    db = _db()
    if source:
        db.cursor.execute("SELECT * FROM v_latest_rates WHERE source_name ILIKE %s", (f"%{source}%",))
    else:
        db.cursor.execute("SELECT * FROM v_latest_rates")
    rows = db.cursor.fetchall()
    db.disconnect()
    return [RateItem(base_currency=r[0], target_currency=r[1], currency_pair=r[2],
                     rate=float(r[3]), rate_date=r[4].isoformat(), source_name=r[5]) for r in rows]


@app.get("/api/rates/{pair}", response_model=list[HistoryItem], tags=["Rates"])
def get_rate_history(pair: str, days: int = Query(default=30, ge=1, le=365)):
    """История курса. Формат: USD-RUB"""
    base, target = _pair(pair)
    db = _db()
    db.cursor.execute(
        """SELECT rate_date, rate FROM exchange_rates
           WHERE base_currency=%s AND target_currency=%s
             AND rate_date >= CURRENT_DATE - (%s||' days')::INTERVAL
           ORDER BY rate_date""",
        (base, target, days)
    )
    rows = db.cursor.fetchall()
    db.disconnect()
    if not rows:
        raise HTTPException(404, f"Данные для {pair} не найдены")
    return [HistoryItem(date=r[0].isoformat(), rate=float(r[1])) for r in rows]


@app.get("/api/convert", response_model=ConvertResponse, tags=["Converter"])
def convert_currency(
    amount: float = Query(..., gt=0),
    from_curr: str = Query(...),
    to_curr: str = Query(...)
):
    """Конвертация валют"""
    db = _db()
    db.cursor.execute("SELECT convert_currency(%s, %s, %s)", (amount, from_curr.upper(), to_curr.upper()))
    result = db.cursor.fetchone()
    db.disconnect()
    return ConvertResponse(amount=amount, from_currency=from_curr.upper(), to_currency=to_curr.upper(),
                           result=float(result[0]) if result and result[0] else None)


@app.get("/api/analysis/{pair}", tags=["Analysis"])
def analyze_pair(pair: str, days: int = Query(default=30, ge=1, le=365)):
    """Анализ пары: тренд, RSI, прогноз. Формат: USD-RUB"""
    analyzer = CurrencyAnalyzer()
    report = analyzer.generate_report(pair.replace("-", "/").upper(), days)
    analyzer.close()
    return report


@app.get("/api/correlation", tags=["Analysis"])
def get_correlation(
    pair1: str = Query(...),
    pair2: str = Query(...),
    days: int = Query(default=30, ge=7, le=365)
):
    """Корреляция двух пар"""
    analyzer = CurrencyAnalyzer()
    corr = analyzer.get_correlation(pair1.replace("-", "/").upper(), pair2.replace("-", "/").upper(), days)
    analyzer.close()
    return {
        "pair1": pair1.upper(), "pair2": pair2.upper(), "days": days, "correlation": corr,
        "interpretation": (
            "сильная положительная" if corr and corr > 0.7 else
            "сильная отрицательная" if corr and corr < -0.7 else
            "умеренная" if corr else "недостаточно данных"
        )
    }


@app.get("/api/volatility", response_model=list[VolatilityItem], tags=["Analysis"])
def get_volatility(days: int = Query(default=7, ge=1, le=90)):
    """Рейтинг волатильности"""
    analyzer = CurrencyAnalyzer()
    ranking = analyzer.get_volatility_ranking(days)
    analyzer.close()
    return [VolatilityItem(**item) for item in ranking]


@app.get("/api/arbitrage", response_model=list[ArbitrageItem], tags=["Analysis"])
def find_arbitrage():
    """Арбитражные возможности"""
    analyzer = CurrencyAnalyzer()
    opportunities = analyzer.find_arbitrage()
    analyzer.close()
    return [ArbitrageItem(**item) for item in opportunities]


@app.get("/api/alerts", tags=["Alerts"])
def check_alerts():
    """Сработавшие алерты"""
    analyzer = CurrencyAnalyzer()
    alerts = analyzer.check_alerts()
    analyzer.close()
    return alerts


@app.get("/api/logs", tags=["Logs"])
def get_parsing_logs(limit: int = Query(default=20, ge=1, le=100)):
    """История запусков парсера"""
    db = _db()
    rows = db.fetchall_dict(
        """SELECT pl.log_id, ds.name AS source, pl.parse_date, pl.status,
                  pl.records_added, pl.execution_time_ms, pl.error_message
           FROM parsing_log pl JOIN data_sources ds USING (source_id)
           ORDER BY pl.log_id DESC LIMIT %s""",
        (limit,)
    )
    db.disconnect()
    for r in rows:
        if r.get("parse_date"):
            r["parse_date"] = str(r["parse_date"])
    return rows


@app.post("/api/parse/run", tags=["Logs"])
def run_parser():
    """Запустить парсер вручную"""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, "main.py")],
            capture_output=True, text=True, timeout=120, cwd=BASE_DIR
        )
        success = result.returncode == 0
        return {
            "success": success,
            "message": "Парсер выполнен успешно" if success else "Ошибка парсера",
            "output": result.stdout[-1000:] if result.stdout else "",
            "error": result.stderr[-500:] if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Таймаут — парсер работал дольше 120 сек"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.get("/api/rates/compare/{pair}", tags=["Compare"])
def compare_sources(pair: str, days: int = Query(default=30, ge=1, le=365)):
    """Сравнение курса одной пары по разным источникам"""
    base, target = _pair(pair)
    db = _db()
    rows = db.fetchall_dict(
        """SELECT er.rate_date, er.rate, ds.name AS source
           FROM exchange_rates er
           JOIN data_sources ds USING (source_id)
           WHERE er.base_currency = %s AND er.target_currency = %s
             AND er.rate_date >= CURRENT_DATE - (%s||' days')::INTERVAL
           ORDER BY er.rate_date, ds.name""",
        (base, target, days)
    )
    db.disconnect()
    # Группируем по источнику
    result = {}
    for r in rows:
        src = r["source"]
        if src not in result:
            result[src] = []
        result[src].append({"date": str(r["rate_date"]), "rate": float(r["rate"])})
    return result


@app.get("/api/crypto/latest", tags=["Crypto"])
def get_crypto_latest():
    """Последние курсы криптовалют"""
    db = _db()
    rows = db.fetchall_dict(
        """SELECT er.base_currency, er.target_currency,
                  er.rate, er.rate_date, ds.name AS source
           FROM exchange_rates er
           JOIN data_sources ds USING (source_id)
           WHERE ds.name ILIKE '%coingecko%'
             AND er.rate_date = (
               SELECT MAX(rate_date) FROM exchange_rates er2
               JOIN data_sources ds2 USING (source_id)
               WHERE ds2.name ILIKE '%coingecko%'
             )
           ORDER BY er.base_currency, er.target_currency"""
    )
    db.disconnect()
    for r in rows:
        r["rate_date"] = str(r["rate_date"])
    return rows


@app.get("/api/moex/latest", tags=["MOEX"])
def get_moex_latest():
    """Последние биржевые курсы MOEX"""
    db = _db()
    rows = db.fetchall_dict(
        """SELECT er.base_currency, er.target_currency,
                  er.rate, er.rate_date, ds.name AS source
           FROM exchange_rates er
           JOIN data_sources ds USING (source_id)
           WHERE ds.name ILIKE '%moex%'
             AND er.rate_date = (
               SELECT MAX(rate_date) FROM exchange_rates er2
               JOIN data_sources ds2 USING (source_id)
               WHERE ds2.name ILIKE '%moex%'
             )
           ORDER BY er.base_currency"""
    )
    db.disconnect()
    for r in rows:
        r["rate_date"] = str(r["rate_date"])
    return rows


@app.post("/api/parse/moex", tags=["Logs"])
def run_moex_parser():
    """Запустить MOEX парсер вручную"""
    try:
        from parsers import MOEXParser
        db = _db()
        from main import _ensure_source
        source_id = _ensure_source(db, "Moscow Exchange (MOEX)",
                                   "https://iss.moex.com/iss")
        parser = MOEXParser()
        data = parser.fetch()
        rates = parser.parse(data)
        rates_data = [
            (r["base_currency"], r["target_currency"], r["rate"], r["rate_date"], source_id)
            for r in rates if db.get_currency_code(r["base_currency"])
        ]
        n = db.insert_rates(rates_data)
        db.disconnect()
        return {"success": True, "records": n, "message": f"MOEX: сохранено {n} курсов"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.post("/api/parse/crypto", tags=["Logs"])
def run_crypto_parser():
    """Запустить крипто парсер вручную"""
    try:
        from parsers import CryptoParser
        from main import _ensure_source, _ensure_currency
        db = _db()
        source_id = _ensure_source(db, "CoinGecko (Crypto)",
                                   "https://api.coingecko.com/api/v3")
        crypto_names = {
            "BTC": ("Bitcoin", "₿"), "ETH": ("Ethereum", "Ξ"),
            "USDT": ("Tether", "₮"), "BNB": ("BNB", ""),
            "SOL": ("Solana", ""), "XRP": ("XRP", ""), "TON": ("Toncoin", ""),
        }
        for code, (name, symbol) in crypto_names.items():
            _ensure_currency(db, code, name, symbol)

        parser = CryptoParser()
        data = parser.fetch()
        rates = parser.parse(data)
        rates_data = [
            (r["base_currency"], r["target_currency"], r["rate"], r["rate_date"], source_id)
            for r in rates if db.get_currency_code(r["base_currency"])
            and db.get_currency_code(r["target_currency"])
        ]
        n = db.insert_rates(rates_data)
        db.disconnect()
        return {"success": True, "records": n, "message": f"Crypto: сохранено {n} курсов"}
    except Exception as e:
        return {"success": False, "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8000, reload=True)
