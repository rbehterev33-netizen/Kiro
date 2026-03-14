#!/usr/bin/env python3
"""Тест всех эндпоинтов FastAPI сервера"""

import urllib.request
import json
import sys

BASE = "http://127.0.0.1:8000"
passed = 0
failed = 0

def req(method, path, body=None, expect_status=200):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw)
    except urllib.error.HTTPError as e:
        return e.code, {}

def check(name, status, data, assertions=None):
    global passed, failed
    ok = True
    reasons = []

    if status != 200:
        ok = False
        reasons.append(f"status={status}")

    if assertions:
        for fn, msg in assertions:
            try:
                if not fn(data):
                    ok = False
                    reasons.append(msg)
            except Exception as e:
                ok = False
                reasons.append(f"exception: {e}")

    if ok:
        passed += 1
        print(f"  ✓  {name}")
    else:
        failed += 1
        print(f"  ✗  {name}  [{', '.join(reasons)}]")

    return data

print("\n" + "="*55)
print("  Currency Tracker — тест сервера")
print("="*55)

# --- Info ---
print("\n[Info]")
s, d = req("GET", "/api/status")
check("GET /api/status", s, d, [
    (lambda d: d.get("db") == "connected",   "db != connected"),
    (lambda d: d.get("currencies", 0) > 0,   "currencies = 0"),
    (lambda d: d.get("exchange_rates", 0) > 0,"exchange_rates = 0"),
])

s, d = req("GET", "/api")
check("GET /api", s, d, [
    (lambda d: "version" in d, "no version"),
])

# --- Pages ---
print("\n[HTML страницы]")
for page in ["/", "/rates", "/converter", "/analysis", "/logs"]:
    try:
        with urllib.request.urlopen(BASE + page, timeout=10) as r:
            size = len(r.read())
            ok = size > 500
        passed += ok
        failed += not ok
        print(f"  {'✓' if ok else '✗'}  GET {page}  ({size} bytes)")
    except Exception as e:
        failed += 1
        print(f"  ✗  GET {page}  ERROR: {e}")

# --- Currencies ---
print("\n[Currencies]")
s, d = req("GET", "/api/currencies")
check("GET /api/currencies", s, d, [
    (lambda d: isinstance(d, list) and len(d) >= 50, f"ожидалось >=50, получено {len(d) if isinstance(d,list) else '?'}"),
    (lambda d: all("code" in c for c in d[:3]),       "нет поля code"),
])

# --- Rates ---
print("\n[Rates]")
s, d = req("GET", "/api/rates/latest")
check("GET /api/rates/latest", s, d, [
    (lambda d: isinstance(d, list) and len(d) > 0, "пустой список"),
    (lambda d: "currency_pair" in d[0],             "нет currency_pair"),
    (lambda d: "rate" in d[0],                      "нет rate"),
])

s, d = req("GET", "/api/rates/USD-RUB?days=7")
check("GET /api/rates/USD-RUB?days=7", s, d, [
    (lambda d: isinstance(d, list) and len(d) > 0, "нет данных"),
    (lambda d: "date" in d[0] and "rate" in d[0],  "нет date/rate"),
])

s, d = req("GET", "/api/rates/EUR-RUB?days=30")
check("GET /api/rates/EUR-RUB?days=30", s, d, [
    (lambda d: isinstance(d, list) and len(d) > 0, "нет данных"),
])

s, d = req("GET", "/api/rates/INVALID-PAIR?days=7")
check("GET /api/rates/INVALID-PAIR (404 ожидается)", 200 if s == 404 else s, d, [])

# --- Converter ---
print("\n[Converter]")
s, d = req("GET", "/api/convert?amount=1000&from_curr=USD&to_curr=RUB")
check("GET /api/convert USD→RUB 1000", s, d, [
    (lambda d: d.get("result") is not None,      "result = null"),
    (lambda d: d.get("result", 0) > 1000,        f"курс подозрительный: {d.get('result')}"),
])

s, d = req("GET", "/api/convert?amount=100&from_curr=EUR&to_curr=USD")
check("GET /api/convert EUR→USD 100", s, d, [
    (lambda d: d.get("result") is not None, "result = null"),
])

# --- Analysis ---
print("\n[Analysis]")
s, d = req("GET", "/api/analysis/USD-RUB?days=7")
check("GET /api/analysis/USD-RUB", s, d, [
    (lambda d: "trend" in d,           "нет trend"),
    (lambda d: "rsi" in d,             "нет rsi"),
    (lambda d: "statistics" in d,      "нет statistics"),
    (lambda d: d["statistics"].get("avg_rate") is not None, "avg_rate = null"),
])

s, d = req("GET", "/api/volatility?days=7")
check("GET /api/volatility?days=7", s, d, [
    (lambda d: isinstance(d, list) and len(d) > 0,  "пустой список"),
    (lambda d: "volatility" in d[0],                "нет volatility"),
])

s, d = req("GET", "/api/correlation?pair1=USD-RUB&pair2=EUR-RUB&days=7")
check("GET /api/correlation USD-RUB / EUR-RUB", s, d, [
    (lambda d: "correlation" in d,       "нет correlation"),
    (lambda d: "interpretation" in d,    "нет interpretation"),
])

s, d = req("GET", "/api/arbitrage")
check("GET /api/arbitrage", s, d, [
    (lambda d: isinstance(d, list), "не список"),
])

# --- Alerts ---
print("\n[Alerts]")
s, d = req("GET", "/api/alerts")
check("GET /api/alerts", s, d, [
    (lambda d: isinstance(d, list), "не список"),
])

# --- Logs ---
print("\n[Logs]")
s, d = req("GET", "/api/logs?limit=10")
check("GET /api/logs?limit=10", s, d, [
    (lambda d: isinstance(d, list) and len(d) > 0, "нет логов"),
    (lambda d: "status" in d[0],                   "нет поля status"),
    (lambda d: "source" in d[0],                   "нет поля source"),
])

# --- Parse run ---
print("\n[Parser]")
s, d = req("POST", "/api/parse/run")
check("POST /api/parse/run", s, d, [
    (lambda d: "success" in d, "нет поля success"),
    (lambda d: "message" in d, "нет поля message"),
])

# --- Static ---
print("\n[Static]")
for f in ["/static/style.css", "/static/app.js"]:
    try:
        with urllib.request.urlopen(BASE + f, timeout=5) as r:
            size = len(r.read())
            ok = size > 100
        passed += ok
        failed += not ok
        print(f"  {'✓' if ok else '✗'}  GET {f}  ({size} bytes)")
    except Exception as e:
        failed += 1
        print(f"  ✗  GET {f}  ERROR: {e}")

# --- Итог ---
total = passed + failed
print("\n" + "="*55)
print(f"  Итого: {total} тестов  |  ✓ {passed} passed  |  ✗ {failed} failed")
print("="*55 + "\n")
sys.exit(0 if failed == 0 else 1)
